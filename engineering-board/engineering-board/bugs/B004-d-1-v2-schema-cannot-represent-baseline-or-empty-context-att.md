---
id: B004
type: bug
status: in_progress
needs: tdd
priority: P1
title: D.1 v2 schema cannot represent baseline or empty-context attempts
affects: evaluation/memory-evaluation-response.schema.json
discovered: 2026-09-09
discovered_at: 2026-09-09T13:17:04Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:7944536504e9620d]
---

# D.1 v2 schema cannot represent baseline or empty-context attempts

## Done when

- [ ] Baseline and empty-context v2 responses use null evaluation and false before-local classification.
- [ ] Recorder rejects fabricated evaluations for absent memory.
- [ ] Schema accepts surfaced cluster IDs as well as hypotheses and Learnings.
- [ ] Real prepared-run regression tests pass with v1 behavior preserved; independent verifier passes the committed fix.

## Evidence

> Independent audit of 151a356: response schema requires object memory_evaluation; recorder requires null and false for baseline, and rejects null for empty context. The locked corpus generates six empty-context arms. Done when response schema and recorder allow null for absent memory, forbid claiming evaluation for absent memory, accept every supplied eligible memory kind, and regression tests cover baseline and empty-context recording without changing v1.

## Comments

- **builder-b004-team-pilot** 2026-09-09T13:17:04Z: Lead acquired claim on behalf of separate builder session. Scope: absent-memory response/recording coherence and memory ID shape only; scoring and evidence-method changes are separate audit follow-ups.
- **independent-audit-triage** 2026-09-09T13:18:18Z: Release blocker for the D.1 v2 contract. Independent audit reproduced failure despite the prior passing test suite.
