#!/usr/bin/env bash
# tests/claims/automated.sh — Top-level runner for all M2.2.a claim tests.
#
# Mirrors the style of tests/smoke/automated.sh: runs each sub-test,
# accumulates pass/fail counts, exits 0 iff ALL sub-tests exit 0.
#
# Sub-tests (in order):
#   1. race-acquire.sh       — two-process race, 20 iterations
#   2. heartbeat-refresh.sh  — atomic heartbeat refresh + owner-mismatch guard
#   3. release-owner-check.sh — owner-verified release
#   4. reclaim-stale.sh      — fresh/stale/very-stale fixture classification
#   5. onedrive-detection.sh — OneDrive path bumps defaults; plain path does not
#
# Usage:
#   bash tests/claims/automated.sh                # auto-detect plugin root
#   bash tests/claims/automated.sh <plugin-root>  # explicit root
#
# Exits 0 iff all 5 sub-tests pass.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PLUGIN_ROOT="${1:-$DEFAULT_ROOT}"

TESTS_DIR="$PLUGIN_ROOT/tests/claims"

# ── Sub-test manifest ─────────────────────────────────────────────────────────
SUBTESTS=(
  "race-acquire.sh"
  "heartbeat-refresh.sh"
  "release-owner-check.sh"
  "reclaim-stale.sh"
  "onedrive-detection.sh"
)

# Verify all sub-test scripts exist before running anything.
for st in "${SUBTESTS[@]}"; do
  if [ ! -f "$TESTS_DIR/$st" ]; then
    echo "MISSING SUB-TEST: $TESTS_DIR/$st" >&2
    exit 1
  fi
done

# Verify python3 is available (required by several sub-tests).
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not on PATH — required by claim tests" >&2
  exit 1
fi

# ── Runner ────────────────────────────────────────────────────────────────────
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

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "================================================================"
echo "CLAIMS TEST SUMMARY: $PASS pass, $FAIL fail  (of ${#SUBTESTS[@]} sub-tests)"
echo "================================================================"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
