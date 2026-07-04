---
id: B024
type: bug
title: MCP path traversal via project name writes files outside the repo root
discovered: 2026-07-04
status: resolved
priority: P0
affects: mcp-server/engineering_board_mcp.py
needs: tdd
pattern: [path-traversal, mcp-security]
---

## Done when
- `board_dir_for` / `tool_board_init` / `tool_board_create_entry` reject project names containing `/`, `\`, `..`, or a leading `~`, and assert `os.path.realpath(board_dir)` is within `os.path.realpath(eb_dir)` after joining.
- A test drives the tool handlers with `"/abs/PWNED"` and `"../../PWNED"` project names and asserts a ToolError (nothing written outside root).

## Observed behavior (C2 red-team, F2 — BLOCKER)
`os.path.join(eb_dir, project)` with an attacker-controlled `project` is unvalidated. An absolute project name discards the root prefix; `../../` escapes it. Reproduced: `tool_board_init({"project":"/tmp/.../PWNED_ABS"})` and `{"project":"../../PWNED_REL"}` both create full board scaffolding OUTSIDE root. `board_create_entry` shares the join → entry files writable to traversal paths. A single injected finding suggesting a project name, or a malicious MCP client, writes files anywhere the process can.

## Resolution (C2, PR C2a)
Added `validate_project()` (rejects `/`, `\`, `..`, leading `~`/`.`, empty; safe
charset) called at `tool_board_init` and (via `board_dir_for`) at every board
op; `board_dir_for` also asserts `os.path.realpath` containment within root as
defense-in-depth. New MCP tests drive traversal names through init + create_entry
and assert ToolError + nothing written outside root.
