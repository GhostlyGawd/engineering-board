---
id: B001
type: bug
status: open
needs: tdd
priority: P1
title: Worker skips an entry that is eligible for review
affects: hooks/worker-routing
discovered: 2026-07-27
pattern: [duplicated-state-contract]
tags: [synthetic-demo, lifecycle]
---

## Observed behavior

The worker selection path treats an otherwise eligible `needs: review` entry as
unavailable.

## Evidence

Synthetic trace: the entry is open, unblocked, and unclaimed, but the worker
returns no work.

## Done when

The worker consumes one shared lifecycle contract and selects the entry.
