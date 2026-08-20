#!/usr/bin/env bash
# tests/run-all.sh — Compatibility adapter for the maintained suite manifest.
#
# NEXT-PHASE.md Tier 4.1 (Single CI runner).
#
# The platform-neutral runner owns suite ordering, later-suite diagnostics,
# normalized decisions, artifact fingerprints, and native-Windows portable
# parity. This Bash path remains the supported Unix/macOS compatibility entry.
#
# The hooks.json regression caught in commit 52e99a4 lived in the tree for
# ~13 days because nobody ran all the suites together. This runner exists
# so "confirm green" is one command, not six.
#
# Usage:
#   bash tests/run-all.sh                # auto-detect plugin root
#   bash tests/run-all.sh <plugin-root>  # explicit root
#
# Exits 0 iff every sub-suite passes.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
exec python3 "$ROOT/scripts/legacy_run_all.py" --root "$ROOT"
