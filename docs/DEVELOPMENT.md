# Engineering Board development process

This is the maintainer operating model approved on 2026-09-09. It is exercised
through Engineering Board itself. It does not add a hosted orchestrator or
change the installed plugin's Worker-mode protocol.

## Team and authority

| Role | Owns | Deliverable and decision |
|---|---|---|
| Product owner | User problem, priority, desired outcome, success criteria | Chooses direction and approves material changes to the evaluation target |
| Lead | Board continuity, scoped assignments, review reconciliation, integration and delivery | Claims coordination work, routes findings, and merges/releases within existing authorization |
| Builder | One bounded implementation assignment | Supplies implementation, meaningful regression coverage, and an evidence handoff |
| Independent verifier | Testing the requirement and completion claim against artifacts | Returns pass, changes required, or blocked, with evidence; unresolved requirement failures hold delivery |

A role is a responsibility, not a permanent agent process. The lead can build
a small change, but a different agent reviews a substantive behavior or
evaluation-contract change. Review agents start with the requirement and exact
artifact revision in a fresh context. They inspect the implementation before
reading the author's conclusions. Another persona in the same context is not
independent review. Different models are optional; no independence claim relies
on a model name alone.

Add a specialist only when its lens can change a concrete decision. Read-only
audits may run concurrently. Keep at most two implementation assignments active
initially, each in its own branch/worktree with explicit file ownership. The
assignments use distinct claim-owning working sessions. The lead owns
integration. Reviewers do not edit code, mutate board state, or merge
their own fixes.

Routine fixes, branches, tests, PRs, merges, releases and installed verification
use the owner's standing authorization. Do not repeatedly request it. Present a
concrete proposal when changing the product outcome, metric, corpus baseline or
irreversible data scope. Administration privileges do not change what evidence
proves or waive CI. Record exceptions explicitly with the owner's instruction.

## Work flow

1. **Observe and route.** Capture a reproducible problem through board intake,
   preview promotion, and apply the unchanged plan. Distinguish observation,
   hypothesis, and demonstrated defect. Synthetic fixtures stay isolated.
2. **Set acceptance.** State the user outcome, example, scope, exclusions,
   failure behavior, evidence needed and release impact. A generated placeholder
   such as "Define and verify the completion criterion" is not acceptance.
3. **Assign and claim.** Use the [assignment brief](../maintainers/templates/assignment.md).
   Record repository, project, entry, session owner, base commit and allowed
   files. Claim before edits; set in_progress only after acquisition. One
   in-progress entry per working session. The lead may own a claim on behalf of
   a named builder; record that relationship and heartbeat long work.
4. **Build and verify.** Reproduce the behavior, implement the agreed scope, and
   test the meaningful failure modes. Record commands, exit status and evidence
   paths. Tests should challenge the requirement, not just repeat the code.
5. **Review independently.** Use the [review brief](../maintainers/templates/review.md).
   Pin the reviewed commit, select lenses below, and report reproducible findings.
   Capture confirmed gaps as board entries. The builder fixes them; the verifier
   rechecks affected criteria at the new revision. Do not average away a failed
   requirement with votes. The lead resolves disagreements from evidence and
   records the reason; material requirement changes return to the owner.
6. **Integrate and deliver.** The lead confirms the acceptance evidence and CI,
   uses the normal PR path, then checks the merged revision. For a release,
   follow [RELEASING.md](RELEASING.md) and verify the published installation.
   A source fix and a released fix have separate evidence states. End the
   implementation claim once its scope is complete; track pending release or
   outcome work as an explicit linked entry rather than silently losing it.
7. **Observe the outcome.** Record what changed in actual use, regressions and
   uncertainty. Claim acquisition, a clean queue, or passing tests alone do not
   demonstrate better engineering diagnoses. H### outcomes and L### promotion
   use their explicit preview/apply contracts and cited evidence.

The lead records review, verification, delivery state and remaining follow-up
before resolving an entry. Questions receive a Finding before closure; update
their dependents against that Finding. Release each claim using its owner id.

## Review lenses and cadence

| Lens | Question | Trigger and minimum artifact |
|---|---|---|
| Product value | Does this change the user's task or just produce more activity? | New feature/direction: outcome and counterexample |
| Correctness | Does it work across success, failure, compatibility and recovery? | Behavior change: regression and integration evidence |
| Evidence quality | Could incorrect behavior pass, or could results be selected after observation? | Metrics, evals, scientific claims: adversarial cases, provenance and fixed scoring rules |
| User experience | Can a new user install, understand, finish and recover? | User-facing workflow change: observed end-to-end path |
| Operations and security | What happens on upgrades, interruption, concurrency or hostile input? | Persistent writes/host/package changes: relevant failure and isolation checks |

Every substantive change receives a correctness review. Add the other lenses
as risk requires; small wording/link edits need focused read-through, not an
entire panel. Run a fresh-user installed workflow at each release. A development
cycle is a delivered user outcome or release batch. At its end, inspect
recurrence and choose one bounded audit if an actual failure or uncertainty
warrants it. A cycle with no useful audit target needs no extra audit task.

Reuse existing `tdd-builder`, `code-reviewer` and `validator` responsibilities
where the host supports them. Their shipped Worker-mode prompts and JSON result
schemas stay intact. The richer maintainer briefs supplement host orchestration
and can be executed through named subagent assignments. No duplicate permanent
management hierarchy is required.

## Evidence and measurement

Keep review reports and task handoffs in version control under `docs/evidence/`.
For experiments, preserve the sanitized scripts, complete input inventory,
instructions, schemas, outputs, receipts and review under a durable repository
directory or a named retained artifact store. Record locator, checksum and
retention owner. Verify retrieval before claiming closeout. Temporary paths and
hashes without retrievable bytes are insufficient. Do not commit credentials or
unrelated private data. No live trial starts until its evidence destination,
comparison, scoring, stopping rules and reviewer are defined.

For each cycle, record time from claim to verified delivery, review regressions,
defects discovered after merge, and observed user outcomes. Record agent cost
and elapsed time when available; use "not measured" otherwise. Compare trends
after several cycles before expanding the team. Never use number of agents,
commits, closed entries or releases as the product-success metric.

## First trial

Audit D.1 v2 before another experiment or the proposed 1.14.0 release. Inspect
whether the schema, recorder, preparation and reports form an executable
workflow; whether ordering and memory disposition are supported by evidence;
whether negative/no-memory controls are possible; and whether old runs retain
their meaning. Record failures, fix the bounded contract gaps, and obtain a
fresh independent verification. Product-effect thresholds remain a separate
owner decision. The first trial's evidence determines the next live evaluation.

The [first independent audit](evidence/2026-09-09-development-team-pilot.md)
found release blockers B004-B007. F002 was reopened; v2 live evaluation and
release-readiness claims were held until those findings were addressed. The
[correction cycle](evidence/2026-09-09-d1-measurement-corrections.md) records
their independent source verification. A retained-evidence live pilot and
release verification remain separate follow-up work.
