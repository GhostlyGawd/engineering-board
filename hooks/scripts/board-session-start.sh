#!/bin/bash
set -euo pipefail

BOARDS_ROUTER="${CLAUDE_PROJECT_DIR}/docs/boards/BOARD-ROUTER.md"

# Fall back to legacy single-board layout if router doesn't exist
LEGACY_BOARD="${CLAUDE_PROJECT_DIR}/docs/board/BOARD.md"
if [ ! -f "${BOARDS_ROUTER}" ]; then
  if [ ! -f "${LEGACY_BOARD}" ]; then
    # No board exists — print a one-line nudge and exit
    echo "Engineering board not initialized in this project. Run /board-init <project-name> to scaffold one (or ignore this if you don't want a board here)."
    exit 0
  fi
  BOARD_PATHS=("${CLAUDE_PROJECT_DIR}/docs/board")
  PROJECT_LABELS=("project")
else
  # Parse project paths from router table rows: | project | path | ... |
  mapfile -t BOARD_PATHS < <(grep "^|" "${BOARDS_ROUTER}" | grep -v "^| project" | grep -v "^|---" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/,"",$3); print $3}' | grep -v "^$" | sed "s|^|${CLAUDE_PROJECT_DIR}/|")
  mapfile -t PROJECT_LABELS < <(grep "^|" "${BOARDS_ROUTER}" | grep -v "^| project" | grep -v "^|---" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/,"",$2); print $2}' | grep -v "^$")
fi

if [ ${#BOARD_PATHS[@]} -eq 0 ]; then
  exit 0
fi

echo "=== Engineering Board ==="
echo ""

for i in "${!BOARD_PATHS[@]}"; do
  BOARD_DIR="${BOARD_PATHS[$i]}"
  LABEL="${PROJECT_LABELS[$i]:-project}"
  BOARD_FILE="${BOARD_DIR}/BOARD.md"

  if [ ! -f "${BOARD_FILE}" ]; then
    continue
  fi

  open_items=$(grep "^- [BFQO]" "${BOARD_FILE}" 2>/dev/null || true)
  open_count=$(echo "${open_items}" | grep -c "^- " 2>/dev/null || echo "0")

  echo "[ ${LABEL} ] — ${open_count} open item(s):"
  if [ -n "${open_items}" ]; then
    echo "${open_items}"
  else
    echo "  (none)"
  fi
  echo ""

  # In-progress warning
  in_progress_files=$(grep -rl "^status: in_progress" "${BOARD_DIR}" --include="*.md" 2>/dev/null || true)
  if [ -n "${in_progress_files}" ]; then
    echo "  WARNING — items left in_progress:"
    while IFS= read -r f; do
      item_id=$(grep "^id:" "${f}" 2>/dev/null | awk '{print $2}' || true)
      item_title=$(grep "^title:" "${f}" 2>/dev/null | sed 's/^title: //' || true)
      echo "    - ${item_id}: ${item_title}"
    done <<< "${in_progress_files}"
    echo "  Resolve or reset before starting new work."
    echo ""
  fi

  # Live dependency map
  blocked_lines=$(grep -r "^blocked_by:" "${BOARD_DIR}" --include="*.md" -h 2>/dev/null | sort | uniq || true)
  if [ -n "${blocked_lines}" ]; then
    echo "  Blocking relationships:"
    while IFS= read -r line; do
      blockers=$(echo "${line}" | grep -oE '[QBF][0-9]+' || true)
      entry_file=$(grep -rl "${line}" "${BOARD_DIR}" --include="*.md" 2>/dev/null | head -1 || true)
      if [ -n "${entry_file}" ] && [ -n "${blockers}" ]; then
        entry_id=$(grep "^id:" "${entry_file}" 2>/dev/null | awk '{print $2}' || true)
        for blocker in ${blockers}; do
          echo "    ${blocker} blocks ${entry_id}"
        done
      fi
    done <<< "${blocked_lines}"
    echo ""
  fi

  # Systemic pattern clusters — warn if any pattern appears 3+ times in open entries
  pattern_clusters=$(grep -r "^pattern:" "${BOARD_DIR}/bugs/" "${BOARD_DIR}/features/" \
    --include="*.md" -h 2>/dev/null \
    | sed 's/^pattern: *//' | tr -d '[]' | tr ',' '\n' | tr -d ' ' | grep -v '^$' \
    | sort | uniq -c | sort -rn | awk '$1 >= 3 {print "    " $1 "x " $2}' || true)
  if [ -n "${pattern_clusters}" ]; then
    echo "  SYSTEMIC PATTERNS (3+ open entries) — investigate root cause before fixing individually:"
    echo "${pattern_clusters}"
    echo ""
  fi
done

echo "Real-time routing active: route findings to the correct project board as they surface — do not batch."
