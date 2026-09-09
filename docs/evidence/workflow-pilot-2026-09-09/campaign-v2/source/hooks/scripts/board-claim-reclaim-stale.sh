#!/usr/bin/env bash
# board-claim-reclaim-stale.sh — Scan _claims/ and remove stale claim directories.
#
# A claim is stale when (now - heartbeat.txt mtime) > stale threshold.
# Uses python3 for mtime arithmetic (no date -d / date -j -f; both non-portable).
#
# Defaults:
#   STALE_SEC=180   (local filesystem)
#   CLOUD_STALE_SEC=300  (cloud-synced paths: OneDrive, Dropbox, iCloud, Google Drive, Box)
#
# Cloud-sync detection: board dir path contains any of the cloud-sync markers
# (case-insensitive). Same detection logic as board-claim-acquire.sh.
#
# Output: JSON-lines to stdout, one record per claim dir examined.
#   { "scratch_id": "...", "decision": "reclaimed|kept|no_heartbeat_skipped",
#     "reason": "...", "age_sec": <float|null> }
#
# Exit: always 0 (reclaim failures are logged but do not abort the run).
#
# Usage:
#   board-claim-reclaim-stale.sh <board-dir>

set -euo pipefail

BOARD_DIR="${1:-}"
if [ -z "$BOARD_DIR" ]; then
  echo '{"error":"usage: board-claim-reclaim-stale.sh <board-dir>"}' >&2
  exit 1
fi

CLAIMS_DIR="$BOARD_DIR/_claims"
RECLAIMED_LOG="$CLAIMS_DIR/_reclaimed.log"

if [ ! -d "$CLAIMS_DIR" ]; then
  # Nothing to do — no _claims/ dir yet.
  exit 0
fi

# ── Cloud-sync detection ─────────────────────────────────────────────────────
# Check if the board path sits inside a cloud-sync folder. Uses the same
# substring markers as board-claim-acquire.sh so thresholds stay in sync.
BOARD_DIR_LOWER="$(echo "$BOARD_DIR" | tr '[:upper:]' '[:lower:]')"
IS_CLOUD=0
for marker in "onedrive" "dropbox" "icloud" "google drive" "googledrive" "box sync" "boxsync"; do
  case "$BOARD_DIR_LOWER" in
    *"$marker"*) IS_CLOUD=1; break ;;
  esac
done

if [ "$IS_CLOUD" -eq 1 ]; then
  STALE_SEC=300
else
  STALE_SEC=180
fi

# Allow env override for tests.
STALE_SEC="${EB_STALE_SEC:-$STALE_SEC}"

# ── Python mtime helper ───────────────────────────────────────────────────────
# Reads heartbeat.txt mtime, computes age, returns JSON decision record.
RECLAIM_PY='
import sys, os, time, json

claims_dir = sys.argv[1]
stale_sec   = float(sys.argv[2])
reclaimed_log = sys.argv[3]

now = time.time()
claim_dirs = []
try:
    for name in os.listdir(claims_dir):
        full = os.path.join(claims_dir, name)
        if name.startswith("_") or not os.path.isdir(full):
            continue
        claim_dirs.append((name, full))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(0)

for entry_id, claim_path in claim_dirs:
    hb_path = os.path.join(claim_path, "heartbeat.txt")
    owner_path = os.path.join(claim_path, "owner.txt")

    if not os.path.isfile(hb_path):
        print(json.dumps({
            "scratch_id": entry_id,
            "decision": "no_heartbeat_skipped",
            "reason": "heartbeat.txt missing — cannot determine staleness",
            "age_sec": None
        }))
        continue

    try:
        age = now - os.path.getmtime(hb_path)
    except Exception as e:
        print(json.dumps({
            "scratch_id": entry_id,
            "decision": "no_heartbeat_skipped",
            "reason": f"mtime read error: {e}",
            "age_sec": None
        }))
        continue

    if age <= stale_sec:
        print(json.dumps({
            "scratch_id": entry_id,
            "decision": "kept",
            "reason": "owner_still_fresh",
            "age_sec": round(age, 2)
        }))
        continue

    # Stale — archive owner info then remove claim dir.
    owner_info = ""
    if os.path.isfile(owner_path):
        try:
            owner_info = open(owner_path, "r", encoding="utf-8").read().strip()
        except Exception:
            owner_info = "(unreadable)"

    log_entry = json.dumps({
        "reclaimed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "entry_id": entry_id,
        "reason": "stale_no_heartbeat",
        "age_sec": round(age, 2),
        "stale_threshold_sec": stale_sec,
        "owner_info": owner_info
    })

    # Append to _reclaimed.log (best-effort).
    try:
        with open(reclaimed_log, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    except Exception as le:
        pass  # log failure is non-fatal

    # Remove the claim directory.
    removed = False
    try:
        import shutil
        shutil.rmtree(claim_path)
        removed = True
    except Exception as re:
        pass

    print(json.dumps({
        "scratch_id": entry_id,
        "decision": "reclaimed" if removed else "reclaim_failed",
        "reason": "stale_no_heartbeat",
        "age_sec": round(age, 2)
    }))
'

python3 - "$CLAIMS_DIR" "$STALE_SEC" "$RECLAIMED_LOG" <<< "$RECLAIM_PY"
