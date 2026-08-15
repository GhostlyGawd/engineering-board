---
id: B070
type: bug
status: open
needs: tdd
priority: P2
title: Fresh Codex marketplace installs mutable main under a released version label
affects: .agents/plugins/marketplace.json
discovered: 2026-08-15
discovered_at: 2026-08-15T01:07:46Z
promoted_from: [mcp:_sessions/mcp-2026-08-15.md:8cce1e10d2b2d5ac]
---

# Fresh Codex marketplace installs mutable main under a released version label

## Done when

- [x] `.agents/plugins/marketplace.json` exposes exactly one Engineering Board entry whose version matches the authoritative manifest and whose root Git source pins `v<version>`.
- [x] Release preparation refuses drift in either marketplace source contract and advances the Codex marketplace version and ref together.
- [x] Focused version-coherence, Codex-plugin, release-preparation, and docs-coherence tests pass while the Claude marketplace retains `source: "./"`.
- [x] Release and install documentation describe the immutable Codex tag boundary without changing Claude installation behavior.
- [ ] A fresh post-release Codex reinstall records the new release tag target instead of mutable `main`.

## Evidence

> On 2026-08-14, codex plugin add reported version 1.13.0, but .codex-marketplace-install.json recorded revision 651766e420c903c70e65d45375318a7bd22de616 while tag v1.13.0 targets dcbd3ea10970d1437899607d77a2e4be1ec157af; the marketplace entry uses source ./ .
