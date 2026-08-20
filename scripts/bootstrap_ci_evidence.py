#!/usr/bin/env python3
# ruff: noqa: UP006, UP035
"""Exercise native-Windows bootstrap contracts and retain exact-head evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]


def _git_at(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return f"<git-exit-{result.returncode}>"
    return result.stdout.strip()


def _git(*arguments: str) -> str:
    return _git_at(ROOT, *arguments)


def _clone_checkout(
    destination: Path,
    source_commit: str,
) -> subprocess.CompletedProcess[str]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    clone = subprocess.run(
        [
            "git",
            "clone",
            "--no-checkout",
            "--no-local",
            str(ROOT),
            str(destination),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if clone.returncode != 0:
        return clone
    checkout = subprocess.run(
        [
            "git",
            "-C",
            str(destination),
            "checkout",
            "--detach",
            source_commit,
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if checkout.returncode != 0:
        return checkout
    return subprocess.CompletedProcess(
        clone.args,
        0,
        clone.stdout + checkout.stdout,
        clone.stderr + checkout.stderr,
    )


def _tree_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    if not root.exists():
        return digest.hexdigest()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _inventory_digest(inventory: Dict[str, str]) -> str:
    encoded = json.dumps(
        inventory,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _run(
    arguments: List[str],
    *,
    cwd: Path,
    environment: Dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=cwd,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def _stage(
    name: str,
    result: subprocess.CompletedProcess[str],
    *,
    parse_inventory: bool = False,
) -> Dict[str, Any]:
    value: Dict[str, Any] = {
        "name": name,
        "exit_code": result.returncode,
    }
    if parse_inventory and result.returncode == 0:
        try:
            inventory = json.loads(result.stdout)
        except json.JSONDecodeError:
            value["inventory_error"] = "stdout was not JSON"
        else:
            value["inventory"] = inventory
            value["inventory_sha256"] = _inventory_digest(inventory)
    if result.returncode != 0:
        value["stderr"] = result.stderr.strip()[-4000:]
    return value


def _atomic_json(path: Path, value: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shell", choices=("cmd", "powershell"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    install_root = (
        ROOT / ".engineering-board" / "validation" / "bootstrap" / f"{args.shell} tool root"
    )
    missing_root = install_root.with_name(f"{args.shell} missing root")
    checkout_root = install_root.with_name(f"{args.shell} checkout with spaces")
    bootstrap = str(ROOT / "scripts" / "bootstrap_dev.py")
    base_command = [
        sys.executable,
        bootstrap,
        "--install-root",
        str(install_root),
    ]
    base_environment = os.environ.copy()
    stages: List[Dict[str, Any]] = []
    status_before = _git("status", "--porcelain=v1", "--untracked-files=all")
    source_commit = _git("rev-parse", "HEAD")

    install = _run(base_command, cwd=ROOT.parent, environment=base_environment)
    stages.append(_stage("clean-install", install, parse_inventory=True))
    fingerprint_after_install = _tree_fingerprint(install_root)

    offline_environment = base_environment.copy()
    offline_environment.update(
        {
            "UV_OFFLINE": "1",
            "npm_config_offline": "true",
            "HTTP_PROXY": "http://127.0.0.1:9",
            "HTTPS_PROXY": "http://127.0.0.1:9",
            "ALL_PROXY": "http://127.0.0.1:9",
        }
    )
    offline = _run(
        [*base_command, "--check"],
        cwd=ROOT.parent,
        environment=offline_environment,
    )
    stages.append(_stage("offline-read-only-check", offline, parse_inventory=True))
    fingerprint_after_check = _tree_fingerprint(install_root)

    shutil.rmtree(checkout_root, ignore_errors=True)
    clone = _clone_checkout(checkout_root, source_commit)
    checkout_status_before = ""
    checkout_status_after = ""
    if clone.returncode == 0:
        checkout_status_before = _git_at(
            checkout_root,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        )
        checkout_check = _run(
            [
                sys.executable,
                str(checkout_root / "scripts" / "bootstrap_dev.py"),
                "--check",
                "--install-root",
                str(install_root),
            ],
            cwd=checkout_root.parent,
            environment=offline_environment,
        )
        checkout_status_after = _git_at(
            checkout_root,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        )
    else:
        checkout_check = clone
    stages.append(
        _stage(
            "spaced-checkout-offline-check",
            checkout_check,
            parse_inventory=True,
        )
    )
    checkout_clean = checkout_status_before == checkout_status_after == ""
    shutil.rmtree(checkout_root, ignore_errors=True)

    second = _run(base_command, cwd=ROOT.parent, environment=base_environment)
    stages.append(_stage("second-bootstrap", second, parse_inventory=True))
    fingerprint_after_second = _tree_fingerprint(install_root)

    missing = _run(
        [
            sys.executable,
            bootstrap,
            "--check",
            "--install-root",
            str(missing_root),
        ],
        cwd=ROOT.parent,
        environment=offline_environment,
    )
    stages.append(_stage("missing-installation", missing))

    unknown = _run(
        [sys.executable, bootstrap, "--not-a-bootstrap-option"],
        cwd=ROOT.parent,
        environment=base_environment,
    )
    stages.append(_stage("unknown-option", unknown))

    status_after = _git("status", "--porcelain=v1", "--untracked-files=all")
    inventories = [
        stage.get("inventory_sha256") for stage in stages[:4] if stage.get("exit_code") == 0
    ]
    expected_exit_codes = [0, 0, 0, 0, 2, 2]
    observed_exit_codes = [stage["exit_code"] for stage in stages]
    recovery = "python scripts/bootstrap_dev.py"
    diagnostics_ok = (
        recovery in str(stages[4].get("stderr", ""))
        and "--not-a-bootstrap-option" in str(stages[5].get("stderr", ""))
        and "usage:" in str(stages[5].get("stderr", "")).lower()
    )
    fingerprints_equal = (
        fingerprint_after_install == fingerprint_after_check == fingerprint_after_second
    )
    inventory_equal = len(inventories) == 4 and len(set(inventories)) == 1
    overall_pass = (
        platform.system() == "Windows"
        and observed_exit_codes == expected_exit_codes
        and diagnostics_ok
        and fingerprints_equal
        and inventory_equal
        and checkout_clean
        and status_before == status_after
        and not (missing_root / ".complete.json").exists()
    )
    evidence = {
        "schema_version": "1",
        "source_commit": source_commit,
        "repository_status_before": status_before,
        "repository_status_after": status_after,
        "support_row": os.environ.get("ENGINEERING_BOARD_SUPPORT_ROW", ""),
        "os_family": platform.system().lower(),
        "architecture": platform.machine().lower(),
        "native_shell": args.shell,
        "python_version": platform.python_version(),
        "recovery_command": recovery,
        "install_root_has_space": " " in str(install_root),
        "spaced_checkout": {
            "path_has_space": " " in str(checkout_root),
            "executed_from_outside_repository": True,
            "repository_status_before": checkout_status_before,
            "repository_status_after": checkout_status_after,
        },
        "install_tree_fingerprints": {
            "after_install": fingerprint_after_install,
            "after_offline_check": fingerprint_after_check,
            "after_second_bootstrap": fingerprint_after_second,
        },
        "stages": stages,
        "overall_pass": overall_pass,
        "completed_unix_ns": time.time_ns(),
    }
    _atomic_json(args.output, evidence)

    for stage in stages:
        print(f"{stage['name']}: exit {stage['exit_code']}")
    print(f"bootstrap evidence: {args.output}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
