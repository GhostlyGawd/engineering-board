---
id: B067
type: bug
status: open
needs: tdd
priority: P2
title: GitHub Actions forces actions/checkout v4 from deprecated Node.js 20 onto Node.js 24
affects: .github/workflows/test.yml
discovered: 2026-08-14
discovered_at: 2026-08-14T14:31:13Z
promoted_from: [mcp:_sessions/mcp-2026-08-14.md:723d97e238bf3d4f]
---

# GitHub Actions forces actions/checkout v4 from deprecated Node.js 20 onto Node.js 24

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> Passing merged-main runs 31808165945 and 31808665101 emitted the annotation: Node.js 20 is deprecated; actions/checkout@v4 targets Node.js 20 and is being forced to run on Node.js 24.
