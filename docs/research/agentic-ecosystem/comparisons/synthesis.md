# Synthesis — cross-cutting patterns

Patterns across the five profiled systems — **engineering-board (EB)**,
**agentic-engineering-max (AEM)**, **agentic-engineering (AE)**, **harness-sdd**, and
**symphony-clone (Symphony)**. See the maps in this folder (drawn for the first three;
harness-sdd + symphony-clone are folded into the prose below, not yet redrawn); see
[`../profiles/`](../profiles/) for per-system detail. Snapshot: 2026-06-08
(extended with harness-sdd + symphony-clone).

## 1. One author's signature, three substrates — and the substrate is the master variable
*(maps: `01-genealogy`, `03-substrate`)* — The defining fork is **where state
lives**: markdown board → markdown + HUD → SQLite-graph-behind-an-MCP-server.
Map 3's takeaway pills say it in five words each: *"Files ARE the database" /
"Files + a dashboard" / "A real database behind a server."* Almost every other
difference (legibility, who can write, what's enforceable) cascades from this one
choice. → consolidation fork #1.

## 2. Falsifiability is the through-line obsession — inserted at four lifecycle points (with one holdout)
*(maps: `04-lifecycle` ★ badges, `05-capability` row 5)* — Four of the five refuse to
let the LLM hand-wave, but bolt the gate on at different stages: **EB at capture**
(evidence must anchor to the transcript), **AEM at planning + review**
(scientific-method interviewer + epistemic lenses), **AE at spec-dispatch** (a
deterministic validator rejects any criterion without a runnable check), and
**harness-sdd at the commit gate** (pre-commit + CI fail a spec whose `Status:`
outruns its artifacts). The holdout is **symphony-clone** — it enforces *nowhere*:
"done" is the agent self-editing the tracker `state:`, backstopped only by turn
budgets + the human review gate. Same value, four positions — a unified product can
enforce at all of them.

## 3. The headless worker-in-worktree loop was built three times — but the observable alternative was built too
*(map: `04-lifecycle` bottom callout; `05` row 3)* — AEM (`orchestrator-loop.ps1`),
AE (`orchestrate.py`), and **symphony-clone** (`claude -p --output-format
stream-json`) all ship the autonomous loop EB's **RFC 0001** is still drafting — all
three **headless**. (Sharp irony: symphony-clone is the very system RFC 0001 names as
*observable* orchestrator prior art, but its workers are in fact headless.) The twist:
**harness-sdd already built the observable model** EB is betting on — a deterministic
sh wave-engine that *cannot* spawn agents and hands every spawn to the **attachable
coordinator session** as Task/Agent subagents in worktrees (single-unit; fan-out
deferred to B14). So fork #2 is a real **3-headless vs. 2-observable** split
(harness-sdd shipped it; EB's Conductor still RFC), with a worked precedent on both
sides — not EB alone. → consolidation fork #2 (observability vs. throughput).

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
opportunity. **The two systems profiled since only reinforce it:** harness-sdd and
symphony-clone both sit at the legible/markdown pole (specs + git gates; an in-memory
loop over a markdown board) — five systems in, the typed-**and**-legible quadrant is
still empty, and AE still stands alone at the typed-DB pole.

---

**Consolidation implications:** [`../consolidation/`](../consolidation/).
