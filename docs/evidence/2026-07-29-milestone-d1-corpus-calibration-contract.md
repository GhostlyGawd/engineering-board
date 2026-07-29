# Milestone D.1 corpus-calibration contract

Date: 2026-07-29

State: Product-owner baseline accepted. Reference run complete.

Completion state: `closeout-pending`

Evidence corpus:

- Identifier: `d1-product-effect`
- Version: `3`
- Role: `evidence`
- Lock state: locked
- Digest:
  `sha256:e8756040e5c6b9c1f9f40e7b47cc17cf196d59e605234fd0c67796a24da6b956`

Structured requirement digest:
`sha256:482579893a8c16adf2e16e2cf06397895d71d49d514ca48961bef9e6b90e5c24`

The structured requirement checker reports
`BASELINED — AUTHORIZED APPROVAL RECORDED`. The product-owner approval matches
the exact digest above.

## Product decision

The saturated first-run cases are a calibration set. They cannot produce
scored product-effect evidence. A separate locked evidence corpus controls the
next Codex reference run.

The design must create a real information difference. It must not tune wording
only to force a lower baseline score. Each positive baseline case has enough
information for a plausible local correction. Engineering Board context adds
the prior repository relationship that supports a shared-cause investigation.

## Source transformation

The product owner approved these source transformations:

1. “Diagnose why the baseline was too easy” becomes an explicit calibration
   corpus that preserves the saturated cases.
2. “Create a separate calibration set” becomes distinct `calibration` and
   `evidence` corpus roles.
3. “Build a locked eight-case evidence corpus” becomes versioned corpus
   metadata and a scored-run lock gate.
4. “Ensure only Engineering Board memory connects the evidence” becomes
   scoring-only information-gap, local-correction, and oracle-term fields plus
   deterministic leakage checks.
5. “Add adversarial validity tests” becomes calibration rejection, visible-
   oracle rejection, and rejected-memory retrieval tests.
6. “Freeze and run Codex” becomes a post-merge reference run against the exact
   evidence-corpus digest.

No provider account, production runtime change, hosted service, SQLite,
embedding system, or Milestone E behavior is added.

## Alignment

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| Calibration and evidence separation | Required | Schema 3 corpus roles and separate JSON files | Calibration corpus validates but scored preparation rejects it | Central spec, evaluation guide, README, roadmap, architecture | Accepted |
| Locked scored input | Required | `prepare_run` accepts only locked `evidence` role | Calibration rejection and normal preparation tests | Evaluation guide | Accepted |
| Positive-case information boundary | Required | Scoring-only information gap, plausible local correction, and oracle terms | Visible expected cause, memory ID, and oracle terms fail validation | Central spec and evidence corpus | Accepted |
| Negative-memory behavior | Required | Lexical decoys use misleading pattern labels and declared rejected memories | Frozen context must retrieve each rejected memory within the first three results | Central spec and corpus cases | Accepted |
| Corpus identity and reproducibility | Required | Manifest records corpus ID, version, and digest | Preparation test inspects manifest metadata | Architecture and evaluation guide | Accepted |
| Reference product-effect run | Required post-merge evidence | Codex reference profile, 24 pairs, 48 arms | Scorer gates and dated live evidence | Calibrated reference-run evidence | Complete; improvement gate failed |
| Historical saturated run | Historical | Preserved without rewrite | Dated report remains unchanged | Calibration corpus and prior evidence | Preserved |
| Runtime, plugin, MCP package, setup, security, privacy, visuals, versions, and releases | Reviewed and unaffected | Evaluation-only files do not enter shipped bundles or runtime paths | Existing release and runtime suites | Current product documentation retains existing runtime claims | Unaffected |

## Verification

The focused evaluation suite must pass all 17 tests. The complete repository
suite must pass. The requirements checker must report no deterministic
requirement-quality defect. Pull-request and merged-main continuous integration
must pass.

The post-merge Codex reference run must:

- use the exact locked corpus digest above;
- use three paired repetitions for all eight cases;
- preserve all scored and failed attempts;
- publish the reference baseline rate, context rate, difference, retrieval
  rank, citation coverage, false-positive count, and limitations.

## External gates and terminal action

External gates:

- product-owner approval of the exact requirement digest: satisfied;
- pull-request continuous integration: satisfied for PR 116;
- merged-main continuous integration: satisfied by run 30495451562;
- completion of the Codex reference run: satisfied;
- review and merge of dated closeout evidence.

Evidence destination:
`docs/evidence/2026-07-29-milestone-d1-calibrated-reference-run.md`

Terminal action: merge the closeout evidence after all named gates pass. Keep
the milestone open until that merge and its merged-main continuous integration
complete.
