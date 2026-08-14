---
id: B069
type: bug
status: open
needs: tdd
priority: P2
title: Resolved entries append below older archive rows despite newest-first contract
affects: mcp-server/engineering_board_mcp.py
discovered: 2026-08-14
discovered_at: 2026-08-14T16:58:03Z
promoted_from: [mcp:_sessions/mcp-2026-08-14.md:e0f7094b14f76f45]
---

# Resolved entries append below older archive rows despite newest-first contract

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> `ARCHIVE_SKELETON` says "Resolved entries. Newest at the top." while `board_update_entry` writes `archive.rstrip() + "\n" + archive_line`. B022 and B016 resolutions both appeared after older rows at the file bottom.
