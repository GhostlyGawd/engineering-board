#!/usr/bin/env bash
# Validate the repository-owned Codex plugin and its portable MCP launcher.

set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
OUT="$(mktemp)"
trap 'rm -f "$OUT"' EXIT

command -v node >/dev/null 2>&1 || {
  echo "codex-plugin: node is required" >&2
  exit 1
}

python3 - "$ROOT" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
manifest = json.loads((root / ".codex-plugin/plugin.json").read_text())
mcp = json.loads((root / ".mcp.json").read_text())
claude = json.loads((root / ".claude-plugin/plugin.json").read_text())

assert manifest["name"] == claude["name"] == "engineering-board"
assert manifest["version"] == claude["version"]
assert manifest["skills"] == "./skills/"
assert manifest["mcpServers"] == "./.mcp.json"
assert set(mcp["mcpServers"]) == {"engineering-board"}
server = mcp["mcpServers"]["engineering-board"]
assert server == {
    "command": "node",
    "args": ["scripts/engineering-board-mcp-launcher.mjs"],
    "cwd": ".",
}
PY

node "$ROOT/scripts/engineering-board-mcp-launcher.mjs" >"$OUT" <<'JSON'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"codex-plugin-test","version":"1"}}}
{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"board_status","arguments":{"project":"test"}}}
JSON

python3 - "$OUT" <<'PY'
import json
import pathlib
import sys

responses = {
    item["id"]: item
    for line in pathlib.Path(sys.argv[1]).read_text().splitlines()
    if line.strip()
    for item in [json.loads(line)]
    if "id" in item
}
assert responses[1]["result"]["protocolVersion"] == "2025-06-18"
tools = responses[2]["result"]["tools"]
assert len(tools) == 19
assert {tool["name"] for tool in tools} >= {
    "board_context",
    "board_claim",
    "board_release",
    "board_promote_findings",
}
missing_root = responses[3]["result"]
assert missing_root["isError"] is True
assert "missing required argument: root" in missing_root["content"][0]["text"]
PY

echo "codex-plugin: manifest, isolated MCP configuration, launcher, and 19 tools verified"
