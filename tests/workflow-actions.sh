#!/usr/bin/env bash
# Verify that every GitHub Actions checkout uses the reviewed Node 24 major.

set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"

python3 - "$ROOT" <<'PY'
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
workflow_dir = root / ".github" / "workflows"
uses = []

for path in sorted(workflow_dir.glob("*.y*ml")):
    text = path.read_text(encoding="utf-8")
    if "allow-unsafe-pr-checkout:" in text:
        print(
            f"workflow-actions: FAIL {path.relative_to(root)} opts out of "
            "checkout's safe fork defaults"
        )
        raise SystemExit(1)
    for match in re.finditer(
        r'''(?m)^\s*(?:-\s*)?uses:\s*["']?actions/checkout@([^\s#"']+)''',
        text,
    ):
        uses.append((path.relative_to(root), match.group(1)))

if not uses:
    print("workflow-actions: FAIL no actions/checkout use found")
    raise SystemExit(1)

unexpected = [(path, version) for path, version in uses if version != "v7"]
if unexpected:
    for path, version in unexpected:
        print(
            f"workflow-actions: FAIL {path} uses actions/checkout@{version}; "
            "expected the reviewed v7 major"
        )
    raise SystemExit(1)

files = len({path for path, _ in uses})
print(
    f"workflow-actions: PASS {len(uses)} checkout uses across {files} "
    "workflow files use v7"
)
PY
