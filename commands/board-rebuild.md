# /board-rebuild — regenerate BOARD.md and GRAPH.yml from the filesystem

The deterministic-cache refresh command. Treats the entry `.md` files in `bugs/`, `features/`, `questions/`, `observations/` as the **single source of truth** and regenerates both `BOARD.md` (the index) and `GRAPH.yml` (the structural graph) from them. This is the fix for B004 (board state drifts from filesystem).

**Safe to run anytime.** Both outputs are deterministic — same input always produces byte-identical output (modulo `generated_at` in GRAPH.yml). No LLM calls in the regeneration step.

**Other modifying commands should call this as their last step** (intake, resolve, manual entry edits). That closes the staleness loop entirely.

## Trigger

- `/board-rebuild` — rebuild every project in BOARD-ROUTER.md
- `/board-rebuild <project-name>` — rebuild just that project

## Process

### Step 1 — Resolve target board(s)

Read `$CLAUDE_PROJECT_DIR/docs/boards/BOARD-ROUTER.md`. Target either the named project or all listed. Fall back to legacy `docs/board/` if no router.

### Step 2 — Scan entry files

For each project's board directory, list `*.md` files under `bugs/`, `features/`, `questions/`, `observations/`. Parse YAML frontmatter from each: `id`, `type`, `priority`, `status`, `title`, `pattern`, `tags`, `blocked_by`.

### Step 3 — Validate

Report (don't auto-fix) any of:

- **Duplicate IDs** — same `id:` field across two or more files. Indicates parallel-write corruption (B005).
- **Resolved entries still listed in BOARD.md** — entry has `status: resolved` but appears in current BOARD.md's Open section. Will be removed in this rebuild.
- **Orphan resolved entries** — entry has `status: resolved` but not in ARCHIVE.md. Should be archived manually or via `/board-resolve`. Do not auto-archive (resolutions need provenance).
- **Missing required frontmatter** — `id`, `type`, `title`, `discovered` missing. Report path for manual fix.
- **Dangling `blocked_by:` references** — `blocked_by:` lists a Q### that doesn't exist or is resolved. Report.

Validation is informational. The rebuild proceeds regardless of warnings.

### Step 4 — Regenerate BOARD.md

Filter to open entries:
- Bugs/Features/Questions with `status: open` (or no `status` field, defaulting to open)
- Observations: include all (observations have no `status` field by convention)
- Skip entries with `status: resolved`, `status: blocked`, `status: in_progress` — wait, no:
  - `status: blocked` and `status: in_progress` are still "open" in the BOARD.md sense — show them with their status as a suffix or in their own subsection? **v1: include them in Open with a `(blocked)` or `(in_progress)` suffix on the line.** Refine later.

Sort:
1. Bugs by priority (P0 → P1 → P2 → P3 → unranked), then by ID ascending within a priority
2. Features by priority, same rules
3. Questions by ID ascending
4. Observations by ID ascending

Emit BOARD.md with header + `## Open` section + the sorted lines + `## Conventions` footer. Use this exact format per line type:

- Bug/Feature: `- B### P# | [title](bugs/filename.md)`
- Bug/Feature with blocking: `- B### P# | [title](bugs/filename.md) ⊘ Q###`
- Bug/Feature in_progress or blocked: `- B### P# | [title](...) (in_progress)` or `(blocked)`
- Question: `- Q### | [title](questions/filename.md)`
- Observation: `- O### | [title](observations/filename.md)`

Filenames are derived from the entry's actual filename on disk, not constructed.

Header and Conventions footer are templated — preserve exact text across runs.

### Step 5 — Diff against existing BOARD.md

Before writing, read the current BOARD.md and diff the Open section against the about-to-be-written content.

Report:
- Lines added (entries that should be in BOARD.md but weren't)
- Lines removed (BOARD.md entries that no longer match a live file or are now resolved)
- Lines reordered (priority changes, ID re-sequencing)

This diff is the audit trail for what drift the rebuild corrected.

### Step 6 — Write BOARD.md

Overwrite. The new content is the source of truth.

### Step 7 — Regenerate GRAPH.yml

Invoke the `/board-graph` logic (Steps 1-7 of that command) using the just-scanned entry frontmatter as input. Same deterministic rules apply. GRAPH.yml gets a fresh `generated_at` timestamp.

### Step 8 — Auto-resolve terminal pass (mandatory)

After regeneration but before reporting, run the auto-resolve terminal pass — see `../references/auto-resolve-pass.md`.

**Why at rebuild:** rebuild is the canonical "I'm refreshing my picture of board state" command. It already detects drift between filesystem and BOARD.md. The auto-resolve pass detects the related drift between filesystem and *truth* — entries that should be closed but aren't.

**Scope:** `full` mode across each rebuilt board. Suppress `weak` candidates (rebuild reports should be terse). Only surface `verbatim` and `semantic`.

**Silent path:** zero candidates → no output, proceed to Step 9.

**If the user closes any entries from the pass:** re-run Steps 4–7 for that board to re-emit BOARD.md and GRAPH.yml with the closures reflected. The second pass is idempotent — won't loop because the closed entries are no longer at `status: open`.

### Step 9 — Report

Print to chat, single block:

```
Rebuilt board for project: <name>
  BOARD.md:  +<added> -<removed> ~<reordered>
  GRAPH.yml: <nodes> nodes, <edges> edges, <clusters> clusters, <findings> findings
  Auto-resolved: <count> entries  (if 0, omit this line)
  Validation: <warning_count> warnings  (if 0, omit this line)
```

If warnings: list them on subsequent lines, one per warning. Brief, no decoration.

## Notes

- **B004 fix mechanism**: this command is the cache invalidation strategy. BOARD.md is now a derived view. Manual edits to BOARD.md will be overwritten on the next rebuild — by design.
- **Idempotent**: running twice produces no change on the second run.
- **Cheap**: pure deterministic scan + format. Safe to call after every entry modification.
- **Recommended integration**: update `/board-intake`, `/board-resolve`, and any future modifying command to call `/board-rebuild` (or invoke its logic inline) as their final step. This closes the staleness loop.
- **What this does NOT do**: rebuild ARCHIVE.md (resolutions need provenance and timestamps that aren't preserved in a derived view); modify entry files except via the explicit Step 8 auto-resolve pass (which prompts before any close); silently auto-close anything — every closure flows through user confirmation in Step 8.
