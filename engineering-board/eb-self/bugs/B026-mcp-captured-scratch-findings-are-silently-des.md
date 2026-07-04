---
id: B026
type: bug
title: MCP-captured scratch findings are silently destroyed on consolidate
discovered: 2026-07-04
status: resolved
priority: P1
affects: mcp-server/engineering_board_mcp.py
needs: tdd
pattern: [silent-data-loss, format-mismatch]
---

## Done when
- MCP `board_capture_finding` output is consolidatable: either `board-consolidate.sh` recognizes the MCP markdown format, OR `board_capture_finding` writes the JSON finding shape the consolidator ingests, OR Stage-5 GC refuses to archive a session file that yielded zero parsed findings (logging `deferred_unparsed`).
- A test captures via the MCP tool, runs board-consolidate.sh, and asserts the finding is either promoted or left with an audit-trail disposition (never silently archived).

## Observed behavior (C2 red-team, F3 — MAJOR, data loss)
`board_capture_finding` writes scratch as markdown (`## <ts> — <kind>: <title>`), but `board-consolidate.sh` `parse_session_findings` extracts only JSON `{...}` blocks. MCP findings parse to zero, are never promoted, then Stage-5 GC moves the scratch file into `_sessions/_archive/` with NO consolidation.log entry. `board-session-start.sh:134` actively tells the user to run board-consolidate.sh to consolidate these — following that guidance destroys the findings without a trace.

## Resolution (C2, PR C2c)
board-consolidate.sh Stage-5 GC now archives only session files that yielded at
least one parsed finding; a file with zero parsed findings (the MCP markdown
inbox, or any malformed file) is left in place and logged `deferred_unparsed`.
MCP findings have no transcript to anchor against and are designed to be
promoted via the MCP `board_create_entry` tool, so the consolidator no longer
destroys them. board-session-start.sh banner now says MCP inbox files
(`mcp-*.md`) are promoted via board_create_entry and the consolidator leaves
them untouched. Pinned by smoke tests 23-24 (preserved + deferred_unparsed).
