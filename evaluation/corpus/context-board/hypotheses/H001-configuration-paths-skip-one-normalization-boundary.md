---
id: H001
type: hypothesis
status: proposed
title: Configuration paths bypass one normalization boundary
claim_key: configuration-paths-skip-one-normalization-boundary
claim_fingerprint: h-e95adce9e131310d
cluster_fingerprint: c-4c7642945faa74a2
graph_source_fingerprint: 30b4a44a230b5e865246c2659709b5422d062d50803d233df0cd899141137671
pattern_ids: [P001]
confidence: medium
derived_from: [B001, B002]
affected_domains: [service]
created: 2026-07-29
last_evaluated: 2026-07-29
revision: 1
---

## Proposed root cause

Configuration values enter through paths that do not share one normalization boundary.

## Supporting evidence

- B001: The evidence shares this canonical failure pattern.
- B002: The evidence shares this canonical failure pattern.

## Alternative explanations

- The symptoms are independent local defects.

## Counter-evidence

None found during this cited review.

## Confidence basis

Two repository domains or paths share one canonical pattern.

## Falsifier

The paths use independent boundaries and fail for unrelated reasons.

## Outcome history

- 2026-07-29: status `proposed` via explicit apply by `d1-fixture-builder`; evidence [B001, B002]; Created from the selected deterministic cluster; not confirmed.
