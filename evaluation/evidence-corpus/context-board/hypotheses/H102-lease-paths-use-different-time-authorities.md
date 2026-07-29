---
id: H102
type: hypothesis
status: proposed
title: Lease paths use different time authorities
claim_key: lease-paths-use-different-time-authorities
claim_fingerprint: h-178c3f7bbcc788eb
cluster_fingerprint: c-7983388cf203f97f
graph_source_fingerprint: f018b5a331c9de8597258aa9d59cfd59871844bf6c2303ab5feacaa0ad27cbe0
pattern_ids: [P102]
confidence: medium
derived_from: [B103, B104]
affected_domains: [recovery, worker]
created: 2026-07-29
last_evaluated: 2026-07-29
revision: 1
---

## Proposed root cause

Lease paths do not share one time authority.

## Supporting evidence

- B103: Renewal compares a stored wall-clock expiration.
- B104: Recovery compares elapsed runtime.

## Alternative explanations

- The resumed worker misses one renewal callback.

## Counter-evidence

None found during this cited review.

## Confidence basis

Two lifecycle paths share one time-authority pattern.

## Falsifier

Both paths derive freshness from the same clock contract.

## Outcome history

- 2026-07-29: status `proposed` via explicit apply by `d1-fixture-builder`; evidence [B103, B104]; Created from the selected deterministic cluster; not confirmed.
