#!/usr/bin/env bash
# board-active-workers-bump.sh — refresh last_seen, optionally update
# claim_ids_held, optionally flip paused, for an existing entry in
# .engineering-board/active-workers.json.
#
# Usage:
#   board-active-workers-bump.sh <session-id> [--claim-acquire <entry-id>]
#                                             [--claim-release <entry-id>]
#                                             [--paused true|false]
#
# Behaviour:
#   - Bumps last_seen on every successful invocation.
#   - --claim-acquire adds entry-id to claim_ids_held (deduped, sorted).
#   - --claim-release removes entry-id from claim_ids_held.
#   - --paused sets the paused field.
#   - If session_id is not present, exits 0 silently (no auto-register).
#   - Multiple flags may be combined in one call.
#   - Atomic-rename write through tmp file in same directory.
#
# Exit codes:
#   0 — bumped (or no-op if session absent).
#   1 — bad arguments.
#   2 — lock not acquired within retry budget.

set -euo pipefail

SESSION_ID="${1:-}"
if [ -z "$SESSION_ID" ]; then
  echo "Usage: $0 <session-id> [--claim-acquire <id>] [--claim-release <id>] [--paused true|false]" >&2
  exit 1
fi
shift

CLAIM_ACQUIRE=""
CLAIM_RELEASE=""
PAUSED_SET=""

while [ $# -gt 0 ]; do
  case "$1" in
    --claim-acquire) CLAIM_ACQUIRE="${2:-}"; shift 2 ;;
    --claim-release) CLAIM_RELEASE="${2:-}"; shift 2 ;;
    --paused)        PAUSED_SET="${2:-}";    shift 2 ;;
    *) echo "bump: unknown flag '$1'" >&2; exit 1 ;;
  esac
done

if [ -n "$PAUSED_SET" ]; then
  case "$PAUSED_SET" in
    true|false) ;;
    *) echo "bump: --paused must be 'true' or 'false', got '$PAUSED_SET'" >&2; exit 1 ;;
  esac
fi

if [ -z "${CLAUDE_PROJECT_DIR:-}" ]; then
  echo "bump: CLAUDE_PROJECT_DIR not set" >&2
  exit 1
fi

STATE_DIR="${CLAUDE_PROJECT_DIR}/.engineering-board"
REGISTRY="${STATE_DIR}/active-workers.json"
LOCK_DIR="${STATE_DIR}/active-workers.json.lock"
TMP="${STATE_DIR}/active-workers.json.tmp.$$"

if [ ! -f "$REGISTRY" ]; then
  exit 0
fi

NOW_ISO="$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))')"

ATTEMPTS=0
while ! mkdir "$LOCK_DIR" 2>/dev/null; do
  ATTEMPTS=$((ATTEMPTS + 1))
  if [ "$ATTEMPTS" -ge 5 ]; then
    echo "bump: lock not acquired after 5 attempts" >&2
    exit 2
  fi
  sleep 0.1
done

cleanup_lock() { rmdir "$LOCK_DIR" 2>/dev/null || true; rm -f "$TMP" 2>/dev/null || true; }
trap cleanup_lock EXIT

python3 - "$REGISTRY" "$TMP" "$SESSION_ID" "$NOW_ISO" "$CLAIM_ACQUIRE" "$CLAIM_RELEASE" "$PAUSED_SET" <<'PY'
import json, os, sys

registry_path, tmp_path, session_id, now_iso, acquire_id, release_id, paused_set = sys.argv[1:]

try:
    with open(registry_path, "r", encoding="utf-8") as f:
        entries = json.load(f)
    if not isinstance(entries, list):
        entries = []
except Exception:
    entries = []

found = None
for e in entries:
    if e.get("session_id") == session_id:
        found = e
        break

if found is None:
    # No-op write to preserve the existing file as-is.
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
        f.write("\n")
    sys.exit(0)

found["last_seen"] = now_iso

cl = found.get("claim_ids_held", [])
if not isinstance(cl, list):
    cl = []
cl_set = set(cl)
if acquire_id:
    cl_set.add(acquire_id)
if release_id and release_id in cl_set:
    cl_set.remove(release_id)
found["claim_ids_held"] = sorted(cl_set)

if paused_set:
    found["paused"] = (paused_set == "true")

with open(tmp_path, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=2)
    f.write("\n")
PY

RENAME_OK=0
for attempt in 1 2 3; do
  if mv "$TMP" "$REGISTRY" 2>/dev/null; then
    RENAME_OK=1
    break
  fi
  sleep 0.25
done
if [ "$RENAME_OK" -ne 1 ]; then
  echo "bump: atomic-rename failed after 3 attempts" >&2
  exit 2
fi

cleanup_lock
trap - EXIT
exit 0
