#!/usr/bin/env bash
# board-permission-self-check.sh
# Usage: bash board-permission-self-check.sh
# Reads references/required-permissions.json and ~/.claude/settings.json,
# reports which patterns are missing from the permissions.allow allowlist.
#
# Exit codes:
#   0 -- all installed
#   1 -- some missing
#   2 -- manifest file unreadable or invalid JSON
#   3 -- settings.json invalid JSON (missing file treated as empty, not error)

set -euo pipefail

MANIFEST="${CLAUDE_PLUGIN_ROOT}/references/required-permissions.json"
SETTINGS="${HOME}/.claude/settings.json"

python3 - "$MANIFEST" "$SETTINGS" <<'PY'
import sys
import json
import os
import re

def normalize_path(path):
    """On Windows, convert MSYS-style /c/foo paths to C:/foo so Python can open them.
    On Linux/Mac, return path unchanged."""
    if os.name == "nt":
        m = re.match(r"^/([a-zA-Z])/(.*)$", path)
        if m:
            return f"{m.group(1).upper()}:/{m.group(2)}"
    return path

manifest_path = normalize_path(sys.argv[1])
settings_path = normalize_path(sys.argv[2])

# Read manifest
try:
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
except (OSError, json.JSONDecodeError) as e:
    print(f"ERROR: could not read manifest: {e}", file=sys.stderr)
    sys.exit(2)

patterns = manifest.get("patterns", [])
total = len(patterns)

# Read settings (missing file = empty allowlist, not an error)
installed_allow = []
if os.path.exists(settings_path):
    try:
        with open(settings_path, encoding="utf-8") as f:
            settings = json.load(f)
        installed_allow = settings.get("permissions", {}).get("allow", [])
    except json.JSONDecodeError as e:
        print(f"ERROR: settings.json invalid JSON: {e}", file=sys.stderr)
        sys.exit(3)

installed_set = set(installed_allow)

missing = [p for p in patterns if p["pattern"] not in installed_set]
installed_count = total - len(missing)
missing_count = len(missing)

print(f"permission self-check: {total} needed, {installed_count} installed, {missing_count} missing")

if missing_count > 0:
    for p in missing:
        print(f"MISSING: {p['tool']}: {p['pattern']}")
    sys.exit(1)
else:
    print("all permissions installed.")
    sys.exit(0)
PY
