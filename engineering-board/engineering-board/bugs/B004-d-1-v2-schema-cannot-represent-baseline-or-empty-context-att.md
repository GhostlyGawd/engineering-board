---
id: B004
type: bug
status: resolved
needs: validate
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

## Independent verification

Builder /root/build_absent_memory committed 19edddcb84c6d5fc3bc57ffb780f841c4ad92073; /root/audit_evaluation independently passed this revision. 28 tests passed; all 48 prepared arms validated and recorded (24 baseline, 6 empty context, 18 cluster evaluations); 54 populated-context adversarial checks rejected null/unsupplied/status-mismatch evaluations. Complete v1 score matched parent. Integrated as 10fec3e. B005-B007 remain outstanding.

## Resolution evidence

Independent verifier passed builder commit 19edddc (integrated as 10fec3e); all 48 prepared arms, 54 adversarial populated checks, v1 comparison and 28 evaluation tests passed. Integrated full suite passed 21/21. Source fix complete; installation/release remains pending with F002 on hold for B005-B007.
