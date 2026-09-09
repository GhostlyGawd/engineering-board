#!/usr/bin/env python3
"""Retained, no-model installed MCP retrieve-to-detail verification."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import tempfile
import threading


def inventory(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--server-command", nargs="+", required=True)
    args = parser.parse_args()
    evidence = {"command": args.server_command, "model_calls": 0, "cases": []}
    with tempfile.TemporaryDirectory(prefix="eb-f005-installed-") as temp:
        root = Path(temp).resolve()
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        with tempfile.TemporaryFile(mode="w+t") as stderr:
            process = subprocess.Popen(args.server_command, stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=stderr,
                                       text=True, env=env, cwd=root)
            replies = queue.Queue()
            def drain():
                for line in process.stdout:
                    replies.put(line)
            reader = threading.Thread(target=drain, daemon=True)
            reader.start()
            request_id = 0
            def request(method, params):
                nonlocal request_id
                request_id += 1
                process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": request_id,
                                                "method": method, "params": params}) + "\n")
                process.stdin.flush()
                response = json.loads(replies.get(timeout=15))
                assert response.get("id") == request_id and "error" not in response, response
                return response["result"]
            def call(name, params, error=False):
                result = request("tools/call", {"name": name, "arguments": params})
                assert result.get("isError") is error, result
                return result if error else json.loads(result["content"][0]["text"])
            try:
                evidence["initialize"] = request("initialize", {
                    "protocolVersion": "2025-06-18", "capabilities": {},
                    "clientInfo": {"name": "f005-installed-verification", "version": "1"}})
                process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
                process.stdin.flush()
                listed = request("tools/list", {})["tools"]
                evidence["read_tool_schemas"] = [t for t in listed if t["name"] in
                                                  ("board_context", "board_get_entry")]
                assert len(listed) == 19
                for tool in evidence["read_tool_schemas"]:
                    assert tool["annotations"]["readOnlyHint"] is True
                for case_id, expected_id, filename in (
                    ("H-useful-catalog", "H101", "catalog.py"),
                    ("H-control-identifiers", "H102", "parts.py")):
                    case = args.repo / "evaluation/workflow-pilot/cases" / case_id
                    workspace = root / expected_id
                    shutil.copytree(case / "taskrepo", workspace)
                    common = {"root": str(workspace), "project": "pilot"}
                    call("board_init", {**common, "agents_md": False})
                    board = workspace / "engineering-board/pilot"
                    shutil.copytree(case / "board", board, dirs_exist_ok=True)
                    call("board_rebuild", common)
                    before = inventory(workspace)
                    context = call("board_context", {**common, "files": [filename],
                                                     "task": "Investigate the reported behavior"})
                    match = next(r for r in context["results"] if r["id"] == expected_id)
                    detail = call("board_get_entry", {**common, "entry_id": match["id"]})
                    assert detail["id"] == expected_id
                    assert detail["frontmatter"]["status"] == "proposed"
                    assert detail["markdown"] == (board / "hypotheses" / (expected_id + ".md")).read_text()
                    for section in ("## Proposed root cause", "## Alternative explanations", "## Falsifier"):
                        assert section in detail["markdown"], section
                    missing = call("board_get_entry", {**common, "entry_id": "H999"}, error=True)
                    after = inventory(workspace)
                    assert before == after, "Read workflow changed repository bytes"
                    evidence["cases"].append({"id": expected_id, "context": context,
                        "detail": detail, "missing": missing, "unchanged": True,
                        "inventory": before})
            finally:
                process.stdin.close()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                reader.join(timeout=2)
                process.stdout.close()
                stderr.seek(0)
                evidence["stderr"] = stderr.read()
                evidence["exit_code"] = process.returncode
        assert process.returncode == 0, evidence
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as output:
        json.dump(evidence, output, indent=2, sort_keys=True)
        output.write("\n")
    print(json.dumps({"cases": len(evidence["cases"]), "unchanged": True,
                      "output": str(args.output), "model_calls": 0}))


if __name__ == "__main__":
    main()
