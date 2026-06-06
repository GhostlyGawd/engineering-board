#!/usr/bin/env bash
# tests/orchestration/pm-fallback-heartbeat.sh — v0.2.3 PM-fallback heartbeat.
#
# Exercises board-pm-fallback-heartbeat.sh across the four decision branches:
#   1. Owner alive + not paused → refresh heartbeat.
#   2. Owner paused → skip (heartbeat unchanged).
#   3. Owner not in registry → skip (heartbeat unchanged).
#   4. Owner in registry but stale (last_seen too old) → skip.
#
# Plants claims directly via filesystem (no PM/Worker session needed).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
FALLBACK="$PLUGIN_ROOT/hooks/scripts/board-pm-fallback-heartbeat.sh"

if [ ! -f "$FALLBACK" ]; then
  echo "MISSING: $FALLBACK" >&2
  exit 1
fi

TMP="$(python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="eb-pmfb-"))')"
cleanup_tmp() { rm -rf "$TMP" 2>/dev/null || true; }
trap cleanup_tmp EXIT

export CLAUDE_PROJECT_DIR="$TMP/project"
BOARD_DIR="$CLAUDE_PROJECT_DIR/engineering-board/p"
CLAIMS_DIR="$BOARD_DIR/_claims"
mkdir -p "$CLAIMS_DIR"
mkdir -p "$CLAUDE_PROJECT_DIR/.engineering-board"

# Plant 4 claims.
plant_claim() {
  local id="$1" sess="$2"
  mkdir -p "$CLAIMS_DIR/$id"
  printf 'session_id: %s\ncwd: /tmp\n' "$sess" > "$CLAIMS_DIR/$id/owner.txt"
  printf 'OLD-HEARTBEAT\n' > "$CLAIMS_DIR/$id/heartbeat.txt"
}

plant_claim "ALIVE-001"  "sess-alive"
plant_claim "PAUSED-001" "sess-paused"
plant_claim "ORPHAN-001" "sess-orphan-not-in-reg"
plant_claim "STALE-001"  "sess-stale-reg"

NOW="$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))')"
OLD="$(python3 -c 'import datetime; print((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=400)).strftime("%Y-%m-%dT%H:%M:%SZ"))')"

cat > "$CLAUDE_PROJECT_DIR/.engineering-board/active-workers.json" <<EOF
[
  {"session_id":"sess-alive",    "started_at":"$NOW","last_seen":"$NOW","mode":"worker","discipline":"tdd","cwd":"/tmp","claim_ids_held":["ALIVE-001"], "paused":false},
  {"session_id":"sess-paused",   "started_at":"$NOW","last_seen":"$NOW","mode":"worker","discipline":"tdd","cwd":"/tmp","claim_ids_held":["PAUSED-001"],"paused":true},
  {"session_id":"sess-stale-reg","started_at":"$OLD","last_seen":"$OLD","mode":"worker","discipline":"tdd","cwd":"/tmp","claim_ids_held":["STALE-001"], "paused":false}
]
EOF

OUTPUT="$(bash "$FALLBACK" "$BOARD_DIR" 2>&1)"

PASS=0
FAIL=0
report() {
  if [ "$1" = "0" ]; then
    printf "  [PASS] %s\n" "$2"; PASS=$((PASS + 1))
  else
    printf "  [FAIL] %s%s\n" "$2" "${3:+ -- $3}"; FAIL=$((FAIL + 1))
  fi
}

decision_for() {
  echo "$OUTPUT" | python3 -c "
import json, sys
id = sys.argv[1]
found = None
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    if d.get('entry_id') == id:
        found = d.get('decision')
        break
print(found if found is not None else 'not_emitted')
" "$1"
}

reason_for() {
  echo "$OUTPUT" | python3 -c "
import json, sys
id = sys.argv[1]
found = None
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    if d.get('entry_id') == id:
        found = d.get('reason')
        break
print(found if found is not None else '')
" "$1"
}

heartbeat_content() {
  cat "$CLAIMS_DIR/$1/heartbeat.txt"
}

# 1. Alive owner → refreshed.
[ "$(decision_for ALIVE-001)" = "refreshed" ] && report 0 "ALIVE owner -> refreshed" || report 1 "ALIVE owner -> refreshed" "got $(decision_for ALIVE-001)"
NEW_HB="$(heartbeat_content ALIVE-001)"
[ "$NEW_HB" != "OLD-HEARTBEAT" ] && report 0 "ALIVE heartbeat content changed" || report 1 "ALIVE heartbeat content changed" "still OLD-HEARTBEAT"

# 2. Paused owner → skipped, heartbeat unchanged.
[ "$(decision_for PAUSED-001)" = "skipped" ] && report 0 "PAUSED owner -> skipped" || report 1 "PAUSED owner -> skipped" "got $(decision_for PAUSED-001)"
[ "$(reason_for PAUSED-001)" = "owner_paused" ] && report 0 "PAUSED reason=owner_paused" || report 1 "PAUSED reason=owner_paused" "got $(reason_for PAUSED-001)"
[ "$(heartbeat_content PAUSED-001)" = "OLD-HEARTBEAT" ] && report 0 "PAUSED heartbeat preserved" || report 1 "PAUSED heartbeat preserved"

# 3. Orphan owner → skipped.
[ "$(decision_for ORPHAN-001)" = "skipped" ] && report 0 "ORPHAN owner -> skipped" || report 1 "ORPHAN owner -> skipped" "got $(decision_for ORPHAN-001)"
[ "$(reason_for ORPHAN-001)" = "owner_not_in_registry" ] && report 0 "ORPHAN reason=owner_not_in_registry" || report 1 "ORPHAN reason=owner_not_in_registry" "got $(reason_for ORPHAN-001)"
[ "$(heartbeat_content ORPHAN-001)" = "OLD-HEARTBEAT" ] && report 0 "ORPHAN heartbeat preserved" || report 1 "ORPHAN heartbeat preserved"

# 4. Stale-registered owner → skipped.
[ "$(decision_for STALE-001)" = "skipped" ] && report 0 "STALE-REG owner -> skipped" || report 1 "STALE-REG owner -> skipped" "got $(decision_for STALE-001)"
[ "$(reason_for STALE-001)" = "owner_stale" ] && report 0 "STALE-REG reason=owner_stale" || report 1 "STALE-REG reason=owner_stale" "got $(reason_for STALE-001)"
[ "$(heartbeat_content STALE-001)" = "OLD-HEARTBEAT" ] && report 0 "STALE-REG heartbeat preserved" || report 1 "STALE-REG heartbeat preserved"

echo ""
echo "pm-fallback-heartbeat: $PASS pass, $FAIL fail"
if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
