---
id: B042
type: bug
title: Landing page did not surface /board-view and still conceded the visualization gap it closed
discovered: 2026-07-04
status: resolved
priority: P3
affects: docs/index.html
needs: tdd
pattern: [marketing-coherence]
---

## Done when
- The landing page mentions /board-view / the committed HTML board and the visualization-gap concession is reconciled honestly (static committed view, not a live daemon).

## Observed behavior (C4 Track B/D)
docs/index.html kept "Agent-MCP ships a live dashboard" with no mention of the just-shipped viewer; F001's CHANGELOG says it "closes the biggest conceded competitive gap (visualization)". The answer to the gap was invisible on the primary marketing surface.

## Resolution (C4, PR C4b)
The comparison concession now states engineering-board answers visualization with /board-view (committed, offline, zero-dep HTML; no daemon; on-brand in-repo projection) — honest (not a live dashboard) and surfaces the feature.
