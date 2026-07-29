# Milestone D.1 live-evaluation preflight — 2026-07-29

## Outcome

The corrected evaluation harness is ready for the primary live trials. The
Codex compatibility profile is complete. The Claude Code primary profile is
not complete because the local Claude Code client is not authenticated.

This evidence does not show that Engineering Board context improves an agent
diagnosis. The primary product-effect gate remains open.

## Validity correction

The live-run preflight found two required conflicts in harness schema 1:

1. The context arm received `expected_relevant_memory` and
   `rejected_memories`. It did not receive a real v1.11.0 context result.
2. The attempt record supplied the outcome-loop match. The harness did not
   apply a product outcome and observe later retrieval.

These conditions could inflate the evaluation result. No scored live trial
used schema 1.

Harness schema 2 makes these corrections:

- It loads `engineering_board_core.py` from release commit
  `e26149bf505ea7f5ae2d95294a8a108e6b3c429f`.
- It builds real context from a sanitized canonical Markdown board fixture.
- It copies the same repository fixture into both trial arms.
- It excludes the expected memory, rejected-memory list, expected cause, and
  scoring contract from the agent input.
- It binds recorded memory identifiers and ranks to the frozen product result.
- It applies a structured outcome to an isolated fixture copy.
- It compares the applicable memory status, score, rank, and context
  fingerprint before and after the outcome.

The frozen evidence identifiers are:

```text
source_commit: e26149bf505ea7f5ae2d95294a8a108e6b3c429f
frozen_core_sha256: 95a6ea2c7d431adc280c7f0da61e5bde14321b707083e84f4cfed279ef09497f
fixture_sha256: 871f75eefd648143041007645641bfcfad038c8969d814fe572a4e9b8ff4c6c3
corpus_sha256: f92417bc4f09da6ba3935b362b5beef3f95dfb71c13e4ae94f3d118dbf20ba4f
client_contracts_sha256: 8f86e5e300cce735291d43a4f4ff8fd3cfb383651d1c0900673fc064095d830f
```

## Outcome-loop evidence

The frozen product comparison passed for all four applicable cases.

| Case | Memory | Before | After | Result |
|---|---|---|---|---|
| D1-C01 | H001 | proposed, score 34, rank 1 | confirmed, score 39, rank 1 | Match |
| D1-C02 | H002 | proposed, score 30, rank 2 | confirmed, score 35, rank 2 | Match |
| D1-C03 | H003 | proposed, score 32, rank 2 | confirmed, score 37, rank 2 | Match |
| D1-C04 | H004 | proposed, score 32, rank 1 | confirmed, score 37, rank 1 | Match |

The four negative cases do not apply a systemic outcome.

## Live-client preflight

| Profile | Client | Model | Readiness |
|---|---|---|---|
| Primary | Claude Code 2.1.200 | `claude-sonnet-5` | Blocked. The client is not authenticated. No API key or OAuth token is present. |
| Compatibility | Codex CLI 0.145.0 | `gpt-5.6-sol`, medium reasoning | Ready. Authentication and the exact-model probe passed. |

The first Codex operator attempt failed before scoring because the client does
not accept `uniqueItems` in its response-schema subset. The failure produced
no model result. The corrected response schema has SHA-256
`9f3cb4daf6f26f9402b986deb80b2707218781abcbe03884d6dcd42fdf66742e`.
Run `d1-2026-07-29-r2` supersedes that pre-score attempt.

## Compatibility evidence

Run `d1-2026-07-29-r2` has manifest fingerprint
`ac5b9fd7f0238f9e33a78a5895703bd8ab2513fca662bceb0a0101d0a7f35f73`.
All 16 Codex compatibility arms produced one scored response. No scored arm
was retried.

| Case | Baseline | Context | Context memory treatment | Durable negative conclusion |
|---|---|---|---|---|
| D1-C01 | Systemic before local | Systemic before local | H001 rank 1 | Not applicable |
| D1-C02 | Systemic before local | Systemic before local | H002 rank 2; rejected H006 | Not applicable |
| D1-C03 | Systemic before local | Systemic before local | H003 rank 2; rejected H005 | Not applicable |
| D1-C04 | Systemic before local | Systemic before local | H004 rank 1 | Not applicable |
| D1-C05 | Local conclusion | Local conclusion | No memory surfaced | No |
| D1-C06 | Local conclusion | Local conclusion | No memory surfaced | No |
| D1-C07 | Local conclusion | Local conclusion | No memory surfaced | No |
| D1-C08 | Local conclusion | Local conclusion | No memory surfaced | No |

Compatibility results:

```text
positive context rate: 100% (4 of 4)
positive baseline rate: 100% (4 of 4)
improvement: 0 percentage points
positive canonical citation coverage: 100% (8 of 8)
negative durable systemic conclusions: 0
```

These results test the Codex surface only. They do not change the primary
Claude product-effect gate.

## Deterministic validation

Worker validation passed:

```text
python3 -m unittest -q tests.evaluation.test_harness
14 tests passed

bash tests/run-all.sh
RUN-ALL SUMMARY: 19 pass, 0 fail (of 19 suites)
```

The deterministic checks verify the declared schemas, fixture integrity,
frozen-source loading, arm isolation, retry policy, scoring calculations, and
documentation counts. They do not prove product effect or perfect semantic
correctness.

PR test run `30430050481` failed because the default one-commit GitHub Actions
checkout did not contain the pinned v1.11.0 source commit. The workflow now
uses a full-history checkout. This correction preserves frozen-source
verification instead of substituting current source.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| Real v1.11.0 context | Required | Load the release core and build context from canonical Markdown | Frozen-context tests and context fingerprint checks | Central spec and evaluation guide | Required conflict repaired |
| No scoring oracle in agent input | Required | Keep case expectations in the manifest only | Pair-input assertions | Central spec and evaluation guide | Required conflict repaired |
| Equal repository in each pair | Required | Copy the same fingerprinted fixture into both arms | Repository equality and tamper checks | Evaluation guide | Required conflict repaired |
| Real outcome comparison | Required | Apply the outcome to an isolated fixture copy and rebuild context | Four outcome assertions | Central spec, report, and this evidence | Required conflict repaired |
| Exact run pins | Required | Pin source, clients, models, instructions, tools, schema, fixture, and context | Configuration and manifest checks | Evaluation guide and this evidence | Worker evidence complete |
| Compatibility run | Required and separate | Record 16 Codex arms | Bounded review and harness report | This evidence | Live compatibility evidence complete |
| Primary product-effect run | Required | Record 48 Claude Code arms | Not run | This evidence | Open: Claude authentication is required |
| Plugin, MCP runtime, package, version, setup, security, privacy, architecture, and visuals | Reviewed current surfaces | No production source, package, command, permission, network, storage, or visual behavior changes | Full repository suite | Current product documentation | Reviewed and unaffected |

## Completion state

- Completion state: `post-merge-pending`.
- External gates: merged-main continuous integration and Claude Code
  authentication.
- Evidence destination:
  `docs/evidence/2026-07-29-milestone-d1-live-evaluation-preflight.md`.
- Terminal action: merge the validity repair, verify merged-main continuous
  integration, then run the 48 primary arms after Claude Code authentication.
- Milestone action: keep Milestone D.1 open. Do not start Milestone E.
