#!/usr/bin/env python3
"""No-model host/MCP preflight. Does not claim effective Codex tool isolation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    host = json.loads(args.host.read_text())
    version = subprocess.run([host["executable"], "--version"], text=True,
                             capture_output=True, check=True, timeout=10)
    help_result = subprocess.run([host["executable"], "exec", "--help"], text=True,
                                 capture_output=True, check=True, timeout=10)
    for flag in ("--ignore-user-config", "--ignore-rules", "--ephemeral", "--sandbox"):
        if flag not in help_result.stdout:
            raise RuntimeError("Missing host flag " + flag)
    # Decode only explicit reviewed command/args overrides; no user config read.
    config = {}
    for index, value in enumerate(host["board_args"]):
        if value == "-c":
            key, raw = host["board_args"][index + 1].split("=", 1)
            config[key] = raw
    command = json.loads(config["mcp_servers.engineering-board.command"])
    server_args = json.loads(config["mcp_servers.engineering-board.args"])
    selected = json.loads(config["mcp_servers.engineering-board.enabled_tools"])
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2025-06-18", "capabilities": {},
            "clientInfo": {"name": "workflow-pilot-no-model-preflight", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    ]
    result = subprocess.run([command, *server_args], input="".join(
        json.dumps(row) + "\n" for row in requests), text=True, capture_output=True,
        check=True, timeout=20)
    responses = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    init = next(row["result"] for row in responses if row.get("id") == 1)
    available = next(row["result"]["tools"] for row in responses if row.get("id") == 2)
    schemas = [tool for tool in available if tool["name"] in selected]
    if sorted(tool["name"] for tool in schemas) != sorted(selected):
        raise RuntimeError("Requested tools missing")
    if not all(tool["annotations"]["readOnlyHint"] for tool in schemas):
        raise RuntimeError("Selected tool not read-only")
    record = {
        "client_version": version.stdout.strip(),
        "client_help_sha256": hashlib.sha256(help_result.stdout.encode()).hexdigest(),
        "host_sha256": hashlib.sha256(args.host.read_bytes()).hexdigest(),
        "command": [command, *server_args], "initialize": init,
        "selected_tool_schemas": schemas, "stderr": result.stderr,
        "model_calls": 0,
        "limits": "Direct MCP schema/launcher verification, not effective Codex tool catalog or OS read-isolation proof.",
        "official_configuration_reference": "https://learn.chatgpt.com/docs/extend/mcp?surface=cli"
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"client_version": record["client_version"],
                      "selected_tools": selected, "model_calls": 0,
                      "output": str(args.output)}))


if __name__ == "__main__":
    main()
