#!/usr/bin/env python3
# ruff: noqa: UP006, UP035
"""Run the compatibility aggregate and retain an exact-head result manifest."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]


def _git(*arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *arguments],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return f"<git-exit-{result.returncode}>"
    return result.stdout.strip()


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
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    status_before = _git("status", "--porcelain=v1", "--untracked-files=all")
    started = time.time_ns()
    result = subprocess.run(
        ["bash", str(ROOT / "tests" / "run-all.sh")],
        cwd=ROOT,
        check=False,
    )
    status_after = _git("status", "--porcelain=v1", "--untracked-files=all")
    evidence = {
        "schema_version": "1",
        "source_commit": _git("rev-parse", "HEAD"),
        "support_row": os.environ.get(
            "ENGINEERING_BOARD_SUPPORT_ROW",
            "linux-x86_64-bash",
        ),
        "os_family": platform.system().lower(),
        "architecture": platform.machine().lower(),
        "command": "bash tests/run-all.sh",
        "exit_code": result.returncode,
        "repository_status_before": status_before,
        "repository_status_after": status_after,
        "started_unix_ns": started,
        "completed_unix_ns": time.time_ns(),
        "overall_pass": (result.returncode == 0 and status_before == status_after),
    }
    _atomic_json(args.output, evidence)
    print(f"aggregate evidence: {args.output}")
    return 0 if evidence["overall_pass"] else (result.returncode or 1)


if __name__ == "__main__":
    raise SystemExit(main())
