# Synthesis — cross-cutting patterns

Patterns across **engineering-board (EB)**, **agentic-engineering-max (AEM)**, and
**agentic-engineering (AE)**. See the maps in this folder; see
[`../profiles/`](../profiles/) for per-system detail. Snapshot: 2026-06-08.

## 1. One author's signature, three substrates — and the substrate is the master variable
*(maps: `01-genealogy`, `03-substrate`)* — The defining fork is **where state
lives**: markdown board → markdown + HUD → SQLite-graph-behind-an-MCP-server.
Map 3's takeaway pills say it in five words each: *"Files ARE the database" /
"Files + a dashboard" / "A real database behind a server."* Almost every other
difference (legibility, who can write, what's enforceable) cascades from this one
choice. → consolidation fork #1.

## 2. Falsifiability is the through-line obsession — inserted at three different lifecycle points
*(maps: `04-lifecycle` ★ badges, `05-capability` row 5)* — All three refuse to let
the LLM hand-wave, but bolt the gate on at different stages: **EB at capture**
(evidence must anchor to the transcript), **AEM at planning + review**
(scientific-method interviewer + epistemic lenses), **AE at spec-dispatch** (a
deterministic validator rejects any criterion without a runnable check). Same
value, three positions — in a unified product they're complementary (enforce at
all three).

## 3. The autonomous headless-worker-in-worktree orchestrator was built twice — EB is deliberately building the opposite
*(map: `04-lifecycle` bottom callout; `05` row 3)* — AEM (`orchestrator-loop.ps1`)
and AE (`orchestrate.py`) both already ship the thing EB's **RFC 0001** is still
drafting — and both did it **headless** (`claude -p`). EB's design explicitly
**rejects** that black box for **observable, attachable** sessions. EB is the
contrarian on worker observability, twice over → consolidation fork #2
(observability vs. throughput).

## 4. Version number inverts capability
*(map: `05` row 10)* — **AE v0.1.0** has the most advanced *engine*; **AEM v2.4.0**
is the most *productized*; **EB v1.1.0** is the most *scope-conservative*. Version
is a release-posture signal, not a depth signal.

## 5. Convergent evolution of the same primitives
*(map: `01` shared-instincts band)* — Deterministic core / LLM-only-at-edges;
atomic claiming (mkdir-lock vs `FileStream CreateNew` vs claim-table-with-overlap);
"a fresh session reconstructs state"; cross-platform lint; never auto-write
`CLAUDE.md`. The author keeps re-deriving the same building blocks in three
languages → the consolidation should build these **once**.

## 6. Components physically leak between siblings
*(map: `01` dotted connector)* — The **8-stance epistemic panel** appears in AEM
(as agents) and AE (as the review lenses in `norns-loop-review/`), both tracing
back to the **"Superpowers"** ancestor. Not independent designs — shared parts.

## 7. The one trade nobody took: typed AND legible
*(map: `02-positioning` — the empty upper-left quadrant)* — AE's DB buys typed
invariants but loses git-diff legibility; EB's markdown keeps legibility but can't
*structurally* enforce invariants; AEM splits the difference. Nobody built
"typed-DB triage." All three trend to the directed/structured corner, with **EB
alone anchoring the legible/reactive corner** — that gap is the consolidation
opportunity.

---

**Consolidation implications:** [`../consolidation/`](../consolidation/).
