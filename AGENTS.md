# Repository agent instructions

## Development team

Follow [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for maintainer product work.
Use a lead, a builder, and an independent verifier with one accountable owner
per board entry. Delegate bounded review and implementation assignments when
they can progress independently. Record scope and acceptance criteria before
implementation; review substantive changes in a fresh agent context.
Existing user authorization covers routine implementation and delivery. Changes
to product goals or evaluation success criteria require a concrete owner decision.
The lead records evidence and resolves entries only after the required review.

## Release work

For Engineering Board release work, read these files before you change a
version, checksum, tag, release, or publication:

1. `maintainers/skills/release-engineering-board/SKILL.md`
2. `docs/RELEASING.md`

Use `scripts/prepare-release.py` for the coordinated release change. Do not
change one versioned surface independently.

Do not use the maintainer release skill in a repository that only installs the
Engineering Board plugin.

The owner approved the current controlled-English text. Do not claim formal
ASD-STE100 compliance without a separate qualified verification.

<!-- engineering-board:start -->
## engineering-board

This repo tracks its work on a markdown board under `engineering-board/`
(bugs, features, questions, observations, learnings, and hypotheses).
`BOARD.md` is a derived index; never edit it by hand, the tools rebuild it.
If you can call the engineering-board MCP tools, use the board:

- Capture findings as you notice them: `board_capture_finding` (project, kind, title).
- List actionable work: `board_list_entries` with `ready: true`.
- Claim an entry BEFORE working on it: `board_claim` (project, entry_id, session_id).
- Record progress on the entry: `board_update_entry` (status, needs, comment).
- Promote a finding to a real entry: `board_create_entry`.
- Save a durable insight: `board_remember` (project, insight).
- Rank systemic investigations: `board_insights` (project).
- Preserve or evaluate a cited root-cause claim: preview/apply with `board_hypotheses`.
- When done: `board_update_entry` to the new status, then `board_release`.

Read one entry with `board_get_entry`; get an overview with `board_status`.
<!-- engineering-board:end -->
