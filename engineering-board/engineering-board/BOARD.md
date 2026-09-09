# engineering-board — Board

Live index of open items. Resolved items move to ARCHIVE.md.

## Open

- B009 P1 | [Packaged MCP server reports 0.0.0 instead of its release version](bugs/B009-packaged-mcp-server-reports-0-0-0-instead-of-its-release-ver.md) (in_progress)
- F005 P2 | [Expose a read-only hypothesis-detail route from retrieved H records](features/F005-expose-a-read-only-hypothesis-detail-route-from-retrieved-h-.md) ⊘ B009 (blocked)
- O001 | [Independent workflow-pilot preflight exposed label leakage and evidence-retention mismatches before live launch](observations/O001-independent-workflow-pilot-preflight-exposed-label-leakage-a.md)
- O002 | [Hypotheses retrieved by board_context are not readable through board_get_entry in installed 1.13.5](observations/O002-hypotheses-retrieved-by-board-context-are-not-readable-throu.md)

## Conventions

- Bug/Feature lines: `- B### P# | [title](bugs/filename.md)` (append `⊘ Q###` when blocked)
- Question lines: `- Q### | [title](questions/filename.md)`
- Observation lines: `- O### | [title](observations/filename.md)`
- Learning lines: `- L### | [title](learnings/filename.md)` (v0.3.0)
- Order within each section: P0 → P1 → P2 → P3 → unranked
