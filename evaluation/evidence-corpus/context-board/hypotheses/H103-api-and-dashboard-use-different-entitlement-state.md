---
id: H103
type: hypothesis
status: proposed
title: API and dashboard use different entitlement state
claim_key: api-and-dashboard-use-different-entitlement-state
claim_fingerprint: h-7d744061b7ebeceb
cluster_fingerprint: c-83434b5ef84853fa
graph_source_fingerprint: f018b5a331c9de8597258aa9d59cfd59871844bf6c2303ab5feacaa0ad27cbe0
pattern_ids: [P103]
confidence: medium
derived_from: [B105, B106]
affected_domains: [api, dashboard]
created: 2026-07-29
last_evaluated: 2026-07-29
revision: 1
---

## Proposed root cause

The API and dashboard read different representations of entitlement state.

## Supporting evidence

- B105: Export authorization reads an invoice snapshot.
- B106: The access badge reads a subscription projection.

## Alternative explanations

- One surface has an isolated stale cache.

## Counter-evidence

None found during this cited review.

## Confidence basis

Two product domains share one entitlement-state pattern.

## Falsifier

Both surfaces read the same authoritative entitlement representation.

## Outcome history

- 2026-07-29: status `proposed` via explicit apply by `d1-fixture-builder`; evidence [B105, B106]; Created from the selected deterministic cluster; not confirmed.
