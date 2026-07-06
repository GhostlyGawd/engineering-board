---
id: B030
type: bug
title: Permission-install delivery is a 6-step copy-paste loop, undiscoverable from onboarding
discovered: 2026-07-04
status: resolved
priority: P2
affects: commands/board-install-permissions.md
needs: done
pattern: [onboarding, delivery-friction]
---

## Done when
- The permission-install path is either referenced from the Quickstart (see B027) and/or its delivery is simplified (fewer manual steps), while preserving the interactive-by-design safety model.

## Observed behavior (C2 Track B — P2)
B004 fixed allowlist COVERAGE, but DELIVERY is still high-friction: self-check → display → type YES → paste ~17 `claude config add` lines into a separate terminal → re-run to confirm. It's the gate that unlocks the no-prompt autonomous loop, yet is unreferenced from onboarding and cannot be completed inside the Claude session. Distinct from B004 (coverage) — this is delivery/discoverability.
