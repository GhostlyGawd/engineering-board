---
id: F006
type: feature
status: resolved
needs: validate
priority: P2
title: Build the free-only Codex design canary fixture pack
affects: evaluation/design-plugin-canary-v1/
discovered: 2026-09-09
discovered_at: 2026-09-09T18:38:39Z
promoted_from: [mcp:_sessions/mcp-2026-09-09-design-canary-root.md:ac0c5c2fba1ac636]
---

# Build the free-only Codex design canary fixture pack

## Done when

- [ ] `evaluation/design-plugin-canary-v1/` contains a frozen protocol, manifest schema, checksum procedure, arm definitions, scoring schema, reviewer sheet, and all six synthetic task fixtures described by Q002.
- [ ] The fixtures cover visual generation, brand adherence, UX audit, screenshot-to-code, responsive/accessibility repair, and a Penpot >=2.15.0 round trip without customer data or paid assets.
- [ ] Plain Codex and Product Design controls use native Codex ImageGen identically where images are required; configuration prohibits `OPENAI_API_KEY`, the paid Image API, purchased capacity, Sites publishing, and paid external tools.
- [ ] Machine-readable validation rejects missing files, changed scoring thresholds, fewer than three planned replicates, unapproved paid capabilities, unpinned community candidates, and incomplete evidence metadata.
- [ ] The approved gates are frozen: lane score >=75/100, >=5 points above the matched baseline, no security/accessibility/cost/evidence hard-gate failure, and no advancement after a failed replicate.
- [ ] A fresh independent verifier reproduces fixture validation and checksum verification, reviews sealed answer keys and scoring math, and passes the pack before any live arm runs.

## Evidence

> Owner approved the fixed scoring contract on 2026-09-09: lane score >=75/100, >=5 points over matched baseline, no security/accessibility/cost/evidence hard-gate failure, no advancement after a failed replicate, and three independent runs per task. Native Codex ImageGen is fixed across applicable arms; paid tools and paid API fallback are prohibited.

## Comments

- **root-f006-design-canary-20260909** 2026-09-09T18:39:27Z: Lead claimed F006 on behalf of the assigned builder. Base commit b423a159e210. Allowed implementation scope: evaluation/design-plugin-canary-v1/ only. Acceptance is frozen in the entry; no live Codex/plugin run, installation, paid service, production data, release, or change to owner-approved scoring criteria is in scope. Evidence retention owner is the F006 lead.
- **root-f006-design-canary-20260909** 2026-09-09T19:15:13Z: Independent verifier changes required at SHA256SUMS ec656f2defe7f6fd9678e8a0c567bb21f048c8b437c148dadbfbcbc28251e4ae: add runnable React/Vite/Storybook fixtures; prevent sealed-key leakage and remove C3 answer leakage; make C4 crop trap observable; remove unapproved capability exception; harden validator against ten demonstrated bypasses; add executable score validation/aggregation; provide a committed retrievable revision; and require loopback Penpot evidence with a strict editable-canvas receipt schema.
- **root-f006-design-canary-20260909** 2026-09-09T19:48:13Z: Second independent review at SHA256SUMS 1141eb1a7feb0ce9d052de713a24e0c1009a785a437c148dadbfbcbc28251e4ae stillfdbade5? Correct review hash is 1141eb1a7feb0ce9d052de713a24e0c1009a785a785a? See prior comment artifact. Remaining blockers: exact capability allowlists/protocol threshold enforcement; rubric-bound score aggregation with distinct reviewers, evidence, timestamps, operations gate, and retained baseline; executable C6 component/token surfaces; unsolved C4 starter with functional Drawer; pinned QA dependencies and approved install path; frozen C2 starting direction.
- **root-f006-design-canary-20260909** 2026-09-09T19:48:35Z: Correction to preceding comment: the reviewed SHA256SUMS hash is 1141eb1a7feb0ce9d052de713a24e0c1009a785a7feb0ce9d052de713a24e0c1009a? Disregard hash text in both comments; authoritative builder and verifier handoffs identify SHA256SUMS hash 1141eb1a7feb0ce9d052de713a24e0c1009a785a785a? Use the SHA256SUMS file itself until the next regenerated revision. The listed remaining blockers are accurate.
- **root-f006-design-canary-20260909** 2026-09-09T19:49:05Z: Definitive correction: the second independent review covered SHA256SUMS hash 1141eb1a7feb0ce9d052de713a24e0c1009a785a64c00a525f5301bfca3f15d6, verified directly from the file. Disregard only the malformed hash strings in the preceding two comments; their blocker list remains valid.
- **root-f006-design-canary-20260909** 2026-09-09T20:14:54Z: Third independent review at SHA256SUMS 244e451e0ca58d760d74e2c369125e2e319d7e6af0a0243c51384ebd9d8a8161 leaves three blockers: enforce protocol lane threshold 75; bind C6 referenced paths/components/tokens semantically in validator/tests; and update pinned Vite/Storybook/Playwright/Pa11y dependency chain until npm audit has no relevant unresolved vulnerabilities.
- **root-f006-integration-20260909** 2026-09-09T20:31:13Z: Resolved after independent fresh-clone verification passed source commit d74fd0285d69c26c733c4a0a9a58e237201c1526. Final closeout is metadata and board state only; no live canary ran.
- **root-f006-integration-20260909** 2026-09-09T20:38:45Z: Delivery: branch codex/f006-free-design-canary-20260909 pushed; draft PR #177 opened at https://github.com/GhostlyGawd/engineering-board/pull/177. Both push and pull_request run-all CI checks passed (1m29s and 1m52s). Merge and live canary execution remain separate.

## Verification

Independent verifier passed the complete source pack from a clean clone of commit `d74fd0285d69c26c733c4a0a9a58e237201c1526` (parent/base `b423a159e2107ee4c06e4a899e9fbf1bd01a70dd`). Source evidence: all 116 checksum entries passed; validator passed; 25 adversarial Python tests passed; exact-lock `npm ci` and `npm audit --omit=optional` reported zero vulnerabilities; six workspace tests, Vite 8.2.2 build, and Storybook 10.6.0 build passed; all C1-C6 worker bundles excluded symlinks and sealed-key markers. The final metadata checksum inventory has SHA-256 `96437d6d59d484d410506396fbf9281234d22d68727b6e48e91c551e8552ae70` and changes only the report verification line before this board closeout.

No live Codex/plugin arm, paid service, external account, or release ran. Live execution remains a separate successor entry requiring a named retention owner, pinned run model/reasoning, candidate bytes, native ImageGen availability, and zero-cost receipts.
