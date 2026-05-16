#!/usr/bin/env bash
# board-stop-gate.sh — pre-prompt gate for the engineering-board Stop hook.
# Reads the Stop stdin payload, saves it, then checks whether the prompt hook
# should be suppressed. Outputs {"continue": false} to block the prompt hook
# when the project is paused or has no board at all.

set -euo pipefail

EB_DIR="${CLAUDE_PROJECT_DIR}/.engineering-board"
mkdir -p "$EB_DIR"

# Read and save stdin (Stop payload) — preserve existing behavior.
PAYLOAD=$(cat)
printf '%s' "$PAYLOAD" > "$EB_DIR/last-stop-stdin.json"

# Gate 1: paused mode — suppress prompt entirely.
MODE_FILE="$EB_DIR/session-mode.json"
if [ -f "$MODE_FILE" ]; then
  MODE=$(python3 -c "
import json, sys
try:
    d = json.load(open('$MODE_FILE'))
    print(d.get('mode', ''))
except Exception:
    print('')
" 2>/dev/null || true)
  if [ "$MODE" = "paused" ]; then
    printf '{"continue": false}\n'
    exit 0
  fi
fi

# Gate 2: no board exists — suppress prompt (no-board case handled in prompt fast-path otherwise).
ROUTER="$CLAUDE_PROJECT_DIR/docs/boards/BOARD-ROUTER.md"
LEGACY="$CLAUDE_PROJECT_DIR/docs/board"
if [ ! -f "$ROUTER" ] && [ ! -d "$LEGACY" ]; then
  printf '{"continue": false}\n'
  exit 0
fi

# Board exists and not paused — let the prompt hook run.
exit 0
