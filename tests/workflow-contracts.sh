#!/usr/bin/env bash
# Accept the shared runner root without passing it to unittest as a test selector.
set -euo pipefail
ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
python3 "$ROOT/tests/triage-ownership/test_claim_contract.py"
python3 "$ROOT/tests/b011-intake-contract.py"
