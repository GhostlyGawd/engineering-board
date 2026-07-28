# Milestone C contract workpad — 2026-07-28

## Decision continuity

- Active outcome: turn deterministic clusters into useful, bounded root-cause
  intelligence for real boards.
- Gate 1: accepted by the product owner on 2026-07-28.
- Gate 2: accepted by the product owner on 2026-07-28; implementation shipped
  as v1.10.0 against central product spec section 19.
- Canonical storage: repository-owned Markdown.
- Derived state: deterministic graph, rank payloads, and HTML projections.
- Explicitly deferred: SQLite, embeddings, hosted services, cross-repository
  aggregation, automatic learning updates, contextual SessionStart retrieval,
  and execution of proposed fixes.
- External boundary: the owner already permits commit, push, merge, release,
  publication, and deployment after implementation and release gates pass.

Repository context:

```text
repository: GhostlyGawd/engineering-board
default_branch: main
baseline_commit: ce47d4cfd62b463dee9715009fc3afa9b794c9e3
implementation_base: 51be227d2d85fd6fb4c5498981514ac441f73181
portfolio_status: inventory-only
audit_source: GhostlyGawd/repo-audit@907f0759f9d08f478cd5384ad88e50963f1af79a
```

## Baseline evidence

v1.9.1 provides stable P### identity, foreground promotion, a shared
deterministic graph core, stable cluster fingerprints, source-bound mutation
plans, and plugin/MCP adapter parity. Production code does not rank clusters,
persist real-board H### hypotheses, enforce negative memory, evaluate
hypothesis outcomes, or render those records in the normal board view.

The contained Milestone A demo already proves the narrow interpretation
contract: exact member citations, one alternative, one falsifier, strict
`status: proposed`, HTML escaping, and no confirmation authority. Milestone C
generalizes that bounded behavior to real boards and adds lifecycle memory.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| Transparent cluster ranking | Required for Milestone C | `rank_clusters` and `build_insights` implement rule v1 over graph schema 3 | Milestone C matrix proves deterministic tie order, component output, CLI/MCP parity, cache deletion, and offline equivalence | Product spec 19.3; README; architecture; `/board-insights`; MCP and LLM docs | Worker-validated |
| Canonical production H### records | Required for Milestone C | Shared core validates, serializes, lists, previews, locks, and atomically applies H### Markdown under `hypotheses/` | Matrix proves no-write preview, exact citations, malformed payload refusal, stale token refusal, single creation, and scaffold behavior | Product spec 19.4–19.8; production hypothesis schema; `/board-hypothesis`; init docs | Worker-validated |
| Evaluation and negative memory | Required for Milestone C | Claim fingerprints, typed negative memory, evidence-gated evaluate/reopen, and split/merge lineage implemented | Matrix proves reject/block/reopen, confirm evidence gate and success, split without children, invalid merge, valid merge, and reverse lineage | Product spec 19.6–19.7; skill; schema; changelog | Worker-validated |
| Plugin and MCP parity | Required current product boundary | `/board-insights`, `/board-hypothesis`, `board_insights`, and `board_hypotheses` delegate to one core | Matrix compares CLI/MCP/shared results; 166-check MCP suite discovers all 17 tools and validates packaging | Command docs, README, MCP reference, architecture, llms, manifests | Worker-validated |
| Pattern-intelligence HTML | Required user-visible proof | Normal `board-view.sh` renders ranked clusters, linked members, H### state, stale bindings, evidence, alternatives, and falsifiers without controls | Matrix proves escaped hypothesis content, stale label, and no mutation controls; 50-check view suite passes | `/board-view`; README and landing; real sanitized Milestone C SVG | Worker-validated |
| Security and preservation | Required | Self-contained tokens bind graph, inventory, target bytes, request, and operation; apply revalidates under lock; linked records/payloads fail closed | Matrix exercises malformed evidence, stale input, repeated apply, closed proxies, escaping, and preserved history; full security suites pass | SECURITY, architecture, schema, product spec | Worker-validated |
| Version, release, and closeout | Required at delivery | Manifests and package metadata identify v1.10.0; 17-tool/19-command counts align; the reproducible MCPB digest is pinned | 16/16 release-tree suites, PR CI, merged-main CI, release workflow, bundle digest, and live publication checks pass | Changelog, manifests, implementation validation, and v1.10.0 release validation | Shipped and externally validated |
| Historical Milestone A/B evidence | Required preservation | No behavior or historical file change proposed | Existing suites must remain green | Historical reports reviewed; no rewrite required because they remain dated truth | Reviewed and unaffected |

No required conflict remains in the worker phase. The implementation evidence
is in `2026-07-28-milestone-c-implementation-validation.md`. Deterministic
checks prevent omission but do not substitute for semantic review.

## Evidence phases

- Worker phase: complete. The deterministic matrix, targeted suites, full
  release tree, offline run, package reproducibility, sanitized visual, and
  documentation alignment passed.
- Post-merge phase: complete. Merged-main CI, the v1.10.0 tag, GitHub Release,
  PyPI package, official MCP Registry version, and Pages deployment passed.
- Closeout phase: complete after the release report and shipped-state updates
  merge and fresh merged-main CI passes.

## Current handoff

Milestone C is terminal and shipped as v1.10.0. The central spec now governs
the next product decision. SQLite, embeddings, hosted services,
cross-repository aggregation, automatic learning updates, SessionStart
retrieval, and fix execution remain deferred. A new milestone requires a new
accepted implementation contract.
