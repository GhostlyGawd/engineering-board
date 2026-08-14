---
id: B066
type: bug
status: resolved
needs: validate
priority: P2
title: board_context rejects the safe repository-relative cwd '.'
affects: mcp-server/engineering_board_core.py
discovered: 2026-08-14
discovered_at: 2026-08-14T12:22:15Z
promoted_from: [mcp:_sessions/mcp-2026-08-14.md:2]
---

# board_context rejects the safe repository-relative cwd '.'

## Done when

- [x] `board_context` accepts `cwd: "."` as the repository root.
- [x] Relative and absolute repository-root inputs produce the same context.
- [x] The exception applies only to `cwd`; `files: ["."]` remains invalid.
- [x] Shared-core, MCP-adapter, and real STDIO regression checks pass.

## Evidence

> A configured MCP dogfood call with cwd='.' returned 'cwd contains an unsafe path'. The same request with the absolute repository root succeeded. A focused regression reproduces the mismatch.

## Comments

- **codex** 2026-08-14T12:24:20Z: Validated in the isolated worktree by the focused Milestone D matrix and the complete 19-suite repository run. The configured long-lived MCP process still requires reload before a live dot-cwd probe can use the new module.
