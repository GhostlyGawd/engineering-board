> DRAFT — FULL COMPLIANCE CHECK NOT COMPLETE

# Root-cause hypothesis schema

Root-cause hypotheses are durable interpretations of deterministic cluster
facts. They are Markdown so humans and agents can inspect, review, reject, and
revisit the reasoning.

```yaml
---
id: H001
type: hypothesis
status: proposed
title: Short explanation of the suspected shared cause
claim_key: shared-owner-is-implicit
claim_fingerprint: h-0123456789abcdef
cluster_fingerprint: c-0123456789abcdef
graph_source_fingerprint: 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
pattern_ids: [P001]
confidence: medium
derived_from: [B001, B002]
affected_domains: [component-a, component-b]
supersedes: []
created: YYYY-MM-DD
last_evaluated: YYYY-MM-DD
revision: 1
---
```

Required fields:

| Field | Values | Meaning |
|---|---|---|
| `id` | `H###` | Stable hypothesis identity. |
| `type` | `hypothesis` | Distinguishes interpretation from observed entries. |
| `status` | `proposed`, `confirmed`, `weakened`, `rejected`, `split`, `merged` | Epistemic state or terminal lineage state. |
| `claim_key` | lowercase kebab-case | Human-readable stable claim key. |
| `claim_fingerprint` | `h-` plus 16 hex characters | Identity derived from the claim key and canonical pattern IDs. |
| `cluster_fingerprint` | `c-` plus 16 hex characters | Deterministic evidence cluster binding. |
| `graph_source_fingerprint` | SHA-256 hex | Canonical graph-source state reviewed for this revision. |
| `pattern_ids` | P### list | Canonical pattern identities represented by the cluster. |
| `confidence` | `low`, `medium`, `high` | Strength of the current explanation. never confirmation authority. |
| `derived_from` | entry IDs | Canonical evidence inspected. |
| `affected_domains` | list | Distinct engineering domains represented. |
| `created` | date | Initial proposal date. |
| `last_evaluated` | date | Most recent evidence review. |
| `revision` | positive integer | Applied record revision. |

Required body sections:

- `## Proposed root cause`
- `## Supporting evidence`
- `## Alternative explanations`
- `## Counter-evidence`
- `## Confidence basis`
- `## Falsifier`
- `## Outcome history`

Authority:

- A graph cluster may justify `status: proposed`.
- Recurrence, domain diversity, topology, or model confidence cannot set
  `status: confirmed`.
- Confirmation requires explicit investigation or fix-outcome evidence cited
  in `## Outcome history`.
- Rejection preserves the file and appends the rejecting evidence. Rejected
  hypotheses are negative memory and must not be silently deleted.
- New evidence may weaken, split, merge, or supersede a hypothesis. Preserve
  the prior outcome history.
- A proposal must cite every current cluster member exactly once and include
  at least one alternative and one observable falsifier.
- A matching rejected claim blocks a new proposal. Reopen that H### only with
  retained evidence plus at least one new current-cluster evidence ID.
- Mutations use content-bound preview/apply tokens. Apply revalidates graph and
  hypothesis inventory fingerprints and refuses stale plans.
