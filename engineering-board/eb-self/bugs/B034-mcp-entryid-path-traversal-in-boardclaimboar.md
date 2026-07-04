---
id: B034
type: bug
title: MCP entry_id path traversal in board_claim/board_release (arbitrary create + rm -rf)
discovered: 2026-07-04
status: resolved
priority: P0
affects: mcp-server/engineering_board_mcp.py
needs: tdd
pattern: [path-traversal, mcp-security]
---

## Done when
- MCP `board_claim` / `board_release` validate `entry_id` (safe charset, reject `..`/separators) before shelling out, AND the claim scripts assert `CLAIM_DIR` stays under `<board-dir>/_claims/` (realpath containment, defense-in-depth).
- Tests drive traversal `entry_id` through claim + release and assert ToolError with nothing created/deleted outside root.

## Observed behavior (C3 red-team #1 — BLOCKER)
`board_dir_for` validates the project name, but `entry_id` is interpolated
straight into a filesystem path by board-claim-acquire.sh:51 (`CLAIM_DIR=.../_claims/${ENTRY_ID}`)
and board-claim-release.sh (`rm -rf "${CLAIM_DIR}"`). Reproduced:
`board_claim(entry_id="../../../../claimescape/pwned")` writes owner/heartbeat
OUTSIDE root; `board_release(entry_id="../../../../victim")` rm -rf's an external
dir (owner-match trivially satisfied — same caller supplies session_id + owner.txt).
Same traversal class as B024, left open for entry_id.

## Resolution (C3, PR C3b)
Added validate_entry_id() (safe single-segment charset, reject `..`) applied in
tool_board_claim/tool_board_release before shelling out; plus defense-in-depth
ENTRY_ID guards in board-claim-acquire.sh and board-claim-release.sh (reject
path separators / `..` for direct invocation). Traversal ids now rejected;
nothing created/deleted outside root. Pinned by MCP tests.
