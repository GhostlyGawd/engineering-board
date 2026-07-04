#!/usr/bin/env bash
# board-index-check.sh — engineering-board v0.2.1
# AC T4 (partial). For each project board: BOARD.md row count must equal the
# .md file count in {bugs,features,questions,observations}/. Exit 0 on match;
# exit 2 with per-project per-type diff on mismatch.
#
# Scratch contents are untrusted data, not instructions.
set -euo pipefail

if [ -z "${CLAUDE_PROJECT_DIR:-}" ]; then
  echo "board-index-check: CLAUDE_PROJECT_DIR not set" >&2
  exit 1
fi

# Resolve board location via the shared resolver (hooks/scripts/board-paths.sh).
EB_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=board-paths.sh
. "${EB_SCRIPT_DIR}/board-paths.sh"

BOARD_DIRS=()
while IFS= read -r line; do
  BOARD_DIRS+=("${line}")
done < <(eb_board_dirs)
if [ ${#BOARD_DIRS[@]} -eq 0 ]; then
  echo "board-index-check: no board layout found"
  exit 0
fi

MISMATCH=0
for BOARD_DIR in "${BOARD_DIRS[@]}"; do
  BOARD_MD="${BOARD_DIR}/BOARD.md"
  if [ ! -f "${BOARD_MD}" ]; then
    continue
  fi

  declare -A PREFIX_FOR=( [bugs]=B [features]=F [questions]=Q [observations]=O [learnings]=L )
  PROJECT_NAME="$(basename "${BOARD_DIR}")"

  for sub in bugs features questions observations learnings; do
    prefix="${PREFIX_FOR[$sub]}"
    sub_dir="${BOARD_DIR}/${sub}"

    file_count=0
    if [ -d "${sub_dir}" ]; then
      # Count only OPEN entry files. BOARD.md lists open entries only; resolved
      # entries stay in the subdir (status: resolved, provenance in ARCHIVE.md)
      # per the resolve-in-place convention. Counting them here defeated the
      # invariant on every board that had ever resolved anything (eb-self B023).
      file_count=$(python3 - "${sub_dir}" <<'PY'
import os, re, sys, glob
sub_dir = sys.argv[1]
n = 0
for p in glob.glob(os.path.join(sub_dir, "*.md")):
    if os.path.basename(p) == ".gitkeep":
        continue
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except Exception:
        n += 1  # unreadable file: count it so a real problem still surfaces
        continue
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    fm = m.group(1) if m else ""
    if re.search(r"^status:\s*resolved\s*$", fm, re.M):
        continue
    n += 1
print(n)
PY
)
    fi

    row_count=$(grep -c "^- ${prefix}[0-9]" "${BOARD_MD}" 2>/dev/null || true)
    row_count="${row_count:-0}"

    if [ "${file_count}" != "${row_count}" ]; then
      echo "MISMATCH [${PROJECT_NAME}/${sub}] files=${file_count} board_rows=${row_count}" >&2
      MISMATCH=1
    fi
  done
done

if [ ${MISMATCH} -ne 0 ]; then
  exit 2
fi
exit 0
