---
name: Board Triage
description: This skill should be used when the user asks "what's next", "what should I work on", "triage the board", "what's the priority", "what order should I fix these", "start work on", "begin implementation", "pick up the next item", or wants a recommended sequence derived from the current open items.
version: 0.1.0
---

# Board Triage

Derives the recommended work sequence from open board items and the five triage rules. Also governs Starting Work — setting an item `in_progress`.

## Step 0 — Identify the project scope

If triage was requested for a specific project, read that project's board at `docs/boards/<project>/BOARD.md`. If no project was specified, read `docs/boards/BOARD-ROUTER.md` to list all projects, then ask which to triage or triage all.

## Step 1 — Read current state

1. Read the target board's `BOARD.md` open list.
2. For each open item: read its entry file to get `priority`, `status`, `blocked_by`, and `affects`.
3. Build the live dependency picture:
   ```bash
   grep -r "blocked_by:" docs/boards/<project>/ --include="*.md" -h | sort | uniq
   ```

## Step 2 — Apply triage rules in order

Apply all five rules in sequence. Each pass narrows the candidate set.

**Rule 1 — Deliverable failures first**
Any bug that caused a missing or broken output already delivered ranks above all quality work regardless of complexity. These are P0/P1 bugs without `blocked_by`. Pull them to the top.

**Rule 2 — Open questions before the work they block**
Find every question with `status: open`. Any bug or feature with `blocked_by: [Q###]` pointing to it cannot start. Resolve the question first. Run open questions in parallel when they don't depend on each other.

**Rule 3 — Prerequisite order within batches**
Where one bug's fix feeds another (noted in entry body under "Fix direction" or "depends on"), fix upstream first. Example from current board: B004 → B003 (B004's keyword prioritization fix must land before B003's phrase integration work).

**Rule 4 — Batch by `affects:` component**
Bugs and features touching the same file go in one PR. Group them before proposing work order — this minimizes context-switching and merge conflicts.

**Rule 5 — Defer structural redesigns**
Changes requiring new content logic or architectural rethink go after incremental fixes are stable. Flag these explicitly as deferred with a reason.

**Rule 6 — Surface systemic pattern clusters**
After applying Rules 1–5, run the pattern cluster analysis:
```bash
# Current density — open entries
grep -r "^pattern:" docs/boards/<project>/bugs/ docs/boards/<project>/features/ \
  --include="*.md" -h 2>/dev/null \
  | sed 's/^pattern: *//' | tr -d '[]' | tr ',' '\n' | tr -d ' ' | grep -v '^$' \
  | sort | uniq -c | sort -rn

# Historical recurrence — archived resolutions
grep "pattern:" docs/boards/<project>/ARCHIVE.md 2>/dev/null \
  | grep -oE '[a-z][a-z-]+' | grep -v '^pattern$' | sort | uniq -c | sort -rn
```
When any pattern appears in **2+ open entries** OR **2+ archived resolutions**: flag it as a systemic investigation candidate. Recommend investigating the shared root cause across all affected entries before fixing them individually — isolated fixes on systemic bugs often recur.

## Step 3 — Output the sequence

Present:
1. **Recommended next item** — with ID, title, and rationale from the rule that selected it
2. **Full prioritized sequence** — all open, unblocked items in order
3. **Blocked items** — list what's waiting and what question unblocks each
4. **Deferred items** — if any, with reason

## Step 4 — Starting Work (when asked to begin an item)

Before marking any item `in_progress`:

1. Check for existing in_progress items across all project boards:
   ```bash
   grep -r "^status: in_progress" docs/boards/ --include="*.md" -l
   ```
2. If any found: surface them. One item `in_progress` per session maximum. Either complete the existing item, reset it to `open` with a note on where it stopped, or confirm explicitly before proceeding.
3. If clear: set `status: in_progress` in the entry file.
4. If a new issue or question surfaces during implementation: create a new entry immediately using board-intake. Add a `## Related discoveries` section to the current item referencing the new ID. Continue with the current item's original scope.
5. If the session ends without resolving: leave `in_progress` — the next session's `SessionStart` hook will surface it.
