---
name: Board Intake
description: This skill should be used when the user says "log this to the board", "route this finding", "add a bug", "create a board entry", "intake this", "new finding", "track this issue", "add an observation", or when a confirmed bug, regression, unexpected behavior, root cause, or noteworthy observation surfaces during a debugging or workflow session. Also use when asked to check for duplicate entries before creating one.
version: 0.1.0
---

# Board Intake

The workspace has multiple project boards under `docs/boards/`. The router lives at `docs/boards/BOARD-ROUTER.md` and lists each project's board path and `affects:` prefix. Entry files use YAML frontmatter. The full schema is in `references/frontmatter-schema.md`.

**Source of truth for ID sequences:** the highest-numbered existing file in the relevant subdirectory.

## Step 0 — Identify the target board

Read `docs/boards/BOARD-ROUTER.md`. Match the finding's `affects:` prefix against the prefix column to determine which project board owns this entry. If ambiguous, surface the options before proceeding.

Common routing:
- `affects: navigator/`, `prompts/`, `scripts/`, `src/` → `docs/boards/navigator/`
- `affects: engineering-board/` → `docs/boards/engineering-board/`

## Protocol

### Step 1 — Duplicate check (mandatory, always first)

Before creating anything:

1. Read the target board's `BOARD.md` open list — scan for entries touching the same component or root cause.
2. `grep -r "affects:" <board-dir>/bugs/ <board-dir>/features/ 2>/dev/null` — find entries with overlapping `affects:` fields.
3. Match on component overlap and root cause similarity, not just title.
4. If a match exists: add a `## Update YYYY-MM-DD` section to the existing entry. Update frontmatter fields if `priority`, `affects`, or `status` changed. Update `## Done when` if verification criteria changed. If `priority` changed, update the priority marker on that item's BOARD.md line. **Stop — do not create a duplicate.**
5. If no match: proceed to Step 2.

### Step 2 — Determine entry type and next ID

Classify the finding:
- **Bug (B###)**: incorrect, missing, or broken output already observable
- **Feature (F###)**: new capability or behavioral change not yet present
- **Question (Q###)**: hypothesis or unknown that blocks a bug or feature
- **Observation (O###)**: run log or noteworthy session finding; no fix required

Get the next ID within the target board:
```bash
ls <board-dir>/<type>/ | grep -oE '[0-9]+' | sort -n | tail -1
```
Increment by 1 and zero-pad to 3 digits (e.g. B013, Q005).

### Step 3 — Create entry file

Create `<board-dir>/<type>/<ID>-<slug>.md`.

Required frontmatter by type — see `references/frontmatter-schema.md` for full field definitions and valid values.

**Bug / Feature minimum:**
```yaml
---
id: B###
type: bug
status: open
needs: tdd
priority: P1
title: Short present-tense description of the broken behavior
affects: path/to/affected/file.md
discovered: YYYY-MM-DD
---
```

**Question minimum:**
```yaml
---
id: Q###
type: question
status: open
title: Short question in interrogative form
discovered: YYYY-MM-DD
---
```

**Observation minimum:**
```yaml
---
id: O###
type: observation
title: YYYY-MM-DD ASIN — brief summary
discovered: YYYY-MM-DD
---
```

Required body sections:
- **Bugs / Features / Questions**: `## Done when` — one line minimum. Required.
- Add `## Observed behavior`, `## Root cause hypothesis`, `## Fix direction` for bugs as applicable.

### Step 3b — Assign pattern tags (all types)

After determining the root cause, assign one or more `pattern` tags to the entry:

```yaml
pattern: [instruction-ambiguity, keyword-placement]
```

**Rules:**
- Grep existing open entries and ARCHIVE.md for existing pattern strings first: `grep -r "^pattern:" <board-dir>/ --include="*.md" -h 2>/dev/null` — reuse existing tags when the failure mode matches rather than coining new ones
- Use kebab-case, describe the *failure mode* not the product area (`instruction-ambiguity` not `seo-copywriting`)
- Multiple tags per entry when the entry reflects more than one failure mode
- Apply to all entry types: bugs and features always; observations when the failure area is identifiable from the run; questions when the investigation area is clear (even before the Finding is written). Tag first occurrences too — tagging singletons is what enables recurrence detection when a second instance appears.

**Pattern recurrence check:** after assigning tags, check whether any assigned tag already appears in 2+ open entries or 2+ ARCHIVE.md resolutions:
```bash
# Open entries
grep -r "^pattern:" <board-dir>/bugs/ <board-dir>/features/ --include="*.md" -h 2>/dev/null \
  | sed 's/^pattern: *//' | tr -d '[]' | tr ',' '\n' | tr -d ' ' | grep -v '^$' | sort | uniq -c | sort -rn

# Archived resolutions
grep "pattern:" <board-dir>/ARCHIVE.md 2>/dev/null \
  | grep -oE '[a-z][a-z-]+' | grep -v '^pattern$' | sort | uniq -c | sort -rn
```

If a tag appears 2+ times (open) or 2+ times (archived): add a `## Pattern recurrence` section to the new entry noting the cluster and flagging it as a systemic investigation candidate.

### Step 4 — Wire blocking relationships (bugs and features only)

```bash
grep -r "status: open" <board-dir>/questions/ --include="*.md" -l
```

For each open question, read its `affects:` field. If it overlaps with the new entry's `affects:`:
- Add `blocked_by: [Q###]` to the new entry's frontmatter
- Change `status: blocked` in the new entry
- Append `⊘ Q###` to the new entry's BOARD.md line (added in Step 5)

### Step 5 — Update BOARD.md index

Add a line under `## Open` in the target board's `BOARD.md`:

- Bug/Feature: `- B### P# | [title](bugs/filename.md)` (append `⊘ Q###` if blocked)
- Question: `- Q### | [title](questions/filename.md)`
- Observation: `- O### | [title](observations/filename.md)`

Placement: P0 → P1 → P2 → P3 → unranked.

## Additional Resources

- **`references/frontmatter-schema.md`** — complete field definitions, valid values, and rules for all entry types
