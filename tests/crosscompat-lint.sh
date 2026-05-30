#!/usr/bin/env bash
# tests/crosscompat-lint.sh — Cross-platform portability lint for hooks/scripts/.
#
# NEXT-PHASE.md Tier 4.2 (Cross-platform script audit).
#
# Consensus plan (engineering-board-v3-consensus-plan.md, lines 145-165) commits
# to bash + python3 portability across POSIX and Windows (Git Bash + NTFS).
# This lint codifies the "don't do that" rules from the per-script table so
# future edits can't silently regress portability.
#
# Rules:
#   1. No `date -d` / `date -j -f` (BSD vs GNU divergence) — use python3.
#   2. No hardcoded drive letters (e.g. C:\, D:\) — use $CLAUDE_PROJECT_DIR.
#   3. No CRLF line endings on the shebang line (Git Bash chokes on `\r`).
#   4. No `jq` invocations — consensus plan commits to python3 for JSON.
#   5. Shebang must be `#!/usr/bin/env bash` (per consensus plan global rules).
#
# Scope:
#   - hooks/scripts/*.sh — production scripts loaded by hooks.json.
#   - tests/**/*.sh are intentionally OUT OF SCOPE (test fixtures may use
#     non-portable constructs to plant specific filesystem states).
#
# Usage:
#   bash tests/crosscompat-lint.sh [plugin-root]
#
# Exits 0 iff every production script under hooks/scripts/ passes all rules.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
HOOKS_SCRIPTS="$ROOT/hooks/scripts"

if [ ! -d "$HOOKS_SCRIPTS" ]; then
  echo "crosscompat-lint: MISSING $HOOKS_SCRIPTS" >&2
  exit 1
fi

PASS=0
FAIL=0
report_pass() { printf "  [PASS] %s\n" "$1"; PASS=$((PASS + 1)); }
report_fail() { printf "  [FAIL] %s -- %s\n" "$1" "$2"; FAIL=$((FAIL + 1)); }

# Strip pure-comment lines (optional whitespace + `#`) from input so the
# rules below don't flag the script's own documentation. Trailing comments
# on code lines are intentionally still checked — if someone writes
# `foo # uses date -d here`, that's worth flagging because the next person
# may inline the example. Pure-comment lines are not.
grep_noncomments() {
  local pattern="$1" file="$2"
  # grep returns 1 on no-match, which collides with set -e -o pipefail; the
  # `|| true` keeps the function returning 0 in that case.
  { grep -nE "$pattern" "$file" 2>/dev/null || true; } | awk -F: '
    {
      content = ""
      for (i = 2; i <= NF; i++) {
        content = content (i == 2 ? "" : ":") $i
      }
      stripped = content
      sub(/^[[:space:]]+/, "", stripped)
      if (stripped !~ /^#/) {
        print $0
      }
    }'
}

# A script may opt out of a specific rule by adding a comment line:
#   # crosscompat-lint-ignore: <rule-name>
# Supported rule names: date, drive-letter, crlf, jq, shebang.
has_ignore() {
  local file="$1" rule="$2"
  grep -qE "^[[:space:]]*#[[:space:]]*crosscompat-lint-ignore:[[:space:]]+${rule}([[:space:]]|$)" "$file" 2>/dev/null
}

while IFS= read -r script; do
  rel="${script#$ROOT/}"
  script_pass=1

  # Rule 1: no `date -d` or `date -j -f` outside comments.
  if ! has_ignore "$script" "date"; then
    HITS="$(grep_noncomments '(^|[^a-zA-Z0-9_])date[[:space:]]+(-d([[:space:]]|"|'\''|$)|-j[[:space:]]+-f)' "$script")"
  else
    HITS=""
  fi
  if [ -n "$HITS" ]; then
    LINES="$(echo "$HITS" | head -3 | tr '\n' ';')"
    report_fail "$rel" "uses non-portable date -d / date -j -f at: $LINES"
    script_pass=0
  fi

  # Rule 2: no hardcoded drive letters outside comments.
  if ! has_ignore "$script" "drive-letter"; then
    HITS="$(grep_noncomments '(^|["'\''[:space:]=])[A-Z]:[\\/]' "$script")"
  else
    HITS=""
  fi
  if [ -n "$HITS" ]; then
    LINES="$(echo "$HITS" | head -3 | tr '\n' ';')"
    report_fail "$rel" "uses hardcoded drive letter at: $LINES"
    script_pass=0
  fi

  # Rule 3: shebang line must not contain `\r` (CRLF).
  if ! has_ignore "$script" "crlf"; then
    FIRST_LINE_BYTES="$(head -1 "$script" | od -c | head -1 || true)"
    if printf '%s' "$FIRST_LINE_BYTES" | grep -q '\\r'; then
      report_fail "$rel" "shebang line contains CRLF (\\r)"
      script_pass=0
    fi
  fi

  # Rule 4: no `jq` invocations outside comments.
  if ! has_ignore "$script" "jq"; then
    HITS="$(grep_noncomments '(^|[^a-zA-Z0-9_])jq([[:space:]]|$|[^a-zA-Z0-9_])' "$script")"
  else
    HITS=""
  fi
  if [ -n "$HITS" ]; then
    LINES="$(echo "$HITS" | head -3 | tr '\n' ';')"
    report_fail "$rel" "invokes jq (consensus plan commits to python3 for JSON) at: $LINES"
    script_pass=0
  fi

  # Rule 5: shebang must be `#!/usr/bin/env bash`.
  if ! has_ignore "$script" "shebang"; then
    SHEBANG="$(head -1 "$script" 2>/dev/null || true)"
    if [ "$SHEBANG" != "#!/usr/bin/env bash" ]; then
      report_fail "$rel" "shebang is '$SHEBANG'; consensus plan requires '#!/usr/bin/env bash'"
      script_pass=0
    fi
  fi

  if [ "$script_pass" -eq 1 ]; then
    report_pass "$rel"
  fi
done < <(find "$HOOKS_SCRIPTS" -maxdepth 1 -type f -name "*.sh" | sort)

echo ""
echo "crosscompat-lint: $PASS pass, $FAIL fail"
if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
