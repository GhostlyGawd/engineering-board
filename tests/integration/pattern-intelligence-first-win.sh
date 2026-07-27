#!/usr/bin/env bash
# Full contained journey: create -> interpret -> render -> tamper refusal -> clean.
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
DEMO="$ROOT/hooks/scripts/board-demo.sh"
PROJECT="$(mktemp -d)"
trap 'rm -rf "$PROJECT"' EXIT
PASS=0
FAIL=0

pass() { printf "  [PASS] %s\n" "$1"; PASS=$((PASS + 1)); }
fail() { printf "  [FAIL] %s\n" "$1"; FAIL=$((FAIL + 1)); }
digest() { sha256sum "$1" | awk '{print $1}'; }

mkdir -p "$PROJECT/engineering-board/real" "$PROJECT/src" "$PROJECT/.claude"
printf '# real router\n' > "$PROJECT/engineering-board/BOARD-ROUTER.md"
printf '# real board\n' > "$PROJECT/engineering-board/real/BOARD.md"
printf 'real source\n' > "$PROJECT/src/app.txt"
printf '{"permissions":{"allow":[]}}\n' > "$PROJECT/.claude/settings.json"
git -C "$PROJECT" init -q
git -C "$PROJECT" config user.name "Demo Test"
git -C "$PROJECT" config user.email "demo@example.invalid"

ROUTER_BEFORE="$(digest "$PROJECT/engineering-board/BOARD-ROUTER.md")"
BOARD_BEFORE="$(digest "$PROJECT/engineering-board/real/BOARD.md")"
SOURCE_BEFORE="$(digest "$PROJECT/src/app.txt")"
SETTINGS_BEFORE="$(digest "$PROJECT/.claude/settings.json")"
GIT_BEFORE="$(digest "$PROJECT/.git/config")"

CREATE="$(CLAUDE_PROJECT_DIR="$PROJECT" EB_DEMO_RUN_ID=full-run bash "$DEMO" create)"
RUN="$PROJECT/.engineering-board/demo/pattern-intelligence/full-run"
echo "$CREATE" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["status"] == "awaiting_hypothesis" and not d["reused"]' \
  && pass "first create is contained and awaiting interpretation" || fail "first create"

REUSE="$(CLAUDE_PROJECT_DIR="$PROJECT" EB_DEMO_RUN_ID=full-run bash "$DEMO" create)"
echo "$REUSE" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["reused"]' \
  && pass "unchanged repeat reuses the run without overwrite" || fail "repeat behavior"

cat > "$PROJECT/hypothesis.json" <<'JSON'
{
  "title": "Lifecycle semantics are duplicated across adapters",
  "root_cause": "The worker, renderer, and MCP adapter appear to interpret the same lifecycle state independently.",
  "supporting_evidence": [
    {"id": "B001", "reason": "Worker selection skips the eligible review state."},
    {"id": "B002", "reason": "Board rendering assigns the equivalent state to the wrong lane."},
    {"id": "B003", "reason": "MCP ready-work output omits the equivalent state."}
  ],
  "alternatives": ["Three unrelated adapter-specific filters could produce similar symptoms."],
  "falsifier": "The adapters already consume one shared contract and the three symptoms still reproduce."
}
JSON
CLAUDE_PROJECT_DIR="$PROJECT" bash "$DEMO" hypothesis full-run \
  < "$PROJECT/hypothesis.json" >/dev/null 2>/dev/null

if [ "$(digest "$PROJECT/engineering-board/BOARD-ROUTER.md")" = "$ROUTER_BEFORE" ] \
  && [ "$(digest "$PROJECT/engineering-board/real/BOARD.md")" = "$BOARD_BEFORE" ] \
  && [ "$(digest "$PROJECT/src/app.txt")" = "$SOURCE_BEFORE" ] \
  && [ "$(digest "$PROJECT/.claude/settings.json")" = "$SETTINGS_BEFORE" ] \
  && [ "$(digest "$PROJECT/.git/config")" = "$GIT_BEFORE" ]; then
  pass "real board, source, settings, and Git configuration remain unchanged"
else
  fail "real-state mutation boundary"
fi

python3 - "$RUN/graph.json" "$RUN/manifest.json" <<'PY' \
  && pass "actual run records one 3-domain cluster and complete manifest" \
  || fail "complete artifact semantics"
import json, sys
graph = json.load(open(sys.argv[1], encoding="utf-8"))
manifest = json.load(open(sys.argv[2], encoding="utf-8"))
cluster = graph["topology"]["clusters"][0]
assert cluster["members"] == ["B001", "B002", "B003"]
assert cluster["affected_domains"] == ["board-view", "hooks", "mcp-server"]
assert manifest["status"] == "complete"
assert "pattern-intelligence.html" in manifest["files"]
PY

printf 'user note\n' > "$RUN/notes.txt"
RC=0
CLAUDE_PROJECT_DIR="$PROJECT" bash "$DEMO" --clean full-run \
  >/dev/null 2>"$PROJECT/cleanup-error.json" || RC=$?
if [ "$RC" -eq 3 ] && grep -q "unexpected: notes.txt" "$PROJECT/cleanup-error.json" \
  && [ -d "$RUN" ]; then
  pass "tampered scope refuses cleanup and preserves the run"
else
  fail "tamper cleanup boundary"
fi

rm "$RUN/notes.txt"
CLAUDE_PROJECT_DIR="$PROJECT" bash "$DEMO" --clean full-run >/dev/null
[ ! -e "$RUN" ] && pass "clean manifest-owned run is removed exactly" || fail "clean run remained"

if ! grep -E '(^|[^a-z])(curl|wget|requests\.|urllib\.|httpx\.)' \
  "$ROOT/hooks/scripts/board-demo.sh" "$ROOT/hooks/scripts/board_demo.py" \
  "$ROOT/hooks/scripts/board-graph-build.py" >/dev/null; then
  pass "demo scripts contain no outbound network client"
else
  fail "network client found in demo scripts"
fi

echo ""
echo "pattern-intelligence-first-win: $PASS pass, $FAIL fail"
[ "$FAIL" -eq 0 ]
