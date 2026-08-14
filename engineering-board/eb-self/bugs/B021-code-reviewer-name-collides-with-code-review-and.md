---
id: B021
type: bug
title: code-reviewer name collides with /code-review and its tools contradict its read-only contract
discovered: 2026-07-04
status: resolved
priority: P3
affects: agents/code-reviewer.md
needs: validate
pattern: [naming, contract-mismatch]
---

## Done when
- The discipline agent is renamed to avoid confusion with the harness `/code-review` and `/review` skills, OR the collision is documented; and its tool list drops Write/Edit to match its "no file writes" contract (like validator).

## Observed behavior (Track B F12)
`code-reviewer.md:6` lists Write/Edit though the contract forces `test_files_added`/`impl_files_changed` to `[]`. Name collides conceptually with `/code-review`.

## Comments

- **codex** 2026-08-14T13:22:33Z: Claimed for a dogfood pass focused on the reviewer name collision and the read-only tool contract.
- **codex** 2026-08-14T13:30:38Z: Red/green discipline test complete. Focused mode, routing, prompt-lint, board-run, and full 20-suite validation pass. Merged-main and closeout evidence remain pending.

## Resolution evidence

- The internal worker keeps its registered routing identity and explicitly distinguishes itself from the harness `/code-review` and `/review` skills.
- Its tool grant is `Read, Bash, Grep, Glob`; `Write` and `Edit` are absent.
- The focused discipline test passes 47 checks. The maintained suite passes 20 of 20 suites.
- Pull request #128 merged as `c06d6bd`; merged-main run 31808165945 passed.
