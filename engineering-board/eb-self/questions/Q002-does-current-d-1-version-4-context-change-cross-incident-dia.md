---
id: Q002
type: question
title: Does current D.1 version 4 context change cross-incident diagnosis?
discovered: 2026-08-16
status: resolved
source: Authorized recursive dogfood against the accepted Milestone D.1 product-proof contract.
affects: evaluation/
---

## Done when

- [x] The unlocked version 4 proposal validates and its context briefs rebuild from exact current main.
- [x] Four positive cases run once in baseline and context arms with equal pinned client, model, instructions, tools, and isolation controls.
- [x] A bounded review classifies cross-incident-before-local outcomes, preserves every response, and reports expected-memory ranks and infrastructure failures without a scored product claim.
- [x] The exact corpus and requirement digests are presented for owner baseline review; the corpus remains unlocked and no scored run starts.

## Finding

No observed change in the strict cross-incident-before-local metric. Baseline
and context each produced zero qualifying first causes across four positive
cases. Each context arm received its expected memory within rank two, but no
first stated cause connected the current incident to its prior incident. This
one-repetition proposal preflight is not a scored product-effect result.

Version 4 remains unlocked. Its corpus digest is
`ccdebc8be431047341bb13920d04fdc9a901e34664da6c90ed53f38be14ef662`.
The draft structured-requirement digest is
`9315bfd6889b0e1cbab6e9e864d0ffaf94a20c59606755cfceeb8cbcbef64ed2`.
The product owner still controls the exact baseline decision.

Detailed evidence: [`2026-08-16 Milestone D.1 version 4 current-source
preflight`](../../../docs/evidence/2026-08-16-milestone-d1-v4-current-preflight.md).

## Comments

- **goal-d1-v4-preflight-20260816** 2026-08-16T02:12:41Z: Claimed from exact main 80ba2c1. The unlocked v4 proposal validates with digest ccdebc8be431 and current context generation returns every expected memory within the first three. Running only the approved eight-arm non-scored preflight; no corpus lock or scored claim.
- **goal-d1-v4-preflight-20260816** 2026-08-16: Eight preserved isolated arms contain valid schema output, empty stderr, and no tool event. Strict primary and independent reviews agree on baseline 0/4 and context 0/4. One outer-shell launch failed before Codex started; inventory showed no response artifact, alignment was renewed, and the completed arms were not rerun. The live executor reported exit 0 for all eight completed arms, but the runner did not persist per-arm exit receipts or an append-only attempt ledger; the dated evidence keeps that limitation explicit.
- **goal-d1-v4-preflight-20260816** 2026-08-16T02:48:11Z: Resolved after evidence PR #160 merged as af82d41 and exact merged-main run 31922615107 passed. Strict result remains baseline 0/4 and context 0/4; version 4 stays unlocked and the owner baseline gate remains open.
