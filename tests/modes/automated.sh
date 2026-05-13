#!/usr/bin/env bash
# tests/modes/automated.sh — Top-level runner for v0.2.2 M2.2.b mode-routing tests.
#
# Sub-tests (in order):
#   1. command-frontmatter.sh                 — /pm-start, /worker-start, /board-claim-release, /board-install-permissions markdown lint
#   2. agent-frontmatter.sh                   — tdd-builder.md frontmatter + body lint
#   3. agent-frontmatter-disciplines.sh       — code-reviewer.md + validator.md frontmatter + body lint (M2.2.c)
#   4. agent-frontmatter-pm-subagents.sh      — consolidator.md + tidier.md + learnings-curator.md frontmatter + body lint (M2.2.c)
#   5. stop-hook-mode-routing.sh              — hooks.json Stop prompt body + stop-hook-procedure.md structural lint
#
# Mirrors tests/claims/automated.sh style.
#
# Usage:
#   bash tests/modes/automated.sh                # auto-detect plugin root
#   bash tests/modes/automated.sh <plugin-root>  # explicit root
#
# Exits 0 iff all 5 sub-tests pass.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PLUGIN_ROOT="${1:-$DEFAULT_ROOT}"

TESTS_DIR="$PLUGIN_ROOT/tests/modes"

SUBTESTS=(
  "command-frontmatter.sh"
  "agent-frontmatter.sh"
  "agent-frontmatter-disciplines.sh"
  "agent-frontmatter-pm-subagents.sh"
  "stop-hook-mode-routing.sh"
)

for st in "${SUBTESTS[@]}"; do
  if [ ! -f "$TESTS_DIR/$st" ]; then
    echo "MISSING SUB-TEST: $TESTS_DIR/$st" >&2
    exit 1
  fi
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not on PATH — required by stop-hook-mode-routing.sh" >&2
  exit 1
fi

PASS=0
FAIL=0

run_subtest() {
  local name="$1"
  local script="$TESTS_DIR/$name"
  printf "\n--- %s ---\n" "$name"
  if bash "$script" "$PLUGIN_ROOT"; then
    printf "[PASS] %s\n" "$name"
    PASS=$((PASS + 1))
  else
    printf "[FAIL] %s\n" "$name"
    FAIL=$((FAIL + 1))
  fi
}

for st in "${SUBTESTS[@]}"; do
  run_subtest "$st"
done

echo ""
echo "================================================================"
echo "MODES TEST SUMMARY: $PASS pass, $FAIL fail  (of ${#SUBTESTS[@]} sub-tests)"
echo "================================================================"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
