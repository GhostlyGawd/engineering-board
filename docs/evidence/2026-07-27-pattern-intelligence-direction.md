# Pattern-Intelligence Direction Evidence — 2026-07-27

## Scope

This report records the current implementation evidence used to revise
[`docs/PRODUCT_EVOLUTION_SPEC.md`](../PRODUCT_EVOLUTION_SPEC.md) around
clustered pattern memory and to evaluate Markdown versus SQLite.

Repository baseline:
`GhostlyGawd/engineering-board` `main` at
`4ee6c5239e152b20c4c2a07ef0c4d4fceefa48f3`.

Portfolio status:
inventory-only, using `GhostlyGawd/repo-audit` context at
`907f0759f9d08f478cd5384ad88e50963f1af79a`.

No runtime behavior, storage schema, dependency, security boundary, release, or
external integration changed in this revision.

## Observed implementation

| Product layer | Evidence | Observation |
|---|---|---|
| Capture | `hooks/stop-hook-procedure.md`; `hooks/scripts/board-scratch-append.sh` | Turn findings are appended with provenance and a visible receipt, but scratch capture does not yet assign normalized pattern identity. |
| Pattern intake | `skills/board-intake/SKILL.md`; `skills/board-intake/references/frontmatter-schema.md` | Intake instructs agents to reuse failure-mode-oriented kebab-case tags and tag first occurrences so later recurrence can be detected. |
| Pattern triage | `skills/board-triage/SKILL.md` | A pattern with 2+ open or archived occurrences is surfaced as a systemic investigation candidate. |
| Graph contract | `commands/board-graph.md` | The command specifies deterministic nodes, typed edges, clusters, topology, and findings in `GRAPH.yml`. Repository inventory found no separate graph-builder executable; the shipped artifact is a command procedure plus contract tests. |
| Session surfacing | `hooks/scripts/board-session-start.sh` | SessionStart warns at 3+ open occurrences and separately retrieves up to three medium/high-confidence learnings filtered by `applies_to` and working directory. |
| Learning curation | `hooks/scripts/board-curate-learnings.sh`; `agents/learnings-curator.md` | The curator creates a Learning at 3+ resolved entries with one exact pattern tag, derives sources, and sets confidence to medium or high based on recurrence. |
| Resolution feedback | `skills/board-resolve/SKILL.md` | Resolution preserves pattern tags, rebuilds derived views, and scans pattern/affects neighbors, but it does not record whether a root-cause hypothesis or fix outcome was confirmed or rejected. |
| Quality pipeline | `hooks/stop-hook-procedure.md` | Worker mode implements TDD, review, and validation transitions. It is a verification mechanism rather than evidence that clustered root-cause intelligence is complete. |

## Current gap

The components exist but are not yet one coherent intelligence loop:

1. Pattern identity is free-form and exact-string based.
2. Thresholds differ between triage, SessionStart, and learning promotion.
3. Deterministic relationships do not discover semantically equivalent
   cross-domain symptoms unless an agent first assigns the same tag.
4. Graph facts stop before evidence-linked causal interpretation.
5. Recurrence dominates learning confidence; failed fixes, counter-evidence,
   domain diversity, and rejected hypotheses do not feed it.
6. Retrieval is path-centric and does not prioritize live cluster context.
7. The current product story emphasizes the downstream quality pipeline more
   than the upstream intelligence benefit.

## Markdown versus SQLite assessment

The current consumer is a repository-local pattern-memory system. Markdown
already supplies its authoritative evidence, human review, Git history,
portability, and agent readability. Replacing it with SQLite would remove
meaningful direct inspection while not solving normalization, causal
interpretation, retrieval relevance, or learning feedback.

SQLite could become useful as a rebuildable read index for:

- compound graph/history queries;
- full-text retrieval;
- incremental aggregation;
- large-corpus ranking and analysis;
- integrity checks across derived relations.

The recommended boundary is therefore:

- Markdown is canonical.
- Graph and query artifacts are derived.
- SQLite is optional, local, ignored by Git, deletable, and rebuildable.
- Adoption requires a benchmarked consumer need and equivalence/recovery tests.

No present failure requires SQLite, so no dependency or migration is proposed.

## Documentation alignment

| Surface | Classification | Disposition |
|---|---|---|
| Product-direction authority | Documentation-only direction change | `docs/PRODUCT_EVOLUTION_SPEC.md` now records its central authority and precedence. |
| Product thesis and milestone order | Documentation-only direction change | Pattern intelligence now leads; verification and execution ergonomics are supporting/deferred layers. |
| Roadmap precedence | Documentation-only drift, repaired | `ROADMAP.md` now defers to the central product-direction spec instead of describing it as a non-authoritative draft. |
| Current README and landing setup/capture corrections | Reviewed and unaffected by this revision | The initial spec commit already repaired current-truth capture and setup wording; this revision does not change those behaviors. |
| Current command and architecture contracts | Reviewed and unaffected | No shipped command, schema, transition, or adapter changed. Current limitations are recorded without claiming future behavior. |
| MCP documentation | Reviewed and unaffected | No MCP tool or capability changed. |
| Security and privacy | Reviewed and unaffected | No credential, network, execution, storage, or trust boundary changed. |
| Versions, releases, manifests, and changelog | Reviewed and unaffected | No release or version claim changed. |
| Existing visuals | Recommended future gap | No future cluster UI is claimed shipped; Milestone A requires real visual evidence when implemented. |
| Historical audits and validation report | Reviewed and preserved | Dated evidence is not rewritten. This report supersedes only the direction interpretation. |

## Evidence limits

- Contract tests establish that the graph command describes required structures;
  they do not prove a shared executable graph engine or semantic correctness.
- Existing recurrence tests prove exact-tag curation behavior, not cross-domain
  causal intelligence.
- No benchmark has demonstrated a need for SQLite, so no latency threshold is
  claimed.
- No live first-win journey changed in this documentation-only revision.

## Deterministic validation

Run from the isolated `docs/product-evolution-spec` worktree after the direction
revision:

```text
bash tests/orchestration/board-graph-command.sh
  52 pass, 0 fail

bash tests/orchestration/learnings-curator.sh
  13 pass, 0 fail

bash tests/docs-coherence.sh
  pass (12 MCP tools; 14 plugin commands across checked current-truth surfaces)

bash tests/token-coherence.sh
  pass (105 token comparisons across the landing page and board renderer)

git diff --check
  pass
```

Repository-relative links in the product spec were inventoried and their target
paths were confirmed to exist. External links were not treated as deterministic
local evidence.
