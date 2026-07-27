# Engineering Board Product Evolution Spec

_Status: Authoritative living product direction — Gate 1 and Milestone A Gate 2
accepted; Milestone A implemented on the direction branch, pending review and
merge_
_Started: 2026-07-27_
_Last direction revision: 2026-07-27_
_Product owner: GhostlyGawd_
_Repository: `GhostlyGawd/engineering-board`_
_Current live baseline: `main` at `4ee6c5239e152b20c4c2a07ef0c4d4fceefa48f3`_
_Portfolio context: inventory-only; audit source `GhostlyGawd/repo-audit` at
`907f0759f9d08f478cd5384ad88e50963f1af79a`_

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

- **Accepted** — explicitly chosen product direction.
- **Active recommendation** — recommended, but still revisable by the owner.
- **Open** — a material product choice is unresolved.
- **Deferred** — deliberately outside the next milestone.
- **Rejected** — considered and deliberately excluded.

No product implementation begins until an implementation contract for the
selected milestone is approved.

## 2. Decision ledger

| Decision | State | Current direction |
|---|---|---|
| Central product-direction source | Accepted | This document is authoritative for product direction. Roadmaps, RFCs, audits, and earlier prose cannot silently override it. |
| Primary product outcome | Accepted | Turn accumulated engineering findings into visible, clustered graph memory that helps agents recognize recurring and cross-domain root causes, avoid repeated band-aid fixes, and make better decisions in later sessions. |
| Product substrate | Accepted | Pattern intelligence is the substrate. Capture, execution, TDD, review, and validation support and improve that intelligence; they are not the primary product identity. |
| Durable state | Accepted | Preserve repository-owned, human-readable Markdown as the canonical evidence and knowledge record. |
| Derived graph | Accepted | Generate machine-readable relationships, clusters, and retrieval views from canonical repository state. Derived artifacts must remain explainable from source evidence. |
| SQLite | Active recommendation | Do not replace Markdown. Consider SQLite only as a disposable, locally rebuildable analysis index after measured scale or query needs justify it. |
| Epistemic boundary | Accepted | Separate observed evidence, deterministic relationships, inferred root-cause candidates, confirmed conclusions, and durable learnings. Never present a cluster as proof of causation. |
| Hypothesis authority | Accepted | Root-cause hypotheses may be stored durably with `status: proposed` and evidence. Only explicit investigation or fix outcomes may confirm them. Rejected hypotheses remain durable negative knowledge. |
| Default capture policy | Active recommendation | Capture automatically; promote explicitly through a foreground action. Automatic capture does not silently become committed project truth. |
| Verification loop | Accepted | Keep `tdd → review → validate` as an optional, falsifiable fix-verification and feedback mechanism. Do not make it the required first experience or the headline value. |
| Claims and resolution | Active recommendation | Preserve atomic claims. Validation may recommend closure; final resolution remains an explicit user or explicitly authorized action. |
| Session modes | Active recommendation | Keep PM and Worker modes as advanced batch controls, not required concepts in the default pattern-memory workflow. |
| Cross-repository intelligence | Deferred | Prove repository-local pattern intelligence before designing aggregation across repositories. |
| Hosted service or required database | Deferred | No hosted control plane, daemon, account system, cloud sync, or required database in the next milestones. |
| Structured planning bridge | Deferred | PRD decomposition remains a possible later input path, not the product substrate. |
| Cross-session Conductor | Deferred | RFC 0001's persistent supervisor is not the next required product step. |
| Team dashboard and monetization | Deferred | Do not build until repository-local intelligence has demonstrated repeatable value. |
| Pending PR #93 | Independent | The B057 fix and 1.7.1 release preparation remain separate from this direction branch. |
| Milestone A delivery | Accepted and implemented | The contained synthetic `/board-demo`, deterministic demo graph engine, proposed-hypothesis contract, real evidence view, cleanup boundary, tests, and dated validation are implemented on the direction branch. Merge, release, tag, and deployment remain separately authorized actions. |

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
| Pattern vocabulary | Intake asks agents to reuse kebab-case failure-mode tags and apply them broadly. | Free-form exact strings fragment easily; aliases, hierarchy, and semantic equivalence are not represented. |
| Structural graph | `/board-graph` defines nodes, explicit relationships, shared-pattern, shared-affects, shared-tag edges, topology, and typed findings in `GRAPH.yml`. | The graph builder is a command procedure rather than a shared deterministic executable engine. Exact tags and path prefixes miss semantically related cross-domain symptoms. |
| Cluster surfacing | Intake and triage flag a pattern at 2+ occurrences; SessionStart warns at 3+ open occurrences. | Thresholds and presentation differ. Counts identify recurrence but do not explain cluster evidence or competing hypotheses. |
| Learning curation | At 3+ resolved entries sharing an exact pattern, the curator creates a source-linked Learning and raises confidence by recurrence. | Curation runs through PM mode, treats recurrence count as the main confidence signal, and does not learn from failed fixes or rejected causal hypotheses. |
| Context retrieval | SessionStart shows up to three medium/high-confidence learnings filtered by `applies_to` and current directory. | Retrieval is path-centric and does not surface relevant live clusters, root-cause candidates, or the reason a cross-domain match matters. |
| Resolution feedback | Resolution archives pattern tags and can cascade across pattern/affects neighbors. | A resolution does not yet record whether the suspected root cause was confirmed, whether the fix held, or which cluster interpretation changed. |
| Quality workflow | Worker mode can drive `tdd → review → validate`, retain claims, and ask for explicit resolution. | This strong implementation loop dominates the current story even though it is downstream of the intelligence benefit. |

The product does not need a new identity invented from scratch. It needs to
connect and elevate mechanisms it already partially owns.

## 6. Epistemic model

Pattern intelligence is only valuable if agents can tell what is known from
what is inferred.

| Layer | Meaning | Authority | Durable form |
|---|---|---|---|
| Observation | A symptom, constraint, result, or user report with provenance. | Captured evidence; reviewed at promotion. | Canonical Markdown finding/entry. |
| Relationship fact | An explicit dependency, contradiction, shared exact pattern, shared affected prefix, or other reproducible relation. | Deterministic rule or explicit author. | Derived graph edge with source/rule reference. |
| Candidate cluster | A reproducible grouping that crosses a configured threshold. | Deterministic clustering engine. | Rebuildable derived graph record. |
| Root-cause hypothesis | An interpretation explaining why cluster members may share a cause. | Agent-generated proposal with cited members, confidence, alternatives, and falsifier. | Proposed insight; durable only when retained through an explicit policy. |
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
| Portability and zero-service use | Excellent | Requires schema/tooling | Excellent; index optional |
| Transactions and referential integrity | Manual | Strong | Canonical writes remain explicit; index can validate |
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

- deletion and deterministic rebuild from canonical Markdown;
- logically equivalent query and cluster results with and without the index;
- source provenance for every returned result;
- no committed binary database or database merge workflow;
- schema versioning and forward recovery;
- corrupt or stale index detection with safe self-rebuild;
- cross-platform packaging and performance evidence;
- no dependency on SQLite for reading, editing, reviewing, or recovering the
  board.

SQLite is therefore a future optimization candidate, not a product-direction
migration.

## 8. Competitive position

Engineering Board should selectively absorb useful interaction patterns from
adjacent products while preserving its distinct job.

| Source | Strength to learn from | Apply to Engineering Board | Boundary |
|---|---|---|---|
| [Beads](https://github.com/gastownhall/beads) | Durable agent memory, graph queries, ready work, and multi-agent coordination. | Make graph memory and contextual retrieval first-class; provide concise next investigation/action. | Do not adopt database-first authority or distributed sync before a current consumer requires it. |
| [Backlog.md](https://github.com/MrLesk/Backlog.md) | Rich, inspectable Markdown tasks and human-friendly browsing. | Keep evidence, hypotheses, acceptance criteria, and learning provenance easy to read and review. | Do not become a general-purpose project-management suite. |
| [Task Master](https://github.com/eyaltoledano/claude-task-master) | PRD decomposition and recommended-next workflows. | Later accept structured plans as one finding source and make the next investigation obvious. | Planning breadth is not the intelligence substrate. |
| Claude Code Tasks | Frictionless in-session checklist. | Compose with it: ephemeral steps remain session-local; durable discoveries enter Engineering Board. | Do not rebuild a personal checklist. |

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

### Milestone A — Pattern-intelligence first win

**Purpose:** Demonstrate the unique product value in one session.

**Implementation state:** complete on the direction branch; pending review and
merge. The delivered scope is:

- A bounded cross-domain sample with a known shared failure pattern.
- Canonical `/board-setup` guidance.
- Foreground sample capture/promotion without PM-mode ceremony.
- Graph and cluster output with member evidence and relationship reasons.
- A root-cause candidate clearly labeled as an inference.
- Explicit, fingerprinted sample cleanup or retention.
- A real visual showing evidence → cluster → root-cause candidate.

If omitted, the first experience continues to showcase workflow mechanics
instead of the product's intelligence advantage.

### Milestone B — Reliable finding-to-graph pipeline

**Purpose:** Ensure real findings become trustworthy, connected memory.

Candidate scope:

- Foreground promotion outside PM mode.
- Pattern normalization and alias handling.
- Stable pattern IDs while preserving readable labels.
- Shared deterministic graph engine used by plugin and MCP paths.
- Unified cluster thresholds and typed output.
- Provenance and correction path for pattern assignments and edges.
- Incremental rebuild contract without adopting a required database.

If omitted, intelligence remains dependent on exact free-form tags and
adapter-specific prompt execution.

### Milestone C — Cross-domain root-cause intelligence

**Purpose:** Turn structural clusters into useful, bounded engineering
interpretation.

Candidate scope:

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

### Milestone D — Contextual retrieval and outcome learning

**Purpose:** Deliver accumulated intelligence at the decision where it changes
agent behavior.

Candidate scope:

- Retrieval based on current files, task intent, patterns, graph neighbors, and
  prior outcomes—not only current working directory.
- SessionStart and on-demand surfacing of relevant clusters and learnings.
- Resolution feedback that updates hypothesis and learning confidence.
- Source-linked explanation of why a memory applies.
- Value reporting based on useful resurfacing and confirmed systemic fixes, not
  vanity counts.

If omitted, the repository may contain strong memory that the acting agent
still fails to use.

### Milestone E — Execution ergonomics and planning bridge

**State: Deferred until A–D are proven.**

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
9. Confirmed fix outcomes strengthen the relevant learning; failed or partial
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

## 13. Accepted and open decisions

### O1 — Pattern normalization

Options:

1. Curated canonical pattern IDs with readable aliases.
2. Free-form tags plus embedding/semantic similarity at query time.
3. A hybrid: canonical IDs for durable memory and bounded semantic suggestions
   for proposed aliases or links.

Recommendation: option 3. Exact canonical identity keeps durable results
deterministic; semantic suggestions can discover cross-domain equivalence but
must remain reviewable before becoming durable.

### A1 — Hypothesis authority

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

### O3 — Cluster model

Options:

1. Exact pattern recurrence only.
2. One global similarity score.
3. Typed signals—explicit relationships, normalized pattern, affected domain,
   temporal recurrence, evidence semantics, and outcome history—with each
   contribution exposed.

Recommendation: option 3. A single opaque score would make false positives hard
to diagnose and weaken trust.

### O4 — First-win fixture

The sample must contain different surface symptoms and affected domains that
share a verifiable root pattern. The owner still needs to approve the exact
scenario and containment/cleanup model before implementation.

### O5 — SQLite trigger and latency target

The layered storage direction is set; the numeric corpus and interactive
latency threshold that would justify an optional SQLite index remains open.
Benchmark the file/graph implementation first rather than inventing a threshold
without evidence.

### O6 — Promotion boundary

Recommendation: a foreground promote action writes validated findings, reports
created/rejected/deduplicated outcomes, and offers a preview. Silent
auto-promotion remains deferred.

### O7 — Resolution and learning feedback

Recommendation: after verification, offer an explicit resolve action that also
records the hypothesis outcome. Do not silently convert successful validation
into confirmed causation.

## 14. Alternatives

### Keep emphasizing the build loop

This proves engineering discipline but underuses the accumulated corpus. Many
tools can run tests and reviews; the unique advantage is recognizing patterns
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

## 15. Explicit non-goals for Milestones A–D

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
| Product-direction authority | Accepted | No runtime behavior | Owner decision recorded here | This file; `ROADMAP.md` precedence note | Direction aligned |
| Pattern-intelligence substrate | Accepted direction | Existing production capture/pattern/graph/curation plus contained Milestone A evidence → cluster → proposed-hypothesis first win | Existing graph/curator tests; Milestone A orchestration, graph, hypothesis, integration, and live-validation evidence | README and landing page now lead with pattern intelligence while distinguishing demo scope from production behavior | Milestone A aligned; production generalization remains Milestone B/C |
| Hypothesis authority | Accepted direction | Demo hypotheses persist as Markdown with `status: proposed`; schema and `board-insights` prohibit confirmation | Hypothesis contract tests and dated live validation | Proposed, confirmed, and rejected authority transitions are explicit | Milestone A aligned |
| Canonical Markdown | Accepted | Entry and learning Markdown is current durable state | Existing intake, rebuild, resolve, and curation tests | Architecture direction documented here | Aligned |
| Derived graph | Accepted direction | `/board-graph` remains the production prompt contract; `board-graph-build.py` is the executable engine used by the contained demo and accepts explicit board paths | Existing command contract plus graph-engine and integration tests | Demo scope and production limitation stated explicitly | Milestone A aligned; shared production integration remains Milestone B |
| SQLite | Optional future accelerator | Not implemented or required | Future benchmark and rebuild-equivalence proof required | Migration explicitly rejected; adoption trigger recorded | Deferred optimization |
| Current capture confirmation | Required current truth | Stop procedure and append helper surface a non-empty receipt | `tests/scratch/append.sh`; mode-routing tests | README was corrected in this branch | Documentation-only drift repaired |
| Canonical setup instruction | Required current truth | `/board-setup` is the plugin setup path | Setup command test | Landing page was corrected in this branch | Documentation-only drift repaired |
| TDD/review/validate | Required current truth, supporting future role | Worker loop remains shipped and unchanged | Existing mode and orchestration tests | Repositioned as optional falsifiable verification feedback, not the headline or required first experience | Behavior unchanged; messaging aligned |
| MCP behavior | Required current truth | Current tools unchanged | Existing MCP tests remain authoritative | Proposed semantic parity is not claimed shipped | Reviewed and unaffected |
| Security, privacy, versions, releases | Required current truth | Demo adds a contained synthetic run and manifest-verified cleanup; manifests and release state unchanged | Negative containment/tamper tests and dated live validation | SECURITY and changelog updated; no version, release, or deployment claim | Behavior and docs aligned; release unaffected |
| Historical audits and evidence | Historical | Preserved | Superseding dated evidence added | Historical claims are not rewritten | Reviewed and preserved |

## 17. Gate 2 accepted: Milestone A implementation contract

_State: Accepted by the product owner on 2026-07-27 and implemented on the
direction branch. Review/merge remains pending._

### 17.1 Milestone purpose

> Give a new user one bounded, trustworthy experience in which three
> surface-different engineering symptoms across separate domains become one
> evidence-linked systemic investigation candidate—proving the product's
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
   `.engineering-board/demo/pattern-intelligence/<run-id>/`;
2. copy only the three labeled sample entries and required templates;
3. record a manifest containing relative paths and content hashes before any
   analysis;
4. build deterministic graph facts from the sample;
5. show the candidate cluster, member evidence, relationship reasons, and
   affected domains;
6. create one evidence-linked `status: proposed` hypothesis;
7. show at least one alternative explanation and one falsifier;
8. render a local static visual and print its path;
9. report the exact cleanup command and that modified files will be preserved.

The command must not:

- initialize or edit the user's real board;
- modify a board router, source file, settings file, or Git configuration;
- start PM/Worker mode;
- run code-generation or fix the synthetic issue;
- require an additional network service, service credentials, SQLite, or a
  hosted control plane beyond the already-active agent runtime;
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
  graph state; generated files are never hand-edited as authority.

### 17.5 State, preservation, and cleanup

| Condition | Meaning | Required behavior |
|---|---|---|
| No prior demo run | Clean start | Create a unique run directory and manifest. |
| Complete unchanged run exists | Repeat request | Reuse or create a new run without overwriting the prior run; report which occurred. |
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
  builder for explicit board paths. Milestone A integrates it with the demo;
  real-board modifying commands remain unchanged until Milestone B.
- `skills/board-insights/SKILL.md`: interpret a completed cluster into the
  hypothesis schema without changing deterministic graph facts.
- `skills/board-intake/references/hypothesis-schema.md`: normative hypothesis
  fields, sections, states, and authority rules.
- `references/demo/pattern-intelligence/`: the three synthetic canonical
  entries and expected scenario metadata.
- `hooks/scripts/board-view.sh`: render the demo's evidence → cluster →
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

- Malformed sample or graph input → non-zero typed error naming the exact
  relative file; no partial success claim.
- Missing Python runtime → explicit prerequisite error; no package installation.
- Analysis timeout or interpreter failure → preserve the run and print a safe
  retry command.
- Hypothesis output missing required citations or sections → reject the output
  as invalid and leave deterministic graph results available.
- Path escape, symlink, reparse point, manifest expansion, or unexpected file →
  refuse cleanup.
- Existing user data under the selected run path → never overwrite; allocate a
  new run ID.
- Captured visual and evidence → synthetic data only; no usernames, absolute
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
| Hypothesis authority | Output is `status: proposed`, cites `B001`–`B003`, includes an alternative and falsifier, and cannot auto-confirm from confidence. |
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
8. Append dated evidence; do not rewrite historical reports.

### 17.10 Documentation-impact contract

When implemented:

| Surface | Required disposition |
|---|---|
| This product spec | Mark Milestone A contract accepted and later record shipped evidence without rewriting the decision history. |
| README and quickstart | Lead the optional first win with pattern intelligence; keep current behavior claims accurate. |
| Landing page | Show the evidence → cluster → proposed-hypothesis outcome only after live validation. |
| Command docs | Add `/board-demo`; revise `/board-setup` optional next step; document cleanup and offline boundaries. |
| Architecture | Document canonical Markdown, deterministic graph facts, interpreted hypotheses, and authority transitions. |
| MCP docs | State unaffected unless an equivalent demo/analysis surface actually ships. |
| Security/privacy | Document contained synthetic data, no-extra-service behavior, path validation, and cleanup refusal conditions. |
| Visuals | Add a real sanitized demo capture with date, source version, alt text, and provenance. |
| Tests/evidence | Add the matrix above and a dated live-validation report. |
| Versions/releases | Review at delivery; change only if the owner separately approves a release. |

### 17.11 Non-goals and delivery boundary

Milestone A does not:

- analyze arbitrary real boards through the new engine by default;
- normalize free-form production tags;
- add semantic embeddings or SQLite;
- confirm hypotheses;
- change resolution, learning confidence, PM/Worker mode, claims, or MCP tools;
- fix the synthetic root cause;
- add cross-repository aggregation or a hosted service;
- merge, release, tag, or deploy without separate owner authorization.

Implementation delivery is this focused branch and draft PR with code, tests,
current-truth documentation, a real visual, and dated evidence. The owner's
approval authorized implementation and push to the draft PR; it did not
authorize merge, release, tag, or deployment.

## 18. Research and evidence

Current product evidence:

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

External product references, reviewed 2026-07-26–27:

- [Beads](https://github.com/gastownhall/beads)
- [Backlog.md](https://github.com/MrLesk/Backlog.md)
- [Task Master](https://github.com/eyaltoledano/claude-task-master)
- [Claude Code Tasks](https://code.claude.com/docs/en/interactive-mode#task-list)
