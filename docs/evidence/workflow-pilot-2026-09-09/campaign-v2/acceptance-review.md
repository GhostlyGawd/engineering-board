# Final independent acceptance

Reviewer: `review_workflow_protocol`. Verdict: **PASS for freeze and launch
under the declared protocol**.

Reviewed source: `3f256bf5949fdfaee39fb699181bc7b5497a7048`.
Campaign: `docs/evidence/workflow-pilot-2026-09-09/campaign-v2/`.
Prepared manifest SHA-256:
`977a6fba9682798a48934ef9d32c359a0ec7598a9fa0ba0bf9a6151390335bf4`.

Independent verification established:

- All four prepared Board cases retrieve the expected memory through the
  installed 1.13.5 launcher: L101, L102, H101 and H102. Results have no stale
  flag or warnings; both hypotheses remain proposed.
- Supporting B records and both Learning records are readable through
  `board_get_entry`.
- All twelve rendered prompts and commands use their assigned workspace roots.
  Common task files match across conditions; only Board arms configure the
  additional MCP server.
- All twelve Board entry bodies match their selected-history counterparts.
  Agent-visible inputs pass the condition-label scan.
- Prepared inventories, trial inputs, runtime identities and runner bytes remain
  unchanged after these read-only checks.
- The committed manifest retrieved from `e210a31` matches the reviewed hash.
  No freeze, run receipts or live results existed when checked. This review
  made zero model calls.

The previous hypothesis-schema blocker is corrected. The rejected first
campaign remains separate.

Remaining limits: this is a four-case synthetic pilot of assisted memory access,
with procedural rather than OS-enforced read isolation. Direct launcher
verification does not establish effective Codex tool exposure or natural
installation activation. Trace review is only partially blinded.

Released `board_get_entry` does not retrieve H101/H102 directly. Their summaries
are available through `board_context`, supporting B records through
`board_get_entry`, and full hypothesis Markdown through permitted local-file
access. Record the actual access route. An unsupported H lookup during a trial
remains subject to the unchanged error-stopping rule; this review does not
authorize retries or recovery coaching.

Persist this final acceptance with the reviewed manifest before freezing. No
unresolved requirement failure blocks the declared pilot.
