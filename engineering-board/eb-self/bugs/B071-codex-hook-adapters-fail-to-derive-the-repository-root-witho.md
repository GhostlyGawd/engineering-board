---
id: B071
type: bug
status: resolved
needs: validate
priority: P2
title: Codex auto-loads Claude hook adapters that require CLAUDE_PROJECT_DIR
affects: .codex-plugin/plugin.json
discovered: 2026-08-15
discovered_at: 2026-08-15T02:41:35Z
promoted_from: [mcp:_sessions/mcp-2026-08-15.md:82e8ec11f639e468]
---

# Codex auto-loads Claude hook adapters that require CLAUDE_PROJECT_DIR

## Done when

- [ ] The Codex plugin manifest selects a Codex-specific hook source instead of auto-discovering the Claude hook manifest.
- [ ] A fresh installed Codex session does not run the Claude SessionStart or Stop adapters and reports no hook warning or failure.
- [ ] The installed Codex plugin still exposes all documented skills and MCP tools.
- [ ] The Claude hook test suite remains green.

## Evidence

> Fresh Codex 0.145.0 SessionStart in the repository reported Engineering board not initialized. A direct no-env run reproduced that output, while setting CLAUDE_PROJECT_DIR to the same PWD found eb-self; board-stop-gate.sh exits 1 with CLAUDE_PROJECT_DIR unbound.

## Scope

The defect is Codex loading adapters whose host contract supplies
`CLAUDE_PROJECT_DIR`. Direct manual execution of those Claude adapters without
their host environment remains outside the Codex product contract. This
checkpoint enforces the host boundary; it does not add a second root-resolution
contract to the Claude scripts.

## Comments

- **goal-hooks-20260815** 2026-08-15T03:40:12Z: Claimed for the explicit Codex hook-boundary checkpoint; completion criteria now require fresh installed-host evidence.
- **goal-hooks-20260815** 2026-08-15T04:05:39Z: Focused checks and the settled complete suite pass. Advanced from TDD to independent review; merged-main and installed-artifact gates remain open.
- **goal-hooks-20260815** 2026-08-15T04:07:31Z: Independent read-only review found no remaining release blocker after patch and minor release-path coverage. Advanced to validation; installed and merged-main gates remain open.

## Release validation — 2026-08-15

Installed v1.13.2 selected the empty Codex hook source. A fresh Codex 0.145.0 process loaded Engineering Board without the prior Claude-hook root error. See docs/evidence/2026-08-15-v1.13.2-release-and-installed-validation.md.
