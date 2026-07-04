---
id: B021
type: bug
title: code-reviewer name collides with /code-review and its tools contradict its read-only contract
discovered: 2026-07-04
status: open
priority: P3
affects: agents/code-reviewer.md
needs: tdd
pattern: [naming, contract-mismatch]
---

## Done when
- The discipline agent is renamed to avoid confusion with the harness `/code-review` and `/review` skills, OR the collision is documented; and its tool list drops Write/Edit to match its "no file writes" contract (like validator).

## Observed behavior (Track B F12)
`code-reviewer.md:6` lists Write/Edit though the contract forces `test_files_added`/`impl_files_changed` to `[]`. Name collides conceptually with `/code-review`.
