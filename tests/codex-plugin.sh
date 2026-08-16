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
codex_hooks = json.loads((root / "hooks/codex-hooks.json").read_text())
codex_mcp = json.loads((root / "codex-mcp.json").read_text())
claude_mcp = json.loads((root / ".mcp.json").read_text())
claude = json.loads((root / ".claude-plugin/plugin.json").read_text())
claude_market = json.loads((root / ".claude-plugin/marketplace.json").read_text())
codex_market = json.loads((root / ".agents/plugins/marketplace.json").read_text())

assert manifest["name"] == claude["name"] == "engineering-board"
assert manifest["version"] == claude["version"]
assert manifest["skills"] == "./skills/"
assert manifest["mcpServers"] == "./codex-mcp.json"
assert manifest["hooks"] == "./hooks/codex-hooks.json"
assert codex_hooks == {"hooks": {}}
assert claude_market["plugins"][0]["source"] == "./"
assert codex_market["name"] == "engineering-board"
assert codex_market["interface"]["displayName"] == "Engineering Board"
assert len(codex_market["plugins"]) == 1
codex_entry = codex_market["plugins"][0]
claude_entry = claude_market["plugins"][0]
assert codex_entry["name"] == manifest["name"]
assert codex_entry["version"] == manifest["version"]
assert codex_entry["source"] == {
    "source": "url",
    "url": "https://github.com/GhostlyGawd/engineering-board.git",
    "ref": f"v{manifest['version']}",
}
assert codex_entry["policy"] == claude_entry["policy"]
assert codex_entry["category"] == claude_entry["category"]
assert set(codex_mcp["mcpServers"]) == {"engineering-board"}
server = codex_mcp["mcpServers"]["engineering-board"]
assert server == {
    "command": "node",
    "args": ["scripts/engineering-board-mcp-launcher.mjs"],
    "cwd": ".",
    "default_tools_approval_mode": "writes",
}
assert claude_mcp == {
    "mcpServers": {
        "engineering-board": {
            "command": "node",
            "args": ["scripts/engineering-board-mcp-launcher.mjs"],
            "cwd": ".",
        }
    }
}
consolidate_skill = (root / "skills/board-consolidate/SKILL.md").read_text()
assert "server restores the preview session scope" in consolidate_skill
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
expected = {
    "board_init": (False, True, True, False),
    "board_list_projects": (True, False, True, False),
    "board_create_entry": (False, True, False, False),
    "board_list_entries": (True, False, True, False),
    "board_get_entry": (True, False, True, False),
    "board_update_entry": (False, True, False, False),
    "board_graph": (False, True, False, False),
    "board_insights": (True, False, True, False),
    "board_context": (True, False, True, False),
    "board_outcomes": (False, True, True, False),
    "board_hypotheses": (False, True, True, False),
    "board_patterns": (False, True, True, False),
    "board_promote_findings": (False, True, False, False),
    "board_rebuild": (False, True, True, False),
    "board_capture_finding": (False, False, False, False),
    "board_claim": (False, False, True, False),
    "board_release": (False, True, True, False),
    "board_remember": (False, True, False, False),
    "board_status": (True, False, True, False),
}
assert {tool["name"] for tool in tools} == set(expected)
for tool in tools:
    read_only, destructive, idempotent, open_world = expected[tool["name"]]
    assert set(tool) == {"name", "description", "inputSchema", "annotations"}
    assert tool["annotations"] == {
        "readOnlyHint": read_only,
        "destructiveHint": destructive,
        "idempotentHint": idempotent,
        "openWorldHint": open_world,
    }
promote = next(tool for tool in tools if tool["name"] == "board_promote_findings")
properties = promote["inputSchema"]["properties"]
assert "restores that preview's session scope" in properties["apply"]["description"]
assert "does not require it" in properties["session"]["description"]
missing_root = responses[3]["result"]
assert missing_root["isError"] is True
assert "missing required argument: root" in missing_root["content"][0]["text"]
PY

echo "codex-plugin: pinned marketplace, host-safe hook boundary, isolated MCP configuration, launcher, and 19 tools verified"
