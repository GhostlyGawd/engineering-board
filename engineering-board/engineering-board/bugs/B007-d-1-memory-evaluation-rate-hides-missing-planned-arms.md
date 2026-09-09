---
id: B007
type: bug
status: resolved
needs: validate
priority: P2
title: D.1 memory-evaluation rate hides missing planned arms
affects: evaluation/harness.py
discovered: 2026-09-09
discovered_at: 2026-09-09T13:18:18Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:28c8efe5cd69d890]
---

# D.1 memory-evaluation rate hides missing planned arms

## Done when

- [ ] Pin evaluation version and eligible population before observing attempts.
- [ ] Report missing arms, completeness and positive-only scope explicitly; unavailable is distinct from zero or success.
- [ ] Cover incomplete, mixed-version, v1-only and complete runs in regression tests.

## Evidence

> Independent audit at 151a356: one successful positive v2 attempt plus 47 missing reference arms yields eligible_context_arms 1 and rate_percent 100. Eligibility depends on recorded schema version rather than planned contract. Complete when eligibility/version is pinned before observations and report labels scope, completeness, missing arms and unavailable rates; partial/mixed/v1-only/complete tests required.

## Comments

- **builder-d1-b007-20260909** 2026-09-09T13:53:26Z: Same builder now owns planned version/eligible population, truthful partial/mixed/legacy reports and all-reference completeness separate from observed safeguards. No thresholds changed.
- **builder-d1-b007-20260909** 2026-09-09T14:00:15Z: Combined commit 51d4fb7 ready for independent review. 37 evaluation tests and two final missing-negative/historical-manifest checks pass; full suite running. Configuration pins version and population; partial/mixed/invalid/unverified/no-local have explicit unavailable rate reasons.
- **builder-d1-b007-fix-20260909** 2026-09-09T14:02:22Z: Independent verifier reproduced denominator shrink at 51d4fb7: delete failed trial from trials+eligible keys and recompute manifest digest; remaining frozen inputs still show original cohort, but report falsely becomes 100/complete. Add complete-cohort binding/check against retained workspace inventory; reverify before integration.
- **builder-d1-b007-fix-20260909** 2026-09-09T14:05:04Z: Correction commit 72ebeea checks exact retained workspace directory/input cohort independently, rejects omitted/redirected/linked inputs and changed population. Three targeted regressions pass; 39-test evaluation suite running. Independent final recheck assigned.

## Final source acceptance

Evaluation version and eligible population are frozen at preparation and checked against the complete retained workspace input cohort. Missing/mixed/invalid/unreviewed/no-local cases have unavailable rates and reasons; omissions of failed positive or negative control reject. Independent72ebeea pass; integrated21 suites/39 evaluation tests pass.

Evidence: docs/evidence/2026-09-09-d1-measurement-corrections.md. Live pilot and release decision are separate F004 follow-up; no product-effect claim.
