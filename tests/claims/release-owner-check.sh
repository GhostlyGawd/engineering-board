#!/usr/bin/env bash
set -euo pipefail

# tests/claims/release-owner-check.sh
# Tests: non-owner release rejected (exit 3, claim still present);
#        owner release succeeds (exit 0, claim dir gone).

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../hooks/scripts" && pwd)"
TMPDIR_BASE="$(mktemp -d)"
trap 'rm -rf "${TMPDIR_BASE}"' EXIT

BOARD_DIR="${TMPDIR_BASE}/board"
ENTRY_ID="B002"
SESSION_A="session-owner-$(python3 -c 'import uuid; print(uuid.uuid4().hex[:8])')"
SESSION_B="session-nonowner-$(python3 -c 'import uuid; print(uuid.uuid4().hex[:8])')"

PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS+1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }

echo "=== release-owner-check ==="

# Setup: create claim owned by SESSION_A
CLAIM_DIR="${BOARD_DIR}/_claims/${ENTRY_ID}"
mkdir -p "${CLAIM_DIR}"
NOW_ISO="$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))')"
printf 'session_id: %s\ntimestamp: %s\ncwd: %s\n' "${SESSION_A}" "${NOW_ISO}" "$(pwd)" > "${CLAIM_DIR}/owner.txt"
printf '%s\n' "${NOW_ISO}" > "${CLAIM_DIR}/heartbeat.txt"

# Attempt release with SESSION_B (non-owner) — must exit 3
exit_code=0
bash "${SCRIPTS_DIR}/board-claim-release.sh" "${BOARD_DIR}" "${ENTRY_ID}" "${SESSION_B}" && exit_code=$? || exit_code=$?
if [ "${exit_code}" -eq 3 ]; then
  pass "non-owner release exits 3"
else
  fail "non-owner release should exit 3, got ${exit_code}"
fi

# Claim dir must still exist after failed release attempt
if [ -d "${CLAIM_DIR}" ]; then
  pass "claim dir still present after non-owner release attempt"
else
  fail "claim dir was removed by non-owner release — should not happen"
fi

# Release with SESSION_A (owner) — must exit 0
exit_code=0
bash "${SCRIPTS_DIR}/board-claim-release.sh" "${BOARD_DIR}" "${ENTRY_ID}" "${SESSION_A}" && exit_code=$? || exit_code=$?
if [ "${exit_code}" -eq 0 ]; then
  pass "owner release exits 0"
else
  fail "owner release should exit 0, got ${exit_code}"
fi

# Claim dir must be gone after owner release
if [ ! -d "${CLAIM_DIR}" ]; then
  pass "claim dir removed after owner release"
else
  fail "claim dir still present after owner release — should be gone"
fi

echo ""
echo "release-owner-check: ${PASS} passed, ${FAIL} failed"
if [ "${FAIL}" -gt 0 ]; then
  exit 1
fi
exit 0
