#!/usr/bin/env python3
"""Thin CLI adapter for deterministic Engineering Board context retrieval."""

from __future__ import annotations

import argparse
import json
import signal
import sys
from pathlib import Path


MCP_DIR = Path(__file__).resolve().parents[2] / "mcp-server"
sys.path.insert(0, str(MCP_DIR))

from engineering_board_core import (  # noqa: E402
    GraphError,
    build_context,
    build_value_report,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--board-dir", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--task", default="")
    parser.add_argument("--file", action="append", dest="files")
    parser.add_argument("--entry", action="append", dest="entry_ids")
    parser.add_argument("--cwd", default="")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--deadline-seconds", type=float)
    args = parser.parse_args(argv)
    board_dir = Path(args.board_dir).resolve()
    if not board_dir.is_dir():
        print(
            json.dumps({"error": "board_not_found", "path": str(board_dir)}),
            file=sys.stderr,
        )
        return 2
    alarm_enabled = bool(
        args.deadline_seconds
        and args.deadline_seconds > 0
        and hasattr(signal, "SIGALRM")
    )
    if alarm_enabled:
        signal.signal(
            signal.SIGALRM,
            lambda _signum, _frame: (_ for _ in ()).throw(
                TimeoutError("context deadline exceeded")
            ),
        )
        signal.setitimer(signal.ITIMER_REAL, args.deadline_seconds)
    try:
        result = (
            build_value_report(board_dir, args.project)
            if args.report
            else build_context(
                board_dir,
                args.project,
                task=args.task,
                files=args.files,
                entry_ids=args.entry_ids,
                cwd=args.cwd,
                limit=args.limit,
            )
        )
    except (GraphError, OSError, TimeoutError, ValueError) as exc:
        print(
            json.dumps(
                {"error": "context_request_failed", "detail": str(exc)},
                ensure_ascii=True,
            ),
            file=sys.stderr,
        )
        return 2
    finally:
        if alarm_enabled:
            signal.setitimer(signal.ITIMER_REAL, 0)
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
