#!/usr/bin/env bash
set -euo pipefail

# board-claim-heartbeat.sh
# Usage: board-claim-heartbeat.sh <board-dir> <entry-id> <session-id>
# Atomically refreshes heartbeat.txt for the named claim.
# Only the current claim owner (matching owner.txt session_id) may heartbeat.
# Exit codes: 0=refreshed, 3=owner mismatch (not the claim holder)

BOARD_DIR="${1:?board-dir required}"
ENTRY_ID="${2:?entry-id required}"
SESSION_ID="${3:?session-id required}"

CLAIM_DIR="${BOARD_DIR}/_claims/${ENTRY_ID}"
OWNER_FILE="${CLAIM_DIR}/owner.txt"
HEARTBEAT_FILE="${CLAIM_DIR}/heartbeat.txt"
HEARTBEAT_TMP="${CLAIM_DIR}/heartbeat.tmp"

if [ ! -f "${OWNER_FILE}" ]; then
  echo "ERROR: claim not found: ${CLAIM_DIR}" >&2
  exit 3
fi

OWNER_SESSION_ID="$(grep '^session_id:' "${OWNER_FILE}" | awk '{print $2}')"

if [ "${OWNER_SESSION_ID}" != "${SESSION_ID}" ]; then
  echo "ERROR: session_id mismatch — owner is '${OWNER_SESSION_ID}', caller is '${SESSION_ID}'" >&2
  exit 3
fi

NOW_ISO="$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))')"

printf '%s\n' "${NOW_ISO}" > "${HEARTBEAT_TMP}"
mv "${HEARTBEAT_TMP}" "${HEARTBEAT_FILE}"

echo "heartbeat refreshed: ${ENTRY_ID} at ${NOW_ISO}"
exit 0
