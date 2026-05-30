#!/usr/bin/env bash
# board-active-workers-cleanup.sh — remove an entry from
# .engineering-board/active-workers.json by session_id.
#
# Usage:
#   board-active-workers-cleanup.sh <session-id>
#
# Behaviour:
#   - No-op if session_id is not present in the registry.
#   - Atomic-rename write through tmp file in same directory.
#   - mkdir-based lockfile for serialisation.
#
# Exit codes:
#   0 — entry removed (or already absent).
#   1 — bad arguments.
#   2 — lock not acquired within retry budget.

set -euo pipefail

SESSION_ID="${1:-}"
if [ -z "$SESSION_ID" ]; then
  echo "Usage: $0 <session-id>" >&2
  exit 1
fi

if [ -z "${CLAUDE_PROJECT_DIR:-}" ]; then
  echo "cleanup: CLAUDE_PROJECT_DIR not set" >&2
  exit 1
fi

STATE_DIR="${CLAUDE_PROJECT_DIR}/.engineering-board"
REGISTRY="${STATE_DIR}/active-workers.json"
LOCK_DIR="${STATE_DIR}/active-workers.json.lock"
TMP="${STATE_DIR}/active-workers.json.tmp.$$"

if [ ! -f "$REGISTRY" ]; then
  # Nothing to clean.
  exit 0
fi

ATTEMPTS=0
while ! mkdir "$LOCK_DIR" 2>/dev/null; do
  ATTEMPTS=$((ATTEMPTS + 1))
  if [ "$ATTEMPTS" -ge 5 ]; then
    echo "cleanup: lock not acquired after 5 attempts (lockfile: $LOCK_DIR)" >&2
    exit 2
  fi
  sleep 0.1
done

cleanup_lock() { rmdir "$LOCK_DIR" 2>/dev/null || true; rm -f "$TMP" 2>/dev/null || true; }
trap cleanup_lock EXIT

python3 - "$REGISTRY" "$TMP" "$SESSION_ID" <<'PY'
import json, os, sys

registry_path, tmp_path, session_id = sys.argv[1:]

try:
    with open(registry_path, "r", encoding="utf-8") as f:
        entries = json.load(f)
    if not isinstance(entries, list):
        entries = []
except Exception:
    entries = []

entries = [e for e in entries if e.get("session_id") != session_id]

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
  echo "cleanup: atomic-rename failed after 3 attempts" >&2
  exit 2
fi

cleanup_lock
trap - EXIT
exit 0
