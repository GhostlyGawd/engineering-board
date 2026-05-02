---
name: Board Resolve
description: This skill should be used when the user says "close this", "mark resolved", "this is fixed", "question answered", "resolve Q###", "resolve B###", "mark done", "it's working now", or when an item's done-when criteria have been met and the work is verified complete.
version: 0.1.0
---

# Board Resolve

The resolution protocol for all entry types. The question-closing sequence (Steps 6–9) is mandatory and order-sensitive — do not skip or reorder.

**Identify the entry's board first:** the board directory is derived from the entry file's path — `docs/boards/<project>/`. All BOARD.md index updates and ARCHIVE.md appends go to that project's board, not a different one.

## Closing a Bug or Feature

### Step 1 — Verify done-when criteria

Read the entry's `## Done when` section. Confirm the stated verification has been performed. If criteria aren't met, do not proceed — note what remains.

### Step 2 — Set resolved

In the entry file:
```yaml
status: resolved
```

### Step 3 — Remove from BOARD.md

Delete the item's line from the `## Open` section of `docs/board/BOARD.md`.

### Step 4 — Append to ARCHIVE.md

Read the entry's `pattern:` field. If present, include it in the archive line:
```
- B### | title | pattern: tag1, tag2 | resolved: YYYY-MM-DD
```
If no `pattern:` field, omit it:
```
- B### | title | resolved: YYYY-MM-DD
```

---

## Closing a Question (8-step sequence — order is mandatory)

Steps 1 and 7 are mandatory and must execute in the order given. Step 1 must come before Step 2 so the finding is documented before the question is marked closed. Step 7 must happen before Step 8 so dependent entries are accurate before triage runs.

### Step 1 — Write the Finding (mandatory before any status change)

In the question entry file, add:
```markdown
## Finding

[The actual answer with evidence. Be specific: what was confirmed, what was ruled out, what the root cause or code location is. This section is permanent — it informs every dependent entry and future sessions.]
```

Do not change `status` yet. The finding must be written first.

### Step 2 — Set resolved

```yaml
status: resolved
```

### Step 3 — Remove from BOARD.md

Delete the question's line from `## Open`.

### Step 4 — Append to ARCHIVE.md

Questions don't carry `pattern:` tags. Append:
```
- Q### | title | resolved: YYYY-MM-DD
```

### Step 5 — Find all blocked dependents

```bash
grep -r "blocked_by:.*Q###" docs/boards/<project>/ --include="*.md" -l
```

Replace `Q###` with the actual question ID. Collect all matching file paths.

### Step 6 — Unblock each dependent

For each file found in Step 5:
1. Remove `Q###` from its `blocked_by:` list in frontmatter.
2. If `blocked_by` is now empty, set `status: open`.
3. In `docs/board/BOARD.md`, remove `⊘ Q###` from that item's index line.

### Step 7 — Update dependent entries against the Finding (mandatory before triage)

For each newly-unblocked entry: read its `## Fix direction`, `affects:`, and `## Root cause hypothesis` sections. Compare against the `## Finding` written in Step 1.

If the finding changes what the entry says — wrong affects field, wrong stage, stale wiring assumption, outdated fix direction — update the entry and add a section:
```markdown
## Q### finding (resolved YYYY-MM-DD)

[Note what changed and why, referencing the finding.]
```

### Step 8 — Apply triage and state next step

After all dependents are updated: apply the board-triage rules to the current open items and state the recommended next step. Do not wait to be asked.

---

## Closing an Observation

Observations are run logs, not work items. There are no done-when criteria. To close:

1. Set no status field — observations don't track status.
2. Remove from BOARD.md if the information is fully captured and no action will follow.
3. Append to ARCHIVE.md: `- O### | title | resolved: YYYY-MM-DD`

Alternatively, leave observations open in BOARD.md indefinitely as reference — this is acceptable if the run data is still useful for pattern analysis.
