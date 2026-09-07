#!/usr/bin/env bash
# Structural contract for /board-demo.
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
CMD="$ROOT/commands/board-demo.md"
PASS=0
FAIL=0

check() {
  local label="$1" needle="$2"
  if grep -qF -- "$needle" "$CMD"; then
    printf "  [PASS] %s\n" "$label"
    PASS=$((PASS + 1))
  else
    printf "  [FAIL] %s\n" "$label"
    FAIL=$((FAIL + 1))
  fi
}

[ -f "$CMD" ] || {
  echo "MISSING FILE: $CMD" >&2
  exit 1
}
check "frontmatter description" "description:"
check "frontmatter argument hint" "argument-hint: [--clean <run-id>]"
check "creates through deterministic script" 'board-demo.sh" create'
check "uses board-insights interpretation skill" "board-insights"
check "quoted hypothesis heredoc" "<<'EB_HYPOTHESIS_JSON'"
check "persists proposed status" 'status: proposed'
check "documents fingerprinted cleanup" 'board-demo.sh" --clean <run-id>'
check "refuses broad manual deletion fallback" "never broaden the target"
check "does not mutate real board" "No router, real board, source, settings, Git configuration"
check "no automatic browser launch" "Do not automatically open a browser"

echo ""
echo "board-demo-command: $PASS pass, $FAIL fail"
[ "$FAIL" -eq 0 ]
