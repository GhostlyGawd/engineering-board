---
id: B065
type: bug
status: resolved
needs: validate
priority: P2
title: Promotion provenance collides when a daily MCP scratch file is recreated
affects: mcp-server/engineering_board_core.py
discovered: 2026-08-14
discovered_at: 2026-08-14T12:22:15Z
promoted_from: [mcp:_sessions/mcp-2026-08-14.md:1]
---

# Promotion provenance collides when a daily MCP scratch file is recreated

## Done when

- [x] Recreating a daily MCP scratch file cannot reuse the durable identity of
  an earlier promoted finding.
- [x] Promotion distinguishes unrelated content even when the source path and
  source index are the same.
- [x] A regression test covers deletion, recreation, preview, and apply.

## Evidence

> A recreated _sessions/mcp-2026-08-14.md finding at source index 0 previewed as already_applied to unrelated resolved entry B063 because B063 retained the same path-and-index provenance from an earlier file lifecycle.

## Resolution evidence

Content-derived provenance and the recreated-daily-file regression pass in the Milestone B pattern pipeline.
