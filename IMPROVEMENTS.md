# IMPROVEMENTS — product discovery pass v2 (2026-07-06, post-1.5.0)

_Discovery only; nothing in this report is implemented. Every idea cites evidence
from this repo. **v1 of this report (same date) was built in full and shipped as
[v1.5.0](https://github.com/GhostlyGawd/engineering-board/releases/tag/v1.5.0)
(PRs #67–#77)** — this v2 pass re-audits the repo as it now stands: the residual
open backlog, the findings from the v1 design audits that were deliberately not
taken, and the new opportunities the v1 ships created._

## 1. Product snapshot

engineering-board turns a committed markdown tree (`engineering-board/<project>/`)
into a kanban board AI agents run themselves: passive per-turn capture, a PM mode
that promotes findings into validated entries **with drafted Done-when criteria**,
a Worker mode for batch discipline runs, and — since 1.5.0 — `/board-run`, which
drives one entry `tdd → review → validate` in a single session under claim lock.
It ships as a Claude Code plugin (13 commands, one-command `/board-setup`
onboarding) and a zero-dependency MCP server (11 tools, CI-proven multi-client),
released and listed on the official MCP Registry at 1.5.0. The journey is now:
install → `/board-setup` → first capture announced on the turn it happens →
`/pm-start` promotes → `/board-run` builds — with the roadmap public at the
[live board](https://ghostlygawd.github.io/engineering-board/board.html) and
adoption tracked weekly into a committed `docs/metrics.csv`. Underused assets
today: the metrics data has no visible surface, the MCP side has no onboarding
twin, and the Conductor's inner loop exists while its supervisor is still a
draft RFC.

## 2. Opportunity map

| | **Low effort (S)** | **Medium (M)** | **Large (L)** |
|---|---|---|---|
| **High impact** | #1 token dedup + drift lint | #8 `board_setup` MCP twin · #9 board-run driver script | #12 Conductor supervisor |
| **Med impact** | #2 viewer type floor · #3 B057 count fix · #4 metrics surface · #5 good-first-issue seeding | #10 F003 remainder (PM-summary learnings) · #11 terminal demo pipeline | |
| **Lower / focused** | #6 B021 code-reviewer rename | #7 B020 migrate split + B022 pipeline honesty | |

## 3. Top 5 quick wins (~a day or less each)

1. **#1 Token dedup + drift lint** — delete the dead third token copy and add a check so the landing page's inline token mirror can never silently diverge from `brand/tokens.css`.
2. **#3 B057 scratch-count fix** — the banner's headline number undercounts multi-finding blocks; a counting bug in the product's most-seen line.
3. **#4 Surface the metrics** — `docs/metrics.csv` accrues weekly rows nobody can see; link it from the landing footer and README Community section as "adoption data, public like everything else."
4. **#2 Viewer type floor** — raise the 0.58–0.68rem micro-type in the board view to a readable floor; the live board is now a public surface.
5. **#5 Seed good-first-issues** — CONTRIBUTING.md points newcomers at a `good first issue` label that has zero issues behind it; open 3–5 from the open P3s.

## 4. Top 3 big bets

1. **#12 Conductor supervisor (RFC 0001, the remaining half)** — `/board-run` shipped the inner loop; the supervisor that schedules it across sessions is now a much smaller build than the original RFC scoped.
2. **#8 + #9 MCP onboarding parity + testable run-driver** — a `board_setup` MCP tool (named in F002's own spec, never built) and extracting `/board-run`'s claim/loop mechanics into a deterministic script so the pipeline's flagship command gains real test coverage (per Learning L001).
3. **#11 Real terminal demo pipeline** — the original launch-spec item still unshipped: a scripted asciinema→GIF of `/board-setup → capture → /pm-start → /board-run` beats the static SVG for conversion.

## 5. Full opportunity list

### #1 — One token source: delete the dead copy, lint the mirror
- **Tag/lens:** FIX · fixes & felt debt
- **Evidence:** `docs/assets/tokens.css` is committed but referenced by nothing (verified: 0 matches for `assets/tokens.css` in `docs/index.html`, which uses its own inline `:root` mirror at `docs/index.html:30-57`); `brand/tokens.css:1-3` declares itself the "single source of truth". Three divergent copies (brand file, inline mirror, dead file) — the v1 audit flagged it (MED); the 1.5.0 work added tokens (`--eb-danger`, `--eb-card`) to `brand/tokens.css` and the viewer but the landing mirror grows staler with each such change.
- **Proposal:** delete `docs/assets/tokens.css`; add a small test that parses the inline `:root` block in `index.html` and asserts every shared variable's value matches `brand/tokens.css` (pure python3, fits the suite).
- **Why it matters:** the brand's core claim is "tokens single-source"; today it demonstrably isn't, and drift lands on the public page first.
- **Effort:** S · **Impact:** High (trust/consistency) · **Risks:** none — dead file plus an additive check.

### #2 — Readable type floor in the board view
- **Tag/lens:** IMPROVE · UI & beauty
- **Evidence:** `hooks/scripts/board-view.sh` still ships `font-size:.58rem` (`.conf`), three `.62rem` (`.tag`, `.lapplies`, rec), `.66rem`, `.68rem` — ~9px text, flagged MED in the v1 audit and deliberately not taken then. The view is now the public `/board.html`.
- **Proposal:** raise the floor to ~0.7rem across `.conf`/`.tag`/`.lapplies`/`.rec`/`.kind`; regenerate the committed board.
- **Effort:** S · **Impact:** Med · **Risks:** slight card-height growth; determinism test unaffected.

### #3 — B057: the banner's scratch count undercounts
- **Tag/lens:** FIX · feedback & state (open board entry, P3)
- **Evidence:** eb-self B057 — `count_scratch_findings` undercounts multi-finding blocks, so the SessionStart line ("N un-promoted session file(s)") can misstate the real pending volume; documented as a "labeled status lower-bound" since C9.
- **Proposal:** count findings, not blocks, in the counting helper; assert with a two-findings-in-one-block fixture.
- **Why it matters:** 1.5.0 made per-turn feedback honest; the last knowingly-wrong number on the banner should follow.
- **Effort:** S · **Impact:** Med · **Risks:** none.

### #4 — Make the adoption data visible
- **Tag/lens:** NEW · synergy (metrics workflow + landing page)
- **Evidence:** `.github/workflows/metrics.yml` appends weekly rows to `docs/metrics.csv`, but no surface links it — the landing footer (`docs/index.html:271+`) links Releases/Registry/Live board, not the data; README's Community section likewise.
- **Proposal:** add "Adoption data (CSV)" to the landing footer + README Community list now; once ≥8 rows exist, render a tiny sparkline on the landing page from the same file (no third-party scripts).
- **Why it matters:** "public adoption data" is an on-brand trust signal that costs one link today.
- **Effort:** S · **Impact:** Med · **Risks:** none for the link; sparkline waits for data.

### #5 — Seed the good-first-issue funnel
- **Tag/lens:** IMPROVE · community
- **Evidence:** `CONTRIBUTING.md` ("Look for issues labelled **good first issue**") points at a label with zero issues behind it; the open P3s (B016/B020/B021/B057) are exactly first-contribution-sized and already have reproductions and Done-whens on the board.
- **Proposal:** open 3–5 GitHub issues mirroring those board entries (linking each to its committed entry file), label them, and note in each that the board entry is the source of truth.
- **Why it matters:** the contribution path exists on paper only; the first outside PR never comes without a first issue to grab.
- **Effort:** S · **Impact:** Med · **Risks:** issue/board dual-tracking — mitigate by declaring the board entry canonical in each issue body.

### #6 — B021: rename `code-reviewer`
- **Tag/lens:** IMPROVE · friendliness (open board entry, P3)
- **Evidence:** eb-self B021 + RFC 0002 ("keep (rename)"): the agent name collides with the harness's `/code-review`, and its frontmatter lists Write/Edit despite a no-writes review contract.
- **Proposal:** rename to `review-worker` (or similar), narrow tools, keep a compatibility note; update the worker procedure + `/board-run` dispatch tables and the pinned lint strings together.
- **Effort:** S · **Impact:** Low–Med · **Risks:** several pins reference the name — one coordinated sweep (L005).

### #7 — B020 + B022: migrate split and pipeline honesty
- **Tag/lens:** IMPROVE · UX & flows (open board entries, P3)
- **Evidence:** B020 — `/board-migrate` bundles the v0.3.0 data migration and the 1.1.0 relocate under one verb; B022 — `nothing_to_test` / `nothing_to_review` still advance the entry (a worker can wave an entry through by declaring nothing to do).
- **Proposal:** split migrate into explicit modes (`--data`, `--relocate`, both documented in the usage string); make `nothing_to_*` route to `cannot_proceed` semantics (skip, don't advance) with a lint pin.
- **Effort:** M · **Impact:** Med (trust in the state machine) · **Risks:** B022 changes worker-loop behavior — needs the orchestration loop tests updated in step.

### #8 — `board_setup` MCP twin (onboarding parity)
- **Tag/lens:** NEW · helpfulness & reach
- **Evidence:** F002's own spec named "`/board-setup [project]` (mirror `board_setup` MCP tool)"; the command shipped in 1.5.0, the tool did not (verified: 0 matches for `board_setup` in `mcp-server/engineering_board_mcp.py`). MCP-only users (Claude Desktop) still onboard by calling `board_init` with the right arguments themselves.
- **Proposal:** a 12th tool composing `board_init` with the repo-basename default and returning the same 3-line ready summary (minus the plugin-only permission check, which doesn't apply to MCP clients).
- **Why it matters:** the registry listing is now the discovery front door; the first tool an MCP user reaches for should be the one-command start.
- **Effort:** M · **Impact:** High for the MCP funnel · **Risks:** tool count 11→12 ripples through README/ARCHITECTURE/registry description — coherence sweep required (Track D discipline).

### #9 — Make `/board-run` deterministically testable
- **Tag/lens:** IMPROVE · fixes & felt debt (applies Learning L001)
- **Evidence:** `commands/board-run.md` is prose the model executes; its only coverage is the structural lint (`tests/orchestration/board-run-command.sh`, 18 assertions). Learning L001 ("ship every deterministic guard with a test that drives its real fixtures and call-sites") is the board's own top lesson, and the claim/loop mechanics (acquire → rounds → transition → release) are exactly the deterministic part.
- **Proposal:** extract those mechanics into `hooks/scripts/board-run-driver.sh` (acquire, apply a supplied `suggested_next_needs`, heartbeat, release, round bound) that the command dispatches — then drive it in tests with stubbed agent outputs, the same pattern `board-mode-guard.sh` used to make mode transitions testable.
- **Effort:** M · **Impact:** High (the flagship command gains real regression coverage) · **Risks:** keep the command's prose thin so the lint and the script can't drift apart.

### #10 — F003 remainder: learnings in the PM-pass summary
- **Tag/lens:** IMPROVE · retention (open board entry, F003 partial)
- **Evidence:** F003's board annotation: "session-end PM-summary surfacing deferred". The 1.5.0 PM summary line (`PM pass: N promoted…`, stop-hook step (f)) now exists as the natural carrier — the deferral predates it.
- **Proposal:** when the PM pass promotes entries whose `affects`/`pattern` match an existing Learning's `applies_to`/`pattern_tag`, append one line: `Related learning: L004 — a denylist is never done.` (reuse the SessionStart matching logic).
- **Why it matters:** the moat surfaces at the exact moment new work enters the board — the third and last of F003's named moments.
- **Effort:** M · **Impact:** Med · **Risks:** false-positive matches train users to ignore it — keep the SessionStart medium+-confidence filter.

### #11 — Real terminal demo (asciinema → GIF)
- **Tag/lens:** NEW · reach & engagement
- **Evidence:** no `.gif`/`.cast` anywhere under `docs/` (verified); the animated `board-demo.svg` is a hand-built illustration, not the product running. The original launch spec's "animated demo of the real product" item was scope-cut in C1 (BLOCKERS B1: no nested interactive sessions in the sandbox) and never revisited — but 1.5.0's `/board-setup` + `/board-run` make the demo script itself only four commands long now.
- **Proposal:** a documented, repeatable demo script (`docs/demo/record.sh`) that a human runs once locally with asciinema, plus the conversion step; embed the GIF above the SVG in the README.
- **Effort:** M (mostly scripting + one human recording session) · **Impact:** Med–High for conversion · **Risks:** recording needs a real interactive session — the script preparation is automatable, the capture is not (same boundary as BLOCKERS B1; say so).

### #12 — The Conductor supervisor (RFC 0001, remaining half)
- **Tag/lens:** NEW · engagement & retention (big bet)
- **Evidence:** `docs/rfcs/0001-symphony-conductor.md` (Draft) minus what 1.5.0 already shipped: `/board-run` is the RFC's inner drive loop, claim-locked and bounded. What remains is the supervisor — pick the next entry, spawn/resume a session, run `/board-run`, repeat — which is now expressible as a scheduler over an existing command rather than a new execution model.
- **Proposal:** slice 2: a `--next` mode (`/board-run --next` picks the highest-priority workable entry itself); slice 3: the cross-session scheduler (Claude Code web triggers/cron driving `/board-run --next` per session), with the RFC's evidence-posting seams resolved then.
- **Why it matters:** "commit a bug to markdown and a PR appears" remains the demo that earns adoption, and the recorded open-core direction (RFC 0003) prices the hosted version of exactly this.
- **Effort:** L (slice 2: M) · **Impact:** High · **Risks:** the RFC's §10 seams (credentials, round boundaries) apply from slice 3 on; slice 2 has none of them.

## 6. Suggested sequence — if only three ship first

1. **#1 token dedup + drift lint** — smallest change that protects the brand's core "single source" claim on the most public surface; unblocks confident future token work.
2. **#9 board-run driver script** — the flagship command is the product's new center of gravity; giving it deterministic coverage before building `--next` (#12 slice 2) on top of it is the L001 lesson applied forward.
3. **#8 `board_setup` MCP twin** — the registry listing is now live distribution; parity onboarding converts the traffic it brings.

---

_All 12 items trace to a file/line, an open board entry, or a verified absence;
nothing is hypothetical. Items #1/#2 revisit v1 audit findings deliberately not
taken then; #3/#5/#6/#7/#10 come from the live residual backlog; #8/#9/#11/#12
are the follow-on opportunities the 1.5.0 ships created._
