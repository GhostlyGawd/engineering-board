#!/usr/bin/env bash
# tests/docs-coherence.sh — Verify the tool/command counts stated in the docs
# match reality, so the counts can never silently drift again (T-B root fix:
# "11 tools"/"13 commands" survived two feature releases as prose).
#
# Asserts:
#   (a) every "N tools" / "N-tool" / "MCP tools (N)" figure in README.md,
#       docs/index.html, mcp-server/README.md, and docs/llms.txt equals the
#       actual count of '"name": "board_' tools in the MCP server source
#       (each of those four files must state the count at least once);
#   (b) the "Commands (N)" figure in README.md equals `ls commands/*.md | wc -l`.
#
# Usage:
#   bash tests/docs-coherence.sh [plugin-root]
#
# Exits 0 iff every stated count matches the source of truth.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"

SERVER="$ROOT/mcp-server/engineering_board_mcp.py"
COMMANDS_DIR="$ROOT/commands"
DOC_FILES=(
  "$ROOT/README.md"
  "$ROOT/docs/index.html"
  "$ROOT/mcp-server/README.md"
  "$ROOT/docs/llms.txt"
)

for f in "$SERVER" "$ROOT/README.md" "$ROOT/docs/index.html" \
         "$ROOT/mcp-server/README.md" "$ROOT/docs/llms.txt"; do
  if [ ! -f "$f" ]; then
    echo "docs-coherence: MISSING $f" >&2
    exit 1
  fi
done
if [ ! -d "$COMMANDS_DIR" ]; then
  echo "docs-coherence: MISSING $COMMANDS_DIR" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "docs-coherence: python3 not on PATH" >&2
  exit 1
fi

TOOL_COUNT="$(grep -c '"name": "board_' "$SERVER")"
COMMAND_COUNT="$(ls "$COMMANDS_DIR"/*.md 2>/dev/null | wc -l | tr -d '[:space:]')"

if [ "$TOOL_COUNT" -lt 1 ] || [ "$COMMAND_COUNT" -lt 1 ]; then
  echo "docs-coherence: implausible ground truth (tools=$TOOL_COUNT commands=$COMMAND_COUNT)" >&2
  exit 1
fi

EXIT=0
RESULT="$(python3 - "$TOOL_COUNT" "$COMMAND_COUNT" "$ROOT/README.md" "${DOC_FILES[@]}" <<'PY'
import re, sys

tool_count = int(sys.argv[1])
command_count = int(sys.argv[2])
readme_path = sys.argv[3]
doc_paths = sys.argv[4:]

# The parseable count patterns docs MUST use (normalize the prose if a new
# phrasing can't be matched — that keeps this test able to see every figure):
#   "12 tools" · "12-tool" · "MCP tools (12)"
TOOL_PAT = re.compile(r"\b(\d+)\s+tools\b|\b(\d+)-tool\b|\bMCP tools \((\d+)\)")

fail = False
for path in doc_paths:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    stated = [int(next(g for g in m.groups() if g)) for m in TOOL_PAT.finditer(text)]
    if not stated:
        print("FAIL %s states no tool count (expected at least one 'N tools' figure)" % path)
        fail = True
        continue
    bad = sorted(set(n for n in stated if n != tool_count))
    if bad:
        print("FAIL %s states tool count(s) %s but the server defines %d tools"
              % (path, bad, tool_count))
        fail = True
    else:
        print("OK   %s: %d stated tool figure(s), all == %d" % (path, len(stated), tool_count))

with open(readme_path, "r", encoding="utf-8") as f:
    readme = f.read()
m = re.search(r"\bCommands \((\d+)\)", readme)
if not m:
    print("FAIL %s has no 'Commands (N)' figure" % readme_path)
    fail = True
elif int(m.group(1)) != command_count:
    print("FAIL %s says Commands (%s) but commands/ has %d files"
          % (readme_path, m.group(1), command_count))
    fail = True
else:
    print("OK   %s: Commands (%d) == commands/*.md count" % (readme_path, command_count))

sys.exit(1 if fail else 0)
PY
)" || EXIT=$?

echo "$RESULT"
if [ "$EXIT" -eq 0 ]; then
  echo "docs-coherence: OK (tools=$TOOL_COUNT commands=$COMMAND_COUNT)"
fi
exit "$EXIT"
