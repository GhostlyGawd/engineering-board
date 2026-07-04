---
id: B039
type: bug
title: MCP board_init follows symlinks to write scaffold outside root
discovered: 2026-07-04
status: resolved
priority: P2
affects: mcp-server/engineering_board_mcp.py
needs: tdd
pattern: [path-traversal, mcp-security]
---

## Done when
- `board_init` applies the same realpath containment the read/bulk tools use, before any makedirs/open.
- A test with a symlinked project dir asserts ToolError + nothing written outside root.

## Observed behavior (C4 red-team F3)
`board_init` was the one path-writing tool without realpath containment. A pre-planted `engineering-board/sneaky -> /outside` symlink made board_init write the full scaffold outside root. Precondition: a symlink already in the tree (malicious commit/PR), hence P2.

## Resolution (C4, PR C4a)
board_init now asserts realpath(eb_dir) and realpath(bd) stay within realpath(root) before writing. Pinned by an MCP symlink test.
