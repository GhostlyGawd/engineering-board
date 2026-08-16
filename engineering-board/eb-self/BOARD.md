# eb-self — Board

Live index of open items. Resolved items move to ARCHIVE.md.

## Open

- Q002 | [Does current D.1 version 4 context change cross-incident diagnosis?](questions/Q002-does-current-d-1-version-4-context-change-cross-incident-dia.md)
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
