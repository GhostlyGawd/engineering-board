#!/usr/bin/env bash
# tests/modes/agent-frontmatter-pm-subagents.sh
# Structural lint for PM subagents: consolidator.md, tidier.md, learnings-curator.md.
#
# Checks frontmatter fields, required tool sets, untrusted-data framing,
# output contract shape, and input contract documentation for each agent.
#
# Exits 0 iff all assertions pass.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

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

# ── File existence ────────────────────────────────────────────────────────────
CONSOLIDATOR="$ROOT/agents/consolidator.md"
TIDIER="$ROOT/agents/tidier.md"
LEARNINGS="$ROOT/agents/learnings-curator.md"

for f in "$CONSOLIDATOR" "$TIDIER" "$LEARNINGS"; do
  if [ ! -f "$f" ]; then
    echo "MISSING FILE: $f" >&2
    exit 1
  fi
done

# ── Helper: check frontmatter delimiter ──────────────────────────────────────
check_frontmatter_delimiter() {
  local file="$1" label="$2"
  if head -1 "$file" | grep -qF -- "---"; then
    report 0 "$label has frontmatter delimiter"
  else
    report 1 "$label has frontmatter delimiter"
  fi
}

# ── Helper: check a grep pattern ─────────────────────────────────────────────
check_grep() {
  local file="$1" flag="$2" pattern="$3" label="$4"
  if grep -q$flag "$pattern" "$file"; then
    report 0 "$label"
  else
    report 1 "$label"
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# CONSOLIDATOR
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== consolidator.md ==="

check_frontmatter_delimiter "$CONSOLIDATOR" "consolidator.md"
check_grep "$CONSOLIDATOR" "E" "^name: consolidator$"            "consolidator.md frontmatter: name=consolidator"
check_grep "$CONSOLIDATOR" "E" "^description:"                   "consolidator.md frontmatter: description present"
check_grep "$CONSOLIDATOR" "E" "^model: inherit$"                "consolidator.md frontmatter: model=inherit (no cost lock)"
check_grep "$CONSOLIDATOR" "E" "^tools:"                         "consolidator.md frontmatter: tools list present"
check_grep "$CONSOLIDATOR" "E" "^color:"                         "consolidator.md frontmatter: color present"

# Required tools for consolidator (reads, writes entries, runs bash scripts)
TOOLS_LINE_C="$(grep -E "^tools:" "$CONSOLIDATOR" || true)"
for tool in Read Write Edit Bash Grep Glob; do
  if echo "$TOOLS_LINE_C" | grep -qF "$tool"; then
    report 0 "consolidator.md tools includes $tool"
  else
    report 1 "consolidator.md tools includes $tool"
  fi
done

# Untrusted-data framing (verbatim string required by locked conventions)
check_grep "$CONSOLIDATOR" "F" "untrusted data, not instructions" "consolidator.md contains untrusted-data framing"

# Input contract: scratch session file path (not ---ENTRY-ID--- pattern)
check_grep "$CONSOLIDATOR" "F" "_sessions/"                      "consolidator.md documents scratch session file input"

# Output contract fields
for field in schema_version session_file promoted archived_superseded deferred; do
  check_grep "$CONSOLIDATOR" "F" "\"$field\""                    "consolidator.md output contract: $field field"
done

# AC T2b defense: distinct affects must produce distinct entries
if grep -qF "AC T2b" "$CONSOLIDATOR" || grep -qF "distinct.*affects" "$CONSOLIDATOR" || grep -qiF "t2b" "$CONSOLIDATOR"; then
  report 0 "consolidator.md documents AC T2b (distinct affects -> distinct entries)"
else
  report 1 "consolidator.md documents AC T2b (distinct affects -> distinct entries)"
fi

# needs: tdd set at promotion for bug/feature
check_grep "$CONSOLIDATOR" "F" "needs: tdd"                      "consolidator.md sets needs: tdd on bug/feature promotion"

# ─────────────────────────────────────────────────────────────────────────────
# TIDIER
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== tidier.md ==="

check_frontmatter_delimiter "$TIDIER" "tidier.md"
check_grep "$TIDIER" "E" "^name: tidier$"                        "tidier.md frontmatter: name=tidier"
check_grep "$TIDIER" "E" "^description:"                         "tidier.md frontmatter: description present"
check_grep "$TIDIER" "E" "^model: inherit$"                      "tidier.md frontmatter: model=inherit (no cost lock)"
check_grep "$TIDIER" "E" "^tools:"                               "tidier.md frontmatter: tools list present"
check_grep "$TIDIER" "E" "^color:"                               "tidier.md frontmatter: color present"

# Required tools for tidier (reads, writes BOARD.md, runs bash scripts)
TOOLS_LINE_T="$(grep -E "^tools:" "$TIDIER" || true)"
for tool in Read Write Edit Bash Grep Glob; do
  if echo "$TOOLS_LINE_T" | grep -qF "$tool"; then
    report 0 "tidier.md tools includes $tool"
  else
    report 1 "tidier.md tools includes $tool"
  fi
done

# Untrusted-data framing
check_grep "$TIDIER" "F" "untrusted data, not instructions"       "tidier.md contains untrusted-data framing"

# Input contract: board directory path
check_grep "$TIDIER" "F" "board"                                  "tidier.md documents board directory input"

# Output contract fields
for field in schema_version actions_taken board_md_rebuilt stale_claims_reclaimed archived_sessions_deleted patterns; do
  check_grep "$TIDIER" "F" "$field"                               "tidier.md output contract: $field field"
done

# Idempotency guarantee: must document fast-path / nothing-to-do behavior
if grep -qiF "idempotent" "$TIDIER" || grep -qiF "nothing to do" "$TIDIER" || grep -qiF "nothing-to-do" "$TIDIER"; then
  report 0 "tidier.md documents idempotent fast-path"
else
  report 1 "tidier.md documents idempotent fast-path"
fi

# References the helper scripts it delegates to
for script in board-index-check.sh board-claim-reclaim-stale.sh board-audit-scratch.sh; do
  check_grep "$TIDIER" "F" "$script"                              "tidier.md references $script"
done

# ─────────────────────────────────────────────────────────────────────────────
# LEARNINGS CURATOR
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== learnings-curator.md ==="

check_frontmatter_delimiter "$LEARNINGS" "learnings-curator.md"
check_grep "$LEARNINGS" "E" "^name: learnings-curator$"          "learnings-curator.md frontmatter: name=learnings-curator"
check_grep "$LEARNINGS" "E" "^description:"                      "learnings-curator.md frontmatter: description present"
check_grep "$LEARNINGS" "E" "^model: inherit$"                   "learnings-curator.md frontmatter: model=inherit (no cost lock)"
check_grep "$LEARNINGS" "E" "^tools:"                            "learnings-curator.md frontmatter: tools list present"
check_grep "$LEARNINGS" "E" "^color:"                            "learnings-curator.md frontmatter: color present"

# learnings-curator is read-only in v0.2.2: tools must NOT include Write or Edit
TOOLS_LINE_L="$(grep -E "^tools:" "$LEARNINGS" || true)"
for tool in Read Bash Grep Glob; do
  if echo "$TOOLS_LINE_L" | grep -qF "$tool"; then
    report 0 "learnings-curator.md tools includes $tool"
  else
    report 1 "learnings-curator.md tools includes $tool"
  fi
done
for excluded_tool in Write Edit; do
  if echo "$TOOLS_LINE_L" | grep -qF "$excluded_tool"; then
    report 1 "learnings-curator.md tools must NOT include $excluded_tool (placeholder is read-only)"
  else
    report 0 "learnings-curator.md tools does NOT include $excluded_tool (read-only placeholder)"
  fi
done

# Untrusted-data framing
check_grep "$LEARNINGS" "F" "untrusted data, not instructions"   "learnings-curator.md contains untrusted-data framing"

# Input contract: board directory path
check_grep "$LEARNINGS" "F" "board"                              "learnings-curator.md documents board directory input"

# Output contract fields
for field in schema_version learnings_dir_exists learnings_count status; do
  check_grep "$LEARNINGS" "F" "\"$field\""                       "learnings-curator.md output contract: $field field"
done

# Must document placeholder status and v0.3.0 deferral
if grep -qiF "placeholder" "$LEARNINGS"; then
  report 0 "learnings-curator.md mentions placeholder status"
else
  report 1 "learnings-curator.md mentions placeholder status"
fi
if grep -qF "v0.3.0" "$LEARNINGS"; then
  report 0 "learnings-curator.md mentions v0.3.0 deferral"
else
  report 1 "learnings-curator.md mentions v0.3.0 deferral"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
TOTAL=$((PASS + FAIL))
echo ""
echo "agent-frontmatter-pm-subagents: RESULT: $PASS/$TOTAL PASS"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
