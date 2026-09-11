# Graphite public rollout: verified

PR: https://github.com/GhostlyGawd/engineering-board/pull/178
Merged: 2026-09-11T16:14:22Z
Main commit: f01f036e6e51c170ecfedf9882ee09a077df02a2
Published gh-pages commit: 5470ec7eed7040f9973253b02214db5998ce3ce5

- PR CI: both run-all checks passed (34620523231 and 34620573993).
- Main CI: https://github.com/GhostlyGawd/engineering-board/actions/runs/34620835213 — success.
- Staging/publication workflow: https://github.com/GhostlyGawd/engineering-board/actions/runs/34620835128 — success.
- GitHub Pages build/deployment: https://github.com/GhostlyGawd/engineering-board/actions/runs/34620852678 — success.

Opened https://ghostlygawd.github.io/engineering-board/ with local Chrome after
publication. The new wordmark, approved layout, Board navigation and synthetic
example are visible. Screenshot: live-site.png. The public board also shows the
Graphite identity and revised controls: live-board.png.

Clicked B001 on the live board. It opened the canonical GitHub Markdown record
with B001 metadata and evidence, rather than the former Pages404. URL:
https://github.com/GhostlyGawd/engineering-board/blob/main/engineering-board/eb-self/bugs/B001-sessionstart-on2-blockedby-loop-exceeds-10s-time.md
Evidence: live-b001-source.png and live-b001-source.txt.

Live desktop axe scans for both website and board returned zero violations and
zero incomplete checks (live-site-a11y.json, live-board-a11y.json). Earlier
staged desktop/mobile, both-theme and no-JavaScript matrix remains recorded in
validation.md and independent-review.md. These are bounded tests, not a claim of
universal accessibility compliance or improved agent diagnosis performance.

F012–F014 source/site rollout and B016–B017 corrections are complete. The
published immutable plugin remains1.14.0; viewer source changes are in main and
Unreleased for the next explicit versioned release. No release tags, package
versions, checksums or registry entries were changed.

The original user workspace was left intact with its pre-existing work; the
rollout and publication evidence were delivered through isolated branches.
