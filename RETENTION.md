# Retention & Lifecycle Audit — engineering-board

_Read-only pass, 2026-07-08. Mission: find why a user comes **back** — and every place
this product lets them drift away. Acquisition fills the top; retention is where
value compounds._

**Counting from real rhythm, not wishful notifications:** this is an **ambient**
tool — a Claude Code plugin / MCP server that runs in the background of normal
coding. Its natural rhythm is **every session**, and its only honest re-engagement
surface is the **SessionStart banner** (the user is already back). It has **no
server, no email, no push** — so retention here means "does the user keep it
installed and keep getting value each session," and win-back is nearly impossible
by design. That makes the *in-session* pull-back and the *compounding value loop*
the whole game.

**The strongest foundation, stated up front:** what persists between visits is
**everything, permanently** — the board is git-committed markdown (it cannot be
lost), learnings accrue as `L###` entries, claims and mode persist. Durable saved
state is the product's thesis and its best retention asset. The question is whether
that state is *resurfaced* to pull the user back — and whether it ever accrues at
all for the casual user.

---

## 1 — Return-trip map

| Dimension | Reading |
|---|---|
| **Visit rhythm** | Every coding session (ambient/passive). Not a destination you visit — a layer that's always on. |
| **What persists** | The board (committed markdown, permanent), `L###` learnings, claims, `session-mode.json`, `consolidation.log` (committed audit trail), the public `board.html`. Durable and version-controlled — the best-persisting state of any tool in the category. |
| **The pull back** | The **SessionStart banner** (`board-session-start.sh`): open items, in-progress warnings, un-promoted scratch count, blocking map, systemic patterns, and **top learnings filtered to your cwd** (`:196-268`). Plus a mid-session **prompt-guard** reminder that routing is active (`board-prompt-guard.sh:13`). Both resurface value the user already created — exactly the right move. |
| **The biggest leak** | **The capture→value gap.** Passive capture (the always-on default) is **invisible and inert** until the user runs `/pm-start` and ends a turn. A user who never dedicates a PM session gets silent scratch files, an empty board, and **never reaches the learnings loop** that makes returning rational → uninstall. The retention engine is gated behind the mode dance (see ACTIVATION.md A1/A3). |

---

## 2 — Findings

Format: **lens · location · why users drift here · the fix · effort (S/M/L).**
Ranked by compounding value — a fix early in the lifecycle pays on every future visit.

### R1 — The compounding loop (the learnings moat) only engages for active-PM users
- **Lens:** Habit and progression (5) · Reason to return (1)
- **Location:** The retention engine is: resolved entries → `learnings-curator` (PM mode only, `README.md:124`) → recurrence ≥ 3 → committed `L###` → resurfaced at SessionStart (`board-session-start.sh:239` requires `confidence ≥ medium`). A **capture-only** user never runs the curator, so **never accrues a single learning.**
- **Why users drift:** The one thing that makes every future session more valuable (accrued, cwd-relevant learnings) is unreachable without the full promote→resolve→curate ceremony. The casual users most likely to churn are exactly the ones locked out of the loop that would retain them.
- **Fix:** Lower the ceremony so the loop spins for everyone — e.g. auto-consolidate scratch on session end even in passive mode (or a one-line `/board-promote` that doesn't require a mode), so boards fill, entries resolve, and learnings start accruing without a dedicated PM session. Ungate the moat.
- **Effort: M.**

### R2 — Un-promoted scratch is a silent churn cliff
- **Lens:** Churn cliffs (6) · Saved state as a hook (2)
- **Location:** Findings accumulate invisibly in `_sessions/` (`README.md:79`); the board stays `## Open (none)` until promotion. The SessionStart banner **does** warn — "SCRATCH ENTRIES — N un-promoted session file(s) waiting" (`board-session-start.sh:180`) — a genuine pull-back.
- **Why users drift:** The warning asks the user to go do **manual promotion work** rather than delivering value; on a young board there may be nothing yet worth the ceremony, so the pile grows, the board looks dead, and the tool reads as "installed once, did nothing."
- **Fix:** Turn the warning from a chore into delivered value: auto-promote (R1) so the count trends to zero on its own, and when scratch *is* pending, offer a one-keystroke promote from the banner rather than a shell command (`bash …/board-consolidate.sh`, `:181`).
- **Effort: S** (banner affordance) / folded into R1 (auto-promote).

### R3 — No async re-engagement or win-back: a departed user is gone by default
- **Lens:** Win-back (7) · Well-timed nudges (4)
- **Location:** No email/push/digest machinery anywhere (verified — the only "notification" is the in-session prompt-guard `systemMessage`, `board-prompt-guard.sh:13`). The only scheduled job is `metrics.yml` (Mondays 06:17 UTC), which collects acquisition stats, not user re-engagement.
- **Why users drift:** Once a user stops opening the repo, nothing reaches them — there's no path to say "your board has findings waiting" or "a learning you saved applies to what you're doing." A leave is permanent.
- **Fix (honoring "no exit held hostage"):** Prefer resurfacing existing value over inventing notifications. The one legitimate async surface is the **public live board** (`pages.yml` republishes `board.html` every merge) — make it carry accrued value (R4) so it's a passive pull. If any active nudge is ever added, gate it to the one thing a user would thank you for: "the pattern you hit before just recurred." Do **not** add generic re-engagement blasts to a local-first tool.
- **Effort: M** (and mostly a "don't" — resist spam; invest in R4 instead).

### R4 — Accruing value is never quantified back to the user
- **Lens:** Habit and progression (5) · Reason to return (1)
- **Location:** `board.html` (`board-view.sh`) shows **current** state ("N open · M total", `:232`) and a learnings panel, but never the **trajectory**: how much the board has learned and resolved over time. The SessionStart banner shows top-3 learnings but not "your board has learned 7 patterns from 23 resolved entries."
- **Why users drift:** Without a visible, growing tally of accrued value, staying feels optional. A true accrual count ("this board has captured 40 findings, resolved 23, and learned 7 recurring patterns — 2 apply here") is a rational, non-coercive reason to return — it's real value the user built, not a manufactured streak.
- **Fix:** Surface an accrual line at SessionStart and atop `board.html`: resolved-count, learnings-count, and "N learnings apply to your current path." All derivable from existing files (`learnings/`, `ARCHIVE.md`, `consolidation.log`).
- **Effort: S.**

### R5 — Local-install mode persistence causes silent drift
- **Lens:** The empty return (3) · Churn cliffs (6)
- **Location:** `session-mode.json` persists on disk locally (`README.md:83`); a forgotten `/worker-start` leaves later sessions in the wrong mode. The banner surfaces the current mode (`board-session-start.sh:53-61`) — good — but the file lingers until manually deleted.
- **Why users drift:** A user returns, is unknowingly still in worker mode, sees unexpected behavior, and blames the tool. Confusion → churn.
- **Fix:** Consider a mode TTL or a "you've been in worker mode for N sessions — still intended?" banner prompt, and a one-command `/board-mode reset`. Keep the surfacing that already works.
- **Effort: S.**

### R6 — A stalled first run is an unguided churn cliff
- **Lens:** Churn cliffs (6)
- **Location:** `/board-run` can end at "stopped at needs:X — fix the blocker" or "still at needs:X after 5 rounds — the state machine is cycling; inspect the entry's review notes" (`board-run.md:63-64`).
- **Why users drift:** A user's first real run stalling, with only "inspect review notes" as guidance, right after the demo, reads as "it doesn't work." No guided recovery.
- **Fix:** On a stall, print the specific next action (which review note, which Done-when failed, "re-run after fixing X") rather than a generic pointer. Recovery guidance retains; a dead-end churns.
- **Effort: S.**

### R7 — Return is not measured at all
- **Lens:** Is return even measured (8)
- **Location:** `docs/metrics.csv` tracks stars/forks/clones/downloads (acquisition) — and is **broken** (403 blobs, per PROOF.md F1). There is **no** cohort, retention curve, or "sessions with board activity over time." The latent signal — `consolidation.log` (committed, `board-consolidate.sh:97`) + the git history of `engineering-board/` — is never read as retention.
- **Why it matters:** Churn is invisible; you can't tell if anyone came back or where they dropped. You're optimizing the funnel blind past install.
- **Fix:** See §4 — self-instrumentation that respects the local-first, zero-dependency ethos (read git + logs locally; opt-in only). No server telemetry.
- **Effort: M.**

### What already works (protect it)
- **SessionStart resurfacing is genuinely good** (`board-session-start.sh:196-268`): it filters learnings to the user's cwd and ranks by confidence×recurrence — resurfacing *relevant* past value, not noise. This is the retention machine; the fixes above mostly feed it more content.
- **State is permanent and diffable** — the board can't be lost; a returning user's context is fully restored from git. The "empty return" is only cold for users who never reached first value (an activation problem, ACTIVATION.md).
- **Nudges are restrained and honest** — the prompt-guard fires only on relevant prompts; there is no spam. Keep it that way.

---

## 3 — The one hook to build

**Make the compounding learnings loop engage automatically, and surface its accrual
at SessionStart — so every user (not just PM power-users) returns to a board that is
visibly getting smarter from their own past work.**

The argument:
- The **resurfacing surface already exists and is well-built** (`board-session-start.sh:196-268`, cwd-filtered, confidence-ranked). The gap is upstream: **most users never accumulate learnings**, because promotion and curation are gated behind the mode dance (R1). An excellent pull-back surface with nothing to pull is inert.
- Fixing the *supply* (ungate promote/curate so boards fill and learnings accrue — R1) turns the existing resurfacing into a real retention engine, and it does so by **resurfacing value the user already created** — the brief's preferred move over inventing new notifications.
- Then quantify it (R4): a single SessionStart line — _"your board has learned 7 patterns from 23 resolved entries; 2 apply to what you're working on now"_ — is a concrete, honest, non-coercive reason to open the next session. It's not a streak or a dark pattern; it's the user's own accrued context, shown growing.

Net: the second visit and the tenth both open with "here's what's waiting for you,
and here's what your board now knows." That is the pull that compounds — and it's
built mostly from machinery that already ships, once the loop is ungated.

---

## 4 — Instrumentation gaps

Retention is currently unmeasurable. The events/cohorts needed — all derivable
**locally**, honoring the zero-dependency, local-first, no-telemetry ethos:

| Signal | Where it already lives (latent) | What it tells you |
|---|---|---|
| **Board activity per day/session** (capture / promote / run / resolve happened?) | git history of `engineering-board/` + `consolidation.log` | The core retention curve — is this board still being worked, or did it go dormant? |
| **Capture→promote funnel** | count of `_sessions/*.md` vs promoted entries in `BOARD.md`/`ARCHIVE.md` | Where the biggest leak (R2) is bleeding — how many findings die in scratch |
| **Learnings accrual over time** | `learnings/L###` frontmatter (created dates, recurrence) | Is the moat compounding, or flat? |
| **Mode engagement** | presence/age of `session-mode.json`, `active-workers` registry | How many users ever reach the retention loop at all (R1) |

**How to surface without a server:** a `/board-stats` command (and/or a footer line
on `board.html`) that reads these locally and prints the retention picture **to the
user themselves** — self-instrumentation, not phone-home telemetry. It doubles as
the R4 accrual hook. Aggregate cross-user retention stays out of reach by design
(no server) — and that's an acceptable trade for the local-first promise; the fix is
to make each user able to *see their own* return-worth, not to track them centrally.

---

_Report only. **Which fixes would you like me to make?** Recommendation: build the
**one hook** — ungate the learnings loop (R1) and surface accrual at SessionStart
(R4) — since it converts already-shipped resurfacing into a real retention engine
and fixes the biggest leak (R2) at the source. Then the S-effort follow-ons: R6
(guided stall recovery), R5 (mode drift), and a local `/board-stats` for R7/R4.
Everything here retains by delivering the user's own value again — no notifications,
no exit held hostage._
