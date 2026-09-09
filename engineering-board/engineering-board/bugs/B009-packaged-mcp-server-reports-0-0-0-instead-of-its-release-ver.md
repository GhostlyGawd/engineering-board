---
id: B009
type: bug
status: in_progress
needs: tdd
priority: P1
title: Packaged MCP server reports 0.0.0 instead of its release version
affects: mcp-server/engineering_board_mcp.py
discovered: 2026-09-09
discovered_at: 2026-09-09T16:06:21Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:e4d7b284c18c2954]
parent: F005
---

# Packaged MCP server reports 0.0.0 instead of its release version

## Done when

- [ ] Source/plugin manifest precedence remains intact, and owned bundle/distribution metadata supplies the runtime version when that manifest is absent.
- [ ] Actual unpacked bundle and installed wheel handshakes report their declared release version; missing, invalid or unrelated metadata has a tested conservative fallback.
- [ ] Independent review, refreshed reproducible bundle checksum, full tests and strict release validation pass before publication.

## Evidence

> F005 release preflight unpacked prepared1.14.0 MCP bundle SHA d506f1348a6248f3a9cf6583468122e49e0fb07c4e64328d0b80fec68be9a782. Actual stdio initialize returns serverInfo.version='0.0.0' despite bundle manifest.version='1.14.0'. Both hypothesis read cases pass unchanged. _plugin_version reads only PLUGIN_ROOT/.claude-plugin/plugin.json, absent in standalone bundle; PyPI distribution needs metadata fallback too. Retained docs/evidence/f005-hypothesis-details-2026-09-09/bundle-smoke.json. Publication held before tag creation; preserve manifest-first source behavior and add package identity fallbacks/tests.

## Accepted scope and verification

Release identity blocker. Keep authoritative source/installed-plugin manifest precedence; use owned bundle manifest or installed Python distribution metadata when the plugin manifest is absent, with conservative unknown-version fallback. Verify actual standalone-bundle and installed-wheel initialize versions against their manifest/metadata, plus source precedence, invalid/missing metadata and legacy reader invariance. Lead claim release-runtime-identity-20260909 owns the bounded follow-up builder assignment; no version target change or publication until reviewed and refreshed checksum matches.

## Comments

- **lead-hypothesis-details-20260909** 2026-09-09T16:12:38Z: Independent review at39aa5f6 reproduced an uncaught Path.resolve RuntimeError for a self-referential symlink row in owning distribution RECORD on Python3.9.6. Builder correcting conservative fallback and adding real/forced resolution-failure regression, testing3.9 and3.14. Actual installed-wheel bytes match reviewed source and two H read workflows pass version1.14.0; deliberately wrong expected-version exits1 with retained receipt. Publication remains held.
