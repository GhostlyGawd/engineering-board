---
id: H106
type: hypothesis
status: rejected
title: Plan label controls export entitlement
claim_key: plan-label-controls-export-entitlement
claim_fingerprint: h-06885c92bc62828f
cluster_fingerprint: c-83434b5ef84853fa
graph_source_fingerprint: f018b5a331c9de8597258aa9d59cfd59871844bf6c2303ab5feacaa0ad27cbe0
pattern_ids: [P103]
confidence: medium
derived_from: [B105, B106]
affected_domains: [api, dashboard]
created: 2026-07-29
last_evaluated: 2026-07-29
revision: 2
---

## Proposed root cause

Documentation capitalization changes export authorization.

## Supporting evidence

- B105: The export incident includes subscription terminology.
- B106: The dashboard incident includes plan terminology.

## Alternative explanations

- The documentation label has no runtime effect.

## Counter-evidence

The guide is not a runtime authorization input.

## Confidence basis

The claim used lexical similarity without a runtime relationship.

## Falsifier

The documentation file is an authorization data source.

## Outcome history

- 2026-07-29: status `proposed` via explicit apply by `d1-fixture-builder`; evidence [B105, B106]; Created from lexical similarity.
- 2026-07-29: status `rejected` via explicit apply by `d1-fixture-builder`; evidence [B105, B106]; No runtime relationship exists.
