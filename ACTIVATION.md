# Activation & First-Win Audit — engineering-board

_Read-only pass, 2026-07-08. Mission: judge the first session — from empty board to
first real win — and whether it leaves a newcomer **able and inspired** to do the
next thing. Install is not activation; the **first win** is._

**First win, defined:** the product visibly does its job = **a card moves through
`tdd → review → validate` and reaches validated — driven by an agent, watched by
the user.** The lesser milestone is a **visible promoted card** appearing on the
board. Both are gated behind an unusually long, mode-laden, partly-**invisible**
path today.

**The core problem in one line:** the product's *first* action (passive capture) is
**silent by design**, and its *best* action (an agent resolving a card) sits ~10
steps and 2 session restarts away — with **no sample data** to watch it work
before you've done the work yourself.

---

## 1 — First-session walk (screen by screen, findings inline)

| # | Step (what the newcomer does) | What they see | Finding |
|---|---|---|---|
| 1 | `/plugin marketplace add GhostlyGawd/engineering-board` | plugin marketplace added | fine |
| 2 | `/plugin install engineering-board` | plugin installed | fine |
| 3 | `/board-setup` (`commands/board-setup.md`) | 3-line "Board ready / Capture is on / Pipeline permissions" summary | **Good reassurance.** But it tees up `/pm-start` as the only next step — a mode, not a win (see A3). |
| 4 | **Restart Claude Code** (`board-init.md:120` "Restart… so the SessionStart hook picks up the new layout") | new session; SessionStart banner | **A4 — a hard restart gate mid-onboarding.** |
| 5 | SessionStart banner (`board-session-start.sh:88-96`) | `[ project ] — 0 open item(s)` · `(none yet — findings are captured automatically…)` | **A2 — blank canvas.** Nothing to look at, nothing to try. The empty state *describes* emptiness; it doesn't hand the user a first action. |
| 6 | Do real work so the agent surfaces a finding | …the turn ends… | **A6 — you must go do real work first**; there's no "try it now." |
| 7 | Turn ends → passive capture fires (Stop hook) | **nothing visible** — a file lands silently in `_sessions/` | **A1 — the first value is invisible by design** (`README.md:79,85` "capture is a passive side effect… deliberately quiet… peek at that folder to confirm"). Newcomer's thought: _"Did anything happen? Is it working?"_ |
| 8 | `/pm-start` (`commands/pm-start.md`) | "PM mode active. Stop hook will route through PM continuation each turn." | **A3 — enters a mode** to get value; **A5 — value won't happen until you _end a turn_** (`pm-start.md:85`), an unintuitive trigger the command states but doesn't explain *why*. |
| 9 | **End another turn** → consolidation runs | first **visible** card appears in `BOARD.md` / `/board-view` | **← lesser first win** (a promoted card). Reached at ~step 9, ~10–15 min (`README.md:85`). |
| 10 | Realize `/board-run` won't work in PM mode → **fresh session** (`board-run.md:14` "currently in PM mode… Start a fresh session") | new passive session | **A3 again — a second restart** just to switch off a mode. |
| 11 | `/board-run <entry-id>` (`commands/board-run.md`) | `round 1: tdd → …`, `round 2: review → …`, `round 3: validate → …`, "validated in N rounds" | **← the real first win** (an agent driving the pipeline). Reached at ~step 11. |
| 12 | `/board-resolve <entry-id>` (`board-run.md:70`) | entry closed | **A3 — even the win needs a manual final flip.** |

---

## 2 — Time-to-first-win: today vs achievable minimum

**Today (to the _real_ win — an agent resolving a card):**
~**11 steps · 2 session restarts · 2 "end-a-turn" waits · 1 invisible step · 3 mode
transitions.** Even the _lesser_ win (a visible promoted card, step 9) is ~10 steps
and the README's own measured **~10–15 minutes** — and the very first thing that
happens (step 7 capture) shows the user nothing.

**Achievable minimum (with a seed entry + guided demo — see §4):**
~**4 steps · 1 session · 0 restarts · 0 waits · 0 invisible steps:**
install (2) → `/board-setup` (scaffolds a **sample entry** + prints "watch it work")
→ `/board-run SAMPLE-B001` → watch an agent drive it to validated. **~2 minutes to
the "aha," with zero real work required first.** Then tee up capture-your-own.

The gap between 11 steps and 4 is almost entirely **deferrable tax**: the restart,
the mode dance, the turn-end waits, and the "go do real work before you can see
anything" requirement are all *before* the win and could move *after* it.

---

## 3 — Findings

Format: **lens · location · what the newcomer feels · the fix · effort (S/M/L).**
Ranked by distance to the first win (the most expensive friction first).

### A1 — The first value is invisible by design
- **Lens:** Empty states that teach (1) · Time-to-first-win (2)
- **Location:** `README.md:79,85`; `board-session-start.sh:95` "(none yet — findings are captured automatically…)". Capture writes silently to `_sessions/`.
- **Feels:** _"I installed it, I worked, and… nothing showed up. Is it broken?"_ The single most novel behavior (the board fills itself) produces **no visible confirmation** the first time it runs — the user is told to go "peek at a folder."
- **Fix:** Make the first capture *say so* — a one-line, non-intrusive confirmation on the turn it happens ("engineering-board: captured 1 finding to the inbox — run `/pm-start` to promote it, or `/board-view` to look"). Quiet ≠ silent; a newcomer needs one heartbeat that it worked.
- **Effort: S.**

### A2 — Blank canvas: no seed or sample to see it work
- **Lens:** Seed and sample data (4) · Guided first action (3)
- **Location:** `/board-init` scaffolds `## Open (none)` (`board-init.md:60`); no `sample`/`demo`/`seed` entry exists anywhere (verified). The SessionStart empty state describes emptiness.
- **Feels:** _"Now what?"_ There is nothing to watch the pipeline work on until the user has done the work of capturing **and** promoting their own entry — so the product's best moment is unreachable on day one without real effort.
- **Fix:** Have `/board-setup` optionally scaffold **one realistic sample entry** (a toy bug in a scratch file, clearly labeled `SAMPLE`) so `/board-run SAMPLE-B001` works immediately. **Sample data beats a blank canvas** — let them watch before they build.
- **Effort: M.**

### A3 — The mode dance is setup tax stacked before the win
- **Lens:** Setup tax (5) · Time-to-first-win (2)
- **Location:** `/pm-start` sets PM mode (`pm-start.md:2`); `/board-run`'s guard rejects non-passive sessions (`board-run.md:14-16`); "one session, one mode" (`README.md:83`) forces a fresh session to switch; `/board-resolve` is a separate manual close (`board-run.md:70`).
- **Feels:** _"To see it work I have to enter a mode, end a turn, start a new session to leave the mode, run a command, then run another to finish?"_ Each transition is a place to stall or give up.
- **Fix:** Route the newcomer through the **mode-free** path first: `/board-run` needs no mode and no restart. Lead onboarding with it (against the seed entry), and defer `/pm-start`/worker-mode to "when you want to batch." The modes are for scale, not for the first win.
- **Effort: S** (sequencing/guidance) — the mechanism already exists.

### A4 — A Claude Code restart is required right after scaffolding
- **Lens:** Setup tax (5)
- **Location:** `board-init.md:120` "Restart Claude Code (or open a new session) so the SessionStart hook picks up the new layout."
- **Feels:** _"I just set it up and now I have to restart before it does anything?"_ A restart mid-flow is a classic momentum-killer.
- **Fix:** Where possible, make `/board-setup` leave the session usable immediately for the seed-demo path (`/board-run` is a foreground command that doesn't depend on the SessionStart banner), and phrase the restart as optional-for-the-banner rather than required-to-proceed.
- **Effort: S** (guidance) / **M** (if truly decoupling hook pickup).

### A5 — "End a turn" is an unexplained, unintuitive trigger
- **Lens:** Progress and reassurance (7) · Guided first action (3)
- **Location:** `README.md:80-81` "then end a turn"; `pm-start.md:77,85` "Stop hook will route through PM continuation each turn."
- **Feels:** _"I ran the command and nothing happened."_ Value fires on the **Stop hook** (turn-end), but a newcomer doesn't know that ending a reply is what triggers work, so they wait on a command that already "finished."
- **Fix:** When `/pm-start` is set, have the command's confirmation say plainly: _"Nothing runs yet — finish your next reply (end the turn) and I'll consolidate then."_ Name the trigger in plain words at the moment it matters.
- **Effort: S.**

### A6 — No "try it now" — the first win requires real work first
- **Lens:** Guided first action (3) · Seed and sample data (4)
- **Location:** Capture is a side-effect of genuine working sessions (`README.md:79`); there is no demo path.
- **Feels:** _"I want to see it work, but I have nothing to capture yet."_ The evaluator who installs to kick the tires hits a wall — the product needs real work to have happened before it shows anything.
- **Fix:** The seed entry (A2) *is* the "try it now." `/board-setup` → `/board-run SAMPLE` gives an instant, work-free demonstration of the actual pipeline.
- **Effort:** folded into A2.

### What already works (protect it)
- **`/board-setup`'s 3-line summary** (`board-setup.md:38-44`) is genuinely reassuring and idempotent — a good landing after install.
- **The SessionStart banner** (`board-session-start.sh`) answers "where am I" well: current mode, open counts, in-progress warnings, learnings. Strong on **progress/reassurance (lens 7)** once there's content.
- **False-start recovery (lens 8) is decent:** mode guards print helpful, specific decline messages ("currently in PM mode… start a fresh session", `board-run.md:14`); recovery is documented (delete `session-mode.json`, `README.md:83`). It's manual on local installs but never traps the user silently.
- **The next-step chain exists:** setup → `/pm-start`; `/board-run` → `/board-resolve`; the banner suggests actions. The links are there — they're just gated by A3/A4/A5.

---

## 4 — The one change

**Seed a labeled sample entry at `/board-setup`, and make the guided first action
`/board-run SAMPLE-B001` — so a newcomer watches an agent drive a real card
`tdd → review → validate` to validated in one command, one session, no restart, no
mode, no waiting.**

This single change collapses the walk from **~11 steps / 2 restarts / 1 invisible
step** to **~4 steps / 0 restarts / a visible "aha" in ~2 minutes**, because it:
- replaces the **blank canvas** (A2) with something to watch;
- routes around the **mode dance** (A3), the **restart** (A4), and the **turn-end
  wait** (A5) via the already-existing mode-free `/board-run`;
- makes the product's best moment — the pipeline actually working — the *first*
  thing a user sees instead of the last.

**The second step it must tee up:** the win is a *sample*; the habit is *their own
work*. `/board-run`'s success report should immediately pivot:

> _"That was a sample. Now the real thing: just keep coding — engineering-board
> quietly captures the bugs and ideas you and your agent surface. When you're
> ready, run `/pm-start` and end a turn to promote them to your board."_

That converts a one-off demo into the actual daily loop (capture → promote → run),
so activation doesn't die at a single win — it hands off to tomorrow's habit. Pair
with A1 (a one-line capture confirmation) so the newcomer's *first real* finding
also gives a visible heartbeat.

---

_Report only. **Which fixes would you like me to make?** Recommendation: ship the
**one change** first — the seed entry + `/board-run SAMPLE` guided path (A2/A6,
effort M) — it moves the most newcomers to a first win. Then **A1** (capture
confirmation) and **A5** (name the turn-end trigger) as S-effort follow-ons that
make the real daily loop legible. A3/A4 are sequencing/guidance edits that fall out
of leading with the mode-free path._
