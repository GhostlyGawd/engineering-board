---
id: B074
type: bug
status: resolved
needs: validate
priority: P2
title: Self-hosted claim locks dirty the repository because runtime board paths are not ignored
affects: .gitignore
discovered: 2026-08-15
discovered_at: 2026-08-15T03:45:44Z
promoted_from: [mcp:_sessions/mcp-2026-08-15.md:dec01777b4997312]
---

# Self-hosted claim locks dirty the repository because runtime board paths are not ignored

## Done when

- [ ] This repository ignores the documented `_sessions/`, `_claims/`, `_migrate-snapshot/`, and hidden `.engineering-board/` runtime paths.
- [ ] Canonical `engineering-board/` entries, indexes, graphs, hypotheses, Learnings, and consolidation receipts remain tracked by default.
- [ ] Acquiring a claim and capturing a scratch finding no longer adds runtime paths to `git status`.
- [ ] A focused repository-hygiene check and the complete required suite pass.

## Evidence

> After board_claim acquired B071 through B073, git status reported ?? engineering-board/eb-self/_claims/. git check-ignore returned no match, while commands/board-init.md recommends engineering-board/*/_claims/ as ephemeral runtime state.

## Comments

- **goal-hooks-20260815** 2026-08-15T03:46:38Z: Claimed after the released MCP workflow reproduced unignored self-hosted runtime state; the printed board-init stanza is the expected contract.
- **goal-hooks-20260815** 2026-08-15T04:05:39Z: Focused checks and the settled complete suite pass. Advanced from TDD to independent review; merged-main and installed-artifact gates remain open.
- **goal-hooks-20260815** 2026-08-15T04:07:31Z: Independent read-only review found no remaining release blocker after patch and minor release-path coverage. Advanced to validation; installed and merged-main gates remain open.

## Release validation — 2026-08-15

Claims plus the B077 capture and promotion produced no visible claim, live session, migration snapshot, or derived-cache path in git status; canonical state remained visible. See docs/evidence/2026-08-15-v1.13.2-release-and-installed-validation.md.
