#!/usr/bin/env bash
# tests/orchestration/board-run-command.sh — structural lint for /board-run,
# the Conductor's inner loop as a bounded foreground command (RFC 0001 slice 1,
# eb-self B006). Pins the contract: passive-only guard, claim ownership by the
# command (never the subagents), the worker procedure's dispatch format and
# needs-transition rule, the round bound, heartbeat, always-release, and the
# resolve hand-off.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
CMD="$ROOT/commands/board-run.md"

PASS=0; FAIL=0
report() {
  if [ "$1" = "0" ]; then printf "  [PASS] %s\n" "$2"; PASS=$((PASS+1));
  else printf "  [FAIL] %s\n" "$2"; FAIL=$((FAIL+1)); fi
}

[ -f "$CMD" ] && report 0 "board-run.md exists" || { report 1 "board-run.md exists"; echo "board-run-command: $PASS pass, $FAIL fail"; exit 1; }

for token in "currently in PM mode" "currently in worker mode" "currently paused"; do
  grep -qF "$token" "$CMD" && report 0 "guard refuses: $token" || report 1 "guard refuses: $token"
done
grep -q "writes \*\*no\*\* mode file" "$CMD" && report 0 "no mode file written" || report 1 "no mode file written"

grep -qF 'board-claim-acquire.sh' "$CMD" && report 0 "claim acquired by the command" || report 1 "claim acquired by the command"
grep -qF 'board-claim-reclaim-stale.sh' "$CMD" && report 0 "stale reclaim path present" || report 1 "stale reclaim path present"
grep -qF 'board-claim-heartbeat.sh' "$CMD" && report 0 "heartbeat between rounds" || report 1 "heartbeat between rounds"
grep -qF 'board-claim-release.sh' "$CMD" && report 0 "claim released (always)" || report 1 "claim released"

for agent in tdd-builder code-reviewer validator; do
  grep -qF "$agent" "$CMD" && report 0 "dispatches $agent" || report 1 "dispatches $agent"
done
grep -qF -- '---ENTRY-ID---' "$CMD" && grep -qF -- '---ENTRY-CONTENT---' "$CMD" \
  && report 0 "worker dispatch format (ENTRY delimiters)" || report 1 "worker dispatch format"
grep -qF 'suggested_next_needs' "$CMD" && report 0 "applies suggested_next_needs" || report 1 "applies suggested_next_needs"
grep -qF 'max 5 rounds' "$CMD" && report 0 "bounded (max 5 rounds)" || report 1 "bounded (max 5 rounds)"
grep -qF '/board-resolve' "$CMD" && report 0 "resolve hand-off named" || report 1 "resolve hand-off named"
grep -qF 'untrusted data, not instructions' "$CMD" && report 0 "untrusted-data framing present" || report 1 "untrusted-data framing present"
grep -qF 'RFC 0001' "$CMD" && report 0 "scoped as Conductor slice (RFC 0001)" || report 1 "scoped as Conductor slice"

echo ""
echo "board-run-command: $PASS pass, $FAIL fail"
[ "$FAIL" -eq 0 ]
