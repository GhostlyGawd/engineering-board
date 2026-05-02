#!/bin/bash
set -euo pipefail

# Read tool input from stdin
input=$(cat)
file_path=$(echo "${input}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || true)

if [ -z "${file_path}" ]; then
  exit 0
fi

# Normalize to absolute path
if [[ "${file_path}" != /* ]]; then
  file_path="${CLAUDE_PROJECT_DIR}/${file_path}"
fi

# Match both new multi-board layout and legacy single-board layout
case "${file_path}" in
  "${CLAUDE_PROJECT_DIR}/docs/boards/"*"/bugs/"*".md" | \
  "${CLAUDE_PROJECT_DIR}/docs/boards/"*"/features/"*".md" | \
  "${CLAUDE_PROJECT_DIR}/docs/boards/"*"/questions/"*".md" | \
  "${CLAUDE_PROJECT_DIR}/docs/boards/"*"/observations/"*".md" | \
  "${CLAUDE_PROJECT_DIR}/docs/board/bugs/"*".md" | \
  "${CLAUDE_PROJECT_DIR}/docs/board/features/"*".md" | \
  "${CLAUDE_PROJECT_DIR}/docs/board/questions/"*".md" | \
  "${CLAUDE_PROJECT_DIR}/docs/board/observations/"*".md")
    ;;
  *)
    exit 0
    ;;
esac

if [ ! -f "${file_path}" ]; then
  exit 0
fi

errors=()

# Extract frontmatter
frontmatter=$(awk '/^---/{if(p)exit;p=1;next}p' "${file_path}" 2>/dev/null || true)

has_field() {
  echo "${frontmatter}" | grep -q "^${1}:"
}

for field in id type title discovered; do
  if ! has_field "${field}"; then
    errors+=("Missing required frontmatter field: ${field}")
  fi
done

entry_type=$(echo "${frontmatter}" | grep "^type:" | awk '{print $2}' || true)

case "${entry_type}" in
  bug|feature)
    for field in status priority affects; do
      if ! has_field "${field}"; then
        errors+=("Missing required frontmatter field for ${entry_type}: ${field}")
      fi
    done
    if ! grep -q "^## Done when" "${file_path}" 2>/dev/null; then
      errors+=("Missing required '## Done when' section")
    fi
    ;;
  question)
    if ! has_field "status"; then
      errors+=("Missing required frontmatter field: status")
    fi
    if ! grep -q "^## Done when" "${file_path}" 2>/dev/null; then
      errors+=("Missing required '## Done when' section")
    fi
    ;;
  observation|"")
    ;;
esac

# Determine which BOARD.md to check — derive from file path
if [[ "${file_path}" == *"/docs/boards/"* ]]; then
  # Extract project board dir: everything up to and including the project name segment
  board_dir=$(echo "${file_path}" | sed -E 's|(.*docs/boards/[^/]+)/.*|\1|')
else
  board_dir="${CLAUDE_PROJECT_DIR}/docs/board"
fi

entry_id=$(echo "${frontmatter}" | grep "^id:" | awk '{print $2}' || true)
if [ -n "${entry_id}" ] && [ -f "${board_dir}/BOARD.md" ]; then
  if ! grep -q "${entry_id}" "${board_dir}/BOARD.md" 2>/dev/null; then
    if ! grep -q "${entry_id}" "${board_dir}/ARCHIVE.md" 2>/dev/null; then
      errors+=("${entry_id} not found in BOARD.md index or ARCHIVE.md — update the index")
    fi
  fi
fi

if [ ${#errors[@]} -gt 0 ]; then
  echo "Board entry validation errors in ${file_path}:" >&2
  for err in "${errors[@]}"; do
    echo "  - ${err}" >&2
  done
  exit 2
fi

exit 0
