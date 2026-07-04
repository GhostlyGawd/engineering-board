---
id: B038
type: bug
title: MCP affects_prefix injects a BOARD-ROUTER row (control-file corruption + bulk DoS + project spoof)
discovered: 2026-07-04
status: resolved
priority: P1
affects: mcp-server/engineering_board_mcp.py
needs: tdd
pattern: [router-injection, mcp-security]
---

## Done when
- `board_init` flattens/sanitizes `affects_prefix` (strip newlines + neutralize `|`) before writing it into the router table.
- A test with an injecting `affects_prefix` asserts no spoofed project row and bulk tools still work.

## Observed behavior (C4 red-team F2 — MAJOR)
`affects_prefix` was written into BOARD-ROUTER.md with bare `%s`, unlike frontmatter (B028). `board_init(affects_prefix="alpha/ |\n| evil | /etc/cron.d | evil/")` injected a full router row → spoofed board_list_projects + persistent DoS of every no-project bulk tool (resolve_board_row rejects the escaping row) until a human edits the router.

## Resolution (C4, PR C4a)
`affects_prefix = _oneline(...).replace("|","/")` — newlines flattened, column separator neutralized, so it stays a single harmless cell. Pinned by an MCP test (no spoofed project, no bulk DoS).
