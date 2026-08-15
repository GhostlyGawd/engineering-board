---
id: B073
type: bug
status: in_progress
needs: validate
priority: P2
title: SessionStart counts BOARD convention examples as open entries
affects: hooks/scripts/board-session-start.sh
discovered: 2026-08-15
discovered_at: 2026-08-15T02:41:35Z
promoted_from: [mcp:_sessions/mcp-2026-08-15.md:337b5dbe8dcecf8d]
---

# SessionStart counts BOARD convention examples as open entries

## Done when

- [ ] A standard board with an empty `## Open` section and the Conventions footer reports zero open entries and renders no convention example.
- [ ] A standard board with one canonical open row reports one entry, renders that row, and renders no convention example.
- [ ] The live `eb-self` SessionStart count equals the canonical rows in `## Open`.
- [ ] Focused, cross-platform, and complete required checks pass while SessionStart remains below 10 seconds.

## Evidence

> With CLAUDE_PROJECT_DIR set correctly, SessionStart reported 5 open items while the graph and canonical BOARD had one open entry B070; the other four displayed rows came from the Conventions examples matched by grep ^- [BFQO].

## Comments

- **goal-hooks-20260815** 2026-08-15T03:40:12Z: Claimed for the section-bounded SessionStart checkpoint; the standard Conventions footer is the negative control.
- **goal-hooks-20260815** 2026-08-15T04:05:39Z: Focused checks and the settled complete suite pass. Advanced from TDD to independent review; merged-main and installed-artifact gates remain open.
- **goal-hooks-20260815** 2026-08-15T04:07:31Z: Independent read-only review found no remaining release blocker after patch and minor release-path coverage. Advanced to validation; installed and merged-main gates remain open.
