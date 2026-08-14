# B020 board-migrate two-mode evidence

- Date: 2026-08-14
- Repository: `GhostlyGawd/engineering-board`
- Base commit: `231dd4587fb3fd7713ab0ae9e480645c6bf32091`
- Board entry: `B020`
- Completion state: closeout
- Implementation pull request: `#142`
- Implementation merge commit:
  `630ac9e148a10cc94c2261df76cbba1ecc526ffb`
- Implementation merged-main run: `31826065558` (`tests`, passed)
- Evidence destination: this file
- External gates: closeout pull request merge and passing closeout merged-main
  continuous integration
- Terminal action: resolve B020 in this closeout change, merge the closeout
  pull request, and verify its merged-main run

## Decision

Keep `/board-migrate` as a compatibility surface. Present data migration and
folder relocation as two independent named workflows. Select the workflow
before target resolution. Data flags use the per-board data script. The
relocation flag uses the repository-level relocation script once. Remove the
instruction that sends relocation around unrelated numbered steps.

This change preserves every existing flag and executable script. It does not
prepare a release, change a product version, move a board, run a migration, or
change deployment state.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| The command presents two independent named workflows. | Required by B020. | The command selects data migration or folder relocation before workflow steps. | The existing board-migrate orchestration test reads the real command file and requires both headings. | The command introduction and architecture summary use the same two workflow names. | Implementation, merged-main, and live closeout evidence pass; external closeout evidence is pending. |
| Data migration remains a per-board operation. | Required compatibility behavior. | Apply, rollback, and status resolve board rows and invoke `board-migrate.sh` per target. | Existing apply, rollback, state, and SHA tests remain unchanged. | The data workflow records current path resolution, output, and rollback safety. | Implementation, merged-main, and live closeout evidence pass; external closeout evidence is pending. |
| Folder relocation remains one repository-level operation. | Required relocation safety boundary. | Relocate invokes `board-relocate.sh` once, then rebuilds and reports. | The command contract rejects the old cross-workflow skip instruction; the existing relocation suite retains executable coverage. | The folder relocation workflow preserves snapshot, router rewrite, idempotency, and legacy-layout limits. | Implementation, merged-main, and live closeout evidence pass; external closeout evidence is pending. |
| Historical controlled-English evidence remains historical. | Required evidence boundary. | No formal review artifact or corpus manifest changes. | Repository validation determines whether live docs remain coherent; it does not re-certify language. | `docs/asd-ste100/CORPUS-MANIFEST.tsv` remains the pre-approval snapshot identified by its validation record. | Reviewed and unaffected. |

## Drift classification

- Required conflict, resolved in the worker: the command mixed a per-board data
  loop and repository relocation, then told relocation users to skip unrelated
  steps.
- Documentation drift, resolved in the worker: the architecture summary used a
  plus sign to combine the operations without explaining their execution
  boundary, and RFC 0002 still described B020 as only tracked.
- Reviewed and unaffected: `board-migrate.sh` and `board-relocate.sh` retain
  their existing executable behavior, arguments, snapshots, and idempotency.
- Reviewed and unaffected: `commands/board-init.md` correctly routes an
  optional folder move to `/board-migrate --relocate`.
- Reviewed and unaffected: `specs/board-relocation.md`, `state.md`, and `.omc/`
  plans are historical design and shipped-state records. Their statements
  remain accurate for the compatibility command.
- Reviewed and unaffected: permission patterns already grant the two separate
  scripts with separate rationales.
- Reviewed and unaffected: README command count and command list do not change.
- Reviewed and unaffected: security, privacy, provenance, visuals, manifests,
  package versions, bundle checksums, tags, releases, registries, and deployment
  state do not change.

## Validation evidence

- Red phase: the existing board-migrate test reported 8 behavior checks passed
  and 4 command-contract checks failed. The command had neither named workflow
  heading and still contained the cross-workflow skip instruction.
- Focused green phase: the board-migrate test reports 12 passing checks. Four
  checks drive the real command file, and eight preserve the executable data
  migration behavior.
- Documentation coherence passes with 21 commands, 5 skills, and 19 MCP tools.
- The orchestration matrix reports 25 of 25 passing sub-suites, including the
  separate relocation script suite.
- Maintained repository suite: 21 of 21 suites pass with exit code 0.
- Implementation pull-request checks: runs 31825953515 and 31825968319
  passed.
- Implementation pull request: #142 merged as `630ac9e`.
- Implementation merged-main tests run 31826065558 passed. Pages did not
  trigger for this path set.
- Closeout source-MCP transition reported `inserted ARCHIVE.md` and resolved
  B020 through the merged `630ac9e` implementation.
- Live closeout comparison: B020 is the first archive row. The complete
  committed pre-resolution archive follows it byte-for-byte unchanged.
- Live repeat comparison: a second resolved update left the archive
  byte-identical with one B020 row.
- Closeout cascade: F003 shares neither B020's path nor its
  `surface-overload` pattern, so there were no candidates. The hypothesis
  inventory is empty.
- The B020 claim was released. Board status reports no open bugs, one open and
  ready feature (F003), no in-progress or blocked items, no dangling blockers,
  and no unpromoted scratch.
- Closeout worker checks: entry validation, board index, documentation
  coherence, archive position and uniqueness, BOARD.md omission, and diff
  checks pass.
- Closeout pull request and merged-main run: pending.

Passing checks establish only their named invariants. They do not establish
perfect semantic correctness or formal controlled-English compliance.
