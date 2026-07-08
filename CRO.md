# Conversion Rate Optimization — engineering-board

_Read-only pass, 2026-07-08. Audited through the eyes of a first-time visitor who
knows nothing about the product or the niche. This is a free, MIT, open-source dev
tool — there is no pricing, signup, or checkout — so the funnel is
**land → grasp value → compare → copy the install command → first value**, and the
"conversion" is a paste into Claude Code. Best-practice rule honored throughout:
**prefer removing friction over adding persuasion.**_

Primary surface: `docs/index.html` (the landing, live at ghostlygawd.github.io/engineering-board).
Secondary entry: `README.md` (GitHub). Activation depth is deferred to `ACTIVATION.md` (stage 5).

---

## 1 — Funnel map

| # | Surface | Who lands / their one question | The action it must drive | Its biggest leak |
|---|---|---|---|---|
| 1 | **Hero** `docs/index.html:197-218` | Cold. _"What is this and is it for me?"_ | Grasp the value; move toward Install | Two things: comprehension (who it's for — see COMPREHENSION.md F1) **and** a co-equal "View on GitHub" CTA that siphons dev-tool visitors off the tuned page onto the raw repo |
| 2 | **Why it's different** `:220-232` | Warming. _"Why not a plain markdown file, or nothing?"_ | Believe the trade-off is real | The **pain is never named** ("your agent forgets everything between sessions; parallel agents clobber each other") — cards lead with abstractions ("Visible, diffable state") |
| 3 | **Compare** `:234-255` | Evaluating. _"Is the differentiation real, and is this thing real?"_ | Accept the four-way-intersection thesis | The only ★ count on the page is a **competitor's** ("Backlog.md… ~5.9k★", `:253`); engineering-board's own traction is absent, and the fairness note ("younger… not yet on a public marketplace", `README.md:168`) **amplifies** the "is this maintained?" doubt at the worst moment |
| 4 | **Install** `:257-288` | Deciding. _"How do I try it, and what will it cost me?"_ | Copy-paste + run the commands | **The MCP path is a dead-end** — `python3 /path/to/engineering-board/…` (`:275`) with no `git clone` shown; **Claude Code is never named as a prerequisite**; **"free / no lock-in" is never stated near the CTA**; no copy button |
| 5 | **Activation** (post-install) | Committed. _"Did it work? What now?"_ | First captured finding → first board entry | Deferred to `ACTIVATION.md`; the "one session, one mode" rule and the deliberately-quiet capture are the known risks |

**Leakiest single moment:** step 4, the **MCP install block's missing `git clone`**
— a visitor who picks that path literally cannot proceed (there is no
`/path/to/engineering-board` on their disk). It's a hard dead-end, not a soft leak.

---

## 2 — Findings

Format: **lens · location · what a first-time visitor experiences · fix · lift (H/M/L) · effort (S/M/L).**

### C1 — MCP install path dead-ends: no `git clone`, no source of the path
- **Lens:** Friction (5)
- **Location:** `docs/index.html:273-283` (and `README.md:91-106`) — `claude mcp add engineering-board -- python3 /path/to/engineering-board/mcp-server/engineering_board_mcp.py`.
- **Experience:** "Where is `/path/to/engineering-board`? I don't have this repo. Do I clone it? From where?" The plugin path auto-registers MCP (`:269`), so this block exists **for** the non-plugin user — the exact person who has *not* cloned anything — yet the clone step is missing. They stall or bounce.
- **Fix:** Prepend the one line that resolves it: `git clone https://github.com/GhostlyGawd/engineering-board` and reference `$(pwd)/engineering-board/...`, or state "clone the repo, then point python3 at `mcp-server/engineering_board_mcp.py`."
- **Lift: M · Effort: S.** (Pure friction removal on the leakiest step.)

### C2 — Claude Code is never named as a prerequisite
- **Lens:** Friction (5) · Objections (6)
- **Location:** Landing has **zero** mentions of a prerequisite (verified); the eyebrow says "Claude Code plugin · MCP server" (`:198`) but never "requires Claude Code." The recommended path opens with `/plugin marketplace add…` (`:264`) — a Claude Code slash command with no context.
- **Experience:** A visitor arriving from an "MCP server" or "AI agent board" search doesn't know `/plugin` is a Claude Code command, or that Claude Code is needed at all. They try to run it in a normal shell and it fails.
- **Fix:** One line above the install cards: _"Requires [Claude Code](https://claude.com/claude-code) (free). New to it? Start there."_ Removes a silent prerequisite gap.
- **Lift: M · Effort: S.**

### C3 — "Free / open source / no lock-in" is never stated near the decision
- **Lens:** Pricing & offer (7) · Trust & risk reversal (4)
- **Location:** The word "free" appears **0 times**; "MIT" appears only in the footer (`:293`). The offer's strongest reassurances — it's free, it's MIT, and *uninstalling leaves plain markdown behind* (no lock-in) — are absent from the hero and the Install section.
- **Experience:** For an OSS dev tool, the unspoken questions are "is this free?" and "what am I locked into?" The page answers neither where it matters. "No hidden database… no external service, no daemon" (`README.md:30`) is a lock-in answer that never reaches the landing.
- **Fix:** A reassurance line under the hero CTA and atop Install: _"Free & MIT. Zero dependencies. It's just markdown in your repo — uninstall any time and the board stays as plain files."_ This is risk reversal, not hype.
- **Lift: H · Effort: S.**

### C4 — Co-equal "View on GitHub" CTA leaks the visitor off the tuned page
- **Lens:** The one action (3)
- **Location:** Hero `docs/index.html:202-203` — `Install` (primary) beside `View on GitHub` (ghost); the nav (`:188-190`) *also* offers Install, Live board, and GitHub.
- **Experience:** Dev-tool visitors reflexively click "GitHub" — and land on the long, dense README (a different, un-tuned funnel) or the raw code, away from the conversion path. The hero offers two near-equal exits at the moment it should offer one.
- **Fix:** Keep one primary action. Demote "View on GitHub" to a quiet text link (the nav already carries GitHub), or relabel it to a non-exit like "See the live board →" (which keeps them on-site). Prefer a single obvious next step.
- **Lift: M · Effort: S.** _(Mark as a candidate to A/B — dev audiences sometimes convert **through** GitHub stars; see Ship-vs-test.)_

### C5 — The pain is never named; value cards lead with abstractions
- **Lens:** Value, not features (2)
- **Location:** `docs/index.html:225-229` — "Visible, diffable state," "Durable memory," "Collision-free agents." Each states a capability; none names the pain it removes.
- **Experience:** A visitor who hasn't felt the pain ("my agent re-derives the same context every session," "two agents edited the same file") reads capabilities in the abstract and feels no urgency. Features listed, outcomes unfelt.
- **Fix:** Lead each card with the pain, then the benefit: _"Your agent forgets everything between sessions → recurring lessons become committed `Learning` entries it re-reads next time."_ Name → bridge → benefit.
- **Lift: M · Effort: S.** _(Overlaps COMPREHENSION.md F1/F6 — do once, together.)_

### C6 — No trust signal for engineering-board itself; the fairness note undercuts at the point of decision
- **Lens:** Trust & risk reversal (4) · Objections (6)
- **Location:** The comparison shows rivals' traction ("~5.9k★", `:253`) but **none of its own** (no star count, no "used by," no testimonial, no download/registry number). The honest fairness note (`:253`, `README.md:168`) — "younger and not yet on a public marketplace" — sits right under the compare table.
- **Experience:** "Everyone else has thousands of stars and this one admits it's new and unlisted — is it a weekend project?" The strongest trust asset the product *does* have — **it runs its own board in public** ("we run our own board," `README.md:199`; the live `board.html`) — is under-played as proof of seriousness.
- **Fix:** (a) Surface the real trust signals it *has*: the green CI/tests badge, "zero dependencies," the published releases + MCP Registry listing, and above all **dogfooding** ("this project is built on its own board — [see it live]"). (b) Reframe the fairness note as forward motion ("new, shipping fast — v1.6.0, weekly changelog") rather than a deficit. Don't fabricate stars; convert dogfooding + cadence into credibility. _(Depth: see PROOF.md, stage 4.)_
- **Lift: H · Effort: M.**

### C7 — The top safety objection for an autonomous agent tool is unaddressed
- **Lens:** Objections (6) · Trust & risk reversal (4)
- **Location:** The landing never mentions safety/security. `SECURITY.md` exists (untrusted-data model + a red-teamed injection corpus — a genuine differentiator per `state.md`), but it's not surfaced on any conversion surface.
- **Experience:** "I'm about to let an agent auto-write files and run hooks in my repo — is that safe?" is a top-3 bounce reason for agent tooling, and the page is silent. A real strength (the injection corpus) goes unused as reassurance.
- **Fix:** One trust line near Install linking `SECURITY.md`: _"Built for untrusted input — scratch content is treated as data, never instructions, and hardened against prompt injection ([security posture](…))."_ Turns an unspoken fear into a selling point.
- **Lift: M · Effort: S.**

### C8 — No copy-to-clipboard on the install commands
- **Lens:** Friction (5)
- **Location:** `docs/index.html:264-283` — the `<pre><code>` install blocks are the literal conversion action (paste into Claude Code) and have no copy button.
- **Experience:** Manual select-drag-copy of multi-line blocks; easy to grab a stray line or the `# comment`. Small friction on the single most important interaction on the page.
- **Fix:** Add a lightweight copy button per code block (a few lines of inline JS, consistent with the page's self-contained, zero-dependency style).
- **Lift: L · Effort: S.**

### C9 — No structured data for rich/AI-search results
- **Lens:** Findable & shareable (9)
- **Location:** `docs/index.html` `<head>` — OG/Twitter/canonical/keywords are all present and good, but there is **no** `application/ld+json` (0 hits).
- **Experience:** Search engines and AI answer-engines can't read a `SoftwareApplication`/`SoftwareSourceCode` entity (name, license MIT, offers: free, category) — a missed eligibility for richer results on a page that's otherwise strong on shareability.
- **Fix:** Add a `SoftwareApplication` JSON-LD block (name, description, `applicationCategory: DeveloperApplication`, `offers: { price: 0 }`, `license: MIT`, `sameAs: [repo]`).
- **Lift: L · Effort: S.**

### What's already strong (don't touch)
- **Findable/shareable (lens 9):** title, meta description, canonical, keywords, OG + Twitter card with a real `social-preview.png` (1280×640), theme-color — all present and well-formed (`:6-28`).
- **Speed:** self-contained HTML, inline CSS, no external requests, CSS-only demo — fast first paint (state.md cites Lighthouse 100×4). Do not add heavy media that regresses this.
- **The one action, mostly:** "Install" is clearly the primary (amber, larger, `:101`), and the recommended path is marked "start here" (`:263`) — good anchoring against choice paralysis between the two install paths.
- **Scannability (lens 8):** hero → why → compare → install is a clean skim order; the compare table is legible. Main drag on the 10-second skim is jargon (MCP, "findings") — see COMPREHENSION.md.

---

## 3 — Top 5 lifts (ranked by lift ÷ effort)

1. **State "Free & MIT · no lock-in · just markdown you can delete" near the hero CTA and atop Install (C3).** _H lift, S effort._ The offer's biggest reassurance is currently invisible; one honest line reduces adoption risk at the decision point. **Ship this first** — highest leverage, zero downside, no design work.
2. **Fix the MCP install dead-end — add the `git clone` step (C1).** _M lift, S effort._ Removes a hard blocker on the leakiest funnel step; anyone choosing that path today cannot proceed.
3. **Name Claude Code as a prerequisite (C2).** _M lift, S effort._ Closes a silent gap that fails visitors before they even start.
4. **Surface real credibility — dogfooding, CI badge, releases/registry — and reframe the fairness note (C6).** _H lift, M effort._ Converts the product's actual proof (it runs its own public board) into trust, and stops the honest self-deprecation from bleeding conversions.
5. **Add the security-posture reassurance line (C7).** _M lift, S effort._ Answers the top unspoken objection for autonomous-agent tooling with a genuine strength you already own.

_Why #1 ships first: it's the only H-lift/S-effort item that is pure reassurance
(no comprehension rewrite, no new asset), so it's safe to ship immediately and
independently of everything else._

---

## 4 — Ship vs test

**Ship now (proven best practice, safe — mostly friction removal & honest reassurance):**
- **C1** (git clone), **C2** (prerequisite), **C8** (copy button) — friction removal, no downside.
- **C3** (free/no-lock-in line), **C7** (security line), **C9** (JSON-LD) — factual reassurance / SEO hygiene, nothing to lose.
- **C6** (surface dogfooding + CI + releases as trust) — replacing an absence with true signals; safe.

**A/B test (hypotheses — the outcome isn't obvious):**
- **C4** (demote "View on GitHub"). Dev-tool audiences sometimes convert *through* a GitHub visit (they star, then install). Test "single Install CTA" vs "Install + quiet GitHub text link" on install-command copies; don't remove the GitHub path outright without data.
- **C5** (pain-first value cards). Reframing headings changes comprehension and could help or muddy the skim; test against the current capability-first cards. Overlaps COMPREHENSION.md — coordinate.
- **C6 wording** of the fairness-note reframe — test that "new, shipping fast" reads as momentum, not spin.

**Handle carefully (don't regress a strength):**
- Any screenshot/media added for trust (per SHOWCASE.md) must not regress the current fast first paint — optimize and lazy-load.
- Keep the comparison **honest** — the credibility of the whole table rests on it; strengthen own-traction signals without deleting the fair "where they're better" note, only reframing it.
- Preserve the single-primary-CTA hierarchy; don't let new reassurance lines spawn competing buttons.

---

_Report only. **Which lifts would you like me to ship?** Recommendation: ship the
S-effort friction/reassurance set now — **C3, C1, C2, C7** (and C8/C9 as freebies)
— all safe, all on `docs/index.html`/`README.md`, and together they fix the
leakiest step and the missing offer. Hold **C4** and **C5** for an experiment. C6
(trust) is best done alongside PROOF.md (stage 4)._
