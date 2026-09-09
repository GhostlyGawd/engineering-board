# Free-only design plugin canary fixture pack v1

This retained synthetic pack prepares lane-specific evaluation of design workflows. It does not install a plugin, call an external service, run an arm, create a paid account, or publish a site. Read `protocol.md` before use. Blinded reviewers must not open `sealed/` before their scores are locked.

From the repository root, validate content, regenerate the complete sorted checksum inventory after any accepted change, and verify it:

```sh
python3 evaluation/design-plugin-canary-v1/scripts/validate_pack.py --skip-checksums
find evaluation/design-plugin-canary-v1 -type f ! -name SHA256SUMS ! -path '*/__pycache__/*' -print \
  | LC_ALL=C sort \
  | while IFS= read -r file; do shasum -a 256 "$file"; done \
  > evaluation/design-plugin-canary-v1/SHA256SUMS
shasum -a 256 -c evaluation/design-plugin-canary-v1/SHA256SUMS
python3 evaluation/design-plugin-canary-v1/scripts/validate_pack.py
python3 -m unittest discover -s evaluation/design-plugin-canary-v1/scripts -p 'test_*.py' -v
cd evaluation/design-plugin-canary-v1/fixture-workspace
npm ci --ignore-scripts --no-audit --no-fund
npm test
npm run build
```

The standard validator checks the inventory. `--skip-checksums` exists only to validate content before regenerating `SHA256SUMS` or to exercise isolated adversarial mutations in tests.

Execution remains blocked until a successor evaluation entry names the retention owner; an independent verifier passes content, sealed keys, scoring math, and checksums; exact candidate bytes and package hashes are retained; the Codex model/reasoning configuration is pinned; native ImageGen availability is checked; and each applicable non-native capability has a current valid zero-cost receipt. Conditional unpinned arms remain excluded until their stated activation prerequisites are satisfied.

Create an isolated worker bundle outside the repository and give the evaluated agent access only to that directory:

```sh
python3 evaluation/design-plugin-canary-v1/scripts/materialize_worker_bundle.py \
  --task C3 \
  --output /absolute/new/path/C3-worker-bundle
```

Aggregate a completed lane only after score records are locked:

```sh
python3 evaluation/design-plugin-canary-v1/scripts/aggregate_scores.py \
  --input /absolute/path/to/lane-scores.json \
  --output /absolute/path/to/lane-result.json
```
