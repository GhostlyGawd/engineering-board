#!/usr/bin/env bash
# tests/orchestration/pause-resume-registry.sh — v0.3.2 pause/resume round-trip.
#
# active-workers-registry.sh covers the bump script's --paused flag in
# isolation. This test exercises the FULL round-trip that /board-pause and
# /board-resume drive through the bump script, asserting the cycle-level
# invariants the commands promise:
#
#   1. register → pause → resume returns to paused=false (single round-trip).
#   2. The cycle is idempotent: pause→pause is a no-op on the second call;
#      resume→resume likewise. The "already paused" / "not currently paused"
#      short-circuits live in the markdown commands; this test covers the
#      bump-script behaviour when the commands DO call bump twice in a row.
#   3. Multiple round-trips (pause/resume/pause/resume) preserve session
#      identity (session_id, started_at, mode, discipline, cwd, claim_ids_held).
#   4. The pause/resume cycle bumps last_seen on every flip — so a paused
#      session continues to register as alive for PM-fallback-heartbeat,
#      which checks "registered + alive + not paused" before refreshing.
#      A paused-but-alive session is the canonical case the consensus plan
#      pre-mortem worried about.
#   5. Pause on a session that was lazy-GC'd between register and pause is
#      a silent no-op (bump.sh exits 0 when session_id is absent). This
#      lines up with the commands' "registry-write failures are not fatal"
#      contract.
#   6. The paused flag does NOT bleed across sessions: pausing sess-A
#      leaves sess-B's paused field untouched.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

REGISTER="$PLUGIN_ROOT/hooks/scripts/board-active-workers-register.sh"
BUMP="$PLUGIN_ROOT/hooks/scripts/board-active-workers-bump.sh"

for f in "$REGISTER" "$BUMP"; do
  if [ ! -f "$f" ]; then
    echo "MISSING: $f" >&2
    exit 1
  fi
done

TMP="$(python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="eb-pr-"))')"
trap 'rm -rf "$TMP" 2>/dev/null || true' EXIT

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
sid, field = sys.argv[1], sys.argv[2]
d = json.load(open('$REGISTRY'))
for e in d:
    if e.get('session_id') == sid:
        print(json.dumps(e.get(field)))
        break
" "$1" "$2"
}

# Simulates /board-pause's invocation of bump --paused true.
pause_cmd() { bash "$BUMP" "$1" --paused true >/dev/null; }
# Simulates /board-resume's invocation of bump --paused false.
resume_cmd() { bash "$BUMP" "$1" --paused false >/dev/null; }

# ── Setup: register one worker session ──────────────────────────────────────
bash "$REGISTER" "sess-tdd" "worker" "tdd" "2026-05-30T00:00:00Z" >/dev/null
ORIG_STARTED="$(read_field sess-tdd started_at)"
ORIG_LAST_SEEN_1="$(read_field sess-tdd last_seen)"
[ "$(read_field sess-tdd paused)" = "false" ] && report 0 "fresh worker register: paused=false" || report 1 "fresh worker register: paused=false"

# ── Invariant 1: single round-trip ──────────────────────────────────────────
pause_cmd sess-tdd
[ "$(read_field sess-tdd paused)" = "true" ] && report 0 "round-trip 1: pause sets paused=true" || report 1 "round-trip 1: pause sets paused=true"

resume_cmd sess-tdd
[ "$(read_field sess-tdd paused)" = "false" ] && report 0 "round-trip 1: resume sets paused=false" || report 1 "round-trip 1: resume sets paused=false"

# ── Invariant 2: idempotent double-pause / double-resume ────────────────────
pause_cmd sess-tdd
pause_cmd sess-tdd
[ "$(read_field sess-tdd paused)" = "true" ] && report 0 "double-pause stays paused=true (bump idempotent)" || report 1 "double-pause stays paused=true"

resume_cmd sess-tdd
resume_cmd sess-tdd
[ "$(read_field sess-tdd paused)" = "false" ] && report 0 "double-resume stays paused=false (bump idempotent)" || report 1 "double-resume stays paused=false"

# ── Invariant 3: multi-cycle preserves identity ─────────────────────────────
sleep 1
pause_cmd sess-tdd
resume_cmd sess-tdd
pause_cmd sess-tdd
resume_cmd sess-tdd
[ "$(read_field sess-tdd started_at)" = "$ORIG_STARTED" ] && report 0 "multi-cycle preserves started_at" || report 1 "multi-cycle preserves started_at"
[ "$(read_field sess-tdd mode)" = '"worker"' ] && report 0 "multi-cycle preserves mode=worker" || report 1 "multi-cycle preserves mode=worker"
[ "$(read_field sess-tdd discipline)" = '"tdd"' ] && report 0 "multi-cycle preserves discipline=tdd" || report 1 "multi-cycle preserves discipline=tdd"
[ "$(read_field sess-tdd paused)" = "false" ] && report 0 "multi-cycle terminates at paused=false" || report 1 "multi-cycle terminates at paused=false"

# Heartbeat MUST have moved forward (every bump refreshes last_seen — alive).
NEW_LAST_SEEN="$(read_field sess-tdd last_seen)"
[ "$NEW_LAST_SEEN" != "$ORIG_LAST_SEEN_1" ] && report 0 "multi-cycle bumps last_seen (session stays alive)" || report 1 "multi-cycle bumps last_seen" "still $ORIG_LAST_SEEN_1"

# ── Invariant 4: paused session is still alive (heartbeat refreshes) ────────
LAST_BEFORE_PAUSE="$(read_field sess-tdd last_seen)"
sleep 1
pause_cmd sess-tdd
LAST_AFTER_PAUSE="$(read_field sess-tdd last_seen)"
[ "$LAST_AFTER_PAUSE" != "$LAST_BEFORE_PAUSE" ] && report 0 "pause itself bumps last_seen (paused-alive distinction preserved)" || report 1 "pause bumps last_seen" "still $LAST_BEFORE_PAUSE"
resume_cmd sess-tdd

# ── Invariant 5: bump on absent session is a silent no-op ───────────────────
bash "$BUMP" "sess-never-registered" --paused true >/tmp/eb-pr-stderr-$$ 2>&1
RC=$?
if [ "$RC" = "0" ]; then
  report 0 "bump --paused on absent session exits 0 (no-op)"
else
  report 1 "bump --paused on absent session exits 0 (no-op)" "rc=$RC, stderr=$(cat /tmp/eb-pr-stderr-$$)"
fi
rm -f /tmp/eb-pr-stderr-$$

# Absent session should NOT have been auto-created.
EXISTS="$(python3 -c "import json; d=json.load(open('$REGISTRY')); print(any(e.get('session_id')=='sess-never-registered' for e in d))")"
[ "$EXISTS" = "False" ] && report 0 "bump on absent session does not auto-create entry" || report 1 "bump on absent session does not auto-create entry"

# ── Invariant 6: paused flag does not bleed across sessions ─────────────────
bash "$REGISTER" "sess-review" "worker" "review" "2026-05-30T00:00:00Z" >/dev/null
pause_cmd sess-tdd
[ "$(read_field sess-tdd paused)" = "true" ] && report 0 "pause sess-tdd: sess-tdd paused=true" || report 1 "pause sess-tdd"
[ "$(read_field sess-review paused)" = "false" ] && report 0 "pause sess-tdd does NOT pause sess-review" || report 1 "pause leaked to sess-review" "sess-review paused=$(read_field sess-review paused)"
resume_cmd sess-tdd

# Symmetric check the other direction.
pause_cmd sess-review
[ "$(read_field sess-review paused)" = "true" ] && report 0 "pause sess-review: sess-review paused=true" || report 1 "pause sess-review"
[ "$(read_field sess-tdd paused)" = "false" ] && report 0 "pause sess-review does NOT pause sess-tdd" || report 1 "pause leaked to sess-tdd"

# ── Invariant 7: pause preserves claim_ids_held ─────────────────────────────
bash "$BUMP" sess-tdd --claim-acquire B042 >/dev/null
bash "$BUMP" sess-tdd --claim-acquire B099 >/dev/null
HELD_BEFORE="$(read_field sess-tdd claim_ids_held)"
pause_cmd sess-tdd
HELD_AFTER_PAUSE="$(read_field sess-tdd claim_ids_held)"
[ "$HELD_BEFORE" = "$HELD_AFTER_PAUSE" ] && report 0 "pause preserves claim_ids_held" || report 1 "pause preserves claim_ids_held" "before=$HELD_BEFORE after=$HELD_AFTER_PAUSE"
resume_cmd sess-tdd
HELD_AFTER_RESUME="$(read_field sess-tdd claim_ids_held)"
[ "$HELD_BEFORE" = "$HELD_AFTER_RESUME" ] && report 0 "resume preserves claim_ids_held" || report 1 "resume preserves claim_ids_held" "before=$HELD_BEFORE after=$HELD_AFTER_RESUME"

echo ""
echo "pause-resume-registry: $PASS pass, $FAIL fail"
if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
