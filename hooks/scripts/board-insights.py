#!/usr/bin/env python3
"""Thin CLI adapter for Engineering Board root-cause intelligence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


MCP_DIR = Path(__file__).resolve().parents[2] / "mcp-server"
sys.path.insert(0, str(MCP_DIR))

from engineering_board_core import (  # noqa: E402
    GraphError,
    apply_hypothesis_plan,
    build_insights,
    list_hypotheses,
    plan_hypothesis_operation,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--board-dir", required=True)
    parser.add_argument("--project", required=True)
    subparsers = parser.add_subparsers(dest="command", required=True)

    rank = subparsers.add_parser("rank")
    rank.add_argument("--cluster")
    rank.add_argument("--limit", type=int)

    subparsers.add_parser("list")

    preview = subparsers.add_parser("preview")
    preview.add_argument("--action", required=True)
    preview.add_argument("--payload")

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--token", required=True)

    args = parser.parse_args(argv)
    board_dir = Path(args.board_dir).resolve()
    if not board_dir.is_dir():
        print(
            json.dumps({"error": "board_not_found", "path": str(board_dir)}),
            file=sys.stderr,
        )
        return 2
    try:
        if args.command == "rank":
            result = build_insights(
                board_dir,
                args.project,
                cluster_fingerprint=args.cluster,
                limit=args.limit,
            )
        elif args.command == "list":
            result = list_hypotheses(board_dir, args.project)
        elif args.command == "preview":
            if args.payload:
                payload_path = Path(args.payload).resolve()
                if payload_path.is_symlink():
                    raise GraphError("linked hypothesis payload is not allowed")
                payload = json.loads(payload_path.read_text(encoding="utf-8"))
            else:
                payload = json.load(sys.stdin)
            if not isinstance(payload, dict):
                raise GraphError("hypothesis payload must be an object")
            result = plan_hypothesis_operation(board_dir, args.project, args.action, payload)
        else:
            result = apply_hypothesis_plan(board_dir, args.project, args.token)
    except (GraphError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {"error": "hypothesis_operation_failed", "detail": str(exc)},
                ensure_ascii=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
