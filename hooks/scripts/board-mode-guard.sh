#!/usr/bin/env bash
# board-mode-guard.sh — deterministic mode-transition decision for the four
# session-mode commands (/pm-start, /worker-start, /board-pause, /board-resume).
#
# ARCHITECTURE.md §11.5 documents the refusal matrix; this script enforces it
# in one place so the four commands can defer the decision instead of each
# re-implementing six rows of conditional logic in markdown.
#
# Usage:
#   board-mode-guard.sh pm
#   board-mode-guard.sh worker --discipline <tdd|review|validate>
#   board-mode-guard.sh paused
#   board-mode-guard.sh resumed
#
# Reads ${CLAUDE_PROJECT_DIR}/.engineering-board/session-mode.json if it exists.
# Decides ALLOW / NOOP / REFUSE per the §11.5 matrix and emits either the
# decision payload (ALLOW) or the canonical user-facing message (NOOP/REFUSE)
# on stdout.
#
# Exit codes:
#   0 — ALLOW: caller proceeds with the state write
#   2 — NOOP:  caller prints stdout verbatim and stops (idempotent short-circuit)
#   3 — REFUSE: caller prints stdout verbatim and stops (transition forbidden)
#   1 — bad arguments
#
# ALLOW payload (key=value lines on stdout):
#   CURRENT_MODE=<pm|worker|paused|null>
#   CURRENT_DISCIPLINE=<tdd|review|validate|null>
#   PREVIOUS_MODE=<pm|worker|null>           # only for target=paused
#   PREVIOUS_DISCIPLINE=<tdd|review|validate|null>  # only for target=paused
#   RESTORE_MODE=<pm|worker|null>            # only for target=resumed
#   RESTORE_DISCIPLINE=<tdd|review|validate|null>   # only for target=resumed
#
# The script does NOT write any state files. The caller still owns the write.

set -euo pipefail

usage() {
  cat >&2 <<EOF
Usage:
  $0 pm
  $0 worker --discipline <tdd|review|validate>
  $0 paused
  $0 resumed
EOF
  exit 1
}

TARGET="${1:-}"
DISCIPLINE=""

case "$TARGET" in
  pm|paused|resumed)
    shift
    ;;
  worker)
    shift
    if [ "${1:-}" = "--discipline" ]; then
      shift
      DISCIPLINE="${1:-}"
      shift || true
    elif [[ "${1:-}" == --discipline=* ]]; then
      DISCIPLINE="${1#--discipline=}"
      shift
    else
      echo "guard: worker target requires --discipline <tdd|review|validate>" >&2
      exit 1
    fi
    case "$DISCIPLINE" in
      tdd|review|validate) ;;
      *) echo "guard: invalid discipline '$DISCIPLINE' (expected tdd|review|validate)" >&2; exit 1 ;;
    esac
    ;;
  ""|-h|--help)
    usage
    ;;
  *)
    echo "guard: unknown target '$TARGET'" >&2
    usage
    ;;
esac

if [ -z "${CLAUDE_PROJECT_DIR:-}" ]; then
  echo "guard: CLAUDE_PROJECT_DIR not set" >&2
  exit 1
fi

STATE_FILE="${CLAUDE_PROJECT_DIR}/.engineering-board/session-mode.json"

# --- Read current state ----------------------------------------------------
# Emits four lines to stdout: CURRENT_MODE / CURRENT_DISCIPLINE / PREVIOUS_MODE / PREVIOUS_DISCIPLINE
# (PREVIOUS_* is the persisted previous_mode/previous_discipline, used only by /board-resume.)
read_state() {
  if [ ! -f "$STATE_FILE" ]; then
    printf 'null\nnull\nnull\nnull\n'
    return 0
  fi
  python3 - "$STATE_FILE" <<'PY'
import json, sys
path = sys.argv[1]
try:
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
except Exception:
    print("null"); print("null"); print("null"); print("null"); sys.exit(0)
if not isinstance(d, dict):
    print("null"); print("null"); print("null"); print("null"); sys.exit(0)
def norm(v):
    if v is None: return "null"
    if isinstance(v, str) and v.strip() == "": return "null"
    return str(v)
print(norm(d.get("mode")))
print(norm(d.get("discipline")))
print(norm(d.get("previous_mode")))
print(norm(d.get("previous_discipline")))
PY
}

STATE_OUT="$(read_state)"
CURRENT_MODE="$(printf '%s\n' "$STATE_OUT" | sed -n '1p')"
CURRENT_DISCIPLINE="$(printf '%s\n' "$STATE_OUT" | sed -n '2p')"
PERSISTED_PREV_MODE="$(printf '%s\n' "$STATE_OUT" | sed -n '3p')"
PERSISTED_PREV_DISCIPLINE="$(printf '%s\n' "$STATE_OUT" | sed -n '4p')"

# Normalize unrecognized modes to "null" — the §11.5 matrix treats unset/null/
# unrecognized identically.
case "$CURRENT_MODE" in
  pm|worker|paused) ;;
  *) CURRENT_MODE="null" ;;
esac

emit_allow() {
  printf 'CURRENT_MODE=%s\n' "$CURRENT_MODE"
  printf 'CURRENT_DISCIPLINE=%s\n' "$CURRENT_DISCIPLINE"
  if [ "$TARGET" = "paused" ]; then
    # previous_mode = the mode we are leaving; null becomes JSON null.
    case "$CURRENT_MODE" in
      pm|worker) printf 'PREVIOUS_MODE=%s\n' "$CURRENT_MODE" ;;
      *)         printf 'PREVIOUS_MODE=null\n' ;;
    esac
    if [ "$CURRENT_MODE" = "worker" ]; then
      printf 'PREVIOUS_DISCIPLINE=%s\n' "$CURRENT_DISCIPLINE"
    else
      printf 'PREVIOUS_DISCIPLINE=null\n'
    fi
  fi
  if [ "$TARGET" = "resumed" ]; then
    printf 'RESTORE_MODE=%s\n' "$PERSISTED_PREV_MODE"
    printf 'RESTORE_DISCIPLINE=%s\n' "$PERSISTED_PREV_DISCIPLINE"
  fi
  exit 0
}

# --- Matrix: target=pm -----------------------------------------------------
if [ "$TARGET" = "pm" ]; then
  case "$CURRENT_MODE" in
    null)
      emit_allow ;;
    pm)
      echo "Engineering board: already in PM mode. No action taken."
      exit 2 ;;
    worker)
      echo "Engineering board: currently in worker mode (discipline=${CURRENT_DISCIPLINE}). Restart the session to switch to PM mode. No action taken."
      exit 3 ;;
    paused)
      echo "Engineering board: currently paused. Run /board-resume first, then /pm-start. No action taken."
      exit 3 ;;
  esac
fi

# --- Matrix: target=worker -------------------------------------------------
if [ "$TARGET" = "worker" ]; then
  case "$CURRENT_MODE" in
    null)
      emit_allow ;;
    pm)
      echo "Engineering board: currently in PM mode. Restart the session to switch to worker mode. No action taken."
      exit 3 ;;
    worker)
      if [ "$CURRENT_DISCIPLINE" = "$DISCIPLINE" ]; then
        echo "Engineering board: already in worker mode (discipline=${CURRENT_DISCIPLINE}). No action taken."
        exit 2
      else
        echo "Engineering board: currently in worker mode (discipline=${CURRENT_DISCIPLINE}). Restart the session to switch to discipline=${DISCIPLINE}. No action taken."
        exit 3
      fi ;;
    paused)
      echo "Engineering board: currently paused. Run /board-resume first, then /worker-start --discipline ${DISCIPLINE}. No action taken."
      exit 3 ;;
  esac
fi

# --- Matrix: target=paused -------------------------------------------------
if [ "$TARGET" = "paused" ]; then
  case "$CURRENT_MODE" in
    paused)
      echo "Engineering board: already paused. No action taken."
      exit 2 ;;
    null|pm|worker)
      emit_allow ;;
  esac
fi

# --- Matrix: target=resumed ------------------------------------------------
if [ "$TARGET" = "resumed" ]; then
  case "$CURRENT_MODE" in
    paused)
      emit_allow ;;
    null|pm|worker)
      echo "Engineering board: not currently paused. No action taken."
      exit 2 ;;
  esac
fi

# Unreachable.
echo "guard: internal error — fell through matrix (target=$TARGET, mode=$CURRENT_MODE)" >&2
exit 1
