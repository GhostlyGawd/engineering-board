#!/usr/bin/env bash
# tests/orchestration/worker-review-loop.sh — End-to-end Worker (review
# discipline) continuation loop test.
#
# NEXT-PHASE.md §1.2 mirror of worker-tdd-loop.sh, exercising the
# review-discipline transitions of the needs: state machine:
#   review -> validate  (mocked: subagent approves)
#   review -> tdd       (mocked: subagent regresses; tests one regression too)
#
# See worker-tdd-loop.sh's header for the scope/mock contract — identical here.

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

TMP="$(python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="eb-worker-review-").replace(chr(92), "/"))')"
cleanup() { rm -rf "$TMP" 2>/dev/null || true; }
trap cleanup EXIT

PROJECT="$TMP/project"
BOARD_DIR="$PROJECT/engineering-board/demo"
SESSION_ID="worker-review-test-session"
mkdir -p "$BOARD_DIR/bugs" "$BOARD_DIR/features" "$BOARD_DIR/_claims" "$PROJECT/.engineering-board"

cat > "$PROJECT/.engineering-board/session-mode.json" <<EOF
{"mode":"worker","discipline":"review","session_id":"$SESSION_ID","started_at":"2026-05-11T12:00:00Z"}
EOF

# Two needs:review entries (one approved, one regressed) + one wrong-discipline.
cat > "$BOARD_DIR/bugs/B200-approved.md" <<'EOF'
---
id: B200
type: bug
title: Approved review path
discovered: 2026-05-11
affects: demo/approved
status: open
priority: P2
needs: review
---

# Approved
EOF

cat > "$BOARD_DIR/bugs/B201-regressed.md" <<'EOF'
---
id: B201
type: bug
title: Regressed review path
discovered: 2026-05-11
affects: demo/regressed
status: open
priority: P2
needs: review
---

# Regressed
EOF

cat > "$BOARD_DIR/features/F200-other-discipline.md" <<'EOF'
---
id: F200
type: feature
title: needs: validate — not for this loop
discovered: 2026-05-11
affects: demo/other
status: open
priority: P2
needs: validate
---

# Validate
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

# Mocked subagent transitions per agents/code-reviewer.md: typically suggests
# `validate` on pass, can regress to `tdd` on test gaps. Map by entry id so
# the test exercises both branches deterministically.
mock_next_needs() {
  case "$1" in
    B200) echo "validate" ;;
    B201) echo "tdd" ;;
    *)    echo "validate" ;;
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

  CANDIDATES="$(list_candidates "review")"
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

# Both needs:review entries dispatched exactly once.
REVIEW_COUNT=$(echo "$WORKED_IDS" | tr ' ' '\n' | grep -cE 'B20[01]' || true)
if [ "$REVIEW_COUNT" -eq 2 ]; then
  report 0 "both B200 and B201 dispatched exactly once"
else
  report 1 "both B200 and B201 dispatched exactly once" "worked='$WORKED_IDS'"
fi

# B200 -> validate (approval path); B201 -> tdd (regression path).
if grep -qE '^needs: validate$' "$BOARD_DIR/bugs/B200-approved.md"; then
  report 0 "B200 transitioned needs: review -> validate (approval)"
else
  report 1 "B200 transitioned needs: review -> validate (approval)"
fi
if grep -qE '^needs: tdd$' "$BOARD_DIR/bugs/B201-regressed.md"; then
  report 0 "B201 regressed needs: review -> tdd (review found gaps)"
else
  report 1 "B201 regressed needs: review -> tdd (review found gaps)"
fi

# F200 (needs: validate) untouched by review-discipline loop.
if grep -qE '^needs: validate$' "$BOARD_DIR/features/F200-other-discipline.md"; then
  report 0 "F200 (needs: validate) not touched by review-discipline loop"
else
  report 1 "F200 (needs: validate) not touched by review-discipline loop"
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
echo "worker-review-loop: $PASS pass, $FAIL fail"
echo "================================================================"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
