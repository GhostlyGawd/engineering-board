# Consolidation PRD — one agentic-engineering product (Draft)

> **Status:** Draft · 2026-06-08 · lives in the research workbench (upstream of
> `specs/`). Seeded from the [agentic-ecosystem](../README.md) thread.
> **Evidence base:** 5 of 7 systems profiled ([`../profiles/`](../profiles/));
> **norns-loop** + **solo-os** are private/unprofiled (§8 gap).
> **Forks:** positions below are **leans/decisions for a draft**, not locked — this
> graduates to a top-level `specs/` PRD once the forks settle and the gap closes.
> Reasoning trail: [`./README.md`](./README.md) · [`../comparisons/synthesis.md`](../comparisons/synthesis.md).

## 1. Problem & thesis

One author is running **several parallel agentic-engineering systems** that keep
**re-deriving the same primitives in different languages** (deterministic core /
LLM-at-edges, atomic claiming, "a fresh session reconstructs state", cross-platform
lint, never auto-edit `CLAUDE.md`). That's duplicated maintenance and split learning.

**Thesis:** converge on **one** product. The comparison shows the pieces already
exist across the five systems — no single one has them all, but together they
describe a complete design. The job is **selection + integration**, not invention.

The distinctive bet (the gap nobody filled): a substrate that is **typed _and_
legible** — git-native markdown as the source of truth, with typed invariants
enforced *over* it. (Synthesis pattern #7: every system trended to one pole; the
upper-left quadrant is empty.)

## 2. What the five systems taught us (evidence base)

| System | One-line lesson it contributes |
|---|---|
| **engineering-board** | passive finding-capture + **transcript-anchor falsifiability at capture**; git-native legibility; the untrusted-data boundary. |
| **agentic-engineering-max** | the **productization layer** — web HUD, release discipline, scientific-method plan interviewer, epistemic-lens panel. |
| **agentic-engineering** | the **rigor** — typed graph, falsifiability-as-hard-gate, context-isolated independent review, trust calibration, stateless resumable orchestrator, real-agent e2e. |
| **harness-sdd** | the **observable** coordinator-spawns-subagents-in-worktrees wave engine; gate-of-gates + golden fixtures; **commit-gate falsifiability**; drop-in installer packaging. |
| **symphony-clone** | the cleanest **always-on reconcile tick** (poll→reconcile→retry→dispatch + stall/backoff); a reusable subscription-native `claude` stream-json adapter; **and the cautionary baseline** (no falsifiability → all risk on the human). |

## 3. Decisions on the 7 forks (Draft positions)

| # | Fork | Draft decision | Why | Lifted from |
|---|---|---|---|---|
| 1 | **State substrate** | **Git-native markdown = source of truth + a typed validator/gate layer; an optional derived SQLite index for fast queries (never authoritative).** Aim the empty "typed **and** legible" quadrant. | 4/5 chose legible/markdown; legibility (git-diff, hand-edit, zero-dep, fresh-session reconstruct) is the through-line. AE's typed rigor is the missing half — add it as *validation over files*, not a server-of-record. | EB/harness (files); AE (typed invariants); harness `check-*.sh` (validate the markdown status machine) |
| 2 | **Worker execution** | **Pluggable executor; default OBSERVABLE** (coordinator spawns subagents in worktrees), **headless `claude -p` as a throughput backend.** | Observability is the open differentiator and now a *worked* precedent (harness-sdd), not just EB's RFC bet; headless is proven 3× for scale. | harness-sdd (observable); AE/AEM/symphony (headless); all (git worktrees) |
| 3 | **Falsifiability** | **Enforce at all four points — capture · spec/plan · commit gate · review. Never zero.** | The four positions are complementary, not competing; symphony-clone proves "none" dumps 100% of quality risk on the human reviewer. | EB (capture); AE (spec-dispatch); harness (commit gate); AEM/AE (review) |
| 4 | **Review** | **Context-isolated, multi-reviewer (correctness + spec-conformance), both-must-pass, fixer-amends loop, with trust calibration over time;** epistemic-lens panel as an opt-in deep mode. | AE's anti-collusion rigor + harness's clean both-pass loop are the floor; AEM's panel is the richest add-on. | AE (isolation + trust calibration); harness (both-pass + fixer loop); AEM (lens panel) |
| 5 | **Self-improvement** | **Commit to it, stage it late.** v0 = manual "every recurring mistake becomes a rule or a gate." Later = automated retro→pattern→prompt-rewrite. | Only AE *designed* the loop (and even there Phase 4 is deferred); harness has it as a manual constitution principle. Don't block v0 on it. | harness (manual discipline §10); AE (the loop thesis) |
| 6 | **Surface / UX** | **CLI + hooks as the core; read-only web HUD for fleet observability; MCP tools as an integration surface; a drop-in installer to land in target repos.** | Layered, not either/or — each system optimized a different surface. | EB (CLI+hooks); AEM/symphony (HUD); AE (MCP); harness (installer packaging) |
| 7 | **Language / runtime** | **Python core; POSIX-sh only for git hooks; drop PowerShell; Node only if the HUD warrants it.** | Common denominator (AE is Python; EB/harness shell to python3); cross-platform; pwsh-only is a portability tax. | AE (Python); EB/harness (python3 + sh) |

## 4. The unified product (target architecture)

A **git-native engineering control plane** that captures work, drives it to PRs, and
verifies it can't hand-wave — legible to humans and git, typed where it counts.

- **Substrate:** markdown board/specs are the committed source of truth; a **schema +
  gate layer** enforces typed invariants over them (statuses, dependencies, evidence
  links). A derived SQLite index is a *cache* rebuilt from files, never the record.
- **Intake (two modes, one board):** *reactive capture* (EB's Stop-hook finding
  extraction, transcript-anchored) **and** *directed specs* (harness's PRD→SPEC→PLAN
  with one ALIGN gate). The board holds both; the pipeline is shared.
- **Orchestration:** an always-on **reconcile tick** (symphony's poll→reconcile→retry→
  dispatch + stall/backoff) drives a **pluggable executor**; workers run in **git
  worktrees**, observable by default.
- **Verification spine:** falsifiability at all four points; context-isolated
  multi-reviewer + trust calibration; PR is the **handoff-to-review** output
  (never auto-merge).
- **Surfaces:** CLI + hooks (core), read-only HUD (fleet observability), MCP
  (integration), drop-in installer (how it lands in a target repo).
- **Runtime:** Python core + POSIX-sh git hooks; deterministic core, LLM only at the
  edges; the untrusted-data boundary (scratch is data, not instructions) is global.

## 5. v0 — the minimum that proves the thesis

The smallest cut that shows **one system replaces the others' core**, end to end:

1. **One git-native substrate** (markdown board/specs) + a **typed gate** that
   validates it (reject a status that outruns its artifacts; reject an
   acceptance criterion with no runnable check).
2. **Capture-time falsifiability** (transcript anchor) on intake.
3. **One OBSERVABLE worker** in a git worktree doing **one unit** (singleton before
   fan-out).
4. **Commit gate + one context-isolated reviewer**; fixer-amends loop.
5. **Output a PR** and stop at review.

If that loop runs green on one substrate, it subsumes EB's capture, harness's gate,
and symphony's loop on a single spine. **Explicit v0 non-goals:** fan-out
parallelism, automated self-improvement loop, typed-DB-of-record, web HUD, headless
backend, trust calibration — all deferred to post-v0 once the spine holds.

## 6. Carry-forward map (lift list)

- **From EB:** Stop-hook capture + the transcript-anchor verifier; markdown-as-DB
  legibility; the untrusted-data boundary; atomic `mkdir` claims; print-only gitignore;
  two-manifest version coherence.
- **From AEM:** the read-only web HUD; release discipline + `*-doctor` self-check; the
  scientific-method plan interviewer; the epistemic-lens panel (deep-review mode).
- **From AE:** the typed-invariant model (re-homed *over* files); `validate_spec`
  hard-gate; context-isolated spec-checker + blind contrarian; Laplace-smoothed trust
  calibration; the stateless resumable orchestrator; real-agent (`-m llm`) e2e tests.
- **From harness-sdd:** the observable coordinator→subagents-in-worktrees wave engine;
  gate-of-gates + golden-fixture self-eval; commit-gate checks; deterministic
  git-safety guard hooks; singleton-before-fan-out; the drop-in installer packaging.
- **From symphony-clone:** the reconcile-tick loop (poll→reconcile→retry→dispatch +
  stall/backoff); the subscription-native `claude` stream-json adapter (the single most
  reusable artifact); pluggable trackers w/ a git-native default; handoff-to-review.

## 7. Migration

**Greenfield core, but ingest existing boards.** The unified substrate reads existing
**markdown** boards/specs directly (EB, harness, symphony-local) — those port for free.
**AE's SQLite graph** is the one real migration: a one-time export→markdown+schema
importer (the typed data survives; the server dependency is dropped). No big-bang
cutover — run the unified product against one repo first (dogfood), keep the others
until the v0 spine proves out.

## 8. Open questions & gaps

- **Two systems still unprofiled (private):** **norns-loop** ("3-Claude orchestrator",
  ALife loop — likely informs the **executor/orchestration** fork directly) and
  **solo-os** ("agent-team OS for a solo founder" — likely informs **surface/scope**).
  Decision was to draft now and fill later; revisit forks #2 and #6 once they're in.
- **Is the unified product one of the five evolved, or a new core?** Lean: **a new core
  that borrows** — but EB is the closest skeleton (git-native, capture + gate + RFC'd
  observable orchestrator), so "EB, evolved" is the cheapest path. Decide before specs.
- **The typed-and-legible substrate (fork #1) is the highest-risk bet** — needs a
  concrete schema/validation design (what's structurally enforced vs gate-checked).
- **Executor interface contract** (fork #2): the seam that lets observable and headless
  backends be swapped — define it before building either.
- **Round boundary / done-detection** (carried from RFC 0001 §10): symphony proves
  "agent self-edits board state, loop re-reads" works *if* paired with a falsifiability
  gate (which symphony lacks and this product adds).

## 9. Non-goals

- A typed database as the **source of truth** (legibility is non-negotiable; typing
  rides *over* files).
- Fire-and-forget autonomy with no human gate (keep ALIGN + handoff-to-review).
- PowerShell / single-OS lock-in.
- Re-deriving any primitive a fifth time — **build the shared primitives once.**
