---
id: O003
type: observation
title: Wheel build emits deprecation warnings for legacy license metadata
affects: mcp-server/pyproject.toml
discovered: 2026-09-09
discovered_at: 2026-09-09T16:19:06Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:05b81971de3e28ea]
---

# Wheel build emits deprecation warnings for legacy license metadata

## Evidence

> B009/F005 prepublication wheel build with uv succeeds, but setuptools warns that project.license as a TOML table and License classifiers are deprecated (warning names2027-Feb-18 transition). Existing metadata predates this feature; no build failure or strict Claude warning. Track a bounded metadata-maintenance follow-up rather than changing release scope again. Python wheel and both H detail cases pass; warning retained in release-validation narrative.
