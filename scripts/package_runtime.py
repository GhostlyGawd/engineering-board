"""Isolated runtime and MCP stdio validation for built distributions."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
from typing import Any, Sequence
import zipfile

from package_contract import (
    PACKAGE_NAME,
    PackageGateError,
    project_string,
    require_equal,
)


MCP_PROTOCOL_VERSION = "2025-06-18"
MCP_TOOL_COUNT = 19
MCP_MAX_MESSAGE_BYTES = 1024 * 1024
GRAPH_PACKAGE_MARKER = "Graph café ↳ package smoke".encode("utf-8")


def run_command(
    command: Sequence[str | Path],
    *,
    cwd: Path,
    environment: dict[str, str],
    label: str,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [str(value) for value in command],
        cwd=cwd,
        env=environment,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        diagnostic = (result.stdout + result.stderr).strip()
        raise PackageGateError(f"{label} failed with exit {result.returncode}: {diagnostic}")
    return result


def _venv_python(venv: Path) -> Path:
    if os.name == "nt":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def _venv_console(venv: Path) -> Path:
    suffix = ".exe" if os.name == "nt" else ""
    directory = "Scripts" if os.name == "nt" else "bin"
    return venv / directory / f"engineering-board-mcp{suffix}"


def _graph_output_issues(path: Path, name: str) -> list[str]:
    issues: list[str] = []
    if not path.is_file():
        issues.append(f"{name} ({path}): missing output")
    else:
        content = path.read_bytes()
        try:
            content.decode("utf-8")
        except UnicodeDecodeError:
            issues.append(f"{name} ({path}): invalid UTF-8")
        if GRAPH_PACKAGE_MARKER not in content:
            issues.append(f"{name} ({path}): marker missing")
        carriage_returns = content.count(b"\r")
        if carriage_returns:
            issues.append(f"{name} ({path}): CR count {carriage_returns}, expected 0")
        terminal_lfs = len(content) - len(content.rstrip(b"\n"))
        if terminal_lfs != 1:
            issues.append(f"{name} ({path}): terminal LF count {terminal_lfs}, expected 1")

    temporary_siblings = sorted(path.parent.glob(path.name + ".tmp*"))
    if temporary_siblings:
        issues.append(
            f"{name} ({path}): temporary sibling residue: "
            + ", ".join(str(sibling) for sibling in temporary_siblings)
        )
    return issues


def _validate_graph_outputs(repository: Path, project: str, label: str) -> None:
    graph_path = repository / "engineering-board" / project / "GRAPH.yml"
    cache_path = repository / ".engineering-board" / "cache" / "graph" / project / "state.json"
    issues = [
        *_graph_output_issues(graph_path, "GRAPH.yml"),
        *_graph_output_issues(cache_path, "cache state.json"),
    ]
    if issues:
        raise PackageGateError(f"{label}: graph output contract failed:\n- " + "\n- ".join(issues))


def _rpc_smoke(
    command: Sequence[str | Path],
    repository: Path,
    label: str,
    expected_tools: list[dict[str, Any]],
) -> None:
    process = subprocess.Popen(
        [str(value) for value in command],
        cwd=repository,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if process.stdin is None or process.stdout is None or process.stderr is None:
        process.kill()
        raise PackageGateError(f"{label}: stdio pipes are unavailable")
    stdin = process.stdin
    stdout = process.stdout
    stderr_stream = process.stderr
    request_id = 0

    def send(method: str, params: dict[str, Any] | None = None) -> None:
        nonlocal request_id
        request_id += 1
        message: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
        }
        if params is not None:
            message["params"] = params
        stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
        stdin.flush()

    def receive(expected_id: int | str | None) -> dict[str, Any]:
        line = stdout.readline()
        if not line:
            diagnostic = stderr_stream.read()
            raise PackageGateError(
                f"{label}: server closed before response {expected_id}: {diagnostic}"
            )
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise PackageGateError(f"{label}: stdout is not JSON-RPC: {line!r}") from exc
        if not isinstance(value, dict):
            raise PackageGateError(f"{label}: response is not an object: {value!r}")
        if value.get("id") != expected_id:
            raise PackageGateError(f"{label}: response id mismatch: {value!r}")
        return value

    def receive_success(expected_id: int | str) -> dict[str, Any]:
        value = receive(expected_id)
        if "error" in value:
            raise PackageGateError(f"{label}: JSON-RPC error: {value['error']!r}")
        return value

    def receive_error(expected_id: int | str | None, expected_code: int) -> dict[str, Any]:
        value = receive(expected_id)
        error = value.get("error")
        if not isinstance(error, dict) or error.get("code") != expected_code:
            raise PackageGateError(f"{label}: expected error {expected_code}, received {value!r}")
        return value

    try:
        send("tools/list", {})
        receive_error(1, -32002)
        send("ping", {})
        require_equal(f"{label} pre-initialize ping", receive_success(2).get("result"), {})
        send(
            "initialize",
            {
                "protocolVersion": "1900-01-01",
                "capabilities": {},
                "clientInfo": {"name": "package-gate-negative", "version": "1"},
            },
        )
        receive_error(3, -32602)
        send(
            "initialize",
            {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "package-gate", "version": "1"},
            },
        )
        initialized = receive_success(4).get("result", {})
        require_equal(
            f"{label} protocol",
            initialized.get("protocolVersion"),
            MCP_PROTOCOL_VERSION,
        )
        stdin.write('{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}\n')
        stdin.flush()
        send("ping", {})
        require_equal(f"{label} ping", receive_success(5).get("result"), {})
        send("tools/list", {})
        tools = receive_success(6).get("result", {}).get("tools")
        if tools != expected_tools:
            raise PackageGateError(f"{label}: public tools differ from the release fixture")
        if len(tools) != MCP_TOOL_COUNT:
            raise PackageGateError(f"{label}: expected {MCP_TOOL_COUNT} tools")

        stdin.write('{"jsonrpc":"2.0","id":7,"method":\n')
        stdin.flush()
        receive_error(None, -32700)
        send("ping", {})
        require_equal(f"{label} post-parse-error ping", receive_success(7).get("result"), {})
        send("does/not/exist", {})
        receive_error(8, -32601)
        send("tools/call", {"name": "nope", "arguments": {}})
        receive_error(9, -32602)
        stdin.write("x" * (MCP_MAX_MESSAGE_BYTES + 1) + "\n")
        stdin.flush()
        receive_error(None, -32001)
        send("ping", {})
        require_equal(f"{label} post-oversize ping", receive_success(10).get("result"), {})

        def call_tool(name: str, arguments: dict[str, Any]) -> None:
            send(
                "tools/call",
                {
                    "name": name,
                    "arguments": arguments,
                },
            )
            tool_result = receive_success(request_id).get("result")
            if not isinstance(tool_result, dict) or tool_result.get("isError") is True:
                raise PackageGateError(f"{label}: {name} failed")

        project = "package-smoke"
        call_tool(
            "board_init",
            {"root": str(repository), "project": project, "agents_md": False},
        )
        call_tool(
            "board_create_entry",
            {
                "root": str(repository),
                "project": project,
                "type": "bug",
                "title": "Graph café ↳ package smoke",
                "priority": "P2",
                "affects": "src/package_graph.py",
                "done_when": ["The packaged graph writer emits literal LF bytes."],
            },
        )
        call_tool(
            "board_graph",
            {"root": str(repository), "project": project, "full": True},
        )
        _validate_graph_outputs(repository, project, label)
        stdin.close()
        exit_code = process.wait(timeout=10)
        stdout_tail = stdout.read()
        stderr = stderr_stream.read()
        if exit_code != 0:
            raise PackageGateError(f"{label}: EOF termination exited {exit_code}: {stderr}")
        if stdout_tail.strip():
            raise PackageGateError(f"{label}: unexpected stdout after EOF: {stdout_tail!r}")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        stdin.close()
        stdout.close()
        stderr_stream.close()


def _installed_metadata(
    python: Path,
    root: Path,
    environment: dict[str, str],
) -> None:
    code = (
        "import importlib.metadata as m,sys;"
        f"d=m.distribution({PACKAGE_NAME!r});"
        f"assert d.version==sys.argv[1],(d.version,sys.argv[1]);"
        "assert not d.requires,d.requires;"
        "print(d.version)"
    )
    run_command(
        [
            python,
            "-c",
            code,
            project_string(root / "mcp-server" / "pyproject.toml", "version"),
        ],
        cwd=root,
        environment=environment,
        label="installed metadata validation",
    )


def find_python(
    uv: Path,
    requested: str,
    root: Path,
    environment: dict[str, str],
) -> Path:
    result = run_command(
        [uv, "python", "find", requested],
        cwd=root,
        environment=environment,
        label=f"Python {requested} discovery",
    )
    path = Path(result.stdout.strip())
    runtime_root = Path(environment["UV_PYTHON_INSTALL_DIR"]).resolve()
    try:
        contained = os.path.commonpath([str(runtime_root), str(path.resolve())]) == str(
            runtime_root
        )
    except ValueError:
        contained = False
    if not path.is_file() or not contained:
        raise PackageGateError(f"Python {requested} discovery returned no pinned interpreter")
    return path


def runtime_smoke(
    *,
    root: Path,
    uv: Path,
    runtime: str,
    interpreter: Path,
    artifact: Path,
    kind: str,
    destination: Path,
    environment: dict[str, str],
) -> None:
    venv = destination / f"python-{runtime}-{kind}"
    run_command(
        [
            uv,
            "venv",
            "--offline",
            "--no-python-downloads",
            "--no-project",
            "--python",
            interpreter,
            venv,
        ],
        cwd=root,
        environment=environment,
        label=f"{kind} virtual environment",
    )
    python = _venv_python(venv)
    run_command(
        [
            uv,
            "pip",
            "install",
            "--offline",
            "--no-cache",
            "--no-deps",
            "--python",
            python,
            artifact,
        ],
        cwd=root,
        environment=environment,
        label=f"{kind} isolated install",
    )
    console = _venv_console(venv)
    if not console.is_file():
        raise PackageGateError(f"{kind}: console script was not installed")
    _installed_metadata(python, root, environment)
    repository = destination / f"repo-python-{runtime}-{kind}"
    repository.mkdir()
    expected_tools = json.loads(
        (root / "mcp-server" / "fixtures" / "public-tools-v1.13.4.json").read_text(encoding="utf-8")
    )
    _rpc_smoke([console], repository, f"Python {runtime} {kind}", expected_tools)


def mcpb_smoke(
    *,
    root: Path,
    runtime: str,
    interpreter: Path,
    artifact: Path,
    destination: Path,
) -> None:
    extracted = destination / f"python-{runtime}-mcpb"
    with zipfile.ZipFile(artifact) as archive:
        archive.extractall(extracted)
    repository = destination / f"repo-python-{runtime}-mcpb"
    repository.mkdir()
    expected_tools = json.loads(
        (root / "mcp-server" / "fixtures" / "public-tools-v1.13.4.json").read_text(encoding="utf-8")
    )
    _rpc_smoke(
        [interpreter, extracted / "mcp-server" / "engineering_board_mcp.py"],
        repository,
        f"Python {runtime} mcpb",
        expected_tools,
    )


def tool_path(tool_root: Path, name: str) -> Path:
    if name == "uv":
        path = tool_root / "bin" / ("uv.exe" if os.name == "nt" else "uv")
    elif name == "python":
        path = (
            tool_root / "python-tools" / "Scripts" / "python.exe"
            if os.name == "nt"
            else tool_root / "python-tools" / "bin" / "python"
        )
    else:
        raise PackageGateError(f"unknown package tool: {name}")
    if not path.is_file():
        raise PackageGateError(
            f"missing pinned package tool {name} at {path}; run the documented bootstrap"
        )
    return path
