#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
exec python3 "$ROOT/tests/foundation/test_application_guidance_aggregate.py"
