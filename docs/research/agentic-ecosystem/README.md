# agentic-ecosystem — research thread

**Focus:** compare and contrast the different agentic-engineering systems I've
built, so I can see how it all maps out — and eventually **consolidate them into
one repo / harness / product.** External / adjacent systems (Superpowers,
claude-squad, Symphony, …) are in scope when they inform that consolidation.

**Output it feeds:** a future **consolidation PRD** — what the single unified
product should be, and what to carry forward from each existing build.

**Status:** active · started 2026-06-08.

---

## Systems in scope

| System | What it is | Substrate | Profile |
|---|---|---|---|
| **engineering-board** (this repo) | triage / work-capture control plane | markdown board | ✅ [profile](profiles/engineering-board.md) |
| **agentic-engineering-max** (AEM) | build factory + web HUD (plan→build→review) | markdown tasks + web HUD | ✅ [profile](profiles/agentic-engineering-max.md) |
| **agentic-engineering** (AE) | self-improving verification engine | SQLite graph via MCP | ✅ [profile](profiles/agentic-engineering.md) |
| **harness-sdd** | drop-in spec-driven-dev harness (gates, not an engine) | markdown specs + git gates | ✅ [profile](profiles/harness-sdd.md) |
| **symphony-clone** (Symphony) | clean-room Claude-native clone of OpenAI's Symphony orchestrator | markdown board + in-memory loop | ✅ [profile](profiles/symphony-clone.md) |
| _candidates (private — blocked)_ | norns-loop · solo-os | — | ☐ not accessible (private repos) |

## Contents

- **[`profiles/`](profiles/)** — one deep profile per system, on a shared template
  so they're directly comparable.
- **[`comparisons/`](comparisons/)** — the visual maps (5× SVG + PNG) and
  **[`synthesis.md`](comparisons/synthesis.md)** (the cross-cutting patterns).
- **[`consolidation/`](consolidation/)** — the "what the unified product should
  be" thinking; the seed of the PRD.
- **[`research-log.md`](research-log.md)** — dated running log, session by session.

## How to add to this thread

1. **Profiling a new system** → add `profiles/<name>.md` from the shared template;
   read it from source (don't trust memory), and note version + access caveats.
2. **Found a cross-cutting pattern** → update `comparisons/synthesis.md`.
3. **Always** → append a dated line to `research-log.md`.
4. **Consolidation implications** → capture in `consolidation/`.

## Caveats (read before trusting any figure here)

- **agentic-engineering-max** was read via its **public** repo — a leak-gated
  `git subtree split` of the private `Dev_006` dev repo — so `Dev_006`'s bleeding
  edge may be ahead of these notes. **agentic-engineering** is fully public.
  **engineering-board** is read from this repo directly.
- Profiles are **point-in-time** snapshots (first pass: 2026-06-08); versions and
  phases move. Date every update.
