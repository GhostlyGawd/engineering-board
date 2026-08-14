---
id: B063
type: bug
status: resolved
needs: validate
priority: P2
title: board_context silently returns no guidance for task-only requests
affects: mcp-server/engineering_board_core.py
discovered: 2026-08-14
discovered_at: 2026-08-14T04:41:36Z
promoted_from: [mcp:_sessions/mcp-2026-08-14.md:0]
---

# board_context silently returns no guidance for task-only requests

## Done when

- [x] A task-only request with no eligible memory returns a bounded corrective
  warning.
- [x] The warning tells the caller to add a file, entry identifier, or current
  directory.
- [x] Task words alone do not make memory eligible.
- [x] An explicit canonical P### pattern remains a valid structural signal.
- [x] Focused and complete repository tests pass.

## Evidence

> Dogfood probe: task='Improve Engineering Board by dogfooding its Codex MCP integration' returned results=[] and warnings=[]. Exact task terms also returned no result. Adding entry_ids=['B021'] returned cluster c-b939686d9ddd7e23. Structural eligibility is correct, but the empty response does not tell the caller to add files, entry_ids, or cwd.

## Comments

- **codex** 2026-08-14T04:41:36Z: Dogfood reproduction confirmed. Task-only context returned no results and no guidance. Structural eligibility remains required; the fix will add a bounded corrective warning.
- **codex** 2026-08-14T04:53:14Z: Verified through the configured MCP server, the lexical-decoy test, the explicit-pattern test, and the complete 19-suite repository run.
