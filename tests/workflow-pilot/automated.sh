#!/usr/bin/env bash
# Deterministic only: fake clients and fixture validation; no model calls.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
cd "$ROOT"
python3 evaluation/workflow-pilot/test_runner.py
python3 evaluation/workflow-pilot/cases/validate.py
echo "Workflow-pilot deterministic checks: PASS (no live model calls)"
