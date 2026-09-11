---
id: F014
type: feature
status: resolved
needs: validate
priority: P2
title: Apply Graphite wordmark styling to the real generated board viewer
affects: hooks/scripts/board-view.sh
discovered: 2026-09-11
discovered_at: 2026-09-11T15:51:43Z
promoted_from: [mcp:_sessions/mcp-2026-09-11.md:a4346e42132a9458]
parent: F012
---

# Apply Graphite wordmark styling to the real generated board viewer

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> Bounded viewer builder assignment in Graphite rollout: real findings/cluster/hypothesis/Kanban viewer styling, readable source navigation and current scope labels; use shared brand tokens/font, add accessible theme/landmarks as appropriate, preserve deterministic single-file offline/noJS rendering, escaping, filters, claims and epistemic behavior; focused tests. No website/publication/brand asset edits.

## Rollout assignment and acceptance

Owner approved rollout; claim graphite-rollout-viewer, project engineering-board. Worktrees based on latest upstream02c019e plus approved prototype commits, base4c21aa4. Viewer builder owns hooks/scripts/board-view.sh, commands/board-view.md, tests/view/automated.sh, tests/token-coherence.sh if adaptation needed. Use shared brand/tokens.css and brand/fonts/Manrope.woff2 (lead supplies) with inline base64 font for standalone offline HTML. Preserve sort/filter/claims/data escaping and noJS, hypotheses state and deterministic behavior. Improve typography/readable metadata, wordmark only, native theme/landmarks; no production illustration or brand asset edits. Test hostile input and noJS. One accountable owner per entry. Review criterion: selected wordmark/A-layout/Graphite finish faithfully applied with real content; dark/light1448 and390, keyboard, noJS, source links, zero unhandled console errors; full tests and independent evidence before delivery. Release notes Unreleased; immutable plugin release is separate versioned publication per release policy.

## Rollout completion evidence

PR #178 merged to main f01f036e6e51c170ecfedf9882ee09a077df02a2. Both PR CI runs and main CI 34620835213 pass. Pages publication 34620835128 and Pages deployment 34620852678 succeed; gh-pages 5470ec7eed7040f9973253b02214db5998ce3ce5. Actual public website and board display Graphite/wordmark-only identity. Live B001 clicked through to canonical GitHub Markdown with metadata instead of Pages 404. Live site and board axe scans have zero violations/incomplete. Staged desktop/mobile, both themes, noJS, keyboard/copy/recovery and source paths independently passed. All 23 portable suites pass; final view/token/site follow-ups pass. Evidence retained under docs/evidence/2026-09-11-graphite-rollout, publication closeout branch; no certification/effect claim. Website, viewer source, README and brand rollout complete. Immutable plugin package remains 1.14.0 with changes in Unreleased for next explicit versioned release. No unrelated workspace edits or goal changes. No additional completed neighbor or H outcome; cost/time not measured.
