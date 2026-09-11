---
id: B017
type: bug
status: resolved
needs: validate
priority: P2
title: Live landing page dark theme fails automated contrast and keyboard scroll checks
affects: docs/index.html
discovered: 2026-09-11
discovered_at: 2026-09-11T02:15:27Z
promoted_from: [mcp:_sessions/mcp-2026-09-11.md:db1a4a79812a80f9]
parent: F013
---

# Live landing page dark theme fails automated contrast and keyboard scroll checks

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> F007 Chrome 153 at 390x844, axe-core 4.12.1: eyebrow and Install CTA contrast 3.24:1 against required body-text 4.5:1; inline trust links lack adequate distinction; three scrollable installation pre blocks not keyboard focusable. Retained 06-landing-a11y.json and 06-mobile-landing.png under docs/evidence/2026-09-10-refero-audit/. Automated findings need focused implementation verification; not a full accessibility audit.

## Acceptance and scope

Correct the recorded landing contrast, inline-link distinction and keyboard-scroll issues. Recheck both themes and mobile/desktop with focused keyboard tests and an automated scan. Separately review board main/content landmark omissions reported in 03-board-a11y.json. Audit evidence identifies problems; it does not prove implementation or full compliance.

## Comments

- **graphite-rollout-root** 2026-09-11T16:14:00Z: Correction implemented under F013/F014 rollout scope, PR178. Independent staged verification passed. B016: publication now freshly renders with absolute canonical GitHub link and reviewer clicked intended record. B017: shared accessible tokens/native controls and main landmark; site/board finalaxe no violations/incomplete. Waiting actual live publication before resolving.

## Rollout completion evidence

PR #178 merged to main f01f036e6e51c170ecfedf9882ee09a077df02a2. Both PR CI runs and main CI 34620835213 pass. Pages publication 34620835128 and Pages deployment 34620852678 succeed; gh-pages 5470ec7eed7040f9973253b02214db5998ce3ce5. Actual public website and board display Graphite/wordmark-only identity. Live B001 clicked through to canonical GitHub Markdown with metadata instead of Pages 404. Live site and board axe scans have zero violations/incomplete. Staged desktop/mobile, both themes, noJS, keyboard/copy/recovery and source paths independently passed. All 23 portable suites pass; final view/token/site follow-ups pass. Evidence retained under docs/evidence/2026-09-11-graphite-rollout, publication closeout branch; no certification/effect claim. Website, viewer source, README and brand rollout complete. Immutable plugin package remains 1.14.0 with changes in Unreleased for next explicit versioned release. No unrelated workspace edits or goal changes. No additional completed neighbor or H outcome; cost/time not measured.
