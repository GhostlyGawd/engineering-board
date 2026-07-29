#!/usr/bin/env python3
"""Thin CLI adapter for Engineering Board outcome and Learning feedback."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


MCP_DIR = Path(__file__).resolve().parents[2] / "mcp-server"
sys.path.insert(0, str(MCP_DIR))

from engineering_board_core import (  # noqa: E402
    GraphError,
    apply_learning_plan,
    apply_outcome_plan,
    build_value_report,
    curate_learning_feedback,
    plan_outcome,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--board-dir", required=True)
    parser.add_argument("--project", required=True)
    subparsers = parser.add_subparsers(dest="command", required=True)
    preview = subparsers.add_parser("preview")
    preview.add_argument("--payload")
    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--token", required=True)
    learning = subparsers.add_parser("apply-learning")
    learning.add_argument("--token", required=True)
    curate = subparsers.add_parser("curate")
    curate.add_argument("--min-recurrence", type=int, default=3)
    subparsers.add_parser("report")
    args = parser.parse_args(argv)
    board_dir = Path(args.board_dir).resolve()
    if not board_dir.is_dir():
        print(
            json.dumps({"error": "board_not_found", "path": str(board_dir)}),
            file=sys.stderr,
        )
        return 2
    try:
        if args.command == "preview":
            if args.payload:
                payload_path = Path(args.payload).resolve()
                if payload_path.is_symlink():
                    raise GraphError("linked outcome payload is not allowed")
                payload = json.loads(payload_path.read_text(encoding="utf-8"))
            else:
                payload = json.load(sys.stdin)
            if not isinstance(payload, dict):
                raise GraphError("outcome payload must be an object")
            result = plan_outcome(board_dir, args.project, payload)
        elif args.command == "apply":
            result = apply_outcome_plan(board_dir, args.project, args.token)
        elif args.command == "apply-learning":
            result = apply_learning_plan(board_dir, args.project, args.token)
        elif args.command == "curate":
            result = curate_learning_feedback(
                board_dir, args.project, args.min_recurrence
            )
        else:
            result = build_value_report(board_dir, args.project)
    except (GraphError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {"error": "outcome_operation_failed", "detail": str(exc)},
                ensure_ascii=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
