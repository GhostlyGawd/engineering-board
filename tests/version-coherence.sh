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
README_MD="$ROOT/README.md"

for f in "$PLUGIN_JSON" "$MARKETPLACE_JSON" "$PYPROJECT_TOML" "$README_MD"; do
  if [ ! -f "$f" ]; then
    echo "version-coherence: MISSING $f" >&2
    exit 1
  fi
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "version-coherence: python3 not on PATH" >&2
  exit 1
fi

# Capture without aborting on a nonzero python exit, so the FAIL diagnostic the
# python block prints is actually echoed instead of set -e killing us silently.
set +e
RESULT="$(python3 - "$PLUGIN_JSON" "$MARKETPLACE_JSON" "$PYPROJECT_TOML" "$README_MD" <<'PY'
import json, re, sys
plugin_path, marketplace_path, pyproject_path, readme_path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
with open(plugin_path, "r", encoding="utf-8") as f:
    plugin = json.load(f)
with open(marketplace_path, "r", encoding="utf-8") as f:
    market = json.load(f)
with open(pyproject_path, "r", encoding="utf-8") as f:
    pyproject_text = f.read()
with open(readme_path, "r", encoding="utf-8") as f:
    readme_text = f.read()

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
# regex, not tomllib (3.11+): matching the repo's python floor. Scope to the
# [project] table so a decoy `version =` under [build-system]/[tool.*] can't be
# read instead of the real package version.
project_section = re.search(
    r'(?ms)^\[project\]\s*$(.*?)(?=^\[|\Z)', pyproject_text)
if not project_section:
    print("FAIL pyproject.toml has no [project] table")
    sys.exit(1)
pm = re.search(r'^version\s*=\s*"([^"]+)"\s*$', project_section.group(1), re.M)
if not pm:
    print(f"FAIL pyproject.toml [project] has no parseable version = \"...\" line")
    sys.exit(1)
pyproject_version = pm.group(1)
if pyproject_version != plugin_version:
    print(f"FAIL version mismatch: plugin.json={plugin_version!r} vs pyproject.toml [project]={pyproject_version!r}")
    sys.exit(1)

# README version badge must match too (the shields badge drifts silently — it is
# the version a human reads first, and nothing else pins it).
bm = re.search(r'img\.shields\.io/badge/version-([0-9][^-]*)-', readme_text)
if not bm:
    print("FAIL README.md has no parseable version badge")
    sys.exit(1)
readme_version = bm.group(1)
if readme_version != plugin_version:
    print(f"FAIL version mismatch: plugin.json={plugin_version!r} vs README badge={readme_version!r}")
    sys.exit(1)

print(f"OK plugin={plugin_name} version={plugin_version} (marketplace.json + pyproject.toml + README badge in lockstep)")
sys.exit(0)
PY
)"
EXIT=$?
set -e

echo "$RESULT"
exit "$EXIT"
