#!/usr/bin/env python3
"""Run platform-neutral repository tests with bounded validator resources."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

from platform_contract import validate_repository_contract
from validator_resources import ResourceError, run_locked


ROOT = Path(__file__).resolve().parents[1]


def _source_commit() -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _write_result(shell_name: str, workers: int, stages: list[dict[str, object]]) -> None:
    result_path = (
        ROOT
        / ".engineering-board"
        / "validation"
        / "platform"
        / f"{shell_name}.json"
    )
    result_path.parent.mkdir(parents=True, exist_ok=True)
    family = platform.system().lower()
    machine = platform.machine().lower()
    architecture = "x86_64" if machine in {"amd64", "x86_64"} else machine
    value = {
        "schema_version": "1",
        "source_commit": _source_commit(),
        "os_family": family,
        "architecture": architecture,
        "native_shell": shell_name,
        "python_version": platform.python_version(),
        "workers_requested": workers,
        "workers_observed_maximum": 1,
        "stages": stages,
        "overall_pass": all(stage["exit_code"] == 0 for stage in stages),
        "skip_inventory": (
            []
            if os.name == "nt"
            else [
                {
                    "case": "native-windows-junction",
                    "reason": "host-application-unavailable",
                }
            ]
        ),
        "completed_unix_ns": time.time_ns(),
    }
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{result_path.name}.",
        dir=result_path.parent,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, result_path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _run_tests(shell_name: str, workers: int) -> int:
    environment = os.environ.copy()
    environment["ENGINEERING_BOARD_NATIVE_SHELL"] = shell_name
    stages = [
        (
            "platform-contract",
            [sys.executable, str(ROOT / "scripts" / "platform_contract.py")],
        ),
        (
            "platform-portability",
            [
                sys.executable,
                str(ROOT / "tests" / "platform" / "test_foundation_portability.py"),
            ],
        ),
        (
            "evaluation-harness",
            [sys.executable, str(ROOT / "tests" / "evaluation" / "test_harness.py")],
        ),
    ]
    results: list[dict[str, object]] = []
    for name, command in stages:
        result = subprocess.run(command, cwd=ROOT, env=environment, check=False)
        results.append({"name": name, "exit_code": result.returncode})
        if result.returncode != 0:
            _write_result(shell_name, workers, results)
            return result.returncode
    _write_result(shell_name, workers, results)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--shell", choices=("bash", "cmd", "powershell"), required=True)
    parser.add_argument("--state-root", type=Path)
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 2:
        parser.error("--workers must be 1 or 2")
    if os.name == "nt" and args.shell == "bash":
        parser.error("native Windows evidence must use cmd or powershell")

    state_root = args.state_root or (
        ROOT / ".engineering-board" / "validator-locks"
    )
    if os.environ.get("ENGINEERING_BOARD_VALIDATOR_SESSION"):
        return _run_tests(args.shell, args.workers)
    try:
        return run_locked(
            state_root.resolve(),
            f"platform-{args.shell}",
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--workers",
                str(args.workers),
                "--shell",
                args.shell,
                "--state-root",
                str(state_root),
            ],
            None,
        )
    except ResourceError as exc:
        print(f"platform-test: {exc}", file=sys.stderr)
        return 75


if __name__ == "__main__":
    raise SystemExit(main())
