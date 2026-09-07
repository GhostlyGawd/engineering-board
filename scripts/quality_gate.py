#!/usr/bin/env python3
"""Run the stable Engineering Board quality selector contract."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
from typing import NoReturn

from quality_checks import QualityError, QualityRunner
from validator_resources import ResourceError, run_locked


ROOT = Path(__file__).resolve().parents[1]
SELECTORS = ("format", "lint", "typecheck", "test", "security", "package", "all")

HELP_EPILOG = """\
Stable Unix/macOS entry points:
  bash scripts/quality-gate.sh format
  bash scripts/quality-gate.sh lint
  bash scripts/quality-gate.sh typecheck
  bash scripts/quality-gate.sh test --workers 2
  bash scripts/quality-gate.sh security
  bash scripts/quality-gate.sh package
  bash scripts/quality-gate.sh all --workers 2

Native Windows equivalents:
  PowerShell: python scripts/quality_gate.py <selector>
  cmd.exe:    python scripts\\quality_gate.py <selector>

Git Bash and WSL are compatibility environments. They are not native Windows
evidence. Coverage is part of the test contract; there is no standalone
coverage selector. The compatibility aggregate remains bash tests/run-all.sh.
"""


class QualityArgumentParser(argparse.ArgumentParser):
    """Argument parser with concise, stable error output."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(2, f"quality-gate: error: {message}\n")


def positive_workers(value: str) -> int:
    try:
        workers = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"--workers expects 1 or 2, got {value!r}") from exc
    if workers not in {1, 2}:
        raise argparse.ArgumentTypeError(f"--workers expects 1 or 2, got {value!r}")
    return workers


def build_parser() -> QualityArgumentParser:
    parser = QualityArgumentParser(
        prog="quality-gate",
        description=(
            "Run repository-owned formatting, linting, typing, test, security, "
            "or package stages with the pinned development toolchain."
        ),
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(dest="selector", metavar="SELECTOR")
    for selector in SELECTORS:
        subparser = subparsers.add_parser(
            selector,
            help=f"run the {selector} quality stage",
            add_help=True,
        )
        if selector in {"test", "all"}:
            subparser.add_argument(
                "--workers",
                type=positive_workers,
                default=2,
                help="maximum test workers, 1 or 2 (default: 2)",
            )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    if arguments.selector is None:
        parser.error("a selector is required: " + ", ".join(SELECTORS))

    root = arguments.root.expanduser().resolve()
    workers = int(getattr(arguments, "workers", 2))
    if (
        arguments.selector == "all"
        and os.environ.get("ENGINEERING_BOARD_VALIDATOR_SESSION") is None
    ):
        try:
            return run_locked(
                root / ".engineering-board" / "validator-locks",
                "quality-all",
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--root",
                    str(root),
                    "all",
                    "--workers",
                    str(workers),
                ],
                "aggregate",
            )
        except ResourceError as exc:
            print(f"quality-gate: {exc}", file=sys.stderr)
            return 75
    runner = QualityRunner(root)
    try:
        return runner.run(str(arguments.selector), workers)
    except QualityError as exc:
        print(f"quality-gate: {exc}", file=sys.stderr)
        return exc.exit_code
    except KeyboardInterrupt:
        print("quality-gate: interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUTF8", "1")
    raise SystemExit(main())
