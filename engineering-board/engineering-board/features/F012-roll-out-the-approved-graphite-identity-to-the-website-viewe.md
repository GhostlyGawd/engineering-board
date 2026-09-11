---
id: F012
type: feature
status: resolved
needs: validate
priority: P2
title: Roll out the approved Graphite identity to the website viewer and brand assets
affects: brand/
discovered: 2026-09-11
discovered_at: 2026-09-11T15:51:43Z
promoted_from: [mcp:_sessions/mcp-2026-09-11.md:646a2d5696a63b8d]
---

# Roll out the approved Graphite identity to the website viewer and brand assets

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> Owner approved rollout after inspecting working prototype. Apply A layout + Graphite palette + wordmark-only identity to actual website, generated read-only board viewer, README and brand assets. Fix B016 hosted evidence links and B017 accessibility defects. Retain compatible offline/noJS/epistemic behavior, tests and independent review; deliver through PR and verify published website. No product-goal or evaluation changes.

## Rollout assignment and acceptance

Owner approved rollout; claim graphite-rollout-root, project engineering-board. Worktrees based on latest upstream02c019e plus approved prototype commits, base4c21aa4. Lead owns brand/**, BRAND.md, BRAND-COHERENCE.md, README.md, CHANGELOG.md, shared font/token artifacts, generated screenshots/social/favicon assets; integrate children, full tests, fresh independent review, normal PR and website publication verification. No unapproved evaluation changes or version edits. One accountable owner per entry. Review criterion: selected wordmark/A-layout/Graphite finish faithfully applied with real content; dark/light1448 and390, keyboard, noJS, source links, zero unhandled console errors; full tests and independent evidence before delivery. Release notes Unreleased; immutable plugin release is separate versioned publication per release policy.

## Comments

- **graphite-rollout-root** 2026-09-11T16:12:58Z: Rollout PR178 created https://github.com/GhostlyGawd/engineering-board/pull/178, branch codex/graphite-rollout, headc90cd51. Full23 suites green locally and independent review passes finalproductsourcef0353be. Site/board browser matrices, noJS, source links, sharedtokens and assetsverified. Waiting remote CI, then merge and livewebsiteverification under standing rollout authorization. Original dirtyworkspace preserved; implementation in /tmp/eb-graphite-rollout. Plugin immutable release not requested; currentrelease unchanged, runtime changes Unreleased.

## Rollout completion evidence

PR #178 merged to main f01f036e6e51c170ecfedf9882ee09a077df02a2. Both PR CI runs and main CI 34620835213 pass. Pages publication 34620835128 and Pages deployment 34620852678 succeed; gh-pages 5470ec7eed7040f9973253b02214db5998ce3ce5. Actual public website and board display Graphite/wordmark-only identity. Live B001 clicked through to canonical GitHub Markdown with metadata instead of Pages 404. Live site and board axe scans have zero violations/incomplete. Staged desktop/mobile, both themes, noJS, keyboard/copy/recovery and source paths independently passed. All 23 portable suites pass; final view/token/site follow-ups pass. Evidence retained under docs/evidence/2026-09-11-graphite-rollout, publication closeout branch; no certification/effect claim. Website, viewer source, README and brand rollout complete. Immutable plugin package remains 1.14.0 with changes in Unreleased for next explicit versioned release. No unrelated workspace edits or goal changes. No additional completed neighbor or H outcome; cost/time not measured.
