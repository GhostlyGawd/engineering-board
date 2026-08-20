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


def _rpc_smoke(command: Sequence[str | Path], repository: Path, label: str) -> None:
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

    def receive(expected_id: int) -> dict[str, Any]:
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
        if "error" in value:
            raise PackageGateError(f"{label}: JSON-RPC error: {value['error']!r}")
        return value

    try:
        send(
            "initialize",
            {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "package-gate", "version": "1"},
            },
        )
        initialized = receive(1).get("result", {})
        require_equal(
            f"{label} protocol",
            initialized.get("protocolVersion"),
            MCP_PROTOCOL_VERSION,
        )
        stdin.write('{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}\n')
        stdin.flush()
        send("ping", {})
        require_equal(f"{label} ping", receive(2).get("result"), {})
        send("tools/list", {})
        tools = receive(3).get("result", {}).get("tools")
        if not isinstance(tools, list) or len(tools) != MCP_TOOL_COUNT:
            raise PackageGateError(f"{label}: expected {MCP_TOOL_COUNT} tools")
        send(
            "tools/call",
            {
                "name": "board_list_projects",
                "arguments": {"root": str(repository)},
            },
        )
        tool_result = receive(4).get("result")
        if not isinstance(tool_result, dict) or tool_result.get("isError") is True:
            raise PackageGateError(f"{label}: representative tool call failed")
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
    _rpc_smoke([console], repository, f"Python {runtime} {kind}")


def mcpb_smoke(
    *,
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
    _rpc_smoke(
        [interpreter, extracted / "mcp-server" / "engineering_board_mcp.py"],
        repository,
        f"Python {runtime} mcpb",
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
