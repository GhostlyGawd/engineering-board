#!/usr/bin/env python3
"""CLI adapter for the shared Engineering Board graph core."""

from pathlib import Path
import sys


MCP_DIR = Path(__file__).resolve().parents[2] / "mcp-server"
sys.path.insert(0, str(MCP_DIR))

from engineering_board_core import main


if __name__ == "__main__":
    raise SystemExit(main())
