#!/usr/bin/env python3
# ruff: noqa: UP006, UP035
"""Run the compatibility aggregate and retain its exact-head result manifest."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = subprocess.run(
        [
            "python3",
            str(ROOT / "scripts" / "legacy_run_all.py"),
            "--root",
            str(ROOT),
            "--report",
            str(args.output),
        ],
        cwd=ROOT,
        check=False,
    )
    print(f"aggregate evidence: {args.output}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
