#!/usr/bin/env bash
# tests/orchestration/worker-validate-loop.sh — End-to-end Worker (validate
# discipline) continuation loop test.
#
# NEXT-PHASE.md §1.2 mirror of worker-tdd-loop.sh, exercising the
# validate-discipline transitions of the needs: state machine:
#   validate -> resolved  (mocked: subagent confirms Done-when)
#   validate -> tdd       (mocked: subagent regresses; covers the regression branch)
#
# See worker-tdd-loop.sh's header for the scope/mock contract — identical here.
# Note: the validator subagent is documented as Read-only (no Write tool), but
# the orchestrator step (h) write-back still rewrites the entry's needs: line.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PLUGIN_ROOT="${1:-$DEFAULT_ROOT}"

ACQUIRE="$PLUGIN_ROOT/hooks/scripts/board-claim-acquire.sh"
RELEASE="$PLUGIN_ROOT/hooks/scripts/board-claim-release.sh"

for s in "$ACQUIRE" "$RELEASE"; do
  if [ ! -f "$s" ]; then
    echo "MISSING SCRIPT: $s" >&2
    exit 1
  fi
done

TMP="$(python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="eb-worker-validate-").replace(chr(92), "/"))')"
cleanup() { rm -rf "$TMP" 2>/dev/null || true; }
trap cleanup EXIT

PROJECT="$TMP/project"
BOARD_DIR="$PROJECT/engineering-board/demo"
SESSION_ID="worker-validate-test-session"
mkdir -p "$BOARD_DIR/bugs" "$BOARD_DIR/features" "$BOARD_DIR/_claims" "$PROJECT/.engineering-board"

cat > "$PROJECT/.engineering-board/session-mode.json" <<EOF
{"mode":"worker","discipline":"validate","session_id":"$SESSION_ID","started_at":"2026-05-11T12:00:00Z"}
EOF

cat > "$BOARD_DIR/bugs/B300-resolves.md" <<'EOF'
---
id: B300
type: bug
title: Validate passes — moves to resolved
discovered: 2026-05-11
affects: demo/resolves
status: open
priority: P2
needs: validate
---

# Resolves
EOF

cat > "$BOARD_DIR/bugs/B301-regresses.md" <<'EOF'
---
id: B301
type: bug
title: Validate fails — regress to tdd
discovered: 2026-05-11
affects: demo/regresses
status: open
priority: P2
needs: validate
---

# Regresses
EOF

# Wrong-discipline guard: needs: tdd entry must not be processed.
cat > "$BOARD_DIR/bugs/B302-other.md" <<'EOF'
---
id: B302
type: bug
title: needs: tdd — not for this loop
discovered: 2026-05-11
affects: demo/other
status: open
priority: P2
needs: tdd
---

# Other
EOF

PASS=0
FAIL=0
report() {
  if [ "$1" = "0" ]; then
    printf "  [PASS] %s\n" "$2"
    PASS=$((PASS + 1))
  else
    printf "  [FAIL] %s%s\n" "$2" "${3:+ -- $3}"
    FAIL=$((FAIL + 1))
  fi
}

list_candidates() {
  local discipline="$1"
  grep -lE "^needs: ${discipline}$" "$BOARD_DIR/bugs"/*.md "$BOARD_DIR/features"/*.md 2>/dev/null || true
}

# Mocked subagent transitions per agents/validator.md: typically suggests
# `resolved` (terminal) on Done-when verified, can regress to `tdd` on
# unmet criteria.
mock_next_needs() {
  case "$1" in
    B300) echo "resolved" ;;
    B301) echo "tdd" ;;
    *)    echo "resolved" ;;
  esac
}

ITER=0
WORKED_IDS=""
while :; do
  ITER=$((ITER + 1))
  if [ "$ITER" -gt 10 ]; then
    report 1 "loop terminates within 10 iterations" "ran $ITER without NOTHING-TO-DO"
    break
  fi

  CANDIDATES="$(list_candidates "validate")"
  if [ -z "$CANDIDATES" ]; then
    WORKER_SENTINEL="<<EB-WORKER-NOTHING-TO-DO>>"
    break
  fi

  ENTRY_FILE="$(echo "$CANDIDATES" | head -1)"
  ENTRY_ID="$(grep -E '^id:' "$ENTRY_FILE" | head -1 | awk '{print $2}')"
  SUGGESTED_NEXT="$(mock_next_needs "$ENTRY_ID")"

  bash "$ACQUIRE" "$BOARD_DIR" "$ENTRY_ID" "$SESSION_ID-iter$ITER" > "$TMP/acq.$ITER.stdout" 2> "$TMP/acq.$ITER.stderr"
  report 0 "iter $ITER: claim acquired for $ENTRY_ID"

  python3 - "$ENTRY_FILE" "$SUGGESTED_NEXT" <<'PY'
import sys, re
path, new_needs = sys.argv[1], sys.argv[2]
with open(path, "r", encoding="utf-8") as f:
    text = f.read()
new_text, n = re.subn(r"^needs:\s*\S+\s*$", f"needs: {new_needs}", text, count=1, flags=re.MULTILINE)
if n == 0:
    new_text = re.sub(r"^(status:.*)$", r"\1\nneeds: " + new_needs, text, count=1, flags=re.MULTILINE)
with open(path, "w", encoding="utf-8") as f:
    f.write(new_text)
PY

  REL_RC=0
  bash "$RELEASE" "$BOARD_DIR" "$ENTRY_ID" "$SESSION_ID-iter$ITER" > "$TMP/rel.$ITER.stdout" 2> "$TMP/rel.$ITER.stderr" || REL_RC=$?
  if [ "$REL_RC" -eq 0 ]; then
    report 0 "iter $ITER: claim released for $ENTRY_ID"
  else
    report 1 "iter $ITER: claim released for $ENTRY_ID" "exit=$REL_RC"
  fi

  if [ -d "$BOARD_DIR/_claims/$ENTRY_ID" ]; then
    report 1 "iter $ITER: no leftover _claims/$ENTRY_ID/" "still present"
  else
    report 0 "iter $ITER: no leftover _claims/$ENTRY_ID/"
  fi

  if grep -qE "^needs: ${SUGGESTED_NEXT}$" "$ENTRY_FILE"; then
    report 0 "iter $ITER: $ENTRY_ID needs: $SUGGESTED_NEXT (post-dispatch)"
  else
    report 1 "iter $ITER: $ENTRY_ID needs: $SUGGESTED_NEXT (post-dispatch)"
  fi

  WORKED_IDS="$WORKED_IDS $ENTRY_ID"
done

# Termination sentinel.
if [ "${WORKER_SENTINEL:-}" = "<<EB-WORKER-NOTHING-TO-DO>>" ]; then
  report 0 "loop terminated with <<EB-WORKER-NOTHING-TO-DO>>"
else
  report 1 "loop terminated with <<EB-WORKER-NOTHING-TO-DO>>" "got '${WORKER_SENTINEL:-<empty>}'"
fi

VAL_COUNT=$(echo "$WORKED_IDS" | tr ' ' '\n' | grep -cE 'B30[01]' || true)
if [ "$VAL_COUNT" -eq 2 ]; then
  report 0 "both B300 and B301 dispatched exactly once"
else
  report 1 "both B300 and B301 dispatched exactly once" "worked='$WORKED_IDS'"
fi

# B300 -> resolved (terminal); B301 -> tdd (regression).
if grep -qE '^needs: resolved$' "$BOARD_DIR/bugs/B300-resolves.md"; then
  report 0 "B300 transitioned needs: validate -> resolved (terminal)"
else
  report 1 "B300 transitioned needs: validate -> resolved (terminal)"
fi
if grep -qE '^needs: tdd$' "$BOARD_DIR/bugs/B301-regresses.md"; then
  report 0 "B301 regressed needs: validate -> tdd (Done-when unmet)"
else
  report 1 "B301 regressed needs: validate -> tdd (Done-when unmet)"
fi

# B302 (needs: tdd) untouched.
if grep -qE '^needs: tdd$' "$BOARD_DIR/bugs/B302-other.md"; then
  report 0 "B302 (needs: tdd) not touched by validate-discipline loop"
else
  report 1 "B302 (needs: tdd) not touched by validate-discipline loop"
fi

# No orphan claims.
if [ -d "$BOARD_DIR/_claims" ]; then
  ORPHANS=$(find "$BOARD_DIR/_claims" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
  if [ "$ORPHANS" -eq 0 ]; then
    report 0 "no orphan claim directories after loop"
  else
    report 1 "no orphan claim directories after loop" "found $ORPHANS leftover claim dirs"
  fi
else
  report 0 "no orphan claim directories after loop (no _claims/ created)"
fi

echo ""
echo "================================================================"
echo "worker-validate-loop: $PASS pass, $FAIL fail"
echo "================================================================"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
