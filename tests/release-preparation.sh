#!/usr/bin/env bash
# Verify deterministic release preparation in a disposable repository copy.

set -uo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0
FAIL=0

pass() {
  printf "  [PASS] %s\n" "$1"
  PASS=$((PASS + 1))
}

fail() {
  printf "  [FAIL] %s\n" "$1"
  FAIL=$((FAIL + 1))
}

mkdir -p "$TMP/.agents/plugins" "$TMP/.claude-plugin" "$TMP/.codex-plugin" \
  "$TMP/mcp-server" "$TMP/hooks" "$TMP/scripts"
cp -R "$ROOT/hooks/scripts" "$TMP/hooks/scripts"
cp "$ROOT/.claude-plugin/plugin.json" "$TMP/.claude-plugin/plugin.json"
cp "$ROOT/.claude-plugin/marketplace.json" "$TMP/.claude-plugin/marketplace.json"
cp "$ROOT/.codex-plugin/plugin.json" "$TMP/.codex-plugin/plugin.json"
cp "$ROOT/.agents/plugins/marketplace.json" "$TMP/.agents/plugins/marketplace.json"
for source in "$ROOT"/mcp-server/*; do
  if [ -f "$source" ]; then
    cp "$source" "$TMP/mcp-server/"
  fi
done
cp "$ROOT/scripts/prepare-release.py" "$TMP/scripts/prepare-release.py"
cp "$ROOT/README.md" "$ROOT/CHANGELOG.md" "$ROOT/LICENSE" "$TMP/"

TARGET_VERSION="$(
  python3 - "$TMP/.claude-plugin/plugin.json" <<'PY'
import json
import pathlib
import sys

version = json.loads(pathlib.Path(sys.argv[1]).read_text())["version"]
major, minor, patch = (int(part) for part in version.split("."))
print(f"{major}.{minor}.{patch + 1}")
PY
)"

python3 - "$TMP/CHANGELOG.md" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
marker = "## [Unreleased]\n"
fixture = "\n### Fixed\n\n- Added a release-preparation test fixture.\n"
path.write_text(path.read_text().replace(marker, marker + fixture, 1))
PY

BEFORE="$(sha256sum "$TMP/.claude-plugin/plugin.json" | awk '{print $1}')"
CODEX_MARKET_BEFORE="$(sha256sum "$TMP/.agents/plugins/marketplace.json" | awk '{print $1}')"
if python3 "$ROOT/scripts/prepare-release.py" "$TARGET_VERSION" \
    --root "$TMP" --date 2026-07-28 --json > "$TMP/preview.json"; then
  pass "preview succeeds"
else
  fail "preview succeeds"
fi

AFTER="$(sha256sum "$TMP/.claude-plugin/plugin.json" | awk '{print $1}')"
CODEX_MARKET_AFTER="$(sha256sum "$TMP/.agents/plugins/marketplace.json" | awk '{print $1}')"
if [ "$BEFORE" = "$AFTER" ]; then
  pass "preview does not write files"
else
  fail "preview does not write files"
fi

if [ "$CODEX_MARKET_BEFORE" = "$CODEX_MARKET_AFTER" ]; then
  pass "preview does not write the Codex marketplace"
else
  fail "preview does not write the Codex marketplace"
fi

if python3 - "$TMP/preview.json" <<'PY'
import json, pathlib, sys
preview = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert preview["status"] == "preview"
assert ".agents/plugins/marketplace.json" in preview["changed_files"]
PY
then
  pass "preview plans the Codex marketplace version and ref update"
else
  fail "preview plans the Codex marketplace version and ref update"
fi

if python3 "$ROOT/scripts/prepare-release.py" "$TARGET_VERSION" \
    --root "$TMP" --date 2026-07-28 --apply --json > "$TMP/applied.json"; then
  pass "apply succeeds"
else
  fail "apply succeeds"
fi

if python3 - "$TMP" "$TARGET_VERSION" <<'PY'
import json, pathlib, re, sys
root = pathlib.Path(sys.argv[1])
target = sys.argv[2]
plugin = json.loads((root / ".claude-plugin/plugin.json").read_text())
codex_plugin = json.loads((root / ".codex-plugin/plugin.json").read_text())
market = json.loads((root / ".claude-plugin/marketplace.json").read_text())
codex_market = json.loads((root / ".agents/plugins/marketplace.json").read_text())
manifest = json.loads((root / "mcp-server/manifest.json").read_text())
server = json.loads((root / "mcp-server/server.json").read_text())
pyproject = (root / "mcp-server/pyproject.toml").read_text()
readme = (root / "README.md").read_text()
changelog = (root / "CHANGELOG.md").read_text()
assert plugin["version"] == target
assert codex_plugin["name"] == plugin["name"]
assert codex_plugin["version"] == target
assert market["plugins"][0]["version"] == target
assert market["plugins"][0]["source"] == "./"
assert codex_market["plugins"][0]["version"] == target
assert codex_market["plugins"][0]["source"] == {
    "source": "url",
    "url": "https://github.com/GhostlyGawd/engineering-board.git",
    "ref": f"v{target}",
}
assert manifest["version"] == target
assert server["version"] == target
assert server["packages"][0]["version"] == target
assert f"/v{target}/" in server["packages"][0]["identifier"]
assert re.search(rf'^version = "{re.escape(target)}"$', pyproject, re.M)
assert f"badge/version-{target}-" in readme
assert f"## [Unreleased]\n\n## [{target}] — 2026-07-28" in changelog
PY
then
  pass "all versioned surfaces align"
else
  fail "all versioned surfaces align"
fi

PIN="$(python3 -c "import json; print(json.load(open('$TMP/mcp-server/server.json'))['packages'][0]['fileSha256'])")"
OUT="$(cd "$TMP" && bash mcp-server/build-mcpb.sh)"
BUILT="$(printf "%s\n" "$OUT" | sed -n 's/^sha256: //p')"
if [ "$PIN" = "$BUILT" ]; then
  pass "pinned MCP bundle checksum reproduces"
else
  fail "pinned MCP bundle checksum reproduces"
fi

printf "\nApproved review change.\n" >> "$TMP/mcp-server/README.md"
if python3 "$ROOT/scripts/prepare-release.py" "$TARGET_VERSION" \
    --root "$TMP" --date 2026-07-28 --refresh --apply --json \
    > "$TMP/refreshed.json"; then
  pass "prepared version refresh succeeds"
else
  fail "prepared version refresh succeeds"
fi

REFRESHED_PIN="$(python3 -c "import json; print(json.load(open('$TMP/mcp-server/server.json'))['packages'][0]['fileSha256'])")"
REFRESHED_OUT="$(cd "$TMP" && bash mcp-server/build-mcpb.sh)"
REFRESHED_BUILT="$(printf "%s\n" "$REFRESHED_OUT" | sed -n 's/^sha256: //p')"
if [ "$REFRESHED_PIN" != "$PIN" ] && [ "$REFRESHED_PIN" = "$REFRESHED_BUILT" ]; then
  pass "refresh pins the changed bundle checksum"
else
  fail "refresh pins the changed bundle checksum"
fi

SECTION_COUNT="$(grep -c "^## \\[$TARGET_VERSION\\]" "$TMP/CHANGELOG.md")"
if [ "$SECTION_COUNT" = "1" ]; then
  pass "refresh preserves one release section"
else
  fail "refresh preserves one release section"
fi

if python3 "$ROOT/scripts/prepare-release.py" "$TARGET_VERSION" \
    --root "$TMP" --date 2026-07-28 >/dev/null 2>&1; then
  fail "same version is refused"
else
  pass "same version is refused"
fi

if python3 "$ROOT/scripts/prepare-release.py" "v$TARGET_VERSION" \
    --root "$TMP" --date 2026-07-28 >/dev/null 2>&1; then
  fail "invalid version is refused"
else
  pass "invalid version is refused"
fi

if python3 "$ROOT/scripts/prepare-release.py" "${TARGET_VERSION%.*}.999" \
    --root "$TMP" --date 2026-07-28 --refresh >/dev/null 2>&1; then
  fail "refresh with another version is refused"
else
  pass "refresh with another version is refused"
fi

python3 - "$TMP/.agents/plugins/marketplace.json" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
market = json.loads(path.read_text())
market["plugins"][0]["source"]["ref"] = "main"
path.write_text(json.dumps(market, indent=2) + "\n")
PY
if python3 "$ROOT/scripts/prepare-release.py" "$TARGET_VERSION" \
    --root "$TMP" --date 2026-07-28 --refresh >/dev/null 2>&1; then
  fail "drifted Codex marketplace ref is refused"
else
  pass "drifted Codex marketplace ref is refused"
fi

printf "\nrelease-preparation: %d pass, %d fail\n" "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
