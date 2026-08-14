#!/usr/bin/env bash
# tests/version-coherence.sh — Verify all product version surfaces agree.
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
# Exits 0 iff the authoritative plugin version matches every release mirror,
# production agent/skill prose contains no legacy product-version label, and
# an unrelated data manifest does not carry a product-version mirror.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"

PLUGIN_JSON="$ROOT/.claude-plugin/plugin.json"
CODEX_PLUGIN_JSON="$ROOT/.codex-plugin/plugin.json"
MARKETPLACE_JSON="$ROOT/.claude-plugin/marketplace.json"
MCP_SERVER_JSON="$ROOT/mcp-server/server.json"
MCP_MANIFEST_JSON="$ROOT/mcp-server/manifest.json"
PYPROJECT_TOML="$ROOT/mcp-server/pyproject.toml"
README_MD="$ROOT/README.md"
PERMISSIONS_JSON="$ROOT/references/required-permissions.json"
RELEASING_MD="$ROOT/docs/RELEASING.md"
AGENTS_DIR="$ROOT/agents"
SKILLS_DIR="$ROOT/skills"

for f in "$PLUGIN_JSON" "$CODEX_PLUGIN_JSON" "$MARKETPLACE_JSON" \
  "$MCP_SERVER_JSON" "$MCP_MANIFEST_JSON" "$PYPROJECT_TOML" "$README_MD" \
  "$PERMISSIONS_JSON" "$RELEASING_MD"; do
  if [ ! -f "$f" ]; then
    echo "version-coherence: MISSING $f" >&2
    exit 1
  fi
done

for d in "$AGENTS_DIR" "$SKILLS_DIR"; do
  if [ ! -d "$d" ]; then
    echo "version-coherence: MISSING $d" >&2
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
RESULT="$(python3 - "$PLUGIN_JSON" "$CODEX_PLUGIN_JSON" "$MARKETPLACE_JSON" \
  "$MCP_SERVER_JSON" "$MCP_MANIFEST_JSON" "$PYPROJECT_TOML" "$README_MD" \
  "$PERMISSIONS_JSON" "$RELEASING_MD" "$AGENTS_DIR" "$SKILLS_DIR" <<'PY'
import json, pathlib, re, sys
(
    plugin_path,
    codex_plugin_path,
    marketplace_path,
    mcp_server_path,
    mcp_manifest_path,
    pyproject_path,
    readme_path,
    permissions_path,
    releasing_path,
    agents_dir,
    skills_dir,
) = sys.argv[1:]
with open(plugin_path, "r", encoding="utf-8") as f:
    plugin = json.load(f)
with open(codex_plugin_path, "r", encoding="utf-8") as f:
    codex_plugin = json.load(f)
with open(marketplace_path, "r", encoding="utf-8") as f:
    market = json.load(f)
with open(mcp_server_path, "r", encoding="utf-8") as f:
    mcp_server = json.load(f)
with open(mcp_manifest_path, "r", encoding="utf-8") as f:
    mcp_manifest = json.load(f)
with open(pyproject_path, "r", encoding="utf-8") as f:
    pyproject_text = f.read()
with open(readme_path, "r", encoding="utf-8") as f:
    readme_text = f.read()
with open(permissions_path, "r", encoding="utf-8") as f:
    permissions = json.load(f)
with open(releasing_path, "r", encoding="utf-8") as f:
    releasing_text = f.read()

plugin_name    = plugin.get("name", "")
plugin_version = plugin.get("version", "")
market_entries = market.get("plugins", [])

if not plugin_name:
    print(f"FAIL plugin.json has no name field")
    sys.exit(1)
if not plugin_version:
    print(f"FAIL plugin.json has no version field")
    sys.exit(1)
if codex_plugin.get("name") != plugin_name:
    print(f"FAIL plugin name mismatch: Claude={plugin_name!r} vs Codex={codex_plugin.get('name')!r}")
    sys.exit(1)
if codex_plugin.get("version") != plugin_version:
    print(f"FAIL version mismatch: Claude plugin={plugin_version!r} vs Codex plugin={codex_plugin.get('version')!r}")
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

failures = []
if mcp_manifest.get("version") != plugin_version:
    failures.append(
        f"MCP manifest={mcp_manifest.get('version')!r} vs plugin.json={plugin_version!r}"
    )
if mcp_server.get("version") != plugin_version:
    failures.append(
        f"MCP server={mcp_server.get('version')!r} vs plugin.json={plugin_version!r}"
    )
packages = mcp_server.get("packages")
if not isinstance(packages, list) or len(packages) != 1:
    failures.append("MCP server must contain exactly one package")
else:
    package = packages[0]
    if not isinstance(package, dict) or package.get("version") != plugin_version:
        value = package.get("version") if isinstance(package, dict) else None
        failures.append(
            f"MCP package={value!r} vs plugin.json={plugin_version!r}"
        )
    expected_release = f"/releases/download/v{plugin_version}/"
    identifier = package.get("identifier", "") if isinstance(package, dict) else ""
    if expected_release not in identifier:
        failures.append(
            f"MCP package identifier does not target release v{plugin_version}"
        )

if "version" in permissions:
    failures.append(
        "required-permissions.json has an unused product-version mirror"
    )

if (
    not re.search(r"authoritative\s+product version", releasing_text)
    or "`.claude-plugin/plugin.json`" not in releasing_text
):
    failures.append(
        "docs/RELEASING.md does not name plugin.json as the authoritative product version"
    )

product_label = re.compile(
    r"\bengineering-board\s+v\d+(?:\.\d+){1,3}\+?\b", re.IGNORECASE
)
for directory in (pathlib.Path(agents_dir), pathlib.Path(skills_dir)):
    for path in sorted(directory.rglob("*.md")):
        if product_label.search(path.read_text(encoding="utf-8")):
            failures.append(
                f"{path.relative_to(directory.parent)} has a legacy product-version label"
            )

if failures:
    for failure in failures:
        print(f"FAIL {failure}")
    sys.exit(1)

print(
    f"OK plugin={plugin_name} version={plugin_version} "
    "(authoritative Claude manifest + Codex + marketplace + MCP + PyPI + README)"
)
sys.exit(0)
PY
)"
EXIT=$?
set -e

echo "$RESULT"
exit "$EXIT"
