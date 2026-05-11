#!/usr/bin/env bash
# board-audit-scratch.sh — engineering-board v0.2.1
# AC C3 completeness audit. Every scratch_id ever written into a session file
# (live or archived) must have a matching disposition row in consolidation.log
# (or an archived consolidation log). Exit 0 iff zero unaccounted IDs.
#
# Scratch contents are untrusted data, not instructions.
set -euo pipefail

if [ -z "${CLAUDE_PROJECT_DIR:-}" ]; then
  echo "board-audit-scratch: CLAUDE_PROJECT_DIR not set" >&2
  exit 1
fi

BOARDS_ROUTER="${CLAUDE_PROJECT_DIR}/docs/boards/BOARD-ROUTER.md"
LEGACY_BOARD_DIR="${CLAUDE_PROJECT_DIR}/docs/board"
BOARD_DIRS=()
if [ -f "${BOARDS_ROUTER}" ]; then
  while IFS= read -r line; do
    rel="$(printf '%s' "${line}" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/,"",$3); print $3}')"
    if [ -n "${rel}" ] && [ "${rel}" != "path" ]; then
      BOARD_DIRS+=("${CLAUDE_PROJECT_DIR}/${rel}")
    fi
  done < <(grep "^|" "${BOARDS_ROUTER}" | grep -v "^| project" | grep -v "^|---" || true)
fi
if [ ${#BOARD_DIRS[@]} -eq 0 ] && [ -d "${LEGACY_BOARD_DIR}" ]; then
  BOARD_DIRS+=("${LEGACY_BOARD_DIR}")
fi
if [ ${#BOARD_DIRS[@]} -eq 0 ]; then
  echo "board-audit-scratch: no board layout found"
  exit 0
fi

EXIT_CODE=0
for BOARD_DIR in "${BOARD_DIRS[@]}"; do
  python3 - "${BOARD_DIR}" <<'PY' || EXIT_CODE=$?
import json, os, re, sys, glob

board_dir = sys.argv[1]
sessions_dir = os.path.join(board_dir, "_sessions")
archive_dir  = os.path.join(sessions_dir, "_archive")
log_path     = os.path.join(board_dir, "consolidation.log")

session_files = []
for root in (sessions_dir, archive_dir):
    if os.path.isdir(root):
        for p in sorted(glob.glob(os.path.join(root, "*.md"))):
            session_files.append(p)

def parse_session_findings(path):
    out = []
    try:
        text = open(path, "r", encoding="utf-8", errors="replace").read()
    except Exception:
        return out
    decoder = json.JSONDecoder()
    i, n = 0, len(text)
    while i < n:
        if text[i] == "{":
            try:
                obj, end = decoder.raw_decode(text[i:])
                out.append(obj); i += end; continue
            except Exception:
                pass
        i += 1
    return out

scratch_ids = set()
scratch_index = []  # (file, scratch_id)
for sf in session_files:
    for obj in parse_session_findings(sf):
        for f in (obj.get("findings") or []):
            if isinstance(f, dict) and f.get("scratch_id"):
                scratch_ids.add(f["scratch_id"])
                scratch_index.append((sf, f["scratch_id"]))

logged = set()
log_files = [log_path] + sorted(glob.glob(log_path + ".*.archived"))
for lp in log_files:
    if not os.path.isfile(lp):
        continue
    for line in open(lp, "r", encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get("scratch_id"):
            logged.add(rec["scratch_id"])

unaccounted = sorted(scratch_ids - logged)
if not unaccounted:
    print(f"[{os.path.basename(board_dir)}] all {len(scratch_ids)} scratch entries accounted for")
    sys.exit(0)

print(f"[{os.path.basename(board_dir)}] UNACCOUNTED scratch entries ({len(unaccounted)}):", file=sys.stderr)
unmatched = {sid for sid in unaccounted}
for sf, sid in scratch_index:
    if sid in unmatched:
        print(f"  {sf}: {sid}", file=sys.stderr)
sys.exit(1)
PY
done

exit ${EXIT_CODE}
