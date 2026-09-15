---
id: F018
type: feature
status: open
needs: validate
priority: P2
title: Versioned release delivery for the triage ownership and intake capture fixes
affects: skills/
discovered: 2026-09-15
discovered_at: 2026-09-15T04:45:15Z
promoted_from: [mcp:_sessions/mcp-2026-09-15.md:c6deab14b40dc3cf]
blocked_by: [B010, B011]
---

# Versioned release delivery for the triage ownership and intake capture fixes

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> B010 and B011 source fixes are being delivered under the user request to work through both actionable bugs. docs/DEVELOPMENT.md requires pending installation/release delivery to remain an explicit linked entry after source closure. Current published plugin is v1.14.0; this source batch does not change an immutable release. Complete only when the next coordinated release includes both skill fixes and fresh installed workflow verification. No new evaluation criteria or product goals.

## Release acceptance

This is the separate installation-delivery follow-up for B010 and B011; their implementation acceptance is source delivery. Prepare the next coordinated Semantic Versioning release under docs/RELEASING.md, include both reviewed skills and all accepted Unreleased changes, pass required release gates, verify published artifacts and a fresh installed ownership/capture workflow, and retain release evidence. Do not infer agent behavioral efficacy from contract tests. Publication is outside the current source-fix batch.
