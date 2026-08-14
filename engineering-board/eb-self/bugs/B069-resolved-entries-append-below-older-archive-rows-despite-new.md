---
id: B069
type: bug
status: in_progress
needs: validate
priority: P2
title: Resolved entries append below older archive rows despite newest-first contract
affects: mcp-server/engineering_board_mcp.py
discovered: 2026-08-14
discovered_at: 2026-08-14T16:58:03Z
promoted_from: [mcp:_sessions/mcp-2026-08-14.md:e0f7094b14f76f45]
---

# Resolved entries append below older archive rows despite newest-first contract

## Done when

- [x] Each newly resolved entry is inserted immediately after the archive
  preamble, before every older archive row.
- [x] A later resolution becomes the first row while all older rows keep their
  relative order and the archive preamble remains byte-for-byte unchanged.
- [x] Repeating a resolved update does not duplicate the entry's archive row.
- [x] MCP real-fixture tests drive two resolutions and the repeated-update path;
  resolver skill, API, architecture, and release-note prose agree.

## Evidence

> `ARCHIVE_SKELETON` says "Resolved entries. Newest at the top." while `board_update_entry` writes `archive.rstrip() + "\n" + archive_line`. B022 and B016 resolutions both appeared after older rows at the file bottom.

## Comments

- **codex** 2026-08-14T17:04:06Z: Claimed immediately after intake. Scope: replace the placeholder with exact newest-first and idempotency criteria, add a red MCP real-fixture test, inspect sibling archive writers per L005, and preserve existing archive prose and rows.
- **codex** 2026-08-14T17:13:05Z: Implementation validation complete. Red: the new real-fixture assertion failed after 100 prior MCP checks because resolution still appended. Green: MCP 180 checks pass; documentation coherence, 6 mode suites, and 25 orchestration suites pass; the maintained suite passes 21 of 21. Acceptance criteria and dated alignment evidence are complete; ready for review and delivery.
