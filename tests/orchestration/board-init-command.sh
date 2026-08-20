#!/usr/bin/env bash
# tests/orchestration/board-init-command.sh — Structural lint for
# commands/board-init.md.
#
# /board-init is a markdown command Claude reads at runtime; we cannot execute
# it from a shell. As with board-graph-command.sh / board-rebuild-command.sh,
# this lint locks in the procedural contract so a future edit cannot silently
# regress it.
#
# The contract this pins (specs/board-relocation.md §6.5):
#   - scaffolds at the 1.1.0 default `engineering-board/<project>/` (NOT docs/boards/),
#   - router lives at engineering-board/BOARD-ROUTER.md with an engineering-board/ path column,
#   - the five entry-type subdirs + .gitkeep,
#   - prints the §6.2 additive runtime .gitignore stanza (committed-by-default content),
#     and never edits .gitignore automatically (print-only),
#   - a --private full-tree opt-out,
#   - backward-compat is documented (docs/boards/ + legacy docs/board/ still resolve;
#     relocate via /board-migrate --relocate),
#   - idempotency.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

CMD="$ROOT/commands/board-init.md"
REPO_GITIGNORE="$ROOT/.gitignore"

if [ ! -f "$CMD" ]; then
  echo "MISSING FILE: $CMD" >&2
  exit 1
fi

PASS=0
FAIL=0
report() {
  if [ "$1" = "0" ]; then
    printf "  [PASS] %s\n" "$2"
    PASS=$((PASS + 1))
  else
    printf "  [FAIL] %s%s\n" "$2" "${3:+ -- $3}"
    FAIL=$((FAIL + 1))
  fi
}

check() {
  local label="$1" needle="$2"
  if grep -qF -- "$needle" "$CMD"; then
    report 0 "$label"
  else
    report 1 "$label" "missing: $needle"
  fi
}

check_re() {
  local label="$1" pattern="$2"
  if grep -qE -- "$pattern" "$CMD"; then
    report 0 "$label"
  else
    report 1 "$label" "missing regex: $pattern"
  fi
}

check_file() {
  local label="$1" file="$2" needle="$3"
  if grep -qxF -- "$needle" "$file"; then
    report 0 "$label"
  else
    report 1 "$label" "missing from ${file#$ROOT/}: $needle"
  fi
}

check_not_ignored() {
  local label="$1" path="$2"
  if git -C "$ROOT" check-ignore --no-index -q -- "$path"; then
    report 1 "$label" "canonical path is ignored: $path"
  else
    report 0 "$label"
  fi
}

check_ignored() {
  local label="$1" path="$2"
  if git -C "$ROOT" check-ignore --no-index -q -- "$path"; then
    report 0 "$label"
  else
    report 1 "$label" "runtime path is not ignored: $path"
  fi
}

check_tracked() {
  local label="$1" path="$2"
  if git -C "$ROOT" ls-files --error-unmatch -- "$path" >/dev/null 2>&1; then
    report 0 "$label"
  else
    report 1 "$label" "canonical path is not tracked: $path"
  fi
}

# ── Frontmatter ─────────────────────────────────────────────────────────────
if head -1 "$CMD" | grep -qF -- "---"; then
  report 0 "board-init.md has frontmatter delimiter"
else
  report 1 "board-init.md has frontmatter delimiter"
fi
check_re "frontmatter: description" "^description:"
check_re "frontmatter: argument-hint" "^argument-hint:"
check_re "frontmatter: argument-hint advertises --private" "argument-hint:.*--private"

# ── New default: engineering-board/ (1.1.0), NOT docs/boards/ ────────────────
check "scaffolds at engineering-board/ default" "engineering-board/\$1"
check "router at engineering-board/BOARD-ROUTER.md" "engineering-board/BOARD-ROUTER.md"
check "router path column uses engineering-board/\$1" "| \$1 | engineering-board/\$1 |"
check "framing: committed by default" "committed by default"

# ── Canonical record subdirs + .gitkeep ─────────────────────────────────────
for sub in bugs features questions observations learnings hypotheses; do
  check "scaffolds subdir: $sub/" "engineering-board/\$1/$sub/"
done
check "entry-type dirs get .gitkeep" ".gitkeep"

# ── .gitignore stanza: §6.2 additive runtime patterns, print-only ───────────
check "gitignore: runtime _sessions/ ignored" "engineering-board/*/_sessions/"
check "gitignore: runtime _claims/ ignored" "engineering-board/*/_claims/"
check "gitignore: runtime _migrate-snapshot/ ignored" "engineering-board/*/_migrate-snapshot/"
check "gitignore: hidden runtime folder ignored" ".engineering-board/"
check "gitignore: consolidation.log stays committed" "consolidation.log"
check "gitignore: print-only (does not auto-edit)" "do not edit \`.gitignore\` automatically"

# The plugin repository dogfoods its own board. It must apply the same runtime
# exclusions that the command prints for consuming repositories.
check_file "self-host: hidden runtime ignored" "$REPO_GITIGNORE" ".engineering-board/"
check_file "self-host: runtime _sessions/ ignored" "$REPO_GITIGNORE" "engineering-board/*/_sessions/"
check_file "self-host: runtime _claims/ ignored" "$REPO_GITIGNORE" "engineering-board/*/_claims/"
check_file "self-host: runtime migration state ignored" "$REPO_GITIGNORE" "engineering-board/*/_migrate-snapshot/"
check_ignored "self-host: scratch path matches ignore policy" "engineering-board/eb-self/_sessions/check.md"
check_ignored "self-host: claim path matches ignore policy" "engineering-board/eb-self/_claims/B999/owner.txt"
check_ignored "self-host: migration path matches ignore policy" "engineering-board/eb-self/_migrate-snapshot/state.json"
check_ignored "self-host: hidden runtime path matches ignore policy" ".engineering-board/session-mode.json"
check_not_ignored "self-host: canonical board remains tracked" "engineering-board/eb-self/BOARD.md"
check_not_ignored "self-host: canonical graph remains tracked" "engineering-board/eb-self/GRAPH.yml"
check_not_ignored "self-host: consolidation receipt remains tracked" "engineering-board/eb-self/consolidation.log"
check_tracked "self-host: canonical board is in the index" "engineering-board/eb-self/BOARD.md"
check_tracked "self-host: canonical graph is in the index" "engineering-board/eb-self/GRAPH.yml"
check_tracked "self-host: consolidation receipt is in the index" "engineering-board/eb-self/consolidation.log"

# ── --private full-tree opt-out ─────────────────────────────────────────────
check "private: full-tree opt-out documented" "# engineering-board (private"

# ── Backward compatibility + relocation pointer ─────────────────────────────
check "compat: documents backward compatibility" "Backward compatibility"
check "compat: docs/boards/ still resolves" "docs/boards/"
check "compat: legacy docs/board/ still resolves" "docs/board/"
check "compat: points relocation at /board-migrate --relocate" "/board-migrate --relocate"

# ── Idempotency ─────────────────────────────────────────────────────────────
check "contract: idempotent" "idempotent"

# ── Step ordering: validate -> router -> dir -> BOARD.md -> ARCHIVE.md ───────
#    -> print .gitignore -> report.
for step in "Step 1" "Step 2" "Step 3" "Step 4" "Step 5" "Step 6" "Step 7"; do
  check_re "procedure: $step heading present" "^### ${step} —"
done

echo ""
echo "================================================================"
echo "board-init-command: $PASS pass, $FAIL fail"
echo "================================================================"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
