# Research

Durable home for **ongoing, exploratory research** — the kind that accumulates
over many sessions and eventually crystallizes into a decision, spec, RFC, or
PRD. Each Claude Code web session starts from a fresh clone, so research that
should survive across chats has to be committed here.

## How this differs from the other doc areas

| Area | Holds | Lifecycle |
|---|---|---|
| **`docs/research/`** (here) | open-ended investigation, profiles, comparisons, notes | accretes; graduates into a spec/RFC/PRD when it matures |
| `specs/` | settled design specs for engineering-board itself | design-locked |
| `docs/rfcs/` | proposals for engineering-board features | Draft → Accepted |
| runtime board (`engineering-board/<project>/`) | findings captured *during coding* (bugs/features/questions) | worked through the `needs:` pipeline |

Research is upstream of all of those: it's where you think *before* committing to
a design.

## Convention

- **One subfolder per research thread.** Each thread owns a `README.md`
  (charter + index + status) and accumulates `profiles/`, `comparisons/`,
  `notes/`, and a dated `research-log.md` as needed.
- **High-signal but allowed to be messy** — this is a workbench, not a published
  doc. Half-formed is fine; just date it.
- **When a thread matures into a decision,** graduate it to a `specs/` doc, a
  `docs/rfcs/` RFC, or a PRD — and leave a pointer back here for the reasoning trail.

## Threads

- **[`agentic-ecosystem/`](agentic-ecosystem/)** — comparing & contrasting the
  agentic-engineering systems built so far, toward consolidating them into a
  single repo / harness / product. *(active, started 2026-06-08)*
