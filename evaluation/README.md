# Milestone D.1 evaluation harness

This repository-only harness prepares and scores the accepted Milestone D.1
product-proof trials. It does not change the Engineering Board plugin or MCP
runtime. It does not execute a live agent client.

## What the harness controls

The harness:

- validates eight sanitized cases with two cases in each accepted category;
- creates 32 isolated pairs and 64 trial arms;
- keeps the declared inputs equal inside each pair;
- adds the context brief only to the context arm;
- pins the source commit, client version, model, instructions, tools, trial
  policy, and context fingerprint;
- permits one replacement only after a recorded pre-score infrastructure
  failure;
- blocks every retry after a scored result;
- scores primary positive cases separately from negative-case false positives;
- writes bounded JSON and Markdown reports.

The positive-case denominator contains the recurring-bug and cross-domain
shared-cause cases. Each primary arm has 12 positive trials. Lexical-decoy and
independent-issue cases use the separate zero-durable-conclusion gate.

## Validate the corpus

```sh
python3 evaluation/harness.py validate \
  --root . \
  --corpus evaluation/corpus.json
```

## Prepare a run

Create a run configuration outside the source tree. Use real pinned values for
the dated evidence run.

```json
{
  "schema_version": "1",
  "run_id": "d1-YYYY-MM-DD",
  "source_commit": "0000000000000000000000000000000000000000",
  "trial_policy": "d1-gate2-v1",
  "profiles": {
    "primary": {
      "client_version": "exact-version",
      "model_identifier": "exact-model",
      "instructions_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
      "tools_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
    },
    "compatibility": {
      "client_version": "exact-version",
      "model_identifier": "exact-model",
      "instructions_sha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
      "tools_sha256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    }
  },
  "context_fingerprints": {
    "D1-C01": "replace-with-exact-fingerprint",
    "D1-C02": "replace-with-exact-fingerprint",
    "D1-C03": "replace-with-exact-fingerprint",
    "D1-C04": "replace-with-exact-fingerprint",
    "D1-C05": "replace-with-exact-fingerprint",
    "D1-C06": "replace-with-exact-fingerprint",
    "D1-C07": "replace-with-exact-fingerprint",
    "D1-C08": "replace-with-exact-fingerprint"
  }
}
```

The `context_fingerprints` object must contain all eight case identifiers.

```sh
python3 evaluation/harness.py prepare \
  --root . \
  --corpus evaluation/corpus.json \
  --contracts evaluation/client-contracts.json \
  --config /safe/path/run-config.json \
  --output /safe/path/run-directory
```

The command refuses an existing output or a linked output path. It creates one
`input.json` file in each isolated workspace. A separate authorized operator
must run the pinned client and record its structured result.

## Record and score evidence

```sh
python3 evaluation/harness.py record \
  --run /safe/path/run-directory \
  --trial primary-D1-C01-r1-context \
  --attempt /safe/path/attempt.json

python3 evaluation/harness.py score \
  --run /safe/path/run-directory \
  --write-report
```

Keep run directories outside the source tree. Do not put raw prompts, private
repository content, credentials, or unrelated user data in an attempt record.
Preserve failed cases and infrastructure failures as evaluation evidence.

## Current proof boundary

The deterministic harness and its tests are implemented. No live paired trial
has run as part of this implementation change. Therefore, Engineering Board
does not yet claim that Milestone D context improves agent diagnoses.
