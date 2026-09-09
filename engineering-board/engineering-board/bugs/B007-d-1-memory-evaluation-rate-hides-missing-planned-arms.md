---
id: B007
type: bug
status: open
needs: tdd
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
