#!/usr/bin/env bash
# tests/claims/onedrive-detection.sh — verify OneDrive path detection in board-claim-acquire.sh
#
# OneDrive detection strategy (documented here per spec requirement):
#   board-claim-acquire.sh normalises backslashes to forward slashes, then checks
#   whether the resulting path contains the substring "/OneDrive/".  This covers
#   both POSIX paths (/home/user/OneDrive/project) and Windows paths converted
#   by Git Bash (C:\Users\user\OneDrive\project -> C:/Users/user/OneDrive/project).
#   The test synthesises a temp path containing "/OneDrive/" — no real OneDrive
#   installation required.
#
# Positive path: board-dir contains /OneDrive/ substring.
#   Assert: acquire emits "cloud-sync detected, bumped heartbeat to 60s / stale to 300s"
#
# Negative path: plain board-dir (no OneDrive substring).
#   Assert: acquire emits no "cloud-sync detected" line.
#
# Usage:
#   bash tests/claims/onedrive-detection.sh [<plugin-root>]
#
# Exits 0 iff both assertions pass.

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

TMP="$(python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="eb-od-").replace(chr(92), "/"))')"
cleanup() { rm -rf "$TMP" 2>/dev/null || true; }
trap cleanup EXIT

PASS=0
FAIL=0

report() {
  if [ "$1" = "0" ]; then
    printf "  [PASS] %s\n" "$2"
    PASS=$((PASS + 1))
  else
    printf "  [FAIL] %s — %s\n" "$2" "$3"
    FAIL=$((FAIL + 1))
  fi
}

BUMP_LOG_LINE="cloud-sync detected, bumped heartbeat to 60s / stale to 300s"

# --- Positive: path with /OneDrive/ substring ----------------------------
OD_BOARD_DIR="$TMP/Users/testuser/OneDrive/Projects/myproject/docs/boards/myboard"
mkdir -p "$OD_BOARD_DIR/_claims"

OD_OUTPUT="$TMP/od_positive.out"
set +e
bash "$ACQUIRE" "$OD_BOARD_DIR" "od-test-entry" "session-od-positive-$$" > "$OD_OUTPUT" 2>&1
OD_EXIT=$?
set -e

if grep -qF "$BUMP_LOG_LINE" "$OD_OUTPUT"; then
  report 0 "positive: OneDrive path emits cloud-sync bump log"
else
  report 1 "positive: OneDrive path emits cloud-sync bump log" \
    "output was: $(tr '\n' '|' < "$OD_OUTPUT")"
fi

# Acquire should succeed (exit 0) on OneDrive path
if [ "$OD_EXIT" -eq 0 ]; then
  report 0 "positive: acquire exits 0 on OneDrive path"
else
  report 1 "positive: acquire exits 0 on OneDrive path" "got exit $OD_EXIT"
fi

# --- Negative: plain path (no OneDrive) ----------------------------------
PLAIN_BOARD_DIR="$TMP/Users/testuser/Projects/myproject/docs/boards/myboard"
mkdir -p "$PLAIN_BOARD_DIR/_claims"

PLAIN_OUTPUT="$TMP/od_negative.out"
set +e
bash "$ACQUIRE" "$PLAIN_BOARD_DIR" "plain-test-entry" "session-plain-negative-$$" > "$PLAIN_OUTPUT" 2>&1
PLAIN_EXIT=$?
set -e

if grep -qF "cloud-sync detected" "$PLAIN_OUTPUT" 2>/dev/null; then
  report 1 "negative: plain path emits no cloud-sync bump log" \
    "unexpected output: $(tr '\n' '|' < "$PLAIN_OUTPUT")"
else
  report 0 "negative: plain path emits no cloud-sync bump log"
fi

if [ "$PLAIN_EXIT" -eq 0 ]; then
  report 0 "negative: acquire exits 0 on plain path"
else
  report 1 "negative: acquire exits 0 on plain path" "got exit $PLAIN_EXIT"
fi

echo ""
echo "================================================================"
echo "onedrive-detection: $PASS pass, $FAIL fail"
echo "================================================================"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
