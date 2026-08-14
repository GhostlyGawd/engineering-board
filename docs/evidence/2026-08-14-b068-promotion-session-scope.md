# B068 promotion session-scope evidence

- Date: 2026-08-14
- Repository: `GhostlyGawd/engineering-board`
- Base commit: `a3e29cfc3010d95253213b868d526b6ab7e37898`
- Board entry: `B068`
- Completion state: `closeout`
- Implementation pull request: `#130`
- Implementation merge commit:
  `350c16144b3732c948aa559e13a7289029d776de`
- Implementation merged-main run: `31811404475` (`tests`, passed)
- Evidence destination: this file
- External gates: closeout pull request merge and passing closeout merged-main
  continuous integration
- Terminal action: resolve B068 in this closeout change, merge the closeout
  pull request, and verify its merged-main run

## Decision

Treat the unchanged promotion plan id as the apply capability for the exact
preview. When apply omits `session`, the core checks the all-scratch plan and
then each live filename and stem selector until it finds the unchanged plan.
An explicit selector remains authoritative. A changed scratch finding or
canonical source does not match and returns `plan_stale`.

This change does not prepare a release or change a version. An installed
plugin remains unchanged until a later owner-authorized release includes the
Unreleased fix.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| An unchanged session-scoped preview applies with its plan id alone. | Required by B068 and the Codex consolidation protocol. | `_promotion_plan_for_apply` restores an omitted filename or stem selector from the matching live plan. | The Milestone B pipeline previews one session and applies without `session`. | `skills/board-consolidate/SKILL.md`, the MCP schema, both README tool descriptions, and `docs/PRODUCT_EVOLUTION_SPEC.md` state the behavior. | Implementation and merged-main evidence pass; closeout evidence is pending. |
| Repeating the same session selector remains supported. | Required by B068 for compatibility. | Explicit `session` uses the direct promotion-plan path and does not infer another selector. | The existing promotion case previews and applies with the same scratch filename. | The consolidation skill and MCP schema identify the repeated selector as optional and supported. | Implementation and merged-main evidence pass; closeout evidence is pending. |
| Changed scratch or canonical input invalidates the plan. | Required content-bound safety behavior. | Every inferred candidate is replanned from live scratch and the current canonical source fingerprint. | Separate Milestone B cases change scratch content and a canonical entry after preview; each apply returns `plan_stale`. A linked unrelated scratch file cannot redirect a valid scoped apply. | The skill requires an unchanged plan id. The schema and changelog preserve stale-plan rejection. | Implementation and merged-main evidence pass; closeout evidence is pending. |
| Current operator and product documentation matches the apply contract without changing release state. | Required alignment invariant. | No manifest, package version, or release artifact changes. | The Codex plugin test checks the published skill wording and live MCP tool schema. Version and release checks pass in the maintained suite. | `CHANGELOG.md` records the Unreleased fix. Historical evidence and released-package claims remain unchanged. | Implementation and merged-main evidence pass; closeout evidence is pending. |

## Drift classification

- Required conflict, resolved in the worker: the Codex protocol instructed the
  caller to apply the unchanged plan id, but the core replanned with
  `session: null` and rejected an unchanged session-scoped preview.
- Documentation-only drift, resolved in the worker: the consolidation skill
  and MCP schema did not explain selector restoration or optional repetition.
- Reviewed and unaffected: `skills/board-intake/SKILL.md` previews the complete
  scratch inbox without a session selector. Its existing apply sequence still
  uses the direct all-scratch plan.
- Reviewed and unaffected: the high-level pattern workflow in `README.md` and
  the tool summary in `docs/llms.txt` do not specify selector arguments. Their
  preview/apply statements remain correct.
- Reviewed and unaffected: `SECURITY.md` does not define promotion selector
  mechanics. Every matching plan still reads current canonical and scratch
  input through the existing path, type, and linked-file checks.
- Reviewed and unaffected: setup, privacy, architecture, and visuals do not
  expose the optional apply selector or conflict with the changed behavior.
- Reviewed and unaffected: plugin manifests, package versions, checksums, and
  release artifacts do not change. The fix remains under Unreleased.
- Reviewed and unaffected: B067 owns the `actions/checkout@v4` Node.js warning
  that remains visible in merged-main run 31811404475. This closeout does not
  modify the workflow or resolve B067.
- Reviewed and unaffected: `.goal/` records and prior dated evidence are
  historical snapshots. Updating them would change their recorded source
  state.

## Validation evidence

- Red phase: the focused Milestone B pipeline raised `plan_stale` when apply
  supplied only the unchanged plan id from a session-scoped preview.
- Green phase: the Milestone B pipeline reports 20 passing checks. It covers
  plan-id-only apply, explicit same-session apply, scratch and canonical
  invalidation, and isolation from unrelated linked scratch.
- MCP contract evidence: the Codex plugin check verifies the isolated launcher,
  all 19 tools, the consolidation instruction, and the live tool schema.
- Python syntax evidence: both changed MCP modules compile with Python 3.12.3.
- Maintained repository suite: 20 of 20 suites pass with exit code 0.
- Implementation pull-request checks: runs 31811255503 and 31811288669 passed.
- Implementation pull request: #130 merged as `350c161`.
- Implementation merged-main run: 31811404475 passed.
- Closeout worker checks: board index and documentation coherence pass.
- Closeout pull request and merged-main run: pending.

Passing checks establish only their named invariants. They do not establish
perfect semantic correctness or formal controlled-English compliance.
