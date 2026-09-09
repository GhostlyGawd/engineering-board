---
id: H001
type: hypothesis
status: rejected
title: Synthetic boundary normalization removes capability markers
claim_key: capability-marker-loss-shared-boundary
claim_fingerprint: h-281350af3da80430
cluster_fingerprint: c-9cf4901983090fce
graph_source_fingerprint: 81989b0f9bd0bc278e51282748fd04d18f4d155dc1084e3aa88f3a5c78ed5cb2
pattern_ids: [P001]
confidence: low
derived_from: [B001, B002, B003, O001]
affected_domains: [tests]
created: 2026-09-09
last_evaluated: 2026-09-09
revision: 4
---

## Proposed root cause

A shared synthetic normalization boundary removes capability markers before three independent test paths consume them.

## Supporting evidence

- B001: Parser path exhibits the canonical synthetic marker-loss pattern.
- B002: Validator path independently exhibits the same canonical pattern.
- B003: Reporter path independently exhibits the same canonical pattern.

## Alternative explanations

- Each synthetic path independently drops the marker.

## Counter-evidence

None found during this cited review.

## Confidence basis

Three canonical-pattern entries form one dense cluster, but no real product behavior is asserted.

## Falsifier

A synthetic trace showing all three paths receive the marker after the shared boundary would falsify this hypothesis.

## Outcome history

- 2026-09-09: status `proposed` via explicit apply by `capability-sweep`; evidence [B001, B002, B003]; Created from the selected deterministic cluster; not confirmed.
- outcome-json: {"actor":"capability-sweep","context_reference":null,"context_used":false,"entry_id":"B001","event_id":"out-481f1c0218a712b2","evidence_ids":["B001"],"fix_result":"inconclusive","fix_summary":"Synthetic sweep recorded the workflow result without asserting a real product fix.","hypothesis_disposition":"unchanged","hypothesis_id":"H001","observed_until":"2026-09-08"}
- 2026-09-09: status `weakened` via explicit apply by `codex-capability-lab`; evidence [B001]; Capability-lab token-only apply reproduction. Rebound graph 610e2820cf26 to 6160522ab2b1.
- 2026-09-09: status `rejected` via explicit apply by `codex-capability-q001-20260908`; evidence [B001, B002, B003, O001, Q001]; Q001 established that B001-B003 are completed synthetic placeholders whose named files do not exist. O001 records only a completed MCP capability sweep, not a marker-loss trace. The cluster links therefore come from synthetic tags and paths, not evidence of a shared normalization boundary. Rebound graph 6160522ab2b1 to 81989b0f9bd0.
