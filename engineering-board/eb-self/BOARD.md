# eb-self — Board

Live index of open items. Resolved items move to ARCHIVE.md.

## Open

### Bugs
- B006 P2 | [B006-advancing-one-entry-through-tdd-review-validate-](bugs/B006-advancing-one-entry-through-tdd-review-validate-.md) (mitigated: 1.3.0 session-mode banner + README "one session, one mode"; full auto-rotation is the Conductor, RFC 0001)
- B014 P2 | [B014-two-implementations-of-scratch-live-promotion-wi](bugs/B014-two-implementations-of-scratch-live-promotion-wi.md)
- B016 P3 | [B016-version-sprawl-across-surfaces-no-authoritative-](bugs/B016-version-sprawl-across-surfaces-no-authoritative-.md) (partial — required-permissions.json done)
- B020 P3 | [B020-board-migrate-is-two-unrelated-operations-under-](bugs/B020-board-migrate-is-two-unrelated-operations-under-.md)
- B021 P3 | [B021-code-reviewer-name-collides-with-code-review-and](bugs/B021-code-reviewer-name-collides-with-code-review-and.md)
- B022 P3 | [B022-nothingtotest--nothingtoreview-still-advance-the](bugs/B022-nothingtotest--nothingtoreview-still-advance-the.md)
- B057 P3 | [B057-count-scratch-findings-undercounts-multi-find](bugs/B057-count-scratch-findings-undercounts-multi-find.md)

### Features
- F003 P3 | [F003-surface-matched-learnings-at-the-moment-of-need-](features/F003-surface-matched-learnings-at-the-moment-of-need-.md) (partial — 1.4.0 viewer Learnings panel done + SessionStart already surfaces matched learnings; session-end PM-summary surfacing deferred, PR-body injection kill-gated to the Conductor)

### Questions
- Q001 | [Q001-does-driving-one-board-from-claude-code--claude-](questions/Q001-does-driving-one-board-from-claude-code--claude-.md)

### Learnings
- L001 | [Ship every deterministic guard with a test that drives its real fixtures and call-sites](learnings/L001-guards-need-tests-that-drive-real-callsites.md)
- L002 | [Board health invariants must respect the open-vs-resolved entry lifecycle](learnings/L002-invariants-must-respect-the-entry-lifecycle.md)
- L003 | [The newest surface carries the most risk — red-team it hardest](learnings/L003-newest-surfaces-carry-the-most-risk.md)
- L004 | [A denylist heuristic is never done — assume every pattern has an adjacent bypass](learnings/L004-a-denylist-is-never-done.md)
- L005 | [Fix an input-handling class across every site at once, not one site per cycle](learnings/L005-fix-the-class-across-every-site.md)

## Conventions

- Bug/Feature lines: `- B### P# | [title](bugs/filename.md)` (append `⊘ Q###` when blocked)
- Question lines: `- Q### | [title](questions/filename.md)`
- Observation lines: `- O### | [title](observations/filename.md)`
- Learning lines: `- L### | [title](learnings/filename.md)` (v0.3.0)
- Order within each section: P0 → P1 → P2 → P3 → unranked
