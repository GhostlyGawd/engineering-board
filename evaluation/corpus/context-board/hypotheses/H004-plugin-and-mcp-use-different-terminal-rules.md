---
id: H004
type: hypothesis
status: proposed
title: Plugin and MCP use different terminal rules
claim_key: plugin-and-mcp-use-different-terminal-rules
claim_fingerprint: h-897d80746afeb973
cluster_fingerprint: c-4efe931269ad13db
graph_source_fingerprint: 30b4a44a230b5e865246c2659709b5422d062d50803d233df0cd899141137671
pattern_ids: [P004]
confidence: medium
derived_from: [B007, B008]
affected_domains: [mcp, plugin]
created: 2026-07-29
last_evaluated: 2026-07-29
revision: 1
---

## Proposed root cause

Plugin and MCP adapters translate one lifecycle model with different terminal-state rules.

## Supporting evidence

- B007: The evidence shares this canonical failure pattern.
- B008: The evidence shares this canonical failure pattern.

## Alternative explanations

- The symptoms are independent local defects.

## Counter-evidence

None found during this cited review.

## Confidence basis

Two repository domains or paths share one canonical pattern.

## Falsifier

The paths use independent boundaries and fail for unrelated reasons.

## Outcome history

- 2026-07-29: status `proposed` via explicit apply by `d1-fixture-builder`; evidence [B007, B008]; Created from the selected deterministic cluster; not confirmed.
