---
id: B003
type: bug
status: open
needs: tdd
priority: P1
title: MCP ready-work output omits the same eligible lifecycle state
affects: mcp-server/ready-queue
discovered: 2026-07-27
pattern: [duplicated-state-contract]
tags: [synthetic-demo, lifecycle]
---

## Observed behavior

The MCP ready queue omits an open, unblocked entry in the same lifecycle state.

## Evidence

Synthetic response: the entry is present in the board but absent from ready
results.

## Done when

MCP consumes the shared lifecycle contract and returns the eligible entry.
