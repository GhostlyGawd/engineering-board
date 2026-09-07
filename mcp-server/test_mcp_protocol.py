#!/usr/bin/env python3
"""Focused MCP lifecycle, launcher, root, and path-containment contracts."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
SERVER_PATH = HERE / "engineering_board_mcp.py"
PLUGIN_ROOT = HERE.parent
LAUNCHER_PATH = PLUGIN_ROOT / "scripts" / "engineering-board-mcp-launcher.mjs"
PUBLIC_TOOLS_FIXTURE = HERE / "fixtures" / "public-tools-v1.13.4.json"
MAX_MESSAGE_BYTES = 1024 * 1024

PASSED = []


class Failure(Exception):
    pass


def check(condition, label, detail=""):
    if not condition:
        raise Failure("%s%s" % (label, (" -- " + detail) if detail else ""))
    PASSED.append(label)
    print("  [PASS] %s" % label)


def load_server():
    spec = importlib.util.spec_from_file_location("eb_mcp_protocol", SERVER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tree_snapshot(root):
    base = Path(root)
    directories = []
    files = {}
    for path in sorted(base.rglob("*")):
        relative = path.relative_to(base).as_posix()
        if path.is_dir():
            directories.append(relative + "/")
        elif path.is_file():
            files[relative] = path.read_bytes()
    return tuple(directories), files


def terminate_host_process(process, native_windows=None):
    if native_windows is None:
        native_windows = os.name == "nt"
    if native_windows:
        process.terminate()
        return 1, "native Windows host termination"
    process.send_signal(signal.SIGINT)
    return 0, "SIGINT"


def suite_protocol_stream():
    print("\n== MCP protocol stream ==")
    repository = tempfile.mkdtemp(prefix="eb-mcp-protocol-")
    process = subprocess.Popen(
        [sys.executable, SERVER_PATH],
        cwd=repository,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=dict(os.environ, CLAUDE_PROJECT_DIR=repository),
    )
    assert process.stdin is not None
    assert process.stdout is not None
    assert process.stderr is not None

    def send(message):
        process.stdin.write(json.dumps(message) + "\n")
        process.stdin.flush()

    def receive():
        line = process.stdout.readline()
        if not line:
            raise Failure("server closed stdout: %r" % process.stderr.read())
        return json.loads(line)

    try:
        send({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
        check(
            receive().get("error", {}).get("code") == -32002,
            "pre-initialize request is rejected",
        )
        send({"jsonrpc": "2.0", "id": 2, "method": "ping", "params": {}})
        check(receive().get("result") == {}, "pre-initialize ping succeeds")
        send(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "initialize",
                "params": {
                    "protocolVersion": "1900-01-01",
                    "capabilities": {},
                    "clientInfo": {"name": "negative", "version": "1"},
                },
            }
        )
        check(
            receive().get("error", {}).get("code") == -32602,
            "unsupported protocol version is rejected",
        )
        send(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "protocol-test", "version": "1"},
                },
            }
        )
        initialized = receive()
        result = initialized.get("result", {})
        check(result.get("protocolVersion") == "2025-06-18", "protocol version is negotiated")
        check(
            result.get("serverInfo", {}).get("name") == "engineering-board",
            "server name is authoritative",
        )
        check(
            result.get("capabilities", {}).get("tools", {}).get("listChanged") is False,
            "tools.listChanged is false",
        )
        send(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "duplicate", "version": "1"},
                },
            }
        )
        check(
            receive().get("error", {}).get("code") == -32600,
            "duplicate initialize is rejected",
        )
        send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        send({"jsonrpc": "2.0", "id": 6, "method": "tools/list", "params": {}})
        tools = receive().get("result", {}).get("tools")
        fixture = json.loads(PUBLIC_TOOLS_FIXTURE.read_text(encoding="utf-8"))
        check(tools == fixture, "tools/list matches the previous-release fixture")
        send({"jsonrpc": "2.0", "id": 7, "method": "tools/list", "params": {}})
        check(
            receive().get("result", {}).get("tools") == fixture,
            "repeated tools/list is byte-normalized stable",
        )

        malformed = [
            ('{"jsonrpc":"2.0","id":8,"method":', -32700, "malformed JSON"),
            (
                json.dumps({"jsonrpc": "1.0", "id": 9, "method": "ping"}),
                -32600,
                "wrong JSON-RPC version",
            ),
            (
                json.dumps({"jsonrpc": "2.0", "id": [], "method": "ping"}),
                -32600,
                "invalid request id",
            ),
            (
                json.dumps({"jsonrpc": "2.0", "id": 11, "method": 7}),
                -32600,
                "non-string method",
            ),
            (
                json.dumps({"jsonrpc": "2.0", "id": 12, "method": "ping", "params": "bad"}),
                -32602,
                "non-object params",
            ),
        ]
        next_id = 20
        for raw, expected, label in malformed:
            process.stdin.write(raw + "\n")
            process.stdin.flush()
            check(
                receive().get("error", {}).get("code") == expected,
                "%s returns the protocol error" % label,
            )
            send({"jsonrpc": "2.0", "id": next_id, "method": "ping", "params": {}})
            check(
                receive().get("id") == next_id,
                "%s preserves synchronization" % label,
            )
            next_id += 1

        send(
            {
                "jsonrpc": "2.0",
                "id": 30,
                "method": "tools/call",
                "params": {
                    "name": "board_context",
                    "arguments": {"project": "missing", "limit": "many"},
                },
            }
        )
        check(
            receive().get("error", {}).get("code") == -32602,
            "invalid tool arguments return invalid params",
        )
        send({"jsonrpc": "2.0", "id": 31, "method": "does/not/exist", "params": {}})
        check(
            receive().get("error", {}).get("code") == -32601,
            "unknown method returns method not found",
        )
        send(
            {
                "jsonrpc": "2.0",
                "id": 32,
                "method": "tools/call",
                "params": {"name": "nope", "arguments": {}},
            }
        )
        check(
            receive().get("error", {}).get("code") == -32602,
            "unknown tool returns invalid params",
        )
        process.stdin.write("x" * (MAX_MESSAGE_BYTES + 1) + "\n")
        process.stdin.flush()
        check(
            receive().get("error", {}).get("code") == -32001,
            "oversized input is rejected",
        )
        send({"jsonrpc": "2.0", "id": 33, "method": "ping", "params": {}})
        check(receive().get("result") == {}, "oversized input preserves synchronization")
        send({"jsonrpc": "2.0", "method": "notifications/unexpected", "params": {}})
        send({"jsonrpc": "2.0", "id": 34, "method": "ping", "params": {}})
        check(
            receive().get("id") == 34,
            "unexpected notification emits no stray response",
        )
    finally:
        process.stdin.close()
        process.wait(timeout=5)
        shutil.rmtree(repository, ignore_errors=True)


def suite_termination_and_launcher():
    print("\n== MCP termination and launcher ==")

    class NativeWindowsProcess:
        def send_signal(self, requested_signal):
            raise ValueError("Unsupported signal: %s" % requested_signal)

        def terminate(self):
            self.terminated = True

    native_windows_process = NativeWindowsProcess()
    terminate_host_process(native_windows_process, native_windows=True)
    if not getattr(native_windows_process, "terminated", False):
        raise Failure("native Windows did not use supported host termination")

    truncated = subprocess.Popen(
        [sys.executable, SERVER_PATH],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    stdout, stderr = truncated.communicate('{"jsonrpc":"2.0","id":1,"method":')
    lines = [line for line in stdout.splitlines() if line.strip()]
    check(truncated.returncode == 0, "truncated EOF terminates cleanly", stderr)
    check(
        len(lines) == 1 and json.loads(lines[0]).get("error", {}).get("code") == -32700,
        "truncated EOF emits one parse error",
        repr(lines),
    )

    interrupted = subprocess.Popen(
        [sys.executable, SERVER_PATH],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    assert interrupted.stdin is not None
    assert interrupted.stdout is not None
    interrupted.stdin.write(
        '{"jsonrpc":"2.0","id":1,"method":"initialize","params":'
        '{"protocolVersion":"2025-06-18","capabilities":{}}}\n'
    )
    interrupted.stdin.flush()
    json.loads(interrupted.stdout.readline())
    expected_returncode, termination = terminate_host_process(interrupted)
    stdout, stderr = interrupted.communicate(timeout=5)
    check(
        interrupted.returncode == expected_returncode,
        "source server exits cleanly on %s" % termination,
        stderr,
    )
    check(
        stdout == "",
        "source %s emits no stdout" % termination,
        repr(stdout),
    )

    invalid = subprocess.run(
        ["node", LAUNCHER_PATH],
        input="",
        capture_output=True,
        text=True,
        env=dict(os.environ, PYTHON="/definitely/missing/engineering-board-python"),
        timeout=10,
    )
    check(invalid.returncode != 0, "invalid Python override fails")
    check(invalid.stdout == "", "invalid Python override emits no stdout", invalid.stdout)
    check(
        "PYTHON override is unavailable" in invalid.stderr,
        "invalid Python override stays on bounded stderr",
        invalid.stderr,
    )


def suite_root_and_paths(module):
    print("\n== MCP root and path containment ==")
    base = Path(tempfile.mkdtemp(prefix="eb-mcp-paths-"))
    explicit = base / "explicit"
    environment = base / "environment"
    current = base / "current"
    outside = base / "outside"
    for path in (explicit, environment, current, outside):
        path.mkdir()
    prior_env = os.environ.get("CLAUDE_PROJECT_DIR")
    prior_cwd = os.getcwd()
    try:
        os.environ["CLAUDE_PROJECT_DIR"] = str(environment)
        os.chdir(current)
        check(
            module.resolve_root({"root": str(explicit)}) == str(explicit.resolve()),
            "explicit root wins precedence",
        )
        check(
            module.resolve_root({}) == str(environment.resolve()),
            "CLAUDE_PROJECT_DIR wins over cwd",
        )
        del os.environ["CLAUDE_PROJECT_DIR"]
        check(module.resolve_root({}) == str(current.resolve()), "cwd remains standalone fallback")

        os.environ["ENGINEERING_BOARD_REQUIRE_ROOT"] = "1"
        for value in (None, "relative", str(base / "missing")):
            arguments = {} if value is None else {"root": value}
            try:
                module.resolve_root(arguments)
                raise Failure("bundled root accepted %r" % value)
            except module.ToolError:
                pass
        check(True, "bundled calls require an existing absolute root")
        os.environ.pop("ENGINEERING_BOARD_REQUIRE_ROOT", None)

        module.tool_board_init({"project": "ctx", "root": str(explicit), "agents_md": False})
        context = {
            "project": "ctx",
            "root": str(explicit),
            "task": "Inspect contained context paths",
        }
        check(
            module.tool_board_context(dict(context, cwd="."))
            == module.tool_board_context(dict(context, cwd=str(explicit))),
            "board_context cwd dot equals the selected root",
        )
        link = explicit / "linked"
        link.symlink_to(outside, target_is_directory=True)
        baseline = tree_snapshot(base)
        for rejected in [
            {"files": ["../outside/file.py"]},
            {"files": [str(outside / "file.py")]},
            {"files": ["linked/file.py"]},
            {"cwd": "../outside"},
            {"cwd": str(outside)},
            {"cwd": "linked"},
        ]:
            try:
                module.tool_board_context(dict(context, **rejected))
                raise Failure("context accepted %r" % rejected)
            except (module.ToolError, module.CoreError):
                pass
        check(tree_snapshot(base) == baseline, "escaping context paths do not mutate")

        for affects in ("../outside/file.py", str(outside / "file.py"), "linked/file.py"):
            try:
                module.tool_board_create_entry(
                    {
                        "project": "ctx",
                        "root": str(explicit),
                        "type": "bug",
                        "title": "Reject escaping affects",
                        "priority": "P1",
                        "affects": affects,
                    }
                )
                raise Failure("affects accepted %r" % affects)
            except module.ToolError:
                pass
        check(tree_snapshot(base) == baseline, "escaping affects paths do not mutate")

        board = explicit / "engineering-board" / "ctx"
        mutations = [
            (
                "bugs",
                module.tool_board_create_entry,
                {
                    "project": "ctx",
                    "root": str(explicit),
                    "type": "bug",
                    "title": "Reject linked entries",
                    "priority": "P1",
                    "affects": "src/linked.py",
                },
            ),
            (
                "_sessions",
                module.tool_board_capture_finding,
                {
                    "project": "ctx",
                    "root": str(explicit),
                    "kind": "bug",
                    "title": "Reject linked scratch",
                },
            ),
            (
                "_claims",
                module.tool_board_claim,
                {
                    "project": "ctx",
                    "root": str(explicit),
                    "entry_id": "B001",
                    "session_id": "linked",
                },
            ),
        ]
        for subdir, tool, arguments in mutations:
            target = board / subdir
            if target.exists():
                shutil.rmtree(target)
            target.symlink_to(outside, target_is_directory=True)
            linked = tree_snapshot(base)
            try:
                tool(arguments)
                raise Failure("%s accepted a linked mutable directory" % subdir)
            except module.ToolError:
                pass
            check(
                tree_snapshot(base) == linked,
                "%s link escape fails before mutation" % subdir,
            )
            target.unlink()
            target.mkdir()

        router = explicit / "engineering-board" / "BOARD-ROUTER.md"
        router_bytes = router.read_bytes()
        outside_router = outside / "BOARD-ROUTER.md"
        outside_router.write_text(
            "| project | path | affects prefix |\n"
            "|---|---|---|\n"
            "| evil | ../outside | ../outside/ |\n",
            encoding="utf-8",
        )
        router.unlink()
        router.symlink_to(outside_router)
        linked = tree_snapshot(base)
        try:
            module.tool_board_list_projects({"root": str(explicit)})
            raise Failure("linked router was accepted")
        except module.ToolError:
            pass
        check(tree_snapshot(base) == linked, "linked router fails without mutation")
        router.unlink()
        router.write_bytes(router_bytes)
    finally:
        os.chdir(prior_cwd)
        if prior_env is None:
            os.environ.pop("CLAUDE_PROJECT_DIR", None)
        else:
            os.environ["CLAUDE_PROJECT_DIR"] = prior_env
        os.environ.pop("ENGINEERING_BOARD_REQUIRE_ROOT", None)
        shutil.rmtree(base, ignore_errors=True)


def main():
    try:
        suite_protocol_stream()
        suite_termination_and_launcher()
        suite_root_and_paths(load_server())
    except Failure as error:
        print("\n  [FAIL] %s" % error, file=sys.stderr)
        print(
            "\nRESULT: FAIL (%d checks passed before failure)" % len(PASSED),
            file=sys.stderr,
        )
        return 1
    print("\nRESULT: PASS (%d checks)" % len(PASSED))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
