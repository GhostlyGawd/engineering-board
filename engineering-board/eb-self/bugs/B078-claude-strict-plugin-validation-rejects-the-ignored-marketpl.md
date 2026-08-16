---
id: B078
type: bug
status: open
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

- [ ] `claude plugin validate --strict .` accepts the Claude marketplace manifest with no ignored-field warning.
- [ ] The Claude marketplace manifest contains only fields supported by Claude Code, while Codex-specific policy remains on a Codex-owned surface.
- [ ] Normal Claude and Codex plugin validation, packaging, and install checks still pass.

## Evidence

> claude plugin validate --strict . exits 1 because plugins[0].policy is unknown and ignored; normal validation passes with the same warning.

> Fresh 2026-08-15 control: normal validation exited 0 with one ignored-field warning. The otherwise identical --strict validation exited 1 because warnings are errors. B077 does not modify this Claude marketplace field.
