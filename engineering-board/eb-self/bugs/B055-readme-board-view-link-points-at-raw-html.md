---
id: B055
type: bug
title: README "rendered live by /board-view" link points at a raw .html blob (GitHub shows source)
discovered: 2026-07-04
status: resolved
priority: P3
affects: README.md
needs: tdd
pattern: [docs, link-degradation]
---

## Done when
- The README hero "rendered live by /board-view" link no longer lands a first-time reader on raw HTML source; either it points at a rendered/hosted view or the link text is softened so the raw-source destination isn't surprising.

## Observed behavior (C8 Track B — P3, low confidence)
README hero links "rendered live by /board-view" to `engineering-board/eb-self/board.html`. GitHub serves committed `.html` as raw source text, so a reader clicking it on the repo front page lands on a wall of HTML, mildly contradicting "rendered live". The adjacent board-demo.svg renders fine; only the hyperlink target degrades.

## Fix direction
Soften the link text (e.g. "the HTML `/board-view` generates") or point at a hosted render.

## Resolution (C8, PR C8b)
README hero link text now reads 'the HTML /board-view generates … open it locally to render' so the raw-source destination isn't surprising.
