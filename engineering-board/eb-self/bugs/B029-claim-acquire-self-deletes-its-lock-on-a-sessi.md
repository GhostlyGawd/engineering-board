---
id: B029
type: bug
title: claim-acquire self-deletes its lock on a session_id containing whitespace
discovered: 2026-07-04
status: open
priority: P2
affects: hooks/scripts/board-claim-acquire.sh
needs: tdd
pattern: [input-validation, silent-failure]
---

## Done when
- The claim read-verify compares the full `session_id` value (not just the first whitespace token), OR whitespace in session ids is rejected at entry.
- A test acquires a claim with a spaced session id and asserts success (exit 0), not false contention.

## Observed behavior (C2 red-team, F5 — MINOR)
`board-claim-acquire.sh:137-143` reads back `session_id` via `awk '{print $2}'` (first token only). A spaced SESSION_ID makes VERIFY_SESSION != SESSION_ID, so the script concludes its own write was clobbered, `rm -rf`s the claim dir it just created, and returns false contention (exit 1). Low impact (owner ids are usually opaque), but a spaced id silently makes claims un-acquirable.
