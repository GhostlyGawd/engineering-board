# F003 moment-of-need Learning validation

Date: 2026-08-14

## Scope

F003 adds one derived delivery surface. After PM curation, the Stop procedure
uses the consolidator's promoted entry ids to retrieve directly matched
Learnings. It appends eligible medium/high-confidence matches to the PM pass
summary. Canonical Learning Markdown remains the authority.

The viewer criterion was already implemented. This change preserves its
dedicated Learnings panel and adds no second viewer parser.

## Behavior and contract alignment

| Surface | Drift classification | Aligned behavior |
|---|---|---|
| Shared context core | Behavior and response-contract change | Contract version 3 exposes confidence. Ranking rule version 2 derives path context from selected entry `affects`, matches Learning `applies_to` by strict prefix, and accepts canonical or normalized raw patterns. |
| Context command adapter | Behavior change | `--learning-summary` returns at most 10 direct medium/high-confidence matches and emits no line when none qualify. |
| PM Stop procedure | Workflow change | The procedure queries after curation with validated promoted entry ids and appends a non-empty `Matched Learnings:` line. Retrieval failure is visible in the turn log and does not undo promotion. |
| Viewer | Reviewed, unaffected | The existing dedicated Learning-panel implementation and fixture remain authoritative. |
| MCP context tool | Additive response change | Each result now includes confidence when applicable. Selected entry ids also supply path context. |
| README, architecture, commands, product specification, MCP guide, site, and LLM index | Documentation change | Current behavior, contract versions, trust boundary, and PM delivery sequence are aligned. Historical version-2 evidence remains unchanged. |

## Security and noise controls

- The context engine validates Learning confidence and repository-relative
  `applies_to` paths before ranking.
- Direct scope matching requires a path-prefix relationship. A matching path
  segment in another branch is insufficient.
- Learning-summary mode requires a direct scope or pattern signal. Graph
  proximity and task terms alone cannot enter the summary.
- The adapter excludes low-confidence matches and bounds output to 10 records.
- Titles remain untrusted, one-line, bounded data. The adapter replaces title
  semicolons before it joins records.

## Targeted verification

The following repository fixtures passed from the Linux-native worktree:

- `tests/orchestration/milestone-d-context-outcome-intelligence.sh`: 16 checks.
  The fixture covers selected-entry path derivation, strict Learning scope,
  raw pattern matching, confidence output, low-confidence exclusion, and the
  real command adapter.
- `tests/orchestration/pm-loop.sh`: 20 checks. The fixture composes a PM summary
  from actual promoted ids and excludes a matching low-confidence decoy.
- `tests/modes/stop-hook-mode-routing.sh`: 102 checks. The procedure contract
  includes the summary invocation, promoted-id input, and append step.
- `tests/view/automated.sh`: 52 checks. The pre-existing Learnings panel remains
  byte-deterministic and renders canonical Learning state.

## Maintained-suite verification

`bash tests/run-all.sh` passed in the final implementation state:

- 21 of 21 maintained suites passed.
- The orchestration suite passed 25 of 25 sub-tests.
- The modes suite passed 6 of 6 sub-tests.
- The MCP server suite passed.
- The viewer suite passed 52 of 52 checks.
- The documentation-coherence, cross-compatibility, security, release-
  preparation, version-coherence, and Codex-plugin suites passed.

This evidence establishes deterministic repository behavior and contract
alignment. It does not establish production deployment, market value, or a
causal improvement in agent decisions.

## Real-board dogfood

The final adapter was also run against canonical `eb-self` entries:

- F003 produced no Learning line. No direct scope or pattern match exists, so
  the summary stayed quiet.
- Resolved MCP-server entry B069 produced one line with L003 and L005. Both
  records have high confidence and directly cover the entry's MCP-server path.

This check confirms current repository matching. It is workflow evidence, not
evidence that the surfaced Learnings caused a better engineering decision.
