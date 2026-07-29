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
baseline_commit: bba602156f5836c94478a588f6c048c30f7ea04e
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
| Deterministic contextual retrieval | Accepted requirement | Shared core, command, MCP, SessionStart, and prompt adapters are allocated in section 20.10 | Repeat equality, lexical decoy, cross-domain, adapter parity, stale source, cache rebuild, and offline rows in section 20.11 | `/board-context` contract and context request/response example | Implementation pending |
| Explainable relevance | Accepted requirement | Five exposed score components, structural eligibility gate, source-linked why templates, and stable tie order are specified | Component, threshold, source-link, and no-fabrication rows in section 20.11 | Product spec sections 20.3-20.5 | Implementation pending |
| Explicit outcome feedback | Accepted requirement | Existing H### plan/apply and lock boundary will add typed fix results and compatible explicit dispositions | No-write preview, incompatible result, stale plan, contention, repeated apply, and history rows | `/board-outcome`, H### schema, and resolve-skill changes | Implementation pending |
| Outcome-aware Learning confidence | Accepted requirement | Shared core will preview one-file L### changes. PM may reuse the same plans sequentially under existing authority | Supported, weakened, contested, untested, partial-batch, retry, and explicit-remember preservation rows | Learning schema and confidence table | Implementation pending |
| Repository-local value evidence | Accepted requirement | Derived report reads canonical H### and L### state. No prompt log or telemetry is allocated | Verified context reference, zero-outcome, and no-vanity-count rows | Product spec section 20.7 | Implementation pending |
| Security, failure, and performance | Accepted requirement | Existing path, parser, token, lock, atomic-write, and offline boundaries are retained and extended | Malformed input, linked evidence, injection text, closed proxy, timeout fallback, and 1,200-entry benchmark | Product spec sections 20.8-20.9; implementation must update SECURITY and architecture | Implementation pending |
| Current product documentation | Required current truth | No runtime behavior changes in this contract PR | Existing 17-suite release tree remains the current evidence | README, setup, commands, MCP, architecture, security, visuals, and manifests remain v1.10.1 current truth | Reviewed and unaffected because accepted future behavior is not shipped behavior |
| Historical Milestone A-C evidence | Required preservation | No historical behavior or report change | Existing dated reports remain immutable observations | Historical reports remain unchanged | Reviewed and unaffected because contract acceptance does not revise shipped evidence |
| Version, release, and publication | Deferred until implementation | Current release remains v1.10.1. The implementation contract requires one coordinated minor release boundary | Future release preparation, bundle, CI, registry, Pages, and closeout gates | Current release docs remain unchanged | Reviewed and unaffected in the specification phase |

No required behavior conflict exists because proposed Milestone D behavior is
clearly labeled as unimplemented. The specification PR also repairs stale
v1.10.0 current-release references in the central alignment table. Historical
Milestone C delivery remains v1.10.0.

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
- Implementation phase: starts after this contract PR merges.
- Post-merge and release phases: remain future work. Their evidence
  destinations are the Milestone D implementation and release-validation
  reports.

PR completion state:

```text
state: self-contained accepted specification
external_gate: none
evidence_destination: docs/evidence/2026-07-28-milestone-d-contract.md
terminal_action: merge after passing continuous integration
```

## Current handoff

The contract PR must merge after passing continuous integration. The
implementation owner must then implement the bounded Milestone D contract.
Approval does not authorize any explicit non-goal in section 20.14.
