---
id: B068
type: bug
status: resolved
needs: validate
priority: P2
title: board-consolidate apply instructions omit the session selector required by session-scoped plans
affects: skills/board-consolidate/SKILL.md
discovered: 2026-08-14
discovered_at: 2026-08-14T14:31:13Z
promoted_from: [mcp:_sessions/mcp-2026-08-14.md:f2879718bb404c55]
---

# board-consolidate apply instructions omit the session selector required by session-scoped plans

## Done when

- [x] A plan previewed with `session` can be applied with its `plan_id` alone,
  as the Codex consolidate protocol instructs.
- [x] Repeating the same `session` selector remains supported and applies only
  that scratch source.
- [x] Changed scratch or canonical input still returns `plan_stale`.
- [x] The core, MCP adapter, skill instructions, and tool schema describe and
  verify the same session-scope behavior.

## Evidence

> A preview scoped to session mcp-2026-08-14.md returned plan_id 8de2481a72c44433f8df0e235911c9bef974a5265e12e9474356a28cc13ac2fb. Following Codex protocol step 5 with only apply caused plan_stale because the MCP adapter replanned with session null. The apply step and tool description do not state that the caller must repeat the preview selector.

## Comments

- **codex** 2026-08-14T14:32:14Z: Claimed after a dogfood preview/apply failure. Scope: preserve the session selector across apply instructions and verify session-scoped promotion end to end.
- **codex** 2026-08-14T14:44:18Z: Red/green promotion tests complete. Focused pipeline, MCP schema, documentation coherence, and the full 20-suite maintained validation pass. Merged-main and closeout evidence remain pending.

## Resolution evidence

- Session-scoped preview applies with its unchanged plan id alone; explicit same-session apply remains supported.
- Scratch and canonical changes return `plan_stale`; unrelated linked scratch cannot redirect scoped apply.
- The focused pipeline passes 20 checks, and the maintained repository suite passes 20 of 20 suites.
- Pull request #130 merged as `350c161`; merged-main run 31811404475 passed.
- Dated alignment evidence: `docs/evidence/2026-08-14-b068-promotion-session-scope.md`.
