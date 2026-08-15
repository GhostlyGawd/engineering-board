---
id: B073
type: bug
status: open
needs: tdd
priority: P2
title: SessionStart counts BOARD convention examples as open entries
affects: hooks/scripts/board-session-start.sh
discovered: 2026-08-15
discovered_at: 2026-08-15T02:41:35Z
promoted_from: [mcp:_sessions/mcp-2026-08-15.md:337b5dbe8dcecf8d]
---

# SessionStart counts BOARD convention examples as open entries

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> With CLAUDE_PROJECT_DIR set correctly, SessionStart reported 5 open items while the graph and canonical BOARD had one open entry B070; the other four displayed rows came from the Conventions examples matched by grep ^- [BFQO].
