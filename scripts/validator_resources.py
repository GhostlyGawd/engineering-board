#!/usr/bin/env python3
"""Run one validator command under global and exclusive repository locks."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time
from typing import Any


MAX_SESSIONS = 2
EXCLUSIVE_RESOURCES = {"aggregate", "browser", "otlp", "port-4173", "port-4318"}
PORT_RESOURCES = {"port-4173": 4173, "port-4318": 4318}


class ResourceError(RuntimeError):
    """A validator resource cannot be acquired safely."""


def _owner_record(label: str, token: str) -> dict[str, Any]:
    return {
        "schema_version": "1",
        "label": label,
        "pid": os.getpid(),
        "token": token,
        "started_unix_ns": time.time_ns(),
    }


def _write_owner(directory: Path, owner: dict[str, Any]) -> None:
    path = directory / "owner.json"
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        json.dump(owner, stream, sort_keys=True)
        stream.write("\n")


def _read_owner(directory: Path) -> dict[str, Any] | None:
    try:
        value = json.loads((directory / "owner.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return value if isinstance(value, dict) else None


def _windows_pid_is_alive(pid: int) -> bool:
    import ctypes
    from ctypes import wintypes

    process_query_limited_information = 0x1000
    still_active = 259
    win_dll = getattr(ctypes, "WinDLL")
    get_last_error = getattr(ctypes, "get_last_error")
    kernel32 = win_dll("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [
        wintypes.DWORD,
        wintypes.BOOL,
        wintypes.DWORD,
    ]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.GetExitCodeProcess.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.GetExitCodeProcess.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    handle = kernel32.OpenProcess(process_query_limited_information, False, pid)
    if not handle:
        return int(get_last_error()) != 87
    try:
        exit_code = wintypes.DWORD()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return True
        return bool(exit_code.value == still_active)
    finally:
        kernel32.CloseHandle(handle)


def _pid_is_alive(pid: object) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name == "nt":
        return _windows_pid_is_alive(pid)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _remove_owned_lock(directory: Path, token: str) -> None:
    owner = _read_owner(directory)
    if owner is None or owner.get("token") != token:
        return
    try:
        (directory / "owner.json").unlink()
        directory.rmdir()
    except FileNotFoundError:
        return
    for parent in (directory.parent, directory.parent.parent):
        try:
            parent.rmdir()
        except OSError:
            break


def _reclaim_stale_lock(directory: Path) -> bool:
    owner = _read_owner(directory)
    if owner is None or _pid_is_alive(owner.get("pid")):
        return False
    try:
        (directory / "owner.json").unlink(missing_ok=True)
        directory.rmdir()
    except OSError:
        return False
    return True


def _acquire_directory(directory: Path, owner: dict[str, Any]) -> bool:
    directory.parent.mkdir(parents=True, exist_ok=True)
    for _attempt in range(2):
        try:
            directory.mkdir()
        except FileExistsError:
            if _reclaim_stale_lock(directory):
                continue
            return False
        try:
            _write_owner(directory, owner)
        except BaseException:
            try:
                directory.rmdir()
            except OSError:
                pass
            raise
        return True
    return False


def _port_is_available(port: int) -> bool:
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        probe.bind(("127.0.0.1", port))
    except OSError:
        return False
    finally:
        probe.close()
    return True


def run_locked(
    state_root: Path,
    label: str,
    command: list[str],
    exclusive: str | None,
) -> int:
    if not command:
        raise ResourceError("validator command is empty")
    if exclusive is not None and exclusive not in EXCLUSIVE_RESOURCES:
        raise ResourceError(f"unknown exclusive resource: {exclusive}")

    token = secrets.token_hex(16)
    owner = _owner_record(label, token)
    session_lock: Path | None = None
    exclusive_lock: Path | None = None
    for slot in range(1, MAX_SESSIONS + 1):
        candidate = state_root / "sessions" / f"slot-{slot}"
        if _acquire_directory(candidate, owner):
            session_lock = candidate
            break
    if session_lock is None:
        raise ResourceError(f"global validator capacity is occupied ({MAX_SESSIONS} sessions)")

    try:
        if exclusive is not None:
            exclusive_lock = state_root / "exclusive" / exclusive
            if not _acquire_directory(exclusive_lock, owner):
                occupant = _read_owner(exclusive_lock) or {}
                occupied_label = occupant.get("label", "unknown")
                raise ResourceError(
                    f"exclusive resource is occupied: {exclusive} (owner label: {occupied_label})"
                )
            port = PORT_RESOURCES.get(exclusive)
            if port is not None and not _port_is_available(port):
                raise ResourceError(f"127.0.0.1:{port} is occupied; no fallback port is allowed")

        environment = os.environ.copy()
        environment["ENGINEERING_BOARD_VALIDATOR_SESSION"] = token
        return subprocess.run(command, env=environment, check=False).returncode
    finally:
        if exclusive_lock is not None:
            _remove_owned_lock(exclusive_lock, token)
        _remove_owned_lock(session_lock, token)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--state-root",
        type=Path,
        default=Path(
            os.environ.get(
                "ENGINEERING_BOARD_VALIDATOR_STATE",
                Path(__file__).resolve().parents[1] / ".engineering-board" / "validator-locks",
            )
        ),
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    run_parser = subparsers.add_parser("run", help="run one locked command")
    run_parser.add_argument("--label", required=True)
    run_parser.add_argument("--exclusive", choices=sorted(EXCLUSIVE_RESOURCES))
    run_parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    try:
        return run_locked(args.state_root.resolve(), args.label, command, args.exclusive)
    except ResourceError as exc:
        print(f"validator-resources: {exc}", file=sys.stderr)
        return 75


if __name__ == "__main__":
    raise SystemExit(main())
