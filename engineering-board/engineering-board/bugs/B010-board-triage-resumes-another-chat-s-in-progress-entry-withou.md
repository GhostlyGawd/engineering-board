---
id: B010
type: bug
status: in_progress
needs: tdd
priority: P2
title: Board triage resumes another chat's in-progress entry without verifying claim ownership
affects: skills/board-triage/SKILL.md
discovered: 2026-09-09
discovered_at: 2026-09-09T17:07:59Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:4c8fea955006aecd]
---

# Board triage resumes another chat's in-progress entry without verifying claim ownership

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> In a new chat, `lets continue dogfooding engineering board` caused the agent to select Q002 solely because board_status reported it in_progress, begin Q002 research, and only stop after the owner said: `wait why are you doing this at the same time as my other chat`. The agent had not verified the active claim owner or asked whether the cross-chat entry belonged to this session.

## 2026-09-14 implementation acceptance

Owner: b010-owner-20260914, lead on behalf of bounded builder. Base 76197522a27fc6f6c1e2e3a45c83a6cecebc4fc6. Before resuming work, verify exact current session claim ownership; other-owner/unknown/stale states never authorize takeover or status reset. Claim before research/implementation, preserve one owned entry per session, allow unrelated sessions and safe read-only overview. Align MCP and shell guidance. Verify own/foreign/missing/stale and contention scenarios against actual claim tools.

Delivery: reviewed source fix via PR, Unreleased notes; no immutable release in this batch. Preserve unrelated worktrees and user changes. Independent correctness/workflow review and appropriate checks required. Evidence: docs/evidence/2026-09-14-workflow-bugs/. No product-effect claim.
