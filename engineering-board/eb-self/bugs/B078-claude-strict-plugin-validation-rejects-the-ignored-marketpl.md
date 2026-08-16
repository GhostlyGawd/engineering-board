---
id: B078
type: bug
status: in_progress
needs: tdd
priority: P2
title: Claude strict plugin validation rejects the ignored marketplace policy field
affects: .claude-plugin/marketplace.json
discovered: 2026-08-15
discovered_at: 2026-08-15T05:18:11Z
promoted_from: [mcp:_sessions/mcp-2026-08-15.md:b79036623cfe40f5]
---

# Claude strict plugin validation rejects the ignored marketplace policy field

## Done when

- [x] `claude plugin validate --strict .` accepts the Claude marketplace manifest with no ignored-field warning.
- [x] The Claude marketplace manifest contains only fields supported by Claude Code, while Codex-specific policy remains on a Codex-owned surface.
- [x] Normal Claude and Codex plugin validation, packaging, and install checks still pass.

## Evidence

> claude plugin validate --strict . exits 1 because plugins[0].policy is unknown and ignored; normal validation passes with the same warning.

> Fresh 2026-08-15 control: normal validation exited 0 with one ignored-field warning. The otherwise identical --strict validation exited 1 because warnings are errors. B077 does not modify this Claude marketplace field.

## Comments

- **goal-b078-20260816** 2026-08-16T01:00:47Z: Claimed after B077 closeout. Claude Code 2.1.200 normal validation passes with one ignored policy warning; strict validation fails on that warning. The approved bounded direction is a host-specific manifest contract with a failing test before the manifest edit.
- **goal-b078-20260816** 2026-08-16T01:04:00Z: Red tests rejected the copied Claude policy, then the one-field removal made normal and strict Claude validation pass without warnings. Codex policy assertions and release-preparation checks pass; full-suite and delivery gates remain open.
- **goal-b078-20260816** 2026-08-16T01:37:59Z: v1.13.4 published from exact merged main e151d3b7a3db. GitHub asset, MCP Registry, and PyPI records align; released Codex and Claude installs match prepared manifest hashes. Claude normal/strict validation and a fresh Codex board_status call pass. Keep open until this evidence merges and exact main revalidation passes.
