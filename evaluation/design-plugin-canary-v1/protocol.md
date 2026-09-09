# Design plugin canary protocol v1.0.0

Status: frozen preparation protocol. The pack revision is the containing Git commit recorded by the F006 lead. No live arm may run until that committed revision exists, an independent verifier passes it from a fresh clone, the retention owner is named on the successor execution entry, candidate bytes are retained, and every applicable eligibility precondition passes.

Source contract: `docs/evidence/2026-09-09-codex-design-plugin-landscape.md`, SHA-256 `3356a15322afcaaebb3cc7d96af2ba0107a6c0e1f4917532282f4731a4c76143`. Product-owner approval recorded in F006 on 2026-09-09.

## Frozen thresholds

- Plan exactly three independent replicates for every applicable arm/task pair. Score each replicate independently and retain failures as zero. Only a prespecified, unrelated local-infrastructure failure may be retried.
- An arm advances only when its normalized lane score is at least 75/100 and it improves by at least 5 normalized points over its matched baseline.
- One failed replicate prevents advancement, even if the median and normalized score pass.
- Any security, accessibility, cost, or evidence hard-gate failure prevents advancement.
- Median elapsed time may regress by no more than 20% against the matched baseline unless the arm wins a prespecified unavailable capability.
- C4 must score at least 70% in workflow and editable-canvas lanes. C6 must score at least 70% in the editable-canvas lane. C2 must score at least 80% in the brand lane. QA augmentation must introduce no deterministic regression.
- Do not compute or publish a cross-lane winner. Mark non-applicable dimensions `N/A`.

## Lane map

| Lane | Opaque arms | Matched baseline | Tasks | Raw denominator |
|---|---|---|---|---:|
| workflow-code-native | arm-a17, arm-b42, arm-c08, arm-d31; optional arm-e59 | arm-a17 | C1, C2, C3, C4, C5 | 90 |
| editable-canvas | arm-f24; conditional arm-g73; winning workflow arm as reference | winning workflow arm | C1, C2, C4, C6 | 85 |
| free-brand-assets | arm-a17, arm-b42; conditional arm-j11 | arm-a17 | C1, C2 | 35 |
| qa-augmentation | winning workflow arm and arm-k90 overlay | winning workflow arm without overlay | C4, C5 | 40 |

The sealed identity map is `sealed/arm-map.json`. Blinded reviewers must not open it until all independent scores and pairwise preferences are locked. Operations/security review is unblinded.

Evaluated agents receive only worker bundles created by `scripts/materialize_worker_bundle.py`. The bundle contains the task's public inputs and runnable workspace, with sealed answer-key/rubric fields and paths removed. The pack root, `sealed/` directories, scorer files, other task fixtures, and answer keys must be unavailable inside the evaluated agent's filesystem and tool scope. Operators must hash and retain each bundle before a run.

## Fixed controls

All Codex arms use one base commit, pinned model snapshot, reasoning effort, wall-clock ceiling, tool-call ceiling, token ceiling, isolated worktree, browser profile, and fresh design/service project. No memory or outputs carry between runs. Native Codex ImageGen using `gpt-image-2` is fixed identically across applicable matched arms.

Never set or read `OPENAI_API_KEY`; never call the paid Image API; never purchase capacity; never publish with Sites; never use a paid connector, hosted visual-regression service, paid accessibility service, paid seat, subscription, add-on, converting trial, commercial-license trigger, or paid hosting. External quota exhaustion, a paywall, billing prompt, or upgrade prompt fails and stops that arm. Normal included Codex/ImageGen exhaustion pauses or defers the complete affected matched set.

Only synthetic fixtures in this pack may be used. Customer data, production data, proprietary production design systems, credentials, session cookies, payment details, and unsanitized browser profiles are prohibited.

Before worker execution, the operator may run `npm ci` only from the retained exact `fixture-workspace/package-lock.json` and may install the matching Playwright browser binary for local fixture verification. This is approved free fixture setup, not an arm capability. Package drift, lockfile updates during a run, remote runtime assets, and hosted QA services are prohibited. The workspace uses retained shadcn-compatible local components and does not require the shadcn CLI or runtime package.

## Review and aggregation

Two blinded reviewers score every human-judged item. Their scores are averaged only when every item differs by at most two points on a ten-point-equivalent scale and their required pairwise preferences agree. They also record pairwise preference against the matched baseline for C1, C2, and C4 visual fidelity. A greater item difference or conflicting pairwise preference triggers a third blinded adjudicator, whose complete replicate score replaces the two primary scores. AI judgments may be retained only as exploratory data.

For each task, take the median of the three replicate scores. Sum applicable task medians and normalize against the lane denominator. Report all raw replicate scores, median, failures, elapsed time, token/tool use, and included/free-quota consumption. Automated accessibility output does not establish conformance, and automated output alone cannot earn more than 8/15 on C5.

## Evidence and retention

Retain prompts, logs, stdout/stderr, receipts, screenshots at every required viewport, accessibility output, code and dependency diffs, editable-canvas receipts, input/output hashes, reviewer sheets, and the final report for at least 12 months after the adoption decision. Early removal requires a recorded product-owner decision. Every off-repository artifact needs a durable URI, retention expiry, owner, byte size, and SHA-256, and a verifier must retrieve and hash it.

Before scoring, an independent verifier must retrieve the exact commit from a fresh clone, verify `SHA256SUMS`, open at least one render and one machine-readable result from every arm/task, inspect all sealed keys and scoring math, and record the result in `report.md`.

For the editable-canvas arm, the Penpot version must be at least 2.15.0 and the observed listener host must be exactly `127.0.0.1` or `::1`. Retain the listener inspection command, complete output, UTC timestamp, and output SHA-256. A wildcard, public, hostname alias, or unrecorded listener fails the security gate.
