---
id: F013
type: feature
status: resolved
needs: validate
priority: P2
title: Promote Graphite prototype into the public website with working example sources
affects: docs/index.html
discovered: 2026-09-11
discovered_at: 2026-09-11T15:51:43Z
promoted_from: [mcp:_sessions/mcp-2026-09-11.md:f05ef2c5eda46f9b]
parent: F012
---

# Promote Graphite prototype into the public website with working example sources

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> Bounded website builder assignment in Graphite rollout: docs landing, example sources, CSS/JS, guides and publication staging workflow; preserve production metadata and accurate client setup, remove prototype framing, retain synthetic labels. Fix public source routes B016 and website accessibility B017. Excludes brand assets/tokens and viewer implementation owned separately.

## Rollout assignment and acceptance

Owner approved rollout; claim graphite-rollout-web, project engineering-board. Worktrees based on latest upstream02c019e plus approved prototype commits, base4c21aa4. Website builder owns docs/index.html, docs/site.css, docs/site.js, docs/guide.html, docs/example/**, docs/llms.txt, scripts/build-site.py and tests/site/ (existing manifest integration by lead), .github/workflows/pages.yml. New shared brand tokens/font/assets supplied by lead. Public B016 links must resolve from freshly generated board with --link-base canonical GitHub root; retained synthetic example served locally separate from real board. Accurate production metadata/install docs, no prototype framing. Browser and staged-publication checks. One accountable owner per entry. Review criterion: selected wordmark/A-layout/Graphite finish faithfully applied with real content; dark/light1448 and390, keyboard, noJS, source links, zero unhandled console errors; full tests and independent evidence before delivery. Release notes Unreleased; immutable plugin release is separate versioned publication per release policy.

## Rollout completion evidence

PR #178 merged to main f01f036e6e51c170ecfedf9882ee09a077df02a2. Both PR CI runs and main CI 34620835213 pass. Pages publication 34620835128 and Pages deployment 34620852678 succeed; gh-pages 5470ec7eed7040f9973253b02214db5998ce3ce5. Actual public website and board display Graphite/wordmark-only identity. Live B001 clicked through to canonical GitHub Markdown with metadata instead of Pages 404. Live site and board axe scans have zero violations/incomplete. Staged desktop/mobile, both themes, noJS, keyboard/copy/recovery and source paths independently passed. All 23 portable suites pass; final view/token/site follow-ups pass. Evidence retained under docs/evidence/2026-09-11-graphite-rollout, publication closeout branch; no certification/effect claim. Website, viewer source, README and brand rollout complete. Immutable plugin package remains 1.14.0 with changes in Unreleased for next explicit versioned release. No unrelated workspace edits or goal changes. No additional completed neighbor or H outcome; cost/time not measured.
