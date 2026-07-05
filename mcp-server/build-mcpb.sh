#!/usr/bin/env bash
# Build the engineering-board MCP bundle (.mcpb) for the MCP Registry / Claude
# Desktop one-click install. An .mcpb is a zip with manifest.json at its root.
#
# The server shells out to hooks/scripts/board-claim-*.sh (resolved relative to
# its own location: mcp-server/../hooks/scripts), so the bundle ships both the
# mcp-server/ and hooks/ trees to keep those relative paths valid.
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

mkdir -p "$OUT_DIR" "$STAGE/mcp-server" "$STAGE/hooks/scripts"

# manifest.json at the bundle root (version pinned to the manifest live in-repo)
cp "$HERE/manifest.json" "$STAGE/manifest.json"

# the server itself
cp "$HERE/engineering_board_mcp.py" "$STAGE/mcp-server/engineering_board_mcp.py"
cp "$HERE/README.md" "$STAGE/mcp-server/README.md"

# the hook scripts the server shells out to (whole scripts dir — small, keeps
# every relative path the server or the claim scripts might use valid)
cp "$ROOT"/hooks/scripts/*.sh "$STAGE/hooks/scripts/"
cp "$ROOT"/hooks/scripts/*.py "$STAGE/hooks/scripts/" 2>/dev/null || true

cp "$ROOT/LICENSE" "$STAGE/LICENSE"

# deterministic zip (sorted entries, no extra attributes)
( cd "$STAGE" && find . -type f | LC_ALL=C sort | zip -q -X "$BUNDLE" -@ )

SHA="$(python3 -c "import hashlib,sys; print(hashlib.sha256(open('$BUNDLE','rb').read()).hexdigest())")"

echo "built: $BUNDLE"
echo "version: $VERSION"
echo "sha256: $SHA"
echo
echo "next (human): upload as a release asset on tag v$VERSION, then set"
echo "  packages[0].fileSha256 in mcp-server/server.json to the sha above and run"
echo "  mcp-publisher publish (see .goal/LAUNCH.md §4)."
