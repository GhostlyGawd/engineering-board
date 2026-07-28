# Milestone C contract workpad — 2026-07-28

## Decision continuity

- Active outcome: turn deterministic clusters into useful, bounded root-cause
  intelligence for real boards.
- Gate 1: accepted by the product owner on 2026-07-28.
- Gate 2: proposed in section 19 of the central product spec; implementation
  requires explicit approval.
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
| Transparent cluster ranking | Required for Milestone C | Shared-core rule proposed; no code change yet | Deterministic ranking and adapter parity cases specified in section 19.10 | Product spec section 19.3 | Gate 2 proposed |
| Canonical production H### records | Required for Milestone C | Schema and directory contract proposed; no code change yet | Preview/apply, stale plan, exact citation, and concurrent-create cases specified | Product spec sections 19.4–19.8; hypothesis schema update pending implementation | Gate 2 proposed |
| Evaluation and negative memory | Required for Milestone C | Transition and claim-fingerprint rules proposed; no code change yet | Reject/reproposal, reopen, confirm, split, and merge cases specified | Product spec sections 19.6–19.7 | Gate 2 proposed |
| Plugin and MCP parity | Required current product boundary | Two commands and two MCP tools proposed over one shared core | CLI/MCP payload comparison and MCP lifecycle cases specified | Command, MCP, README, and architecture updates pending implementation | Gate 2 proposed |
| Pattern-intelligence HTML | Required user-visible proof | Read-only normal-board section proposed; current Kanban and demo remain | State labels, stale binding, injection, and no-mutation-control cases specified | View docs and real sanitized visual pending implementation | Gate 2 proposed |
| Security and preservation | Required | One-file atomic mutation, plan revalidation, lock, linked-input refusal, offline scope, and history preservation proposed | Failure and security sequences specified in section 19.10 | SECURITY and schema updates pending implementation | Gate 2 proposed |
| Version, release, and closeout | Required at delivery | v1.10.0 proposed after green implementation gates | Full release tree, reproducible package, publication checks, and merged-main closeout CI required | Changelog, manifests, dated implementation evidence, and later release report pending | Gate 2 proposed |
| Historical Milestone A/B evidence | Required preservation | No behavior or historical file change proposed | Existing suites must remain green | Historical reports reviewed; no rewrite required because they remain dated truth | Reviewed and unaffected |

No required conflict exists in the proposed contract. Implementation evidence
is intentionally pending. Path and keyword checks will prevent omission, but
they will not substitute for semantic review.

## Evidence phases

- Worker phase: deterministic matrix, targeted suites, full release tree,
  offline run, package reproducibility, sanitized visual, and documentation
  alignment.
- Post-merge phase: merged-main CI, tag, GitHub Release, package publication,
  MCP Registry publication, and Pages deployment.
- Closeout phase: append external evidence in a new Markdown report, mark
  Milestone C shipped, merge that report, and require fresh merged-main CI.

## Current handoff

Required reviewer decision: approve or revise the Gate 2 contract in central
spec section 19. If approved, resume from the implementation component map in
section 19.9 and the evidence matrix in section 19.10.
