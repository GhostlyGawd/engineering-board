# Milestone D.1 client-neutral evaluation contract

Date: 2026-07-29

State: Product-owner baseline accepted.

Requirement digest:
`sha256:7f583c3d03aca672c77b35adf436d2f2bf45a57b85824cbaf32bf4e024cd21fd`

## Decision

Codex is the required reference client for Milestone D.1. Engineering Board
does not require an account with each model provider. A dated evaluation can
add another client as an optional replication profile.

The reference profile controls the product-effect gate. A replication result
cannot change that gate. Compatibility claims use deterministic evidence for
the named protocol or package surface. A live provider run adds behavioral
replication evidence only.

## Reason

Provider accounts do not scale as a compatibility strategy. They add an
external authentication dependency that is not part of Engineering Board.
They also combine two different questions:

1. Does Engineering Board context improve the reference agent diagnosis?
2. Does a named client surface satisfy its protocol or package contract?

The reference evaluation answers the first question. Deterministic contract
tests answer the second question. Optional replication runs can measure
client-specific behavior when an operator has the applicable access.

## Current evidence

The complete Codex run `d1-2026-07-29-r2` scored 100 percent in the positive
baseline arms and 100 percent in the positive context arms. The improvement
was zero percentage points. This result does not show that context has no
value. It shows that the current corpus does not discriminate between the two
arms for the reference client.

The earlier Claude Code preflight remains historical evidence of the
superseded provider-specific contract. No Claude Code authentication task
remains open.

## Alignment

| Surface | Drift classification | Required disposition | Evidence |
|---|---|---|---|
| Central product spec | Normative decision drift | Replace primary and compatibility roles with reference and optional replication roles | Section 21 and D1-REQ-012, D1-REQ-013, D1-REQ-016, and D1-REQ-023 through D1-REQ-025 |
| Evaluation harness | Behavior and contract drift | Require one reference profile, permit optional replications, and exclude replications from the product gate | Focused harness tests |
| Evaluation guide | Operational documentation drift | Document the Codex reference run and optional replication configuration | `evaluation/README.md` |
| README and roadmap | Current-status drift | Remove the pending provider-authentication step and name corpus calibration as next | Current product prose |
| Architecture | Boundary documentation drift | Separate reference evaluation, replication evidence, and compatibility evidence | Evaluation-tree description |
| Historical evidence | No drift | Preserve prior workpads and preflight records without revision | Git history and dated evidence |
| Runtime, plugin, MCP package, setup, security, privacy, visuals, versions, and releases | Reviewed and unaffected | Do not change these surfaces because evaluation tooling does not change shipped runtime behavior | Existing release and runtime test suites |

## Verification

The focused harness suite must pass all 14 tests. The full repository suite
must pass. The requirements checker must report no deterministic defect in the
changed normative requirements. Pull-request and merged-main continuous
integration must pass.

The requirements checker reports `BASELINED — AUTHORIZED APPROVAL RECORDED`.
All deterministic, lifecycle, authority, semantic-review, and baseline-
approval gates pass for the digest above.

## Next product task

Calibrate the fixed corpus so the positive baseline arms can plausibly miss or
delay a shared cause. Preserve the current saturated run as dated evidence.
Run the Codex reference profile again against a new frozen corpus version.
Milestone E remains deferred until the product owner accepts the new evidence.

## Approval gate

The product owner approved the exact requirement digest on 2026-07-29. This
contract is the accepted baseline. Merge the reviewed branch after continuous
integration passes.
