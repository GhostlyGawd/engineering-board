---
id: B005
type: bug
status: in_progress
needs: tdd
priority: P1
title: D.1 before-local metric has no preserved ordering evidence
affects: evaluation/harness.py
discovered: 2026-09-09
discovered_at: 2026-09-09T13:18:18Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:cb81421d9c1dcfe6]
---

# D.1 before-local metric has no preserved ordering evidence

## Done when

- [ ] Define an evidence-backed ordering rubric and retain response or sequence evidence supporting every classification.
- [ ] Unsupported supplied flags cannot be reported as verified ordering success.
- [ ] Adversarial tests cover contradictory or missing evidence; any changed evaluation target receives an owner decision.

## Evidence

> Independent audit at 151a356: _validate_attempt only type-checks memory_evaluation_before_local; score_run counts it. A true flag with classification_evidence stating correction came first is accepted. Response object has no sequence evidence and serialization sorts keys. Complete when a defined review rubric binds classification to retained response/sequence evidence, distinguishes reviewer annotation from verified ordering, and adversarial tests prevent unsupported success; any metric target change requires an explicit owner decision.

## Comments

- **independent-audit-triage** 2026-09-09T13:18:18Z: Release blocker for the D.1 v2 contract. Independent audit reproduced failure despite the prior passing test suite.
- **builder-d1-b005-20260909** 2026-09-09T13:39:55Z: Lead claims on behalf of measurement builder; approved correction cycle begins with preserved response evidence and frozen ordering rubric, then sequential B006/B007. Independent verifier assigned; no live experiments or metric target changes.
