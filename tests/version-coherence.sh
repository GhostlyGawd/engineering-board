#!/usr/bin/env bash
# tests/version-coherence.sh — Verify .claude-plugin/plugin.json and
# marketplace.json agree on the version string.
#
# NEXT-PHASE.md Tier 4.3 (Plugin version coherence check).
#
# Rationale: v0.2.2 shipped without a plugin.json version bump until the
# v0.2.2 docs-sync audit. Independent test guarantees the two manifests
# stay in lockstep regardless of which file gets edited.
#
# Usage:
#   bash tests/version-coherence.sh [plugin-root]
#
# Exits 0 iff plugin.json.version == marketplace.json.plugins[name=plugin.json.name].version.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"

PLUGIN_JSON="$ROOT/.claude-plugin/plugin.json"
MARKETPLACE_JSON="$ROOT/.claude-plugin/marketplace.json"

for f in "$PLUGIN_JSON" "$MARKETPLACE_JSON"; do
  if [ ! -f "$f" ]; then
    echo "version-coherence: MISSING $f" >&2
    exit 1
  fi
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "version-coherence: python3 not on PATH" >&2
  exit 1
fi

RESULT="$(python3 - "$PLUGIN_JSON" "$MARKETPLACE_JSON" <<'PY'
import json, sys
plugin_path, marketplace_path = sys.argv[1], sys.argv[2]
with open(plugin_path, "r", encoding="utf-8") as f:
    plugin = json.load(f)
with open(marketplace_path, "r", encoding="utf-8") as f:
    market = json.load(f)

plugin_name    = plugin.get("name", "")
plugin_version = plugin.get("version", "")
market_entries = market.get("plugins", [])

if not plugin_name:
    print(f"FAIL plugin.json has no name field")
    sys.exit(1)
if not plugin_version:
    print(f"FAIL plugin.json has no version field")
    sys.exit(1)

match = [p for p in market_entries if p.get("name") == plugin_name]
if not match:
    print(f"FAIL marketplace.json has no plugins[] entry with name={plugin_name!r}")
    sys.exit(1)
if len(match) > 1:
    print(f"FAIL marketplace.json has {len(match)} entries with name={plugin_name!r}; expected exactly 1")
    sys.exit(1)

market_version = match[0].get("version", "")
if market_version != plugin_version:
    print(f"FAIL version mismatch: plugin.json={plugin_version!r} vs marketplace.json={market_version!r}")
    sys.exit(1)

print(f"OK plugin={plugin_name} version={plugin_version}")
sys.exit(0)
PY
)"
EXIT=$?

echo "$RESULT"
exit "$EXIT"
