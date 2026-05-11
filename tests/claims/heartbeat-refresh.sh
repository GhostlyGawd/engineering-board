#!/usr/bin/env bash
set -euo pipefail

# tests/claims/heartbeat-refresh.sh
# Tests: acquire claim, heartbeat refreshes mtime, wrong session_id rejected with exit 3.

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../hooks/scripts" && pwd)"
TMPDIR_BASE="$(mktemp -d)"
trap 'rm -rf "${TMPDIR_BASE}"' EXIT

BOARD_DIR="${TMPDIR_BASE}/board"
ENTRY_ID="B001"
SESSION_A="session-hb-$(python3 -c 'import uuid; print(uuid.uuid4().hex[:8])')"
SESSION_B="session-wrong-$(python3 -c 'import uuid; print(uuid.uuid4().hex[:8])')"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS+1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

echo "=== heartbeat-refresh ==="

# Setup: create claim directory manually (simulating acquire)
CLAIM_DIR="${BOARD_DIR}/_claims/${ENTRY_ID}"
mkdir -p "${CLAIM_DIR}"
NOW_ISO="$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))')"
printf 'session_id: %s\ntimestamp: %s\ncwd: %s\n' "${SESSION_A}" "${NOW_ISO}" "$(pwd)" > "${CLAIM_DIR}/owner.txt"
printf '%s\n' "${NOW_ISO}" > "${CLAIM_DIR}/heartbeat.txt"

# Get initial mtime using python3 with path as argv (avoids Windows backslash escaping)
MTIME_BEFORE="$(python3 -c 'import os,sys; print(int(os.path.getmtime(sys.argv[1])))' "${CLAIM_DIR}/heartbeat.txt")"

# Sleep 1 second so mtime can advance
sleep 1

# Heartbeat with correct session_id
exit_code=0
bash "${SCRIPTS_DIR}/board-claim-heartbeat.sh" "${BOARD_DIR}" "${ENTRY_ID}" "${SESSION_A}" && exit_code=$? || exit_code=$?
if [ "${exit_code}" -eq 0 ]; then
  pass "heartbeat exits 0 with correct session_id"
else
  fail "heartbeat exits non-zero (${exit_code}) with correct session_id"
fi

MTIME_AFTER="$(python3 -c 'import os,sys; print(int(os.path.getmtime(sys.argv[1])))' "${CLAIM_DIR}/heartbeat.txt")"

if [ "${MTIME_AFTER}" -gt "${MTIME_BEFORE}" ]; then
  pass "heartbeat.txt mtime advanced after refresh"
else
  fail "heartbeat.txt mtime did NOT advance (before=${MTIME_BEFORE} after=${MTIME_AFTER})"
fi

# Attempt heartbeat with wrong session_id — must exit 3
exit_code=0
bash "${SCRIPTS_DIR}/board-claim-heartbeat.sh" "${BOARD_DIR}" "${ENTRY_ID}" "${SESSION_B}" && exit_code=$? || exit_code=$?
if [ "${exit_code}" -eq 3 ]; then
  pass "heartbeat exits 3 on wrong session_id"
else
  fail "heartbeat should exit 3 on wrong session_id, got ${exit_code}"
fi

echo ""
echo "heartbeat-refresh: ${PASS} passed, ${FAIL} failed"
if [ "${FAIL}" -gt 0 ]; then
  exit 1
fi
exit 0
