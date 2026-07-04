# /goal — Product development & improvement loop: make engineering-board a seamless, high-PMF experience

## Mission

`engineering-board` v1.2.0 is launched: dual-distributed (Claude Code plugin + MCP server), branded, tested (11 CI suites), with a live landing page (https://ghostlygawd.github.io/engineering-board/). That run proved the *mechanics* work. This run's job is to prove — and where it falls short, build — the *experience*: a product a stranger installs in two minutes, understands in five, and trusts with their engineering workflow by the end of day one.

Run fully autonomously in repeating improvement cycles. You are simultaneously the red team, the product manager, the UX critic, the engineer, and the docs owner. The run ends only when the Convergence Criteria at the bottom are met — not when a fixed checklist is done.

**Read first, in order:** `state.md` (repo handoff conventions — binding), `.goal/FINAL_REPORT.md`, `.goal/POSITIONING.md`, `.goal/BLOCKERS.md`, `.goal/PRODUCT_FACTS.md`. Do not re-derive what they already establish.

---

## Operating rules (non-negotiable)

1. **Dogfood as the validation engine.** Run the product on itself: `/board-init eb-self` in this repo (or via the MCP tools). Every finding from every track below enters the board as a real entry and flows through the real `tdd → review → validate` state machine. If dogfooding is painful, that pain is itself a top-priority finding. The committed `engineering-board/eb-self/` tree is the run's living backlog AND its best demo artifact.
2. **Experience over features.** Before building anything new, you must be able to state: the persona, the moment of need, the current friction (measured or reproduced, not imagined), and why this beats the next-best alternative. Features that can't clear that bar get written down and rejected — a decided "no" is a deliverable.
3. **Every feature is challengeable, including existing ones.** Nothing shipped is sacred. If a command, agent, hook, or flow doesn't survive a first-principles "would we build this today, this way?" review, simplify, merge, or deprecate it (with a migration path). Removal PRs are as valuable as feature PRs.
4. **Evidence over claims.** Every finding needs a reproduction; every fix needs a test; every UX claim needs a walkthrough transcript or measurement; everything lands in `.goal/evidence/loop/` with cycle-numbered filenames.
5. **Ship in small PRs, merged continuously.** One coherent change per PR to `main` via the GitHub MCP (branch → CI green → un-draft → merge). Never push `main` directly. Keep `bash tests/run-all.sh` green — it is the merge gate. New behavior ships with tests; changed behavior ships with changed tests.
6. **Resumability.** Maintain `.goal/LOOP_PROGRESS.md`: current cycle number, per-track status, backlog snapshot pointer (the board itself is the backlog), and evidence links. A fresh session must resume from it alone.
7. **Honest failure & honest limits.** Unresolvable items go to `.goal/BLOCKERS.md` with what was tried. Do not simulate results you couldn't produce. Real PMF requires real users — where validation is simulated (personas, fresh-install audits), label it as simulated and prepare the channels that will capture real signal.
8. **Respect the pinned surface.** Tests pin literal tokens in `hooks/stop-hook-procedure.md`, the untrusted-data framing string in 10 prompt files, version lockstep between the two manifests, and crosscompat rules for `hooks/scripts/*.sh` (bash shebang, no jq, no `date -d`). Read the relevant test before editing anything it pins.
9. **Version discipline.** Bump `plugin.json` + `marketplace.json` together; users only receive fixes when the version increases. Batch merged work into meaningful releases (1.3.0, 1.4.0…) with `CHANGELOG.md` entries; note that publishing the git tag itself is human-gated (see Environment notes).

---

## The cycle (repeat until convergence)

Each cycle is numbered (C1, C2, …) and has six steps. Log each cycle's outcome in `LOOP_PROGRESS.md` before starting the next.

### 1. DISCOVER — four tracks, run all four every cycle

**Track A — Red team & hardening.**
Attack the product as a skeptical senior engineer and as an adversary:
- Prompt-injection: can crafted board entries, scratch findings, or router rows make an orchestrating agent do something the user didn't ask? (There are 30 adversarial fixtures in `tests/fixtures/adversarial-paste/` — extend them.)
- Failure modes: corrupt/truncated state files (`session-mode.json` fail-open is a known, deferred defect — D4 in PRODUCT_FACTS), interrupted writes, claim races under parallelism, cloud-sync latency, missing `python3`, huge boards (1000+ entries — measure hook latency), concurrent PM+Worker sessions on one board.
- Fresh-eyes install: clean environment, follow only the README. Every stumble, unclear step, or silent failure is a finding with severity.

**Track B — UX & first-principles product critique.**
Walk the three personas from POSITIONING.md (solo agentic dev, small-team lead, OSS maintainer) through their actual day-one and day-seven journeys, executing the flows for real:
- Measure time-to-first-value: minutes from install → first finding captured → first entry promoted → first autonomous fix. Where is the cliff?
- Question every surface: 10 commands, 8 agents, 4 skills, 11 MCP tools, the permission-installer flow, the mode-transition refusal matrix, entry frontmatter requirements. For each: is the name right? is the mental model learnable? could two things be one thing? does an error message tell the user what to do next? Would a first-time user know why the Stop hook just did what it did?
- The onboarding question specifically: today a new user must add a marketplace, install, grant permissions, run `/board-init`, and understand modes before value appears. Design the shortest honest path and build toward it.

**Track C — PM-level feature development.**
From the competitive gaps and persona needs, maintain a ranked opportunity list. Known seeds (validate before building; kill freely):
- **Board visibility**: Backlog.md wins on its Kanban TUI/visualizer; Agent-MCP on its live dashboard. Ours is markdown-only. Options to evaluate: a zero-dep local HTML board viewer (could reuse the landing page's board demo components), a `board_render` MCP tool, richer `/board-graph` output, or a README-embeddable auto-generated board SVG.
- **Animated demo**: the README still has no animated demo of the real product (original launch spec item, never shipped). A scripted asciinema/GIF of capture → promote → autonomous fix would do more for conversion than any copy.
- **Onboarding wizard**: one command (or one MCP tool) that takes a fresh repo to a working board with sensible defaults and prints what it did.
- **Learnings surfacing**: Learnings (L###) are the moat — are they actually reaching the user at the right moment, or buried? Explore surfacing them in PR descriptions, session summaries, or the board viewer.
- **Multi-client story**: same board driven from Claude Code + Claude Desktop simultaneously — test it, fix what breaks, then document it as a differentiator.
Each candidate gets a one-page mini-RFC (problem, persona, evidence of need, smallest shippable slice, kill criteria) in `docs/rfcs/` before code.

**Track D — Surface coherence.**
After each cycle's changes: README, landing page, ARCHITECTURE.md, BRAND voice, CHANGELOG, and the board demo must still tell one true story. Marketing claims must match shipped behavior exactly (rule: cut copy, never ship vaporware). Re-run the link check and Lighthouse (mirror technique documented in `.goal/evidence/G4-live-verification.txt`) when the site changes.

### 2. DECIDE
Intake all discoveries onto the `eb-self` board with severity/priority. Then choose the cycle's slate: all new blockers/majors, the highest-leverage UX fix, and at most one feature slice. Record what you deliberately deferred and why.

### 3. BUILD
Work the slate through the board's own state machine (dogfood). TDD where the substrate is deterministic; walkthrough-verified where it's prompt/UX.

### 4. VERIFY
`bash tests/run-all.sh` green; re-run the specific reproductions from DISCOVER to prove them fixed; for UX changes, re-run the persona walkthrough and re-measure time-to-first-value; capture evidence.

### 5. SHIP
PR(s) → CI green → merge via GitHub MCP. Update CHANGELOG under an Unreleased/next-version heading. Sync surfaces (Track D). Update `state.md` snapshot when the change is significant (fold into the real PR, never a bookkeeping-only one).

### 6. REFLECT
Write the cycle retro in `LOOP_PROGRESS.md`: what the cycle proved, what it disproved, whether any positioning claim needs revision, and the updated convergence scorecard (below). Promote recurring lessons into real Learnings on the `eb-self` board — the product should be accumulating its own memory about itself.

---

## Convergence criteria (Definition of Done)

The run is complete when ALL of these hold, evidenced in `LOOP_PROGRESS.md`:

1. **Two consecutive full cycles** (all four DISCOVER tracks executed with real effort — show the work) produce **zero new blocker, major, or P0/P1 findings**.
2. The `eb-self` board has **no open blocker/major/P0/P1 entries**; every remaining open entry is P2/P3 with an explicit "why deferred" note, or promoted to the public roadmap.
3. **Time-to-first-value is measured, documented, and defensible**: a fresh-install persona reaches first captured finding in ≤ 5 minutes and first promoted entry in ≤ 15, following only public docs — or the honest number plus the friction analysis lives in the README's expectations.
4. Every shipped surface (commands, agents, skills, MCP tools) has survived an explicit keep/simplify/merge/deprecate decision, recorded in one `docs/rfcs/` product-review doc.
5. README + landing page + CHANGELOG + positioning are coherent with shipped reality, link-checked, Lighthouse ≥ 95 across categories, and the README has a real animated demo of the real product.
6. A release version is batched, CHANGELOG'd, and manifests bumped; `.goal/BLOCKERS.md` contains only human-gated or explicitly-accepted items; `.goal/FINAL_REPORT.md` gets a closing "improvement loop" section: cycles run, what changed, what was killed and why, PMF evidence and its limits, and the instrumented channels awaiting real users.

---

## Environment notes (learned the hard way — trust these)

- Land everything via PR; merge with the GitHub MCP tools (`create_pull_request` draft → CI `run-all` green → `update_pull_request` draft:false → `merge_pull_request`). The sandbox git relay allows **branch** pushes but **rejects tag pushes** — releases/tags stay human-gated in BLOCKERS.
- GitHub Pages serves from the **`gh-pages` branch**; `.github/workflows/pages.yml` auto-syncs `docs/{index.html,assets,.nojekyll}` on `main` pushes. Don't switch to actions/deploy-pages — the workflow token cannot manage the Pages site ("Resource not accessible by integration").
- You **cannot run a nested interactive Claude Code session** (2-min cap) — plugin-in-session E2E stays simulated + `claude plugin validate` + suite coverage; say so in evidence. Direct api.github.com calls are blocked; use the MCP tools. Lighthouse against the live HTTPS URL hits a TLS interstitial — use the curl-mirror technique from `evidence/G4-live-verification.txt`.
- `mcp-server/run-tests.sh` is CI suite #11; the MCP server reads its version from `plugin.json`.
- Repo-metadata (description/topics/social preview) is Settings-UI-only; channel submissions need human accounts. Both are out of scope — keep them current in LAUNCH.md instead.

## Loop mechanics

Self-pace with ScheduleWakeup (re-arm each turn with this same /loop input; prefer completing a full cycle step before yielding). Commit and push work-in-progress before any long pause — the container is ephemeral. If interrupted, resume from `.goal/LOOP_PROGRESS.md` and the `eb-self` board. Stop re-arming only when the Convergence Criteria pass — then deliver the final summary.
