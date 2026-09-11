---
id: B016
type: bug
status: resolved
needs: validate
priority: P1
title: Public board entry link leads to GitHub Pages 404
affects: hooks/scripts/board-view.sh
discovered: 2026-09-11
discovered_at: 2026-09-11T02:15:27Z
promoted_from: [mcp:_sessions/mcp-2026-09-11.md:a62f57591d99a359]
parent: F013
---

# Public board entry link leads to GitHub Pages 404

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> Audit F007: live landing → Live board → search B001 → click B001 navigates to https://ghostlygawd.github.io/engineering-board/bugs/B001-sessionstart-on2-blockedby-loop-exceeds-10s-time.md and shows 404 File not found. Retained screenshot and DOM: docs/evidence/2026-09-10-refero-audit/05-entry.png and 05-entry.txt. Observed deployed behavior; cause not yet established.

## Acceptance and scope

Reproduce the deployed B001 evidence link failure, establish the responsible generation/publication path, and verify hosted entry links reach their canonical evidence rather than 404. Preserve offline rendering. Audit reproduction is not a fix. No implementation performed in F007.

## Comments

- **graphite-rollout-root** 2026-09-11T16:14:00Z: Correction implemented under F013/F014 rollout scope, PR178. Independent staged verification passed. B016: publication now freshly renders with absolute canonical GitHub link and reviewer clicked intended record. B017: shared accessible tokens/native controls and main landmark; site/board finalaxe no violations/incomplete. Waiting actual live publication before resolving.

## Rollout completion evidence

PR #178 merged to main f01f036e6e51c170ecfedf9882ee09a077df02a2. Both PR CI runs and main CI 34620835213 pass. Pages publication 34620835128 and Pages deployment 34620852678 succeed; gh-pages 5470ec7eed7040f9973253b02214db5998ce3ce5. Actual public website and board display Graphite/wordmark-only identity. Live B001 clicked through to canonical GitHub Markdown with metadata instead of Pages 404. Live site and board axe scans have zero violations/incomplete. Staged desktop/mobile, both themes, noJS, keyboard/copy/recovery and source paths independently passed. All 23 portable suites pass; final view/token/site follow-ups pass. Evidence retained under docs/evidence/2026-09-11-graphite-rollout, publication closeout branch; no certification/effect claim. Website, viewer source, README and brand rollout complete. Immutable plugin package remains 1.14.0 with changes in Unreleased for next explicit versioned release. No unrelated workspace edits or goal changes. No additional completed neighbor or H outcome; cost/time not measured.
