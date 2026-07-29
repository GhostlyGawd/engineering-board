---
id: H104
type: hypothesis
status: proposed
title: Clients use different cache generations
claim_key: clients-use-different-cache-generations
claim_fingerprint: h-7d6bb56e0d4f5d9c
cluster_fingerprint: c-7615a70b60147de8
graph_source_fingerprint: f018b5a331c9de8597258aa9d59cfd59871844bf6c2303ab5feacaa0ad27cbe0
pattern_ids: [P104]
confidence: medium
derived_from: [B107, B108]
affected_domains: [cli, extension]
created: 2026-07-29
last_evaluated: 2026-07-29
revision: 1
---

## Proposed root cause

CLI and extension clients do not share one cache generation contract.

## Supporting evidence

- B107: The CLI index uses directory modification time.
- B108: The extension status uses a service generation.

## Alternative explanations

- One client misses an isolated refresh event.

## Counter-evidence

None found during this cited review.

## Confidence basis

Two client domains share one invalidation pattern.

## Falsifier

Both clients consume the same generation signal.

## Outcome history

- 2026-07-29: status `proposed` via explicit apply by `d1-fixture-builder`; evidence [B107, B108]; Created from the selected deterministic cluster; not confirmed.
