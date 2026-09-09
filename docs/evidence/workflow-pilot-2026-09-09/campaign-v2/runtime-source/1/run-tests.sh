#!/usr/bin/env bash
# run-tests.sh — run the engineering-board MCP server test suite and print a
# single PASS/FAIL summary line.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if python3 "$SCRIPT_DIR/test_mcp_server.py"; then
  echo "================================================================"
  echo "mcp-server tests: PASS"
  echo "================================================================"
  exit 0
else
  echo "================================================================"
  echo "mcp-server tests: FAIL"
  echo "================================================================"
  exit 1
fi
