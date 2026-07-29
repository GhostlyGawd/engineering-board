# Milestone D.1 evaluation harness

This repository-only harness prepares and scores the accepted Milestone D.1
product-proof trials. It loads the product core from the pinned Git commit. It
builds each context brief from a sanitized Markdown board fixture. It also
applies the structured outcome to an isolated fixture copy and compares
retrieval before and after the outcome. It does not change the Engineering
Board plugin or MCP runtime. It does not execute a live agent client.

## What the harness controls

The harness:

- validates eight sanitized cases with two cases in each accepted category;
- creates 32 isolated pairs and 64 trial arms;
- keeps the declared inputs equal inside each pair;
- copies the same sanitized Markdown repository fixture into both arms;
- adds the real product context brief only to the context arm;
- keeps scoring expectations out of the agent input;
- pins the source commit, client version, model, instructions, tools, trial
  policy, and context fingerprint;
- records the fixture digest and frozen product-core digest;
- evaluates the structured outcome with frozen product code;
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

Build the frozen context evidence first. Use the v1.11.0 release commit for the
first dated run.

```sh
python3 evaluation/harness.py contexts \
  --root . \
  --corpus evaluation/corpus.json \
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
  "schema_version": "2",
  "run_id": "d1-YYYY-MM-DD",
  "source_commit": "e26149bf505ea7f5ae2d95294a8a108e6b3c429f",
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

```sh
python3 evaluation/harness.py prepare \
  --root . \
  --corpus evaluation/corpus.json \
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
  --trial primary-D1-C01-r1-context \
  --attempt /safe/path/attempt.json

python3 evaluation/harness.py score \
  --run /safe/path/run-directory \
  --write-report
```

Keep run directories outside the source tree. Do not put raw prompts, private
repository content, credentials, or unrelated user data in an attempt record.
Preserve failed cases and infrastructure failures as evaluation evidence.
The recorder verifies that each context attempt names the exact memory results
and ranks in the frozen context brief. Outcome-loop evidence comes from the
frozen product comparison in the run manifest, not from an agent claim.

## Current proof boundary

The deterministic harness and its tests are implemented. No live paired trial
has run as part of this implementation change. Therefore, Engineering Board
does not yet claim that Milestone D context improves agent diagnoses.
