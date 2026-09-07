#!/usr/bin/env bash
# Canonical Unix/macOS local web QA entry point.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "${ROOT}/scripts/serve_qa.py" "$@"
