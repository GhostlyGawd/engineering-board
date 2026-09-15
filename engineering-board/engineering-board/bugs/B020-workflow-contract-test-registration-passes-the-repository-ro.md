---
id: B020
type: bug
status: resolved
needs: validate
priority: P2
title: Workflow contract test registration passes the repository root as a unittest selector
affects: tests/run-all.sh
discovered: 2026-09-15
discovered_at: 2026-09-15T04:48:02Z
promoted_from: [mcp:_sessions/mcp-2026-09-15.md:6c9634eb48f8e96d]
---

# Workflow contract test registration passes the repository root as a unittest selector

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> During B010/B011 integration at ad6a885, all 23 existing suites passed but both newly registered Python scripts failed because run-all appends ROOT, which unittest.main interpreted as a test selector. Focused direct execution passed. Lead will fix the runner wrapper within this batch and request independent recheck; not a released regression.

## Integration correction acceptance

Lead-owned correction within the existing B010/B011 shared test-runner assignment. Both focused Python checks must run through tests/run-all.sh with its appended repository-root argument, including invocation from another working directory. Required evidence: independent wrapper review, focused execution, full portable suite and CI. Fix 34e5a9798f932d04c63f85894636d8b8d548a6f3 changes only test registration/wrapper. No runtime change or released regression.

## Verified source delivery

Scoped implementation acceptance is complete. PR #180 merged as 24c7237c440c78ad9148288e1fa177e0e002bcef. Independent source review PASS at ad6a885; runner correction independently rechecked at 34e5a97. Final full suite 24 pass/0 fail; PR CI 34930240580 and 34930244039 pass; merged-main CI 34930412370 passes. Merged source matches reviewed skills/tests and explicit-root contract checks pass. Evidence: docs/evidence/2026-09-14-workflow-bugs/ including initial/final logs and review. B020 was discovered and corrected during integration, not a released defect. F018 remains the separate versioned-release/installed-verification follow-up for B010/B011. No behavioral efficacy or installed-release claim. No unrelated observation or hypothesis is resolved by these checks; cost/time-to-outcome not measured.
