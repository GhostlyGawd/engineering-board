#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
python3 "$ROOT/tests/orchestration/python-newline-compatibility.py"
