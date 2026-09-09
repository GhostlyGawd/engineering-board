#!/usr/bin/env bash
# Apply outcome-aware pattern Learning plans through the shared core.
set -euo pipefail

BOARD_DIR="${1:-}"
MIN_RECURRENCE="${2:-3}"
if [ -z "${BOARD_DIR}" ]; then
  echo '{"error":"usage: board-curate-learnings.sh <board-dir> [min-recurrence]"}' >&2
  exit 1
fi
if [ ! -d "${BOARD_DIR}" ]; then
  printf '{"error":"board-dir not found: %s"}\n' "${BOARD_DIR}" >&2
  exit 2
fi

PROJECT="$(basename "${BOARD_DIR}")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/board-outcome.py" \
  --board-dir "${BOARD_DIR}" \
  --project "${PROJECT}" \
  curate \
  --min-recurrence "${MIN_RECURRENCE}"
