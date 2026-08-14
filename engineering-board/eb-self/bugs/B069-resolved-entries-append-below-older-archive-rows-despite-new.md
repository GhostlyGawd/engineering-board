---
id: B069
type: bug
status: resolved
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
- **codex** 2026-08-14T17:22:49Z: Merged-main closeout preflight found a real-fixture gap before resolution. The live archive begins with legacy rows such as '- B057 P3 | ...', but the merged matcher recognizes only '- B057 | ...'; it would insert B069 near the bottom. B069 remains in_progress. Follow-up scope: support both legacy priority-bearing and current canonical rows, drive the live format in tests, and rerun delivery.
- **codex** 2026-08-14T17:26:08Z: Real-fixture follow-up validation complete. Red: 103 MCP checks passed before O001 appeared below two '- B### P# |' rows. Green: all 180 MCP checks pass with priority-bearing historical rows followed by a current compact row; the full maintained suite passes 21 of 21. Acceptance checks are complete again; follow-up delivery is ready.
- **codex** 2026-08-14T17:31:19Z: Resolving after PR #139 and real-fixture follow-up PR #140 reached main. Exact merged-main tests runs 31823479030 and 31824199079 passed; implementation Pages run 31823478978 also passed. Source-MCP archive placement and repeat idempotency are verified immediately after this transition.
- **codex** 2026-08-14T17:31:55Z: Live closeout verification passed: B069 is the first archive row, every pre-existing archive byte follows unchanged, and a repeated resolved update leaves one B069 row with byte-identical archive content.

## Resolution

PR #139 replaced bottom appends with newest-first insertion. Closeout dogfooding then found that the initial matcher missed historical priority-bearing rows. PR #140 added that live format to the matcher and real-fixture test. Exact merged-main tests runs 31823479030 and 31824199079 passed; implementation Pages run 31823478978 also passed. The final source-MCP transition inserted B069 before the prior first B057 P3 row. A byte-for-byte comparison confirmed that the archive preamble and every older byte remained unchanged. Repeating the resolved update left the archive byte-identical with one B069 row. Product version 1.12.0, releases, packages, and deployment state remain unchanged.
