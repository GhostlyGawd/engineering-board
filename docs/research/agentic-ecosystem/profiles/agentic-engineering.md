# Profile — agentic-engineering (AE)

> Snapshot 2026-06-08. Source: **public** `agentic-engineering` repo (fully public;
> dogfoods itself).

**Identity:** a **self-improving engineering system** — a typed SQLite knowledge
graph + falsifiability-gated specs + independent verification, with all durable
writes mediated by a bundled stdio **MCP server**. Treats a project as *"a small
organization with persistent memory rather than a stateless pipeline."*

**Repo / version / lang / status:** `GhostlyGawd/agentic-engineering` (public) ·
**v0.1.0** · Python ≥3.12 + MCP (`mcp==1.27.1`) · MIT · Windows-only (PS 5.1
SessionStart hook; POSIX planned). The most architecturally ambitious engine.

## Core mental model
Every Goal / Spec / Task / Decision / Bug / Finding / Pattern / Module / File /
Review / Retro / ArchDebt is a **typed node in a graph**. Specs can't dispatch
unless **falsifiable**; multiple **independent** reviewers verify; the system reads
its own **Retros** to improve over time.

## State substrate
**A real database behind a server.** SQLite typed graph at `./.agentic/graph.db`
(`schema.sql`): **14 named entity types** (+ `epic`, `subtask` = 16 entity-shape
tables), a typed `relations` edge table (`implements`/`depends-on`/`blocks`/
`supersedes`/`caused-by`/…), `claim` + `calibration` tables (schema v3),
`critical_loop` table; `PRAGMA user_version` migrations. **All durable writes go
through the bundled stdio MCP server** (`Server("agentic-graph")`, **26 tools**) —
the only writer. Not git-diffable, not hand-editable; the server is a hard
dependency.

## Components
- **7 agents** (`model: sonnet`): `builder`, `spec-checker`, `code-reviewer`,
  `contrarian`, `spec-writer`, `orchestrator`, `pattern-finder`. *(The 8-stance
  epistemic panel appears here as a worked example in `norns-loop-review/`, and as
  agents in AEM.)*
- **8 commands** `/agentic:*`: `init`, `detect-conflicts`, `import-spec`,
  `dispatch`, `review-pr`, `new-spec`, `orchestrate`, `find-patterns`.
- **2 skills:** `router`, `spec-writing`. **SessionStart hook** (injects open-spec
  / dispatched / critical counts).
- **~45 Python tests** incl. **live-`claude` e2e** behind a default-off `-m llm`
  marker. No `marketplace.json` (single plugin). **No `CLAUDE.md` by design**
  (philosophy in skills; context via SessionStart injection).

## Orchestration model
**Stateless single-tick** `orchestrate.py` — each `tick()` rehydrates from the
graph: weed stale specs → pick a **max-disjoint-scope batch** of ready tasks
(DAG-gated via `implements` + `depends-on`) → `claim_scope` (overlap →
`ClaimConflict` → serial; unknown scope → `["**"]` → forced serial) → dispatch
**headless `claude -p --permission-mode bypassPermissions`** builders into real
**git worktrees** (`.worktrees/<task>`, branch `orch/<task>`) → review + calibrate
→ merge CLEAN in DAG topo order (`git merge --no-ff`). Never raises (failures
become result dicts → crash-safe/resumable). Dispatch failure → `critical_loop`
strike; 3rd strike → escalate.

## Review / verification
**Four-role, anti-collusion:** `builder` → `spec-checker` (**context-isolated** —
sees *only* the spec + artifact files, never the builder's prose) gates first →
then `code-reviewer` + `contrarian` run **blind to each other, in parallel**
("gate-then-parallel"). **Four-tier severity:** Critical (blocks; loops with **no
cap**) / Important (needs `record_triage` fix-in-pr|backlog) / Suggested /
Strength (feeds calibration). **CriticalLoop:** no cap but a one-time iteration-3
*"maybe the spec is wrong"* diagnostic; state in SQLite, control on the Claude
side. **Contrarian:** asymmetric "assume it's wrong" — hunts
architecture/concurrency/scaling/security/hidden-assumptions, **not** style.
**Trust calibration:** `record_outcome` / `adjust_trust`, Laplace-smoothed score,
`distrusted` flag (FLOOR 0.4 / CEILING 0.7).

## Falsifiability stance
At **spec dispatch** — the hardest of the three. `validate_spec`: every criterion's
`verify` must start with a runnable command prefix (`pytest`/`npm`/`cargo`/`mypy`/
`ruff`/`./`…) **or** name a runtime signal (`p95`/`error rate`/`logs show`…),
**and** the spec must declare a `feedback_loop` with both an observable signal and
a fix path; a hand-wave blocklist (`tbd`/`todo`/`works correctly`/`appropriately`…)
rejects vague prose. Dispatched specs are **immutable** (supersession only).

## Self-improvement (the thesis)
Retros tagged by `failed_layer` (spec/implementation/integration/review/unknowable)
→ `pattern-finder` mints `Pattern` nodes (derived-from evidence; rejects
coincidence) → **(Phase 4, deferred)** automation rewrites reviewer/spec-writer
prompts + reviewer trust decay. *"Phase 1 records, Phase 4 calibration judges."*
`detect_stability_contradiction` logs a **soft** Pattern when a Critical hits a
byte-identical file a reviewer previously approved — **records, never suppresses.**

**Status:** Phases 0–2 shipped · Phase 3 partial (`pattern-finder` +
`/agentic:find-patterns` exist; sqlite-vec embeddings, architectural-review agent,
cross-project meta-graph deferred) · Phase 4 deferred.

## Distinctive design decisions
- DB + MCP-server as substrate (typed invariants, indexed queries, atomic claims).
- Falsifiability as a **hard pre-dispatch gate**; dispatched-immutability +
  supersession.
- **Stateless resumable** orchestration (crash-safe; failures-as-data).
- Serial-when-shared scope isolation with a **fail-safe default** (`["**"]`).
- **Record-never-suppress** + deferred judgment.
- **Trust calibration on the reviewers themselves.**
- Real-agent e2e behind a default-off marker.
- **No `CLAUDE.md`** by design.

## Strengths / gaps (for consolidation)
- **Strengths:** the most rigorous engine — typed invariants, independent
  verification, calibration, falsifiability hard-gate, resumable worktree
  orchestration, live e2e.
- **Gaps:** DB opaque to git, not hand-editable, MCP server is a hard dependency;
  Windows-only; least productized surface (v0.1.0); self-improvement loop is still
  substrate-only (Phase 4 deferred).

## Consolidation notes
Carry forward: the **typed-graph rigor**, the **falsifiability hard-gate**
validator, **context-isolated + blind-parallel + contrarian** review, **trust
calibration**, **stateless resumable worktree** orchestration, and the
**retros→patterns** substrate. The **DB-vs-legibility** tradeoff is the central
consolidation fork.
