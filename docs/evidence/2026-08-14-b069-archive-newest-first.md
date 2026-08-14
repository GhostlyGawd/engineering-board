# B069 newest-first archive evidence

- Date: 2026-08-14
- Repository: `GhostlyGawd/engineering-board`
- Base commit: `1c77039aa0e5d993b243062718b17bfbc877f031`
- Board entry: `B069`
- Completion state: closeout
- Implementation pull request: `#139`
- Implementation merge commit:
  `d3f4023a3648eb6c890b2ded11ab070243fe075e`
- Implementation merged-main runs: `31823479030` (`tests`, passed) and
  `31823478978` (`pages`, passed)
- Evidence destination: this file
- Follow-up base commit: `d3f4023a3648eb6c890b2ded11ab070243fe075e`
- Follow-up pull request: `#140`
- Follow-up merge commit: `f42516c552ed292531f400b8bf70b7d07f59a8f6`
- Follow-up merged-main run: `31824199079` (`tests`, passed)
- External gates: closeout pull request merge and passing closeout merged-main
  continuous integration
- Terminal action: resolve B069 in this closeout change, merge the closeout
  pull request, and verify its merged-main run

## Decision

Insert a newly resolved entry immediately after the existing archive preamble
and before the first recognized archive entry row. Support both the historical
priority-bearing rows and the current compact rows. Preserve every existing
byte of the preamble and every older row in its current relative order. Do not
reorder the historical archive because those rows are durable evidence. Keep
repeated resolved updates idempotent through the existing status-transition
guard.

This change does not prepare a release or change a product version. Installed
copies remain unchanged until a later owner-authorized release includes the
Unreleased fix.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| A newly resolved entry is the first archive entry row. | Required by `ARCHIVE_SKELETON` and B069. | `archive_with_newest_row` inserts before the first recognized current or historical row. | The MCP lifecycle resolves O001 above two priority-bearing historical rows, then resolves O002 above canonical O001. | Resolver skill, board manager, MCP README and schema, public LLM summary, architecture, auto-resolve protocol, and changelog state newest-first insertion. | Implementation, follow-up, and live closeout evidence pass; external closeout evidence is pending. |
| Existing archive evidence is not rewritten. | Required evidence-preservation boundary. | The helper retains the preamble byte-for-byte and does not sort or rewrite older rows. | The fixture asserts the unchanged preamble and the unchanged B900/B901 suffix after both resolutions. | Resolver instructions require preservation of the preamble and older-row relative order. | Implementation, follow-up, and live closeout evidence pass; external closeout evidence is pending. |
| A repeated resolved update does not add another archive row. | Required lifecycle idempotency. | Archive insertion runs only on a transition from a non-resolved state to `resolved`. | The fixture repeats the O001 resolved update and asserts one O001 row. | The Unreleased note identifies repeat-update idempotency. | Fixture and live closeout evidence pass. |
| All supported resolver paths use the same archive rule. | Required by L005 and the documentation-alignment invariant. | MCP is the only executable archive writer found in the sibling-writer sweep. | MCP real-fixture coverage drives observation resolution, which uses the shared transition path for each entry type. | Bug, feature, question, observation, cascade, API, and architecture prose use the same rule. | Implementation, follow-up, and live closeout evidence pass; external closeout evidence is pending. |

## Drift classification

- Required conflict, resolved in the worker: `ARCHIVE_SKELETON` requires newest
  entries at the top, but `board_update_entry` appended new rows at the bottom.
- Documentation drift, resolved in the worker: the resolver skill, board
  manager, auto-resolve protocol, MCP README, public LLM summary, live schema,
  and architecture used append language.
- Verification gap, found during closeout: the initial test used only current
  `- B### |` rows. The durable eb-self archive begins with historical
  `- B### P# |` rows, which the initial matcher did not recognize.
- Reviewed and unaffected: archive row fields, pattern rendering, resolution
  date generation, status-transition validation, and BOARD.md regeneration do
  not change.
- Reviewed and unaffected: existing archive rows remain in their recorded
  relative order. This change does not rewrite historical evidence.
- Reviewed and unaffected: graph generation, claim ownership, context ranking,
  hypothesis outcome handling, and scratch promotion do not write archive rows.
- Reviewed and unaffected: setup, security, privacy, provenance, and visual
  documentation do not define archive placement.
- Reviewed and unaffected: manifests, package versions, bundle checksums, tags,
  releases, registries, and deployment state do not change.
- Reviewed and unaffected: prior dated evidence remains historical and is not
  rewritten.

## Validation evidence

- Red phase: the focused MCP suite passed its first 100 checks, then failed the
  new archive-change assertion because the resolver still reported and used an
  append operation.
- Initial green phase: the focused MCP suite reported 180 passing checks, but
  its older-row fixture used only the current canonical format.
- Follow-up red phase: 103 checks passed before the live-format assertion
  failed. O001 appeared after two priority-bearing historical rows instead of
  immediately after the preamble.
- Follow-up green phase: the focused MCP suite reports 180 passing checks. The
  first resolution precedes priority-bearing historical rows, and the second
  resolution precedes the current compact row created by the first.
- Live archive dry-run: the merged-source helper inserted a candidate row
  before the actual first `- B057 P3 |` row. A byte-for-byte comparison
  confirmed that every existing archive byte remained unchanged.
- Sibling-writer sweep: MCP `board_update_entry` is the only executable archive
  writer. The board manager, manual resolver, and auto-resolve paths delegate
  the same lifecycle but had stale append wording, which this change aligns.
- Initial and follow-up maintained repository suites each report 21 of 21
  passing suites with exit code 0.
- Implementation pull-request checks: runs 31823346381 and 31823374743
  passed.
- Implementation pull request: #139 merged as `d3f4023`.
- Implementation merged-main tests run 31823479030 and Pages run 31823478978
  passed.
- Follow-up pull-request checks: runs 31824093894 and 31824112492 passed.
- Follow-up pull request: #140 merged as `f42516c`.
- Follow-up merged-main tests run 31824199079 passed. Pages did not trigger for
  the follow-up path set.
- Closeout source-MCP transition reported `inserted ARCHIVE.md` and resolved
  B069 through the merged `f42516c` implementation.
- Live closeout comparison: B069 is the first archive row. The complete
  committed pre-resolution archive follows it byte-for-byte unchanged.
- Live repeat comparison: a second resolved update left the archive
  byte-identical with one B069 row.
- Closeout cascade: B020 and F003 share neither B069's path nor a pattern, so
  there were no candidates. The hypothesis inventory is empty.
- The B069 claim was released. Board status reports no in-progress or blocked
  items, no dangling blockers, no unpromoted scratch, and ready items B020 and
  F003.
- Closeout worker checks: entry validation, board index, documentation
  coherence, archive position and uniqueness, BOARD.md omission, and diff
  checks pass.
- Closeout pull request and merged-main run: pending.

Passing checks establish only their named invariants. They do not establish
perfect semantic correctness or formal controlled-English compliance.
