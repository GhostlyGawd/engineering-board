# Research log — agentic-ecosystem

Reverse-chronological. One entry per working session. Terse: what was done, what
was found, what's next.

## 2026-06-08 (session 2) — profiled harness-sdd + symphony-clone

- **Profiled** two more systems from public source (cloned + read via fan-out
  subagents): **harness-sdd** (constitution v1.1.0; POSIX-sh + python3 + a tiny TS
  CLI) and **symphony-clone** (v0.1.0, Node ESM, zero-dep) — the latter a clean-room
  re-impl of **OpenAI's** Symphony spec. → `profiles/harness-sdd.md`,
  `profiles/symphony-clone.md`.
- **Findings that move the synthesis:**
  - **Worker-execution fork (#2) is now 5-wide.** symphony-clone is a **third headless
    `claude -p`** build (joining AEM + AE) — and it's the very system RFC 0001 cited as
    *observable* prior art, yet its workers are headless. But **harness-sdd actually
    shipped the OBSERVABLE model** EB's Conductor bets on: a deterministic sh wave-engine
    that *refuses* to spawn agents and delegates every spawn to the attachable
    coordinator session as Task/Agent subagents in worktrees (single-unit; fan-out
    deferred). Observable-worker is no longer EB-only — there's a worked precedent.
  - **Falsifiability (#3) gains a 4th position:** harness-sdd enforces at the **commit
    gate** (pre-commit + CI). symphony-clone is the outlier — enforces **nowhere**
    (done = agent self-edits the tracker `state:`).
  - **Substrate (#1):** both sit at the legible/markdown pole; neither opens the empty
    "typed AND legible" quadrant (pattern #7 holds; AE alone at the DB pole).
  - **Lineage:** neither shares the Superpowers 8-stance-panel code — harness-sdd traces
    to the author's own `/batch` + the Ralph loop; symphony-clone to OpenAI Symphony.
- **Blocked:** **norns-loop** + **solo-os** are **private**; the GitHub MCP is scoped to
  engineering-board and scope-expansion tools aren't in this session, so they can't be
  profiled without access (make public / read token / paste source).
- **Started a living consolidation PRD** (`consolidation/prd.md`) from the 5 profiled
  systems: current leanings on all 7 forks, a sketch of the unified product, a
  thought-experiment v0, carry-forward map. A research doc we keep updating — not a spec.
- **Next:** unblock norns-loop + solo-os (private) and keep refining the PRD as we go.

## 2026-06-08 — kickoff: profiled the three core systems + built the maps

- **Profiled** engineering-board, agentic-engineering-max (v2.4.0, via public
  repo), and agentic-engineering (v0.1.0) via fan-out subagents reading each
  repo. → `profiles/*.md`.
- **Built 5 visual maps** (`comparisons/`): genealogy, 2×2 positioning, substrate
  stacks, lifecycle swimlanes, capability matrix. Authored as SVG, rendered to
  PNG with `@resvg/resvg-js`.
- **Synthesis** (`comparisons/synthesis.md`): 7 cross-cutting patterns. Headline —
  the autonomous, parallel, **headless** worker-in-worktree orchestrator was built
  **twice** (AEM `orchestrator-loop.ps1`, AE `orchestrate.py`); engineering-board's
  RFC 0001 Conductor is designing the **opposite** (observable, attachable
  sessions). The defining fork across all three is the **state substrate**
  (markdown board / markdown+HUD / SQLite-graph-via-MCP).
- **Maps** shipped to `main` via PR #14, then relocated under this thread.
- **Next:** firm up consolidation direction (see `consolidation/`); candidates to
  profile next — norns-loop, Symphony / symphony-clone, harness-sdd.
