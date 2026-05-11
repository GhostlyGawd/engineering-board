# Manual smoke checks (v0.2.1)

Two of the v0.2.1 surfaces can only be exercised inside a live Claude Code session because they depend on the Stop hook firing and on the SessionStart hook running at session boot. The deterministic surfaces are covered by `tests/smoke/automated.sh` — see that script for the 21-assertion battery covering consolidation, blocklist, supersession, anchor verification, audit, and index-check.

The two checks below take ~30 seconds each.

## Prerequisites

- `engineering-board@engineering-board` installed at v0.2.1 and reloaded.
- A scratch project directory with the board scaffold initialized (`/board-init <project>` then session restart).

## Check 1 — PAUSED sentinel suppresses extraction

Goal: `/board-pause` writes `mode: paused` to `.engineering-board/session-mode.json`, and the next Stop hook short-circuits to `<<EB-PASSIVE-PAUSED>>` without invoking the extractor or writing to scratch.

Steps:
1. In a Claude Code session in your scratch project, run `/board-pause`.
2. Note the size of `docs/boards/<project>/_sessions/<session-id>.md` (if it exists; if not, that's also fine).
3. Send any short message to the assistant — for example, `ok`.
4. After the assistant replies, the Stop hook fires.

Pass signals:
- The assistant's final line contains exactly `<<EB-PASSIVE-PAUSED>>`.
- The scratch file's size does not change. No new `<!-- timestamp -->` block, no new JSON.
- `cat .engineering-board/session-mode.json` shows `"mode": "paused"`.

Fail signals:
- A new JSON block appears in the scratch file (the PAUSED gate failed; extractor still ran).
- The assistant emits `<<EB-PASSIVE-DONE>>` instead of `<<EB-PASSIVE-PAUSED>>`.
- Any other sentinel, or no sentinel at all.

To resume after the check: `/board-resume`. Confirm session-mode.json shows `"mode": null` (or the prior mode) and that subsequent Stop fires emit `<<EB-PASSIVE-DONE>>` again.

## Check 2 — SessionStart surfaces un-promoted scratch counts

Goal: when `_sessions/` contains one or more `*.md` files, the SessionStart banner lists the un-promoted count per project and each session-id.

Steps:
1. Confirm at least one scratch file exists at `docs/boards/<project>/_sessions/*.md` (run the assistant for one turn after `/board-init` to seed one — or skip and verify the empty case first).
2. Close the Claude Code session.
3. Reopen a session in the same cwd. The SessionStart hook runs.

Pass signal — when scratch files exist:
```
[ <project> ] - N open item(s):
  ...
  SCRATCH ENTRIES - 1 un-promoted session file(s) in _sessions/. Will consolidate on real session end. Run `bash $CLAUDE_PLUGIN_ROOT/hooks/scripts/board-consolidate.sh` manually to consolidate now.
        <session-id>
```

Pass signal — when scratch is empty:
- The banner does NOT include any `SCRATCH ENTRIES` line. Existing v0.2.0 sections (open items, in-progress warnings, blocking relationships, pattern clusters) appear unchanged.

Fail signals:
- `SCRATCH ENTRIES` line appears with the wrong count (off-by-one against `ls _sessions/*.md` excluding `_archive/`).
- `_archive/` files leak into the count.
- The line appears even when `_sessions/` is empty or doesn't exist.

## When to run

Run `bash tests/smoke/automated.sh` after any change to:
- `hooks/scripts/board-consolidate.sh`
- `hooks/scripts/board-audit-scratch.sh`
- `hooks/scripts/board-index-check.sh`
- `agents/finding-extractor.md` (its reject rules duplicate the consolidator's; if they diverge, both must continue to work)

Run the two manual checks above after any change to:
- `hooks/hooks.json` Stop-hook prompt body (Check 1 covers the PAUSED gate)
- `hooks/scripts/board-session-start.sh` (Check 2 covers the `_sessions/` block)
- `commands/board-pause.md` or `commands/board-resume.md` (Check 1 covers the round-trip)
