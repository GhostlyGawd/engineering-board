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

mkdir -p "$TMP/.claude-plugin" "$TMP/mcp-server" "$TMP/hooks" "$TMP/scripts"
cp -R "$ROOT/hooks/scripts" "$TMP/hooks/scripts"
cp "$ROOT/.claude-plugin/plugin.json" "$TMP/.claude-plugin/plugin.json"
cp "$ROOT/.claude-plugin/marketplace.json" "$TMP/.claude-plugin/marketplace.json"
for source in "$ROOT"/mcp-server/*; do
  if [ -f "$source" ]; then
    cp "$source" "$TMP/mcp-server/"
  fi
done
cp "$ROOT/scripts/prepare-release.py" "$TMP/scripts/prepare-release.py"
cp "$ROOT/README.md" "$ROOT/CHANGELOG.md" "$ROOT/LICENSE" "$TMP/"

BEFORE="$(sha256sum "$TMP/.claude-plugin/plugin.json" | awk '{print $1}')"
if python3 "$ROOT/scripts/prepare-release.py" 1.10.1 \
    --root "$TMP" --date 2026-07-28 --json > "$TMP/preview.json"; then
  pass "preview succeeds"
else
  fail "preview succeeds"
fi

AFTER="$(sha256sum "$TMP/.claude-plugin/plugin.json" | awk '{print $1}')"
if [ "$BEFORE" = "$AFTER" ]; then
  pass "preview does not write files"
else
  fail "preview does not write files"
fi

if python3 "$ROOT/scripts/prepare-release.py" 1.10.1 \
    --root "$TMP" --date 2026-07-28 --apply --json > "$TMP/applied.json"; then
  pass "apply succeeds"
else
  fail "apply succeeds"
fi

if python3 - "$TMP" <<'PY'
import json, pathlib, re, sys
root = pathlib.Path(sys.argv[1])
plugin = json.loads((root / ".claude-plugin/plugin.json").read_text())
market = json.loads((root / ".claude-plugin/marketplace.json").read_text())
manifest = json.loads((root / "mcp-server/manifest.json").read_text())
server = json.loads((root / "mcp-server/server.json").read_text())
pyproject = (root / "mcp-server/pyproject.toml").read_text()
readme = (root / "README.md").read_text()
changelog = (root / "CHANGELOG.md").read_text()
assert plugin["version"] == "1.10.1"
assert market["plugins"][0]["version"] == "1.10.1"
assert manifest["version"] == "1.10.1"
assert server["version"] == "1.10.1"
assert server["packages"][0]["version"] == "1.10.1"
assert "/v1.10.1/" in server["packages"][0]["identifier"]
assert re.search(r'^version = "1\.10\.1"$', pyproject, re.M)
assert "badge/version-1.10.1-" in readme
assert "## [Unreleased]\n\n## [1.10.1] — 2026-07-28" in changelog
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

if python3 "$ROOT/scripts/prepare-release.py" 1.10.1 \
    --root "$TMP" --date 2026-07-28 >/dev/null 2>&1; then
  fail "same version is refused"
else
  pass "same version is refused"
fi

if python3 "$ROOT/scripts/prepare-release.py" v1.10.2 \
    --root "$TMP" --date 2026-07-28 >/dev/null 2>&1; then
  fail "invalid version is refused"
else
  pass "invalid version is refused"
fi

printf "\nrelease-preparation: %d pass, %d fail\n" "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
