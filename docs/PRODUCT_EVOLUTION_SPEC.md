# Engineering Board Product Evolution Spec

_Status: Authoritative living product direction: Milestone A shipped in
v1.8.0. Milestone B shipped in v1.9.1. Milestone C shipped in v1.10.0.
Milestone D shipped in v1.11.0. Milestone D.1 Gate 2 is accepted. The corrected
repository-only evaluation harness builds real v1.11.0 context and outcome
evidence. Codex is the required reference client. Live provider replications
are optional. The first Codex run exposed a non-discriminating corpus. The
product owner accepted a separate locked evidence-corpus baseline. Its
reference run improved the positive rate by 16.67 percentage points. This
result failed the required 25-point product-effect gate. An unlocked version 4
proposal now enforces a one-current-incident boundary. Its non-scored preflight
found that v1.11.0 ranks the expected memory but does not return the memory
content that an agent needs to identify the prior incident relationship._
_Started: 2026-07-27_
_Last direction revision: 2026-07-30_
_Product owner: GhostlyGawd_
_Repository: `GhostlyGawd/engineering-board`_
_Current release boundary: `v1.11.0`_
_Portfolio context: inventory-only. audit source `GhostlyGawd/repo-audit` at
`0ced6f4136b12c6251439ff72ca8f22b6dec9b61`_

## 1. Authority and use

This document is the central source of truth for Engineering Board product
direction. It records the product thesis, accepted boundaries, sequencing,
open decisions, and the contract that future implementation plans must serve.
Update it as product decisions are made instead of relying on chat memory.

Authority and precedence:

1. The product owner's latest explicit decision.
2. This living product-direction spec.
3. An approved milestone implementation contract.
4. `ROADMAP.md`, RFCs, audits, and dated research as planning evidence.

This document governs intended direction, not claims about shipped behavior.
Current code, tests, command contracts, and current-truth documentation govern
what the released product does today. Proposed behavior must not be advertised
as shipped until its implementation, tests, documentation, and evidence land
together.

Decision states:

- **Accepted**: explicitly chosen product direction.
- **Active recommendation**: recommended, but still revisable by the owner.
- **Open**: a material product choice is unresolved.
- **Deferred**: deliberately outside the next milestone.
- **Rejected**: considered and deliberately excluded.

No product implementation begins until an implementation contract for the
selected milestone is approved.

## 2. Decision ledger

| Decision | State | Current direction |
|---|---|---|
| Central product-direction source | Accepted | This document is authoritative for product direction. Roadmaps, RFCs, audits, and earlier prose cannot silently override it. |
| Primary product outcome | Accepted | Turn accumulated engineering findings into visible, clustered graph memory that helps agents recognize recurring and cross-domain root causes, avoid repeated band-aid fixes, and make better decisions in later sessions. |
| Product substrate | Accepted | Pattern intelligence is the substrate. Capture, execution, TDD, review, and validation support and improve that intelligence. they are not the primary product identity. |
| Durable state | Accepted | Preserve repository-owned, human-readable Markdown as the canonical evidence and knowledge record. |
| Derived graph | Accepted | Generate machine-readable relationships, clusters, and retrieval views from canonical repository state. Derived artifacts must remain explainable from source evidence. |
| SQLite | Active recommendation | Do not replace Markdown. Consider SQLite only as a disposable, locally rebuildable analysis index after measured scale or query needs justify it. |
| Epistemic boundary | Accepted | Separate observed evidence, deterministic relationships, inferred root-cause candidates, confirmed conclusions, and durable learnings. Never present a cluster as proof of causation. |
| Hypothesis authority | Accepted | Root-cause hypotheses may be stored durably with `status: proposed` and evidence. Only explicit investigation or fix outcomes may confirm them. Rejected hypotheses remain durable negative knowledge. |
| Default capture policy | Active recommendation | Capture automatically. promote explicitly through a foreground action. Automatic capture does not silently become committed project truth. |
| Verification loop | Accepted | Keep `tdd → review → validate` as an optional, falsifiable fix-verification and feedback mechanism. Do not make it the required first experience or the headline value. |
| Claims and resolution | Active recommendation | Preserve atomic claims. Validation may recommend closure. final resolution remains an explicit user or explicitly authorized action. |
| Session modes | Active recommendation | Keep PM and Worker modes as advanced batch controls, not required concepts in the default pattern-memory workflow. |
| Cross-repository intelligence | Deferred | Prove repository-local pattern intelligence before designing aggregation across repositories. |
| Hosted service or required database | Deferred | No hosted control plane, daemon, account system, cloud sync, or required database in the next milestones. |
| Structured planning bridge | Deferred | PRD decomposition remains a possible later input path, not the product substrate. |
| Cross-session Conductor | Deferred | RFC 0001's persistent supervisor is not the next required product step. |
| Team dashboard and monetization | Deferred | Do not build until repository-local intelligence has demonstrated repeatable value. |
| B057 prerequisite | Landed | PR #93's scratch-finding count fix landed before Milestone A and is included in v1.8.0. The superseded 1.7.1 preparation was folded into the combined feature release instead of publishing two adjacent versions. |
| Milestone A delivery | Accepted and shipped | The contained synthetic `/board-demo`, deterministic demo graph engine, proposed-hypothesis contract, real evidence view, cleanup boundary, tests, and dated validation ship in v1.8.0. |
| Milestone B direction | Accepted and shipped | Make real findings from every supported intake path converge into trustworthy, normalized, provenance-linked graph memory before adding richer root-cause reasoning. |
| Stable pattern identity | Accepted for Milestone B | Add repository-owned `P###` pattern records with readable labels and aliases. Preserve legacy free-form labels as evidence and compatibility input. do not let semantic suggestions silently become canonical identity. |
| Foreground promotion | Accepted for Milestone B | Preview captured findings and their proposed pattern assignments, then require an explicit apply action. PM mode may retain its already-authorized batch behavior but must use the same promotion core. |
| Adapter parity | Accepted for Milestone B | Plugin and MCP surfaces must consume the same zero-dependency parser, pattern resolver, and deterministic graph engine and return semantically equivalent facts. |
| Codex plugin | Accepted 2026-08-14 | Distribute the five pattern-memory skills and the 19-tool MCP server as one installable Codex plugin. The plugin must not require a provider account, Claude Code hook scripts, or unrelated MCP servers. |
| Milestone B implementation | Accepted and shipped | Section 18 shipped in v1.9.1 without Milestone C reasoning, SQLite, hosted services, or cross-repository aggregation. The v1.9.0 publication workflow failed closed on a packaging-check mismatch before a GitHub Release. v1.9.1 is the corrected publication boundary. |
| Milestone C direction | Accepted and shipped | Deterministic cluster ranking, evidence-linked H### hypotheses, explicit evaluation, negative memory, adapter parity, and the normal pattern-intelligence view shipped in v1.10.0. Section 19 remains the approved contract. |
| Milestone D direction | Accepted and shipped | Relevant repository-local pattern memory now enters the agent decision path. Explicit fix outcomes improve later retrieval and Learning confidence. Section 20 remains the accepted implementation contract. |
| Milestone D.1 direction | Context information correction approved; version 4 remains unlocked | Prove whether context changes an agent diagnosis before a local fix. Keep version 3 locked with its failed result. Context contract version 2 returns bounded canonical memory content. Run a new version 4 preflight before the owner reviews an exact scored baseline. |

## 3. Product thesis

Engineering Board is a repository-owned pattern-intelligence system for
engineering agents.

Its core value is not that it can move a task through a build loop. Its core
value is that it accumulates findings across turns and sessions, connects
symptoms that would otherwise remain isolated, and makes recurring or
cross-domain failure patterns visible early enough for an agent to investigate
the shared cause.

```text
encounter a symptom
  → capture the finding and provenance
  → promote reviewed repository evidence
  → normalize failure patterns and affected domains
  → connect related findings in a graph
  → detect recurring and cross-domain clusters
  → propose an evidence-linked root-cause hypothesis
  → surface it when an agent is making a relevant decision
  → fix the system rather than each symptom
  → feed the outcome back into confidence and durable learning
```

The Markdown board is the visible memory. The graph is the connective memory.
The pattern-analysis and retrieval layer is the intelligence multiplier.
Verification closes the feedback loop by showing whether the inferred cause
and chosen fix were actually correct.

### The job to be done

> When engineering findings accumulate over time, help the next agent see the
> system-level pattern that no individual chat contains, with enough provenance
> to act on it without trusting an opaque conclusion.

### Product promise

Engineering Board should help an agent answer:

1. What has been observed?
2. Which findings appear related, even across different components?
3. What recurring failure pattern connects them?
4. Is there a plausible shared root cause, and what evidence supports it?
5. What prior fixes or learnings apply here?
6. What root-level investigation or action should happen next?
7. Did the eventual fix validate or weaken the hypothesis?

## 4. Non-negotiable properties

1. **Canonical evidence stays visible.** A human or fresh agent can inspect
   meaningful Markdown, provenance, diffs, and history without a special
   database client.
2. **Derived intelligence is explainable.** Every edge, cluster, hypothesis,
   and learning links back to the findings or rules that produced it.
3. **Evidence and inference remain distinct.** Similarity is not causation.
   Root-cause candidates carry confidence and status rather than masquerading
   as facts.
4. **Memory compounds across sessions.** Useful findings do not disappear with
   chat context, and resolved cases continue to inform later work.
5. **Cross-domain connections are first-class.** Shared failure modes may
   connect different files, subsystems, or workflows even when their surface
   symptoms differ.
6. **The system resists vocabulary fragmentation.** Pattern aliases and
   normalization prevent equivalent concepts from becoming disconnected tags.
7. **Repository state is portable and local-first.** A required service,
   account, or opaque binary store is not a prerequisite for correct behavior.
8. **Automatic capture is not automatic belief.** Promotion and interpretation
   retain review boundaries appropriate to their authority.
9. **Verification improves memory.** Fix outcomes may strengthen, weaken, split,
   merge, or retire a hypothesis or learning.
10. **Automation fails visibly.** A corrupt cache, failed rebuild, unsupported
    adapter, or uncertain inference produces an explicit limitation, not false
    confidence.

## 5. What exists today

The current product already contains important pieces of this direction:

| Layer | Current behavior | Limitation |
|---|---|---|
| Finding capture | Stop-hook extraction appends evidence-backed scratch findings and surfaces a capture receipt. | Pattern metadata is not assigned until intake/promotion, so captured evidence does not immediately participate in analysis. |
| Canonical board | Promoted bugs, features, questions, observations, and learnings are readable Markdown with frontmatter. | The board is optimized around entry lifecycle more than knowledge connectivity. |
| Pattern vocabulary | Intake asks agents to reuse kebab-case failure-mode tags and apply them broadly. | Free-form exact strings fragment easily. aliases, hierarchy, and semantic equivalence are not represented. |
| Structural graph | `/board-graph` defines nodes, explicit relationships, shared-pattern, shared-affects, shared-tag edges, topology, and typed findings in `GRAPH.yml`. | The graph builder is a command procedure rather than a shared deterministic executable engine. Exact tags and path prefixes miss semantically related cross-domain symptoms. |
| Cluster surfacing | Intake and triage flag a pattern at 2+ occurrences. SessionStart warns at 3+ open occurrences. | Thresholds and presentation differ. Counts identify recurrence but do not explain cluster evidence or competing hypotheses. |
| Learning curation | At 3+ resolved entries sharing an exact pattern, the curator creates a source-linked Learning and raises confidence by recurrence. | Curation runs through PM mode, treats recurrence count as the main confidence signal, and does not learn from failed fixes or rejected causal hypotheses. |
| Context retrieval | SessionStart shows up to three medium/high-confidence learnings filtered by `applies_to` and current directory. | Retrieval is path-centric and does not surface relevant live clusters, root-cause candidates, or the reason a cross-domain match matters. |
| Resolution feedback | Resolution archives pattern tags and can cascade across pattern/affects neighbors. | A resolution does not yet record whether the suspected root cause was confirmed, whether the fix held, or which cluster interpretation changed. |
| Quality workflow | Worker mode can drive `tdd → review → validate`, retain claims, and ask for explicit resolution. | This strong implementation loop dominates the current story even though it is downstream of the intelligence benefit. |
| Codex adapter | A repository-owned plugin manifest packages the five skills and the isolated 19-tool MCP configuration. | Codex does not run Claude Code hooks. It uses the MCP-first workflow and requires an explicit repository root for each bundled-plugin tool call. |

The product does not need a new identity invented from scratch. It needs to
connect and elevate mechanisms it already partially owns.

## 6. Epistemic model

Pattern intelligence is only valuable if agents can tell what is known from
what is inferred.

| Layer | Meaning | Authority | Durable form |
|---|---|---|---|
| Observation | A symptom, constraint, result, or user report with provenance. | Captured evidence. reviewed at promotion. | Canonical Markdown finding/entry. |
| Relationship fact | An explicit dependency, contradiction, shared exact pattern, shared affected prefix, or other reproducible relation. | Deterministic rule or explicit author. | Derived graph edge with source/rule reference. |
| Candidate cluster | A reproducible grouping that crosses a configured threshold. | Deterministic clustering engine. | Rebuildable derived graph record. |
| Root-cause hypothesis | An interpretation explaining why cluster members may share a cause. | Agent-generated proposal with cited members, confidence, alternatives, and falsifier. | Proposed insight. durable only when retained through an explicit policy. |
| Confirmed finding | A hypothesis supported by investigation or fix outcome. | Explicit resolution/investigation evidence. | Canonical Markdown update with provenance. |
| Learning | A reusable conclusion with scope, recurrence, confidence, and source cases. | Explicit remember action or approved deterministic curation policy. | Canonical Markdown learning. |

Required state transitions:

```text
evidence
  → deterministic relation/cluster
  → proposed hypothesis
  → confirmed | weakened | rejected | split | merged
  → contextual learning
```

A candidate may remain unresolved indefinitely. Rejection is useful memory and
must prevent the same weak explanation from being repeatedly proposed without
new evidence.

## 7. Storage architecture: Markdown, graph, and SQLite

### Decision

Use a layered model:

```text
Canonical write model        Derived read models
---------------------        -------------------
Markdown entries      ────→  GRAPH.yml / graph records
Markdown learnings    ────→  cluster and retrieval views
Markdown decisions    ────→  optional local SQLite index later
Git history           ────→  regenerated caches
```

Markdown remains authoritative. Generated graph or database artifacts are
disposable read models. If every derived artifact is deleted, the product must
be able to reconstruct the same logical intelligence from canonical files.

### Tradeoff

| Property | Markdown only | SQLite as authority | Recommended layered model |
|---|---|---|---|
| Human inspection and review | Excellent | Poor without tooling | Excellent |
| Git diffs and merge recovery | Excellent | Binary and conflict-prone | Canonical diffs remain excellent |
| Portability and zero-service use | Excellent | Requires schema/tooling | Excellent. index optional |
| Transactions and referential integrity | Manual | Strong | Canonical writes remain explicit. index can validate |
| Large scans, joins, ranking, and aggregation | Degrades with corpus size | Strong | SQLite can accelerate only when justified |
| Full-text and compound queries | Awkward | Strong | Optional index serves advanced queries |
| Corruption recovery | Source files are directly recoverable | Depends on backup/migrations | Delete and rebuild derived state |
| Agent readability | Direct | Tool-mediated | Direct evidence plus efficient query tools |
| Trust and explainability | High | Can become opaque | High if every result links to source |

### Why not migrate now

At the current product stage, SQLite would improve query mechanics more than
user value. It would not by itself solve tag fragmentation, causal inference,
cluster explanation, contextual retrieval, or feedback from fix outcomes.
Those are the actual intelligence gaps.

Adding a database now would create schema migration, cache invalidation,
cross-platform packaging, corruption recovery, and Git-ignore behavior before
a measured workload proves they are needed. Nothing in the current
repository-local consumer fails because SQLite is absent.

### Adoption trigger for an optional SQLite index

Evaluate a derived SQLite index only when at least one is demonstrated:

1. A representative large-board benchmark cannot meet an approved interactive
   latency target by parsing canonical files and generated graph records.
2. Required cluster, history, or retrieval queries cannot be expressed
   reliably in the current read model.
3. Incremental recomputation is required to keep analysis usable at a measured
   corpus size.

Any SQLite proposal must prove:

- deletion and deterministic rebuild from canonical Markdown.
- logically equivalent query and cluster results with and without the index.
- source provenance for every returned result.
- no committed binary database or database merge workflow.
- schema versioning and forward recovery.
- corrupt or stale index detection with safe self-rebuild.
- cross-platform packaging and performance evidence.
- no dependency on SQLite for reading, editing, reviewing, or recovering the
  board.

SQLite is therefore a future optimization candidate, not a product-direction
migration.

## 8. Competitive position

Engineering Board should selectively absorb useful interaction patterns from
adjacent products while preserving its distinct job.

| Source | Strength to learn from | Apply to Engineering Board | Boundary |
|---|---|---|---|
| [Beads](https://github.com/gastownhall/beads) | Durable agent memory, graph queries, ready work, and multi-agent coordination. | Make graph memory and contextual retrieval first-class. provide concise next investigation/action. | Do not adopt database-first authority or distributed sync before a current consumer requires it. |
| [Backlog.md](https://github.com/MrLesk/Backlog.md) | Rich, inspectable Markdown tasks and human-friendly browsing. | Keep evidence, hypotheses, acceptance criteria, and learning provenance easy to read and review. | Do not become a general-purpose project-management suite. |
| [Task Master](https://github.com/eyaltoledano/claude-task-master) | PRD decomposition and recommended-next workflows. | Later accept structured plans as one finding source and make the next investigation obvious. | Planning breadth is not the intelligence substrate. |
| Claude Code Tasks | Frictionless in-session checklist. | Compose with it: ephemeral steps remain session-local. durable discoveries enter Engineering Board. | Do not rebuild a personal checklist. |

The differentiator is:

> Evidence-visible, repository-owned, clustered engineering memory that helps
> agents connect symptoms across time and domains, form inspectable root-cause
> hypotheses, and learn from what actually fixed them.

## 9. Retain, append, replace, revise

### Retain

- Canonical Markdown entries, learnings, and Git history.
- Automatic scratch capture with evidence anchors.
- Explicit promotion as the commitment boundary.
- `pattern`, `affects`, relationships, source IDs, and resolution provenance.
- Deterministic graph facts and typed findings.
- Local-first operation with no required service.
- Atomic claims, blockers, priorities, hierarchy, and `## Done when`.
- Explicit final resolution.
- TDD, review, and validation as available proof mechanisms.

### Append

1. A normalized pattern vocabulary with aliases and stable pattern identity.
2. A shared deterministic graph builder below plugin and MCP adapters.
3. Candidate clusters that explain membership, signals, thresholds, and
   cross-domain reach.
4. An on-demand interpretation layer that proposes root-cause hypotheses with
   evidence, alternatives, confidence, and falsifiers.
5. Durable feedback recording whether an investigation or fix confirmed,
   weakened, rejected, split, or merged a hypothesis.
6. Context retrieval that surfaces relevant live clusters and learnings when an
   agent is investigating or changing related code.
7. Foreground promotion and analysis that do not require persistent PM mode.
8. A visible pattern-memory view showing how current findings connect to prior
   cases.
9. Evaluation fixtures that measure useful cross-domain connection and false
   positives, not only file/schema conformance.

### Replace

1. Replace the headline
   `capture → tdd → review → validate`
   story with
   `capture → connect → recognize → investigate root cause → learn`.
2. Replace the first-win build demo with a pattern-intelligence demo: several
   apparently separate findings reveal a shared, evidence-linked cause.
3. Replace exact-string recurrence as the whole intelligence model with a
   layered model of normalized patterns, explicit relations, topology, and
   bounded semantic interpretation.
4. Replace raw recurrence counts as confidence with evidence quality, diversity
   of domains, investigation outcomes, counter-evidence, and recurrence.
5. Replace “show me a card” as the primary board question with “what systemic
   pattern needs attention, and why?”

### Revise

1. Revise `/board-graph` from a prompt-level procedure into a tested shared
   engine with stable output semantics.
2. Revise SessionStart to prioritize active systemic patterns, relevant
   clusters, unresolved hypotheses, and applicable learnings.
3. Revise learning curation to consume direct promotion/resolution feedback,
   not only PM turns and exact resolved-tag counts.
4. Revise the HTML board into an evidence-to-pattern view while retaining
   action and lifecycle visibility.
5. Revise promotion so pattern assignment and normalization are inspectable
   and correctable.
6. Revise TDD/review/validation messaging so it demonstrates how a root-cause
   fix was verified and how that outcome updates memory.
7. Revise plugin and MCP adapters to expose the same graph, cluster, and
   evidence semantics without promising unsupported autonomous execution.

## 10. Target journeys

### 10.1 First win

```text
install
  → /board-setup
  → load a bounded sample containing three symptoms in different domains
  → capture/promote the findings
  → generate the graph
  → see the shared pattern and why each finding belongs
  → inspect the proposed common root cause and its uncertainty
  → remove or retain the sample explicitly
```

Success is not watching a card change columns. Success is seeing a connection
that would have been missed in three isolated chats.

The demo may optionally show a fix and validation afterward, but the
intelligence insight must be independently understandable.

### 10.2 Normal work

```text
work normally
  → receive a quiet capture confirmation
  → promote reviewed findings
  → normalize and connect them
  → surface a new or strengthened cluster
  → inspect member evidence and root-cause candidate
  → choose a root investigation or fix
  → validate the result
  → update hypothesis and learning confidence
```

Singleton findings remain useful evidence. The system must not manufacture a
cluster merely to appear intelligent.

### 10.3 Returning to a repository

SessionStart should prioritize:

1. Safety, recovery, or stale-derived-state warnings.
2. Active high-impact systemic clusters and newly changed evidence.
3. In-progress investigations and claims.
4. Context-relevant root-cause hypotheses and learnings.
5. Pending scratch promotion.
6. Best ready action when action is requested.
7. Advanced mode state, if active.

### 10.4 Inspecting an insight

An agent or human can move from:

```text
cluster
  → member findings
  → source evidence
  → relationship reasons
  → hypothesis and alternatives
  → prior attempted fixes
  → confirmation or rejection evidence
  → reusable learning
```

No conclusion should be a dead-end summary without drill-down.

## 11. Product milestones

Milestones are ordered by the product's intelligence value.

### Milestone A: Pattern-intelligence first win

**Purpose:** Demonstrate the unique product value in one session.

**Implementation state:** shipped in v1.8.0. The delivered scope is:

- A bounded cross-domain sample with a known shared failure pattern.
- Canonical `/board-setup` guidance.
- Foreground sample capture/promotion without PM-mode ceremony.
- Graph and cluster output with member evidence and relationship reasons.
- A root-cause candidate clearly labeled as an inference.
- Explicit, fingerprinted sample cleanup or retention.
- A real visual showing evidence to cluster to root-cause candidate.

If omitted, the first experience continues to showcase workflow mechanics
instead of the product's intelligence advantage.

### Milestone B: Reliable finding-to-graph pipeline

**Purpose:** Ensure real findings become trustworthy, connected memory.

**Implementation state:** shipped in v1.9.1. The delivered scope is:

- Foreground promotion outside PM mode.
- Pattern normalization and alias handling.
- Stable pattern IDs while preserving readable labels.
- Shared deterministic graph engine used by plugin and MCP paths.
- Unified cluster thresholds and typed output.
- Provenance and correction path for pattern assignments and edges.
- Incremental rebuild contract without adopting a required database.

If omitted, intelligence remains dependent on exact free-form tags and
adapter-specific prompt execution.

### Milestone C: Cross-domain root-cause intelligence

**Purpose:** Turn structural clusters into useful, bounded engineering
interpretation.

**Direction state:** Gate 1 and Gate 2 accepted by the product owner on
2026-07-28. The approved section 19 contract is implemented, validated, and
shipped in v1.10.0.

Implemented scope:

- Cluster ranking using recurrence, domain diversity, severity, recency, and
  evidence quality.
- On-demand hypothesis generation with cited members.
- Alternative hypotheses and explicit falsifiers.
- Confirm, weaken, reject, split, and merge feedback states.
- Negative memory so rejected explanations are not recycled without new
  evidence.
- Pattern-focused HTML and command views.

If omitted, Engineering Board can count and group patterns but cannot reliably
help an agent reason from symptoms toward a shared cause.

### Milestone D: Contextual retrieval and outcome learning

**Purpose:** Deliver accumulated intelligence at the decision where it changes
agent behavior.

**Implementation state:** shipped in v1.11.0. Gate 1 and Gate 2 were accepted
by the product owner on 2026-07-28. Section 20 remains the accepted
implementation contract.

Delivered scope:

- Retrieval based on current files, task intent, patterns, graph neighbors, and
  prior outcomes-not only current working directory.
- SessionStart and on-demand surfacing of relevant clusters and learnings.
- Resolution feedback that updates hypothesis and learning confidence.
- Source-linked explanation of why a memory applies.
- Value reporting based on useful resurfacing and confirmed systemic fixes, not
  vanity counts.

If omitted, the repository may contain strong memory that the acting agent
still fails to use.

### Milestone D.1: Product proof and retrieval calibration

**Purpose:** Prove whether the shipped context changes an agent diagnosis
before the agent proposes a local correction.

**Direction state:** Gate 1 and Gate 2 accepted by the product owner on
2026-07-29. Section 21 contains the accepted implementation contract.

Approved direction:

- Use a fixed and sanitized evaluation corpus.
- Run paired clean-agent trials with and without the real context brief.
- Record whether the agent identifies the systemic investigation before it
  proposes a symptom-only correction.
- Measure expected-memory rank, irrelevant results, rejected-memory treatment,
  canonical citations, and the effect of an applied outcome on later
  retrieval.
- Keep production behavior frozen during each evidence run.
- Use failed cases to propose later ranking, explanation, presentation, or
  outcome-ergonomics changes.
- Keep Milestone E deferred until the product owner accepts the validation
  evidence and the resulting next-step decision.

If omitted, Engineering Board can show that its components work without
showing that the accumulated memory improves an agent decision.

### Milestone E: Execution ergonomics and planning bridge

**State: Deferred until Milestone D.1 product validation is accepted.**

Possible work:

- One obvious next investigation or action.
- Direct `/board-run` and explicit resolve ergonomics.
- Action-first lifecycle presentation alongside the pattern view.
- Approved-spec decomposition into existing entry hierarchy.

The quality loop remains valuable here as a way to prove a systemic fix and
feed the result back into memory. It does not lead the roadmap.

## 12. Outcome acceptance

### Pattern-intelligence value

1. Given a fixture with three surface-different findings in distinct affected
   domains and one known shared failure mode, the system produces one
   evidence-linked candidate cluster containing all three.
2. The same canonical input produces logically identical nodes, edges,
   clusters, and relationship reasons.
3. An agent can explain why each member belongs using repository evidence,
   without relying on hidden chat state.
4. A fixture containing merely similar language but unrelated causes is not
   forced into the same durable conclusion.
5. A singleton remains a singleton without fabricated confidence.

### Root-cause trust

6. A root-cause output is labeled as proposed until evidence confirms it.
7. Every hypothesis identifies supporting members, counter-evidence or
   alternatives, confidence basis, and at least one falsifier.
8. Rejected hypotheses remain queryable and are not proposed again without
   materially new evidence.
9. Confirmed fix outcomes strengthen the relevant learning. failed or partial
   fixes weaken or split it.
10. A user can correct a pattern, edge, cluster interpretation, or learning
    without editing an opaque cache.

### Memory and retrieval

11. A later session working in a different domain receives a relevant prior
    cluster when its current symptom shares the underlying failure pattern.
12. Surfaced memory states why it applies and links to canonical source cases.
13. Deleting derived graph/index artifacts loses no canonical evidence and a
    rebuild restores equivalent logical results.
14. The system reports stale, corrupt, or unavailable derived analysis instead
    of silently presenting incomplete intelligence.

### Compatibility and boundaries

15. Existing Markdown boards require no destructive migration.
16. Plugin and MCP adapters return semantically equivalent graph facts where
    both advertise support.
17. No read or recommendation request begins code execution, commits a
    hypothesis, or resolves work without the appropriate explicit authority.
18. TDD, review, and validation remain usable but are not required to experience
    pattern discovery.
19. README, setup, examples, architecture, visuals, security/privacy,
    versions, tests, and dated evidence are reconciled with each shipped
    milestone.
20. One Codex plugin installation exposes all five skills and all 19 MCP tools
    without another model-provider account or an unrelated MCP server.

## 13. Accepted and open decisions

### A1: Hypothesis authority

**State: Accepted 2026-07-27.**

Options:

1. All root-cause hypotheses remain ephemeral unless explicitly confirmed.
2. Proposed hypotheses may be saved durably with `proposed` status and evidence,
   but only investigation/fix outcomes can confirm them.
3. High-confidence clusters automatically become confirmed learnings.

Decision: option 2. Durable proposals prevent repeated rediscovery while
preserving the distinction between useful inference and established knowledge.
Option 3 is rejected: confidence never converts correlation into confirmed
causation without outcome evidence.

### A2: Pattern normalization

**State: Accepted for Milestone B on 2026-07-27.**

Options:

1. Curated canonical pattern IDs with readable aliases.
2. Free-form tags plus embedding/semantic similarity at query time.
3. A hybrid: canonical IDs for durable memory and bounded semantic suggestions
   for proposed aliases or links.

Decision: option 3. Exact canonical identity keeps durable results
deterministic. semantic suggestions can discover cross-domain equivalence but
must remain reviewable before becoming durable.

### A3: Cluster model

**State: Accepted for Milestone B on 2026-07-27.**

Options:

1. Exact pattern recurrence only.
2. One global similarity score.
3. Typed signals-explicit relationships, normalized pattern, affected domain,
   temporal recurrence, evidence semantics, and outcome history-with each
   contribution exposed.

Decision: option 3. A single opaque score would make false positives hard
to diagnose and weaken trust.

### A4: First-win fixture

**State: Accepted, implemented, and shipped in v1.8.0.**

The sample contains different surface symptoms and affected domains that share
the verifiable `duplicated-state-contract` pattern. Its containment and cleanup
model are pinned by the accepted Milestone A contract and dated evidence.

### O5: SQLite trigger and latency target

The layered storage direction is set. the numeric corpus and interactive
latency threshold that would justify an optional SQLite index remains open.
Benchmark the file/graph implementation first rather than inventing a threshold
without evidence.

### A5: Promotion boundary

**State: Accepted for Milestone B on 2026-07-27.**

Decision: a foreground promote action writes validated findings, reports
created/rejected/deduplicated outcomes, and offers a preview. Silent
auto-promotion remains deferred.

### O7: Resolution and learning feedback

**State: Gate 1 and Gate 2 accepted in section 20.**

After verification, offer explicit outcome feedback that records the fix
result against cited evidence. The outcome can recommend a hypothesis or
Learning change. It cannot silently convert successful validation into
confirmed causation.

## 14. Alternatives

### Keep emphasizing the build loop

This proves engineering discipline but underuses the accumulated corpus. Many
tools can run tests and reviews. the unique advantage is recognizing patterns
that a stateless agent misses. Rejected as the primary product story.

### Use Markdown only forever

This preserves simplicity, but an absolute ban on derived indexing could become
costly at large corpus sizes. Keep Markdown authoritative while allowing a
measured, disposable accelerator later.

### Make SQLite authoritative now

This improves transactions and querying but weakens direct inspection, Git
diffs, recovery, and zero-tool portability before scale evidence exists.
Rejected.

### Use an LLM to directly generate the graph

This may discover semantic connections but makes topology unstable and hard to
reproduce. Keep deterministic graph facts separate from bounded semantic
interpretation.

### Copy a general task or planning product

This adds breadth while diluting the root-cause memory job. Continue composing
with session tasks and planning tools instead.

## 15. Explicit non-goals for Milestones A-D.1

- Replacing canonical Markdown with SQLite or another database.
- Committing a binary database as collaboration state.
- A hosted service, login, organization model, billing, or cloud sync.
- Cross-repository aggregation.
- A general-purpose project-management suite.
- Reimplementing a personal session checklist.
- Autonomous code execution from a read-only insight request.
- Treating semantic similarity as confirmed causation.
- Silent confirmation, resolution, or auto-promotion.
- Removing advanced modes before compatibility evidence exists.
- Implementing RFC 0001's persistent supervisor.

## 16. Documentation and behavior alignment

| Contract item | Normative level | Current implementation | Test/evidence | Documentation disposition | Status |
|---|---|---|---|---|---|
| Product-direction authority | Accepted | No runtime behavior | Owner decision recorded here | This file. `ROADMAP.md` precedence note | Direction aligned |
| Pattern-intelligence substrate | Accepted direction | Production capture, promotion, stable pattern identity, deterministic graph behavior, contextual retrieval, durable H### outcome history, and outcome-aware L### state form one evidence-to-learning substrate | Existing graph and curator tests plus Milestone A-D lifecycle matrices | README, landing page, commands, normal view, and architecture explain the context-to-outcome loop | Milestones A-D implemented and aligned |
| Hypothesis authority | Accepted direction | Canonical H### records support proposed, weakened, confirmed, rejected, split, and merged states through evidence-gated preview/apply. negative memory blocks unchanged rejected claims | Hypothesis contract, Milestone C matrix, MCP suite, full release tree, and v1.10.0 publication evidence | Schema, command, skill, security, architecture, and product docs aligned | Shipped in v1.10.0 |
| Canonical Markdown | Accepted | Entry, pattern, hypothesis, and Learning Markdown is durable state. Graphs, rankings, context briefs, value reports, cache, and HTML remain derived | Intake, graph, context, hypothesis, outcome, rebuild, resolve, and curation tests | Architecture and storage boundary documented | Aligned |
| Derived graph | Accepted direction | One shared zero-dependency engine serves production plugin, PM, contained demo, and MCP adapters. canonical P### identities and legacy fallbacks produce source-linked graph facts | Existing graph suites plus the Milestone B pattern-pipeline matrix | Graph schema, cache authority, and adapter parity are current in command, MCP, architecture, and schema docs | Milestone B aligned |
| Milestone B reliable pipeline | Accepted and shipped | Stable P### records, foreground promotion, shared PM/MCP/plugin core, disposable cache, receipts, and graph provenance shipped in v1.9.1 | `tests/orchestration/milestone-b-pattern-pipeline.sh`, full release-tree suite, bundle-content parity, implementation evidence, and external release validation | Current-truth product, command, MCP, architecture, security, landing, and LLM docs updated | Shipped in v1.9.1 |
| SQLite | Optional future accelerator | Not implemented or required | Future benchmark and rebuild-equivalence proof required | Migration explicitly rejected. adoption trigger recorded | Deferred optimization |
| Current capture confirmation | Required current truth | Stop procedure and append helper surface a non-empty receipt | `tests/scratch/append.sh`. mode-routing tests | README was corrected in this branch | Documentation-only drift repaired |
| Canonical setup instruction | Required current truth | `/board-setup` is the plugin setup path | Setup command test | Landing page was corrected in this branch | Documentation-only drift repaired |
| TDD/review/validate | Required current truth, supporting future role | Worker loop remains shipped and unchanged | Existing mode and orchestration tests | Repositioned as optional falsifiable verification feedback, not the headline or required first experience | Behavior unchanged. messaging aligned |
| MCP behavior | Required current truth | Nineteen tools share canonical Markdown. Pattern, promotion, graph, ranking, context, hypothesis, outcome, and Learning tools delegate to the same core as plugin adapters | MCP lifecycle suite plus Milestone B-D adapter-parity matrices | MCP reference, manifests, package modules, and counts updated | Published in v1.11.0 |
| Codex plugin | Accepted current direction | `.codex-plugin/plugin.json` packages five MCP-first skills. Root `.mcp.json` starts only Engineering Board through a portable launcher and requires the repository root. Claim and release use the Python server instead of Claude hook scripts | Codex plugin manifest and launcher test, MCP lifecycle suite, plugin validator, and dated installation evidence | README, MCP reference, architecture, security, release procedure, changelog, skills, and this central spec aligned in the same change | Implemented after v1.12.0; publication requires a later versioned release |
| Security, privacy, versions, releases | Required current truth | Bounded automatic reads, content-bound H### and L### writes, lock revalidation, linked-input refusal, HTML escaping, no raw-prompt retention, and offline operation extend the existing controls | Security suites, Milestone D matrix, hook benchmarks, full release tree, reproducible bundle gate, merged-main CI, and publication checks | SECURITY, changelog, architecture, commands, manifests, visual, implementation evidence, and release validation aligned | v1.11.0 published and externally validated |
| Milestone C implementation contract | Accepted and shipped | Shared core, two commands, two MCP tools, H### schema and lifecycle, graph schema 3, normal HTML intelligence view, permissions, and packaging shipped | Milestone C 15-check matrix, 166-check MCP suite, 17/17 current release-tree suites, merged-main CI, release workflow, and live-surface checks pass | Central spec, contract workpad, current-truth docs, real sanitized visual, implementation evidence, and v1.10.0 release validation remain current for Milestone C behavior | Shipped in v1.10.0; packaging current at v1.10.1 |
| Milestone D implementation contract | Accepted and shipped | Shared contextual retrieval, automatic read adapters, explicit H### fix outcomes, separate L### feedback, value evidence, and the normal HTML view shipped from the accepted section 20 baseline. | Milestone D core, hook, MCP, view, security, performance, recovery, full release-tree, merged-main, and publication evidence | Central spec, workpad, schemas, commands, skills, README, MCP, architecture, security, landing page, LLM guide, sanitized visual, and release validation are aligned | Shipped in v1.11.0 |
| Milestone D.1 product-proof contract | Calibrated reference run complete; product gate failed | The repository-only harness separates a non-scored calibration corpus from a locked evidence corpus. Scored runs require the locked corpus. The validator rejects declared oracle leakage, requires positive-case information gaps, and verifies that lexical decoys retrieve rejected memory. Codex remains the reference client. | Baselined requirements checker, 17 focused harness tests, full release tree, continuous integration, and dated Codex evidence | Central spec section 21, evaluation guide, calibration workpad, calibrated reference evidence, and preserved historical evidence | Version 3 preserved; a new baseline is required before another scored run |
| Historical audits and evidence | Historical | Preserved | Superseding dated evidence added | Historical claims are not rewritten | Reviewed and preserved |

## 17. Gate 2 accepted: Milestone A implementation contract

_State: Accepted by the product owner on 2026-07-27 and implemented on the
direction branch. shipped in v1.8.0._

### 17.1 Milestone purpose

> Give a new user one bounded, trustworthy experience in which three
> surface-different engineering symptoms across separate domains become one
> evidence-linked systemic investigation candidate-proving the product's
> intelligence advantage before introducing its operating model.

### 17.2 Demonstration scenario

The built-in sample models lifecycle-contract drift across three adapters:

| Entry | Surface symptom | Affected domain |
|---|---|---|
| `B001` | A worker does not select an entry that should be eligible for review. | `hooks/` worker routing |
| `B002` | The HTML board renders the same lifecycle state in the wrong lane. | `hooks/scripts/board-view.sh` |
| `B003` | MCP ready-work output omits the same class of eligible entry. | `mcp-server/` |

The canonical normalized pattern is `duplicated-state-contract`.

The expected candidate cluster contains all three findings because the
independent adapters interpret one lifecycle contract separately. The expected
proposed hypothesis is:

> Lifecycle semantics are duplicated across the worker, renderer, and MCP
> adapter instead of being consumed from one shared contract.

The sample is synthetic and labeled as such. It must not imply these are
currently open production bugs.

### 17.3 User interaction contract

Proposed command:

```text
/board-demo
/board-demo --clean <run-id>
```

`/board-setup` remains the canonical setup command and ends with one optional
next step:

```text
Try the pattern-intelligence sample: /board-demo
```

`/board-demo` must:

1. create a run-scoped workspace under
   `.engineering-board/demo/pattern-intelligence/<run-id>/`.
2. copy only the three labeled sample entries and required templates.
3. record a manifest containing relative paths and content hashes before any
   analysis.
4. build deterministic graph facts from the sample.
5. show the candidate cluster, member evidence, relationship reasons, and
   affected domains.
6. create one evidence-linked `status: proposed` hypothesis.
7. show at least one alternative explanation and one falsifier.
8. render a local static visual and print its path.
9. report the exact cleanup command and that modified files will be preserved.

The command must not:

- initialize or edit the user's real board.
- modify a board router, source file, settings file, or Git configuration.
- start PM/Worker mode.
- run code-generation or fix the synthetic issue.
- require an additional network service, service credentials, SQLite, or a
  hosted control plane beyond the already-active agent runtime.
- confirm the proposed root cause.

### 17.4 Data contract

The deterministic graph retains the existing `GRAPH.yml` concepts and adds
stable cluster identity plus exposed signal provenance:

```yaml
clusters:
  - id: C001
    members: [B001, B002, B003]
    patterns: [duplicated-state-contract]
    affected_domains: [hooks, board-view, mcp-server]
    signals:
      - kind: shared-pattern
        value: duplicated-state-contract
        members: [B001, B002, B003]
    density: 1.0
```

The interpreted result is separate Markdown:

```yaml
---
id: H001
type: hypothesis
status: proposed
title: Lifecycle semantics are duplicated across adapters
cluster_id: C001
patterns: [duplicated-state-contract]
confidence: medium
derived_from: [B001, B002, B003]
affected_domains: [hooks, board-view, mcp-server]
created: YYYY-MM-DD
last_evaluated: YYYY-MM-DD
---
```

Required hypothesis sections:

- `## Proposed root cause`
- `## Supporting evidence`
- `## Alternative explanations`
- `## Falsifier`
- `## Outcome history`

Authority rules:

- Graph nodes, edges, cluster membership, and signal values are deterministic
  derived facts.
- `H001` is an agent interpretation and must remain `proposed`.
- Recurrence or confidence alone cannot change it to `confirmed`.
- Confirmation requires an explicit cited investigation or fix outcome.
- Rejection preserves the hypothesis and appends the rejecting evidence.
- A correction changes canonical sample/finding state, then rebuilds derived
  graph state. generated files are never hand-edited as authority.

### 17.5 State, preservation, and cleanup

| Condition | Meaning | Required behavior |
|---|---|---|
| No prior demo run | Clean start | Create a unique run directory and manifest. |
| Complete unchanged run exists | Repeat request | Reuse or create a new run without overwriting the prior run. report which occurred. |
| Prior run is modified | User or external process changed demo content | Preserve it, create a new run, and report why cleanup is withheld. |
| Graph generation fails | Derived analysis is incomplete | Keep canonical sample entries, emit a typed failure, and do not create a hypothesis or claim success. |
| Hypothesis generation fails | Structural result exists but interpretation does not | Show the graph result, label interpretation unavailable, and preserve the run for inspection/retry. |
| Cleanup manifest matches | All targets retain recorded identity and hashes | Remove only the exact run directory and report the removed paths. |
| Cleanup fingerprint differs | Content or scope changed | Refuse deletion, preserve the run, and identify mismatches. |

Demo cleanup is the only destructive boundary in Milestone A. It is limited to
one manifest-owned run directory. It never follows symlinks or reparse points,
never expands to the parent demo root, and never deletes an unmanifested path.

### 17.6 Component and file responsibilities

Proposed implementation map:

- `commands/board-demo.md`: user-facing orchestration, report contract, and
  failure semantics.
- `commands/board-setup.md`: add only the optional demo next step.
- `hooks/scripts/board-demo.sh`: create the contained run, copy fixtures,
  fingerprint artifacts, invoke deterministic analysis, and perform bounded
  cleanup.
- `hooks/scripts/board-graph-build.py`: shared deterministic parser and graph
  builder for explicit board paths. Milestone A integrates it with the demo.
  real-board modifying commands remain unchanged until Milestone B.
- `skills/board-insights/SKILL.md`: interpret a completed cluster into the
  hypothesis schema without changing deterministic graph facts.
- `skills/board-intake/references/hypothesis-schema.md`: normative hypothesis
  fields, sections, states, and authority rules.
- `references/demo/pattern-intelligence/`: the three synthetic canonical
  entries and expected scenario metadata.
- `hooks/scripts/board-view.sh`: render the demo's evidence to cluster  to
  hypothesis drill-down without adding mutation controls.
- `tests/fixtures/pattern-intelligence/`: positive, negative, malformed, and
  cleanup-tamper fixtures.
- `tests/orchestration/board-demo-command.sh`: pin command scope, containment,
  and visible output.
- `tests/orchestration/board-graph-engine.sh`: execute deterministic graph and
  cluster fixtures.
- `tests/orchestration/hypothesis-contract.sh`: validate epistemic state and
  required provenance.
- `tests/integration/pattern-intelligence-first-win.sh`: exercise the complete
  contained journey, retry, and cleanup.

The graph engine must consume the existing entry schema rather than create a
parallel task model. Milestone A may add graph fields needed by the sample, but
must not silently change real-board command behavior.

### 17.7 Failure and security contract

- Malformed sample or graph input to non-zero typed error naming the exact
  relative file. no partial success claim.
- Missing Python runtime to explicit prerequisite error. no package installation.
- Analysis timeout or interpreter failure to preserve the run and print a safe
  retry command.
- Hypothesis output missing required citations or sections to reject the output
  as invalid and leave deterministic graph results available.
- Path escape, symlink, reparse point, manifest expansion, or unexpected file  to
  refuse cleanup.
- Existing user data under the selected run path to never overwrite. allocate a
  new run ID.
- Captured visual and evidence to synthetic data only. no usernames, absolute
  personal paths, tokens, repository secrets, or private findings.
- Demo scripts make no network calls and perform no credential reads, settings
  writes, repository commits, or automatic browser launch. Interpretation uses
  only the already-active agent runtime.

### 17.8 Acceptance-test matrix

| Area | Required proof |
|---|---|
| Positive cluster | Three sample entries produce exactly three nodes, three `shared-pattern` edges, one cluster, three affected domains, and stable membership. |
| Determinism | Repeated analysis of unchanged canonical sample input produces logically identical graph output, excluding documented volatile timestamps. |
| Cross-domain value | The rendered explanation identifies three distinct domains and traces the shared pattern to all member entries. |
| Hypothesis authority | Output is `status: proposed`, cites `B001`-`B003`, includes an alternative and falsifier, and cannot auto-confirm from confidence. |
| Negative fixture | Surface-similar entries without a shared supported signal do not become one durable cluster or hypothesis. |
| Singleton fixture | One finding remains isolated and produces no fabricated systemic hypothesis. |
| Malformed input | A bad entry produces an explicit error and no success/hypothesis artifact. |
| No real-board mutation | Before/after hashes for the router, real board, source tree, settings, and Git configuration are unchanged. |
| Retry | A failed interpretation can retry from preserved deterministic graph state without recopying or mutating canonical sample entries. |
| Cleanup success | An unchanged run is removed completely using only its manifest. |
| Cleanup tamper | Modified, extra, linked, or reparse-point content causes cleanup refusal and preservation. |
| No extra service dependency | With outbound access denied to demo scripts, the journey succeeds using local files and the already-active agent runtime. |
| Visual truth | Static visual is generated from the actual demo result, contains the three evidence nodes and proposed hypothesis, and is captured with provenance and alt text. |
| Existing regression suite | Current setup, graph command, view, permissions, docs, token, security, and orchestration tests remain green. |

### 17.9 Live validation

1. Run the demo in a disposable local Git repository with no existing board.
2. Record elapsed user-directed interaction separately from model execution
   time.
3. Deny outbound access to demo scripts and verify the exact graph,
   proposed-hypothesis label, drill-down, and negative checks.
4. Initialize a real board beside the demo and prove its hashes do not change.
5. Tamper with one demo file and prove cleanup refuses.
6. Restore or create a clean run, execute cleanup, and verify only that run was
   removed.
7. Capture a sanitized static visual from the observed output.
8. Append dated evidence. do not rewrite historical reports.

### 17.10 Documentation-impact contract

When implemented:

| Surface | Required disposition |
|---|---|
| This product spec | Mark Milestone A contract accepted and later record shipped evidence without rewriting the decision history. |
| README and quickstart | Lead the optional first win with pattern intelligence. keep current behavior claims accurate. |
| Landing page | Show the evidence to cluster to proposed-hypothesis outcome only after live validation. |
| Command docs | Add `/board-demo`. revise `/board-setup` optional next step. document cleanup and offline boundaries. |
| Architecture | Document canonical Markdown, deterministic graph facts, interpreted hypotheses, and authority transitions. |
| MCP docs | State unaffected unless an equivalent demo/analysis surface actually ships. |
| Security/privacy | Document contained synthetic data, no-extra-service behavior, path validation, and cleanup refusal conditions. |
| Visuals | Add a real sanitized demo capture with date, source version, alt text, and provenance. |
| Tests/evidence | Add the matrix above and a dated live-validation report. |
| Versions/releases | Review at delivery. change only if the owner separately approves a release. |

### 17.11 Non-goals and delivery boundary

Milestone A does not:

- analyze arbitrary real boards through the new engine by default.
- normalize free-form production tags.
- add semantic embeddings or SQLite.
- confirm hypotheses.
- change resolution, learning confidence, PM/Worker mode, claims, or MCP tools.
- fix the synthetic root cause.
- add cross-repository aggregation or a hosted service.
- merge, release, tag, or deploy without separate owner authorization.

Implementation delivery is this focused branch and draft PR with code, tests,
current-truth documentation, a real visual, and dated evidence. The owner
separately authorized merge, release, tag, publication, and deployment on
2026-07-27. v1.8.0 is the resulting delivery boundary.

## 18. Gate 2 accepted: Milestone B implementation contract

_State: Gate 1 accepted on 2026-07-27. Gate 2 accepted by the product owner on
2026-07-28. Implemented, validated, and shipped as v1.9.1 on 2026-07-28.
Publication state is recorded in dated release evidence._

### 18.1 Milestone purpose

> Make every supported real-finding path converge on the same trustworthy,
> explainable pattern graph so later root-cause reasoning is based on durable
> evidence rather than exact free-form tags or adapter-specific behavior.

Milestone B is the production generalization of the v1.8.0 first win. It does
not add more ambitious interpretation. It makes the evidence-to-graph substrate
reliable enough for Milestone C to interpret.

### 18.2 Canonical pattern and entry contract

Canonical evidence remains repository-owned Markdown. Each reviewed pattern
gets one stable record under the owning board:

```text
engineering-board/<project>/patterns/P001-duplicated-state-contract.md
```

```yaml
---
id: P001
type: pattern
status: active
label: duplicated-state-contract
aliases: [duplicate-state-contract, split-state-contract]
created: YYYY-MM-DD
---
```

Required pattern-record sections:

- `## Definition`: the failure mode, independent of product area.
- `## Inclusion evidence`: what is sufficient to assign the pattern.
- `## Exclusions`: nearby symptoms that do not establish the pattern.
- `## History`: label, alias, merge, retirement, and correction events.

Pattern IDs are allocated from the highest existing `P###` in that board and
are never reused. Labels and aliases normalize by Unicode case folding,
whitespace/hyphen folding, and surrounding-space removal. A normalized label
or alias may resolve to only one active pattern. Renaming a label does not
change its ID. A merged record remains durable with `status: merged` and
`merged_into: P###`. it is never deleted or silently reused.

Entry frontmatter gains an optional canonical assignment:

```yaml
pattern: [split-state-contract]
pattern_ids: [P001]
```

The two fields have different authority:

- `pattern` preserves readable wording supplied or observed at intake and
  remains backward-compatible input.
- `pattern_ids` records the reviewed canonical assignment used for durable
  graph identity.
- the current display label comes from the `P###` record, not from rewriting
  every historical entry.
- assignment and correction reasons are appended to the entry's
  `## Pattern history`. generated graph files are never edited as authority.

Resolution precedence is:

1. an explicit valid `pattern_ids` assignment.
2. an exact unique match from a `pattern` label to a registry label or alias.
3. an exact normalized legacy label represented as
   `legacy:<normalized-label>`.

The third form preserves existing exact-label clustering without pretending an
unreviewed label is a canonical pattern. It must be surfaced in typed
`unresolved_patterns` output. Unknown labels never auto-create `P###` records.
Semantic or agent-authored alias suggestions may appear in a preview, but only
an explicit apply action may write them.

No destructive migration is required. Existing boards with no `patterns/`
directory or `pattern_ids` fields continue to build using the legacy fallback.

### 18.3 User interaction and adapter contract

#### Plugin commands

```text
/board-promote [project] [--session <session-id>]
/board-promote [project] --apply <plan-id>

/board-pattern <project> list
/board-pattern <project> create <label> [--alias <label> ...]
/board-pattern <project> alias <P###> <label>
/board-pattern <project> assign <entry-id> <P###> [--reason "<text>"]
/board-pattern <project> correct <entry-id> --replace <P###|legacy-label> \
  --with <P###> --reason "<text>"
/board-pattern <mutation...> --apply <plan-id>

/board-graph [project] [--full]
```

`/board-promote` previews by default. The preview includes selected scratch
IDs, target board, duplicate disposition, proposed entry type, pattern
resolution, proposed new pattern records, rejection/defer reasons, and a
content-bound `plan_id`. It performs no canonical write.

`--apply <plan-id>` is valid only for the unchanged scratch inputs, router,
target entry set, pattern registry, and next-ID state included in that plan.
The command emits a typed per-finding receipt and rebuilds `BOARD.md` and
`GRAPH.yml` after successful canonical writes. A direct user request to promote
is apply authority. otherwise the interactive agent must show the preview and
obtain approval.

PM mode retains its already-authorized per-turn promotion behavior, but its
consolidator must invoke the same planner, validator, pattern resolver, writer,
and receipt model. It may not retain a separate promotion implementation.

`/board-pattern` is read-only for `list` and preview-first for every mutation.
`correct` preserves the prior assignment and reason in Markdown history.

`/board-graph` uses the shared engine in automatic incremental mode. `--full`
ignores and replaces only the disposable cache. Both modes must produce the
same logical graph from the same canonical source snapshot.

#### MCP surface

Milestone B adds three tools:

| Tool | Contract |
|---|---|
| `board_promote_findings` | Preview or apply captured scratch findings using the same content-bound plan and per-finding receipt as `/board-promote`. |
| `board_patterns` | List patterns or preview/apply create, alias, assign, and correct operations using the same registry rules as `/board-pattern`. |
| `board_graph` | Build or return the typed deterministic graph using the shared full/incremental engine. |

Existing `board_create_entry` and `board_update_entry` accept `pattern_ids`,
validate them against the selected board, and return pattern-resolution
warnings. Existing `pattern` input remains supported. Existing tool behavior
outside pattern handling remains compatible.

Plugin and MCP outputs need not use identical presentation, but they must agree
on canonical IDs, normalized labels, unresolved labels, nodes, edges, clusters,
relationship reasons, source fingerprints, and typed failure codes.

### 18.4 State, authority, and preservation

| Condition | Meaning | Authoritative owner | Required behavior | Preservation |
|---|---|---|---|---|
| Scratch captured | Evidence exists but is not canonical project truth | Scratch file plus capture provenance | Include in foreground preview. do not graph as a live entry | Keep until applied, explicitly rejected, or manually retained |
| Promotion previewed | A deterministic write proposal exists | Content-bound plan | Return plan and warnings. write nothing canonical | Preserve scratch and current board |
| Promotion applied | Explicit authority accepted the unchanged plan | Entry and pattern Markdown | Write each idempotent finding once, record receipt, rebuild derived views | Archive processed scratch only after its canonical write is verified |
| Pattern unresolved | A readable label has no reviewed registry identity | Entry `pattern` field | Preserve legacy exact-label behavior and expose unresolved status | Never invent or silently persist a `P###` |
| Pattern assigned | Entry cites a valid active `P###` | Entry `pattern_ids` plus pattern record | Use stable ID for graph identity and expose assignment provenance | Preserve observed label and history |
| Pattern corrected | Reviewed assignment changed | Entry and its appended history | Replace the canonical reference only through an explicit plan | Preserve old ID, reason, timestamp, and actor/source |
| Pattern merged | Two canonical identities are intentionally unified | Durable source and target pattern records | Resolve the old ID to `merged_into` and expose that resolution | Never delete or reuse the old record |
| Graph current | Derived source fingerprint matches canonical inputs | Canonical Markdown snapshot | Serve graph facts | Cache may be deleted and rebuilt |
| Graph stale or invalid | Inputs changed or parsing failed | Canonical Markdown remains authoritative | Return typed stale/invalid state. do not claim current intelligence | Preserve last good graph and all canonical evidence |

Canonical precedence is entry and pattern Markdown, followed by the generated
`GRAPH.yml`, followed by the disposable local cache. A cache, graph, or command
receipt can never override canonical Markdown.

Promotion apply and pattern mutation are the only new durable-write
boundaries. Graph build and graph retrieval are read-only with respect to
canonical evidence.

### 18.5 Deterministic graph and incremental rebuild contract

The production graph schema adds:

- `schema_version`.
- `source_fingerprint` over sorted canonical relative paths and content hashes.
- per-node `pattern_ids`, resolved display labels, original labels, resolution
  kind, and source field.
- typed `unresolved_patterns`.
- `pattern_id` and source-entry/field provenance on `shared-pattern` edges.
- a deterministic cluster `fingerprint` derived from sorted member IDs,
  relationship kinds, and canonical pattern identities.
- `build_mode: full|incremental` as diagnostic metadata, not graph meaning.

Existing display IDs such as `C001` remain ordered presentation identifiers.
Consumers that need continuity use the cluster fingerprint.

Incremental state lives only at:

```text
.engineering-board/cache/graph/<project>/state.json
```

It stores schema version, source fingerprints, and parsed per-file facts. It
contains no evidence unavailable from canonical Markdown and must be ignored
by Git. Incremental rebuild may reuse unchanged parsed facts, but global edges,
clusters, findings, and output ordering are recomputed deterministically from
the complete logical entry set.

The engine writes candidate graph and cache files to same-directory temporary
paths, rechecks the canonical source fingerprint, and atomically replaces
derived outputs only when the snapshot is unchanged. A concurrent source
change returns `source_changed` and preserves the prior graph/cache.

For identical canonical inputs:

- full and incremental builds must have identical logical graph content.
- deleting the cache and rebuilding must recover the same logical graph.
- only documented volatile metadata such as `generated_at` and diagnostic
  `build_mode` may differ.
- plugin and MCP adapters must return the same source fingerprint and graph
  facts.

No SQLite, embedding store, network service, or required package dependency is
introduced.

### 18.6 Component and file responsibilities

- `mcp-server/engineering_board_core.py`: new zero-dependency shared core for
  entry parsing, pattern-registry parsing and normalization, source
  fingerprinting, graph construction, incremental-state validation, promotion
  planning, and typed domain errors. It contains no MCP or Claude-specific
  presentation.
- `mcp-server/engineering_board_mcp.py`: retain JSON-RPC transport and tool
  schemas. delegate graph, pattern, direct-entry pattern handling, and
  promotion behavior to the shared core.
- `mcp-server/pyproject.toml`: package both the MCP adapter and shared core
  without adding a runtime dependency.
- `hooks/scripts/board-graph-build.py`: become the thin CLI adapter over the
  shared graph core while retaining the explicit-board-path contract used by
  the demo.
- `hooks/scripts/board-intake.py`: new local CLI adapter for deterministic
  create, promote-plan/apply, and pattern-plan/apply operations.
- `hooks/scripts/board-consolidate.sh`: retain Stop-hook/transcript framing and
  PM authority, but delegate validation, deduplication, pattern resolution,
  canonical writes, and receipts to the shared intake core.
- `commands/board-promote.md`: foreground preview/apply interaction, authority,
  typed receipt, retry, and preservation behavior.
- `commands/board-pattern.md`: pattern registry, alias, assignment, and
  correction interaction without opaque-cache editing.
- `commands/board-graph.md`: shared-engine invocation, incremental/full
  behavior, typed output, and unresolved-pattern reporting.
- `skills/board-intake/SKILL.md`: use the deterministic intake adapter after
  duplicate review instead of independently serializing canonical files.
- `skills/board-intake/references/frontmatter-schema.md`: define
  `pattern_ids`, legacy `pattern` semantics, and `## Pattern history`.
- `references/required-permissions.json` and plugin metadata: add only the
  command/script permissions and discovery entries required by the new
  surfaces.
- `tests/orchestration/milestone-b-pattern-pipeline.sh`: consolidated
  deterministic matrix for registry normalization, stable identity, aliases,
  merge preservation, legacy fallback, preview/apply, promotion outcomes,
  correction history, MCP/plugin parity, source-change refusal, link refusal,
  and full/incremental/cache-deleted equivalence.
- `tests/orchestration/board-graph-engine.sh`: retained executable positive,
  negative, deterministic, and malformed-input graph fixtures.
- `mcp-server/test_mcp_server.py`: retained full stdio, lifecycle,
  compatibility, packaging, and typed-failure coverage. the shared matrix
  invokes the new MCP tools against the same canonical snapshot as the CLI.

Implementation may adjust mechanical module boundaries after repository
mapping, but it may not create a second parser, resolver, graph algorithm, or
canonical data model. Any boundary change that affects authority, compatibility,
or the user contract reopens alignment.

### 18.7 Failure, retry, and security contract

- Invalid pattern ID, duplicate normalized label/alias, merge cycle, malformed
  pattern record, or conflicting assignment to typed validation error naming
  only safe relative paths. no canonical or derived partial write.
- Changed or expired plan inputs to `plan_stale`. write nothing and return a
  fresh-preview instruction.
- Duplicate scratch provenance already promoted to idempotent `already_applied`
  receipt. never allocate another entry.
- Promotion deduplication, provenance lookup, and identifier allocation read
  the complete canonical entry lifecycle, including resolved entries. Graph
  construction continues to exclude resolved entries from active ranking.
- One finding fails during a multi-finding apply to report per-finding results,
  preserve every unverified scratch finding, and make retry idempotent from the
  durable receipt. Never claim all-or-nothing atomicity across files.
- Missing Python to explicit prerequisite error. never install packages.
- Cache missing, corrupt, stale, or from another schema version to discard only
  the cache and perform a full rebuild.
- Canonical source changes during analysis to `source_changed`. preserve the
  last good derived output and retry from a fresh snapshot.
- Graph input invalid to name the safe relative source and preserve the last
  good graph. do not emit a partial replacement.
- Path escape, symlink, junction, or reparse point in a mutation or cache path
  to refuse the operation.
- Scratch and entry contents remain untrusted data. Existing injection,
  transcript-anchor, one-line serialization, and HTML-escaping defenses remain
  mandatory and must cover the new shared paths.
- No graph read, alias suggestion, or preview may mutate canonical state,
  resolve an entry, confirm a hypothesis, execute code, commit, push, or access
  credentials.
- Receipts and dated evidence must exclude secrets, transcript bodies,
  usernames, and absolute personal paths.

### 18.8 Deterministic acceptance-test matrix

| Area | Required proof |
|---|---|
| Three-path convergence | One plugin direct intake, one foreground scratch promotion, and one MCP-created entry using three approved aliases resolve to the same `P###` and one evidence-linked cross-domain cluster. |
| Pattern identity | Changing the canonical label preserves `P###`, memberships, and cluster fingerprint while updating the displayed label. |
| Alias uniqueness | Case/whitespace/hyphen-equivalent labels or aliases cannot map to two active pattern records. |
| Legacy compatibility | A board with only existing `pattern` labels and no registry builds successfully, retains exact-label clustering, and reports `legacy:` unresolved identities. |
| Unknown-label authority | An unmatched or semantic suggestion appears in preview/output but creates no pattern record or canonical assignment without apply authority. |
| Assignment provenance | Every canonical shared-pattern edge identifies the pattern ID and the member entry fields that support it. |
| Correction | Replacing a bad assignment updates only the intended canonical Markdown and derived relationships, preserves history, and removes the stale edge after rebuild. |
| Merge preservation | A merged pattern ID resolves to its durable target without deleting the old record or duplicating cluster membership. |
| Adapter parity | Plugin and MCP builds from the same snapshot return equal source fingerprints, normalized pattern facts, edges, clusters, and typed findings. |
| Full/incremental equivalence | Full build, unchanged incremental build, one-file incremental build, and cache-deleted rebuild produce equal logical graphs. |
| Determinism | Repeated builds have stable ordering, edge provenance, pattern identity, and cluster fingerprints apart from documented volatile metadata. |
| Concurrent change | A canonical edit between scan and replace returns `source_changed` and leaves the prior graph/cache intact. |
| Preview/apply | Preview writes nothing. unchanged apply succeeds once. changed inputs make the plan stale. retry cannot duplicate an entry. |
| Promotion outcomes | Created, deduplicated, rejected, deferred, and already-applied findings receive explicit typed receipts and only verified applied scratch is archived. |
| Malformed input | Invalid entries, registry records, caches, and plans fail closed without partial canonical or graph replacements. |
| Security regression | Hostile scratch/frontmatter strings remain data, path/link escapes are refused, and rendered output stays escaped. |
| No extra infrastructure | The complete pipeline works with outbound access denied, no database, and only the supported Python runtime. |
| Existing behavior | Current intake, PM/Worker modes, setup, view, resolve, claims, demo, MCP, permissions, security, documentation, and release-tree tests remain green. |

### 18.9 Live validation

1. Create a disposable local repository using the released setup path.
2. Create one real fixture entry through direct plugin intake, capture and
   foreground-promote a second, and create a third through MCP.
3. Use distinct readable aliases approved in one `P###` record and verify one
   cross-domain cluster with source-linked relationship reasons.
4. Compare plugin and MCP graph results from the same source fingerprint.
5. Rename the canonical display label, correct one assignment, and verify
   identity continuity plus the expected edge change.
6. Compare full, incremental, and cache-deleted rebuilds.
7. Change a canonical file during a controlled build and verify refusal to
   replace the prior graph.
8. Deny outbound access to the scripts and verify the journey remains local.
9. Capture a sanitized terminal or static graph view generated from the actual
   result, with source commit, date, alt text, and provenance.
10. Remove only the disposable validation repository and append dated evidence.
    preserve prior Milestone A and release reports unchanged.

### 18.10 Documentation-impact contract

When implemented:

| Surface | Required disposition |
|---|---|
| This product spec | Mark Gate 2 accepted, then record implementation and release state without rewriting decision history. |
| Entry/pattern schemas | Document `P###` records, `pattern_ids`, legacy fallback, precedence, corrections, and merge preservation. |
| README and setup | Show real finding-to-graph value and the foreground promote path without making PM/Worker mode mandatory. |
| Plugin command docs | Add promote/pattern contracts and update graph behavior, permissions, failure, and retry guidance. |
| MCP docs and manifests | Document the three tools, extended entry/update fields, tool count, packaging, and semantic parity only after tests pass. |
| Architecture | Replace adapter-specific graph/promotion descriptions with the shared-core, canonical/derived, cache, and authority model. |
| Security/privacy | Document preview/apply authority, untrusted-data handling, path containment, receipts, cache contents, and local-only behavior. |
| Visuals | Add a real sanitized graph/terminal capture if user-facing output changes. preserve the v1.8.0 synthetic demo provenance. |
| Changelog and versions | Record behavior in Unreleased. coordinate versions and release claims only at the actual release boundary. |
| Tests/evidence | Add the matrix above and a dated live-validation report. keep volatile totals and run results out of timeless prose. |
| Historical reports | Preserve Milestone A and v1.8.0 evidence as historical state and append superseding Milestone B observations. |

README, landing-page, setup, examples, architecture, security, MCP metadata,
visuals, and release claims must each be updated or recorded as reviewed and
unaffected in the implementation change. A passing path or keyword test does
not establish semantic alignment.

### 18.11 Non-goals and delivery boundary

Milestone B does not:

- generate, rank, confirm, reject, split, or merge root-cause hypotheses.
- add embeddings or an autonomous semantic-similarity authority.
- replace Markdown or require SQLite.
- aggregate across repositories.
- add a hosted service, daemon, login, organization, billing, or cloud sync.
- turn read-only graph requests into code execution or project mutation.
- silently promote captures, create aliases, assign patterns, or resolve work.
- redesign the pattern-focused HTML experience planned for Milestone C.
- remove PM/Worker modes or change the TDD/review/validate state machine.
- implement the persistent supervisor from RFC 0001.

Implementation shipped through reviewed PRs #97 and #98. The v1.9.1 release
passed the contract and publication gates. Publication does not weaken this
contract or authorize unvalidated Milestone C behavior.

## 19. Gate 2 accepted: Milestone C implementation contract

_State: Gate 1 and Gate 2 accepted by the product owner on 2026-07-28.
Implemented, validated, and shipped as v1.10.0 on 2026-07-28._

### 19.1 Milestone purpose

> Turn trustworthy structural clusters into ranked, inspectable root-cause
> proposals that agents can evaluate over time without confusing correlation
> with causation or repeating rejected explanations.

Milestone B can show which findings are connected and why. The acting agent
must still interpret every cluster from scratch, decide which cluster matters,
and remember failed explanations in chat. Milestone C moves that work into a
bounded product contract:

```text
canonical evidence
  → deterministic graph
  → transparent cluster ranking
  → agent-authored proposal with exact citations
  → explicit preview/apply
  → confirmed | weakened | rejected | split | merged
  → durable negative memory and outcome history
```

The user benefit is earlier recognition of a shared engineering cause, with
enough visible evidence and counter-evidence to investigate the system instead
of repeatedly patching symptoms.

### 19.2 Comparative benefit and selected direction

| Aspect | v1.9.1 behavior | Milestone C behavior | Why it matters |
|---|---|---|---|
| Cluster priority | The graph returns stable clusters in structural order. | A deterministic score exposes recurrence, domain diversity, severity, relative recency, and evidence quality separately. | Agents can inspect the highest-value systemic candidate first without treating the score as causal confidence. |
| Interpretation | The contained demo can create one synthetic proposed hypothesis. Real boards require ad hoc chat reasoning. | `/board-insights` prepares a strict, evidence-complete proposal for one real cluster. | Useful reasoning becomes reproducible and repository-visible. |
| Authority | Production graph facts are deterministic. no production hypothesis writer exists. | Proposal and evaluation mutations use content-bound preview/apply plans. Confirmation requires an explicit outcome-evidence action. | An agent cannot silently convert correlation into truth. |
| Failed explanations | Rejection can be written manually but has no production query or suppression contract. | Rejected claim identities remain queryable and suppress unchanged reproposals. | Later sessions do not recycle a disproven explanation without new evidence. |
| Inspection | The normal HTML view emphasizes entry lifecycle. | A read-only pattern-intelligence section shows ranked clusters, evidence, hypotheses, status, and stale bindings. | The accumulated intelligence is visible without reading graph serialization. |

The current v1.9.1 behavior remains preferable for users who only need
deterministic structure or do not want agent interpretation. `/board-graph`
stays independent, offline, deterministic, and sufficient for that use case.

Selected and implemented items:

| Item | Purpose | Capability or safety property | If omitted |
|---|---|---|---|
| Transparent ranking | Order clusters without hiding the basis | Reproducible investigation priority with exposed factors | Agents must rescan every cluster and may overvalue a large but low-quality group |
| Canonical H### records | Keep one inspectable explanation and its evidence | Cross-session reasoning with stable identity and Git history | Root-cause reasoning remains disposable chat context |
| Explicit evaluation and negative memory | Learn from investigation outcomes | Rejected explanations remain visible and unchanged reproposals are blocked | Later agents repeat disproven theories |
| Shared plugin/MCP core | Give supported adapters the same facts and mutation rules | Adapter parity and one security boundary | Clients can disagree about status, stale evidence, or authority |
| Pattern-intelligence view | Make ranked evidence and hypothesis state inspectable | Read-only, escaped visual drill-down | The core capability remains hidden behind YAML and Markdown scanning |

Alternatives considered:

1. Keep all interpretation ephemeral. This has the least implementation cost,
   but it preserves repeated rediscovery and cannot provide negative memory.
2. Generate deterministic hypothesis templates without agent interpretation.
   This preserves reproducibility, but a template can restate graph structure.
   it cannot responsibly infer a shared causal mechanism.
3. Let a model write or confirm hypotheses directly. This is faster but
   collapses the evidence, inference, and authority boundaries. It is rejected.
4. Use deterministic ranking and validation around agent-authored proposals,
   then require explicit apply and evaluation actions. This is the selected
   direction because it adds useful interpretation while preserving visible
   evidence and user authority.

### 19.3 Deterministic cluster ranking

The shared core adds a pure ranking function over the current graph. It does
not call a model, write canonical state, or change topology.

Each cluster receives a score from 0 through 100:

| Component | Maximum | Rule |
|---|---:|---|
| Recurrence | 25 | `min(member_count, 5) × 5` |
| Domain diversity | 25 | `min(distinct_affected_domains, 5) × 5` |
| Severity | 20 | Highest member priority: P0=20, P1=15, P2=10, P3=5, absent=0 |
| Relative recency | 15 | Newest valid member `discovered` date compared with the newest valid date in the corpus: 0-7 days=15, 8-30=10, 31-90=5, older or unknown=0 |
| Evidence quality | 15 | `floor(10 × members_with_canonical_pattern_ids / member_count)` plus 5 when the cluster contains at least two distinct deterministic signal kinds |

The result includes every component, input count, warning, and rule version.
The score ranks investigation opportunities. It is not probability,
confidence, severity authority, or evidence of causation. Ties sort by stable
cluster fingerprint. Relative recency uses canonical dates, not the wall
clock, so the same canonical input produces the same ranking.

`GRAPH.yml` adds member `discovered` dates when present. It does not store
rankings. Ranking remains a rebuildable read model returned at the point of
use.

### 19.4 Production hypothesis schema

Real-board hypotheses are canonical Markdown under:

```text
engineering-board/<project>/hypotheses/H###-<slug>.md
```

Existing boards require no migration. The first hypothesis apply creates the
directory. `/board-init` adds it for new boards.

Required frontmatter:

```yaml
---
id: H001
type: hypothesis
status: proposed
title: One suspected shared mechanism
claim_key: duplicated-lifecycle-contract
claim_fingerprint: h-<16 lowercase hex>
cluster_fingerprint: c-<16 lowercase hex>
graph_source_fingerprint: <64 lowercase hex>
pattern_ids: [P001]
confidence: medium
derived_from: [B001, B002, B003]
affected_domains: [hooks, mcp-server, view]
supersedes: []
created: YYYY-MM-DD
last_evaluated: YYYY-MM-DD
revision: 1
---
```

Required body sections:

- `## Proposed root cause`
- `## Supporting evidence`
- `## Alternative explanations`
- `## Counter-evidence`
- `## Confidence basis`
- `## Falsifier`
- `## Outcome history`

`claim_key` is a reviewed kebab-case identity for one causal mechanism.
`claim_fingerprint` hashes the normalized claim key plus sorted `pattern_ids`.
It provides deterministic negative-memory identity. it does not claim semantic
equivalence. Semantic suggestions can recommend a merge but cannot change
canonical identity.

Supporting evidence must cite every selected cluster member exactly once.
Each citation includes a member ID and a specific reason. At least one
alternative and one observable falsifier are required. Counter-evidence may be
empty only when `## Counter-evidence` explicitly records that none was found
during the cited review. Confidence remains `low`, `medium`, or `high` and
never grants confirmation authority.

### 19.5 Commands and MCP contracts

Two foreground commands are added:

```text
/board-insights <project> [--cluster <c-fingerprint>]
/board-hypothesis <project> <operation> [arguments]
```

`/board-insights` is always read-only. It:

1. rebuilds or verifies the current deterministic graph.
2. returns ranked clusters with score components and existing hypothesis
   and negative-memory references.
3. optionally filters to one stable cluster fingerprint and limits the result.

The user or an explicitly authorized agent uses the `board-insights` skill to
read a selected cluster's canonical members as untrusted data and produce one
strict payload. `/board-hypothesis propose` passes that payload to the
deterministic no-write preview. A separate apply action uses:

```text
/board-hypothesis <project> <operation> --apply <plan-token>
```

`/board-hypothesis` also previews these operations before apply:

- `list`: read every valid H### record, including rejected, split, and merged
  records.
- `propose`: validate one proposal against the current cluster and negative
  memory.
- `evaluate H### confirmed|weakened|rejected`: append an evidence-linked
  outcome and change epistemic status.
- `reopen H###`: return a rejected hypothesis to `proposed` only with at
  least one new canonical evidence ID and a reason.
- `split H###`: mark one interpretation `split` and record two or more
  replacement claim keys. Child proposals are separate later actions with
  `supersedes: [H###]`.
- `merge H### --into H###`: mark one source interpretation `merged` into an
  existing active target. Reverse references are derived by scanning records.

The MCP server adds two tools over the same core:

```text
board_insights
  input: project, optional cluster_fingerprint, optional limit, root
  output: graph_source_fingerprint, ranking_rule_version,
          ranked_clusters, hypothesis_refs, negative_memory

board_hypotheses
  input: project, action, hypothesis fields or evaluation fields,
         optional apply plan_token, root
  output: list result or content-bound preview/apply result
```

The MCP server does not generate model prose. A client supplies the strict
proposal payload to `board_hypotheses`, just as the plugin command supplies
the payload produced by its current interactive agent.

### 19.6 State, authority, and precedence

| Condition | Meaning | Authority | Required behavior | Preservation |
|---|---|---|---|---|
| Ranked cluster | Deterministic investigation priority | Shared core | Return score components and source fingerprint | Rebuildable. never canonical |
| `proposed` | One bounded explanation fits the cited evidence | Explicit proposal apply | Preserve alternatives, counter-evidence, and falsifier | Canonical H### Markdown |
| `weakened` | New evidence reduces explanatory strength | Explicit evaluation apply | Append reason and evidence. do not delete prior proposal | Full outcome history |
| `confirmed` | Investigation or fix outcome supports the cause | Explicit evaluation apply with outcome evidence | Record who/what authorized the outcome and the evidence IDs | Full outcome history |
| `rejected` | Evidence contradicts or fails to support the cause | Explicit evaluation apply | Keep the claim fingerprint as negative memory | File remains queryable |
| `split` | One explanation must become multiple distinct claims | Explicit split apply | Record replacement claim keys. create children only through later proposal applies | Parent remains terminal history |
| `merged` | One explanation is the same canonical interpretation as another | Explicit merge apply | Record the active target H### | Source remains terminal history |
| Stale binding | Graph source or selected cluster changed after preview | Shared core | Refuse apply and require a new preview | Existing canonical files unchanged |

Authority precedence:

1. The latest explicit owner decision.
2. Canonical entry, pattern, and hypothesis Markdown.
3. Explicit hypothesis outcome history.
4. Deterministic graph and ranking read models.
5. Agent-authored proposed interpretation.

A rank score or model statement cannot override canonical evidence or set
`confirmed`. Milestone C does not automatically create a Learning. Outcome-to-
learning feedback remains Milestone D.

### 19.7 Negative memory and transition rules

A rejected record blocks a new `propose` operation when its
`claim_fingerprint` is equal to the proposed claim fingerprint. The preview
returns `blocked_by_negative_memory`, the H### ID, the rejecting outcome, and
the evidence already evaluated.

The agent must use `reopen`, not create a duplicate. Reopen requires:

- at least one canonical evidence ID not present in the hypothesis history.
- a specific `new_evidence_reason`.
- the current cluster fingerprint that contains the retained and new evidence.
- an unchanged content-bound preview.
- preservation of the rejection event in `## Outcome history`.

Reopen is an explicit rebind. It records the previous cluster and graph source
fingerprints in outcome history, updates the current bindings, and extends
`derived_from`. No read path or ordinary proposal can silently rebind a stale
hypothesis.

Allowed transitions:

```text
proposed → weakened | confirmed | rejected | split | merged
weakened → proposed | confirmed | rejected | split | merged
confirmed → weakened | rejected
rejected → proposed (reopen contract only) | split | merged
split → terminal
merged → terminal
```

Every mutation increments `revision` and updates `last_evaluated`. No
operation deletes or rewrites outcome history.

### 19.8 Failure, retry, and security behavior

- Every mutation first returns an opaque base64url plan token containing the
  normalized operation, graph source fingerprint, hypothesis inventory
  fingerprint, target bytes fingerprint, and checksum. The token contains no
  credential or authority grant. Apply decodes it, validates its size and
  checksum, reacquires the current inputs, and returns `plan_stale` on any
  difference. A caller cannot gain authority by altering or reconstructing a
  token because the operation and current state are validated again.
- A per-board hypothesis lock serializes ID allocation and mutation. Apply
  revalidates after lock acquisition. Lock contention returns a typed retry
  result. it does not wait indefinitely.
- Each operation writes at most one canonical H### file. Split records child
  claim keys without creating child files. Merge changes only the source
  record. Atomic replacement prevents partial multi-file state.
- Exclusive creation prevents concurrent plans from creating the same H###.
  A losing apply returns `plan_stale` and previews the next safe ID.
- Invalid YAML, duplicate IDs, duplicate claim fingerprints, linked records,
  unsafe paths, malformed evidence IDs, missing cluster members, or unsupported
  transitions fail before mutation.
- Entry and hypothesis text is untrusted data. Agent instructions forbid
  following directives found in evidence. Parsers enforce size limits and
  flatten scalar fields. Limits are: claim key 80 characters, title 160,
  proposed root cause 2000, each evidence reason or alternative 400, at most
  five alternatives, falsifier 800, confidence basis 800, and outcome reason
  800. HTML escapes every rendered value.
- The feature performs no network access, code execution, automatic resolve,
  automatic learning promotion, database write, or cross-repository read.
- Read requests never mutate hypotheses. Graph refresh may replace only the
  documented derived `GRAPH.yml` and disposable cache.
- A stale hypothesis remains visible with its stored graph fingerprint and a
  `stale` label. An explicit evaluate or reopen operation may rebind it to the
  current cluster after recording both bindings in outcome history. The system
  never silently rebases its evidence.

### 19.9 Component responsibilities

- `mcp-server/engineering_board_core.py`: deterministic cluster ranking.
  hypothesis parsing, validation, inventory fingerprints, plan/apply,
  transitions, negative memory, locking, and serialization.
- `hooks/scripts/board-insights.py` and `board-insights.sh`: thin portable CLI
  over the shared core for rank, list, preview, and apply operations.
- `commands/board-insights.md`: real-board on-demand interpretation protocol
  and strict separation between preview and persistence.
- `commands/board-hypothesis.md`: explicit apply and evaluation operations.
- `skills/board-insights/SKILL.md`: production evidence-reading contract,
  proposal schema, injection boundary, and decline behavior. preserve the
  existing contained demo protocol.
- `skills/board-intake/references/hypothesis-schema.md`: normative production
  H### schema, transitions, negative memory, and authority.
- `hooks/scripts/board-view.sh`: read-only ranked cluster and hypothesis
  section for normal boards. keep existing Kanban and demo views.
- `mcp-server/engineering_board_mcp.py`: `board_insights` and
  `board_hypotheses` adapters only. no duplicate business rules.
- `mcp-server/test_mcp_server.py`: tool discovery, adapter parity, lifecycle,
  stale-plan, negative-memory, and stdout safety coverage.
- `tests/orchestration/milestone-c-root-cause-intelligence.sh`: deterministic
  end-to-end evidence matrix.
- `tests/view/automated.sh`: escaped ranked-cluster and hypothesis rendering,
  terminal states, and stale labels.
- `references/required-permissions.json`: only the bounded shared CLI command
  needed by the two foreground commands.
- `README.md`, `ARCHITECTURE.md`, `SECURITY.md`, `commands/board-view.md`,
  `mcp-server/README.md`, `docs/index.html`, and `docs/llms.txt`: current user,
  setup, architecture, security, adapter, and product-view truth.
- `docs/assets/`: one sanitized visual generated from the real Milestone C
  fixture, with date, source version, alt text, and provenance.
- Coordinated manifests and changelog: version and tool/command counts updated
  only at the release boundary.

### 19.10 Deterministic acceptance matrix

| Sequence | Failure injection | Expected semantic outcome | Durable evidence | Test |
|---|---|---|---|---|
| Rank three clusters with different recurrence, domains, priorities, dates, and pattern coverage | Equal totals on two clusters | Components are visible. ties sort by stable fingerprint. repeat runs are equal | Returned ranking payload | Milestone C matrix |
| Request one real cluster through plugin CLI and MCP | Two adapters | Both return the same ranked facts, evidence members, hypothesis refs, and negative-memory facts | Compared JSON payloads | Milestone C matrix and MCP suite |
| Preview a valid proposal that cites every member | No apply token | No H### file exists. preview returns the next ID and bound plan | Plan payload only | Milestone C matrix |
| Change an entry or pattern after preview | Stale graph source | Apply returns `plan_stale`. no hypothesis file is written | Unchanged hypothesis inventory | Milestone C matrix |
| Supply missing member evidence, an extra ID, no alternative, no falsifier, or unsafe scalar content | Malformed agent output | Preview rejects the payload before mutation | Typed validation errors | Hypothesis contract and security suites |
| Apply one valid proposal | Concurrent second plan for the same next ID | Exactly one H### is created. the loser receives a retry/stale result | Canonical H### and outcome receipt | Milestone C matrix |
| Reject H001, then propose the same claim fingerprint | Unchanged explanation | New proposal is blocked and cites H001 negative memory | Preserved rejected H001 | Milestone C matrix |
| Reopen rejected H001 without new evidence, then with one new canonical member | Missing then valid novelty | First request is rejected. second returns to proposed and retains rejection history | Revised H001 history | Milestone C matrix |
| Confirm a proposal without outcome evidence, then with explicit evidence | Missing authority evidence | First preview fails. second records confirmation without changing entries or creating a Learning | Revised H### history | Milestone C matrix |
| Split H001 into two claim keys | Child creation failure is not possible in the split action | H001 becomes terminal `split`. no child file appears until separate proposal applies | H001 split record | Milestone C matrix |
| Merge H002 into active H003 | Missing or terminal target | Invalid target fails. valid merge changes only H002 and reverse lookup finds it from H003 | H002 merge record | Milestone C matrix |
| Render normal board view with proposed, rejected, stale, split, and merged records | Crafted HTML and prompt text in evidence | Output escapes content, labels each state, exposes citations, and contains no mutation controls | Generated HTML | View and security suites |
| Delete GRAPH.yml and disposable cache | Missing read model | Shared core rebuilds equal graph/ranking facts. hypotheses remain unchanged | Rebuilt graph and compared ranks | Milestone C matrix |
| Run with outbound proxies pointed at a closed local port | Network unavailable | Complete ranking, proposal, evaluation, and view sequence stays green | Dated offline result | Milestone C matrix |
| Run all existing suites | Compatibility regression opportunity | Milestone A/B, claims, modes, capture, view, package, and MCP behavior remain green | Full release-tree result | `tests/run-all.sh` |

### 19.11 Live validation and visual evidence

Implementation validation uses a disposable repository fixture with:

- at least three clusters.
- one cross-domain high-priority cluster.
- one valid proposed hypothesis.
- one rejected explanation that exercises negative memory.
- one new item that permits an evidence-backed reopen.
- malicious Markdown and HTML strings that must remain inert.

The run must use the real plugin CLI, shared core, MCP stdio adapter, and normal
HTML renderer. It must run offline. The report records logical results,
sanitized paths, source commit, graph and hypothesis fingerprints, and cleanup.
The visual is generated from this actual fixture. A conceptual mockup is not
release evidence.

### 19.12 Documentation alignment and delivery

The implementation change must update or substantively review:

- the central product spec and this contract state.
- README quickstart, command list, MCP table, and product claims.
- command and skill contracts.
- hypothesis schema and graph schema.
- architecture and security/privacy boundaries.
- normal HTML view documentation and a real visual.
- MCP package, manifests, tool counts, and installation docs.
- changelog, coordinated versions, deterministic tests, and dated evidence.
- historical v1.8.0 and v1.9.1 reports, which remain unchanged.

The release boundary is v1.10.0 because Milestone C adds user-visible commands,
canonical hypothesis behavior, HTML output, and MCP tools. PR #101 merged the
implementation. The v1.10.0 tag, GitHub Release, PyPI package, official MCP
Registry record, and Pages deployment were then validated. The dated release
report records the immutable digests, workflow runs, and live observations.

### 19.13 Explicit non-goals

Milestone C does not:

- use a model to build or modify deterministic graph topology.
- treat ranking as confidence or confirmation.
- automatically apply a proposal or evaluation.
- automatically resolve entries or create/update Learnings.
- execute a proposed fix.
- add embeddings, SQLite, a hosted service, or cross-repository aggregation.
- add SessionStart retrieval or task-context retrieval from Milestone D.
- redesign PM/Worker orchestration or the TDD/review/validate state machine.
- delete rejected, split, merged, or stale hypotheses.
- claim semantic duplicate detection beyond reviewed `claim_key` identity.

Gate 2 approval authorizes implementation of this contract. It does not
authorize the deferred Milestone D or E scope.

## 20. Gate 2 accepted: Milestone D implementation contract

_State: Gate 1 and Gate 2 accepted by the product owner on 2026-07-28.
Milestone D shipped in v1.11.0 on 2026-07-29._

### 20.1 Milestone purpose

> Make relevant systemic memory difficult for an agent to miss when it chooses
> a fix, then use explicit fix outcomes to improve the memory that a later
> agent receives.

Current workflow:

1. Engineering Board captures and promotes findings.
2. The shared graph builds patterns and clusters.
3. `/board-insights` ranks systemic investigations.
4. H### records preserve proposed, confirmed, weakened, rejected, split, and
   merged explanations.
5. SessionStart separately counts exact pattern labels and filters Learnings
   by the current directory.

The current workflow can contain the correct systemic memory without giving it
to the acting agent. The agent must know when and how to request the memory.
Resolution also does not carry a structured fix result into Learning
confidence. The product can therefore preserve intelligence without using or
improving it at the next decision.

Milestone D changes the actor that performs retrieval. The product, not the
user, performs a bounded relevance check when a work session or investigation
begins. The user or an explicitly authorized agent retains authority over every
canonical hypothesis, outcome, resolution, and Learning change.

Implementation is divided into two ordered slices:

1. **D1: Contextual retrieval.** Deliver a source-linked context brief through
   SessionStart, relevant UserPromptSubmit events, a foreground command, and
   MCP.
2. **D2: Outcome learning.** Record an explicit fix outcome in H### history,
   then preview any resulting Learning change through the same shared core.

D1 must ship with the D2 data contract in place. D2 must ship before Milestone
D is called complete.

### 20.2 Requirement profile and authority

This section uses `shall` for a proposed binding product requirement. The
lifecycle profile is general requirements engineering. This section does not
claim NASA, BCP 14, or formal ASD-STE100 compliance.

Source precedence is:

1. The product owner's latest explicit decision.
2. Sections 1-16 of this product-direction spec.
3. The shipped Milestone B and C contracts in sections 18 and 19.
4. Current implementation and current-truth documentation.

The product owner is the approval authority. Gate 2 approval makes each
requirement in this section an accepted implementation requirement.

| ID | Product requirement | Rationale and parent trace | Allocation | Planned verification |
|---|---|---|---|---|
| MD-REQ-001 | The shared core shall accept one bounded context request and return one deterministic context brief from repository-local canonical evidence. | Delivers section 11 Milestone D retrieval without hidden chat state. | Shared Python core | Repeat-run equality test |
| MD-REQ-002 | The retrieval engine shall return a memory only when the memory has at least one structural relevance signal. | Prevents plausible but unrelated language from becoming false context. Traces to outcome acceptance 4 and 5. | Shared Python core | Lexical-decoy negative test |
| MD-REQ-003 | Each returned memory shall state its score components, matched signals, status, staleness, and canonical source references. | Keeps derived intelligence explainable. Traces to non-negotiable properties 1-3. | Shared core and all adapters | Payload and source-link inspection |
| MD-REQ-004 | The command, MCP, SessionStart, and UserPromptSubmit adapters shall return semantically equivalent memory facts for equivalent context signals. | Prevents adapter-specific intelligence. Traces to the accepted parity boundary. | Plugin and MCP adapters | Cross-adapter matrix |
| MD-REQ-005 | A context request shall not modify canonical or derived board state, execute code, or use network access. | Keeps retrieval safe at the decision boundary. | Shared core and adapters | Filesystem, process, and closed-proxy tests |
| MD-REQ-006 | SessionStart shall surface no more than three eligible memories from current directory, changed-file, and active-entry context. | Makes repository return useful without overwhelming startup. | SessionStart adapter | SessionStart fixture |
| MD-REQ-007 | UserPromptSubmit shall return no output for an unrelated prompt and no more than three eligible memories for a bounded investigation or change prompt. | Delivers memory when task intent first becomes available without adding noise to every turn. | Prompt adapter | Positive and silent-path fixtures |
| MD-REQ-008 | The foreground command and MCP tool shall accept explicit task, file, entry, and result-limit context. | Gives agents a direct and testable retrieval path. | `/board-context` and `board_context` | Command/MCP schema tests |
| MD-REQ-009 | When evidence is insufficient, invalid, stale, or unavailable, the retrieval engine shall return an empty result or a typed limitation without a fabricated match. | Makes uncertainty visible. | Shared core | Missing, malformed, and stale-input tests |
| MD-REQ-010 | Each hook retrieval shall complete within its configured timeout on the 1,200-entry benchmark or return a typed limitation before the timeout. | Prevents contextual memory from blocking the interactive agent. | Shared core and hook adapters | Timed benchmark |
| MD-REQ-011 | Outcome preview shall validate one entry, one H### record, a typed fix result, cited evidence, an actor, and a bounded fix summary without writing a file. | Connects verified work to memory without granting silent mutation authority. | Shared core | No-write preview tests |
| MD-REQ-012 | Outcome apply shall require an unchanged content-bound plan, revalidate under the per-board lock, and update at most one H### file atomically. | Preserves Milestone C mutation safety and resumability. | Shared core | Stale, contention, and repeated-apply tests |
| MD-REQ-013 | A fix result shall not confirm, weaken, reject, or split a hypothesis without an explicit compatible disposition in the applied request. | Validation success is evidence, not automatic causal authority. | Shared core | Result/disposition compatibility matrix |
| MD-REQ-014 | Applied outcome history shall preserve the fix result, entry, evidence IDs, summary, actor, date, and optional verified context reference. | Makes later confidence and value reports auditable. | H### serializer and schema | Round-trip and history-preservation tests |
| MD-REQ-015 | A Learning-feedback preview shall derive its proposed L### change only from canonical resolved entries and structured H### fix outcomes. | Prevents recurrence or model confidence from silently becoming a Learning. | Shared core and curator adapter | Learning preview/apply matrix |
| MD-REQ-016 | The Learning apply core shall update at most one L### file atomically for a foreground or authorized PM caller. | Preserves explicit foreground authority and resumable batch behavior. | Shared core and PM adapter | Partial-batch and retry tests |
| MD-REQ-017 | The value report shall derive all counts only from canonical outcome history. | Measures useful resurfacing and systemic fixes instead of activity volume. | Shared core and read adapters | Derived-report fixture |
| MD-REQ-018 | After deletion of `GRAPH.yml` and disposable caches, a rebuild shall restore logically equivalent retrieval results without loss of context, outcome, or Learning evidence. | Preserves Markdown authority and postpones SQLite until evidence justifies it. | Graph and retrieval core | Delete-and-rebuild equivalence test |

Requirement verification proves the specified behavior. Product validation
must separately show that a representative agent receives a relevant
cross-domain memory before it chooses a local fix.

The product owner's 2026-07-31 decision adds the bounded memory-content
requirements in section 21.14. That additive contract extends the current
response. It does not rewrite the historical 2026-07-28 Gate 2 approval or
change the ranking rule.

### 20.3 Context request and response contract

The shared core accepts this logical request:

```json
{
  "project": "atlas",
  "task": "Investigate why the CLI loses tenant state after a retry.",
  "files": ["cli/session.py"],
  "entry_ids": ["B014"],
  "cwd": "cli",
  "limit": 3
}
```

Rules:

- `project` is required.
- At least one of `task`, `files`, `entry_ids`, or `cwd` is required.
- `task` permits at most 4000 Unicode characters.
- `files` permits at most 100 repository-relative paths. Each path permits at
  most 512 characters.
- `entry_ids` permits at most 50 canonical IDs.
- `cwd` must resolve inside the repository.
- `limit` is 1-10. The default is 3.
- Adapters can add a repository root as transport context. The root is not
  part of the logical relevance input.
- The core normalizes path separators and compares path segments. It does not
  read a file named in task text.

The response contains:

```json
{
  "project": "atlas",
  "context_fingerprint": "ctx-<16 lowercase hex>",
  "source_fingerprint": "<canonical source fingerprint>",
  "ranking_rule_version": "1",
  "context_contract_version": "2",
  "results": [
    {
      "kind": "hypothesis",
      "id": "H003",
      "status": "confirmed",
      "title": "Lifecycle state has no shared owner",
      "summary_kind": "proposed_root_cause",
      "summary": "The CLI and session adapter implement different lifecycle ownership rules.",
      "stale": false,
      "score": 90,
      "components": {
        "canonical_pattern": 35,
        "affected_path": 30,
        "graph_proximity": 20,
        "intent_overlap": 0,
        "outcome_relevance": 5
      },
      "matched_signals": [
        "P004 lifecycle-state-ownership",
        "cli/session.py overlaps cli"
      ],
      "why": "The current file and B014 share P004 with H003.",
      "source_refs": [
        "hypotheses/H003-lifecycle-state-ownership.md",
        "bugs/B014.md"
      ]
    }
  ],
  "warnings": [],
  "context_token": "<self-contained non-authority token>"
}
```

The context fingerprint binds a digest of the normalized request, canonical
source fingerprint, context-contract version, ranking-rule version, and
ordered result IDs. The context token contains the same identity fields plus
a checksum. It does not contain raw task or prompt text. It is historical
reference data. It does not grant mutation authority.

Every `why` statement is generated from typed signal templates. The core does
not ask a model to invent the explanation.

Each title is one line and permits at most 160 Unicode characters. Each
summary is one line and permits at most 2,000 Unicode characters. The core
flattens line and control separators before it returns either field.

A cluster uses `cluster_scope`. Its title contains normalized pattern labels.
Its summary identifies pattern IDs, normalized labels, member IDs, and
affected top-level domains. A hypothesis and rejected negative memory use
`proposed_root_cause`. Their summary contains the canonical proposed-root-
cause section. A Learning uses `learning_takeaway`. Its summary contains the
canonical Takeaway.

The result `kind` and `status` preserve epistemic authority. A readable
proposed root cause is not confirmed unless the separate status is
`confirmed`.

### 20.4 Deterministic retrieval and ranking

Eligible memory kinds are:

- ranked graph clusters.
- active or terminal H### hypotheses.
- active L### Learnings.
- rejected H### negative memory.

The core derives context entries from explicit `entry_ids` and from canonical
entries whose `affects` path overlaps an explicit file or `cwd`. It then scores
each memory:

| Component | Maximum | Deterministic rule |
|---|---:|---|
| Canonical pattern | 35 | 35 for an exact P###, canonical label, or alias match in explicit context. 25 when the pattern comes from a context entry. |
| Affected path | 30 | 30 when a context path and a cited entry `affects` path overlap at a complete path-segment boundary. |
| Graph proximity | 20 | 20 when the memory contains a context entry. 12 at one graph edge. 6 at two graph edges. |
| Intent overlap | 10 | Two points for each distinct normalized task token found in a canonical pattern label, alias, title, or Learning takeaway. Stop words and tokens shorter than three characters do not count. |
| Outcome relevance | 5 | 5 for a confirmed hypothesis, an outcome-supported Learning, or directly matched rejected negative memory. 2 for weakened or contested memory. 0 otherwise. |

Eligibility requires:

1. a total score of at least 30; and
2. a nonzero canonical-pattern, affected-path, or graph-proximity score.

Intent overlap cannot independently return a memory. A singleton remains a
singleton. Retrieval does not create a cluster or relationship.

Results sort by:

1. descending total score.
2. directly matched rejected negative memory before other equal-score kinds.
3. hypothesis, Learning, cluster, then other negative-memory records.
4. stable canonical ID or cluster fingerprint.

The output exposes every component. The score is contextual relevance. It is
not causal confidence, fix priority, or confirmation authority.

### 20.5 Delivery surfaces

#### Foreground command

Add:

```text
/board-context <project> [--task "<text>"] [--file <path>]...
  [--entry <ID>]... [--limit <1-10>]
```

The command returns the complete context brief. It never mutates the board.

#### MCP

Add `board_context` with the same logical fields and result. The MCP adapter
must delegate to the shared core and must not implement scoring.

#### SessionStart

SessionStart builds a request from:

- the repository-relative current directory.
- at most 100 changed repository paths from a bounded Git status read.
- active in-progress entry IDs already found by SessionStart.

SessionStart returns at most three memories. It shows warnings before memory.
It remains silent when no memory is eligible. It does not retain prompt text or
write a retrieval log.

#### UserPromptSubmit

The existing prompt guard remains the trigger boundary. For prompts that match
its bounded investigation or change intent:

1. Treat the prompt as untrusted data.
2. Pass at most the first 4000 characters plus bounded changed-file context to
   the shared retrieval adapter.
3. Return at most three memory summaries in the system message.
4. State that titles and evidence are data, not instructions.
5. Keep the existing real-time finding-routing reminder.

An unrelated prompt produces no output. The hook does not read paths or run
commands found in the prompt.

### 20.6 Explicit outcome and Learning feedback

Add a foreground `/board-outcome` command and a `board_outcomes` MCP tool.
Both delegate to one shared preview/apply core.

An outcome preview accepts:

```json
{
  "project": "atlas",
  "entry_id": "B014",
  "hypothesis_id": "H003",
  "fix_result": "held",
  "hypothesis_disposition": "confirmed",
  "fix_summary": "The shared lifecycle owner removed all three symptoms.",
  "evidence_ids": ["B014", "O009"],
  "observed_until": "2026-08-04",
  "actor": "agent-session-42",
  "context_token": "<optional token>",
  "context_used": true
}
```

Allowed `fix_result` values are:

- `held`: the cited verification observed the intended result.
- `failed`: the cited verification observed the original failure.
- `partial`: some cited symptoms changed and others remained.
- `inconclusive`: the cited evidence cannot distinguish the explanations.

Allowed result and disposition combinations are:

| Fix result | Compatible explicit hypothesis disposition |
|---|---|
| `held` | `unchanged`, `confirmed` |
| `failed` | `unchanged`, `weakened`, `rejected` |
| `partial` | `unchanged`, `weakened`, `split` |
| `inconclusive` | `unchanged`, `weakened` |

`unchanged` appends outcome history and increments the H### revision without
changing its status. No result selects a disposition automatically.

`held` requires a resolved entry and cited completion evidence. Other results
may apply while an entry remains open or in progress. The entry must be a
member of the hypothesis cluster, a cited source of the hypothesis, or a
current graph neighbor with a shared canonical pattern. `observed_until`
cannot precede the entry discovery date.

If `context_used` is true, `context_token` is required. Preview verifies the
token checksum and verifies that it surfaced the target hypothesis or its
Learning. A changed canonical source does not erase the historical reference.
The outcome history labels whether the context source was current or stale
when the outcome was recorded.

Apply uses the Milestone C plan-token, inventory, lock, path, symlink,
revalidation, and atomic-write rules. It updates one H### file. It returns
zero or more Learning feedback previews. It does not apply them.

Learning feedback applies to curator-managed `subtype: pattern` records.
Explicit `source: remember` records remain user-authored unless the user links
them in a separate explicit request.

Add these Learning fields:

```yaml
outcome_status: untested
outcome_refs: [H003]
confidence_basis: "Three resolved cases; one held systemic fix."
```

Allowed `outcome_status` values are:

- `untested`: no structured fix outcome applies.
- `supported`: one or more `held` outcomes apply and no `failed` outcome
  applies.
- `weakened`: one or more `failed` outcomes apply and no `held` outcome
  applies.
- `contested`: held and failed or partial outcomes both apply.

For curator-managed pattern Learnings, deterministic confidence is:

| Outcome status | Recurrence | Confidence |
|---|---:|---|
| `supported` | 3 or more | `high` |
| `supported` | 1-2 | `medium` |
| `untested` | 3 or more | `medium` |
| `untested` | 1-2 | `low` |
| `weakened` or `contested` | any | `low` |

The Learning preview shows the old and new fields, cited entries, cited
hypotheses, and rationale. A foreground apply changes one L### file. PM mode
may apply a batch only through the same one-file plans under its existing
authorization. A partial batch reports applied, pending, stale, and failed
plans. A retry recomputes only pending plans.

### 20.7 Value report

The context command and MCP tool can request a derived value report. It
contains:

- hypotheses with at least one structured fix outcome.
- outcome-supported, weakened, and contested Learnings.
- confirmed systemic fixes, defined as a `held` outcome that explicitly
  confirms a hypothesis whose cluster spans at least two affected domains.
- useful resurfacing events, defined as an applied outcome with a verified
  context token and explicit `context_used: true`.

The report does not count prompts, sessions, token volume, graph size, command
calls, or raw retrieval impressions as product value. It reads canonical H###
and L### files. It does not require or emit telemetry.

### 20.8 State, authority, and preservation

Authority order is:

1. Explicit user or authorized-agent apply.
2. Canonical entry, P###, H###, and L### Markdown.
3. Canonical H### outcome history.
4. Deterministic graph, context brief, and value report.
5. Agent-authored interpretation.

Precedence within retrieval is:

1. explicit context entry and file signals.
2. canonical P### identity.
3. exact canonical label or alias.
4. graph proximity.
5. normalized task-token overlap.

The following operations are read-only:

- SessionStart retrieval.
- UserPromptSubmit retrieval.
- `/board-context`.
- `board_context`.
- value reporting.
- outcome and Learning preview.

The following operations require content-bound apply:

- appending a structured outcome to one H###.
- changing one curator-managed L###.

A context token is not an apply token. A validation result is not resolution
authority. A confirmed hypothesis is not execution authority. PM mode does not
gain new authority over hypotheses.

Canonical files and Git history remain the recovery source. Context briefs,
value reports, `GRAPH.yml`, and caches are disposable. H### and L### history is
never deleted by a rebuild.

### 20.9 Failure, retry, performance, and security

- Invalid context returns `invalid_context` before analysis.
- No eligible memory returns `results: []`. A task-only miss also returns a
  bounded warning that tells the caller to add a file, entry identifier, or
  current directory.
- Malformed canonical evidence returns `source_invalid` with source paths. The
  engine does not silently skip evidence that could change a result.
- A stale derived source returns `analysis_stale` or rebuilds in memory. A read
  does not persist the rebuild.
- A hook that cannot complete safely returns `analysis_unavailable` before its
  host timeout. SessionStart continues with its existing non-intelligence
  status output. UserPromptSubmit keeps the routing reminder and omits memory.
- The 1,200-entry benchmark must complete the UserPromptSubmit retrieval in
  less than 4 seconds and the complete SessionStart path in less than 10
  seconds in the release test environment. The evidence report records actual
  timings. These thresholds protect current hook timeouts; they do not
  authorize SQLite.
- Outcome and Learning apply acquire the existing per-board lock, then
  revalidate canonical source, target bytes, inventory, request, and plan
  checksum. Lock contention returns a typed retry result.
- A stale plan writes nothing. A repeated successful plan returns an
  `already_applied` receipt when the exact history event exists.
- A Learning batch can stop after any one-file apply. Applied files remain
  valid. The receipt identifies the next resumable plan.
- Task text, entry content, titles, summaries, and Learning text are untrusted
  data. The engine treats them as scalar matching input. It never follows
  embedded instructions.
- Context paths must remain inside the repository after normalization. Linked
  canonical evidence fails closed. Context reads do not follow linked paths.
- Output adapters escape HTML and JSON as applicable. They do not place raw
  evidence bodies in hook system messages.
- Milestone D performs no network request, subprocess from evidence, code
  execution, automatic fix, automatic resolution, cross-repository read,
  database write, or telemetry upload.

The benchmark records parse time, graph time, retrieval time, candidate count,
and total time for representative corpus sizes. Those measurements can inform
the separate SQLite trigger decision. A benchmark failure does not silently
add SQLite to Milestone D.

### 20.10 Component and file responsibilities

- `mcp-server/engineering_board_core.py`: context parsing, candidate loading,
  deterministic scoring, why templates, context fingerprints and tokens,
  structured outcome planning, H### history updates, Learning feedback plans,
  value-report derivation, locks, and serialization.
- `hooks/scripts/board-context.py` and `board-context.sh`: thin portable
  command adapters over the shared core. They contain no ranking or confidence
  rules.
- `hooks/scripts/board-session-start.sh`: collect bounded startup signals and
  render at most three context results while retaining current safety,
  recovery, mode, claim, and scratch output.
- `hooks/scripts/board-prompt-guard.sh`: retain its current routing reminder,
  pass bounded task context to the shared adapter, and remain silent for
  unrelated prompts.
- `commands/board-context.md`: foreground read-only interaction contract.
- `commands/board-outcome.md`: outcome and Learning preview/apply interaction
  contract.
- `skills/board-insights/SKILL.md`: evidence-reading, context explanation,
  untrusted-data, and no-match behavior.
- `skills/board-resolve/SKILL.md`: after verification or resolution, offer the
  relevant outcome preview. It cannot apply an outcome without explicit
  authority.
- `skills/board-intake/references/hypothesis-schema.md`: structured fix-result
  fields, compatible dispositions, context reference, and history rules.
- `skills/board-intake/references/frontmatter-schema.md`: Learning outcome
  status, references, and confidence rules.
- `hooks/scripts/board-curate-learnings.sh`: delegate pattern-Learning plans to
  the shared core. Preserve PM batch authorization and resumable receipts.
- `mcp-server/engineering_board_mcp.py`: add `board_context` and
  `board_outcomes`. Both tools remain adapters over the shared core.
- `mcp-server/test_mcp_server.py`: discovery, schema, adapter parity,
  read-only, outcome, Learning, retry, and standard-output safety coverage.
- `tests/orchestration/milestone-d-context-outcome-intelligence.sh`: complete
  deterministic D1 and D2 lifecycle matrix.
- `tests/session-start/automated.sh`: startup relevance, caps, silence,
  failure, and 1,200-entry performance.
- A new prompt-guard test suite: relevant-prompt retrieval, unrelated-prompt
  silence, bounded input, injection text, and timeout fallback.
- `tests/view/automated.sh`: supported, weakened, contested, and context-linked
  outcome presentation.
- `hooks/scripts/board-view.sh`: show Learning outcome state and derived value
  evidence. It does not add mutation controls.
- `README.md`, `ARCHITECTURE.md`, `SECURITY.md`, `mcp-server/README.md`,
  `docs/index.html`, and `docs/llms.txt`: shipped user value, setup,
  architecture, security, MCP, and retrieval boundaries.
- `docs/assets/`: one sanitized real Milestone D context-brief visual with
  source version, capture date, alt text, and provenance.
- Coordinated manifests, changelog, bundle checksum, and release evidence:
  update together at an explicit minor release boundary.

### 20.11 Deterministic acceptance matrix

| Sequence | Failure injection | Expected semantic outcome | Durable evidence | Requirement |
|---|---|---|---|---|
| Retrieve with one task, file, and entry twice | Same canonical source | Ordered results, component scores, why text, fingerprints, and warnings are equal | Compared payloads | MD-REQ-001, 003 |
| Use similar task words for an unrelated pattern | Text overlap without a structural signal | No memory is eligible | Empty result and corrective structural-signal warning | MD-REQ-002, 009 |
| Match a prior pattern through a file in another domain | Different affected domain, same P### identity | Prior cluster, H###, and Learning surface with cross-domain reasons and source links | Context brief | MD-REQ-001-003 |
| Request the same context through CLI and MCP | Two adapters | Both return semantically equal facts and fingerprints | Compared JSON | MD-REQ-004, 008 |
| Trigger SessionStart with relevant changed files | More than three eligible memories | Exactly three highest-ranked memories surface after safety warnings | Captured hook output | MD-REQ-006 |
| Submit a relevant and then unrelated prompt | Prompt contains instruction-like evidence text | Relevant prompt returns escaped data and routing guidance. Unrelated prompt is silent. No embedded instruction executes. | Captured hook output and process assertions | MD-REQ-005, 007 |
| Corrupt a canonical pattern, hypothesis, or Learning | Candidate could change | Retrieval returns a typed limitation and source path. It does not return an incomplete confident result. | Error payload | MD-REQ-009 |
| Run 1,200-entry hook fixtures | Cold parse and graph build | Prompt retrieval completes in less than 4 seconds. Complete SessionStart remains below 10 seconds. | Timed release evidence | MD-REQ-010 |
| Preview one held outcome | No apply token | H### and L### files remain byte-identical. Preview shows compatible disposition and Learning effects. | Plan only | MD-REQ-011, 015 |
| Pair `held` with `rejected`, or `failed` with `confirmed` | Incompatible disposition | Preview fails before mutation | Typed validation error | MD-REQ-013 |
| Change the entry, H###, or evidence after preview | Stale plan | Apply returns `plan_stale`. No file changes. | Compared inventory | MD-REQ-012 |
| Apply one valid outcome twice and concurrently | Same H### target | One history event exists. Other attempts return stale or already-applied receipts. | Revised H### | MD-REQ-012, 014 |
| Apply held, failed, partial, and inconclusive outcomes | Each uses cited evidence | H### status changes only to the explicit compatible disposition. Each history event remains queryable. | H### history | MD-REQ-013, 014 |
| Apply one outcome that yields two Learning recommendations | Fail the second Learning apply | First L### remains valid. Second remains pending and succeeds on retry without rewriting the first. | L### files and batch receipt | MD-REQ-015, 016 |
| Create supported, weakened, contested, and untested pattern Learnings | Mixed recurrence and outcomes | Outcome status and confidence follow the exact table. Explicit remember Learnings remain unchanged. | L### files | MD-REQ-015, 016 |
| Record an outcome with a verified context token and `context_used: true` | Canonical source changed after retrieval | H### history preserves the historical reference and labels staleness. Value report counts one useful resurfacing event. | H### history and derived report | MD-REQ-014, 017 |
| Generate a value report from prompts with no applied outcomes | Many retrieval calls | Report contains no useful-resurfacing claim and no prompt or session counts. | Derived report | MD-REQ-017 |
| Delete graph and cache artifacts, then repeat retrieval | Missing derived state | Rebuilt context results are logically equal. H### and L### files are unchanged. | Compared payloads and file digests | MD-REQ-018 |
| Run with closed outbound proxies | Network unavailable | Context, outcome, Learning, and value-report sequences pass offline | Offline test result | MD-REQ-005 |
| Run all current suites | Compatibility regression opportunity | Milestones A-C, capture, claims, modes, view, package, and MCP behavior remain green | Full release-tree result | All |

### 20.12 Product validation and live evidence

Use a disposable repository with:

- earlier findings in authentication and worker-recovery domains.
- one canonical cross-domain pattern.
- one confirmed H### and one rejected competing explanation.
- one outcome-supported Learning.
- a new CLI symptom that shares the pattern but not the prior paths.
- one lexical decoy with similar words and an unrelated canonical pattern.
- malicious Markdown, HTML, path, and prompt strings.

Run two bounded scenarios:

1. A clean agent receives only the new CLI symptom and current file.
2. A clean agent receives the same task plus the real Milestone D context
   brief.

The product validation report must show whether the second agent identifies the
prior systemic investigation before proposing a local fix. It must cite the
exact brief and canonical evidence. The report must not generalize one scenario
into a universal productivity claim.

The live run uses the real SessionStart adapter, UserPromptSubmit adapter,
foreground command, MCP stdio tools, outcome preview/apply, Learning
preview/apply, value report, and normal HTML renderer. It runs offline and
records sanitized paths, source commit, timings, fingerprints, file digests,
negative checks, and cleanup.

### 20.13 Documentation alignment and delivery

Before Milestone D can ship, the implementation change must update or
substantively review:

- this central spec and the contract state.
- the Milestone D contract workpad and implementation evidence.
- README first-win, setup, command list, and product claims.
- command, skill, hypothesis, Learning, and MCP contracts.
- SessionStart and UserPromptSubmit behavior.
- architecture, security, privacy, failure, and performance boundaries.
- normal HTML view documentation and one real sanitized visual.
- tool and command counts, manifests, package files, and bundle contents.
- changelog, coordinated version surfaces, release tests, and dated release
  evidence.

An Unreleased source change can differ from the immutable checksum of the
published MCP bundle only when `[Unreleased]` contains a release note. A later
explicit release must rebuild and pin the bundle through the coordinated
release script.
- historical Milestone A-C reports, which remain unchanged.

The implementation must use a feature branch, commit, push, and pull request.
Worker validation, PR CI, merged-main CI, release publication, package
registries, product-site deployment, and dated closeout evidence remain
separate evidence phases. The release is a Semantic Versioning minor release
if no later release already contains part of the behavior.

### 20.14 Explicit non-goals

Milestone D does not:

- replace canonical Markdown or require SQLite.
- add embeddings, vector search, or model-generated graph edges.
- read or aggregate another repository.
- add a hosted service, account, synchronization layer, or telemetry.
- retain raw prompts after the hook request.
- use text similarity alone as a structural relation.
- make SessionStart or UserPromptSubmit mutate canonical state.
- automatically confirm, reject, split, resolve, or execute work.
- automatically apply a foreground Learning recommendation.
- redesign PM or Worker orchestration.
- add Milestone E planning, ready-action, or execution ergonomics.
- claim that a relevance score measures causal confidence.
- claim that one product-validation scenario proves general performance.

Gate 2 approval authorizes implementation of this section. It does not
authorize any non-goal or deferred portfolio work.

## 21. Gate 2 accepted: Milestone D.1 product-proof contract

_State: Gate 1 and Gate 2 were accepted by the product owner on 2026-07-29.
The owner replaced the provider-specific run contract on 2026-07-29. The
client-neutral correction baseline was accepted on 2026-07-29. Corpus
calibration remains open. Version 4 is an unlocked proposal. It is not an
accepted evidence baseline._

### 21.1 Product question

Milestone D proves that Engineering Board can retrieve bounded systemic memory
and record explicit outcomes. Milestone D.1 must answer a different question:

> Does the retrieved memory cause an engineering agent to identify the prior
> systemic investigation before it proposes another symptom-only correction?

Release tests verify product requirements. They do not answer this product
validation question.

### 21.2 Stakeholder expectation

The product owner expects Engineering Board to improve an agent diagnosis, not
only to return technically correct context.

The validation must show:

- whether the context arm identifies the systemic investigation before a local
  correction;
- whether the baseline arm misses or delays that investigation;
- whether the expected memory appears in the first three results;
- whether irrelevant, stale, or rejected memory misleads the agent;
- whether the agent cites canonical evidence;
- whether an applied structured outcome changes later retrieval as expected.

The validation must preserve failed cases. A failed case is calibration
evidence, not a result to remove from the corpus.

### 21.3 Evaluation boundary

The evaluation uses repository-local, sanitized cases. Each case declares:

- canonical evidence;
- expected relevant memory;
- rejected memory;
- expected systemic cause;
- task and file context;
- scoring facts.

Each paired trial has:

1. A baseline arm with no Engineering Board context brief.
2. A context arm with the real v1.11.0 context brief.

The two arms use equal declared task, repository, tool, client, model, and
trial-policy inputs. Only the context brief differs.

Each trial starts with a clean workspace and agent session. A trial cannot use
prompt text, generated files, or mutable agent memory from another trial.

### 21.4 Accepted requirements

| ID | Requirement |
|---|---|
| D1-REQ-001 | The evaluation corpus shall define the canonical evidence, expected relevant memory, rejected memory, and expected systemic cause for each case. |
| D1-REQ-002 | The paired-trial runner shall give each arm equal declared task, repository, tool, client, model, and trial-policy inputs except for the context brief. |
| D1-REQ-003 | The paired-trial runner shall isolate each trial from prior trial prompts, context briefs, generated files, and agent memory. |
| D1-REQ-004 | The trial recorder shall preserve the first proposed correction, the first stated cause, canonical citations, surfaced memory identifiers, and final diagnosis for each trial. |
| D1-REQ-005 | The outcome scorer shall classify whether each trial achieved a systemic-before-local outcome from the preserved trial record and case contract. |
| D1-REQ-006 | The retrieval-quality scorer shall report expected-memory rank, irrelevant-memory count, rejected-memory treatment, and lexical-decoy treatment for each context arm. |
| D1-REQ-007 | The outcome-loop evaluator shall compare retrieval before and after an applied structured outcome against unchanged canonical case expectations. |
| D1-REQ-008 | The validation cycle shall use a frozen production baseline for the evidence run, with calibration changes recorded as later candidate changes. |
| D1-REQ-009 | The validation report shall publish per-case evidence, aggregate results, limitations, failed cases, and approved next-step decisions. |
| D1-REQ-010 | The validation report shall not make a general productivity claim from the bounded D.1 evidence. |
| D1-REQ-011 | Milestone E implementation shall remain deferred until the product owner accepts the D.1 validation evidence and the resulting next-step decision. |
| D1-REQ-012 | The reference evidence run shall execute three independent paired repetitions for each of the eight fixed cases through the single profile that has the `reference` role in the dated contract. |
| D1-REQ-013 | The evaluation contract shall permit zero or more profiles that have the `replication` role. |
| D1-REQ-014 | The run manifest shall pin the exact source commit, client version, model identifier, instructions, tool set, trial policy, and context fingerprint for each evidence arm. |
| D1-REQ-015 | The paired-trial runner shall not retry a trial after the trial produces a scored result. |
| D1-REQ-016 | The reference evidence scorer shall pass the product-effect gate only when the positive-case context arms achieve at least 75 percent systemic-before-local outcomes and exceed the positive-case baseline arms by at least 25 percentage points. |
| D1-REQ-017 | The validation report shall cite canonical evidence for 100 percent of positive systemic-before-local classifications. |
| D1-REQ-018 | The retrieval-quality scorer shall pass an applicable context-arm trial only when the expected relevant memory appears within the first three results. |
| D1-REQ-019 | The false-positive scorer shall pass the evidence run only when lexical-decoy and independent-issue cases produce zero durable systemic conclusions. |
| D1-REQ-020 | The trial recorder shall preserve each invalid attempt, infrastructure-failure reason, and replacement relationship. |
| D1-REQ-021 | The paired-trial runner shall permit no more than one replacement for an infrastructure failure that occurs before a scored result. |
| D1-REQ-022 | The locked evidence corpus shall contain exactly two recurring-bug cases, two cross-domain shared-cause cases, two lexical-decoy cases, and two independent-issue cases. |
| D1-REQ-023 | A client-compatibility claim shall identify one tested protocol or package surface. |
| D1-REQ-024 | A client-compatibility claim shall cite deterministic contract evidence for the identified surface. |
| D1-REQ-025 | The reference product-effect gate shall not depend on the availability or result of a `replication` profile. |
| D1-REQ-026 | Each D.1 corpus shall declare one corpus identifier, one corpus role, one integer version, and one lock state. |
| D1-REQ-027 | The paired-trial runner shall prepare a scored run only when the selected corpus has the `evidence` role and a locked state. |
| D1-REQ-028 | The paired-trial runner shall reject a corpus that has the `calibration` role. |
| D1-REQ-029 | For each positive evidence case, the corpus validator shall reject an agent-visible title, task, file path, or evidence file that contains the expected cause, expected memory identifier, or a declared oracle term. |
| D1-REQ-030 | Each positive evidence case shall record its information gap and plausible local correction in scoring-only fields. |
| D1-REQ-031 | Each lexical-decoy context shall retrieve its declared rejected memory within the first three results. |
| D1-REQ-032 | The run manifest shall record the corpus identifier, corpus version, and corpus digest. |
| D1-REQ-033 | A content change to a locked evidence corpus shall increment the corpus version and create a new evidence baseline. |
| D1-REQ-034 | A proposal corpus shall have the `proposal` role, an integer version, a proposal date, and an unlocked state. |
| D1-REQ-035 | The paired-trial runner shall reject a corpus that has the `proposal` role. |
| D1-REQ-036 | Each positive corpus case in version 4 or later shall expose exactly one current incident in exactly one top-level domain. |
| D1-REQ-037 | Each positive corpus case in version 4 or later shall identify one current repository entry and at least one prior repository entry in scoring-only data. |
| D1-REQ-038 | For each positive corpus case in version 4 or later, the expected memory shall cite the declared current and prior repository entries. |
| D1-REQ-039 | For each positive corpus case in version 4 or later, a systemic-before-local classification shall identify a relationship across at least two incidents. A rule confined to the current component shall be classified as local. |
| D1-REQ-040 | The trial-response schema shall accept canonical evidence identifiers that include a corpus-version segment. |
| D1-REQ-041 | For corpus version 4 or later, the corpus digest shall bind the JSON contract, each canonical case-evidence file, and the complete context fixture. |

The structured requirement artifact has no deterministic requirement-quality
failure. Its current status and content digest are recorded in the D.1
contract workpad. Automated checks do not replace semantic review.

### 21.5 Reference evaluation record

For each trial, preserve:

- the first proposed correction;
- the first stated cause;
- each cited canonical source;
- each surfaced memory identifier and rank;
- the final diagnosis;
- the systemic-before-local classification;
- the classification evidence and reviewer.

For each context arm, also preserve:

- expected-memory rank;
- irrelevant-memory count;
- rejected-memory treatment;
- lexical-decoy treatment;
- context fingerprint and evaluated source commit.

These records are product-validation evidence. They are not product telemetry.
The repository must not retain unrelated raw prompts or private user data.

### 21.6 Baseline integrity and calibration

One immutable Git commit identifies the behavior under evaluation. The
validation cannot change ranking weights, prompts, result presentation, or
outcome behavior during the evidence run.

The report records each failed case and assigns the likely defect class:

- corpus or expectation defect;
- retrieval eligibility defect;
- ranking defect;
- explanation defect;
- presentation defect;
- agent-use defect;
- outcome-feedback defect;
- inconclusive evidence.

A calibration candidate becomes a later product change. It requires its own
requirement, test, documentation review, and new validation baseline.

### 21.7 Accepted Gate 2 decisions

The product owner accepted the following values on 2026-07-29.

#### Corpus

The corpus contains exactly eight fixed cases with this allocation:

- two recurring-bug cases;
- two cross-domain shared-cause cases;
- two lexical-decoy cases;
- two independent-issue cases.

Each case remains fixed for an evidence run. A later case change creates a new
corpus version and a new evidence baseline.

#### Trials and retry policy

The reference evidence run uses three independent paired repetitions for each
case. Codex is the current reference client. A dated evaluation contract can
add one or more replication profiles for other clients. Replications are
optional and do not change the reference gate.

A scored trial cannot be retried. An infrastructure failure is invalid only if
it occurs before the trial produces a scored result. The recorder must preserve
the invalid attempt, its failure reason, and its replacement relationship.
Only one replacement is permitted. A second infrastructure failure makes the
applicable evidence run incomplete.

#### Client and model control

The current reference client is Codex CLI through the MCP server. Each dated
run manifest pins the exact client version, model identifier, instructions,
tools, source commit, trial policy, and context fingerprint. A baseline and
context pair use equal pinned values except for the context brief. A
replication profile uses the same controls.

#### Success gates

The reference evidence run passes only when all these conditions are true:

- the 12 positive-case context trials achieve at least 75 percent systemic-before-local outcomes;
- the positive-case context rate exceeds the positive-case baseline rate by at least 25 percentage points;
- 100 percent of positive classifications cite canonical evidence;
- the expected relevant memory is in the first three results for each
  applicable context-arm trial;
- lexical-decoy and independent-issue cases produce zero durable systemic
  conclusions.

The positive-case rate denominators contain only recurring-bug and cross-domain
shared-cause cases. Lexical-decoy and independent-issue cases use the separate
zero-durable-conclusion gate.

Replication results are reported separately and do not change the reference
product-effect gate. Client compatibility is a separate claim. MCP
compatibility requires deterministic MCP protocol and package evidence. Plugin
compatibility requires deterministic plugin package and manifest evidence. A
live provider run can add behavioral replication evidence, but it is not
required for compatibility.

### 21.8 Explicit non-goals

Milestone D.1 does not:

- start Milestone E;
- add a general planning system;
- change production ranking during an evidence run;
- add hosted evaluation infrastructure or telemetry;
- acquire or maintain accounts for each model provider;
- add SQLite, embeddings, or cross-repository aggregation;
- automatically execute a fix;
- make a general productivity claim;
- hide, remove, or relabel a failed case after the baseline is frozen.

### 21.9 Gate 2 and delivery

Gate 2 is accepted. It authorizes implementation of the evaluation harness,
frozen corpus, scoring tools, and evidence-reporting path in this repository.
The implementation must keep the exact client and model identifiers in dated
run evidence instead of timeless product prose.

Gate 2 does not authorize production ranking changes, a release, Milestone E,
or any section 21.8 non-goal. The first evidence run must evaluate the frozen
v1.11.0 behavior. A failed gate produces calibration candidates and a new
product decision. It does not permit the current evidence baseline to change.

The repository-only harness, frozen corpus, real Markdown context fixture,
client contracts, recorder, scorer, report writer, and deterministic tests
implement the corrected contract on the review branch. The harness loads the
product core from the pinned commit. It builds real product context, keeps
scoring expectations out of agent input, and applies structured outcomes to
isolated fixture copies. The harness does not execute a live client. Therefore,
the harness implementation is not product-effect evidence.

### 21.10 Preflight validity correction

The first live-run preflight found that harness schema 1 did not satisfy the
accepted contract. Its context arm contained the expected memory and rejected-
memory list instead of a real v1.11.0 context brief. Its outcome gate accepted
an agent-supplied match instead of applying and observing a product outcome.
Either behavior could inflate the result.

Harness schema 2 corrects both defects before any scored live trial:

- The corpus includes a sanitized canonical Markdown board fixture.
- The harness loads `engineering_board_core.py` from the exact pinned source
  commit.
- The context arm receives the complete `build_context` result and no scoring
  oracle field.
- The recorder binds surfaced memory identifiers and ranks to that result.
- The outcome evaluator resolves an isolated fixture entry, applies the
  structured outcome with frozen product code, rebuilds context, and records
  the observed status, score, rank, and fingerprint change.
- The manifest records the fixture and frozen-core digests.

No schema 1 trial is valid D.1 product evidence. The dated preflight evidence
records the live-client readiness result and the remaining external gate.

### 21.11 Client-neutral evaluation correction

The first complete Codex profile scored 100 percent in the positive baseline
arms and 100 percent in the positive context arms. The zero-point difference
does not prove a product effect. It shows that the current corpus gives the
reference client no measurable headroom.

The owner rejected provider accounts as a required evaluation dependency.
Harness schema 3 applies that decision:

- One `reference` profile is required.
- Codex is the repository reference profile.
- A contract can add zero or more `replication` profiles.
- An incomplete replication cannot fail the reference product gate.
- Compatibility evidence names a protocol or package surface.
- Deterministic MCP and plugin tests support compatibility claims.
- Live provider behavior is optional dated replication evidence.

The saturated first-run cases are retained as calibration evidence. They
cannot enter a scored product-effect run. Milestone E remains deferred until
the owner accepts the resulting product-effect evidence and next-step
decision.

### 21.12 Corpus calibration and evidence isolation

The corpus-calibration correction separates benchmark development from scored
evidence:

- `calibration-corpus.json` preserves the first-run cases that gave Codex no
  measurable headroom.
- `evidence-corpus.json` defines a separate locked eight-case baseline.
- Positive evidence cases withhold the prior cross-session or cross-domain
  relationship from agent-visible evidence.
- Scoring-only fields record the missing relationship, a plausible local
  correction, and terms that would disclose the scoring oracle.
- The validator rejects an evidence case when an agent-visible field contains
  the expected cause, expected memory identifier, or a declared oracle term.
- Lexical-decoy cases deliberately surface rejected memory. This tests whether
  the agent uses negative memory instead of following a misleading label.
- A run manifest records the corpus identifier, version, and digest.

This design does not force a low baseline score. It creates an information
boundary that gives the baseline a realistic local explanation and gives the
context arm prior repository knowledge.

The version 3 reference run produced these results:

- Positive context rate: 100 percent.
- Positive baseline rate: 83.33 percent.
- Improvement: 16.67 percentage points.
- Negative durable systemic conclusions: zero.
- Product-effect result: fail. The required improvement is 25 percentage
  points.

The first three positive cases still disclosed enough current cross-path
evidence for Codex to infer a systemic boundary without repository memory.
Only D1-C04 produced local-first baseline diagnoses. Preserve version 3 and its
failed result. Do not change its content after observation.

The next D.1 corpus proposal is an active recommendation, not an accepted
baseline. The proposal should use a new version. The current trial should show
a plausible local symptom, and only Engineering Board context should supply
the prior incident relationship that supports a recurring or cross-domain
cause. Keep the accepted scoring thresholds unchanged. Obtain product-owner
approval before another scored run.

### 21.13 Version 4 proposal preflight

Version 4 is an unlocked proposal. It is not a scored evidence corpus. The
proposal adds these controls:

- Each positive case shows one current incident in one top-level domain.
- Scoring-only data identifies the current incident and the prior incidents.
- The expected memory must cite both the current incident and the prior
  incidents.
- Declared prior-incident terms cannot appear in agent-visible input.
- A positive systemic classification must connect at least two incidents.
- A general rule that stays inside the current component is local for this
  product-effect test.
- The prepare command rejects the proposal role.

A non-scored preflight tested the four positive cases. The frozen v1.11.0
product ranked each expected hypothesis within the first three results.
However, the context payload did not include the hypothesis title, proposed
root cause, evidence summary, or Learning takeaway. The payload included the
memory identifier, kind, state, score, match details, and source paths.

The ranking engine already uses the title, proposed root cause, and Learning
takeaway to calculate intent overlap. It removes those fields before it returns
the result. The agent therefore receives evidence that a memory is relevant
without receiving the bounded memory content that explains the prior incident
relationship.

Do not seal version 4 while this product-information gap remains. Additional
corpus wording cannot supply information that the version 1 result omits.

The approved correction adds bounded, agent-usable memory content to
each context result:

- a stable title;
- a bounded summary;
- the epistemic state;
- the match reason and score components;
- canonical source references.

For a hypothesis, the summary should contain the proposed root cause. For a
Learning, the summary should contain the Takeaway. For a cluster, the summary
should identify its normalized patterns and member scope. The result must keep
evidence separate from inference and must not present a proposed hypothesis as
confirmed.

The product owner selected the self-contained result on 2026-07-31. Section
21.14 defines the exact additive contract, limits, sanitization rules, adapter
parity, and tests.

An alternative is to let the agent open each returned source reference. This
would test a multi-step retrieval workflow instead of a self-contained context
result. That alternative requires equal-tool controls and a new operator
contract. The owner did not select it for this correction.

The implementation correction does not prove product effect. Run a new
unlocked preflight against the new product source. Then present the exact
version 4 corpus and requirement digests for owner baseline review.

Milestone D.1 remains open. Milestone E remains deferred.

### 21.14 Approved bounded memory-content contract

_State: approved by the product owner on 2026-07-31. Implementation and
release verification are recorded in the linked workpad._

The shared context response uses contract version `2`. Ranking rule version
`1` remains unchanged.

| ID | Product requirement | Verification |
|---|---|---|
| BMS-REQ-001 | Each context brief shall identify context contract version `2`. | Core, command, and MCP payload assertions |
| BMS-REQ-002 | Each returned memory shall include a one-line title of at most 160 Unicode characters. | Kind and boundary tests |
| BMS-REQ-003 | Each returned memory shall identify its summary as `cluster_scope`, `proposed_root_cause`, or `learning_takeaway`. | Kind matrix |
| BMS-REQ-004 | Each returned memory shall include a one-line summary of at most 2,000 Unicode characters. | Multiline and over-limit tests |
| BMS-REQ-005 | The shared core shall derive each summary only from the canonical content that its summary kind identifies. | Exact source-content assertions |
| BMS-REQ-006 | The shared core shall preserve each memory kind and canonical epistemic status. | Proposed, rejected, and Learning state assertions |
| BMS-REQ-007 | The command, MCP, SessionStart, and UserPromptSubmit adapters shall expose semantically equivalent title, summary, status, match, and source facts. | Adapter and hook matrices |
| BMS-REQ-008 | The context fingerprint and token shall bind context contract version `2` while ranking rule version `1` remains unchanged. | Token decode and repeat equality |
| BMS-REQ-009 | Context retrieval shall not modify canonical or derived board state, execute code, or use network access after it adds memory content. | No-write, hostile-input, and closed-proxy tests |
| BMS-REQ-010 | The shared core shall not infer a stronger epistemic state from summary content. | Proposed-hypothesis assertion |

The exact result fields are:

```json
{
  "title": "<one line; 0-160 Unicode characters>",
  "summary_kind": "cluster_scope | proposed_root_cause | learning_takeaway",
  "summary": "<one line; 0-2000 Unicode characters>"
}
```

The fields are additive. Existing clients can ignore them. The same shared
core supplies the plugin command, MCP tool, SessionStart, and
UserPromptSubmit. No adapter implements its own content selection.

All returned Markdown content remains untrusted data. The core collapses line
and control separators. It truncates content after the applicable character
limit. It does not execute content, make a network request, open a source
reference, change canonical Markdown, or record raw task text.

A cluster summary is structural evidence. A hypothesis summary is an
inference with the separate H### status. A Learning summary is a durable
takeaway with its separate outcome status. Match reasons and source
references remain separate from the memory claim.

The formal structured requirement artifact remains draft until it receives
digest-matched human reviews and baseline approval. This state does not change
the owner's source decision that selects and authorizes the product
correction.

## 22. Research and evidence

Current product evidence:

- [`2026-07-31 bounded memory summary contract`](evidence/2026-07-31-bounded-memory-summary-contract.md)
- [`2026-07-30 Milestone D.1 version 4 proposal preflight`](evidence/2026-07-30-milestone-d1-corpus-v4-proposal.md)
- [`2026-07-29 Milestone D.1 live-evaluation preflight`](evidence/2026-07-29-milestone-d1-live-evaluation-preflight.md)
- [`2026-07-29 Milestone D.1 client-neutral evaluation contract`](evidence/2026-07-29-milestone-d1-client-neutral-evaluation-contract.md)
- [`2026-07-29 Milestone D.1 corpus-calibration contract`](evidence/2026-07-29-milestone-d1-corpus-calibration-contract.md)
- [`2026-07-29 Milestone D.1 calibrated reference run`](evidence/2026-07-29-milestone-d1-calibrated-reference-run.md)
- [`2026-07-29 Milestone D.1 harness implementation`](evidence/2026-07-29-milestone-d1-harness-implementation.md)
- [`2026-07-29 Milestone D.1 product-proof contract workpad`](evidence/2026-07-29-milestone-d1-product-proof-contract.md)
- [`2026-07-29 v1.11.0 release validation`](evidence/2026-07-29-v1.11.0-release-validation.md)
- [`2026-07-28 Milestone D implementation validation`](evidence/2026-07-28-milestone-d-implementation-validation.md)
- [`2026-07-28 Milestone D contract workpad`](evidence/2026-07-28-milestone-d-contract.md)
- [`2026-07-28 v1.10.0 release validation`](evidence/2026-07-28-v1.10.0-release-validation.md)
- [`2026-07-28 Milestone C implementation validation`](evidence/2026-07-28-milestone-c-implementation-validation.md)
- [`2026-07-28 Milestone C contract workpad`](evidence/2026-07-28-milestone-c-contract.md)
- [`2026-07-28 v1.9.1 release validation`](evidence/2026-07-28-v1.9.1-release-validation.md)
- [`2026-07-28 Milestone B implementation validation`](evidence/2026-07-28-milestone-b-implementation-validation.md)
- [`2026-07-27 Milestone B contract evidence`](evidence/2026-07-27-milestone-b-contract.md)
- [`2026-07-27 v1.8.0 release validation`](evidence/2026-07-27-v1.8.0-release-validation.md)
- [`2026-07-27 pattern-intelligence direction evidence`](evidence/2026-07-27-pattern-intelligence-direction.md)
- [`2026-07-27 Milestone A contract evidence`](evidence/2026-07-27-milestone-a-contract.md)
- [`2026-07-27 Milestone A implementation validation`](evidence/2026-07-27-milestone-a-implementation-validation.md)
- [`2026-07-27 initial spec validation`](evidence/2026-07-27-product-evolution-spec-validation.md)
- [`README.md`](../README.md)
- [`ROADMAP.md`](../ROADMAP.md)
- [`ACTIVATION.md`](../ACTIVATION.md)
- [`RETENTION.md`](../RETENTION.md)
- [`COMPREHENSION.md`](../COMPREHENSION.md)
- [`commands/board-graph.md`](../commands/board-graph.md)
- [`skills/board-intake/SKILL.md`](../skills/board-intake/SKILL.md)
- [`skills/board-triage/SKILL.md`](../skills/board-triage/SKILL.md)
- [`hooks/scripts/board-curate-learnings.sh`](../hooks/scripts/board-curate-learnings.sh)
- [`hooks/scripts/board-session-start.sh`](../hooks/scripts/board-session-start.sh)

External product references, reviewed 2026-07-26-27:

- [Beads](https://github.com/gastownhall/beads)
- [Backlog.md](https://github.com/MrLesk/Backlog.md)
- [Task Master](https://github.com/eyaltoledano/claude-task-master)
- [Claude Code Tasks](https://code.claude.com/docs/en/interactive-mode#task-list)
