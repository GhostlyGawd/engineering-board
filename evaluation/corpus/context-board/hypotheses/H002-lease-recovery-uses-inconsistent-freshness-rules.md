---
id: H002
type: hypothesis
status: proposed
title: Lease recovery uses inconsistent freshness rules
claim_key: lease-recovery-uses-inconsistent-freshness-rules
claim_fingerprint: h-a43346bb099ce834
cluster_fingerprint: c-bc48b2b5a563e192
graph_source_fingerprint: 30b4a44a230b5e865246c2659709b5422d062d50803d233df0cd899141137671
pattern_ids: [P002]
confidence: medium
derived_from: [B003, B004]
affected_domains: [worker]
created: 2026-07-29
last_evaluated: 2026-07-29
revision: 1
---

## Proposed root cause

Lease claim and restart recovery use different freshness boundaries.

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
