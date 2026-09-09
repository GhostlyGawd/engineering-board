---
id: B002
type: bug
title: Synthetic validator path drops capability marker
discovered: 2026-09-08
status: resolved
priority: P2
affects: tests/capability_lab/validator_b.py
needs: tdd
pattern: [capability-marker-loss]
pattern_ids: [P001]
---

## Done when

- [ ] Synthetic capability marker is preserved

## Comments

- **Codex** 2026-09-09T03:03:52Z: Blocked with owner confirmation on Q001; the affected synthetic file is absent and the preserved evidence does not assert a product defect.
- **codex-capability-q001-20260908** 2026-09-09T03:07:39Z: Unblocked after Q001 resolution and updated against its finding; this entry is ready only for terminal non-product disposition, not implementation.
- **codex-capability-b002-disposition-20260908** 2026-09-09T03:09:10Z: Resolved as a completed non-product capability artifact under Q001; no code change and no fix outcome.

## Q001 dependency

This synthetic probe is not implementation-ready. Q001 must determine the lifecycle/disposition for completed synthetic capability records before this entry is implemented or closed.

## Q001 finding (resolved 2026-09-09)

Q001 determined that this record is a completed synthetic capability probe, not an implementation defect. Its named fixture path does not exist, and its original marker-preservation criterion is superseded by the approved non-product terminal disposition. Do not create code to make this synthetic assertion true.

## Resolution evidence

Closed under the approved Q001 terminal-disposition finding. This was a completed synthetic capability record, its named fixture path never existed, and no product defect or marker-loss behavior was demonstrated. The original synthetic preservation criterion is superseded; no implementation was created and no product-effect claim is made.
