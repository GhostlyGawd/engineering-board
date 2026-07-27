#!/usr/bin/env bash
# Deterministic substrate test for proposed-hypothesis persistence and rendering.
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
DEMO="$ROOT/hooks/scripts/board-demo.sh"
PROJECT="$(mktemp -d)"
trap 'rm -rf "$PROJECT"' EXIT
PASS=0
FAIL=0

pass() { printf "  [PASS] %s\n" "$1"; PASS=$((PASS + 1)); }
fail() { printf "  [FAIL] %s\n" "$1"; FAIL=$((FAIL + 1)); }

CREATE="$(CLAUDE_PROJECT_DIR="$PROJECT" EB_DEMO_RUN_ID=hypothesis-test bash "$DEMO" create)"
echo "$CREATE" | python3 -c 'import json,sys; assert json.load(sys.stdin)["status"] == "awaiting_hypothesis"' \
  && pass "create returns awaiting_hypothesis" || fail "create state"

cat > "$PROJECT/payload.json" <<'JSON'
{
  "title": "Lifecycle semantics are duplicated across adapters",
  "root_cause": "The three adapters appear to interpret one lifecycle state independently.",
  "supporting_evidence": [
    {"id": "B001", "reason": "Worker routing skips an eligible state."},
    {"id": "B002", "reason": "The board renders the same state in the wrong lane."},
    {"id": "B003", "reason": "MCP omits the same state from ready work."}
  ],
  "alternatives": ["The adapters may have three unrelated filtering defects."],
  "falsifier": "All adapters consume one shared contract while the fixture still reproduces."
}
JSON

RESULT="$(CLAUDE_PROJECT_DIR="$PROJECT" bash "$DEMO" hypothesis hypothesis-test < "$PROJECT/payload.json" 2>/dev/null)"
echo "$RESULT" | python3 -c 'import json,sys; assert json.load(sys.stdin)["status"] == "complete"' \
  && pass "valid hypothesis reaches complete state" || fail "complete state"

RUN="$PROJECT/.engineering-board/demo/pattern-intelligence/hypothesis-test"
H="$RUN/hypotheses/H001-lifecycle-semantics-are-duplicated-across-adapters.md"
if grep -q '^status: proposed$' "$H" && grep -q '^derived_from: \[B001, B002, B003\]$' "$H"; then
  pass "hypothesis stays proposed and cites every member"
else
  fail "hypothesis authority fields"
fi
for section in "Proposed root cause" "Supporting evidence" "Alternative explanations" "Falsifier" "Outcome history"; do
  grep -q "^## $section$" "$H" || fail "missing section: $section"
done
pass "required hypothesis sections present"
grep -q '^status: confirmed$' "$H" && fail "hypothesis auto-confirmed" || pass "confidence does not auto-confirm"

HTML="$RUN/pattern-intelligence.html"
if grep -q 'Three symptoms. One systemic investigation.' "$HTML" \
  && grep -q 'status: proposed' "$HTML" \
  && grep -q 'B001' "$HTML" \
  && grep -q 'C001' "$HTML"; then
  pass "static evidence-cluster-hypothesis visual rendered"
else
  fail "static visual content"
fi

CLAUDE_PROJECT_DIR="$PROJECT" EB_DEMO_RUN_ID=invalid-test bash "$DEMO" create >/dev/null
cat > "$PROJECT/invalid.json" <<'JSON'
{
  "title": "Incomplete evidence",
  "root_cause": "A guess missing one required member.",
  "supporting_evidence": [
    {"id": "B001", "reason": "One."},
    {"id": "B002", "reason": "Two."}
  ],
  "alternatives": ["Another cause."],
  "falsifier": "A disconfirming observation."
}
JSON
RC=0
CLAUDE_PROJECT_DIR="$PROJECT" bash "$DEMO" hypothesis invalid-test \
  < "$PROJECT/invalid.json" >/dev/null 2>"$PROJECT/invalid-error.json" || RC=$?
INVALID_RUN="$PROJECT/.engineering-board/demo/pattern-intelligence/invalid-test"
if [ "$RC" -eq 2 ] && grep -q "supporting evidence must cite exactly" "$PROJECT/invalid-error.json" \
  && [ ! -d "$INVALID_RUN/hypotheses" ]; then
  pass "missing citation rejects the hypothesis without partial artifact"
else
  fail "invalid hypothesis rejection"
fi

CLAUDE_PROJECT_DIR="$PROJECT" bash "$DEMO" --clean hypothesis-test >/dev/null
CLAUDE_PROJECT_DIR="$PROJECT" bash "$DEMO" --clean invalid-test >/dev/null

echo ""
echo "hypothesis-contract: $PASS pass, $FAIL fail"
[ "$FAIL" -eq 0 ]
