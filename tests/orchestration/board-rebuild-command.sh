#!/usr/bin/env bash
# tests/orchestration/board-rebuild-command.sh — Structural lint for
# commands/board-rebuild.md.
#
# NEXT-PHASE.md §1.4: "/board-rebuild: assert BOARD.md and GRAPH.yml
# deterministic regeneration; drift detection; auto-resolve terminal pass."
#
# /board-rebuild is a markdown command Claude reads at runtime; we cannot
# execute it from a shell. What we CAN test is that the procedural contract
# documented in the file stays intact across refactors — the same approach
# tests/modes/command-frontmatter.sh and stop-hook-mode-routing.sh take.
#
# Each assertion below ties to a specific contract the test domain locks in:
# regeneration source-of-truth, the 4 entry-type subdirs, drift-vs-write
# ordering, auto-resolve invocation, and the documented idempotency guarantee.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

CMD="$ROOT/commands/board-rebuild.md"
AUTO_RESOLVE="$ROOT/references/auto-resolve-pass.md"

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

# ── Trigger surface ─────────────────────────────────────────────────────────
check "trigger: /board-rebuild documented"                   "/board-rebuild"
check "trigger: per-project variant"                         "/board-rebuild <project-name>"

# ── Outputs: BOARD.md + GRAPH.yml are the two regeneration targets ──────────
check "regen target: BOARD.md"                               "BOARD.md"
check "regen target: GRAPH.yml"                              "GRAPH.yml"
check "single source of truth: entry .md files"              "single source of truth"

# ── Determinism + idempotency are non-negotiable contract terms ─────────────
check "contract: deterministic regeneration"                 "deterministic"
check "contract: idempotent"                                 "Idempotent"
check "contract: same input -> byte-identical (modulo generated_at)" "byte-identical"

# ── Boards lookup: router-first with legacy fallback ────────────────────────
check "boards: reads BOARD-ROUTER.md"                        "BOARD-ROUTER.md"
check "boards: legacy fallback"                              "legacy"

# ── Four entry-type subdirs must all be enumerated ──────────────────────────
for sub in bugs features questions observations; do
  check "scans subdir: $sub/" "$sub"
done

# ── Validation pass surfaces (informational, does not block) ────────────────
check "validation: duplicate IDs reported"                   "Duplicate IDs"
check "validation: resolved-in-Open reported"                "Resolved entries still listed"
check "validation: missing frontmatter reported"             "Missing required frontmatter"
check "validation: dangling blocked_by reported"             "Dangling"

# ── Step ordering: scan -> validate -> regen BOARD.md -> diff -> write ──────
#    -> regen GRAPH.yml -> auto-resolve terminal pass -> report.
for step in "Step 1" "Step 2" "Step 3" "Step 4" "Step 5" "Step 6" "Step 7" "Step 8" "Step 9"; do
  check_re "procedure: $step heading present" "^### ${step} —"
done

# ── Diff-before-write ordering: Step 5 (diff) must precede Step 6 (write) ───
DIFF_LINE=$(grep -nF '### Step 5' "$CMD" | head -1 | cut -d: -f1)
WRITE_LINE=$(grep -nF '### Step 6' "$CMD" | head -1 | cut -d: -f1)
if [ -n "$DIFF_LINE" ] && [ -n "$WRITE_LINE" ] && [ "$DIFF_LINE" -lt "$WRITE_LINE" ]; then
  report 0 "procedure: diff (Step 5) precedes write (Step 6)"
else
  report 1 "procedure: diff (Step 5) precedes write (Step 6)" "diff=$DIFF_LINE write=$WRITE_LINE"
fi

# ── Auto-resolve terminal pass is mandatory and references the protocol ─────
check "auto-resolve: mandatory terminal pass"                "Auto-resolve terminal pass (mandatory)"
check "auto-resolve: references shared protocol"             "auto-resolve-pass.md"
if [ -f "$AUTO_RESOLVE" ]; then
  report 0 "auto-resolve protocol file exists at references/auto-resolve-pass.md"
else
  report 1 "auto-resolve protocol file exists at references/auto-resolve-pass.md" \
    "missing: $AUTO_RESOLVE"
fi

# ── /board-graph integration: Step 7 must hand off to graph logic ───────────
check "graph integration: Step 7 invokes /board-graph logic" "/board-graph"

# ── B004 framing: rebuild is the cache-invalidation fix ─────────────────────
check "framing: B004 fix mechanism"                          "B004"

# ── Sort order documented for stable BOARD.md output ────────────────────────
check "sort: bugs by priority then ID"                       "P0"
check "sort: questions by ID ascending"                      "Questions by ID ascending"
check "sort: observations by ID ascending"                   "Observations by ID ascending"

# ── Report shape (one block to chat) ────────────────────────────────────────
check "report: BOARD.md add/remove/reorder counts"           "BOARD.md:"
check "report: GRAPH.yml node/edge/cluster counts"           "GRAPH.yml:"

echo ""
echo "================================================================"
echo "board-rebuild-command: $PASS pass, $FAIL fail"
echo "================================================================"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
