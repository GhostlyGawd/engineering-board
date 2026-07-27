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
cluster_id: C001
patterns: [failure-mode]
confidence: medium
derived_from: [B001, B002]
affected_domains: [component-a, component-b]
created: YYYY-MM-DD
last_evaluated: YYYY-MM-DD
---
```

Required fields:

| Field | Values | Meaning |
|---|---|---|
| `id` | `H###` | Stable hypothesis identity. |
| `type` | `hypothesis` | Distinguishes interpretation from observed entries. |
| `status` | `proposed`, `confirmed`, `weakened`, `rejected` | Epistemic state, not workflow state. |
| `cluster_id` | `C###` | Deterministic cluster interpreted by this hypothesis. |
| `patterns` | list | Normalized failure modes represented by the cluster. |
| `confidence` | `low`, `medium`, `high` | Strength of the current explanation; never confirmation authority. |
| `derived_from` | entry IDs | Canonical evidence inspected. |
| `affected_domains` | list | Distinct engineering domains represented. |
| `created` | date | Initial proposal date. |
| `last_evaluated` | date | Most recent evidence review. |

Required body sections:

- `## Proposed root cause`
- `## Supporting evidence`
- `## Alternative explanations`
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
