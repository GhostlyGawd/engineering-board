#!/usr/bin/env bash
# board-paths.sh — centralized board/runtime path resolution (engineering-board 1.1.0).
#
# SOURCED, NOT EXECUTED. Defines functions + constants; has no top-level side
# effects. Consumers do: `. "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-paths.sh"`.
#
# This is the single source of truth for *where the board lives*, replacing the
# router-parse block copy-pasted in board-consolidate.sh / board-index-check.sh /
# board-audit-scratch.sh (identical `while`-loop) and the `mapfile` variant in
# board-session-start.sh. Per specs/board-relocation.md §6.1, resolution order is:
#
#   1. $CLAUDE_PROJECT_DIR/engineering-board/BOARD-ROUTER.md  — new default (1.1.0)
#   2. $CLAUDE_PROJECT_DIR/docs/boards/BOARD-ROUTER.md        — compat (pre-1.1.0)
#   3. $CLAUDE_PROJECT_DIR/docs/board/                        — legacy single-board (no router)
#   4. none of the above                                     — no board (empty output)
#
# Per-project board dirs come from the chosen router's `path` column (relative,
# prepended with $CLAUDE_PROJECT_DIR) exactly as before — only the *router
# location* gains the new-default and compat lookup. Row parsing is kept
# byte-identical to the code it replaces so this is a faithful drop-in.
#
# Portability: pure bash + grep + awk (crosscompat-lint clean — no jq, no
# date -d/-j, no drive letters).
#
# API:
#   eb_router_path            -> resolved BOARD-ROUTER.md path, or empty (legacy/none)
#   eb_board_dirs             -> newline-separated ABSOLUTE board dirs (router-driven,
#                                with legacy single-board fallback)
#   eb_board_rows             -> "<label><TAB><absolute-path>" per project (for
#                                session-start, which needs the project labels)
# Constants (single source of truth for the three locations):
#   EB_NEW_ROOT, EB_COMPAT_ROOT, EB_LEGACY_DIR

EB_NEW_ROOT="engineering-board"
EB_COMPAT_ROOT="docs/boards"
EB_LEGACY_DIR="docs/board"

# eb_router_path — echo the resolved router file path per the §6.1 order, or
# nothing when no router exists (legacy single-board and no-board both return "").
eb_router_path() {
  local proj="${CLAUDE_PROJECT_DIR:-}"
  if [ -f "${proj}/${EB_NEW_ROOT}/BOARD-ROUTER.md" ]; then
    printf '%s\n' "${proj}/${EB_NEW_ROOT}/BOARD-ROUTER.md"
  elif [ -f "${proj}/${EB_COMPAT_ROOT}/BOARD-ROUTER.md" ]; then
    printf '%s\n' "${proj}/${EB_COMPAT_ROOT}/BOARD-ROUTER.md"
  fi
  return 0
}

# eb_board_dirs — echo absolute board dirs, one per line. Router-driven when a
# router exists (path column, prepended with $CLAUDE_PROJECT_DIR); else the
# legacy single-board dir when present; else nothing.
eb_board_dirs() {
  local proj="${CLAUDE_PROJECT_DIR:-}"
  local router line rel
  router="$(eb_router_path)"
  if [ -n "$router" ]; then
    while IFS= read -r line; do
      rel="$(printf '%s' "$line" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/,"",$3); print $3}')"
      if [ -n "$rel" ] && [ "$rel" != "path" ]; then
        printf '%s\n' "${proj}/${rel}"
      fi
    done < <(grep "^|" "$router" | grep -v "^| project" | grep -v "^|---" || true)
    return 0
  fi
  if [ -d "${proj}/${EB_LEGACY_DIR}" ]; then
    printf '%s\n' "${proj}/${EB_LEGACY_DIR}"
  fi
  return 0
}

# eb_board_rows — echo "<label><TAB><absolute-path>" per project. Same resolution
# as eb_board_dirs, but also carries the router's `project` column (col 2) as the
# label; the legacy single-board fallback is labeled "project". A row with an
# empty label cell defaults to "project" (matches session-start's use-site
# default) so label/path pairing never drifts.
eb_board_rows() {
  local proj="${CLAUDE_PROJECT_DIR:-}"
  local router line label rel
  router="$(eb_router_path)"
  if [ -n "$router" ]; then
    while IFS= read -r line; do
      label="$(printf '%s' "$line" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/,"",$2); print $2}')"
      rel="$(printf '%s' "$line" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/,"",$3); print $3}')"
      if [ -n "$rel" ] && [ "$rel" != "path" ]; then
        [ -z "$label" ] && label="project"
        printf '%s\t%s\n' "$label" "${proj}/${rel}"
      fi
    done < <(grep "^|" "$router" | grep -v "^| project" | grep -v "^|---" || true)
    return 0
  fi
  if [ -d "${proj}/${EB_LEGACY_DIR}" ]; then
    printf '%s\t%s\n' "project" "${proj}/${EB_LEGACY_DIR}"
  fi
  return 0
}
