---
id: B002
type: bug
status: open
needs: tdd
priority: P1
title: Board renders the same review-ready state in the wrong lane
affects: board-view/lifecycle-lanes
discovered: 2026-07-27
pattern: [duplicated-state-contract]
tags: [synthetic-demo, lifecycle]
---

## Observed behavior

The HTML renderer places a `needs: review` entry in the To do lane.

## Evidence

Synthetic snapshot: the Markdown state and rendered lane disagree for the same
entry.

## Done when

The renderer consumes the shared lifecycle contract and uses the Review lane.
