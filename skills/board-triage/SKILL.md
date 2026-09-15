---
name: board-triage
description: This skill should be used when the user asks "what's next", "what should I work on", "triage the board", "what's the priority", "what order should I fix these", "start work on", "begin implementation", "pick up the next item", or wants a recommended sequence derived from the current open items.
---


# Board Triage

Derives the recommended work sequence from open board items and the six triage rules. Also governs Starting Work: setting an item `in_progress`.

## Codex and MCP protocol

Use this protocol when the `engineering-board` MCP server is available:

1. Resolve the absolute repository root and project name. Pass `root` in every
   tool call.
2. Call `board_status` and `board_list_entries` with `ready: true`. Also inspect
   `in_progress` entries and claims across the repository using Step 4. A ready
   list is not an ownership check.
3. Keep this initial pass to board overview and recommendation. Before resuming
   an entry, researching its fix, or changing its state, pass the ownership gate
   in Step 4. Call `board_context` for the current task and candidate entries. Use
   `board_insights` when a repeated pattern or graph cluster can change the
   recommended scope.
4. Recommend the next entry from priority, blocker, dependency, affected-area,
   and systemic-pattern evidence. Explain the reason.
5. When work starts or resumes, follow Step 4, including its existing-claim
   checks. For a new entry, call `board_claim` before `board_update_entry`; only
   `acquired: true` with `exit_code: 0` permits setting `in_progress`.
6. Capture new findings with `board_capture_finding`. Do not expand the claimed
   entry silently.

Use the detailed rules below to interpret the returned board state. Use shell
commands for board operations only when MCP is unavailable. Claim inspection
requires read-only filesystem access even with MCP: `board_status` and
`board_list_entries` do not return claim ownership or heartbeat evidence. If
that access is unavailable, ownership is unknown; do not start or resume work.

## Step 0: Identify the project scope

If triage was requested for a specific project, read that project's board at `engineering-board/<project>/BOARD.md`. If no project was specified, read the resolved `BOARD-ROUTER.md` (resolution order: `engineering-board/BOARD-ROUTER.md` to `docs/boards/BOARD-ROUTER.md` to legacy `docs/board/`) to list all projects, then ask which to triage or triage all.

## Step 1: Read current state

1. Read the target board's `BOARD.md` open list.
2. For each open item: read its entry file to get `priority`, `status`, `blocked_by`, and `affects`.
3. Build the live dependency picture:
   ```bash
   grep -r "blocked_by:" engineering-board/<project>/ --include="*.md" -h | sort | uniq
   ```

## Step 1b: Auto-resolve terminal pass (run before triage output)

Before applying the triage rules, run the auto-resolve terminal pass: see `../../references/auto-resolve-pass.md`.

Apply the Step 4 ownership gate first to every `in_progress` candidate. Exclude
foreign, stale, missing, or unverifiable claims from fix research and closure
actions in this pass. A board overview may report their recorded state.

**Why at triage:** recommendations should never point at already-done items. If a Done-when criterion was satisfied by work that happened between the last `/board-rebuild` and this triage call, surface it now so the user can close it before the triage output is computed.

**Scope:** `full` mode across the target board. Suppress `weak` candidates: the triage view should not be cluttered with low-confidence noise. Only surface `verbatim` and `semantic` candidates.

**Silent path:** zero candidates to no output, proceed to Step 2 unchanged.

**If the user closes any entries from the pass:** re-read the open list from disk before continuing to Step 2 (closed entries should not appear in the triage output).

## Step 2: Apply triage rules in order

Apply all six rules in sequence. Each pass narrows the candidate set.

**Rule 1: Deliverable failures first**
Any bug that caused a missing or broken output already delivered ranks above all quality work regardless of complexity. These are P0/P1 bugs without `blocked_by`. Pull them to the top.

**Rule 2: Open questions before the work they block**
Find every question with `status: open`. Any bug or feature with `blocked_by: [Q###]` pointing to it cannot start. Resolve the question first. Run open questions in parallel when they do not depend on each other.

**Rule 3: Prerequisite order within batches**
Where one bug's fix feeds another (noted in entry body under "Fix direction" or "depends on"), fix upstream first. Example from current board: B004 to B003 (B004's keyword prioritization fix must land before B003's phrase integration work).

**Rule 4: Batch by `affects:` component**
Bugs and features touching the same file go in one PR. Group them before proposing work order: this minimizes context-switching and merge conflicts.

**Rule 5: Defer structural redesigns**
Changes requiring new content logic or architectural rethink go after incremental fixes are stable. Flag these explicitly as deferred with a reason.

**Rule 6: Surface systemic pattern clusters**
After applying Rules 1-5, run the pattern cluster analysis:
```bash
# Current density — open entries
grep -r "^pattern:" engineering-board/<project>/bugs/ engineering-board/<project>/features/ \
  --include="*.md" -h 2>/dev/null \
  | sed 's/^pattern: *//' | tr -d '[]' | tr ',' '\n' | tr -d ' ' | grep -v '^$' \
  | sort | uniq -c | sort -rn

# Historical recurrence — archived resolutions
grep "pattern:" engineering-board/<project>/ARCHIVE.md 2>/dev/null \
  | grep -oE '[a-z][a-z-]+' | grep -v '^pattern$' | sort | uniq -c | sort -rn
```
When any pattern appears in **2+ open entries** OR **2+ archived resolutions**: flag it as a systemic investigation candidate. Recommend investigating the shared root cause across all affected entries before fixing them individually: isolated fixes on systemic bugs often recur.

> **Two distinct thresholds: not a contradiction.** `2+` here is the *cluster-surfacing* threshold: it flags a pattern for human investigation during triage. It is separate from the *Learning-promotion* threshold used by the `learnings-curator` PM subagent, which promotes a pattern to a durable `L###` entry only at **recurrence ≥ 3** (across resolved entries). A pattern can be surfaced as a cluster (2+) well before it earns a committed Learning (3+).

## Step 3: Output the sequence

Present:
1. **Recommended next item**: with ID, title, and rationale from the rule that selected it
2. **Full prioritized sequence**: all open, unblocked items in order
3. **Blocked items**: list what is waiting and what question unblocks each
4. **Deferred items**: if any, with reason

## Step 4: Ownership gate (before starting or resuming work)

An `in_progress` status records work state, not permission for this chat to
continue it. This gate also applies to “continue”, “resume”, and fix research.
Reading board records to report an overview is permitted before acquisition.

### 4a. Establish the current working session

Use the current host session identifier from this chat's trusted session/hook
context, or the stable working-session id explicitly assigned to this worker.
A lead may hold a claim on behalf of a named builder when the explicit
assignment records that owner and delegation. Never adopt an id found in a
claim, another chat, a copied transcript, or repository-wide
`.engineering-board/last-stop-stdin.json` as proof of this chat's identity.
If the host supplies no identifier, create a unique id for this working session
and retain it for subsequent calls. That new id cannot prove ownership of an
older claim. If identity or delegation cannot be verified, treat existing
ownership as unknown and limit the action to an overview.

### 4b. Inspect ownership before choosing work

Resolve the actual board directories from the board router (including legacy
locations). Across all project boards in this repository, inspect entry status
and `_claims/<entry-id>/owner.txt` plus `heartbeat.txt`. Include this session's
claims even when an entry has not yet been marked `in_progress`. Read the full
`session_id:` value and require one unambiguous, exact match to the current
working session. Project plus entry id identifies the work; ids can repeat
across projects.

Require a parseable, recent UTC heartbeat: less than 180 seconds old. Allow
less than 300 seconds only when the active claim implementation is verified to
use its OneDrive mode for this exact board path; MCP and shell detection differ.
Use the conservative 180-second limit when that mode is uncertain. A future timestamp, duplicate/malformed owner,
missing file, or unreadable claim is unverifiable. Re-read the claim before
resuming research or making a state change; if ownership changed, stop work on
that entry. Do not infer ownership from the title, status, cwd, prior summary,
or the fact that this repository was opened in this chat.

| Observed state | Permitted action |
| --- | --- |
| Exactly one claim is verified as this session's, and its heartbeat is fresh | Resume that entry within the authorized scope; if its status is still open, set `in_progress` after the ownership check. |
| A different session owns an `in_progress` entry | Report it as another session's work. Do not research its fix, reset its status, release its claim, or resume it. It does not block this session from claiming a different ready entry. |
| An `in_progress` entry has no claim, a stale claim, or unknown ownership | Report the ownership gap and leave status and claim unchanged. Do not auto-reclaim or treat age as permission to take over. |
| This session already owns an entry and requests a different one | Keep one owned entry per working session. Finish or deliberately park its own work with a progress note and owner-checked release before acquiring another. Never reset somebody else's work to satisfy this limit. |
| Multiple claims match this session | Surface the conflict and reconcile this session's assignments before starting or resuming work. Do not choose one silently. |
| No claim belongs to this session, and the selected ready entry is open and unclaimed | Attempt atomic acquisition as below. |

A transfer or stale-claim recovery is a separate, explicitly authorized action,
not a triage side effect. This includes a stale claim with this session's id.
A request to start an entry does not authorize overriding its existing owner.

### 4c. Acquire, then update

With MCP, call `board_claim` with `root`, `project`, `entry_id`, and the current
`session_id`. Proceed only when `exit_code: 0` and `acquired: true`. Exit 1
(`contended`) or exit 2 (`stale`) means leave the entry unchanged, report the
result, and return to the overview or select another unclaimed ready entry.
Any error or ambiguous response also stops acquisition. Do not call release,
reclaim, or retry using the observed owner's id to bypass contention. Claiming
an already-owned entry returns contention too; use 4b to verify a resume,
not repeated acquisition as an ownership probe.

Without MCP, use the same gate and the atomic script:

```bash
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-claim-acquire.sh" "<board-dir>" "<entry-id>" "<current-session-id>"
```

Only exit 0 permits continuation; exits 1 and 2 have the same meanings as MCP.
Never replace acquisition with an entry-file status edit. After successful
acquisition, re-read ownership and entry eligibility before `board_update_entry`
(or the shell fallback entry edit), then set `status: in_progress`. If the entry
is no longer eligible, release only the verified claim just acquired and
recompute the recommendation. If updating fails, report the retained claim and
recover it within this session before selecting different work.

Keep the claim heartbeat current during long work with the installed
`board-claim-heartbeat.sh <board-dir> <entry-id> <current-session-id>` where
available; it checks ownership. MCP has no heartbeat tool. If a heartbeat
cannot be maintained, stop at the stale boundary and report it; never refresh a
stale claim merely to make the resume gate pass.

### 4d. Continue within scope

If a new issue or question surfaces during implementation, use board-intake and
link the resulting finding or entry under `## Related discoveries`. Continue
with the current entry's original scope. If the session ends without resolving,
leave a progress note and follow the host's owner-checked claim lifecycle. The
next session may see `in_progress` in its startup summary, but must run this
ownership gate before resuming it.
