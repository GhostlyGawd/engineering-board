---
id: B072
type: bug
status: resolved
needs: validate
priority: P2
title: Codex skips the prompt Stop hook and reports failure after every turn
affects: .codex-plugin/plugin.json
discovered: 2026-08-15
discovered_at: 2026-08-15T02:41:35Z
promoted_from: [mcp:_sessions/mcp-2026-08-15.md:96759e36ef6a9c4a]
---

# Codex skips the prompt Stop hook and reports failure after every turn

## Done when

- [ ] Codex loads an explicit Codex-specific hook source that contains no unsupported prompt hooks.
- [ ] A fresh installed Codex turn prints no unsupported-prompt warning and no Stop-hook failure.
- [ ] Claude continues to load `hooks/hooks.json`, including its prompt Stop workflow.
- [ ] Documentation states the host boundary without claiming passive Codex hook capture.

## Evidence

> Fresh Codex 0.145.0 printed prompt hooks are not supported yet for hooks.json, then printed Stop hook failed with code 1 after each response, so passive capture cannot complete through the shipped prompt procedure.

## Comments

- **goal-hooks-20260815** 2026-08-15T03:40:12Z: Claimed with B071 because both reproduce from Codex auto-discovering the Claude hook manifest; unsupported prompt hooks remain the negative control.
- **goal-hooks-20260815** 2026-08-15T04:05:39Z: Focused checks and the settled complete suite pass. Advanced from TDD to independent review; merged-main and installed-artifact gates remain open.
- **goal-hooks-20260815** 2026-08-15T04:07:31Z: Independent read-only review found no remaining release blocker after patch and minor release-path coverage. Advanced to validation; installed and merged-main gates remain open.

## Release validation — 2026-08-15

Installed v1.13.2 selected the empty Codex hook source. A fresh Codex 0.145.0 process produced no prompt Stop warning or Stop failure. See docs/evidence/2026-08-15-v1.13.2-release-and-installed-validation.md.
