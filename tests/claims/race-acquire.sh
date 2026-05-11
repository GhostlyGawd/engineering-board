#!/usr/bin/env bash
# tests/claims/race-acquire.sh — two-process race test for board-claim-acquire.sh
#
# Forks two background invocations of board-claim-acquire.sh against the same
# entry-id with a random startup jitter <= 50ms.  Asserts that exactly one
# exits 0 (success) and exactly one exits 1 (contention).  Runs 20 iterations
# to surface ordering issues.
#
# Usage:
#   bash tests/claims/race-acquire.sh [<plugin-root>]
#
# Exits 0 iff all 20 iterations pass.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PLUGIN_ROOT="${1:-$DEFAULT_ROOT}"

ACQUIRE="$PLUGIN_ROOT/hooks/scripts/board-claim-acquire.sh"

if [ ! -f "$ACQUIRE" ]; then
  echo "MISSING: $ACQUIRE" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not on PATH — required" >&2
  exit 1
fi

TMP="$(python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="eb-race-").replace(chr(92), "/"))')"
cleanup() { rm -rf "$TMP" 2>/dev/null || true; }
trap cleanup EXIT

BOARD_DIR="$TMP/board"
mkdir -p "$BOARD_DIR/_claims"

ENTRY_ID="test-race-entry"

PASS=0
FAIL=0

report() {
  if [ "$1" = "0" ]; then
    printf "  [PASS] iteration %s\n" "$2"
    PASS=$((PASS + 1))
  else
    printf "  [FAIL] iteration %s — %s\n" "$2" "$3"
    FAIL=$((FAIL + 1))
  fi
}

for i in $(seq 1 20); do
  # Clean up any leftover claim dir from previous iteration
  rm -rf "${BOARD_DIR}/_claims/${ENTRY_ID}" 2>/dev/null || true

  # Random jitter 0-50ms for each racer (in milliseconds, sleep uses seconds)
  JITTER_A="$(python3 -c 'import random; print(random.randint(0,50) / 1000.0)')"
  JITTER_B="$(python3 -c 'import random; print(random.randint(0,50) / 1000.0)')"

  EXIT_A_FILE="$TMP/exit_a_$i"
  EXIT_B_FILE="$TMP/exit_b_$i"

  # Fork racer A.
  # Use 'rc=...; echo $rc' pattern so set -e cannot abort the subshell between
  # the acquire call and the write: we assign to a variable (assignment never
  # triggers set -e even on non-zero exit in bash), then write the variable.
  (
    sleep "$JITTER_A"
    rc=0; bash "$ACQUIRE" "$BOARD_DIR" "$ENTRY_ID" "session-A-$i" > /dev/null 2>&1 || rc=$?
    echo "$rc" > "$EXIT_A_FILE"
  ) &
  PID_A=$!

  # Fork racer B — same pattern
  (
    sleep "$JITTER_B"
    rc=0; bash "$ACQUIRE" "$BOARD_DIR" "$ENTRY_ID" "session-B-$i" > /dev/null 2>&1 || rc=$?
    echo "$rc" > "$EXIT_B_FILE"
  ) &
  PID_B=$!

  wait $PID_A 2>/dev/null || true
  wait $PID_B 2>/dev/null || true

  EXIT_A="$(cat "$EXIT_A_FILE" 2>/dev/null || echo "missing")"
  EXIT_B="$(cat "$EXIT_B_FILE" 2>/dev/null || echo "missing")"

  # Exactly one must exit 0 and the other exit 1
  if { [ "$EXIT_A" = "0" ] && [ "$EXIT_B" = "1" ]; } || \
     { [ "$EXIT_A" = "1" ] && [ "$EXIT_B" = "0" ]; }; then
    report 0 "$i"
  else
    report 1 "$i" "exit_A=$EXIT_A exit_B=$EXIT_B (expected one 0 and one 1)"
  fi
done

echo ""
echo "================================================================"
echo "race-acquire: $PASS pass, $FAIL fail (20 iterations)"
echo "================================================================"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
