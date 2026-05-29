#!/usr/bin/env bash
# board-pm-fallback-heartbeat.sh — PM-side claim-heartbeat fallback.
#
# Invoked by the PM Stop pipeline (stop-hook-procedure.md Section 3-PM
# pre-flight). For each claim in _claims/<entry-id>/, looks up the owner
# session in .engineering-board/active-workers.json and refreshes the claim
# heartbeat IFF:
#   1. The owner session is present in the registry.
#   2. The owner session is alive: (now - last_seen) < 2 * staleClaimSec.
#   3. The owner session is NOT paused (paused: false).
#
# Skipped claims fall back to the normal stale-claim reclaim path
# (board-claim-reclaim-stale.sh) on the next tick.
#
# Usage:
#   board-pm-fallback-heartbeat.sh <board-dir>
#
# Output: one JSON line per claim examined to stdout.
#   { "entry_id": "...", "decision": "refreshed|skipped|orphan",
#     "reason": "...", "owner_session_id": "..." }
#
# Exit: always 0 (per-claim failures logged but do not abort the run).

set -euo pipefail

BOARD_DIR="${1:-}"
if [ -z "$BOARD_DIR" ]; then
  echo '{"error":"usage: board-pm-fallback-heartbeat.sh <board-dir>"}' >&2
  exit 1
fi

if [ -z "${CLAUDE_PROJECT_DIR:-}" ]; then
  echo '{"error":"CLAUDE_PROJECT_DIR not set"}' >&2
  exit 1
fi

CLAIMS_DIR="$BOARD_DIR/_claims"
REGISTRY="$CLAUDE_PROJECT_DIR/.engineering-board/active-workers.json"

if [ ! -d "$CLAIMS_DIR" ]; then
  exit 0
fi
if [ ! -f "$REGISTRY" ]; then
  exit 0
fi

# Cloud-sync detection (mirrors board-claim-acquire.sh / reclaim-stale.sh).
BOARD_DIR_LOWER="$(echo "$BOARD_DIR" | tr '[:upper:]' '[:lower:]')"
STALE_CLAIM_SEC=180
for marker in "onedrive" "dropbox" "icloud" "google drive" "googledrive" "box sync" "boxsync"; do
  case "$BOARD_DIR_LOWER" in
    *"$marker"*) STALE_CLAIM_SEC=300; break ;;
  esac
done
LIVENESS_THRESHOLD=$((STALE_CLAIM_SEC * 2))

python3 - "$CLAIMS_DIR" "$REGISTRY" "$LIVENESS_THRESHOLD" <<'PY'
import json, os, sys, time, datetime

claims_dir, registry_path, liveness_threshold = sys.argv[1:]
liveness_threshold = int(liveness_threshold)

# Load registry.
try:
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)
    if not isinstance(registry, list):
        registry = []
except Exception:
    registry = []

now = datetime.datetime.now(datetime.timezone.utc)
now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")

def parse_iso(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    except Exception:
        return None

# Index registry by session_id.
reg_by_session = {e.get("session_id"): e for e in registry if e.get("session_id")}

# Walk claims.
for entry in sorted(os.listdir(claims_dir)):
    if entry.startswith("_"):
        continue
    claim_path = os.path.join(claims_dir, entry)
    if not os.path.isdir(claim_path):
        continue
    owner_file = os.path.join(claim_path, "owner.txt")
    heartbeat_file = os.path.join(claim_path, "heartbeat.txt")
    if not os.path.isfile(owner_file):
        print(json.dumps({"entry_id": entry, "decision": "orphan",
                          "reason": "no_owner_file", "owner_session_id": None}))
        continue

    owner_session_id = None
    try:
        with open(owner_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("session_id:"):
                    owner_session_id = line.split(":", 1)[1].strip()
                    break
    except Exception:
        owner_session_id = None
    if not owner_session_id:
        print(json.dumps({"entry_id": entry, "decision": "orphan",
                          "reason": "owner_file_unparseable", "owner_session_id": None}))
        continue

    reg = reg_by_session.get(owner_session_id)
    if reg is None:
        print(json.dumps({"entry_id": entry, "decision": "skipped",
                          "reason": "owner_not_in_registry", "owner_session_id": owner_session_id}))
        continue

    if reg.get("paused") is True:
        print(json.dumps({"entry_id": entry, "decision": "skipped",
                          "reason": "owner_paused", "owner_session_id": owner_session_id}))
        continue

    last_seen = parse_iso(reg.get("last_seen", ""))
    if last_seen is None:
        print(json.dumps({"entry_id": entry, "decision": "skipped",
                          "reason": "owner_last_seen_unparseable", "owner_session_id": owner_session_id}))
        continue
    age = (now - last_seen).total_seconds()
    if age >= liveness_threshold:
        print(json.dumps({"entry_id": entry, "decision": "skipped",
                          "reason": "owner_stale", "owner_session_id": owner_session_id, "age_sec": age}))
        continue

    # Refresh heartbeat. Atomic-rename through tmp.
    tmp_file = heartbeat_file + ".tmp"
    try:
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write(now_iso + "\n")
        os.replace(tmp_file, heartbeat_file)
        print(json.dumps({"entry_id": entry, "decision": "refreshed",
                          "reason": "owner_alive", "owner_session_id": owner_session_id,
                          "refreshed_at": now_iso}))
    except Exception as ex:
        print(json.dumps({"entry_id": entry, "decision": "skipped",
                          "reason": f"refresh_failed:{ex}", "owner_session_id": owner_session_id}))
PY

exit 0
