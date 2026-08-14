---
id: B064
type: bug
title: MCP bundle builder reports a pin that it does not update
discovered: 2026-08-14
status: resolved
priority: P2
affects: mcp-server/build-mcpb.sh
needs: validate
pattern: [invariant-mismatch, dogfooding-pain]
---

## Done when

- [x] The builder compares the rebuilt checksum with the published pin.
- [x] The builder reports whether the checksum matches or requires a later release.
- [x] CI permits a mismatch only when Unreleased contains a release note.
- [x] Release preparation still requires an exact rebuilt checksum.
- [x] The complete repository test suite passes.

## Comments

- **codex** 2026-08-14T04:49:11Z: Dogfood reproduction confirmed. The builder produced a new checksum, then falsely said that server.json already contained it. Repository release policy requires the current published pin to remain unchanged until explicit release preparation.
- **codex** 2026-08-14T04:53:14Z: Verified with the builder mismatch message, the documented-Unreleased checksum gate, release-preparation tests, and the complete 19-suite repository run.
