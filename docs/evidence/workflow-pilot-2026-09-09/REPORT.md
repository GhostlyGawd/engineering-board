# Workflow-value pilot — 2026-09-09

Status: execution and staged semantic review complete; final corrected-report
check and integration pending.

## Finding

Board-assisted and manually selected-history arms each produced four complete
repairs out of four. Ordinary repository work produced three. This is a small
signal worth investigating for historical memory access, **not evidence of an
Engineering Board-specific correctness advantage over equivalent selected
history**. The tasks were authored synthetic examples, not sampled customer
incidents, and each condition ran only once per case.

The one incomplete ordinary repair noticed the sibling replay defect but left
it unchanged as presumed compatibility. That is an incorrect scope decision
against the visible API contract, not simply failure to discover related code.
Both history conditions repaired it. One contrasting execution per condition
does not establish why the decisions differed.

This result supports the central caution in the owner's product-value review:
working memory infrastructure and observed use do not yet establish reliable
incremental engineering benefit or willingness to pay. The previous D.1 source
corrections made a narrower measurement contract trustworthy; they did not
themselves establish product value. This workflow pilot provides retained task
outcomes, but does not turn the historical failed first-cause gate into a pass.

## Design and execution

See [frozen protocol](campaign-v2/study-documents/0-PROTOCOL.md) and
[independent acceptance](FINAL-ACCEPTANCE.md). Four fresh stdlib Python cases
covered two procedural Learning situations and two proposed-hypothesis
situations, including irrelevant-scope and wrong-shared-cause controls.
Each case had ordinary, selected-history and Board-assisted conditions.

The history comparator included the same synthesized guidance and incident
facts as the Board, not only raw logs. It was manually curated; selection effort
was not measured. The Board condition used explicit, optional MCP availability
instructions and the installed 1.13.5 launcher. This was assisted retrieval,
not a natural installation/discovery study. Shared model/client/tools/starting
repository contracts and a 180-second per-arm limit were pinned before launch.

- Source: `3f256bf5949fdfaee39fb699181bc7b5497a7048`.
- Client: Codex CLI 0.153.4; model alias `gpt-5.6-sol`, reasoning `medium`.
  The alias does not pin unobservable provider weights.
- Prepared manifest SHA-256:
  `977a6fba9682798a48934ef9d32c359a0ec7598a9fa0ba0bf9a6151390335bf4`.
- Frozen acceptance committed and pushed at `8a14c09` before any live arm.
- Twelve of twelve arms completed; no timeout, client failure, reported trace
  violation, operator intervention, coaching, extension or retry.
- All twelve emitted a nonterminal configuration warning about the experimental
  `skip_host_skill_discovery` feature. This is not a claim of zero client warnings
  or proof that effective host isolation was complete.
- Total measured invocation wall time: 960.3 seconds (16.0 minutes). This
  excludes fixture design, setup, review and integration effort.
- All 22 deterministic CI suites passed on the frozen revision, including the
  39 existing evaluation tests and seven new runner tests.

## Correctness and elapsed time

Each cell shows independently graded checks passed out of four, then total
invocation seconds. Checks overlap semantically; they are not independent
samples and are not a population success-rate estimate.

| Synthetic task | Ordinary | Selected history | Board-assisted |
|---|---:|---:|---:|
| Zero retries / preview compatibility | 4/4 · 69.3s | 4/4 · 83.2s | 4/4 · 80.8s |
| Sensor precision / replay scope | 2/4 · 58.7s | 4/4 · 93.1s | 4/4 · 89.0s |
| Catalog read-only views / shared mutation | 4/4 · 71.4s | 4/4 · 91.7s | 4/4 · 84.8s |
| CSV and identifier lookup / wrong shared cause | 4/4 · 87.3s | 4/4 · 63.5s | 4/4 · 87.6s |
| Complete task repairs | 3/4 | 4/4 | 4/4 |

The blinded static reviewer judged eleven repairs complete and the same
ordinary precision arm incomplete before seeing traces, graders or condition
mapping. Its judgments were committed at `101ec714` before trace-packet
creation. No condition was inferred from the patch-only packets. Hidden checks
agreed: arm `836c4078663e4d83` failed replay preservation and no-quantization
checks. Its shorter time is not time to a complete solution.

Mean invocation time was 71.7s ordinary, 82.9s selected history and 85.6s Board.
These single-run timings include host/tool startup and provider variability.
They do not isolate investigation time and do not demonstrate time saved.

## Usage and overhead

All twelve receipts included provider-reported usage. These are cumulative
input tokens across model requests, including cached input, **not** distinct
prompt size or dollars. Execution/MCP counts deduplicate started/completed events
by item id and exclude file-change items, which are reported separately. Neither
is the runner's raw tool-event count or a universal count of all model actions.

| Across four arms per condition | Ordinary | Selected history | Board-assisted |
|---|---:|---:|---:|
| Input tokens, including cached | 279,846 | 294,815 | 392,059 |
| Cached input tokens | 226,816 | 215,552 | 307,840 |
| Input minus cached input | 53,030 | 79,263 | 84,219 |
| Output tokens | 6,784 | 7,910 | 8,382 |
| Distinct execution/MCP calls | 17 | 20 | 37 |
| File-change items | 5 | 4 | 4 |

Board added visible interaction and input-token overhead in this sample without
improving correctness over selected history. Billing, preparation, manual
selection and review effort were not measured, so no cost-effectiveness or
return-on-investment claim follows. Caching makes input-token totals especially
unsuitable as a direct monetary-cost comparison.

## Memory-use interpretation

The independent [trace review](TRACE-REVIEW.json) records actual MCP retrieval in
all four Board arms, direct HISTORY.md reads in all four history arms, and no
historical delivery in the four ordinary arms. No Board Markdown body was
directly read. All grader outcomes agree with the committed patch judgments.

The useful Learning arms repaired both retry consumers and preserved the
different heartbeat-zero contract. The irrelevant Learning Board arm explicitly
rejected applying currency guidance to sensor ingestion. Those actions are
consistent with appropriate memory use, but current source and docs also
support them. The hypothesis arms used or rejected proposed mechanisms against
current code; none requires forced systemic confirmation to count as useful.

Importantly, the two Board hypothesis arms received summaries but did not fetch
the full H alternatives/falsifiers. Selected history delivered those full
documents. Available information parity therefore does not mean identical
information was actually delivered. Do not credit the Board arms with reading
or executing an undelivered falsifier. This makes a discoverable full-H reading
route a concrete follow-up, not a new success counter.

The reviewer also distinguished commands written from commands executed. Some
custom probes were skipped after failed Git checks. For the Board catalog arm,
a newline-separated final shell command retained source output but not the
earlier unittest/compile reports; the last command's exit zero does not prove
those earlier checks passed. Its independent hidden grade remains 4/4, but
the candidate's exact reported test count is not independently captured.
See the [application ledger](MEMORY-APPLICATION-LEDGER.md) for action evidence
and causal limits. No production H outcome or Learning counter was backfilled.

## What dogfooding caught before launch

Independent review caught useful/control labels in model-visible hypothesis
metadata, overly directive task wording, incomplete-run review retention gaps,
and missing per-arm input revalidation. These were corrected before preparation.
The first prepared hypothesis fixtures then failed actual released retrieval:
their fingerprints and section structure were invalid. Schema listing and
reference-repair tests had missed this. Actual four-case retrieval checks were
added and passed on source and installed 1.13.5.

The rejected first preparation remains in [campaign/](campaign/); it made zero
live model calls and was never frozen or run. The corrected
[campaign-v2/](campaign-v2/) is the only live campaign. These are not repeated
attempts selected after observing model outcomes.

Preflight also found that released `board_get_entry` cannot open H records by
H-id. `board_context` provides their summaries, the getter can read supporting
B records, and full Markdown is locally readable. This read-navigation
limitation was recorded before launch, with unchanged error-stopping rules;
it is a product follow-up observation, not a reason to manufacture an H outcome
for direct Learning use.

## Development and release decision

Keep the current small lead/builder/independent-verifier process. It caught
concrete prelaunch failures; this does not establish that the product itself
improved engineering outcomes. Do not expand the agent organization, add a
hosted supervisor, or add a new success counter on this evidence.

The next bounded product task is F005: a discoverable, read-only H-detail route
that preserves proposed status, provenance, alternatives and falsifier, with
legacy-read compatibility and byte-invariance tests. It does not authorize
automatic causal confirmation. The finding is tracked; implementation is not
part of this pilot.

The next value test should use independently selected real maintenance work
with less obvious multi-file or lifecycle scope, retaining the ordinary and
equivalent-history comparators. It must measure setup/selection/review overhead
and the actual supported installed activation path. Preserve the direct
Learning-use review ledger before deciding whether product attribution needs
a new API or counter.

No version, tag or publication is changed for this pilot, and no 1.14.0
product-value claim is authorized by these results. Historical D.1 thresholds,
locks and meanings remain unchanged. This workflow study does not compute the
D.1 v2 emitted-ordering score or establish internal reasoning order. Source
fix release readiness and product-effect evidence remain separate decisions.

## Evidence

Retention owner: repository owner Rhen McLeod. The source, rejected preparation,
accepted inputs, schemas, raw streams, snapshots, start/end receipts, grades,
reviews and mapping are retained in Git under this directory. See
[descriptive results](RESULTS-v2.json), [summary script](summarize_results.py),
[patch review](PATCH-REVIEW.json), and [application ledger](MEMORY-APPLICATION-LEDGER.md).
The raw run was committed at `408a449`, with grading and descriptive analysis
at `e763127`. Final byte-retrieval audit and delivery references follow below.

The independent post-run audit found that the initial `RESULTS.json` label
`distinct_tool_calls` excluded file-change items. Corrected `RESULTS-v2.json`
names execution/MCP calls explicitly and reports file-change items separately.
The earlier analysis, all raw outputs, receipts and frozen inputs are preserved;
no task grade, timing, token count or stopping decision was changed.
