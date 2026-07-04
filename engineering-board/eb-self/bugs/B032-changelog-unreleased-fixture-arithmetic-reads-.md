---
id: B032
type: bug
title: CHANGELOG Unreleased fixture arithmetic reads as a contradiction (50 vs 36+24)
discovered: 2026-07-04
status: open
priority: P3
affects: CHANGELOG.md
needs: tdd
pattern: [doc-drift]
---

## Done when
- The CHANGELOG [Unreleased] reject-filter paragraph no longer juxtaposes "(36)"+"(24)"=60 with "the 50-fixture corpus" without qualification (e.g. "the then-50-fixture corpus" or "60-fixture corpus (now)").

## Observed behavior (C2 Track D — LOW)
`CHANGELOG.md:30-36` gives 36 adversarial + 24 benign but calls it "the 50-fixture corpus." 50 is historically correct (C1 added 10) but reads as bad arithmetic next to 36+24.
