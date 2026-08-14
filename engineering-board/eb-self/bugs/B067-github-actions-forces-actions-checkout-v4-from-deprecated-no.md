---
id: B067
type: bug
status: resolved
needs: validate
priority: P2
title: GitHub Actions forces actions/checkout v4 from deprecated Node.js 20 onto Node.js 24
affects: .github/workflows/
discovered: 2026-08-14
discovered_at: 2026-08-14T14:31:13Z
promoted_from: [mcp:_sessions/mcp-2026-08-14.md:723d97e238bf3d4f]
---

# GitHub Actions forces actions/checkout v4 from deprecated Node.js 20 onto Node.js 24

## Done when

- [x] Every tracked GitHub Actions checkout uses the reviewed v7 major and its
  Node.js 24 runtime; no `actions/checkout@v4` reference remains.
- [x] Existing workflow triggers, permissions, checkout inputs, and release
  publication gates remain unchanged.
- [x] A maintained test rejects an older checkout major and an unsafe fork
  checkout opt-out.
- [x] Pull-request and merged-main tests pass without the checkout Node.js 20
  deprecation annotation. No version, tag, checksum, or publication changes.

## Evidence

> Passing merged-main runs 31808165945 and 31808665101 emitted the annotation: Node.js 20 is deprecated; actions/checkout@v4 targets Node.js 20 and is being forced to run on Node.js 24.

## Comments

- **codex** 2026-08-14T14:57:02Z: Claimed after passing PR and merged-main runs repeatedly reported that actions/checkout@v4 targets deprecated Node.js 20 and is forced onto Node.js 24.
- **codex** 2026-08-14T15:03:34Z: Red/green workflow-action contract complete. All five checkout steps use v7, four workflow files parse, and the expanded 21-suite maintained validation passes. Live PR and merged-main annotation evidence remain pending.

## Resolution evidence

- All five checkout steps across four workflow files use `actions/checkout@v7`; no v4 reference or unsafe fork opt-out remains.
- The workflow-action contract passes, all workflow YAML parses, and the maintained suite passes 21 of 21 suites.
- Pull request #132 merged as `711ba4d`; PR runs 31812748391 and 31812770073 passed without annotations.
- Merged-main tests run 31812894176 and Pages run 31812894181 passed without annotations.
- Dated alignment evidence: `docs/evidence/2026-08-14-b067-checkout-node24.md`.
