# Auto-Resolve Terminal Pass — Shared Protocol

Every board operation ends with this pass. The board is meant to be **constantly self-healing**: entries whose Done-when criteria are already satisfied should not sit at `status: open` waiting for someone to remember to close them. This protocol is invoked as the final step of `/board-intake`, `/board-triage`, `/board-resolve`, `/board-rebuild`, and `/board-consolidate`.

**Cheap, idempotent, silent when zero candidates.** If the pass finds nothing, produce zero output. Noise here re-creates O001.

## Inputs

The caller supplies one of three scope modes:

| Mode | Scope | Used by |
|------|-------|---------|
| `focused` | A single entry (the one just written or modified) plus its `pattern:` / `affects:` neighbors | `/board-intake` after writing the new entry |
| `cascade` | The `pattern:` / `affects:` neighbors of a just-closed entry | `/board-resolve` after closing an entry |
| `full` | Every open entry on the target board(s) | `/board-triage`, `/board-rebuild`, `/board-consolidate` |

The caller also supplies the **target board(s)** — the project directory under `docs/boards/<project>/`.

## Algorithm

### Step 1 — Build the candidate set

Load entries with `status: open`, `status: blocked`, or `status: in_progress` from the target board(s) — restricted to the scope mode:

- `focused`: the named entry + entries sharing any `pattern:` tag OR overlapping `affects:` field.
- `cascade`: entries sharing any `pattern:` tag with the just-closed entry OR overlapping `affects:`.
- `full`: all open/blocked/in_progress entries.

Skip entries already at `status: resolved`. Skip entries already on this run's "to be closed" list (prevent double-close).

### Step 2 — Extract Done-when text per entry

For each candidate, read its `## Done when` section. Entries with no Done-when (observations) are skipped — observations are run logs, not work items.

If the entry has multiple criteria (numbered list, bullet list, multi-paragraph): treat them as ALL-must-match conjuncts, not any-match disjuncts. A partial match is `weak` confidence, not `verbatim`.

### Step 3 — Gather evidence sources

Three sources, queried in this order (cheapest first):

1. **Current session transcript** — the user-and-assistant turns of the active session. Highest signal for same-session bug-and-fix. Available via the conversation history; no extra tool call needed.
2. **Recent git log** — `git log --since=<entry.discovered>` on the project root if available. Filter to commits whose subject/body or changed files match the entry's `affects:` or evidence keywords. Skip silently if not a git repo.
3. **Filesystem state at `affects:` paths** — read the files referenced by `affects:`. If the entry asserts "X is broken" and X is now provably correct (e.g. a file no longer contains the broken pattern), that's evidence.

Each source returns zero or more evidence snippets per entry.

### Step 4 — Rank by confidence

Three tiers:

| Tier | Criterion | Action |
|------|-----------|--------|
| `verbatim` | A complete Done-when criterion appears as a substring or near-paraphrase in the evidence (session transcript quote, commit message, or diff) | Surface as **strong candidate** — prompt to close |
| `semantic` | All Done-when keywords are present in the evidence but in a different phrasing | Surface as **likely candidate** — prompt to close with note |
| `weak` | Only one keyword or partial criterion matches | Surface as **possible candidate** only if scope is `focused` or `cascade`; suppress in `full` mode (too noisy) |

For multi-criterion Done-when entries, ALL criteria must reach at least `semantic` for the entry to surface. A single matched criterion is not enough.

### Step 5 — Present candidates and prompt

If the candidate list is empty: produce zero output. Continue silently.

If non-empty: present inline with the parent command's output, in this format:

```
Auto-resolve candidates:
- B### [verbatim]   "Done-when: <one-line summary>"
  Evidence: <one-line quote from transcript/commit/file>
- Q### [semantic]   "Done-when: <one-line summary>"
  Evidence: <one-line quote>

Close any of these? (reply with IDs, or "skip")
```

Wait for user response. **Never auto-close without confirmation in v1.** False positives are unrecoverable in user trust terms.

If the user confirms closure of one or more IDs: execute the standard resolve protocol on each (frontmatter `status: resolved`, ARCHIVE.md append, BOARD.md regeneration). Cascade: closing each one re-invokes this pass with `cascade` mode on its neighbors — but **bounded depth 2** to prevent runaway cascades.

If the user replies "skip" or leaves them: leave entries at their current status. The next board operation will surface them again.

## What this pass does NOT do

- **Does not close anything without explicit user confirmation.** The pass surfaces, never auto-closes.
- **Does not modify entries other than the closed targets.** No "while we're here, let me also..." behavior.
- **Does not rerun if the parent command was itself triggered by this pass's cascade.** Bound depth 2.
- **Does not write to disk if the candidate list is empty.** Zero-output path is the common case at maturity.

## Failure modes and safeguards

- **Session transcript unavailable** — skip source 1, fall back to git+filesystem. Don't error.
- **Not a git repo** — skip source 2. Don't error.
- **`affects:` paths missing or null** — skip source 3 for that entry. Don't error.
- **Concurrent close** — if the entry's `status` field is no longer `open` by the time the user confirms close, skip silently (another session beat us to it). This is the B005 concurrent-write surface — surface as a warning, don't error.

## Caller integration notes

Each caller passes:
- `scope: focused | cascade | full`
- `target_board: <project-name>` or `all`
- Optional `seed_entry_id: <ID>` (the entry that triggered the pass — required for `focused` and `cascade`)
- Optional `cascade_depth: <int>` (default 0; the pass increments on recursive invocation; bound at 2)

The pass returns:
- List of closed entries (if any)
- List of candidates the user declined (for the caller's awareness)
- Warnings (concurrent-close detections, unparseable Done-when, etc.)
