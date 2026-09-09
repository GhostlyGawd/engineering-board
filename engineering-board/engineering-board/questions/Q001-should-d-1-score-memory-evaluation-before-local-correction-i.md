---
id: Q001
type: question
status: resolved
title: Should D.1 score memory evaluation before local correction instead of first-cause adoption?
affects: evaluation/operator-instructions.md
discovered: 2026-09-09
discovered_at: 2026-09-09T04:56:20Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:3a66bf0b9179a0a1]
---

# Should D.1 score memory evaluation before local correction instead of first-cause adoption?

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> Q003 returned zero strict cross-incident first causes across raw/prose and before/after presentation. Every response noticed but declined to adopt proposed H104 because the current case did not establish it, then proposed a local correction. Earlier instruction-only and supporting-evidence probes were also insufficient. The current first-cause metric may reward premature adoption of unconfirmed memory instead of the safer behavior of explicitly evaluating it before a local fix.

## Related discoveries

- B003 — Claim acquisition reports false contention when an in-session plugin upgrade removes the running MCP process working directory. Fix B003 before resuming this question so it can be claimed through the normal workflow.

## Comments

- **codex-d1-memory-evaluation-20260909** 2026-09-09T05:05:39Z: Claimed after B003 fixed the in-session upgrade failure. Evaluate whether D.1 should reward explicit memory consideration before a local correction rather than unconfirmed first-cause adoption.
- **codex-d1-memory-evaluation-20260909** 2026-09-09T05:07:00Z: Resolved: explicit apply/hold/reject memory evaluation before local correction becomes the primary D.1 use gate; systemic first cause remains a secondary diagnostic.

## Finding

Yes. D.1 should score an explicit decision about retrieved memory before the first local correction instead of requiring an unconfirmed cross-incident hypothesis to become the first stated cause. The systemic-first-cause rate remains a separate, stricter diagnostic signal; it is not the primary memory-use gate.

A qualifying memory evaluation must identify the surfaced memory and its epistemic status, connect the named current and prior incidents, choose an explicit `apply`, `hold`, or `reject` disposition, and state the supporting evidence or information gap before proposing a local correction. `Apply` permits a systemic correction when evidence supports it. `Hold` permits an evidence-calibrated local correction while naming what would test the cross-incident claim. `Reject` records why the memory does not apply. None of these dispositions may silently promote a proposed hypothesis.

Q003 supports this decision: all four treatments noticed H104, preserved it as proposed, and declined to adopt it from one local symptom, but the first-cause-only gate counted that safe behavior as failure. The new gate measures whether repository memory changes the decision process without rewarding premature causal certainty.
