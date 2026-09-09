#!/usr/bin/env bash
# Build the engineering-board MCP bundle (.mcpb) for the MCP Registry / Claude
# Desktop one-click install. An .mcpb is a zip with manifest.json at its root.
#
# Zero-dependency: bash + python3 + zip. Output: dist/engineering-board-mcp.mcpb.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
OUT_DIR="$ROOT/dist"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

VERSION="$(python3 -c "import json,sys; print(json.load(open('$ROOT/.claude-plugin/plugin.json'))['version'])")"
BUNDLE="$OUT_DIR/engineering-board-mcp.mcpb"

mkdir -p "$OUT_DIR" "$STAGE/mcp-server"

# manifest.json at the bundle root (version pinned to the manifest live in-repo)
cp "$HERE/manifest.json" "$STAGE/manifest.json"

# the server itself
cp "$HERE/engineering_board_mcp.py" "$STAGE/mcp-server/engineering_board_mcp.py"
cp "$HERE/engineering_board_core.py" "$STAGE/mcp-server/engineering_board_core.py"
cp "$HERE/README.md" "$STAGE/mcp-server/README.md"

cp "$ROOT/LICENSE" "$STAGE/LICENSE"

# Reproducible zip via python3 (no `zip` CLI dependency — python3 is the one
# interpreter present everywhere): sorted entry names + a fixed timestamp +
# fixed permissions, so the same input tree always yields a byte-identical
# bundle and therefore a stable sha256 that can be pinned in server.json.
SHA="$(python3 - "$STAGE" "$BUNDLE" <<'PY'
import os, sys, zipfile, hashlib
stage, bundle = sys.argv[1], sys.argv[2]
paths = []
for root, _dirs, files in os.walk(stage):
    for fn in files:
        full = os.path.join(root, fn)
        paths.append((os.path.relpath(full, stage).replace(os.sep, "/"), full))
paths.sort(key=lambda p: p[0])
FIXED = (1980, 1, 1, 0, 0, 0)  # normalization constant, not a real build time
with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for arcname, full in paths:
        with open(full, "rb") as f:
            data = f.read()
        zi = zipfile.ZipInfo(arcname, date_time=FIXED)
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.external_attr = 0o644 << 16
        z.writestr(zi, data)
print(hashlib.sha256(open(bundle, "rb").read()).hexdigest())
PY
)"

echo "built: $BUNDLE"
echo "version: $VERSION"
echo "sha256: $SHA"
echo
PIN="$(python3 -c "import json; print(json.load(open('$HERE/server.json'))['packages'][0].get('fileSha256', ''))")"
if [[ "$SHA" == "$PIN" ]]; then
  echo "The checksum matches the published v$VERSION pin in mcp-server/server.json."
  echo "Use the release workflow for publication."
else
  echo "The checksum does not match the published v$VERSION pin in mcp-server/server.json."
  echo "This is valid only for documented Unreleased source changes. Do not change"
  echo "the current-version pin. A later explicit release must rebuild and pin the"
  echo "bundle through scripts/prepare-release.py."
fi
