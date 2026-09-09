# Direct memory-application review ledger

Status: completed descriptive review of the synthetic pilot. No causal benefit
is established by this ledger.
This ledger distinguishes direct Learning use from the product's existing
hypothesis-based outcome accounting. It does not backfill H records or change
the product counter.

One record per observed candidate application, including rejected or irrelevant
memory. Complete after blind patch judgments and then trace inspection.

| Field | Required observation |
|---|---|
| Anonymous arm and stage | Review packet id; patch verdict timestamp before trace exposure |
| Source | Exact L/H/history source and retained digest; unavailable if not retrieved |
| Retrieval evidence | Trace event/quote showing delivery, or absent/failed |
| Application evidence | Executed check, patch or test linked to the source; citation alone insufficient |
| Disposition | Applied, narrowed, rejected, irrelevant, or indeterminate with evidence |
| Outcome | Independent correctness/coverage result, including adverse effect |
| Causal limit | Alternative explanation from visible code/docs; no counterfactual benefit inferred from one action |
| Ordering | Observable delivery/action timestamps only; internal reasoning not measured |
| Review | Reviewer, artifact hashes, uncertainty and inferred condition/confidence |

Keep source delivery, action-supported use and incremental benefit separate.
The third requires a comparison; the first two do not establish it.

## Reviewed applications

Patch judgments were committed at `101ec714` before trace exposure. The fresh
reviewer inferred no condition from patches, then explicitly updated inference
after partially blinded trace inspection. All eight memory-available arms
actually read memory: four via HISTORY.md and four via MCP. The four ordinary
arms had no observed historical content delivery. No Board Markdown body was
directly read. Record-by-record source scope, quotes, event ids, line references,
reviewer uncertainty and condition inference are in [TRACE-REVIEW.json](TRACE-REVIEW.json).
Exact inputs/source digests remain in the frozen campaign manifest and each
arm's input inventory; outputs are bound by the start/end receipts.

| Arm / source | Delivery and disposition | Action evidence and limit |
|---|---|---|
| `0534b4aa6fa44e4e` / L101 history | Full Learning and B101/B102 delivered | Sibling enumeration, both retry repairs and heartbeat-zero testing align with the procedure; no explicit causal attribution. Trace items 3, 5, 6, 10, 11. |
| `75bd98ebef9d4419` / L101 Board | MCP summary then full L101; B records referenced, not fetched | Both retry consumers repaired and sentinel tested; action-aligned use, not proof of reliance. Trace items 2, 5, 7 and subsequent edit/tests. |
| `86633e4fc7f54bd6` / L102 history | Full currency-only procedure and scope exclusions delivered | Both sensor ingestion paths repaired without payment rounding; non-application is consistent with the boundary but not itself proof of use. |
| `bdb88ef7a0034ce1` / L102 Board | MCP summary, full L102 and both B sources | Explicitly identifies currency guidance as inapplicable, reads current contracts, repairs live/replay and leaves payment logic untouched. Action-supported boundary handling; current docs independently support the decision. |
| `1736655682d44fad` / H101 history | Full proposed mechanism, alternatives and falsifier delivered | Explicit historical-hypothesis reference plus executed before/after snapshots for both views. Local evaluation is supported; general causation or incremental benefit is not. |
| `a3fdbe22065a4868` / H101 Board | Proposed H summary and cluster delivered; full H/B records not fetched | Source inspection and direct export-order reproductions support local mutation. Full alternatives/falsifier delivery is not established; some final test output is absent. |
| `1a55ff5a65494e0f` / H102 history | Full proposed normalization theory and falsifier delivered | Explicit rejection plus independent local fixes. Source/baseline tests support the rejection; the prescribed fixed-id custom experiment did not execute after a Git-command failure. |
| `c33139a00c714707` / H102 Board | Proposed H summary and both B observations through MCP; full H not fetched | Rejects unsupported normalization and fixes two independent operations. Do not credit reading or executing the undelivered H falsifier. |

All eight memory arms passed four independent hidden checks. That outcome does
not make each aligned action a confirmed memory-caused benefit. The ordinary
retry and hypothesis repairs also passed. The ordinary precision repair
`836c4078663e4d83` explicitly noticed replay truncation and wrongly preserved it
as compatibility; this is not evidence that retrieval simply revealed an
otherwise unseen sibling. No H outcomes or production Learning counters were
backfilled from these synthetic applications.
