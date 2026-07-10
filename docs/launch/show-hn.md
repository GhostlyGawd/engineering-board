# Show HN draft — engineering-board

_Launch asset (IMPROVEMENTS.md v4, C11). This is a draft to paste, not a page to
publish. Fire only after the comparison rebuild (C1/C2), proof badges (C9), and
the one-command install (C3) are live on `main` — otherwise the traffic lands on
a stale story. Submitting is a human action (an HN account with some history
reads better than a fresh one)._

Submission URL: <https://news.ycombinator.com/submit>
Link field: <https://github.com/GhostlyGawd/engineering-board>

---

## Title options (pick one, ≤ 80 chars)

1. `Show HN: The board is the database – a git kanban your AI agents run` _(68 chars)_
2. `Show HN: Engineering-board – a kanban your coding agents fill in themselves` _(75 chars)_
3. `Show HN: I keep my AI agents' task board as markdown in the repo` _(64 chars)_

Option 1 leads with the thesis; option 3 is the most HN-native "I did a thing"
framing. Avoid superlatives in all cases — HN titles get flagged for them.

## Body (paste as the submission text)

I built engineering-board because my Claude Code sessions kept ending with "I
also noticed three other issues" — and then the session ended and the issues
evaporated. It's a kanban board that lives as plain markdown inside your repo:
a Stop hook passively captures the bugs and ideas the agent surfaces each turn,
you promote the ones worth keeping into real cards, and worker agents drive each
card through a tdd → review → validate state machine under an atomic claim lock
so parallel agents don't collide. Recurring lessons get promoted into committed
"Learning" entries that survive session boundaries.

The storage model is the actual point, not an implementation detail. Everything —
cards, work-in-progress locks, learnings, the rendered board — is markdown and
plain files committed to git. That means your agents' coordination state shows up
in the same PRs as the code they wrote, your teammates can read it without
installing anything, `git blame` works on your agent's memory, and there's no
server, daemon, or database that can disappear out from under you. It ships as a
Claude Code plugin and as a zero-dependency Python MCP server, so any MCP client
can work the same board.

It's built in the open on its own board: the repo's real board — captured
findings, claim locks, learnings and all — is committed in the repo and published
as a static page on every merge, so you can see exactly what the tool produces
before installing it. MIT licensed. I'd genuinely like to hear where the model
breaks down for you.

Live board: https://ghostlygawd.github.io/engineering-board/board.html

## Prepared first comment (post immediately after submitting)

Author here — a few questions I expect, answered up front:

**Why not Claude Code's built-in Tasks?** They're good, and they do persist
across sessions — but they live in `~/.claude/tasks/`: per-user, per-machine,
outside the repo. Invisible in PRs, invisible to teammates, no capture pipeline,
no review states, no committed learnings. Use native Tasks for personal
in-session tracking; engineering-board is the *repo's* shared board — the durable
state everyone (human or agent) sees. They compose fine.

**Why not beads?** beads is excellent and much bigger than this project — durable
memory (`bd remember`/`bd prime`) and atomic claims are its headline, at ~25k
stars. The difference is the storage model: beads runs on Dolt with JSONL export;
engineering-board's state *is* plain markdown in your tree — no runtime between
you and your data, reviewable in the PR diff. We're also opinionated about one
pipeline (Claude Code hooks driving tdd → review → validate) rather than being a
general substrate. If you want a graph issue DB at scale, use beads.

**Why not Backlog.md?** Also excellent — the richest markdown task model in the
field and the closest overall shape. Backlog.md is a task manager you drive;
engineering-board is a board that fills itself in: passive per-turn capture of
what the agent noticed, an opinionated tdd → review → validate pipeline that
works the cards, and learnings that accumulate as committed memory. Different
job, honestly overlapping ground.

**Known limits, honestly:** it's a young project, built solo. The claim-locking
path is the concurrency-hardened part; the rest of the engine has a public
hardening backlog — on the board itself, where you can read it. Traction is
small; what I can show instead is cadence (releases, changelog) and the live
dogfooded board.

## Launch-day checklist

- [ ] **Timing:** submit a weekday morning US Eastern (roughly 8–10am ET);
      avoid Fri/Sat/Sun and holiday weeks.
- [ ] Post the prepared first comment within minutes of submitting.
- [ ] **Respond:** stay available for 4–6 hours; answer every substantive
      question; concede valid criticism plainly (the honest-comparison voice is
      the brand — it must hold under fire); never argue tone.
- [ ] If it doesn't get traction, let it die quietly — one re-submission weeks
      later is acceptable HN practice; vote-nudging is not.
- [ ] **What NOT to claim:** no invented user/star/download numbers; don't claim
      competitors lack things they ship (beads HAS memory and atomic claims;
      native Tasks DO persist across sessions); don't call anything "the first"
      or "the only" beyond the storage-model claim we can defend (plain-markdown,
      PR-reviewable board state); don't disparage vibe-kanban or any sunsetting
      project.
- [ ] Update README/landing links only after the thread exists (no "as seen on
      HN" pre-baking).
