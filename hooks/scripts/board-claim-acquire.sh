#!/usr/bin/env bash
# board-claim-acquire.sh — atomic claim acquisition for _claims/<entry-id>/
#
# Usage:
#   board-claim-acquire.sh <board-dir> <entry-id> <session-id>
#
# Exit codes:
#   0 — claim acquired successfully
#   1 — contention (claim already held by an alive owner)
#   2 — stale claim exists but reclaim is not this script's job (caller should run reclaim-stale)
#
# OneDrive detection: if <board-dir> contains /OneDrive/ or \OneDrive\ (with
# forward or back slashes) the default heartbeat interval (30s) and stale
# threshold (180s) are bumped to 60s / 300s respectively.  This compensates for
# cloud-sync scan latency that can delay directory-creation visibility.
#
# File layout written on success:
#   <board-dir>/_claims/<entry-id>/owner.txt   — session_id, timestamp, cwd (3 labeled lines)
#   <board-dir>/_claims/<entry-id>/heartbeat.txt — single ISO UTC timestamp line

set -euo pipefail

BOARD_DIR="${1:-}"
ENTRY_ID="${2:-}"
SESSION_ID="${3:-}"

if [ -z "$BOARD_DIR" ] || [ -z "$ENTRY_ID" ] || [ -z "$SESSION_ID" ]; then
  echo "Usage: $0 <board-dir> <entry-id> <session-id>" >&2
  exit 1
fi

# --- Cloud-sync detection ------------------------------------------------
# Detect OneDrive (or other cloud-sync) by checking for /OneDrive/ or
# \OneDrive\ in the board path.  Normalise backslashes to forward slashes
# first so the check is a single string comparison.
BOARD_DIR_NORMALISED="${BOARD_DIR//\\//}"
HEARTBEAT_INTERVAL_SEC=30
STALE_CLAIM_SEC=180

if [[ "$BOARD_DIR_NORMALISED" == */OneDrive/* ]]; then
  HEARTBEAT_INTERVAL_SEC=60
  STALE_CLAIM_SEC=300
  echo "cloud-sync detected, bumped heartbeat to 60s / stale to 300s"
fi

export HEARTBEAT_INTERVAL_SEC
export STALE_CLAIM_SEC

# --- Paths ---------------------------------------------------------------
CLAIMS_DIR="${BOARD_DIR}/_claims"
CLAIM_DIR="${CLAIMS_DIR}/${ENTRY_ID}"
OWNER_FILE="${CLAIM_DIR}/owner.txt"
HEARTBEAT_FILE="${CLAIM_DIR}/heartbeat.txt"

NOW_ISO="$(python3 -c 'import datetime; print(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))')"
CWD="$(pwd)"

# Ensure the parent _claims/ directory exists (not the claim dir itself).
mkdir -p "$CLAIMS_DIR"

# --- Attempt atomic mkdir ------------------------------------------------
# Use plain `mkdir` (NOT `mkdir -p`) on the claim dir.  `mkdir` without -p
# fails atomically if the directory already exists; `mkdir -p` always exits 0
# regardless of whether the directory existed — so it cannot be used as a lock.
# This single mkdir call is the POSIX and NTFS atomic primitive for locking.
if ! mkdir "$CLAIM_DIR" 2>/dev/null; then
  # Directory already exists — check if owner is still alive
  if [ ! -f "$OWNER_FILE" ]; then
    # Claim dir exists but no owner.txt — treat as stale, signal caller
    exit 2
  fi

  EXISTING_SESSION="$(grep '^session_id:' "$OWNER_FILE" 2>/dev/null | awk '{print $2}' || true)"
  EXISTING_HEARTBEAT=""
  if [ -f "$HEARTBEAT_FILE" ]; then
    EXISTING_HEARTBEAT="$(cat "$HEARTBEAT_FILE" 2>/dev/null || true)"
  fi

  if [ -z "$EXISTING_HEARTBEAT" ]; then
    # No heartbeat — stale, signal caller
    exit 2
  fi

  # Check heartbeat age via python3 (portable; no date -d / date -j -f)
  HEARTBEAT_AGE_SEC="$(python3 - "$EXISTING_HEARTBEAT" "$STALE_CLAIM_SEC" <<'PY'
import sys, datetime

raw_ts = sys.argv[1].strip()
stale_sec = int(sys.argv[2])

try:
    hb = datetime.datetime.strptime(raw_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    now = datetime.datetime.now(datetime.timezone.utc)
    age = int((now - hb).total_seconds())
    print(age)
except Exception:
    # Unparseable timestamp — treat as stale
    print(stale_sec + 1)
PY
)"

  if [ "$HEARTBEAT_AGE_SEC" -ge "$STALE_CLAIM_SEC" ]; then
    # Claim is stale — signal caller to run reclaim-stale
    exit 2
  fi

  # Live owner holds the claim — contention
  exit 1
fi

# mkdir succeeded — we own the directory.  Write owner.txt then heartbeat.txt.
{
  printf 'session_id: %s\n' "$SESSION_ID"
  printf 'timestamp: %s\n'  "$NOW_ISO"
  printf 'cwd: %s\n'        "$CWD"
} > "$OWNER_FILE"

printf '%s\n' "$NOW_ISO" > "$HEARTBEAT_FILE"

# --- Read-verify own write -----------------------------------------------
# Guard against cloud-sync or AV that might rename/delay the file.
VERIFY_SESSION="$(grep '^session_id:' "$OWNER_FILE" 2>/dev/null | awk '{print $2}' || true)"
if [ "$VERIFY_SESSION" != "$SESSION_ID" ]; then
  # Our write was overwritten by another process between mkdir and write —
  # release and report contention.
  rm -rf "$CLAIM_DIR" 2>/dev/null || true
  exit 1
fi

VERIFY_HB="$(cat "$HEARTBEAT_FILE" 2>/dev/null || true)"
if [ -z "$VERIFY_HB" ]; then
  rm -rf "$CLAIM_DIR" 2>/dev/null || true
  exit 1
fi

exit 0
