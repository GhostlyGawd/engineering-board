# Milestone D.1 product-proof contract workpad — 2026-07-29

## Decision continuity

- Active outcome: prove whether shipped Engineering Board context causes an
  agent to identify the prior systemic investigation before a symptom-only
  correction.
- Gate 1: accepted by the product owner on 2026-07-29.
- Gate 2: accepted by the product owner on 2026-07-29.
- Implemented work: repository-local evaluation harness, frozen corpus,
  scoring tools, and dated evidence path.
- Evaluated product: frozen Engineering Board v1.11.0 behavior. The dated run
  manifest must identify the exact source commit, clients, and models.
- Canonical storage: repository-owned Markdown remains authoritative.
- Evidence boundary: repository-local sanitized cases and dated validation
  reports. The evaluation is not telemetry.
- Explicitly deferred: production calibration, Milestone E, SQLite,
  embeddings, hosted evaluation, cross-repository aggregation, and fix
  execution.

Repository context:

```text
repository: GhostlyGawd/engineering-board
default_branch: main
contract_baseline: a26c8fb82f055ff7a65aa940c414f86990a0060d
portfolio_status: inventory-only
audit_source: GhostlyGawd/repo-audit@ee6e44fe4498f9f624f43d2f355516f98f821148
```

The portfolio record is partial. Empty project and capability lists do not
prove that no project or capability exists.

## Why this milestone is next

Milestone D release evidence proves that retrieval, outcome, Learning, and
adapter behavior meet their specified contracts. It does not prove that the
context changes an agent diagnosis.

Milestone E could make the product act faster. If retrieval is noisy or the
agent does not use the surfaced evidence, execution ergonomics could amplify a
weak decision. Milestone D.1 tests the intelligence advantage before the
product adds another action layer.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| D.1 product question | Gate 1 accepted | Harness implemented without a production behavior change | Live paired product validation remains required | Product spec sections 11 and 21 | Harness implemented; proof pending |
| Fixed evaluation corpus | Gate 2 accepted | `evaluation/corpus.json` defines eight sanitized cases with two cases in each accepted category | Schema, allocation, semantic, evidence-path, and digest tests | Product spec sections 21.3, 21.4, and 21.7; evaluation guide | Implemented |
| Primary paired trials | Gate 2 accepted | Planner creates three isolated baseline/context pairs for each case under the Claude Code plugin contract | Controlled-input, isolation, count, and retry tests | Product spec sections 21.3-21.7; evaluation guide | Planning and recording implemented; live trials pending |
| MCP compatibility trials | Gate 2 accepted | Planner creates one isolated pair for each case under the Codex CLI MCP contract | Profile, count, and evidence-parity tests | Product spec sections 21.4 and 21.7; evaluation guide | Planning and recording implemented; live trials pending |
| Run controls | Gate 2 accepted | Manifest pins source, client, model, instructions, tools, policy, and context; recorder permits one bounded infrastructure replacement | Manifest fingerprint, linked-path, input digest, retry, and replacement tests | Product spec sections 21.6-21.7; implementation evidence | Implemented |
| Product-effect threshold | Gate 2 accepted | Twelve positive-case context trials must reach 75 percent and exceed the 12 positive-case baseline trials by 25 percentage points | Aggregate boundary scorer test and preserved records | Product spec sections 21.4 and 21.7; implementation evidence | Implemented; live proof pending |
| Retrieval and false-positive gates | Gate 2 accepted | Positive claims require 100 percent canonical citation; expected memory must rank in the first three; decoy and independent cases allow zero durable systemic conclusions | Retrieval, citation, decoy, and independent-case scorer tests | Product spec sections 21.4, 21.5, and 21.7; implementation evidence | Implemented; live proof pending |
| Outcome-loop evidence | Gate 2 accepted | Each context record preserves expected and observed outcome effects and rank changes | Outcome-loop schema and scorer tests | Product spec sections 21.4-21.5; implementation evidence | Implemented; live proof pending |
| Baseline integrity | Gate 2 accepted | One frozen source commit and content fingerprints identify each run | Manifest and input-integrity tests | Product spec section 21.6; evaluation guide | Implemented |
| Bounded reporting | Gate 2 accepted | JSON and Markdown reports contain per-case evidence, limitations, failed cases, and no general productivity claim | Bounded-report test | Product spec sections 21.5-21.9; implementation evidence | Implemented |
| Milestone E sequencing | Accepted constraint | No Milestone E implementation before owner acceptance of D.1 evidence | Repository and GitHub history inspection | Product spec sections 11 and 21.8-21.9 | Deferred |
| Current roadmap sequence | Required precedence clarity | Harness implemented; live product validation is next | Documentation inspection | ROADMAP current-sequence note and central spec | Aligned |
| Current runtime documentation | Required current truth | v1.11.0 plugin and MCP behavior is unchanged; repository tooling adds the harness | Harness suite and full release tree | README, architecture, security, changelog, evaluation guide, and evidence changed; setup, commands, MCP, landing page, LLM guide, visuals, versions, and manifests reviewed | Runtime surfaces unaffected; repository tooling aligned |
| Historical Milestone A-D evidence | Required preservation | No historical behavior or evidence change | Existing dated evidence remains immutable | Historical reports | Reviewed and unaffected because they describe completed release boundaries |

No required behavior conflict remains. This change implements product-validation
tooling. It does not advertise a product effect or new runtime behavior.

## Requirement state

The requirement mode is `write`. The language profile is `shall`. The
lifecycle profile is `general`.

The structured artifact contains D1-REQ-001 through D1-REQ-022. The
deterministic checker reports no `FAIL` result.

```text
status: DRAFT — SOURCE OR DECISIONS INCOMPLETE
content_digest: sha256:1428c553a5490546d21f8a649d12f4ac5d823bf3d6bc6719a3d5ab4e641f2cfb
deterministic_failures: 0
```

The product owner approved the Gate 2 values. The structured requirements
checker uses a separate release gate. It cannot report `BASELINED — AUTHORIZED
APPROVAL RECORDED` until digest-matched human semantic reviews and approval are
recorded. This limitation does not reverse the accepted product decision.

## Contract-change validation

Evidence collected on 2026-07-29:

- the bundled requirements-reference status check passed;
- the structured requirements checker passed every deterministic check and
  reported the draft status and digest above;
- `git diff --check` passed;
- the focused harness suite passed all 13 tests;
- the complete repository suite passed all 19 suites;
- the focused documentation-coherence check passed;
- the workpad contains exactly one alignment table; and
- the central specification contains all 22 checked requirement identifiers.

These checks verify contract structure, documentation consistency, and runtime
regression safety. They do not prove the Milestone D.1 product effect. The
paired evidence run must supply that proof.

## Accepted Gate 2 decisions

1. Use eight fixed cases with two cases in each approved category.
2. Use three primary paired repetitions per case. Do not retry a scored trial.
   Permit one replacement only for a preserved infrastructure failure that
   occurs before a scored result.
3. Use the Claude Code plugin as the primary client. Use Codex CLI as the MCP
   compatibility client. Pin exact client and model identifiers in dated run
   evidence.
4. Apply the 75 percent rate and 25-percentage-point improvement to the 12
   positive-case trials in each primary arm. Apply the separate zero-conclusion
   gate to lexical-decoy and independent-issue cases.
5. Require the expected relevant memory in the first three results and
   canonical citations for every positive classification.
6. Permit zero durable systemic conclusions from lexical-decoy or
   independent-issue cases.

## Delivery phases

- [x] Record Gate 1 approval.
- [x] Write the product question, boundary, requirements, validation records,
  and non-goals.
- [x] Resolve the Gate 2 product decisions.
- [x] Record Gate 2 acceptance.
- [x] Run the deterministic requirements checker.
- [x] Align the central spec, roadmap, and this workpad.
- [x] Implement the evaluation harness and frozen corpus.
- [ ] Run paired product validation.
- [ ] Publish dated results and calibration candidates.
- [ ] Decide whether to calibrate Milestone D or begin a Milestone E contract.

## Documentation disposition

Changed:

- `docs/PRODUCT_EVOLUTION_SPEC.md`
- `docs/evidence/2026-07-29-milestone-d1-product-proof-contract.md`
- `docs/evidence/2026-07-29-milestone-d1-harness-implementation.md`
- `evaluation/README.md`
- `README.md`
- `ARCHITECTURE.md`
- `SECURITY.md`
- `CHANGELOG.md`
- `ROADMAP.md`

Reviewed and unaffected:

- Setup, command, skill, MCP, landing-page, LLM-guide, visual, version,
  manifest, permission, and package surfaces because the harness does not
  change a runtime interface, permission, package, bundle, or release.
- Historical Milestone A-D evidence because each report describes a dated
  completed state.

## Completion state

```text
state: self-contained Milestone D.1 harness implementation
external_gate: none
evidence_destination: docs/evidence/2026-07-29-milestone-d1-harness-implementation.md
terminal_action: merge after continuous integration
next_owner: authorize and run the dated paired product validation
```
