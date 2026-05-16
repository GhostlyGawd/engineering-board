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

### Step 3 — Append to ARCHIVE.md

Read the entry's `pattern:` field. If present, include it in the archive line:
```
- B### | title | pattern: tag1, tag2 | resolved: YYYY-MM-DD
```
If no `pattern:` field, omit it:
```
- B### | title | resolved: YYYY-MM-DD
```

### Step 4 — Run /board-rebuild

Invoke `/board-rebuild <project>` (or run its logic inline). The just-resolved entry has `status: resolved` so it will be omitted from the regenerated BOARD.md automatically. GRAPH.yml regenerates in the same step. Do not manually edit BOARD.md.

### Step 5 — Auto-resolve cascade pass (mandatory)

After the rebuild, run the auto-resolve terminal pass — see `../../references/auto-resolve-pass.md`.

**Why at resolve:** closing one entry often satisfies adjacent ones. A bug fix usually resolves the observation that documented it; a feature shipping often resolves a related question. The cascade pass catches these without making the user re-run triage.

**Scope:** `cascade` mode. Seed entry is the entry just closed. Pass scans entries sharing any `pattern:` tag or overlapping `affects:` field with the closed entry.

**Cascade depth:** the pass increments depth on each recursive close and stops at 2 — closing A surfaces B, closing B surfaces C, closing C does not invoke another pass. Prevents runaway cascades on densely-clustered boards.

**Silent path:** zero candidates → no output. The resolution proceeds normally.

---

## Closing a Question (9-step sequence — order is mandatory)

Steps 1, 6, 7, and 8 are mandatory and must execute in the order given. Step 1 must come before Step 2 so the finding is documented before the question is marked closed. Steps 5-6 (unblock dependents + update them against the finding) must complete before Step 7 (/board-rebuild) so BOARD.md regenerates with all dependent-state changes reflected. Step 7 must complete before Step 8 (cascade pass) so the pass runs against fresh board state. Step 8 must complete before Step 9 so triage doesn't recommend items the cascade just closed.

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

### Step 3 — Append to ARCHIVE.md

Questions don't carry `pattern:` tags. Append:
```
- Q### | title | resolved: YYYY-MM-DD
```

### Step 4 — Find all blocked dependents

```bash
grep -r "blocked_by:.*Q###" docs/boards/<project>/ --include="*.md" -l
```

Replace `Q###` with the actual question ID. Collect all matching file paths.

### Step 5 — Unblock each dependent

For each file found in Step 4:
1. Remove `Q###` from its `blocked_by:` list in frontmatter.
2. If `blocked_by` is now empty, set `status: open`.

(The `⊘ Q###` markers in BOARD.md get regenerated correctly by `/board-rebuild` in the final step.)

### Step 6 — Update dependent entries against the Finding (mandatory before triage)

For each newly-unblocked entry: read its `## Fix direction`, `affects:`, and `## Root cause hypothesis` sections. Compare against the `## Finding` written in Step 1.

If the finding changes what the entry says — wrong affects field, wrong stage, stale wiring assumption, outdated fix direction — update the entry and add a section:
```markdown
## Q### finding (resolved YYYY-MM-DD)

[Note what changed and why, referencing the finding.]
```

### Step 7 — Run /board-rebuild

Invoke `/board-rebuild <project>` (or run its logic inline). This:
- Removes the resolved question from BOARD.md
- Removes `⊘ Q###` markers from any unblocked dependents' lines
- Re-sorts the board if any dependents' priorities changed
- Regenerates GRAPH.yml in the same step

Do not manually edit BOARD.md. The rebuild handles all the BOARD.md surgery that prior versions of this protocol did by hand.

### Step 8 — Auto-resolve cascade pass (mandatory)

After rebuild and before triage, run the auto-resolve terminal pass — see `../../references/auto-resolve-pass.md`.

**Scope:** `cascade` mode. Seed entry is the resolved question. The pass scans entries sharing `pattern:` tags or overlapping `affects:` with the question. Resolving a question often satisfies its dependents directly (the answer renders the dependent's investigation moot).

**Depth bound:** 2, same as for bug/feature resolve.

**Silent path:** zero candidates → no output. Proceed to Step 9.

### Step 9 — Apply triage and state next step

After the cascade pass settles, apply the board-triage rules to the now-current open items and state the recommended next step. Do not wait to be asked. (Triage itself will run its own auto-resolve pass — that's expected and idempotent; the cascade pass at Step 8 will already have surfaced anything triage's pass would catch, so triage's pass should be a no-op in the typical case.)

---

## Closing an Observation

Observations are run logs, not work items. There are no done-when criteria. To close:

1. Set `status: resolved` in the observation's frontmatter (observations didn't track status historically, but adding it makes `/board-rebuild` correctly omit the entry from BOARD.md).
2. Append to ARCHIVE.md: `- O### | title | resolved: YYYY-MM-DD`
3. Run `/board-rebuild <project>` — this removes the observation from BOARD.md and regenerates GRAPH.yml.
4. Run the auto-resolve cascade pass — see `../../references/auto-resolve-pass.md`. Scope: `cascade`, seed: the closed observation. Closing an observation often satisfies the bug or feature it was documenting evidence for (e.g. O003 documented the fix that satisfies B003).

Alternatively, leave observations open in BOARD.md indefinitely as reference — this is acceptable if the run data is still useful for pattern analysis.
