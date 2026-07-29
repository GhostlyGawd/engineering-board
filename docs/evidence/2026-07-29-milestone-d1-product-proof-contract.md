# Milestone D.1 product-proof contract workpad — 2026-07-29

## Decision continuity

- Active outcome: prove whether shipped Engineering Board context causes an
  agent to identify the prior systemic investigation before a symptom-only
  correction.
- Gate 1: accepted by the product owner on 2026-07-29.
- Gate 2: not accepted. Four product decisions and human semantic review
  remain open.
- Evaluated product: Engineering Board v1.11.0 at an immutable commit selected
  by the future Gate 2 contract.
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
direction_baseline: 1134f6abc21efdb0077cde71a71ab5a7aa4ecf19
portfolio_status: inventory-only
audit_source: GhostlyGawd/repo-audit@9c64832e0d97e62a4fa45f2a544ffbc4c29b7a11
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
| D.1 product question | Gate 1 accepted | No production behavior change | Future paired product validation | Product spec sections 11 and 21 | Direction accepted |
| Fixed evaluation corpus | Gate 2 draft | Evaluation-only manifest and sanitized cases proposed | Future corpus schema and case-integrity checks | Product spec sections 21.2-21.4 | Open values |
| Paired clean-agent trials | Gate 2 draft | Isolated baseline and context arms proposed | Future controlled-input and isolation checks | Product spec sections 21.3-21.5 | Open client and repetition decisions |
| Systemic-before-local outcome | Gate 2 draft | Per-trial decision record and human-supported classification proposed | Future scorer and review evidence | Product spec sections 21.2, 21.4, and 21.5 | Open threshold |
| Retrieval-quality evidence | Gate 2 draft | Expected rank, irrelevant result, rejected-memory, and decoy measures proposed | Future retrieval-score fixtures | Product spec sections 21.4-21.5 | Open threshold |
| Outcome-loop evidence | Gate 2 draft | Before-and-after retrieval comparison proposed | Future outcome-loop fixture | Product spec section 21.4 | Draft |
| Baseline integrity | Gate 1 accepted | One frozen source commit for each evidence run | Future manifest and report inspection | Product spec section 21.6 | Direction accepted |
| Bounded reporting | Gate 1 accepted | Per-case evidence, limitations, failed cases, and no general productivity claim | Future report review | Product spec sections 21.5-21.8 | Direction accepted |
| Milestone E sequencing | Gate 1 accepted | No Milestone E implementation before owner acceptance of D.1 evidence | Repository and GitHub history inspection | Product spec sections 11 and 21.8-21.9 | Deferred |
| Legacy roadmap sequence | Required precedence clarity | No runtime behavior | Documentation inspection | ROADMAP current-sequence note points to the central spec | Documentation-only drift repaired |
| Current runtime documentation | Required current truth | v1.11.0 behavior is unchanged | Existing 18-suite release tree remains the current runtime evidence | README, setup, commands, MCP, architecture, security, landing page, LLM guide, visuals, versions, and manifests | Reviewed and unaffected because this change adds validation direction only |
| Historical Milestone A-D evidence | Required preservation | No historical behavior or evidence change | Existing dated evidence remains immutable | Historical reports | Reviewed and unaffected because they describe completed release boundaries |

No required behavior conflict exists. This change records an accepted product
question and a draft validation contract. It does not advertise new runtime
behavior.

## Draft requirement state

The requirement mode is `write`. The language profile is `shall`. The
lifecycle profile is `general`.

The structured draft contains D1-REQ-001 through D1-REQ-011. The deterministic
checker reports no `FAIL` result.

```text
status: DRAFT — SOURCE OR DECISIONS INCOMPLETE
content_digest: sha256:de04bb3b948792baa138bba0e98dbb3fc7423c5cec2ac5b95c2a1a52fa31adea
deterministic_failures: 0
```

This status is correct. The draft cannot become a Gate 2 baseline until the
open owner decisions, human semantic reviews, and exact-digest approval are
complete.

## Open Gate 2 decisions

1. Select the fixed case count and category allocation.
2. Select the independent repetition count and retry policy.
3. Select the primary client and model and any compatibility arms.
4. Select the systemic-before-local threshold, expected-memory rank threshold,
   and maximum false-positive rate.

The product spec gives recommended starting values for review. It does not
label them as approved.

## Draft delivery phases

- [x] Record Gate 1 approval.
- [x] Write the product question, boundary, draft requirements, validation
  records, and non-goals.
- [x] Run the deterministic requirements checker.
- [x] Align the central spec and this workpad.
- [ ] Resolve the four product-owner decisions.
- [ ] Complete human semantic review.
- [ ] Record Gate 2 approval against the exact content digest.
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
state: self-contained Gate 1 direction
external_gate: none
evidence_destination: docs/evidence/2026-07-29-milestone-d1-product-proof-contract.md
terminal_action: merge after continuous integration
next_owner: product owner resolves Gate 2 decisions
```
