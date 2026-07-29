# Milestone D.1 calibrated reference run

Date: 2026-07-29

State: Reference run complete. Closeout merge pending.

Completion state: `closeout-pending`

## Outcome

The locked version 3 evidence corpus did not pass the product-effect gate.

- Positive context rate: 100 percent, 12 of 12 arms.
- Positive baseline rate: 83.33 percent, 10 of 12 arms.
- Improvement: 16.67 percentage points.
- Required improvement: 25 percentage points.
- Negative durable systemic conclusions: zero.
- Infrastructure failures: zero.
- Replacements: zero.
- Overall result: fail.

Engineering Board does not claim that context improves agent diagnoses from
this result.

## Run identity

- Run: `d1-2026-07-29-calibrated-r1`
- Merged source: `c96831ec849638585c8859f686340e6c0a45c33b`
- Frozen product source:
  `e26149bf505ea7f5ae2d95294a8a108e6b3c429f`
- Client: `codex-cli 0.145.0`
- Model: `gpt-5.6-sol`
- Reasoning effort: medium
- Trial policy: `d1-client-neutral-v2`
- Corpus: `d1-product-effect`, version 3
- Corpus digest:
  `e8756040e5c6b9c1f9f40e7b47cc17cf196d59e605234fd0c67796a24da6b956`
- Manifest fingerprint:
  `70f5afdc2b7bcabf434522d0cfde05507b439f330679226eb395bda9830fee92`
- Context fixture digest:
  `21224482fb9c7881ccf1314e9b33a52b76847b148324d89ee026668ae0c14e8a`
- Frozen core digest:
  `95a6ea2c7d431adc280c7f0da61e5bde14321b707083e84f4cfed279ef09497f`
- Client-contract digest:
  `73306a3ab7ee148987fd495c2ef15fae66a624ee9dcbc7d09ce918445e6ae3ec`
- Run-configuration digest:
  `0f22078ccc81e979dbf2dea1949b029838b0fdcd23260b1f50ae8540a9f0d148`
- Complete run-directory digest:
  `fbeef6fa1e023430028ca60606f601534c71be87d45af9a9e333d7685dc21244`
- Bounded JSON report digest:
  `8cc200ad48d963464fcb5531a51ba2a041e6054205606bed1c8ef6f2609a4170`

The run used 24 isolated pairs and 48 arms. Each arm used an ephemeral Codex
session and a separate read-only workspace. The operator supplied the same
case evidence to both arms in a pair. Only the context arm received the frozen
Engineering Board context. The operator preserved all 48 structured
responses, client timing records, and scored attempt records outside the
source tree.

The installed Codex runtime also passed a separate signed-in app-server
validation. That validation proved a programmatic turn, a bounded workspace
edit, a host-mediated tool, child credential isolation, idempotent replay, and
token telemetry. The scored evaluation used noninteractive `codex exec` with
the pinned response schema.

## Bounded rubric review

The reviewer classified the first stated cause. A systemic classification
required the first cause to identify a shared boundary or rule before the
first proposed correction.

- D1-C01: Baseline 3 of 3 systemic. Context 3 of 3 systemic.
- D1-C02: Baseline 3 of 3 systemic. Context 3 of 3 systemic.
- D1-C03: Baseline 3 of 3 systemic. Context 3 of 3 systemic.
- D1-C04: Baseline 1 of 3 systemic. Context 3 of 3 systemic.
- D1-C05 through D1-C08: No systemic-first classification and no durable
  systemic conclusion in any arm.

Context retrieved each expected positive memory within the first three
results. The lexical-decoy contexts retrieved rejected memories H105 and H106.
Codex rejected those memories in all six applicable context arms. It did not
use the misleading memory as a root cause.

## Alignment

| Contract item | Normative level | Observed evidence | Gate | Documentation disposition | Status |
|---|---|---|---|---|---|
| Reference completion | Required | 48 of 48 scored arms; no failures or replacements | `reference_complete` | This dated evidence and harness report | Pass |
| Positive context rate | Required | 100 percent, 12 of 12 | At least 75 percent | This dated evidence and central spec | Pass |
| Product-effect improvement | Required | 16.67 percentage points | At least 25 percentage points | README, roadmap, evaluation guide, and central spec state the failed result | Fail |
| Canonical citations and retrieval | Required | All systemic-first arms used valid case citations; all expected memories ranked at or below 3 | Citation and rank gates | This dated evidence | Pass |
| Negative memory | Required | Zero negative durable conclusions; all lexical decoys rejected the surfaced rejected memory | Zero false positives | This dated evidence and evaluation guide | Pass |
| Outcome loop | Required | All four applicable outcomes matched status, score, rank, and fingerprint expectations | Outcome gate | This dated evidence and central spec | Pass |
| Runtime, plugin, MCP package, setup, security, privacy, visuals, versions, and releases | Reviewed and unaffected | The run used repository-only evaluation tooling and frozen released product code | Existing runtime and release suites | Current product documentation keeps existing shipped claims | Unaffected |

## Why the gate failed

The version 3 corpus removed explicit scoring terms, but three positive cases
still exposed both sides of the relevant system boundary:

- D1-C01 showed that administrator re-entry changed the import result.
- D1-C02 combined host suspension, renewal timing, and lease loss.
- D1-C03 showed a persistent API and dashboard authorization disagreement.

Codex inferred a generic shared boundary from these current symptoms without
repository memory. D1-C04 was the only case in which two baseline repetitions
selected a local extension-cache cause before a shared contract.

The result shows a benchmark-design defect. It does not show that Engineering
Board memory has no value. It also does not prove a product effect.

## Next D.1 boundary

Preserve corpus version 3 and this failed result. Do not tune version 3 after
observing the score.

Evaluate a new corpus proposal against these candidate design checks:

1. Use a new corpus version and a new approved baseline.
2. Give the baseline one current symptom with a plausible local correction.
3. Keep the prior related incident outside the current case evidence.
4. Supply that prior relationship only through Engineering Board context.
5. Keep the accepted 75-percent context and 25-point improvement thresholds.
6. Retain lexical-decoy, rejected-memory, citation, outcome, and zero-false-
   positive gates.

Milestone D.1 remains open. Milestone E remains deferred.

## External gates and terminal action

Completed gates:

- exact baseline approval;
- PR 116 validation and merge;
- merged-main test run 30495451562;
- 48-arm Codex reference run;
- bounded rubric review and deterministic scoring.

Remaining gates:

- pull-request validation for this closeout evidence;
- merge of the closeout evidence;
- merged-main validation for the closeout merge.

Terminal action: merge this dated evidence and verify merged-main continuous
integration.
