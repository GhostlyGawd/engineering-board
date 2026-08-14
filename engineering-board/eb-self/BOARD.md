# eb-self — Board

Live index of open items. Resolved items move to ARCHIVE.md.

## Open

- B065 P2 | [Promotion provenance collides when a daily MCP scratch file is recreated](bugs/B065-promotion-provenance-collides-when-a-daily-mcp-scratch-file-.md)
- B016 P3 | [Version sprawl across surfaces; no authoritative version signal](bugs/B016-version-sprawl-across-surfaces-no-authoritative-.md)
- B020 P3 | [board-migrate is two unrelated operations under one verb](bugs/B020-board-migrate-is-two-unrelated-operations-under-.md)
- B021 P3 | [code-reviewer name collides with /code-review and its tools contradict its read-only contract](bugs/B021-code-reviewer-name-collides-with-code-review-and.md)
- B022 P3 | [nothing_to_test / nothing_to_review still advance the entry forward](bugs/B022-nothingtotest--nothingtoreview-still-advance-the.md)
- F003 P3 | [Surface matched Learnings at the moment of need (session summary + viewer panel)](features/F003-surface-matched-learnings-at-the-moment-of-need-.md)
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
