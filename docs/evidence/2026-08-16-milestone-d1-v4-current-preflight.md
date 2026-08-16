# Milestone D.1 version 4 current-source preflight — 2026-08-16

## Identity and authoritative state

This is the durable workpad for Q002. The authoritative repository is
`GhostlyGawd/engineering-board` at merged main
`80ba2c1abc9dd8c436802a57b68aa66b2a9a24cb`. The working branch is
`codex/d1-v4-preflight`.

The version 4 corpus is an unlocked proposal. This work runs one bounded,
non-scored preflight against current product code. It cannot lock the corpus,
start a scored run, or establish a product-effect claim.

## Decision ledger

- Active outcome: determine whether the current bounded-memory result changes
  a clean agent's first diagnosis from one visible incident to a relationship
  across the current and prior incidents.
- Approved direction: run one baseline and one context arm for each of the four
  positive proposal cases with equal client inputs and isolated sessions.
- Rejected alternatives: retain resolved entries in the active graph, change
  corpus wording during the run, retry a completed arm, infer success from
  retrieval rank, or seal and score version 4 without owner review.
- Authority boundary: repository work and configured Codex use are authorized.
  The product owner still owns exact baseline approval. The corpus remains
  unlocked and Milestone E remains deferred.

## Milestone purpose

Test the remaining north-star uncertainty: whether delivered repository memory
causes an agent to identify a prior cross-incident relationship before it
proposes another symptom-only correction.

## Plan

- [x] Revalidate the unlocked proposal and rebuild its deterministic context
  evidence from exact current main.
- [x] Create and claim Q002 before live trial work.
- [x] Pin the client, model, reasoning effort, instructions, response schema,
  tool boundary, source commit, corpus digest, and prompt bundle.
- [x] Run eight isolated arms: four positive cases, each baseline plus context.
- [x] Validate every response and review the first cause and correction against
  the version 4 cross-incident rubric.
- [x] Preserve raw evidence and append a bounded result without editing the
  proposal corpus or historical version 3 evidence.
- [x] Run focused and full repository checks plus independent pre-PR review.
- [ ] Pass pull-request and exact merged-main checks.
- [ ] Resolve and archive Q002 only after the evidence merge and current
  canonical revalidation.

## Acceptance criteria

### Worker phase

- [x] Proposal validation reports eight cases in the required 2/2/2/2 category
  distribution and corpus digest
  `ccdebc8be431047341bb13920d04fdc9a901e34664da6c90ed53f38be14ef662`.
- [x] Current-source context generation returns all expected positive memories
  within the first three results and all eight outcome-loop controls match.
- [x] Every arm uses Codex CLI 0.145.0, model `gpt-5.6-sol`, reasoning effort
  `medium`, approval `never`, read-only sandboxing, no tools or file reads, the
  same response schema, and one ephemeral session.
- [x] Baseline and context prompts differ only by the real Engineering Board
  context brief.
- [x] All eight responses conform to the schema and remain preserved; no
  completed arm is retried.
- [x] Review reports the baseline and context cross-incident-before-local
  rates, expected-memory ranks, canonical citations, and infrastructure
  failures. It does not compare this one-repetition preflight with the scored
  thresholds.

### Post-merge phase

- [ ] Pull-request checks and the exact merged-main check pass.
- [ ] Canonical Q002, BOARD, and GRAPH state agree with the evidence state.

### Closeout phase

- [x] Q002 has a source-linked Finding that answers the question.
- [x] The owner baseline-review gate is explicit, and version 4 remains
  unlocked with no scored run prepared.

## Implementation progress

- Q002 remains claimed and `in_progress` until merged-main revalidation.
- The proposal validates unchanged on current main.
- Eight immutable prompt arms were generated outside the repository. Pairwise
  common-input digests match. Before launch, each arm directory contained only
  `prompt.txt`.
- All eight arms completed once. Baseline and context each produced zero
  cross-incident-before-local first causes across four positive cases.
- Raw prompts, JSONL streams, responses, stderr logs, metadata, and review
  artifacts remain preserved in the bounded scratch evidence root.

## Validation evidence

- `evaluation/harness.py validate` returned corpus version 4, proposal role,
  eight cases, and the expected digest.
- `evaluation/harness.py contexts` against `80ba2c1abc9` returned current
  context fingerprints for D1-V4-C01 through D1-V4-C08, fixture digest
  `21224482fb9c7881ccf1314e9b33a52b76847b148324d89ee026668ae0c14e8a`,
  and frozen-core SHA-256
  `80f28ae659518d9d4fd3d2132c32f824bc7827a8ba69c72115a3b013e06bcbcb`.
- The four positive expected memories rank 1, 2, 2, and 1. Each structured
  outcome control changes its proposed H### to confirmed, adds five score
  points, preserves a rank at or below three, and changes the context
  fingerprint.
- The live contract is pinned to Codex CLI 0.145.0, model `gpt-5.6-sol`,
  reasoning effort `medium`, approval `never`, read-only sandboxing, ephemeral
  sessions, and an empty tool set. Source commit is `80ba2c1abc9`; instruction,
  tool-contract, and response-schema SHA-256 values are
  `5965e6804b4c94dffda15a8520e19a7edac1349808f15e3f4b8b51d942253899`,
  `4a87e7b188976494c73980f1ac6c7b89a0e6fb2533b3c812ccc50fc2671e6bab`,
  and `aa3d64eec5bcf746184effed089f92c0cdb559c4eb856d5ed077f87c5ab91153`.
- The prompt-bundle SHA-256 is
  `e515101b1a9968f719709dd120f505c17ccbc8985bdbc1be5abdccb6ddabf819`.
  All four baseline/context pairs have equal common-input SHA-256 values. A
  corrected read-only metadata assertion passed after the first `jq` command
  used the wrong scope; no live trial had started and no artifact changed.
- The first four-arm launch command failed in the Windows-to-WSL quoting layer
  before `codex exec` started. A post-failure inventory found only each frozen
  `prompt.txt`: no stdout, stderr, response, or session artifact existed. No
  response was completed or retried.
- The live executor reported exit 0 for all eight completed arms. The preserved
  artifacts independently prove eight unique threads, one `turn.completed`
  event per thread, only `agent_message` items, schema-valid responses equal to
  the JSONL agent messages, and empty stderr. The runner did not persist exit
  receipts or an append-only attempt ledger, so the local artifact set cannot
  independently reconstruct process exit codes or prove that an earlier
  attempt was never deleted. No arm is rerun to repair that historical gap.
- The execution-manifest SHA-256 is
  `309137885db42a303d8ecbbbca9b682f2d4f93d9bd053f27162bceadd4962e42`;
  the metadata and strict-review SHA-256 values are
  `16e39c1ca81e53f8f3ee774a946256cabe77dad135b620951e16e80202e26495`
  and `162852a60c91b69eec1817b6a475ce42b1af9d7bcd80e06a64b8bf01a922df37`.
- Every response cited only its matching `E-D1-V4-C##` evidence identifier.
  Expected memories H101 through H104 ranked 1, 2, 2, and 1.
- Focused gates passed: evaluation 22/22, graph engine 6/6, documentation
  coherence, and version coherence. The complete maintained suite passed 21 of
  21 suites in 57.3 seconds. `git diff --check` passed, and GRAPH source
  fingerprint `d7f0e279a9c2db30ef9dfe5e80cc6cf1d8ce4e079ab8f14332fc853b0082e453`
  matched the canonical board sources after the final entry edit.
- The self-board viewer was regenerated twice with identical SHA-256
  `83987dfef62839ec142c7b70ff56fe849fce022a507f40348476365277fd484f`.
  It renders Q002 as `in_progress`, reports one open question, and the focused
  board-view suite passed 52 of 52 checks.

## Bounded result

| Case | Expected memory rank | Baseline first cause and correction | Context first cause and correction | Strict result |
|---|---:|---|---|---|
| D1-V4-C01 | 1 | Import-only representation mismatch; canonicalize import validation | Import-only region-boundary mismatch; route import through shared validation | Both local: neither connects the administrator order-editor incident |
| D1-V4-C02 | 2 | Renewal-only expiration comparison; unify renewal representation | Renewal values use different time authorities; unify lease acquisition, renewal, and recovery | Both local under the first-cause rule: context does not connect the recovery incident until the later correction |
| D1-V4-C03 | 2 | API-only stale authorization state; invalidate API cache | API-only stale entitlement state; invalidate API entitlement state | Both local: neither connects the dashboard projection incident |
| D1-V4-C04 | 1 | Extension cache-generation race; add extension generation checks | Extension-only stale cache; invalidate on branch transition | Both local: neither connects the command-line index incident |

Baseline: 0 of 4, or 0 percent. Context: 0 of 4, or 0 percent. Observed
change: 0 percentage points. This is a one-repetition non-scored preflight, so
the accepted scored thresholds do not apply.

The context arm changed the response's `durable_systemic_conclusion` boolean
from false to true for C02 and from true to false for C04. Those opposite
changes show response variation, not the required cross-incident product
effect. The review does not count the word `systemic`, a later correction, a
retrieval rank, or context text that the response did not use in its first
cause. An independent strict review reached the same eight classifications.

Exact version 4 corpus digest:
`ccdebc8be431047341bb13920d04fdc9a901e34664da6c90ed53f38be14ef662`.
Exact draft structured-requirement digest:
`9315bfd6889b0e1cbab6e9e864d0ffaf94a20c59606755cfceeb8cbcbef64ed2`.
Version 4 remains an unlocked proposal and no scored run is prepared.

## Alignment matrix

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| Non-scored proposal isolation | Required | Proposal role remains unlocked; no prepare or score action | Proposal validation and prepare rejection | Product spec section 21, evaluation guide, this workpad | Preflight validated |
| Equal paired inputs | Required | One pinned client contract; context brief is the only arm difference | Prompt and metadata digest comparison | Operator instructions and this workpad | Frozen and verified |
| Cross-incident outcome | Required for v4 | Review must connect current and prior incidents; current-only rule is local | Preserved first cause and correction per arm | Corpus scoring-only contract and dated result | No observed effect: 0/4 in each arm |
| Agent-usable memory content | Required | Context contract version 3 returns title and typed bounded summary | Current frozen context payload inspection | Product spec sections 21.14-21.15 | Deterministic gate passed |
| No scored product claim | Required | One repetition per positive arm; corpus remains proposal | Absence of locked run/score artifacts | This workpad and final evidence | Enforced |
| Owner baseline authority | Required | Exact corpus and requirement digests are presented, not approved by the agent | Final state inspection | Product spec and handoff | Presented; owner decision pending |

## Documentation impact

- Changed: this dated workpad, Q002, BOARD, GRAPH, the authoritative product
  spec, the evaluation guide, the root README, and the generated self-board
  HTML now record the bounded current result, open question, and owner gate.
- Reviewed and unaffected: runtime core,
  MCP schemas, plugin manifests, setup, README commands, architecture,
  security/privacy, release versions, and published package artifacts. This
  checkpoint evaluates existing behavior and does not change a command,
  payload, installation, security boundary, or release artifact. CHANGELOG is
  unaffected because no shipped behavior or version changes.
- Historical version 3 and the 2026-07-30 proposal evidence remain unchanged.

## Uncertainties and assumptions

- A one-repetition preflight calibrates the product-information correction. It
  cannot estimate stable effect size or pass the accepted scored thresholds.
- Model behavior can vary even with pinned client inputs. A completed response
  is preserved rather than retried for a preferred answer.
- Raw trial artifacts use only the sanitized repository corpus. The local
  evidence root is under `$WSL_SCRATCH`; it remains resumable until the dated
  result is durably reviewed.
- A future scored or preflight runner needs an exclusively created start
  receipt and an appended end receipt for each arm. The receipts must bind the
  exact arguments and prompt, schema, runner, response, and stream hashes, and
  preserve the process exit code. The current post-run manifest cannot repair
  that missing historical chain.

## Blockers

No human action is required for the non-scored preflight. Exact version 4
baseline approval remains an owner gate after the result is presented.

## Campaign controls

- Start: `2026-08-16T02:12:41Z`.
- Correction cycles: 1 of 2. The cycle replaced the failed nested-quote launch
  with the hash-pinned direct-argument runner before any Codex turn began.
- Unexpected live failures: 1 of 1. The failed launch did not start Codex or
  produce a response.
- Elapsed-time limit: 120 minutes.
- Renew alignment before another correction cycle, branch, pull request, or
  external mutation after one unexpected live failure, two correction cycles,
  the elapsed limit, an authority change, or conflicting terminal evidence.

Alignment renewed at `2026-08-16T02:18:51Z`: the source commit, corpus,
prompts, client contract, non-scored boundary, and owner gate remain unchanged.
The failure mechanism is only nested command quoting. The corrected launch uses
one inspected scratch runner with direct arguments, refuses to run when any
response artifact already exists, and preserves stdout, stderr, and the final
response. The live executor reports the process exit, but the runner does not
persist that value in an arm receipt. The runner passed `bash -n` and has SHA-256
`3fda780098b93521d387f439db7121fdc1d149652a072a3c58e0aea1ee0513a9`.
This renewal authorizes the same eight one-shot arms; any further unexpected
launch or trial failure stops the campaign for owner review.

## Handoff and resume route

Completion state: `post-merge-pending`.

Next owner: the primary dogfood loop.

Remaining gates: run repository and pull-request checks, merge the evidence
pull request, pass exact merged-main checks, and revalidate Q002 before
resolution. The separate version 4 baseline decision remains with the owner.

Evidence destination: this Markdown workpad and the preserved bounded trial
artifacts under `$WSL_SCRATCH`.

Resume route: validate the settled documentation and board state, deliver the
evidence pull request, then revalidate and close Q002 without changing the
unlocked corpus.

Terminal action: `keep-open`.
