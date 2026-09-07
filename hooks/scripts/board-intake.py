#!/usr/bin/env python3
"""Foreground promotion and canonical pattern operations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


MCP_DIR = Path(__file__).resolve().parents[2] / "mcp-server"
sys.path.insert(0, str(MCP_DIR))

from engineering_board_core import (
    GraphError,
    apply_pattern_operation,
    apply_promotion,
    load_pattern_registry,
    plan_pattern_operation,
    plan_promotion,
)
from engineering_board_mcp import rebuild_board


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--board-dir", required=True)
    parser.add_argument("--project", required=True)
    subcommands = parser.add_subparsers(dest="command", required=True)

    promote = subcommands.add_parser("promote")
    promote.add_argument("--session")
    promote.add_argument("--apply")

    pattern = subcommands.add_parser("pattern")
    pattern.add_argument(
        "--action",
        required=True,
        choices=["list", "create", "alias", "assign", "correct"],
    )
    pattern.add_argument("--label")
    pattern.add_argument("--alias", action="append", dest="aliases")
    pattern.add_argument("--pattern-id")
    pattern.add_argument("--entry-id")
    pattern.add_argument("--replace")
    pattern.add_argument("--with", dest="with_pattern")
    pattern.add_argument("--reason")
    pattern.add_argument("--definition")
    pattern.add_argument("--inclusion-evidence")
    pattern.add_argument("--exclusions")
    pattern.add_argument("--apply")

    args = parser.parse_args(argv)
    board_dir = Path(args.board_dir).resolve()
    if not board_dir.is_dir():
        print(
            json.dumps({"error": "board_not_found", "path": str(board_dir)}),
            file=sys.stderr,
        )
        return 2

    try:
        if args.command == "promote":
            if args.apply:
                result = apply_promotion(
                    board_dir,
                    args.project,
                    args.session,
                    args.apply,
                )
                rebuild_board(str(board_dir), args.project)
            else:
                result = plan_promotion(board_dir, args.project, args.session)
        elif args.action == "list":
            registry = load_pattern_registry(board_dir)
            result = {
                "patterns": [
                    {
                        key: record.get(key)
                        for key in (
                            "id",
                            "status",
                            "label",
                            "aliases",
                            "merged_into",
                            "source",
                        )
                        if record.get(key) is not None
                    }
                    for _, record in sorted(registry["by_id"].items())
                ]
            }
        else:
            params = {
                "label": args.label,
                "aliases": args.aliases,
                "alias": (args.aliases[0] if args.aliases else None),
                "pattern_id": args.pattern_id,
                "entry_id": args.entry_id,
                "replace": args.replace,
                "with": args.with_pattern,
                "reason": args.reason,
                "definition": args.definition,
                "inclusion_evidence": args.inclusion_evidence,
                "exclusions": args.exclusions,
            }
            if args.apply:
                result = apply_pattern_operation(
                    board_dir,
                    args.project,
                    args.action,
                    params,
                    args.apply,
                )
            else:
                result = plan_pattern_operation(board_dir, args.action, params)
    except GraphError as exc:
        detail = str(exc)
        error = detail.split(":", 1)[0] if ":" in detail else "invalid_operation"
        print(
            json.dumps({"error": error, "detail": detail}),
            file=sys.stderr,
        )
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
