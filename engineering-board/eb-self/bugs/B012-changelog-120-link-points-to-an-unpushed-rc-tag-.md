---
id: B012
type: bug
title: CHANGELOG 1.2.0 link points to an unpushed rc tag (likely 404)
discovered: 2026-07-04
status: open
priority: P3
affects: CHANGELOG.md
needs: tdd
pattern: [doc-drift]
---

## Done when
- `CHANGELOG.md`'s `[1.2.0]` link points at a resolvable target (the merge commit / compare view / `v1.2.0` once cut), not `v1.2.0-rc.1` which is not pushed.

## Observed behavior (Track D F5)
`CHANGELOG.md:90` → `.../releases/tag/v1.2.0-rc.1`. state.md:22 notes tag pushes are rejected by the sandbox relay (human-gated), so the tag does not exist remotely — wrong version anchor and a live 404.
