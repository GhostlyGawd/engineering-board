---
name: Board Intake
description: This skill should be used when the user says "log this to the board", "route this finding", "add a bug", "create a board entry", "intake this", "new finding", "track this issue", "add an observation", or when a confirmed bug, regression, unexpected behavior, root cause, or noteworthy observation surfaces during a debugging or workflow session. Also use when asked to check for duplicate entries before creating one.
version: 0.1.0
---

# Board Intake

The workspace has multiple project boards under `docs/boards/`. The router lives at `docs/boards/BOARD-ROUTER.md` and lists each project's board path and `affects:` prefix. Entry files use YAML frontmatter. The full schema is in `references/frontmatter-schema.md`.

**Source of truth for ID sequences:** the highest-numbered existing file in the relevant subdirectory.

## Step 0a — Source the findings

Two invocation modes:

**Specific-finding mode** — the user named what to intake (e.g. "log this regression", "add a bug for X"). Use exactly what the user described. Skip to Step 0b.

**Auto-scan mode** — invoked as a bare command (`/board-intake` with no target). Self-source findings:

1. Scan the current session for candidate findings — bugs (confirmed broken behavior), features (capabilities discussed but not yet built), questions (open unknowns), observations (noteworthy non-actionable facts).
2. For each candidate, extract: title, one-line evidence quote from the conversation, type, rough priority guess.
3. **Briefly present the candidate list to the user** (numbered, one line each) and ask: "Intake all of these? Or pick a subset?" — do NOT intake silently. The user may have raised something rhetorically that doesn't deserve a board entry.
4. After the user confirms or trims, proceed through Steps 0b–5 once per confirmed finding.

If the session contains zero substantial findings (e.g. pure conversational session with no bugs/features surfaced), say so and stop — do not invent entries.

## Step 0b — Identify the target board

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
discovered_at: YYYY-MM-DDTHH:MM:SSZ
contradicts: [F001]   # OPTIONAL — list of entry IDs whose claims this entry contradicts
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
discovered_at: YYYY-MM-DDTHH:MM:SSZ
---
```

**Observation minimum:**
```yaml
---
id: O###
type: observation
title: YYYY-MM-DD ASIN — brief summary
discovered: YYYY-MM-DD
discovered_at: YYYY-MM-DDTHH:MM:SSZ
---
```

**Required fields explained:**
- `discovered:` — date-only (YYYY-MM-DD) for filename/grouping/weekly rollups
- `discovered_at:` — full ISO-8601 UTC timestamp for intra-day ordering. Required because same-day sessions need precise ordering to track sequence and recency.

**Optional explicit-relationship fields** (use to wire structural relationships that `/board-graph` will surface deterministically):
- `blocked_by: [Q###]` — this entry cannot proceed until Q### is resolved
- `superseded_by: [B###]` — this entry was replaced by B###
- `merged_into: [B###]` — this entry's content was folded into B###
- `contradicts: [F###]` — this entry's existence disproves a claim made by F### (use for bug/feature pairs where the bug refutes the feature's promised behavior)

Add these at intake time when the relationship is known. They become `weight: 3` edges in GRAPH.yml. Without them, `/board-graph` can only infer relationships from shared tags/patterns, which is lossy.

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

### Step 5 — Run /board-rebuild

After the entry file is written, invoke `/board-rebuild <project>` (or run its logic inline). This regenerates BOARD.md from the filesystem — the new entry is automatically added to the correct section in correct priority order, with `⊘ Q###` blocking markers preserved from frontmatter. GRAPH.yml is regenerated in the same step.

**Do not manually edit BOARD.md to add the new entry.** Manual edits will be overwritten on the next rebuild. The rebuild is the canonical source for BOARD.md content; the entry file is the canonical source for entry data. This eliminates the drift problem (B004).

### Step 6 — Auto-resolve terminal pass (mandatory)

After the rebuild, run the auto-resolve terminal pass — see `../../references/auto-resolve-pass.md`.

**Why at intake:** same-session bug-and-fix is the common case, not the edge case. A user often surfaces a bug *because* they just fixed it (or just observed the fix landing). Writing `status: open` and walking away leaves the entry rotting until the next manual triage. The pass catches this at write time.

**Scope:** `focused` mode. Seed entry is the entry just written. Pass scans the new entry plus its `pattern:` / `affects:` neighbors — closing one finding often closes adjacent ones too (e.g. an observation documenting a fix satisfies the bug entry that fix addresses).

**Silent path:** if the pass finds zero candidates, produce no output. The intake command's normal "intaken B### / F### / Q### / O###" message is sufficient.

**Confirmation:** the pass prompts the user before closing anything. Never auto-close at intake.

## Additional Resources

- **`references/frontmatter-schema.md`** — complete field definitions, valid values, and rules for all entry types
- **`../../references/auto-resolve-pass.md`** — the shared auto-resolve terminal-pass protocol invoked at Step 6
