---
id: B035
type: bug
title: MCP bulk tools bypass router-row containment (arbitrary BOARD.md overwrite + cross-root read)
discovered: 2026-07-04
status: resolved
priority: P1
affects: mcp-server/engineering_board_mcp.py
needs: tdd
pattern: [path-traversal, mcp-security]
---

## Done when
- `tool_board_rebuild` / `tool_board_status` / `tool_board_list_entries` build router-row targets through a single checked resolver (realpath containment, reusing board_dir_for's guarantee), not raw `os.path.join(root, r["path"])`; rows that escape root are skipped/raised.
- A test with a tampered router row (`path = ../outside`) asserts the bulk tools don't write/read outside root.

## Observed behavior (C3 red-team #2 — MAJOR)
The no-`project` branches of board_rebuild (:873), board_status (:1049), and
board_list_entries (:619) use raw `os.path.join(root, r["path"])`, bypassing the
realpath containment board_dir_for applies (whose comment says "even a tampered
router row must not escape the root"). A router row `| evil | ../outside | |`
makes board_rebuild overwrite `../outside/BOARD.md`; a `../secret` row makes
board_list_entries/board_status read entries outside root. Gated behind a
tampered (hand-editable) router, hence P1 not P0.

## Resolution (C3, PR C3b)
Added resolve_board_row() (realpath containment) and routed the three bulk
(no-project) tools — board_rebuild, board_status, board_list_entries — through
it instead of raw os.path.join(root, r["path"]). A router row whose path escapes
root now raises ToolError; external files are not read or overwritten. Pinned by
an MCP test with a tampered router row.
