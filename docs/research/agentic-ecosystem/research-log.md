# Research log — agentic-ecosystem

Reverse-chronological. One entry per working session. Terse: what was done, what
was found, what's next.

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
