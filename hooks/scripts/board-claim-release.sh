#!/usr/bin/env bash
set -euo pipefail

# board-claim-release.sh
# Usage: board-claim-release.sh <board-dir> <entry-id> <session-id>
# Removes _claims/<entry-id>/ directory. Only the claim owner may release.
# NTFS retry-on-EBUSY: 3 attempts at 250ms intervals with jitter.
# Exit codes: 0=released, 3=owner mismatch, 4=all retries exhausted

BOARD_DIR="${1:?board-dir required}"
ENTRY_ID="${2:?entry-id required}"
SESSION_ID="${3:?session-id required}"

CLAIM_DIR="${BOARD_DIR}/_claims/${ENTRY_ID}"
OWNER_FILE="${CLAIM_DIR}/owner.txt"

if [ ! -d "${CLAIM_DIR}" ]; then
  echo "ERROR: claim not found: ${CLAIM_DIR}" >&2
  exit 3
fi

if [ ! -f "${OWNER_FILE}" ]; then
  echo "ERROR: owner.txt missing in claim dir: ${CLAIM_DIR}" >&2
  exit 3
fi

OWNER_SESSION_ID="$(grep '^session_id:' "${OWNER_FILE}" | awk '{print $2}')"

if [ "${OWNER_SESSION_ID}" != "${SESSION_ID}" ]; then
  echo "ERROR: session_id mismatch — owner is '${OWNER_SESSION_ID}', caller is '${SESSION_ID}'" >&2
  exit 3
fi

# NTFS retry loop: up to 3 attempts with 250ms base + random jitter (0-50ms)
MAX_ATTEMPTS=3
attempt=0
while [ ${attempt} -lt ${MAX_ATTEMPTS} ]; do
  attempt=$((attempt + 1))
  if rm -rf "${CLAIM_DIR}" 2>/dev/null; then
    echo "released: ${ENTRY_ID}"
    exit 0
  fi
  if [ ${attempt} -lt ${MAX_ATTEMPTS} ]; then
    jitter="$(python3 -c 'import random; print(random.randint(0,50))')"
    sleep_ms=$((250 + jitter))
    python3 -c "import time; time.sleep(${sleep_ms}/1000.0)"
  fi
done

echo "ERROR: failed to remove claim dir after ${MAX_ATTEMPTS} attempts: ${CLAIM_DIR}" >&2
exit 4
