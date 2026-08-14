---
id: F004
type: feature
title: Package Engineering Board as an installable Codex plugin
discovered: 2026-08-14
status: resolved
priority: P2
affects: .codex-plugin/plugin.json
needs: tdd
---

## Done when

- [x] Codex installs five valid Engineering Board skills.
- [x] The installed plugin starts only the 19-tool Engineering Board MCP server.
- [x] A Windows-hosted installed-plugin lifecycle verifies claim, resolution archive, and release.

## Verification evidence

The official plugin validator and all five skill validators pass. Codex installed version 1.12.0 from the local marketplace. The cached package contains five skills and one isolated MCP server. The Windows launcher negotiated protocol 2025-06-18, listed 19 tools, created and claimed B001 in a disposable board, appended its resolution archive, and released the claim.
