# Milestone D.1 evaluation harness

This repository-only harness prepares and scores the accepted Milestone D.1
product-proof trials. It keeps a development calibration corpus and an
unlocked proposal corpus separate from the locked evidence corpus. A proposal
can pass structural validation, but it cannot enter a scored run. The harness
loads the product core from the pinned Git
commit. It builds each context brief from a sanitized Markdown board fixture.
It also applies the structured outcome to an isolated fixture copy and
compares retrieval before and after the outcome. It does not change the
Engineering Board plugin or MCP runtime. It does not execute a live agent
client.

## What the harness controls

The harness:

- validates eight sanitized cases with two cases in each accepted category;
- identifies each corpus by role, version, digest, and lock state;
- rejects a calibration or proposal corpus as input to a scored run;
- rejects declared scoring-oracle leakage from positive evidence cases;
- creates 24 required reference pairs and 48 trial arms;
- keeps the declared inputs equal inside each pair;
- copies the same sanitized Markdown repository fixture into both arms;
- adds the real product context brief only to the context arm;
- keeps scoring expectations out of the agent input;
- pins the source commit, client version, model, instructions, tools, trial
  policy, and context fingerprint;
- records the fixture digest and frozen product-core digest;
- evaluates the structured outcome with frozen product code;
- requires each lexical-decoy context to retrieve its rejected memory;
- permits one replacement only after a recorded pre-score infrastructure
  failure;
- blocks every retry after a scored result;
- scores reference positive cases separately from negative-case false positives;
- reports optional replication profiles without adding them to the product gate;
- writes bounded JSON and Markdown reports.

For corpus version 4 and later, validation also requires one visible current
domain, one current incident, at least one prior incident that appears only in
the expected memory, and a cross-incident scoring contract. A diagnosis that
states only a rule inside the current component is local for this bounded
product-effect test.

For corpus version 4 and later, the reported corpus digest binds the JSON
contract, all canonical case-evidence files, and the complete context fixture.
A change to any of these inputs changes the digest.

The positive-case denominator contains the recurring-bug and cross-domain
shared-cause cases. Each reference arm has 12 positive trials. Lexical-decoy and
independent-issue cases use the separate zero-durable-conclusion gate.

## Validate the corpus

```sh
python3 evaluation/harness.py validate \
  --root . \
  --corpus evaluation/evidence-corpus.json
```

Use `evaluation/calibration-corpus.json` to develop and test benchmark
structure. It preserves the saturated cases from the first Codex run. The
prepare command refuses this corpus because calibration cases cannot produce
product-effect evidence.

Validate the unlocked version 4 proposal separately:

```sh
python3 evaluation/harness.py validate \
  --root . \
  --corpus evaluation/corpus-v4-proposal.json
```

## Prepare a run

Build the frozen context evidence first. Use the v1.11.0 release commit for the
first dated run. The local Git object database must contain that commit. Use a
full-history checkout for continuous integration.

```sh
python3 evaluation/harness.py contexts \
  --root . \
  --corpus evaluation/evidence-corpus.json \
  --source-commit e26149bf505ea7f5ae2d95294a8a108e6b3c429f
```

Copy the returned context fingerprints into a run configuration outside the
source tree. Use the exact live-client values for the dated evidence run.
Set both instructions hashes to the SHA-256 digest of
`evaluation/operator-instructions.md`. Set both tools hashes to the SHA-256
digest of `evaluation/tool-contracts.json`. Require each client response to conform to
`evaluation/trial-response.schema.json`.

```json
{
  "schema_version": "3",
  "run_id": "d1-YYYY-MM-DD",
  "source_commit": "e26149bf505ea7f5ae2d95294a8a108e6b3c429f",
  "trial_policy": "d1-client-neutral-v2",
  "profiles": {
    "reference": {
      "client_version": "exact-version",
      "model_identifier": "exact-model",
      "instructions_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
      "tools_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
    }
  },
  "context_fingerprints": {
    "D1-C01": "ctx-replace-with-16-hex",
    "D1-C02": "ctx-replace-with-16-hex",
    "D1-C03": "ctx-replace-with-16-hex",
    "D1-C04": "ctx-replace-with-16-hex",
    "D1-C05": "ctx-replace-with-16-hex",
    "D1-C06": "ctx-replace-with-16-hex",
    "D1-C07": "ctx-replace-with-16-hex",
    "D1-C08": "ctx-replace-with-16-hex"
  }
}
```

The `context_fingerprints` object must contain all eight case identifiers. The
prepare command fails if a configured value differs from frozen product
output.

The repository contract uses Codex as the required reference client. A dated
contract can add one or more `replication` profiles for other clients. Each
replication must use the same paired-trial rules and pinned inputs. A
replication result does not change the reference product gate. A provider
account is not required unless an operator elects to run that provider as a
replication.

```sh
python3 evaluation/harness.py prepare \
  --root . \
  --corpus evaluation/evidence-corpus.json \
  --contracts evaluation/client-contracts.json \
  --config /safe/path/run-config.json \
  --output /safe/path/run-directory
```

The command refuses an existing output or a linked output path. It creates one
`input.json` file in each isolated workspace. Context inputs contain the
product result, source references, and product fingerprints. They do not
contain the expected memory, rejected-memory list, expected cause, or scoring
contract. A separate authorized operator must run the pinned client and record
its structured result.

## Record and score evidence

```sh
python3 evaluation/harness.py record \
  --run /safe/path/run-directory \
  --trial reference-D1-C01-r1-context \
  --attempt /safe/path/attempt.json

python3 evaluation/harness.py score \
  --run /safe/path/run-directory \
  --write-report
```

Keep run directories outside the source tree. Do not put raw prompts, private
repository content, credentials, or unrelated user data in an attempt record.
Preserve failed cases and infrastructure failures as evaluation evidence.
For a custom proposal preflight outside a prepared harness run, create an
exclusive start receipt before each arm and append an end receipt after the
process exits. Bind the exact arguments and prompt, schema, runner, response,
and stream hashes. Record the process exit code. Refuse an arm when its start
receipt already exists. A post-run manifest cannot prove exit status or the
absence of an earlier deleted attempt.
The recorder verifies that each context attempt names the exact memory results
and ranks in the frozen context brief. Outcome-loop evidence comes from the
frozen product comparison in the run manifest, not from an agent claim.

## Current proof boundary

The deterministic harness and its tests are implemented. The first dated
Codex run produced a 100 percent positive-case rate in both the baseline and
context arms. Those cases now form the calibration corpus and cannot be used
for a scored run. The locked evidence corpus withholds the prior cross-session
or cross-domain relationship from agent-visible evidence. Its positive cases
also record a plausible local correction in scoring-only data. The locked
corpus reference run produced a 100 percent context rate and an 83.33 percent
baseline rate. The 16.67-point improvement failed the required 25-point gate.

The unlocked version 4 proposal keeps one current incident visible and places
the prior incident relationship in Engineering Board memory. A non-scored
positive-case preflight used four baseline and four context arms. The preflight
found no cross-incident diagnosis in either arm. The frozen v1.11.0 product
ranked each expected memory within the first three results, but it omitted the
hypothesis title, proposed cause, and bounded summary.

Context contract version `2` corrected that product-information boundary.
Current contract version `3` preserves the stable title and typed bounded
summary and adds matched-memory confidence.

A current-source, one-repetition preflight then ran the four positive version 4
cases once in baseline and context arms. Every expected memory ranked first or
second. Strict review found zero cross-incident-before-local first causes in
both arms, for an observed change of zero percentage points. The context
responses did not explicitly connect the visible incident to the prior
incident. The result does not distinguish a stable product limitation from
one-sample model variation or an operator-output limitation.

Engineering Board does not claim that Milestone D context improves agent
diagnoses. Version 4 remains an unlocked proposal. Its exact corpus digest and
the draft structured-requirement digest are recorded in the current dated
preflight evidence for product-owner review. Do not prepare a scored run before
that approval. See
[`2026-08-16 Milestone D.1 version 4 current-source preflight`](../docs/evidence/2026-08-16-milestone-d1-v4-current-preflight.md).
