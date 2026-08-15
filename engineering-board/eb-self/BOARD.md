# eb-self — Board

Live index of open items. Resolved items move to ARCHIVE.md.

## Open

- B071 P2 | [Codex auto-loads Claude hook adapters that require CLAUDE_PROJECT_DIR](bugs/B071-codex-hook-adapters-fail-to-derive-the-repository-root-witho.md) (in_progress)
- B072 P2 | [Codex skips the prompt Stop hook and reports failure after every turn](bugs/B072-codex-skips-the-prompt-stop-hook-and-reports-failure-after-e.md) (in_progress)
- B073 P2 | [SessionStart counts BOARD convention examples as open entries](bugs/B073-sessionstart-counts-board-convention-examples-as-open-entrie.md) (in_progress)
- B074 P2 | [Self-hosted claim locks dirty the repository because runtime board paths are not ignored](bugs/B074-self-hosted-claim-locks-dirty-the-repository-because-runtime.md) (in_progress)
- B075 P2 | [Authoritative current-behavior table describes superseded graph context and outcome limitations](bugs/B075-authoritative-current-behavior-table-describes-superseded-gr.md) (in_progress)
- B076 P2 | [Dated root audit snapshots can be mistaken for current product truth](bugs/B076-dated-root-audit-snapshots-can-be-mistaken-for-current-produ.md) (in_progress)
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
