#!/usr/bin/env bash
# tests/orchestration/active-workers-registry.sh — v0.2.3 registry lifecycle.
#
# Exercises board-active-workers-{register,bump,cleanup}.sh against
# .engineering-board/active-workers.json. Covers:
#   1. PM register creates entry with mode=pm, discipline=null.
#   2. Worker register creates entry with mode=worker + discipline.
#   3. Re-register of same session_id bumps last_seen, preserves started_at.
#   4. Bump with --claim-acquire / --claim-release maintains claim_ids_held.
#   5. Bump with --paused flips paused field.
#   6. Cleanup removes a session by session_id.
#   7. Lazy GC drops entries whose last_seen is older than 2 * staleClaimSec.
#   8. Invalid mode / missing discipline arguments are rejected.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

REGISTER="$PLUGIN_ROOT/hooks/scripts/board-active-workers-register.sh"
CLEANUP="$PLUGIN_ROOT/hooks/scripts/board-active-workers-cleanup.sh"
BUMP="$PLUGIN_ROOT/hooks/scripts/board-active-workers-bump.sh"

for f in "$REGISTER" "$CLEANUP" "$BUMP"; do
  if [ ! -f "$f" ]; then
    echo "MISSING: $f" >&2
    exit 1
  fi
done

TMP="$(python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="eb-reg-"))')"
cleanup_tmp() { rm -rf "$TMP" 2>/dev/null || true; }
trap cleanup_tmp EXIT

export CLAUDE_PROJECT_DIR="$TMP/project"
mkdir -p "$CLAUDE_PROJECT_DIR/.engineering-board"

REGISTRY="$CLAUDE_PROJECT_DIR/.engineering-board/active-workers.json"

PASS=0
FAIL=0
report() {
  if [ "$1" = "0" ]; then
    printf "  [PASS] %s\n" "$2"; PASS=$((PASS + 1))
  else
    printf "  [FAIL] %s%s\n" "$2" "${3:+ -- $3}"; FAIL=$((FAIL + 1))
  fi
}

read_field() {
  python3 -c "
import json, sys
session_id, field = sys.argv[1], sys.argv[2]
d = json.load(open('$REGISTRY'))
for e in d:
    if e.get('session_id') == session_id:
        print(json.dumps(e.get(field)))
        break
" "$1" "$2"
}

count_entries() {
  python3 -c "import json; print(len(json.load(open('$REGISTRY'))))"
}

# 1. PM register.
bash "$REGISTER" "sess-pm" "pm" "" "now" >/dev/null
[ "$(count_entries)" = "1" ] && report 0 "PM register creates one entry" || report 1 "PM register creates one entry" "got $(count_entries)"
[ "$(read_field sess-pm mode)" = '"pm"' ] && report 0 "PM register: mode=pm" || report 1 "PM register: mode=pm" "got $(read_field sess-pm mode)"
[ "$(read_field sess-pm discipline)" = "null" ] && report 0 "PM register: discipline=null" || report 1 "PM register: discipline=null" "got $(read_field sess-pm discipline)"
[ "$(read_field sess-pm paused)" = "false" ] && report 0 "PM register: paused=false default" || report 1 "PM register: paused=false default"

# 2. Worker register.
bash "$REGISTER" "sess-tdd" "worker" "tdd" "now" >/dev/null
[ "$(count_entries)" = "2" ] && report 0 "Worker register adds second entry" || report 1 "Worker register adds second entry" "got $(count_entries)"
[ "$(read_field sess-tdd mode)" = '"worker"' ] && report 0 "Worker register: mode=worker" || report 1 "Worker register: mode=worker"
[ "$(read_field sess-tdd discipline)" = '"tdd"' ] && report 0 "Worker register: discipline=tdd" || report 1 "Worker register: discipline=tdd"

# 3. Re-register bumps last_seen, preserves started_at.
ORIG_STARTED="$(read_field sess-pm started_at)"
sleep 1
bash "$REGISTER" "sess-pm" "pm" "" "now" >/dev/null
[ "$(read_field sess-pm started_at)" = "$ORIG_STARTED" ] && report 0 "Re-register preserves started_at" || report 1 "Re-register preserves started_at"

# 4. Bump with --claim-acquire / --claim-release.
bash "$BUMP" "sess-tdd" --claim-acquire "B001" >/dev/null
HELD="$(read_field sess-tdd claim_ids_held)"
[ "$HELD" = '["B001"]' ] && report 0 "Bump --claim-acquire adds B001" || report 1 "Bump --claim-acquire adds B001" "got $HELD"
bash "$BUMP" "sess-tdd" --claim-acquire "B002" >/dev/null
HELD="$(read_field sess-tdd claim_ids_held)"
[ "$HELD" = '["B001", "B002"]' ] && report 0 "Bump second --claim-acquire is additive" || report 1 "Bump second --claim-acquire is additive" "got $HELD"
bash "$BUMP" "sess-tdd" --claim-release "B001" >/dev/null
HELD="$(read_field sess-tdd claim_ids_held)"
[ "$HELD" = '["B002"]' ] && report 0 "Bump --claim-release drops B001" || report 1 "Bump --claim-release drops B001" "got $HELD"

# 5. Bump --paused flips paused.
bash "$BUMP" "sess-tdd" --paused "true" >/dev/null
[ "$(read_field sess-tdd paused)" = "true" ] && report 0 "Bump --paused true sets field" || report 1 "Bump --paused true sets field"
bash "$BUMP" "sess-tdd" --paused "false" >/dev/null
[ "$(read_field sess-tdd paused)" = "false" ] && report 0 "Bump --paused false clears field" || report 1 "Bump --paused false clears field"

# 6. Cleanup removes the session.
bash "$CLEANUP" "sess-pm" >/dev/null
[ "$(count_entries)" = "1" ] && report 0 "Cleanup removes PM entry" || report 1 "Cleanup removes PM entry" "got $(count_entries)"
# Cleanup on absent session: no-op (preserve worker entry).
bash "$CLEANUP" "sess-does-not-exist" >/dev/null
[ "$(count_entries)" = "1" ] && report 0 "Cleanup absent session is no-op" || report 1 "Cleanup absent session is no-op"

# 7. Lazy GC: plant a stale entry, register fresh, stale gone.
python3 -c "
import json
with open('$REGISTRY','r') as f: d=json.load(f)
d.append({'session_id':'very-old','started_at':'2020-01-01T00:00:00Z','last_seen':'2020-01-01T00:00:00Z','mode':'worker','discipline':'tdd','cwd':'/old','claim_ids_held':[],'paused':False})
with open('$REGISTRY','w') as f: json.dump(d,f)
"
bash "$REGISTER" "sess-new" "pm" "" "now" >/dev/null
SESSIONS="$(python3 -c "import json; print(sorted(e['session_id'] for e in json.load(open('$REGISTRY'))))")"
case "$SESSIONS" in
  *very-old*) report 1 "Lazy GC drops stale entry" "sessions=$SESSIONS" ;;
  *) report 0 "Lazy GC drops stale entry" ;;
esac

# 8. Invalid arguments.
if bash "$REGISTER" "sess-bad" "INVALID_MODE" "" "now" >/dev/null 2>&1; then
  report 1 "Invalid mode rejected"
else
  report 0 "Invalid mode rejected"
fi
if bash "$REGISTER" "sess-bad" "worker" "" "now" >/dev/null 2>&1; then
  report 1 "Worker without discipline rejected"
else
  report 0 "Worker without discipline rejected"
fi
if bash "$REGISTER" "sess-bad" "worker" "INVALID_DISC" "now" >/dev/null 2>&1; then
  report 1 "Worker invalid discipline rejected"
else
  report 0 "Worker invalid discipline rejected"
fi

echo ""
echo "active-workers-registry: $PASS pass, $FAIL fail"
if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
