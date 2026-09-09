#!/usr/bin/env bash
# board-demo.sh — contained pattern-intelligence first-win lifecycle.
set -euo pipefail

if [ -z "${CLAUDE_PROJECT_DIR:-}" ]; then
  echo '{"error":"project_dir_missing","detail":"CLAUDE_PROJECT_DIR is not set"}' >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CORE="${SCRIPT_DIR}/board_demo.py"
VIEW="${SCRIPT_DIR}/board-view.sh"

core() {
  python3 "${CORE}" \
    --project-dir "${CLAUDE_PROJECT_DIR}" \
    --plugin-root "${PLUGIN_ROOT}" \
    "$@"
}

case "${1:-create}" in
  create)
    shift || true
    if [ -n "${EB_DEMO_RUN_ID:-}" ]; then
      core create --run-id "${EB_DEMO_RUN_ID}"
    else
      core create "$@"
    fi
    ;;
  hypothesis)
    if [ "$#" -ne 2 ]; then
      echo '{"error":"usage","detail":"board-demo.sh hypothesis <run-id>"}' >&2
      exit 2
    fi
    RESULT="$(core hypothesis "$2")"
    RUN_DIR="$(printf '%s' "${RESULT}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["run_dir"])')"
    bash "${VIEW}" --demo-dir "${RUN_DIR}" >&2
    core finalize "$2" "${RUN_DIR}/pattern-intelligence.html"
    ;;
  --clean|clean)
    if [ "$#" -ne 2 ]; then
      echo '{"error":"usage","detail":"board-demo.sh --clean <run-id>"}' >&2
      exit 2
    fi
    core clean "$2"
    ;;
  status)
    if [ "$#" -ne 2 ]; then
      echo '{"error":"usage","detail":"board-demo.sh status <run-id>"}' >&2
      exit 2
    fi
    core status "$2"
    ;;
  *)
    echo '{"error":"usage","detail":"use create, hypothesis <run-id>, status <run-id>, or --clean <run-id>"}' >&2
    exit 2
    ;;
esac
