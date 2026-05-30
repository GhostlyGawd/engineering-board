#!/usr/bin/env bash
# tests/modes/mode-transition-guard.sh — exercise the deterministic
# mode-transition guard (hooks/scripts/board-mode-guard.sh) across every
# cell of the ARCHITECTURE.md §11.5 refusal matrix.
#
# The four mode commands (/pm-start, /worker-start, /board-pause,
# /board-resume) used to each re-implement the matrix in markdown that the
# model interprets. That is non-deterministic — the model may produce a
# different error wording on a different turn, and the matrix has six rows
# × four columns of conditional logic to get right in prose every time.
#
# The guard centralises the decision in one shell script with three exit
# codes (0 ALLOW, 2 NOOP, 3 REFUSE). This test pins every matrix cell so
# any future refactor regresses loudly.
#
# Exits 0 iff every fixture+target produces the expected exit code AND
# stdout payload.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

GUARD="$ROOT/hooks/scripts/board-mode-guard.sh"
if [ ! -x "$GUARD" ]; then
  echo "MISSING or non-executable: $GUARD" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 required" >&2
  exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

export CLAUDE_PROJECT_DIR="$TMP"
mkdir -p "$TMP/.engineering-board"
SF="$TMP/.engineering-board/session-mode.json"

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

# Set up a session-mode.json fixture. Pass JSON content as $1, or empty
# string to remove the file.
fixture() {
  local body="$1"
  if [ -z "$body" ]; then
    rm -f "$SF"
  else
    printf '%s' "$body" > "$SF"
  fi
}

# Run the guard, capture exit code + stdout. Assert both.
expect() {
  local label="$1" expected_rc="$2" stdout_needle="$3"
  shift 3
  local actual_stdout actual_rc
  actual_stdout="$(bash "$GUARD" "$@" 2>/dev/null)" && actual_rc=0 || actual_rc=$?
  if [ "$actual_rc" != "$expected_rc" ]; then
    report 1 "$label" "expected rc=$expected_rc, got rc=$actual_rc, stdout='$actual_stdout'"
    return
  fi
  if ! printf '%s' "$actual_stdout" | grep -qF -- "$stdout_needle"; then
    report 1 "$label" "expected stdout to contain '$stdout_needle', got '$actual_stdout'"
    return
  fi
  report 0 "$label"
}

# ── Row 1: no session-mode.json (fresh / unset / null) ───────────────────────
fixture ""
expect "fresh → /pm-start ALLOW"                        0 "CURRENT_MODE=null" pm
expect "fresh → /worker-start --discipline tdd ALLOW"   0 "CURRENT_MODE=null" worker --discipline tdd
expect "fresh → /board-pause ALLOW (prev=null)"         0 "PREVIOUS_MODE=null" paused
expect "fresh → /board-resume NOOP"                     2 "not currently paused" resumed

# ── Row 2: mode=pm ───────────────────────────────────────────────────────────
fixture '{"mode":"pm","previous_mode":null,"started_at":"2026-05-29T00:00:00Z","session_id":"s1"}'
expect "pm → /pm-start NOOP"                            2 "already in PM mode" pm
expect "pm → /worker-start --discipline tdd REFUSE"     3 "currently in PM mode" worker --discipline tdd
expect "pm → /board-pause ALLOW (prev=pm)"              0 "PREVIOUS_MODE=pm" paused
expect "pm → /board-resume NOOP"                        2 "not currently paused" resumed

# ── Row 3: mode=worker, discipline=tdd ───────────────────────────────────────
fixture '{"mode":"worker","discipline":"tdd","previous_mode":null,"started_at":"2026-05-29T00:00:00Z","session_id":"s2"}'
expect "worker:tdd → /pm-start REFUSE"                  3 "currently in worker mode" pm
expect "worker:tdd → /worker-start tdd NOOP"            2 "already in worker mode (discipline=tdd)" worker --discipline tdd
expect "worker:tdd → /worker-start review REFUSE"       3 "Restart the session to switch to discipline=review" worker --discipline review
expect "worker:tdd → /board-pause ALLOW (prev=worker)"  0 "PREVIOUS_MODE=worker" paused
expect "worker:tdd → /board-pause preserves disc"       0 "PREVIOUS_DISCIPLINE=tdd" paused
expect "worker:tdd → /board-resume NOOP"                2 "not currently paused" resumed

# ── Row 4: mode=paused, previous_mode=null ───────────────────────────────────
fixture '{"mode":"paused","previous_mode":null,"previous_discipline":null,"paused_at":"2026-05-29T00:00:00Z","session_id":"s3"}'
expect "paused(prev=null) → /pm-start REFUSE"           3 "currently paused" pm
expect "paused(prev=null) → /worker-start REFUSE"       3 "currently paused" worker --discipline tdd
expect "paused(prev=null) → /board-pause NOOP"          2 "already paused" paused
expect "paused(prev=null) → /board-resume ALLOW"        0 "RESTORE_MODE=null" resumed

# ── Row 5: mode=paused, previous_mode=pm ─────────────────────────────────────
fixture '{"mode":"paused","previous_mode":"pm","previous_discipline":null,"paused_at":"2026-05-29T00:00:00Z","session_id":"s4"}'
expect "paused(prev=pm) → /pm-start REFUSE"             3 "currently paused" pm
expect "paused(prev=pm) → /board-resume ALLOW (restore pm)" 0 "RESTORE_MODE=pm" resumed

# ── Row 6: mode=paused, previous_mode=worker, previous_discipline=review ─────
fixture '{"mode":"paused","previous_mode":"worker","previous_discipline":"review","paused_at":"2026-05-29T00:00:00Z","session_id":"s5"}'
expect "paused(prev=worker:review) → /pm-start REFUSE"  3 "currently paused" pm
expect "paused(prev=worker:review) → /board-resume ALLOW (restore worker)" 0 "RESTORE_MODE=worker" resumed
expect "paused(prev=worker:review) → restores disc=review" 0 "RESTORE_DISCIPLINE=review" resumed

# ── Bad arguments ────────────────────────────────────────────────────────────
fixture ""
out=$(bash "$GUARD" 2>&1) && rc=0 || rc=$?
if [ "$rc" = "1" ]; then report 0 "no-args → exit 1"; else report 1 "no-args → exit 1" "got rc=$rc"; fi

out=$(bash "$GUARD" worker 2>&1) && rc=0 || rc=$?
if [ "$rc" = "1" ]; then report 0 "worker without --discipline → exit 1"; else report 1 "worker without --discipline → exit 1" "got rc=$rc"; fi

out=$(bash "$GUARD" worker --discipline bogus 2>&1) && rc=0 || rc=$?
if [ "$rc" = "1" ]; then report 0 "worker with invalid discipline → exit 1"; else report 1 "worker with invalid discipline → exit 1" "got rc=$rc"; fi

out=$(bash "$GUARD" totally-fake-target 2>&1) && rc=0 || rc=$?
if [ "$rc" = "1" ]; then report 0 "unknown target → exit 1"; else report 1 "unknown target → exit 1" "got rc=$rc"; fi

# ── Robustness: corrupt session-mode.json treated as fresh ───────────────────
fixture 'this is not json {{{'
expect "corrupt JSON → /pm-start ALLOW (treated as null)"  0 "CURRENT_MODE=null" pm

# Unrecognized mode value normalized to null.
fixture '{"mode":"chimera"}'
expect "unrecognized mode → /pm-start ALLOW (normalized)" 0 "CURRENT_MODE=null" pm

# ── --discipline=value long form ─────────────────────────────────────────────
fixture ""
expect "worker --discipline=tdd long form ALLOW" 0 "CURRENT_MODE=null" worker --discipline=tdd

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "mode-transition-guard: $PASS pass, $FAIL fail"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0
