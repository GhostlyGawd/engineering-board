#!/usr/bin/env bash
# tests/version-coherence.sh — Verify .claude-plugin/plugin.json,
# marketplace.json, and mcp-server/pyproject.toml agree on the version string.
#
# NEXT-PHASE.md Tier 4.3 (Plugin version coherence check); pyproject added for
# the C3 PyPI channel (a PyPI release with a stale version is irreversible).
#
# Rationale: v0.2.2 shipped without a plugin.json version bump until the
# v0.2.2 docs-sync audit. Independent test guarantees the manifests
# stay in lockstep regardless of which file gets edited.
#
# Usage:
#   bash tests/version-coherence.sh [plugin-root]
#
# Exits 0 iff plugin.json.version == marketplace.json.plugins[name=plugin.json.name].version
#           == pyproject.toml [project].version.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"

PLUGIN_JSON="$ROOT/.claude-plugin/plugin.json"
MARKETPLACE_JSON="$ROOT/.claude-plugin/marketplace.json"
PYPROJECT_TOML="$ROOT/mcp-server/pyproject.toml"

for f in "$PLUGIN_JSON" "$MARKETPLACE_JSON" "$PYPROJECT_TOML"; do
  if [ ! -f "$f" ]; then
    echo "version-coherence: MISSING $f" >&2
    exit 1
  fi
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "version-coherence: python3 not on PATH" >&2
  exit 1
fi

RESULT="$(python3 - "$PLUGIN_JSON" "$MARKETPLACE_JSON" "$PYPROJECT_TOML" <<'PY'
import json, re, sys
plugin_path, marketplace_path, pyproject_path = sys.argv[1], sys.argv[2], sys.argv[3]
with open(plugin_path, "r", encoding="utf-8") as f:
    plugin = json.load(f)
with open(marketplace_path, "r", encoding="utf-8") as f:
    market = json.load(f)
with open(pyproject_path, "r", encoding="utf-8") as f:
    pyproject_text = f.read()

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

# pyproject.toml (C3 PyPI package) must be in the same lockstep. Parsed with a
# regex, not tomllib (3.11+): the version key is the first `version = "..."`
# top-level assignment inside [project] — matching the repo's python floor.
pm = re.search(r'^version\s*=\s*"([^"]+)"\s*$', pyproject_text, re.M)
if not pm:
    print(f"FAIL pyproject.toml has no parseable version = \"...\" line")
    sys.exit(1)
pyproject_version = pm.group(1)
if pyproject_version != plugin_version:
    print(f"FAIL version mismatch: plugin.json={plugin_version!r} vs pyproject.toml={pyproject_version!r}")
    sys.exit(1)

print(f"OK plugin={plugin_name} version={plugin_version} (marketplace.json + pyproject.toml in lockstep)")
sys.exit(0)
PY
)"
EXIT=$?

echo "$RESULT"
exit "$EXIT"
