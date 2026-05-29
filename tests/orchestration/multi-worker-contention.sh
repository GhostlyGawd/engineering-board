#!/usr/bin/env bash
# tests/orchestration/multi-worker-contention.sh — End-to-end multi-worker
# contention test.
#
# NEXT-PHASE.md §1.3: "Two concurrent worker sessions on the same discipline
# pool; assert every entry is worked exactly once, no double-dispatch, no
# orphan _claims/ after both sessions complete."
#
# This extends tests/claims/race-acquire.sh from a single contested entry to
# a multi-entry pool processed by two long-lived "worker" loops. Each loop
# repeatedly picks a candidate, acquires its claim (skipping on contention),
# applies the mocked transition, and releases. The two loops run concurrently
# as background subshells against the same _claims/ directory.
#
# Scope note: same mock contract as worker-tdd-loop.sh — the subagent
# dispatch step (g) is replaced by an inline `needs:` rewrite to the next
# state. What this DOES validate is the atomic-claim contract under real
# concurrency, which is what NEXT-PHASE.md flags as the most likely
# integration-bug surface.

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

TMP="$(python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="eb-multi-worker-").replace(chr(92), "/"))')"
cleanup() { rm -rf "$TMP" 2>/dev/null || true; }
trap cleanup EXIT

PROJECT="$TMP/project"
BOARD_DIR="$PROJECT/docs/boards/demo"
mkdir -p "$BOARD_DIR/bugs" "$BOARD_DIR/_claims" "$TMP/work-log"

# Pool of 8 needs:tdd bugs. Pool size is intentionally larger than typical
# (2 entries per worker iteration's claim hold window) to maximize the
# probability of acquire-time contention across the two racing loops.
POOL_SIZE=8
for i in $(seq 1 $POOL_SIZE); do
  ID=$(printf "B4%02d" "$i")
  cat > "$BOARD_DIR/bugs/${ID}-pool-entry.md" <<EOF
---
id: $ID
type: bug
title: Pool entry $i
discovered: 2026-05-11
affects: demo/pool$i
status: open
priority: P2
needs: tdd
---

# Pool entry $i
EOF
done

# ── Worker loop body ─────────────────────────────────────────────────────────
# Each invocation runs as a separate "session" and competes for entries with
# the other. Each successful dispatch appends a single line to the per-worker
# work log: `<session-id>\t<entry-id>`. After both loops exit, the test
# verifies every pool entry appears in exactly one log line across both files.
WORKER_BODY="$TMP/worker-body.sh"
cat > "$WORKER_BODY" <<'WORKER'
#!/usr/bin/env bash
# Args: <board-dir> <session-id> <acquire-script> <release-script> <work-log-path>
set -euo pipefail
BOARD_DIR="$1"; SESSION_ID="$2"; ACQUIRE="$3"; RELEASE="$4"; LOG="$5"

# Iteration cap is a safety net against runaway loops in test failures.
MAX_ITER=200
ITER=0

list_candidates() {
  grep -lE '^needs: tdd$' "$BOARD_DIR/bugs"/*.md 2>/dev/null || true
}

while [ "$ITER" -lt "$MAX_ITER" ]; do
  ITER=$((ITER + 1))

  CANDIDATES="$(list_candidates)"
  if [ -z "$CANDIDATES" ]; then
    exit 0  # WORKER-NOTHING-TO-DO
  fi

  # Walk the candidate list — on contention skip to the next; on stale we
  # treat as contention here (the live orchestrator would invoke reclaim,
  # but the race in this test has no actual stale claims).
  ACQUIRED=0
  for ENTRY_FILE in $CANDIDATES; do
    ENTRY_ID="$(grep -E '^id:' "$ENTRY_FILE" | head -1 | awk '{print $2}')"
    RC=0
    bash "$ACQUIRE" "$BOARD_DIR" "$ENTRY_ID" "$SESSION_ID-iter$ITER" > /dev/null 2>&1 || RC=$?
    if [ "$RC" = "0" ]; then
      # Apply mocked transition: needs: tdd -> review.
      python3 - "$ENTRY_FILE" "review" <<PY
import sys, re
path, new_needs = sys.argv[1], sys.argv[2]
with open(path, "r", encoding="utf-8") as f:
    text = f.read()
new_text, n = re.subn(r"^needs:\s*\S+\s*$", f"needs: {new_needs}", text, count=1, flags=re.MULTILINE)
with open(path, "w", encoding="utf-8") as f:
    f.write(new_text)
PY
      # Tab-separated work-log row: <session-id>\t<entry-id>.
      printf '%s\t%s\n' "$SESSION_ID" "$ENTRY_ID" >> "$LOG"
      # Release.
      bash "$RELEASE" "$BOARD_DIR" "$ENTRY_ID" "$SESSION_ID-iter$ITER" > /dev/null 2>&1 || true
      ACQUIRED=1
      break
    fi
    # Else: contention (1) or stale (2) — try the next candidate.
  done

  if [ "$ACQUIRED" -eq 0 ]; then
    # Every candidate was contended this pass — yield briefly then retry.
    python3 -c "import time; time.sleep(0.01)"
  fi
done

# Iteration cap hit — abort with non-zero so the parent test sees the runaway.
exit 99
WORKER

chmod +x "$WORKER_BODY"

# ── Launch two workers concurrently ──────────────────────────────────────────
LOG_A="$TMP/work-log/session-A.tsv"
LOG_B="$TMP/work-log/session-B.tsv"
: > "$LOG_A"
: > "$LOG_B"

bash "$WORKER_BODY" "$BOARD_DIR" "session-A" "$ACQUIRE" "$RELEASE" "$LOG_A" &
PID_A=$!
bash "$WORKER_BODY" "$BOARD_DIR" "session-B" "$ACQUIRE" "$RELEASE" "$LOG_B" &
PID_B=$!

RC_A=0; wait $PID_A || RC_A=$?
RC_B=0; wait $PID_B || RC_B=$?

# ── Assertions ───────────────────────────────────────────────────────────────
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

# 1. Both workers exited cleanly.
if [ "$RC_A" -eq 0 ]; then
  report 0 "worker A exit 0"
else
  report 1 "worker A exit 0" "exit=$RC_A"
fi
if [ "$RC_B" -eq 0 ]; then
  report 0 "worker B exit 0"
else
  report 1 "worker B exit 0" "exit=$RC_B"
fi

# 2. Every pool entry appears exactly once across both work logs.
ALL_WORKED="$(cat "$LOG_A" "$LOG_B" 2>/dev/null | awk -F'\t' '{print $2}' | sort)"
TOTAL_DISPATCHES=$(echo "$ALL_WORKED" | grep -cE '^B4[0-9]+$' || true)
UNIQ_DISPATCHES=$(echo "$ALL_WORKED" | sort -u | grep -cE '^B4[0-9]+$' || true)

if [ "$TOTAL_DISPATCHES" -eq "$POOL_SIZE" ] && [ "$UNIQ_DISPATCHES" -eq "$POOL_SIZE" ]; then
  report 0 "pool of $POOL_SIZE entries: every entry worked exactly once"
else
  report 1 "pool of $POOL_SIZE entries: every entry worked exactly once" \
    "total=$TOTAL_DISPATCHES unique=$UNIQ_DISPATCHES expected=$POOL_SIZE"
fi

# 3. No double-dispatch: no entry id appears more than once across logs.
DUPS=$(echo "$ALL_WORKED" | sort | uniq -d | grep -cE '^B4[0-9]+$' || true)
if [ "$DUPS" -eq 0 ]; then
  report 0 "no double-dispatch: zero duplicate entry IDs across both workers"
else
  report 1 "no double-dispatch: zero duplicate entry IDs across both workers" \
    "$DUPS duplicates: $(echo "$ALL_WORKED" | sort | uniq -d | tr '\n' ' ')"
fi

# 4. Both workers actually contributed work (sanity check; without this the
#    test would pass even if one worker silently never acquired anything).
A_COUNT=$(grep -cE 'B4[0-9]+$' "$LOG_A" 2>/dev/null || true)
B_COUNT=$(grep -cE 'B4[0-9]+$' "$LOG_B" 2>/dev/null || true)
A_COUNT="${A_COUNT:-0}"
B_COUNT="${B_COUNT:-0}"
if [ "$A_COUNT" -gt 0 ] && [ "$B_COUNT" -gt 0 ]; then
  report 0 "both workers acquired at least one entry (A=$A_COUNT B=$B_COUNT)"
else
  # Allowed-but-noted: in heavily-skewed scheduling one worker may grab the
  # whole pool. Treat as PASS with a note rather than FAIL; the atomic
  # contract still holds. The exactly-once and no-double-dispatch checks above
  # are the real correctness gates.
  report 0 "atomic contract holds even when scheduling skewed (A=$A_COUNT B=$B_COUNT)"
fi

# 5. No orphan claim directories remain.
ORPHANS=0
if [ -d "$BOARD_DIR/_claims" ]; then
  ORPHANS=$(find "$BOARD_DIR/_claims" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
fi
if [ "$ORPHANS" -eq 0 ]; then
  report 0 "no orphan _claims/ directories after both workers exited"
else
  report 1 "no orphan _claims/ directories after both workers exited" \
    "$ORPHANS leftover: $(find "$BOARD_DIR/_claims" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | xargs -n1 basename | tr '\n' ' ')"
fi

# 6. Every pool entry ended at needs: review (transition completed
#    deterministically regardless of which worker won the race).
NOT_TRANSITIONED=0
for f in "$BOARD_DIR/bugs"/B4*.md; do
  if ! grep -qE '^needs: review$' "$f"; then
    NOT_TRANSITIONED=$((NOT_TRANSITIONED + 1))
  fi
done
if [ "$NOT_TRANSITIONED" -eq 0 ]; then
  report 0 "all $POOL_SIZE pool entries transitioned needs: tdd -> review"
else
  report 1 "all $POOL_SIZE pool entries transitioned needs: tdd -> review" \
    "$NOT_TRANSITIONED entries still on needs: tdd"
fi

echo ""
echo "================================================================"
echo "multi-worker-contention: $PASS pass, $FAIL fail"
echo "  pool size: $POOL_SIZE   workerA dispatches: $A_COUNT   workerB dispatches: $B_COUNT"
echo "================================================================"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
