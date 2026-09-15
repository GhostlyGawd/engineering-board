# B011 builder handoff

## Scope and acceptance

Owner: lead on behalf of `b011_builder`, claim `b011-owner-20260914`.
Base: `7619752`; branch: `fix/b011-intake-capture`.

Correct `skills/board-intake/SKILL.md` so acknowledging a concrete workflow
defect triggers scratch capture before the final response, including read-only
mistakes. Preserve uncertain-cause labeling, project routing, duplicate
handling, promotion preview/apply authorization, and truthful failure reports.
No runtime, release, metric, or canonical board changes are in this assignment.

## Change

The previous guidance required an "accepted finding" but did not define the
automatic acknowledgment trigger or a completion check. It also required user
selection for auto-scan findings without distinguishing confirmed defects.
The revised guidance separates automatic scratch capture, speculative scan
selection, and authorized canonical promotion. It adds the scratch receipt or
explicit failure check before the final response, honors paused capture, and
prevents retries after uncertain append results without inspecting the inbox.

MCP examples use actual parameters (`kind`, `title`, `affects`, `evidence`,
`project`, `root`) and receipt fields (`scratch_file`, `captured_at`). Capture
has no `pattern`, `confidence`, or `scratch_id` parameter. Promotion is scoped
to the receipt's scratch filename; every proposed change must be reviewed
because the daily inbox can contain unrelated findings.

## Verification

`python3 tests/b011-intake-contract.py` — exit 0, 5 tests passed.

The tests call the real MCP handlers against temporary boards. They verify:

1. A read-only workflow defect has a scratch receipt before any canonical
   entry; preview does not create the entry, and unchanged apply does.
2. An uncertain cause recorded as an observation remains an observation.
3. Repeated behavior with new evidence matches the existing bug on promotion
   without modifying its file or creating a second canonical bug.
4. A missing target board raises a tool error without writing scratch.
5. An unavailable inbox write raises an error without returning a receipt.

These tests establish that the documented tool paths exist and preserve their
contracts. They do **not** establish that an agent will consistently recognize
or follow the new trigger. No live behavioral effectiveness or installed
release claim is made. Independent review and lead integration remain pending.

During fixture construction, an identical same-second recapture was classified
as already applied through its existing receipt. The duplicate fixture therefore
uses new evidence to exercise a distinct recurring observation and the actual
canonical deduplication path.
