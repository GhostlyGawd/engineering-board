---
id: H105
type: hypothesis
status: rejected
title: Clock icon pause causes lease expiry
claim_key: clock-icon-pause-causes-lease-expiry
claim_fingerprint: h-94f27a7820b467f3
cluster_fingerprint: c-7983388cf203f97f
graph_source_fingerprint: f018b5a331c9de8597258aa9d59cfd59871844bf6c2303ab5feacaa0ad27cbe0
pattern_ids: [P102]
confidence: medium
derived_from: [B103, B104]
affected_domains: [recovery, worker]
created: 2026-07-29
last_evaluated: 2026-07-29
revision: 2
---

## Proposed root cause

A dashboard icon animation changes worker lease expiration.

## Supporting evidence

- B103: The renewal incident includes time terminology.
- B104: The recovery incident includes time terminology.

## Alternative explanations

- The animation is independent presentation behavior.

## Counter-evidence

The animation does not read or write lease state.

## Confidence basis

The claim used lexical similarity without a runtime relationship.

## Falsifier

The animation mutates a worker time source.

## Outcome history

- 2026-07-29: status `proposed` via explicit apply by `d1-fixture-builder`; evidence [B103, B104]; Created from lexical similarity.
- 2026-07-29: status `rejected` via explicit apply by `d1-fixture-builder`; evidence [B103, B104]; No runtime relationship exists.
