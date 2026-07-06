#!/usr/bin/env bash
# tests/orchestration/board-setup-command.sh — structural lint for the
# /board-setup onboarding wizard (eb-self F002 / IMPROVEMENTS #9).
#
# /board-setup is a composing command: it must infer a default project name,
# reuse the /board-init procedure (never re-implement it), run the permission
# self-check without editing settings, and end with the 3-line ready summary,
# leaving the session passive. This lint pins that contract.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
CMD="$ROOT/commands/board-setup.md"

PASS=0; FAIL=0
report() {
  if [ "$1" = "0" ]; then printf "  [PASS] %s\n" "$2"; PASS=$((PASS+1));
  else printf "  [FAIL] %s\n" "$2"; FAIL=$((FAIL+1)); fi
}

[ -f "$CMD" ] && report 0 "board-setup.md exists" || { report 1 "board-setup.md exists"; echo "board-setup-command: $PASS pass, $FAIL fail"; exit 1; }

grep -q "basename of \`\$CLAUDE_PROJECT_DIR\`" "$CMD" \
  && report 0 "infers the project name from the repo dir basename" \
  || report 1 "infers the project name from the repo dir basename"

grep -q "commands/board-init.md" "$CMD" \
  && report 0 "delegates scaffolding to the /board-init procedure" \
  || report 1 "delegates scaffolding to the /board-init procedure"

grep -q "board-permission-self-check.sh" "$CMD" \
  && report 0 "runs the permission self-check" \
  || report 1 "runs the permission self-check"

grep -q "never edits your settings" "$CMD" \
  && report 0 "permission install stays interactive (no settings edits)" \
  || report 1 "permission install stays interactive"

grep -q "Board ready:" "$CMD" && grep -q "Capture is on:" "$CMD" && grep -q "Pipeline permissions:" "$CMD" \
  && report 0 "3-line ready summary present" \
  || report 1 "3-line ready summary present"

grep -q "stays in \*\*passive\*\* mode" "$CMD" \
  && report 0 "leaves the session passive (no mode file)" \
  || report 1 "leaves the session passive"

grep -qi "idempotent" "$CMD" \
  && report 0 "documented idempotent" \
  || report 1 "documented idempotent"

# The smart default must also live in /board-init itself (shared behavior).
grep -q "default it to the repository directory" "$ROOT/commands/board-init.md" \
  && report 0 "board-init Step 1 carries the same smart default" \
  || report 1 "board-init Step 1 carries the same smart default"

echo ""
echo "board-setup-command: $PASS pass, $FAIL fail"
[ "$FAIL" -eq 0 ]
