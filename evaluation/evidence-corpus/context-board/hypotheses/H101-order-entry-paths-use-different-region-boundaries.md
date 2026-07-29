---
id: H101
type: hypothesis
status: proposed
title: Order entry paths use different region boundaries
claim_key: order-entry-paths-use-different-region-boundaries
claim_fingerprint: h-396891ad85d61115
cluster_fingerprint: c-53730b325de4f920
graph_source_fingerprint: f018b5a331c9de8597258aa9d59cfd59871844bf6c2303ab5feacaa0ad27cbe0
pattern_ids: [P101]
confidence: medium
derived_from: [B101, B102]
affected_domains: [admin, imports]
created: 2026-07-29
last_evaluated: 2026-07-29
revision: 1
---

## Proposed root cause

Order entry paths do not share one canonical region-code boundary.

## Supporting evidence

- B101: The scheduled path preserves the supplied value.
- B102: The administrator path rewrites the supplied value.

## Alternative explanations

- The partner batch contains unrelated invalid orders.

## Counter-evidence

None found during this cited review.

## Confidence basis

Two entry paths share one payload pattern.

## Falsifier

Both paths use the same canonicalizer before validation.

## Outcome history

- 2026-07-29: status `proposed` via explicit apply by `d1-fixture-builder`; evidence [B101, B102]; Created from the selected deterministic cluster; not confirmed.
