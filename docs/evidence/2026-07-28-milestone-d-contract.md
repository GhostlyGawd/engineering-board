# Milestone D contract workpad — 2026-07-28

## Decision continuity

- Active outcome: give an acting agent relevant systemic memory before it
  chooses another local fix, then use explicit fix results to improve later
  memory.
- Gate 1: accepted by the product owner on 2026-07-28.
- Gate 2: accepted by the product owner on 2026-07-28. Central product spec
  section 20 is the implementation baseline.
- Canonical storage: repository-owned entry, pattern, hypothesis, and Learning
  Markdown.
- Derived state: graph, context briefs, relevance scores, and value reports.
- Explicit authority: reads are automatic and bounded. H### and L### writes
  require existing PM authority or an explicit content-bound apply.
- Explicitly deferred: SQLite, embeddings, hosted services, telemetry,
  cross-repository aggregation, Milestone E planning, and fix execution.

Repository context:

```text
repository: GhostlyGawd/engineering-board
default_branch: main
baseline_commit: becbb3eaf219c239fbd186c2f749f4067b06cb3e
portfolio_status: inventory-only
audit_source: GhostlyGawd/repo-audit@9c64832e0d97e62a4fa45f2a544ffbc4c29b7a11
```

## Baseline evidence

v1.10.1 provides:

- canonical Markdown entries, P### patterns, H### hypotheses, and L###
  Learnings;
- a shared deterministic graph and ranked cluster engine;
- explicit hypothesis proposal, evaluation, reopen, split, and merge;
- negative memory for rejected explanations;
- plugin and MCP parity for graph and hypothesis facts;
- a normal HTML pattern-intelligence view.

The current gap is observable:

- SessionStart detects systemic patterns through exact open-label counts.
- SessionStart filters Learnings through `applies_to` and the current
  directory.
- task intent does not participate in retrieval.
- an agent must deliberately request `/board-insights`.
- hypothesis evaluation can record status and evidence, but the fix result
  does not deterministically update Learning outcome state.

The accepted contract reuses the shipped graph, hypothesis, locking, plan,
cache, and adapter boundaries. It does not create a database or another
repository.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| Milestone D purpose and authority | Gate 1 and Gate 2 accepted | Implementation starts only from the accepted section 20 baseline | Owner approval and baselined requirements digest | Product spec sections 2, 11, 13, and 20 | Accepted |
| Deterministic contextual retrieval | Accepted requirement | Shared core, command, MCP, SessionStart, and prompt adapters use one implementation | Repeat equality, lexical decoy, adapter parity, cache rebuild, hook, and offline checks | `/board-context`, README, MCP, architecture, and product spec | Implemented and verified |
| Explainable relevance | Accepted requirement | Five score components, a structural eligibility gate, source-linked reason templates, and stable tie order are implemented | Component, threshold, source-link, and lexical-decoy checks | Product spec sections 20.3-20.5 and Milestone D visual | Implemented and verified |
| Explicit outcome feedback | Accepted requirement | The H### preview/apply and lock boundary records typed fix results and compatible explicit dispositions | No-write preview, incompatible input, repeated apply, structured history, and lifecycle checks | `/board-outcome`, H### schema, resolve skill, architecture, and security | Implemented and verified |
| Outcome-aware Learning confidence | Accepted requirement | The shared core previews and applies one-file L### changes. PM uses the same plans sequentially under existing authority | Supported, contested, recurrence-confidence, idempotency, and curator compatibility checks | Learning schema, outcome command, view, and confidence table | Implemented and verified |
| Repository-local value evidence | Accepted requirement | The derived report reads canonical H### and L### state only | Verified context reference and no-prompt/no-session checks | README, MCP, architecture, security, and view | Implemented and verified |
| Security, failure, and performance | Accepted requirement | Existing path, parser, token, lock, atomic-write, and offline boundaries are extended to context and outcomes | Malformed input, unrelated prompt, hostile prompt, no-write, deadline, and 1,200-entry checks | SECURITY and architecture | Implemented and verified |
| Current product documentation | Required current truth | Runtime behavior, schemas, commands, adapters, counts, and view are aligned | Documentation-coherence and full release-tree gates | README, product spec, commands, skills, MCP, architecture, security, landing, LLM guide, visual, and changelog | Updated for v1.11.0 |
| Historical Milestone A-C evidence | Required preservation | No historical behavior or report change | Existing dated reports remain immutable observations | Historical reports remain unchanged | Reviewed and unaffected because contract acceptance does not revise shipped evidence |
| Version, release, and publication | Required after implementation | The coordinated v1.11.0 release preparation updates all versioned surfaces and rebuilds the MCP bundle pin | Release preparation, full suite, PR CI, merged-main CI, publication, registry, PyPI, Pages, and closeout gates | Changelog, manifests, package files, README badge, and dated release evidence | In progress |

No required behavior conflict remains. The implementation follows the accepted
section 20 authority and storage boundaries. Historical Milestone A-C reports
remain unchanged.

## Implementation plan and acceptance phases

- [x] Worker: baseline the accepted Gate 2 contract.
- [x] Worker: implement deterministic contextual retrieval in the shared core.
- [x] Worker: connect the command, MCP, SessionStart, and UserPromptSubmit
  adapters.
- [x] Worker: implement explicit H### outcome preview and apply.
- [x] Worker: implement outcome-aware L### preview and apply.
- [x] Worker: implement the derived value report.
- [x] Worker: pass the Milestone D lifecycle matrix.
- [x] Worker: align schemas, commands, skills, architecture, security, product
  guidance, visuals, and manifests.
- [x] Worker: pass the complete 18-suite release tree.
- [ ] Worker: pass pull-request continuous integration.
- [ ] Post-merge: pass merged-main continuous integration.
- [ ] Post-merge: build and publish the coordinated minor release.
- [ ] Closeout: append external release evidence, merge it, pass closeout
  continuous integration, and revalidate current GitHub state.

## Lifecycle evidence matrix

| Sequence | Failure injection | Expected semantic outcome | Durable evidence | Test |
|---|---|---|---|---|
| Retrieve equal context twice | None | Equal ordered facts and fingerprint | Compared JSON | Milestone D core matrix |
| Retrieve a lexical decoy | No structural signal | Empty result | Empty JSON result | Milestone D core matrix |
| Retrieve through each adapter | Equivalent normalized input | Equal IDs, scores, signals, and sources | Captured adapter output | Adapter-parity matrix |
| Run automatic retrieval | Timeout, malformed evidence, or unrelated prompt | Typed limitation before timeout, or silence for unrelated input | Captured hook output | Hook and benchmark matrix |
| Preview an outcome | No apply token | No canonical file changes | File digests and preview | Outcome matrix |
| Apply an outcome | Stale source, replay, or lock contention | One atomic H### change, or a typed no-change receipt | H### digest and receipt | Outcome lifecycle matrix |
| Derive Learning feedback | Mixed held, failed, partial, and absent outcomes | Exact outcome state and confidence from canonical evidence | L### preview and file | Learning matrix |
| Apply multiple Learning plans | Second apply fails | First change persists. Retry changes only the pending L###. | Batch receipt and file digests | Partial-batch matrix |
| Generate a value report | Retrieval calls without outcomes | No activity or telemetry count appears | Derived report | Value-report matrix |
| Delete derived state and rebuild | Graph and cache absent | Equal logical retrieval. H### and L### remain unchanged. | Compared payloads and digests | Recovery matrix |
| Run offline and with hostile text | Closed proxy and instruction-like evidence | No network use, code execution, path escape, or instruction execution | Process assertions and payload | Security matrix |

## Requirements review state

The requirement mode is `write`. The language profile is `shall`. The
lifecycle profile is `general`.

The product owner approved the complete Gate 2 contract on 2026-07-28.
Automated checking verified the artifact structure. The recorded human review
and approval remain the authority for semantic acceptance.

Baseline status:

```text
BASELINED — AUTHORIZED APPROVAL RECORDED
approval authority: GhostlyGawd
approval state: approved on 2026-07-28
```

Deterministic requirements check:

```text
content_digest: sha256:3bd8c997b2b1e7b204b209a67711e0ca3f86950527f5c7289c3d3a0619c562d2
status: BASELINED — AUTHORIZED APPROVAL RECORDED
FAIL: 0
```

The baselined artifact records approved controlled terms, all five required
human semantic review dimensions, and the authorized baseline approval
against the same content digest.

## Evidence and delivery phases

- Specification phase: this PR contains the accepted central contract and this
  workpad.
- Owner gate: complete. The product owner approved section 20 on 2026-07-28.
- Implementation phase: complete on `agent/milestone-d-intelligence`.
- Post-merge and release phases: in progress. Their evidence destinations are
  the Milestone D implementation and v1.11.0 release-validation reports.

PR completion state:

```text
state: implementation and documentation aligned; external gates pending
external_gate: none
evidence_destination: docs/evidence/2026-07-28-milestone-d-implementation-validation.md
terminal_action: keep open through merge, publication, and closeout evidence
```

## Current handoff

The implementation must pass the complete release tree and PR continuous
integration. It must then merge, publish v1.11.0, and add dated closeout
evidence. Approval does not authorize an explicit non-goal in section 20.14.
