#!/usr/bin/env bash
# board-active-workers-register.sh — append-or-update an entry in
# .engineering-board/active-workers.json. See references/active-workers-registry.md
# for the full contract.
#
# Usage:
#   board-active-workers-register.sh <session-id> <mode> <discipline> <started-at-iso>
#
# Arguments:
#   session-id     UUID-like string; may be empty for the pre-first-Stop window.
#   mode           "pm" or "worker".
#   discipline     "tdd" | "review" | "validate" for worker; "null" or empty for pm.
#   started-at-iso ISO 8601 UTC second-precision timestamp; pass "now" to compute here.
#
# Behaviour:
#   - GC pass: removes entries whose last_seen is older than 2*staleClaimSec.
#   - If session-id already present, bumps last_seen.
#   - Otherwise appends a new entry.
#   - Atomic-rename write through tmp file in same directory.
#   - mkdir-based lockfile for serialisation.
#
# Exit codes:
#   0 — registered (or updated).
#   1 — bad arguments.
#   2 — lock not acquired within retry budget.

set -euo pipefail

SESSION_ID="${1:-}"
MODE="${2:-}"
DISCIPLINE="${3:-}"
STARTED_AT="${4:-now}"

if [ -z "$MODE" ]; then
  echo "Usage: $0 <session-id> <mode> <discipline> <started-at-iso>" >&2
  exit 1
fi
case "$MODE" in
  pm|worker) ;;
  *) echo "register: bad mode '$MODE'" >&2; exit 1 ;;
esac
if [ "$MODE" = "worker" ]; then
  case "$DISCIPLINE" in
    tdd|review|validate) ;;
    *) echo "register: worker mode requires discipline in {tdd,review,validate}, got '$DISCIPLINE'" >&2; exit 1 ;;
  esac
fi

if [ -z "${CLAUDE_PROJECT_DIR:-}" ]; then
  echo "register: CLAUDE_PROJECT_DIR not set" >&2
  exit 1
fi

STATE_DIR="${CLAUDE_PROJECT_DIR}/.engineering-board"
REGISTRY="${STATE_DIR}/active-workers.json"
LOCK_DIR="${STATE_DIR}/active-workers.json.lock"
TMP="${STATE_DIR}/active-workers.json.tmp.$$"

mkdir -p "$STATE_DIR"

# --- Resolve started_at ----------------------------------------------------
if [ "$STARTED_AT" = "now" ]; then
  STARTED_AT="$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))')"
fi
NOW_ISO="$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))')"

# --- Detect cloud-sync for staleClaimSec ----------------------------------
BOARD_DIR_LOWER="$(echo "$CLAUDE_PROJECT_DIR" | tr '[:upper:]' '[:lower:]')"
STALE_CLAIM_SEC=180
for marker in "onedrive" "dropbox" "icloud" "google drive" "googledrive" "box sync" "boxsync"; do
  case "$BOARD_DIR_LOWER" in
    *"$marker"*) STALE_CLAIM_SEC=300; break ;;
  esac
done
GC_THRESHOLD=$((STALE_CLAIM_SEC * 2))

# --- Acquire lock ----------------------------------------------------------
ATTEMPTS=0
while ! mkdir "$LOCK_DIR" 2>/dev/null; do
  ATTEMPTS=$((ATTEMPTS + 1))
  if [ "$ATTEMPTS" -ge 5 ]; then
    echo "register: lock not acquired after 5 attempts (lockfile: $LOCK_DIR)" >&2
    exit 2
  fi
  sleep 0.1
done

cleanup_lock() { rmdir "$LOCK_DIR" 2>/dev/null || true; rm -f "$TMP" 2>/dev/null || true; }
trap cleanup_lock EXIT

# --- Mutate registry via python3 -------------------------------------------
DISCIPLINE_PY="$DISCIPLINE"
if [ "$MODE" = "pm" ]; then DISCIPLINE_PY=""; fi

python3 - "$REGISTRY" "$TMP" "$SESSION_ID" "$MODE" "$DISCIPLINE_PY" "$STARTED_AT" "$NOW_ISO" "$CLAUDE_PROJECT_DIR" "$GC_THRESHOLD" <<'PY'
import json, os, sys, datetime

registry_path, tmp_path, session_id, mode, discipline, started_at, now_iso, cwd, gc_threshold = sys.argv[1:]
gc_threshold = int(gc_threshold)

# Load existing.
entries = []
if os.path.isfile(registry_path):
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            entries = json.load(f)
        if not isinstance(entries, list):
            entries = []
    except Exception:
        # Corrupt or unreadable — start fresh; the lazy GC reclaims any lost data.
        entries = []

def parse_iso(s):
    if not s: return None
    try:
        # Strict ISO 8601 with Z suffix.
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    except Exception:
        return None

now_dt = parse_iso(now_iso)

# --- GC pass: drop entries whose last_seen is older than gc_threshold ------
def is_alive(entry):
    last_seen = parse_iso(entry.get("last_seen", ""))
    if last_seen is None or now_dt is None:
        return True  # keep, can't tell
    age = (now_dt - last_seen).total_seconds()
    return age < gc_threshold

entries = [e for e in entries if is_alive(e)]

# --- Find / append / update ------------------------------------------------
disc_field = discipline if discipline else None

found = None
for e in entries:
    if e.get("session_id") == session_id and session_id != "":
        found = e
        break

if found is not None:
    # Update last_seen and mode/discipline if they changed.
    found["last_seen"] = now_iso
    found["mode"] = mode
    found["discipline"] = disc_field
    found["cwd"] = cwd
    # paused stays as-is on a re-register.
else:
    entries.append({
        "session_id":      session_id,
        "started_at":      started_at,
        "last_seen":       now_iso,
        "mode":            mode,
        "discipline":      disc_field,
        "cwd":             cwd,
        "claim_ids_held":  [],
        "paused":          False,
    })

# --- Canonicalise claim_ids_held order -------------------------------------
for e in entries:
    cl = e.get("claim_ids_held", [])
    if isinstance(cl, list):
        e["claim_ids_held"] = sorted(cl)

with open(tmp_path, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=2)
    f.write("\n")
PY

# --- Atomic-rename ---------------------------------------------------------
# NTFS may transiently EBUSY the rename if a reader has the file open.
RENAME_OK=0
for attempt in 1 2 3; do
  if mv "$TMP" "$REGISTRY" 2>/dev/null; then
    RENAME_OK=1
    break
  fi
  sleep 0.25
done
if [ "$RENAME_OK" -ne 1 ]; then
  echo "register: atomic-rename failed after 3 attempts" >&2
  exit 2
fi

cleanup_lock
trap - EXIT
exit 0
