---
id: B072
type: bug
status: open
needs: tdd
priority: P2
title: Codex skips the prompt Stop hook and reports failure after every turn
affects: hooks/hooks.json
discovered: 2026-08-15
discovered_at: 2026-08-15T02:41:35Z
promoted_from: [mcp:_sessions/mcp-2026-08-15.md:96759e36ef6a9c4a]
---

# Codex skips the prompt Stop hook and reports failure after every turn

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> Fresh Codex 0.145.0 printed prompt hooks are not supported yet for hooks.json, then printed Stop hook failed with code 1 after each response, so passive capture cannot complete through the shipped prompt procedure.
