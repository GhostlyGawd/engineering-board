# Milestone D contract workpad — 2026-07-28

## Decision continuity

- Active outcome: give an acting agent relevant systemic memory before it
  chooses another local fix, then use explicit fix results to improve later
  memory.
- Gate 1: accepted by the product owner on 2026-07-28.
- Gate 2: proposed in central product spec section 20. Owner approval is
  pending.
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

The proposed contract reuses the shipped graph, hypothesis, locking, plan,
cache, and adapter boundaries. It does not create a database or another
repository.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| Milestone D purpose and authority | Gate 1 accepted; Gate 2 proposed | No behavior change in this specification PR | Owner review against the stated current problem and outcome | Product spec sections 2, 11, 13, and 20 | Ready for Gate 2 review |
| Deterministic contextual retrieval | Proposed requirement | Shared core, command, MCP, SessionStart, and prompt adapters are allocated in section 20.10 | Repeat equality, lexical decoy, cross-domain, adapter parity, stale source, cache rebuild, and offline rows in section 20.11 | Proposed `/board-context` contract and context request/response example | Not implemented |
| Explainable relevance | Proposed requirement | Five exposed score components, structural eligibility gate, source-linked why templates, and stable tie order are specified | Component, threshold, source-link, and no-fabrication rows in section 20.11 | Product spec sections 20.3-20.5 | Not implemented |
| Explicit outcome feedback | Proposed requirement | Existing H### plan/apply and lock boundary will add typed fix results and compatible explicit dispositions | No-write preview, incompatible result, stale plan, contention, repeated apply, and history rows | Proposed `/board-outcome`, H### schema, and resolve-skill changes | Not implemented |
| Outcome-aware Learning confidence | Proposed requirement | Shared core will preview one-file L### changes. PM may reuse the same plans sequentially under existing authority | Supported, weakened, contested, untested, partial-batch, retry, and explicit-remember preservation rows | Proposed Learning schema and confidence table | Not implemented |
| Repository-local value evidence | Proposed requirement | Derived report reads canonical H### and L### state. No prompt log or telemetry is allocated | Verified context reference, zero-outcome, and no-vanity-count rows | Product spec section 20.7 | Not implemented |
| Security, failure, and performance | Required if Gate 2 is accepted | Existing path, parser, token, lock, atomic-write, and offline boundaries are retained and extended | Malformed input, linked evidence, injection text, closed proxy, timeout fallback, and 1,200-entry benchmark | Product spec sections 20.8-20.9; future SECURITY and architecture updates | Proposed |
| Current product documentation | Required current truth | No current behavior changes in this PR | Existing 17-suite release tree remains the current evidence | README, setup, commands, MCP, architecture, security, visuals, and manifests remain v1.10.1 current truth | Reviewed and unaffected because this PR labels Milestone D as proposed |
| Historical Milestone A-C evidence | Required preservation | No historical behavior or report change | Existing dated reports remain immutable observations | Historical reports remain unchanged | Reviewed and unaffected because the proposal does not revise shipped evidence |
| Version, release, and publication | Deferred until implementation | Current release remains v1.10.1. The implementation contract requires one coordinated minor release boundary | Future release preparation, bundle, CI, registry, Pages, and closeout gates | Current release docs remain unchanged | Reviewed and unaffected in the specification phase |

No required behavior conflict exists because proposed Milestone D behavior is
clearly labeled as unimplemented. The specification PR also repairs stale
v1.10.0 current-release references in the central alignment table. Historical
Milestone C delivery remains v1.10.0.

## Requirements review state

The requirement mode is `write`. The language profile is `shall`. The
lifecycle profile is `general`.

The central sources are complete enough for owner review. Automated checking
can verify structure, atomicity patterns, identifiers, and planned evidence. It
cannot approve product necessity, semantic correctness, feasibility, or the
owner's baseline.

Current status:

```text
DRAFT — SOURCE OR DECISIONS INCOMPLETE
approval authority: GhostlyGawd
approval state: pending
```

The product owner's Gate 2 semantic review and approval are incomplete. No
implementation requirement is released as an accepted baseline until the
product owner approves section 20.

Deterministic requirements check:

```text
content_digest: sha256:8e8f0a5048efc5a0e02aba8a610bcabe31a6b91e68417e779bc33d031730999f
PASS: 46
FAIL: 0
REVIEW_REQUIRED: 5
```

The five open review findings cover four proposed controlled terms and the
required human semantic review dimensions: source fidelity, coverage,
conflicts, feasibility, and verification adequacy. These findings are
expected before the product owner's Gate 2 review. They block a clean or
baselined requirements claim.

## Evidence and delivery phases

- Specification phase: this PR contains the central contract and this workpad.
- Owner gate: review section 20 and approve or revise Gate 2.
- Implementation phase: starts only after Gate 2 approval and contract merge.
- Post-merge and release phases: remain future work. Their evidence
  destinations are the Milestone D implementation and release-validation
  reports.

PR completion state:

```text
state: self-contained specification proposal
external_gate: product-owner Gate 2 approval
evidence_destination: docs/evidence/2026-07-28-milestone-d-contract.md
terminal_action: keep-open until owner approval or revision
```

## Current handoff

The owner must approve or revise central product spec section 20. Approval
authorizes the bounded Milestone D implementation. It does not authorize any
explicit non-goal in section 20.14.
