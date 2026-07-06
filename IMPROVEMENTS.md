# IMPROVEMENTS — product discovery pass (2026-07-06)

_Discovery only; nothing here is implemented. Every idea cites evidence from this
repo. Generated from a fresh 12-lens audit (two independent design/UX audits of
the HTML artifacts and command microcopy, plus the live `eb-self` backlog and a
verification pass on each headline claim)._

## 1. Product snapshot

engineering-board turns a committed markdown tree (`engineering-board/<project>/`)
into a kanban board that AI agents run themselves: a Stop-hook pipeline passively
captures findings from every Claude Code session, a PM mode promotes them into
validated board entries, and a Worker mode drives entries through a
`tdd → review → validate` state machine with atomic claim-locking — all state
committed, diffable, and reviewed in the same PRs as code ("the board is the
database"). It ships as a Claude Code plugin and a zero-dependency MCP server,
released at v1.4.0 with a live landing page and an official MCP Registry listing.
The current journey: install from the repo marketplace → `/board-init` →
passive capture surfaces a first finding in ~5 minutes (`EB-CAPTURE-SUMMARY`
line) → `/pm-start` promotes it → a fresh session's `/worker-start` builds it.
The audience is solo agentic developers, small team leads, and OSS maintainers
(`.goal/POSITIONING.md`). Underused assets: the Pages deploy pipeline only
publishes the landing page, the `/board-view` HTML viewer is invisible outside a
local clone, and Learnings (`L###`) — the stated moat — reach users on only two
of the surfaces that could carry them.

## 2. Opportunity map

| | **Low effort (S)** | **Medium (M)** | **Large (L)** |
|---|---|---|---|
| **High impact** | #1 sentinel/feedback pass · #3 publish the live board · #11 fail-loudly cluster | #4 Done-when synthesis · #9 `/board-setup` wizard | #13 Conductor |
| **Med impact** | #2 dark-mode badge + tokens · #5 reclaim visibility · #6 banner readability · #14 traffic snapshot | #7 landing refresh · #8 viewer affordances · #12 single consolidation engine | |
| **Lower / focused** | | #10 multi-client story (Q001) | |

## 3. Top 5 quick wins (~a day or less each)

1. **#3 Publish the live board** — one path added to an existing workflow turns the committed `board.html` into a public, always-current roadmap the README currently apologizes for.
2. **#1 Sentinel & feedback pass** — every raw `<<EB-*>>` token a user can see gets a plain-language companion line; the flagship loop stops looking like debug output.
3. **#11 Fail-loudly cluster (B008+B009)** — the two known silent-failure paths (corrupt mode file, missing python3) start telling the user what happened.
4. **#2 Dark-mode blocked badge + token upstreaming** — a measured 2.96:1 contrast failure in the product's best demo artifact, plus the viewer minting colors the brand tokens should own.
5. **#6 Banner readability** — the first screen every session sees loses its wall-of-text line, gains an empty-state hint and a sigil legend.

## 4. Top 3 big bets

1. **#13 The Conductor (RFC 0001)** — an orchestrator that drives entries across all three disciplines without per-session restarts; subsumes the largest documented UX friction (B006) and is the demo that sells the product.
2. **#9 `/board-setup` onboarding wizard (F002 + B030)** — collapses install→value from 4 commands + a 17-line permission paste into one command with smart defaults.
3. **#12 Single consolidation engine (B014)** — the promotion path exists twice (agent prompt + shell script) with duplicated supersession logic; merging them removes the product's biggest correctness-drift risk.

## 5. Full opportunity list

### #1 — Plain-language companions for every user-visible sentinel
- **Tag/lens:** FIX · feedback & state
- **Evidence:** `hooks/stop-hook-procedure.md:68` ends the passive turn with a raw `<<EB-PASSIVE-DONE>>` as the final message; `:113` emits `<<EB-WORKER-NOTHING-TO-DO>>` with no translation; while paused, every turn emits bare `<<EB-PASSIVE-PAUSED>>` (`commands/board-pause.md:83`). The sentinels are load-bearing (the Stop-hook loop guard greps them — `tests/modes/stop-hook-mode-routing.sh` pins all 10), so they cannot be removed.
- **Proposal:** keep every sentinel byte-exact, but require a plain-language line alongside each user-visible one: "Nothing captured this turn." / "No tdd tasks left — worker is idle." / a quiet paused indicator. Also verify the `/board-resolve` next-action string added in 1.4.0 matches how the skill is actually invoked (`README.md:131` lists it as a skill, not a command).
- **Why it matters:** the autonomous loop is the product's core; today its per-turn output reads as internal debug tokens.
- **Effort:** S · **Impact:** High · **Risks:** modes-suite pins the literal tokens — edits must be additive prose (pattern already proven in 1.3.0/1.4.0).

### #2 — Dark-mode blocked badge + upstream the viewer's colors into tokens
- **Tag/lens:** FIX · UI & beauty
- **Evidence:** `hooks/scripts/board-view.sh:280` hardcodes `.badge.blocked{color:#B23A2E}` with no dark override — measured **2.96:1** on the dark background (needs 4.5:1). The viewer also mints `--eb-card` values (`:239,246,251`) that don't exist in `brand/tokens.css`, and `docs/index.html:146-147` hardcodes code-block colors; `docs/assets/tokens.css` is a third, unreferenced token copy.
- **Proposal:** add `--eb-card` and `--eb-danger` (light+dark) to `brand/tokens.css`, use them in the viewer, add the dark-mode blocked color, and delete or actually reference `docs/assets/tokens.css`.
- **Why it matters:** the viewer is the committed demo artifact; an unreadable "blocked" badge in dark mode (most developers' default) undercuts the "premium through restraint" brand claim.
- **Effort:** S · **Impact:** Med · **Risks:** viewer output is byte-deterministic and pinned by `tests/view/` — regenerate `eb-self/board.html` in the same change.

### #3 — Publish the live board (the roadmap becomes a URL)
- **Tag/lens:** NEW · community & synergy
- **Evidence:** `.github/workflows/pages.yml:17-19` syncs only `docs/{index.html,assets,.nojekyll}` to Pages; `README.md:23` links the committed `board.html` with the apology "(open it locally to render)"; the README's Community section already names the eb-self board as the public roadmap.
- **Proposal:** add `engineering-board/eb-self/board.html` to the pages sync (e.g. served at `/board.html`), link it from the README hero and the landing page. Every `/board-view` refresh on `main` updates the public roadmap automatically.
- **Why it matters:** "our roadmap is run by the product" becomes a clickable proof instead of a claim; every share of the link demos the product. Cheapest community/viral surface available.
- **Effort:** S · **Impact:** High · **Risks:** none significant — static HTML, already committed, already XSS-escaped.

### #4 — Consolidator writes real Done-when criteria, not a TODO placeholder
- **Tag/lens:** FIX · helpfulness & synergy
- **Evidence:** `hooks/scripts/board-consolidate.sh:365` writes `<!-- TODO — define completion criteria. -->` into every promoted bug/feature/question; `agents/validator.md:63` declares `cannot_proceed` for entries lacking a usable `## Done when`. Auto-promoted findings therefore flow into the worker pipeline pre-stalled unless a human hand-edits each entry.
- **Proposal:** the consolidator agent (an LLM with the finding's title + evidence in hand) drafts one or two concrete, testable Done-when bullets at promotion time; the deterministic script keeps the placeholder only as a fallback. The PM turn summary counts entries still carrying the placeholder.
- **Why it matters:** closes the gap between "captured" and "workable" — the pipeline's headline promise — without any new surface.
- **Effort:** M · **Impact:** High · **Risks:** LLM-drafted criteria vary in quality; mitigate with the existing untrusted-data framing and by marking drafted criteria as such.

### #5 — Make stale-claim reclamation visible
- **Tag/lens:** IMPROVE · feedback & trust
- **Evidence:** `hooks/scripts/board-claim-reclaim-stale.sh:141` `rm -rf`s another session's claim; output is JSON consumed by the hook (`:146-151`), never surfaced. The owner is archived to `_reclaimed.log` but the user is never told a claim was force-taken.
- **Proposal:** when the worker path reclaims a claim, add one plain line to the turn output ("Reclaimed a stale claim on B017 from an inactive session — details in `_claims/_reclaimed.log`").
- **Why it matters:** it's the product's only destructive-ish automatic action; invisible destruction erodes exactly the trust the committed-state model is selling.
- **Effort:** S · **Impact:** Med · **Risks:** none — additive output.

### #6 — Banner readability pass
- **Tag/lens:** IMPROVE · user friendliness
- **Evidence:** `hooks/scripts/board-session-start.sh:166` packs four sentences + two code paths + an MCP aside into one un-wrapped line; `:83` empty state prints bare `(none)` with no next action; `:245` prints internal notation (`L004 [high / x3]`, `[BFQO]` sigils) with no legend; `:256` closes with a directive addressed to the model, not the user.
- **Proposal:** one-line scratch summary with details on a second indented line; `(none)` → "No open items yet — findings are captured automatically; run /pm-start to promote them."; expand sigils on first use; reword or drop the model-directive line.
- **Why it matters:** this is the first thing every session shows; it currently front-loads jargon at the exact moment a new user is deciding whether the product is comprehensible.
- **Effort:** S · **Impact:** Med · **Risks:** `tests/session-start/` pins some strings — extend, don't break.

### #7 — Landing-page refresh: show what shipped
- **Tag/lens:** IMPROVE · reach & UI
- **Evidence:** `docs/index.html` never states a version or links Releases (`:271-278`), doesn't link the MCP Registry listing it now has (`:252-264`), names `/board-view` only in a footnote (`:233`) and never shows the Learnings panel (the moat); `#demo-status` swaps text with no `aria-live` (`:187,309`); at ≤640px all nav anchors vanish with no menu (`:87`); only a dark `theme-color` (`:10`).
- **Proposal:** version pill linking Releases; "Listed on the MCP Registry" link; a viewer screenshot (or live `/board.html` link per #3) featuring the Learnings panel; `aria-live="polite"` on the demo status; keep nav anchors as a wrapped row on mobile; add a light `theme-color` variant.
- **Why it matters:** the page still sells the 1.2.0 story; the credibility artifacts that exist now (releases, registry, viewer) are its best conversion evidence.
- **Effort:** S–M · **Impact:** Med–High · **Risks:** re-run the Lighthouse mirror check after edits (loop convention).

### #8 — Viewer affordances: click-through, freshness, scale
- **Tag/lens:** IMPROVE · engagement
- **Evidence:** `hooks/scripts/board-view.sh:134-141` renders cards as plain `<div>`s — no link to the entry's markdown file the script already knows; no generation stamp anywhere (deliberate byte-determinism, `:4-6`) so readers can't judge freshness; the eb-self board's Done column renders 52 cards flat; `.affects` uses `word-break:break-all` (ugly mid-word breaks); no `@media print`.
- **Proposal:** wrap each card id in an `<a>` to its `.md` (relative link works on GitHub and Pages); an opt-in `--stamp` that footers the git short-sha (keeps default deterministic); collapse the Done column beyond ~10 with a count; `overflow-wrap:anywhere`; a small print block.
- **Why it matters:** the viewer graduates from screenshot to working surface — especially once it's public (#3).
- **Effort:** M · **Impact:** Med · **Risks:** determinism test must keep passing for the default mode.

### #9 — `/board-setup` onboarding wizard
- **Tag/lens:** NEW · onboarding (F002 + B030 on the board)
- **Evidence:** F002 entry: today's path is 4 manual commands + a ~17-line `claude config add` paste (B030: "6-step copy-paste loop… cannot be completed inside the session") before the pipeline runs unprompted. `commands/board-init.md:19` blocks on a missing project name that the repo directory basename could default (`:9` already derives a default prefix the same way).
- **Proposal:** per F002's own spec: `/board-setup [project]` infers the project from the repo dir, runs board-init with defaults, runs the permission self-check (prints the paste block only if needed), and ends with a 3-line "you're ready + next action" summary. Fold the smart-default into `/board-init` regardless.
- **Why it matters:** time-to-first-value is the retention cliff the improvement loop measured; this is the designed fix, still unbuilt.
- **Effort:** M · **Impact:** High · **Risks:** F002's kill criteria apply — if the permission paste is irreducible, demote to a board-init epilogue.

### #10 — Prove and document the multi-client story (Q001)
- **Tag/lens:** NEW · reach
- **Evidence:** Q001 on the board: "does driving one board from Claude Code + Claude Desktop simultaneously work?" — a listed differentiator (README VP5) that has never been exercised; the claim currently rests on the shared on-disk format alone.
- **Proposal:** run the experiment (two clients, one board, concurrent claims), fix what breaks, then document it as a README section with the locking behavior users should expect.
- **Effort:** M · **Impact:** Med · **Risks:** may surface real locking edge cases (that's the point).

### #11 — Fail-loudly cluster: mode file + python3 preflight
- **Tag/lens:** FIX · feedback & state (B008 + B009 on the board)
- **Evidence:** B008: a corrupt/truncated `session-mode.json` silently un-pauses/reverts to passive (the Stop procedure's `(pre)` step routes unparseable files to EXTRACTOR by design — `hooks/stop-hook-procedure.md:26-30` — with no warning emitted); B009: `board-consolidate.sh` silently no-ops when `python3` is missing, losing the turn's promotions.
- **Proposal:** unparseable-but-present mode file → one warning line ("session-mode.json was unreadable — treating this session as passive; run /pm-start to re-enter PM"); consolidate script preflights `python3` and fails with a named remedy.
- **Why it matters:** both are documented silent-data-loss shapes; the improvement loop's own L-series learnings say honest failure beats silent fallback.
- **Effort:** S · **Impact:** Med–High · **Risks:** fail-open for an *absent* file is correct and must be preserved; only the corrupt-file case changes messaging.

### #12 — One consolidation engine (B014)
- **Tag/lens:** IMPROVE · fixes & felt debt
- **Evidence:** B014 on the board + RFC 0002's `merge` verdict: the `consolidator` agent prompt and `hooks/scripts/board-consolidate.sh` implement the same promotion algorithm twice (same supersession language, same disposition vocabulary). Every hardening fix (e.g. the C7 flatten-every-field work) has had to be applied to both.
- **Proposal:** make the script the single engine; the agent becomes a thin dispatcher that interprets its JSON — RFC 0002 already decided the direction.
- **Why it matters:** double-maintenance of the security-critical promotion path is the likeliest future source of a drift bug the red-team then finds.
- **Effort:** M–L · **Impact:** Med–High · **Risks:** the smoke suite pins consolidation behavior end-to-end — good; that's the safety net.

### #13 — The Conductor (RFC 0001)
- **Tag/lens:** NEW · engagement & retention (big bet)
- **Evidence:** `docs/rfcs/0001-symphony-conductor.md` (Draft, design complete, dependency shipped in 1.1.0); B006 documents the friction it removes ("advancing one entry through tdd→review→validate requires two session restarts"), now mitigated but not solved by the 1.3.0 mode banner.
- **Proposal:** build the bounded first slice: an orchestrator that spawns one worker session per discipline round and advances a single entry end-to-end unattended, posting its trail to the entry.
- **Why it matters:** "commit a bug to markdown and a PR appears" is the demo that earns stars; it's also the natural paid tier in the recorded monetization direction (RFC 0003).
- **Effort:** L · **Impact:** High · **Risks:** needs infrastructure beyond a single sandbox session (the RFC's §10 seams); explicitly out of scope for autonomous container runs so far.

### #14 — Signal capture without surveillance: weekly traffic snapshot
- **Tag/lens:** NEW · retention measurement
- **Evidence:** zero instrumentation anywhere (verified: no analytics in `docs/index.html`); the improvement loop's own charter (`.goal/NEXT_GOAL_IMPROVEMENT_LOOP.md`, rule 7) requires "instrumented channels awaiting real users," and none exist. GitHub's traffic API (stars, clones, views, release-asset downloads) is available to a scheduled workflow with the default token.
- **Proposal:** a weekly Action appends a one-row snapshot (stars, clones, unique views, `.mcpb` downloads) to a committed `docs/metrics.csv` — the board-is-the-database philosophy applied to the product's own adoption data. Optionally a Plausible-class script on the landing page if finer grain is ever wanted.
- **Why it matters:** post-launch decisions (what to build next, whether distribution worked) currently have no feedback signal at all.
- **Effort:** S · **Impact:** Med · **Risks:** traffic API needs a scheduled workflow with repo scope — verify the default token suffices; keep the data public/honest.

## 6. Suggested sequence — if only three ship first

1. **#3 Publish the live board** — smallest change, largest new surface: the public roadmap URL makes every other improvement visible and shareable, and it compounds with #7 and #8.
2. **#1 + #11 as one "honest feedback" PR** — sentinel companions plus the two silent-failure fixes; together they make the core loop's output trustworthy, which is the precondition for anyone relying on it daily.
3. **#4 Done-when synthesis** — the highest-leverage functional fix: it converts the capture pipeline's output from "stalled drafts" into "workable entries," which is the product's actual promise.

---

_All 14 items trace to a file/line or a live board entry; nothing here is
hypothetical. Items #2/#5/#6/#7/#8 derive from two independent design audits run
for this pass (dark-mode contrast measured at 2.96:1; sentinel/microcopy findings
verified against the pinned test surface)._
