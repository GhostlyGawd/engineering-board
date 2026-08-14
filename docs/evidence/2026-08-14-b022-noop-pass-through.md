# B022 no-op pass-through evidence

- Date: 2026-08-14
- Repository: `GhostlyGawd/engineering-board`
- Base commit: `635c85c4c16e103d3fcdaf03476b94d897421901`
- Board entry: `B022`
- Completion state: `post-merge-pending`
- Implementation pull request: pending
- Evidence destination: this file
- External gates: implementation pull request merge, passing implementation
  merged-main continuous integration, closeout pull request merge, and passing
  closeout merged-main continuous integration
- Terminal action: `keep-open` until implementation merged-main evidence passes;
  then resolve B022 in a closeout change and verify the closeout merged-main run

## Decision

Preserve the existing pass-through transitions. `nothing_to_test` and
`nothing_to_review` mean that a worker completed its applicability check and
found no work for that discipline. They do not mean that the entry failed or
that work is incomplete. Advancing prevents the same inapplicable discipline
from repeatedly selecting the entry and delaying later work.

Require the worker to record why the discipline is not applicable and what
evidence supports that decision. Keep `cannot_proceed` with a null
`suggested_next_needs` value as the explicit hold path.

This change does not alter the state-machine implementation, output schema,
sentinel inventory, claim lifecycle, product version, or release state.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| `nothing_to_test` and `nothing_to_review` are completed applicability decisions and require evidence in `notes`. | Required by B022. | The TDD and review worker prompts define both statuses and their evidence requirement. | Agent-frontmatter tests require the definition, rationale, and notes contract. | `ARCHITECTURE.md` records the state-machine meaning. | Worker contract evidence passes; post-merge evidence is pending. |
| A no-op result advances to the next discipline; `cannot_proceed` with null holds. | Selected B022 completion alternative and existing compatibility contract. | Worker output mappings remain review and validate for no-op, and null for a held failure. | Mode routing and `/board-run` structural tests require the pass-through rule. | `hooks/stop-hook-procedure.md` and `commands/board-run.md` state the rationale and hold contrast. | Worker contract evidence passes; post-merge evidence is pending. |
| Product-review history preserves the original concern and records the decision that supersedes it. | Required evidence-preservation boundary. | No historical row is rewritten. | Documentation coherence passes in the maintained suite. | RFC 0002 appends a dated B022 resolution note; `CHANGELOG.md` records the Unreleased clarification. | Worker and full-suite evidence pass; post-merge evidence is pending. |
| Unrelated orchestration, security, and release behavior remains unchanged. | Required alignment invariant. | No sentinel, hook code, claim path, schema, permission, version, checksum, tag, or publication change. | Existing mode, orchestration, security, version, and release suites pass as regression gates. | README, setup, security, privacy, release, and visual surfaces do not specify these two outcome semantics. | Worker and full-suite evidence pass; post-merge evidence is pending. |

## Drift classification

- Documentation-only drift, resolved in the worker: the prompts said
  pass-through but did not explain that no-op is a completed applicability
  decision or why a hold would cause repeated dispatch.
- Recommended gap, resolved in the worker: no-op workers now must put their
  reason and supporting evidence in `notes`.
- Reviewed and unaffected: the executable state-machine transition does not
  change. The Stop procedure and `/board-run` already applied each worker's
  non-null next discipline.
- Reviewed and unaffected: `nothing_to_validate` is a terminal validator
  result and remains distinct. B022 concerns only the TDD and review gates.
- Reviewed and unaffected: `hooks/hooks.json` does not interpret worker status
  values. Its fast paths and sentinel inventory remain correct.
- Reviewed and unaffected: claim acquisition, heartbeat, release, and board
  frontmatter mutation mechanics do not change.
- Reviewed and unaffected: README, setup, security, privacy, provenance,
  release guidance, product version surfaces, and visuals do not define these
  outcome semantics.
- Reviewed and unaffected: RFC 0002 is historical product-review evidence. A
  dated note supersedes its open concern without rewriting the original row.

## Validation evidence

- Red phase: mode contracts reported seven missing rationale and evidence
  checks; the `/board-run` contract reported one missing rationale check.
- Green mode phase: all six mode groups pass. The TDD prompt reports 20
  checks, the review/validator prompt reports 50, and Stop routing reports 99.
- Green command phase: the `/board-run` contract reports 19 passing checks.
- Maintained repository suite: 21 of 21 suites pass.
- Implementation pull request and merged-main run: pending.
- Closeout pull request and merged-main run: pending.

These path and phrase checks prevent silent omission of the reviewed contract.
They do not prove model behavior or perfect semantic correctness. They do not
establish formal controlled-English compliance.
