# Development team pilot — 2026-09-09

## Assignment and acceptance

Owner: repository product owner; approval recorded in the development
conversation. Lead/builder for maintainer process: `/root`.
Process verifier: `/root/review_process`. Evaluation auditor:
`/root/audit_evaluation`. Both reviewers began in fresh contexts and were
read-only. Base revision: `151a3563b70ca0df62b35cee422be66d2227ab16`.

Scope: establish the approved maintainer team and reusable handoffs (F003),
then independently audit the new D.1 v2 contract before another live trial.
Acceptance: clear responsibilities, claim and worktree ownership, proportional
review, durable evidence and delivery states; independent process review;
audited contract with reproducible defects routed to canonical work.
No experiment, baseline change or release is part of this pilot's acceptance.

## Process review

`review_process` passed the proposed AGENTS.md, CONTRIBUTING.md,
docs/DEVELOPMENT.md and assignment/review templates. It compared the process
with the existing Worker-mode role prompts and release policy. No blocker was
found. The lead incorporated its suggestions: distinct claim-owning working
sessions for concurrent assignments, a defined cycle with optional targeted
audit, and concrete canonical Done-when checklists instead of placeholders.

This is a review of instruction coherence. It does not demonstrate team
effectiveness or better engineering diagnoses.

## Independent D.1 v2 audit

Verdict: changes required. All 26 existing evaluation tests passed while the
auditor reproduced the following defects at the base revision. Reproduction
used deterministic synthetic attempts and the actual prepared locked corpus;
no live model trials were executed.

| Entry | Severity | Failed requirement and reproduction |
|---|---|---|
| B004 | P1 | Response schema requires an evaluation object, baseline recorder requires null/false, and empty-context recorder requires a surfaced target. Actual locked corpus C07/C08 produces six empty-context arms. Neither null nor an invented ID works across the contract. |
| B005 | P1 | Recorder accepts before-local=true with classification_evidence explicitly stating the local correction appeared first. No preserved sequence or offsets bind the flag to the response; JSON serialization sorts keys. |
| B006 | P1 | Six lexical-decoy v2 attempts with memory_status=rejected, disposition=apply, rejected_memory_treatment=used, lexical_decoy_treatment=used and durable_systemic_conclusion=false can coexist with overall_pass=true in a complete synthetic run. |
| B007 | P2 | One recorded positive v2 success and 47 missing reference arms produces eligible_context_arms=1 and rate_percent=100. Eligibility is chosen from recorded attempts rather than the planned contract. |

Source locations at the audited revision:

- `evaluation/memory-evaluation-response.schema.json`: evaluation object at
  line 15.
- `evaluation/harness.py`: baseline handling at line 836, v2 evaluation
  validation at lines 864-912, negative conclusion gate at line 1064, metric
  population and counting at lines 1087-1092.
- `evaluation/harness.py`: sorted serialization at line 139 cannot preserve
  the original order of response fields.

Compatibility check: the auditor compared a complete synthetic v1-only run
with the pre-v2 harness at `1974c94`. All historical score fields matched after
removing the two additive metric fields. Historical response schema, operator
instructions, locked corpus and calibration corpus were unchanged by v2.

The auditor recommends treating `memory_evaluation_before_local` as a reviewer
annotation until a frozen rubric and retrievable response/sequence evidence
support it. Structural status equality and incident-ID checks do not prove
that a disposition is correct or that a response preserved epistemic status
throughout its free text.

## Lead disposition and first correction

F002 is reopened. B004-B007 track the unmet criteria. Live v2 evaluation and
release-readiness claims are held pending corrective work and independent
review. The historical product-effect gates are unchanged.

B004 is the first bounded build assignment. `/root/build_absent_memory` works
on `fix/d1-absent-memory` in a separate worktree. The lead holds its claim on
behalf of session `builder-b004-team-pilot`. Allowed changes: schema, absent
memory validation, v2 instructions, relevant tests and release note. Acceptance:
null/false for baseline and empty context, rejection of fabricated memory use,
support for surfaced cluster IDs, and preserved v1 behavior. Ordering evidence,
safeguard scoring and denominator design remain separate findings.

The independent auditor passed builder commit
`19edddcb84c6d5fc3bc57ffb780f841c4ad92073` before integration as `10fec3e`.
It ran 28 evaluation tests and independently validated/recorded all 48 prepared
arms: 24 baseline null responses, six empty-context null responses and 18
surfaced-cluster evaluations. All 54 populated-context adversarial checks
rejected null evaluations, unsupplied targets and changed statuses. Complete
v1 scoring matched the parent commit; historical inputs remain unchanged.

B004 is verified within that scope. B005-B007 remain open; this pass does not
establish trustworthy before-local measurement or authorize a live evaluation.
F003 closes after the process and first audit are delivered; F002 stays blocked
until its own requirements are met.

## Pilot measures

- Independent evaluation audit: four concrete defects surfaced despite green
  existing tests; all four linked to board work.
- Process review: no blocker, three clarity suggestions incorporated.
- Product or live-model outcomes: not measured in this pilot.
- Integrated verification: all 21 repository suites passed, including 28
  evaluation tests. B004 and F003 resolved as source-complete; owning claims
  released. F002 remains blocked by B005-B007.
- Agent token cost and comparable prior cycle time: not measured.
- B004 builder-to-verifier handoff: passed at the first submitted revision;
  source integration recorded above. Installation/release has not occurred.
- Cycle timing: F003 claimed at approximately 13:14 UTC; final source delivery
  timing is available from the PR merge and board closeout records.

These counts describe this trial only. Team productivity and defect escape
rates require observations across several delivered outcomes.
