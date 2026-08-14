# B069 newest-first archive evidence

- Date: 2026-08-14
- Repository: `GhostlyGawd/engineering-board`
- Base commit: `1c77039aa0e5d993b243062718b17bfbc877f031`
- Board entry: `B069`
- Completion state: implementation validation
- Evidence destination: this file
- External gates: implementation pull request merge, passing merged-main
  continuous integration, and a separate resolved-entry closeout
- Terminal action: resolve B069 after the implementation reaches `main`

## Decision

Insert a newly resolved entry immediately after the existing archive preamble
and before the first canonical archive row. Preserve every existing byte of the
preamble and every older row in its current relative order. Do not reorder the
historical archive because those rows are durable evidence. Keep repeated
resolved updates idempotent through the existing status-transition guard.

This change does not prepare a release or change a product version. Installed
copies remain unchanged until a later owner-authorized release includes the
Unreleased fix.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| A newly resolved entry is the first canonical archive row. | Required by `ARCHIVE_SKELETON` and B069. | `archive_with_newest_row` inserts before the first canonical row. | The MCP lifecycle resolves O001 above two older rows, then resolves O002 above O001. | Resolver skill, board manager, MCP README and schema, public LLM summary, architecture, auto-resolve protocol, and changelog state newest-first insertion. | Worker validation passes; pull-request and merged-main evidence are pending. |
| Existing archive evidence is not rewritten. | Required evidence-preservation boundary. | The helper retains the preamble byte-for-byte and does not sort or rewrite older rows. | The fixture asserts the unchanged preamble and the unchanged B900/B901 suffix after both resolutions. | Resolver instructions require preservation of the preamble and older-row relative order. | Worker validation passes; pull-request and merged-main evidence are pending. |
| A repeated resolved update does not add another archive row. | Required lifecycle idempotency. | Archive insertion runs only on a transition from a non-resolved state to `resolved`. | The fixture repeats the O001 resolved update and asserts one O001 row. | The Unreleased note identifies repeat-update idempotency. | Worker validation passes; pull-request and merged-main evidence are pending. |
| All supported resolver paths use the same archive rule. | Required by L005 and the documentation-alignment invariant. | MCP is the only executable archive writer found in the sibling-writer sweep. | MCP real-fixture coverage drives observation resolution, which uses the shared transition path for each entry type. | Bug, feature, question, observation, cascade, API, and architecture prose use the same rule. | Worker validation passes; pull-request and merged-main evidence are pending. |

## Drift classification

- Required conflict, resolved in the worker: `ARCHIVE_SKELETON` requires newest
  entries at the top, but `board_update_entry` appended new rows at the bottom.
- Documentation drift, resolved in the worker: the resolver skill, board
  manager, auto-resolve protocol, MCP README, public LLM summary, live schema,
  and architecture used append language.
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
- Green phase: the focused MCP suite reports 180 passing checks. It covers an
  archive with no prior rows, two ordered resolutions above two older rows,
  preservation of the preamble and older-row suffix, and repeat-update
  idempotency.
- Sibling-writer sweep: MCP `board_update_entry` is the only executable archive
  writer. The board manager, manual resolver, and auto-resolve paths delegate
  the same lifecycle but had stale append wording, which this change aligns.
- Maintained repository suite: 21 of 21 suites pass with exit code 0.
- Implementation pull request, merge commit, and merged-main run: pending.
- Closeout pull request and merged-main run: pending.

Passing checks establish only their named invariants. They do not establish
perfect semantic correctness or formal controlled-English compliance.
