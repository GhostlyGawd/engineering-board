---
id: B071
type: bug
status: open
needs: tdd
priority: P2
title: Codex hook adapters fail to derive the repository root without CLAUDE_PROJECT_DIR
affects: hooks/scripts/board-paths.sh
discovered: 2026-08-15
discovered_at: 2026-08-15T02:41:35Z
promoted_from: [mcp:_sessions/mcp-2026-08-15.md:82e8ec11f639e468]
---

# Codex hook adapters fail to derive the repository root without CLAUDE_PROJECT_DIR

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> Fresh Codex 0.145.0 SessionStart in the repository reported Engineering board not initialized. A direct no-env run reproduced that output, while setting CLAUDE_PROJECT_DIR to the same PWD found eb-self; board-stop-gate.sh exits 1 with CLAUDE_PROJECT_DIR unbound.
