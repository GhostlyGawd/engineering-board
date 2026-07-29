# Milestone D.1 product-proof contract workpad — 2026-07-29

## Decision continuity

- Active outcome: prove whether shipped Engineering Board context causes an
  agent to identify the prior systemic investigation before a symptom-only
  correction.
- Gate 1: accepted by the product owner on 2026-07-29.
- Gate 2: accepted by the product owner on 2026-07-29.
- Authorized next work: implement the repository-local evaluation harness,
  frozen corpus, scoring tools, and dated evidence path.
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
| D.1 product question | Gate 1 accepted | No production behavior change | Paired product validation is required | Product spec sections 11 and 21 | Direction accepted |
| Fixed evaluation corpus | Gate 2 accepted | Exactly eight sanitized cases: two recurring-bug, two cross-domain shared-cause, two lexical-decoy, and two independent-issue cases | Future schema, category, and case-integrity checks | Product spec sections 21.3, 21.4, and 21.7 | Implementation authorized |
| Primary paired trials | Gate 2 accepted | Three independent paired repetitions for each case through the Claude Code plugin | Future controlled-input, isolation, count, and retry checks | Product spec sections 21.3-21.7 | Implementation authorized |
| MCP compatibility trials | Gate 2 accepted | One paired repetition for each case through Codex CLI as an MCP client | Future protocol and evidence-parity checks | Product spec sections 21.4 and 21.7 | Implementation authorized |
| Run controls | Gate 2 accepted | Each dated manifest pins source, client, model, instructions, tools, policy, and context; one bounded infrastructure replacement is permitted | Future manifest and invalid-attempt checks | Product spec sections 21.6-21.7 | Implementation authorized |
| Product-effect threshold | Gate 2 accepted | Context arm must reach 75 percent and exceed baseline by 25 percentage points | Future aggregate scorer and preserved trial records | Product spec sections 21.4 and 21.7 | Implementation authorized |
| Retrieval and false-positive gates | Gate 2 accepted | Positive claims require 100 percent canonical citation; expected memory must rank in the first three; decoy and independent cases allow zero durable systemic conclusions | Future retrieval, citation, decoy, and independent-case checks | Product spec sections 21.4, 21.5, and 21.7 | Implementation authorized |
| Outcome-loop evidence | Gate 2 accepted | Before-and-after retrieval comparison remains required | Future outcome-loop fixture | Product spec sections 21.4-21.5 | Implementation authorized |
| Baseline integrity | Gate 2 accepted | One frozen source commit for each evidence run | Future manifest and report inspection | Product spec section 21.6 | Implementation authorized |
| Bounded reporting | Gate 2 accepted | Per-case evidence, limitations, failed cases, and no general productivity claim | Future report review | Product spec sections 21.5-21.9 | Implementation authorized |
| Milestone E sequencing | Accepted constraint | No Milestone E implementation before owner acceptance of D.1 evidence | Repository and GitHub history inspection | Product spec sections 11 and 21.8-21.9 | Deferred |
| Current roadmap sequence | Required precedence clarity | No runtime behavior | Documentation inspection | ROADMAP current-sequence note points to the accepted D.1 contract | Documentation-only drift repaired |
| Current runtime documentation | Required current truth | v1.11.0 behavior is unchanged | Existing 18-suite release tree remains the current runtime evidence | README, setup, commands, MCP, architecture, security, landing page, LLM guide, visuals, versions, and manifests | Reviewed and unaffected because this change authorizes evaluation work only |
| Historical Milestone A-D evidence | Required preservation | No historical behavior or evidence change | Existing dated evidence remains immutable | Historical reports | Reviewed and unaffected because they describe completed release boundaries |

No required behavior conflict exists. This change accepts a product-validation
contract. It does not advertise new runtime behavior.

## Requirement state

The requirement mode is `write`. The language profile is `shall`. The
lifecycle profile is `general`.

The structured artifact contains D1-REQ-001 through D1-REQ-022. The
deterministic checker reports no `FAIL` result.

```text
status: DRAFT — SOURCE OR DECISIONS INCOMPLETE
content_digest: sha256:28728a96582a6a118647fb4680726b40f05eadf2f08b444bdd87e8988600e71f
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
- the full release-tree test command passed all 18 suites;
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
4. Require at least 75 percent systemic-before-local outcomes in the context
   arm and at least a 25-percentage-point improvement over baseline.
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
- [ ] Implement the evaluation harness and frozen corpus.
- [ ] Run paired product validation.
- [ ] Publish dated results and calibration candidates.
- [ ] Decide whether to calibrate Milestone D or begin a Milestone E contract.

## Documentation disposition

Changed:

- `docs/PRODUCT_EVOLUTION_SPEC.md`
- `docs/evidence/2026-07-29-milestone-d1-product-proof-contract.md`
- `ROADMAP.md`

Reviewed and unaffected:

- README, setup, command, skill, MCP, architecture, security, privacy, visual,
  version, manifest, and package surfaces because no runtime behavior, command,
  interface, permission, security boundary, package, or release changed.
- Historical Milestone A-D evidence because each report describes a dated
  completed state.

## Completion state

```text
state: self-contained Gate 2 contract
external_gate: none
evidence_destination: docs/evidence/2026-07-29-milestone-d1-product-proof-contract.md
terminal_action: merge after continuous integration
next_owner: implement the Milestone D.1 evaluation harness
```
