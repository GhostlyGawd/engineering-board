#!/usr/bin/env python3
"""Run the legacy suite manifest with portable failure control."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
from typing import Any

from application_contract import ApplicationContractError, shared_contract_fingerprint
from validator_resources import ResourceError, run_locked


ROOT = Path(__file__).resolve().parents[1]
VOLATILE_KEYS = {
    "completed_unix_ns",
    "duration_ns",
    "started_unix_ns",
    "timestamp",
}


def _configure_console_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        getattr(stream, "reconfigure")(encoding="utf-8", errors="strict")


def _native_shell() -> str:
    native_shell = os.environ.get("ENGINEERING_BOARD_NATIVE_SHELL")
    if native_shell is not None:
        return native_shell
    support_row = os.environ.get("ENGINEERING_BOARD_SUPPORT_ROW", "")
    if support_row.endswith("-powershell"):
        return "powershell"
    if support_row.endswith("-cmd"):
        return "cmd"
    return "cmd" if os.name == "nt" else "bash"


def _git_status(root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _normalized(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _normalized(child)
            for key, child in sorted(value.items())
            if key not in VOLATILE_KEYS and not key.endswith("_duration_ns")
        }
    if isinstance(value, list):
        return [_normalized(child) for child in value]
    return value


def _validation_fingerprint(root: Path) -> str:
    validation = root / ".engineering-board" / "validation"
    digest = hashlib.sha256()
    if not validation.exists():
        return digest.hexdigest()
    package_root = validation / "package"
    for path in sorted(package_root.glob("*")):
        if path.is_file() and path.name != "report.json":
            digest.update(path.name.encode("utf-8"))
            digest.update(path.read_bytes())
    for relative in ("coverage/summary.json", "package/report.json", "platform/bash.json"):
        path = validation / relative
        if not path.is_file():
            continue
        value = json.loads(path.read_text(encoding="utf-8"))
        if relative == "coverage/summary.json":
            value = {
                "applications": [
                    {"id": item["id"], "passed": item["passed"]} for item in value["applications"]
                ],
                "base": value["base"],
                "changed_lines": value["changed_lines"],
                "head": value["head"],
                "identity": value["identity"],
                "passed": value["passed"],
                "schema_version": value["schema_version"],
            }
        digest.update(relative.encode("utf-8"))
        digest.update(
            json.dumps(
                _normalized(value),
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
    return digest.hexdigest()


def _atomic_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=path.parent,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def _command(raw: list[str], root: Path) -> list[str]:
    return [
        sys.executable if value == "{python}" else str(root) if value == "{root}" else value
        for value in raw
    ]


def _execute_suite(root: Path, suite: dict[str, Any]) -> dict[str, object]:
    suite_id = str(suite["id"])
    command = _command(list(suite["command"]), root)
    print("\n================================================================")
    print(f"RUN: {suite_id}")
    print("================================================================")
    started = time.monotonic_ns()
    completed = subprocess.run(
        command,
        cwd=root,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    duration_ns = time.monotonic_ns() - started
    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if completed.stderr:
        print(
            completed.stderr,
            end="" if completed.stderr.endswith("\n") else "\n",
            file=sys.stderr,
        )
    status = "passed" if completed.returncode == 0 else "failed"
    print(f"[{'PASS' if status == 'passed' else 'FAIL'}] {suite_id}")
    return {
        "id": suite_id,
        "status": status,
        "exit_code": completed.returncode,
        "duration_ns": duration_ns,
        "rerun_command": " ".join(command),
    }


def _contract_fingerprint(root: Path, manifest: dict[str, Any]) -> str:
    try:
        return shared_contract_fingerprint(root)
    except (ApplicationContractError, OSError):
        value = {
            "applications": [],
            "portable_shared_suites": [
                suite["id"] for suite in manifest["suites"] if suite.get("portable") is True
            ],
        }
        return hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()


def _run(root: Path, manifest_path: Path, portable_only: bool, report_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "1":
        print("legacy-run-all: unsupported suite manifest schema", file=sys.stderr)
        return 2
    status_before = _git_status(root)
    results: list[dict[str, object]] = []
    passed = failed = skipped = 0
    for suite in manifest["suites"]:
        suite_id = str(suite["id"])
        if portable_only and not suite.get("portable"):
            reason = str(suite.get("skip_reason", "not-portable"))
            print(f"[SKIP] {suite_id}: {reason}")
            results.append(
                {
                    "id": suite_id,
                    "status": "skipped",
                    "exit_code": None,
                    "skip_reason": reason,
                }
            )
            skipped += 1
            continue
        suite_result = _execute_suite(root, suite)
        passed += suite_result["status"] == "passed"
        failed += suite_result["status"] == "failed"
        results.append(suite_result)

    decisions = [
        {
            "id": suite_result["id"],
            "status": suite_result["status"],
            "exit_code": suite_result["exit_code"],
            "skip_reason": suite_result.get("skip_reason"),
        }
        for suite_result in results
    ]
    decision_fingerprint = hashlib.sha256(
        json.dumps(decisions, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    contract_fingerprint = _contract_fingerprint(root, manifest)
    status_after = _git_status(root)
    report = {
        "schema_version": "1",
        "source_commit": _git_head(root),
        "support_row": os.environ.get("ENGINEERING_BOARD_SUPPORT_ROW", "local"),
        "os_family": platform.system().lower(),
        "architecture": platform.machine().lower(),
        "native_shell": _native_shell(),
        "command": (
            f"{sys.executable} scripts/legacy_run_all.py --root {root}"
            + (" --portable-only" if portable_only else "")
        ),
        "repository_root": str(root),
        "repository_status_before": status_before,
        "repository_status_after": status_after,
        "repository_clean": status_before == status_after,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "suite_count": len(results),
        "results": results,
        "normalized_decision_fingerprint": decision_fingerprint,
        "shared_contract_fingerprint": contract_fingerprint,
        "artifact_fingerprint": _validation_fingerprint(root),
        "overall_pass": failed == 0 and status_before == status_after,
    }
    _atomic_json(report_path, report)
    print(
        f"\nRUN-ALL SUMMARY: {passed} pass, {failed} fail, "
        f"{skipped} skip (of {len(results)} suites)"
    )
    if failed:
        print("FAILED SUITES:")
        for suite_result in results:
            if suite_result["status"] == "failed":
                print(f"  - {suite_result['id']}")
                print(f"    rerun: {suite_result['rerun_command']}")
    if status_before != status_after:
        print("legacy-run-all: checkout changed during validation", file=sys.stderr)
    return 0 if report["overall_pass"] else 1


def main(argv: list[str] | None = None) -> int:
    _configure_console_utf8()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--portable-only", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--state-root", type=Path)
    args = parser.parse_args(argv)
    root = args.root.expanduser().resolve()
    manifest = (args.manifest or root / "support" / "legacy-suites.json").resolve()
    report = (
        args.report
        or root / ".engineering-board" / "validation" / "aggregate" / "legacy-run-all.json"
    ).resolve()
    if os.environ.get("ENGINEERING_BOARD_VALIDATOR_SESSION"):
        return _run(root, manifest, args.portable_only, report)
    state_root = (args.state_root or root / ".engineering-board" / "validator-locks").resolve()
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--root",
        str(root),
        "--manifest",
        str(manifest),
        "--report",
        str(report),
        "--state-root",
        str(state_root),
    ]
    if args.portable_only:
        command.append("--portable-only")
    try:
        return run_locked(
            state_root,
            "legacy-run-all",
            command,
            "aggregate",
        )
    except ResourceError as exc:
        print(f"legacy-run-all: {exc}", file=sys.stderr)
        return 75


if __name__ == "__main__":
    raise SystemExit(main())
