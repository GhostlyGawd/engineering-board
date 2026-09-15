---
id: B011
type: bug
status: resolved
needs: validate
priority: P2
title: Board Intake misses a confirmed workflow bug after the agent acknowledges it
affects: skills/board-intake/SKILL.md
discovered: 2026-09-09
discovered_at: 2026-09-09T17:09:08Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:c795bc6caa4e364f]
---

# Board Intake misses a confirmed workflow bug after the agent acknowledges it

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> After the owner exposed the cross-chat Q002 collision, the agent replied that it had only performed read-only inspection and would leave Q002 alone, then ended the turn without invoking Board Intake. This occurred even though repository instructions require findings to be captured as noticed and the Board Intake skill declares unexpected behavior as an automatic trigger. The owner had to ask `why didnt you just log that as a bug` before capture occurred.

## 2026-09-14 implementation acceptance

Owner: b011-owner-20260914, lead on behalf of bounded builder. Base 76197522a27fc6f6c1e2e3a45c83a6cecebc4fc6. Capture an acknowledged concrete workflow defect before ending the turn without requiring the user to request logging again, including read-only mistakes. Distinguish confirmed automatic scratch capture from speculative scans and canonical promotion authorization. Preserve deduplication, foreground preview/apply, project routing and failures. Verify confirmed/uncertain/duplicate/unavailable-capture cases.

Delivery: reviewed source fix via PR, Unreleased notes; no immutable release in this batch. Preserve unrelated worktrees and user changes. Independent correctness/workflow review and appropriate checks required. Evidence: docs/evidence/2026-09-14-workflow-bugs/. No product-effect claim.

## Verified source delivery

Scoped implementation acceptance is complete. PR #180 merged as 24c7237c440c78ad9148288e1fa177e0e002bcef. Independent source review PASS at ad6a885; runner correction independently rechecked at 34e5a97. Final full suite 24 pass/0 fail; PR CI 34930240580 and 34930244039 pass; merged-main CI 34930412370 passes. Merged source matches reviewed skills/tests and explicit-root contract checks pass. Evidence: docs/evidence/2026-09-14-workflow-bugs/ including initial/final logs and review. B020 was discovered and corrected during integration, not a released defect. F018 remains the separate versioned-release/installed-verification follow-up for B010/B011. No behavioral efficacy or installed-release claim. No unrelated observation or hypothesis is resolved by these checks; cost/time-to-outcome not measured.
