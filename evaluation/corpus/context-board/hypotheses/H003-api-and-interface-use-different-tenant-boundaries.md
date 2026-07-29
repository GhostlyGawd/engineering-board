---
id: H003
type: hypothesis
status: proposed
title: API and interface use different tenant boundaries
claim_key: api-and-interface-use-different-tenant-boundaries
claim_fingerprint: h-4c65d91754902acd
cluster_fingerprint: c-d8be5014327a544e
graph_source_fingerprint: 30b4a44a230b5e865246c2659709b5422d062d50803d233df0cd899141137671
pattern_ids: [P003]
confidence: medium
derived_from: [B005, B006]
affected_domains: [api, ui]
created: 2026-07-29
last_evaluated: 2026-07-29
revision: 1
---

## Proposed root cause

The API and interface derive tenant scope from different ownership boundaries.

## Supporting evidence

- B005: The evidence shares this canonical failure pattern.
- B006: The evidence shares this canonical failure pattern.

## Alternative explanations

- The symptoms are independent local defects.

## Counter-evidence

None found during this cited review.

## Confidence basis

Two repository domains or paths share one canonical pattern.

## Falsifier

The paths use independent boundaries and fail for unrelated reasons.

## Outcome history

- 2026-07-29: status `proposed` via explicit apply by `d1-fixture-builder`; evidence [B005, B006]; Created from the selected deterministic cluster; not confirmed.
