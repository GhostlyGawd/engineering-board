---
id: B005
type: bug
status: resolved
needs: validate
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
- **builder-d1-b005-20260909** 2026-09-09T13:47:24Z: Builder phase committed bc40217, 30 evaluation tests pass. Awaiting independent review at isolated pinned revision while same builder advances sequentially to B006. Not resolved.
- **builder-d1-b005-fix-20260909** 2026-09-09T13:50:31Z: Independent verifier requires correction: raw 0 equals recorded False in Python payload comparison; review cannot represent no-local-correction responses. Add type-sensitive binding and explicit unavailable no-local review, then reverify. Prior 30 tests green did not establish these criteria.
- **builder-d1-b005-fix-20260909** 2026-09-09T13:53:26Z: Revised commit 782594a addresses numeric/bool binding and truthful no-local correction representation; 33 evaluation tests pass. Independent recheck pending.

## Independent reverification

/root/verify_measurement passed 782594a59955d844c937af37191658320189a1f5. Record/score probes reject numeric and nonfinite JSON in place of bool; no-local response remains retained, null ordering rate and zero success; contradictory no-local declarations reject. Mixed healthy success plus no-local stays unavailable. Semantic correction selection remains attributed reviewer judgment.

## Final source acceptance

Retained exact raw responses, checksums, frozen rubric and named semantic reviewer spans now support ordering classifications. Legacy bare flags never count; invalid binding, duplicate keys, numeric/bool substitution and overlapping/early corrections are tested. No-local correction remains unavailable. Independent final pass at 72ebeea; integrated 21 suites/39 evaluation tests pass.

Evidence: docs/evidence/2026-09-09-d1-measurement-corrections.md. Live pilot and release decision are separate F004 follow-up; no product-effect claim.
