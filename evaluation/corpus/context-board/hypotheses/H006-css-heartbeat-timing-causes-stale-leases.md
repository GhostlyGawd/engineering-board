---
id: H006
type: hypothesis
status: rejected
title: CSS heartbeat timing causes stale leases
claim_key: css-heartbeat-timing-causes-stale-leases
claim_fingerprint: h-3083d5663124aae8
cluster_fingerprint: c-bc48b2b5a563e192
graph_source_fingerprint: 30b4a44a230b5e865246c2659709b5422d062d50803d233df0cd899141137671
pattern_ids: [P002]
confidence: medium
derived_from: [B003, B004]
affected_domains: [worker]
created: 2026-07-29
last_evaluated: 2026-07-29
revision: 2
---

## Proposed root cause

Interface animation timing changes worker lease freshness.

## Supporting evidence

- B003: The evidence shares this canonical failure pattern.
- B004: The evidence shares this canonical failure pattern.

## Alternative explanations

- The symptoms are independent local defects.

## Counter-evidence

None found during this cited review.

## Confidence basis

Two repository domains or paths share one canonical pattern.

## Falsifier

The paths use independent boundaries and fail for unrelated reasons.

## Outcome history

- 2026-07-29: status `proposed` via explicit apply by `d1-fixture-builder`; evidence [B003, B004]; Created from the selected deterministic cluster; not confirmed.
- 2026-07-29: status `rejected` via explicit apply by `d1-fixture-builder`; evidence [B003, B004]; Canonical evidence shows that the lexical match does not share the runtime cause.
