# Consolidation — toward one repo / harness / product

The point of this thread: stop running several parallel agentic-engineering
systems and **converge on one.** This folder is where that thinking accumulates
until it's ready to become a real **consolidation PRD** (then graduate to `specs/`
or a PRD doc and leave a pointer back here).

Nothing here is decided — these are the questions the comparison surfaced that a
unified product has to answer.

## The big forks to resolve (from [`../comparisons/synthesis.md`](../comparisons/synthesis.md))

1. **State substrate — the master variable.** markdown board (legible, git-native,
   hand-editable, zero deps) vs. SQLite typed graph behind an MCP server (typed
   invariants, indexed queries, atomic claims — but opaque to git, not
   hand-editable, server is a hard dependency) vs. the middle (files + a HUD).
   *Everything else cascades from this.* The unexplored quadrant is "typed **and**
   legible" — is there a representation that's both?
2. **Worker execution model.** Observable, attachable sessions vs. headless
   `claude -p` fleets — now **3 headless** builds (AEM, AE, **symphony-clone**) vs.
   **2 observable** (**harness-sdd** shipped a coordinator-spawns-subagents-in-worktrees
   wave engine; EB's RFC 0001 bets on attachable tmux sessions). Observability is a
   *worked* option now, not just EB's bet. Observability vs. throughput/simplicity —
   pick one, or make it pluggable.
3. **Where falsifiability is enforced.** At capture (EB transcript anchor) /
   planning+review (AEM epistemic lenses) / spec-dispatch (AE hard gate) / **commit
   gate (harness-sdd pre-commit+CI)** — four complementary positions, not competing; a
   unified product could enforce at **all four**. (symphony-clone enforces at *none* —
   the cautionary baseline: an always-on loop that pushes all quality risk onto the
   human reviewer.)
4. **Review model.** reviewer+validator (EB) vs. epistemic-lens panel (AEM) vs.
   context-isolated spec-checker + blind contrarian + trust calibration (AE).
   AE's independent-verification design is the most rigorous; AEM's panel the
   richest — reconcile into one.
5. **Self-improvement.** Only AE designed the retros→patterns→prompt-rewrite loop
   (and even there Phase 4 is deferred). Decide whether the unified product
   commits to it.
6. **Surface / UX.** CLI + hooks (EB) vs. web HUD (AEM) vs. MCP-tools-only (AE).
7. **Language / runtime.** bash + python3 (EB) vs. PowerShell / pwsh 7 (AEM) vs.
   Python + MCP (AE). Consolidation likely means picking one — **Python** is the
   common denominator (AE is Python; EB already shells to python3).

## What each build does best (carry-forward candidates)

- **engineering-board** — passive finding-capture with transcript-anchor
  verification; git-native legibility; the Stop-hook intake discipline.
- **agentic-engineering-max** — the productization layer: web HUD control plane,
  `/aem-doctor`, release discipline, the most polished operator experience.
- **agentic-engineering** — the rigor: typed graph, falsifiability-as-hard-gate,
  context-isolated independent review, trust calibration, stateless resumable
  orchestrator, real-agent e2e tests.
- **harness-sdd** — the *observable* worktree wave engine (coordinator spawns the
  subagents — no black box); gate-of-gates + golden-fixture self-eval; commit-time
  falsifiability; deterministic git-safety guards; the drop-in harness-installer
  packaging.
- **symphony-clone** — the cleanest always-on reconcile tick (poll → reconcile →
  retry → dispatch, with stall-detect + backoff) and a reusable subscription-native
  `claude` stream-json adapter; pluggable trackers with a git-native markdown default.

## Open questions for the PRD

- Is the unified product **one of these three, evolved**, or a **new core** that
  borrows from all (e.g., AE's engine + AEM's HUD + EB's capture discipline)?
- Migration: do existing boards/graphs need to port, or is this greenfield?
- What is the **minimum** that proves the consolidation thesis (the v0 cut)?

## Next steps

- harness-sdd + Symphony now profiled (5 systems mapped). Remaining: **norns-loop**
  and **solo-os** — both **private**, blocked on repo access (the GitHub MCP is scoped
  to engineering-board this session). Unblock (make public / read token / paste
  source), then profile.
- Once the forks above have leanings, draft the consolidation PRD.
