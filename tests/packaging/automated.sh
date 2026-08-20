#!/usr/bin/env bash

set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
python3 "$ROOT/tests/packaging/test_package_gate.py"
