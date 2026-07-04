---
id: B050
type: bug
title: /board-view (flagship visual viewer) absent from the Quickstart first-value path
discovered: 2026-07-04
status: resolved
priority: P3
affects: README.md
needs: tdd
pattern: [onboarding, discoverability]
---

## Done when
- The Quickstart's "how do I see my board" moment references `/board-view` (the themed visual Kanban) alongside `/board-rebuild` (markdown index refresh), so a first-time user discovers the headline viewer F001 shipped.

## Observed behavior (C7 Track B — P3)
README Quickstart's "visible confirmation" sentence points only at `_sessions/` or `/board-rebuild` (which regenerates the markdown BOARD.md index, not the visual board). `/board-view` (generates board.html) appears only in the hero caption + command list, never in the Quickstart — so a user following only the Quickstart is pointed at the markdown-refresh command at the exact moment they want to SEE their board, and never discovers the visual viewer that closed the visualization competitive gap.

## Fix direction
One-line README edit: add `/board-view` to the step-3 "visible confirmation" sentence.

## Resolution (C7, PR C7b)
README Quickstart 'visible confirmation' sentence now surfaces /board-view (themed visual Kanban) alongside /board-rebuild (markdown index refresh).
