#!/usr/bin/env bash
# tests/orchestration/automated.sh — Top-level runner for Tier 1 orchestration
# integration tests (NEXT-PHASE.md §Tier 1).
#
# These tests exercise the v0.2.2 PM and Worker pipelines end-to-end at the
# *deterministic substrate* layer. The LLM-dispatched subagent layer is not
# reachable from a shell harness, so each test mocks the subagent step by
# applying the documented deterministic effect (e.g. `suggested_next_needs`
# write-back) directly, and asserts the substrate scripts (claim acquire /
# release / reclaim, board-consolidate, board-index-check, board-audit-scratch)
# produce the contracted state transitions around it.
#
# Sub-tests (in order):
#   1.  pm-loop.sh                  — PM pipeline: scratch -> consolidate -> tidy -> audit
#   2.  worker-tdd-loop.sh          — Worker TDD discipline: tdd -> review transition
#   3.  worker-review-loop.sh       — Worker review discipline: review -> validate / regress
#   4.  worker-validate-loop.sh     — Worker validate discipline: validate -> resolved
#   5.  multi-worker-contention.sh  — Two concurrent workers on a shared pool
#   6.  board-rebuild-command.sh    — /board-rebuild command markdown structural lint
#   7.  board-graph-command.sh      — /board-graph command markdown structural lint
#   8.  active-workers-registry.sh  — v0.2.3 registry lifecycle (8 invariants)
#   9.  pm-fallback-heartbeat.sh    — v0.2.3 PM pre-flight refreshes registered/alive heartbeats
#   10. learnings-curator.sh        — v0.3.0 L### promotion + idempotency
#   11. board-migrate.sh            — v0.3.0 migration apply/rollback/status SHA256-idempotent
#   12. pause-resume-registry.sh    — v0.3.2 pause/resume cycle invariants (round-trip, isolation, identity)
#   13. subagent-fixtures.sh        — v0.3.2 subagent contract lint (Output contract heading + load-bearing keys + JSON parse)
#
# Usage:
#   bash tests/orchestration/automated.sh                # auto-detect plugin root
#   bash tests/orchestration/automated.sh <plugin-root>  # explicit root
#
# Exits 0 iff all sub-tests pass.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PLUGIN_ROOT="${1:-$DEFAULT_ROOT}"

TESTS_DIR="$PLUGIN_ROOT/tests/orchestration"

SUBTESTS=(
  "pm-loop.sh"
  "worker-tdd-loop.sh"
  "worker-review-loop.sh"
  "worker-validate-loop.sh"
  "multi-worker-contention.sh"
  "board-rebuild-command.sh"
  "board-graph-command.sh"
  "active-workers-registry.sh"
  "pm-fallback-heartbeat.sh"
  "learnings-curator.sh"
  "board-migrate.sh"
  "pause-resume-registry.sh"
  "subagent-fixtures.sh"
)

for st in "${SUBTESTS[@]}"; do
  if [ ! -f "$TESTS_DIR/$st" ]; then
    echo "MISSING SUB-TEST: $TESTS_DIR/$st" >&2
    exit 1
  fi
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not on PATH — required by orchestration tests" >&2
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
echo "ORCHESTRATION TEST SUMMARY: $PASS pass, $FAIL fail  (of ${#SUBTESTS[@]} sub-tests)"
echo "================================================================"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
