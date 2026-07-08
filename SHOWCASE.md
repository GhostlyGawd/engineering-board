# Show, Don't Tell — engineering-board

_Read-only pass, 2026-07-08. Question asked: does this product **show** its value
and mechanics — screenshots, demos, diagrams, annotated examples — or only
**describe** them in prose you have to trust? A benefit shown converts; a benefit
asserted gets skimmed._

**Headline:** the product's entire pitch is _"the board is the database — visible,
diffable, committed markdown you review in the same PRs as your code."_ Yet across
every public surface there is **not one screenshot of the running product**, not
one line of the actual markdown, and not one PR diff. Every visual is a hand-built
SVG diagram or a CSS mock-up. **A product whose promise is "you can see it" never
shows itself.**

### Asset inventory (what exists today)

| Asset | Where | What it is | Real product? |
|---|---|---|---|
| `brand/logomark-*.svg` | README header | Logo | n/a |
| `docs/board-demo.svg` (720×300, 4K) | README hero `README.md:22` | Hand-drawn 4-column board, one card "B042 surface the board viewer" | **No — stylized diagram** |
| Interactive CSS demo | Landing hero `docs/index.html:206-217` | JS-animated card moving tdd→review→validate→resolved | **No — CSS mock** |
| `docs/how-it-works.svg` (1200×1990, 16K) | README feature tour `README.md:114` | Excellent plain-language "back office team" explainer | **No — diagram (but the best copy on any surface)** |
| `docs/how-it-works.png` (524K) | **referenced nowhere** | Rendered copy of the SVG | Dead weight |
| `docs/assets/social-preview.png` (44K) | OG/Twitter card | Share image | n/a |
| `board.html` (live board) | **linked** from hero+README, never embedded | The real product UI | **Yes — but you must click to see it** |

There are **zero** `.png`/`.jpg`/`.gif` screenshots of the actual UI on any public
surface (verified). The one real artifact — `board.html` — is only ever a hyperlink.

---

## 1 — Show-vs-tell map

| Key claim of value | Shown / Told today | The visual that would prove it |
|---|---|---|
| **"The board is the database — committed markdown you can diff"** (`docs/index.html:200`, `README.md:13,30`) | **Told** — asserted on 4 surfaces, shown as markdown on 0 | A screenshot of a real entry `.md` (frontmatter + body) beside its `BOARD.md` index — the literal thing being claimed |
| **"Reviewed in the same PRs as your code"** (VP1, `README.md:36,43`) | **Told** | A cropped **GitHub PR diff** showing a board card + `BOARD.md` changing next to a code file — the single most on-brand proof possible |
| **"Findings captured automatically as you work"** (`README.md:79`, `docs/index.html:228`) | **Told** (+ named in the SVG "Note-Taker" step) | A **terminal GIF/screenshot** of a real Claude Code session: a turn ends, a finding lands in `_sessions/`. Proof it "fills itself" |
| **"Durable cross-session memory / learnings"** (VP2, `docs/index.html:226`) | **Told** | A **before/after**: the SessionStart banner surfacing a `Learning L###` in a later session (`board-session-start.sh:264` renders it) |
| **"Collision-free parallel agents / atomic claim-locking"** (VP3, `docs/index.html:227`) | **Told** (+ one abstract line in the SVG) | A small diagram or split-terminal: worker A holds a claim, worker B is turned away |
| **"Autonomous tdd→review→validate pipeline"** (VP4, `docs/index.html:228`) | **Shown** — landing demo + `board-demo.svg` + the SVG's Build-Team panel | Best-covered claim. Upgrade: pair the abstract demo with one real board screenshot |
| **"The actual board UI / /board-view"** (`README.md:24`, `docs/index.html:253`) | **Linked, never pictured** | A **static screenshot of `board.html`** (priority pills, Learnings panel, lanes) embedded inline in hero + compare section |
| **"Plugin + MCP server, 11 tools"** (VP5) | **Told** (install code blocks) | Fine as text; optional: a one-frame clip of an MCP client listing the 11 tools |

**Pattern:** the two claims that carry the differentiation — _visible/diffable state_
and _it fills itself_ — are the two most purely **told**. The one claim that is
well **shown** (the pipeline) is the least differentiating (every rival has states).

---

## 2 — Findings

Format: **lens · location · what a visitor can't see · asset to add/fix · effort.**
Effort key: **S** = screenshot of something already built · **M** = short capture/GIF
or recolor · **L** = new designed asset.

### F1 — The real product is never shown before the click _(highest leverage)_
- **Lens:** The product, unseen (2) · Prose where a picture belongs (1)
- **Location:** Landing hero `docs/index.html:206-217` shows a CSS mock, not the UI; `board.html` is only linked (`docs/index.html:189,253`, `README.md:24,199`). The landing embeds only a favicon `<img>` (`docs/index.html:182`) — no product image.
- **Can't see:** A visitor never watches the actual thing — the real board with its priority pills (P0 filled/P1 solid), the Learnings panel, the Questions·Observations lane — before deciding to install. They're asked to click through to `board.html` on faith.
- **Asset:** Embed a **static screenshot of the real `board.html`** in the hero (replacing or flanking the CSS demo) and again in the "compare" section where "see this repo's own live board" is mentioned. The asset already exists as a rendered page — just capture it, light + dark.
- **Effort:** **S** (screenshot an existing, shipping page).

### F2 — "Committed markdown you can diff" is never shown as markdown or a diff
- **Lens:** Show the outcome (4) · Prose where a picture belongs (1)
- **Location:** `README.md:30,36,43` "committed markdown… reviewed in the same PRs as your code"; `docs/index.html:200,225` "The board is the database," proof string "engineering-board/ · BOARD.md · GRAPH.yml."
- **Can't see:** The single most differentiating claim — that coordination state is *legible git* — is proven with a mono-font **text label**, not a picture of the git. No entry file, no `BOARD.md`, no PR diff is ever shown.
- **Asset:** (a) A syntax-highlighted snippet of a real entry `.md` (frontmatter + Done-when) beside the `BOARD.md` index; (b) the killer shot — a **cropped GitHub PR** where a board card and code change land in the same diff. This turns the thesis from claim into evidence.
- **Effort:** **S** for the markdown snippet (paste real content); **S–M** for the PR screenshot (annotate one real PR from this repo's history, e.g. #79/#86).

### F3 — Passive capture ("it fills itself") is told, never demonstrated
- **Lens:** The product, unseen (2) · Show the outcome (4)
- **Location:** `README.md:79` "capture is a passive side effect"; `docs/index.html:228` "Findings flow through…"; the mechanic is *named* in `how-it-works.svg` ("The Note-Taker") but never *shown running*.
- **Can't see:** The most novel behavior in the product — you just work, and the board populates itself — is invisible. A visitor can't watch a finding get born.
- **Asset:** A short **terminal GIF/asciinema** (or, cheaper, an annotated static terminal screenshot): a Claude Code turn ends → the SessionStart/Stop output → a new file in `_sessions/`. Even the plain `board-session-start.sh` banner as a screenshot would show the empty-state → populated transition.
- **Effort:** **M** (record a real session) or **S** (static annotated terminal shot).

### F4 — The clearest explanation on any surface is trapped in an off-brand image, below the fold
- **Lens:** How it works, undiagrammed (3, inverted) · Stale/fake visuals (6)
- **Location:** `docs/how-it-works.svg` (`README.md:114`, feature-tour section). Its copy — _"An always-on back office team for your AI coding assistant… The Note-Taker… The Project Manager… The Build Team… It is all plain text inside your project"_ — is **the best plain-language description in the entire repo**, far clearer than the hero or "What it is."
- **Can't see (two problems):** (a) it's placed **late** (feature tour, below the compare table), so the skimmer who needed it most never reaches it; (b) it is **off-brand** — the diagram uses a Tailwind rainbow (emerald `#059669`, blue `#2563eb`, indigo/violet `#5b21b6`/`#7c3aed`/`#8b5cf6`, red `#ef4444`) over cool slate (`#334155`/`#64748b`/`#94a3b8`), while the brand is warm paper/ink + amber (`#9A5B00`/`#E6A94E`). It clashes with the polished landing and reads as a different product's asset. _(Consistent with COLOR.md / BRAND-COHERENCE.md, which flagged the same drift.)_
- **Asset/fix:** (a) **Promote** the diagram (or a distilled 3-panel version of it) above the fold, near the hero; (b) **recolor** to the brand ramp (warm neutrals + amber accents, single-hue). This is "has an asset, used wrong" — great content, wrong palette and placement.
- **Effort:** **M** (recolor + reposition; content is done).

### F5 — Outcomes are promised, not pictured (memory & locking)
- **Lens:** Show the outcome (4)
- **Location:** `docs/index.html:226` "Durable memory" and `:227` "Collision-free agents" — both cards are text + a mono proof string, no after-state.
- **Can't see:** The *payoff*. For memory: a lesson learned in session 1 auto-appearing at the top of session 5. For locking: two agents genuinely not colliding. Both are the emotional wins, both are invisible.
- **Asset:** A tiny **before/after strip** for memory (SessionStart banner surfacing `L001` with `[high / x3]`, which `board-session-start.sh:264` already renders); an optional 2-node diagram for locking.
- **Effort:** **S** (memory screenshot exists as banner output) · **M** (locking diagram is new).

### F6 — `how-it-works.png` (524KB) is unused dead weight; the SVG's alt text is thin
- **Lens:** Weight and accessibility (7) · Stale/fake visuals (6)
- **Location:** `docs/how-it-works.png` is **referenced nowhere** in README or landing (verified). `README.md:114` alt text is `"How engineering-board works"` — a single generic phrase for a 1200×1990 diagram carrying ~30 labels and the product's clearest explanation.
- **Can't see:** Screen-reader users get nothing from the richest explainer; the repo ships a half-MB image no page uses.
- **Fix:** Retire `how-it-works.png` (or wire it in as the `<picture>` raster fallback and compress it — 524KB is heavy). Rewrite the SVG alt/caption to summarize the flow ("A five-step diagram: you and your AI chat → a Note-Taker captures findings → a PM sorts them into bugs/features/questions → a Build Team runs test→review→validate → done; all as plain text in your repo").
- **Effort:** **S** (delete/compress + alt rewrite).

### F7 — The landing demo is honest but abstract; label it as illustrative
- **Lens:** Stale/fake visuals (6) · Annotated over raw (5)
- **Location:** `docs/index.html:206-217` + the demo card content `:340` ("B001 Login retries exhaust silently").
- **Can't see / risk:** The animated card is a **hand-authored illustration**, not the real UI — which is fine (it demonstrates the state machine clearly and is a genuine strength), but a visitor may read it as a screenshot of the product. It's a *concept demo*, and nearby copy doesn't say so. Not misleading enough to pull, but it should be captioned as illustrative once a real screenshot (F1) sits beside it.
- **Fix:** Add a one-line caption ("Illustrative — [see the real board →](board.html)") and pair with the F1 screenshot so the abstraction and the reality sit together.
- **Effort:** **S** (one caption line).

### F8 — No visual would mislead if shipped (integrity check — clean)
- **Lens:** Stale/fake visuals (6)
- **Finding:** Nothing pictures a feature that doesn't exist. The pipeline shown (tdd→review→validate) is real and shipping; the demo card is clearly conceptual; the roadmap items (Conductor) are text-only and honestly marked "designed, not shipped" (`README.md:176`). **No promise-dressed-as-proof.** Noting the absence because it's the thing most likely to go wrong when adding the assets above — keep new screenshots to shipping behavior only.

---

## 3 — Top 3 visuals to make (in order of persuasion-per-pixel)

1. **A real screenshot of `board.html`, embedded in the hero** (F1). Highest
   leverage, lowest effort: the product's actual face, already built, currently
   hidden behind a link. One capture (light+dark) converts "trust me it's visible"
   into "look, it's visible." **Effort: S.**

2. **A cropped GitHub PR diff showing a board card change beside a code change**
   (F2). This is the *only* asset that proves the thesis competitors can't match —
   coordination state living in reviewable git. It closes the biggest tell-gap on
   the most differentiating claim. **Effort: S–M** (annotate a real past PR).

3. **A recolored, promoted `how-it-works` diagram above the fold** (F4). The best
   explanation you already have, currently late and off-brand. Fix the palette to
   the amber/paper ramp and move it up — turns your strongest "how it works" asset
   from buried to load-bearing. **Effort: M.**

_(Runner-up: the passive-capture terminal GIF (F3) — the most delightful "show,"
but a real recording is more effort than the three above.)_

---

## 4 — Media hygiene

- **Retire or compress `how-it-works.png`** — 524KB, referenced by nothing (F6). Delete, or wire it in as a compressed `<picture>` fallback.
- **Recolor `how-it-works.svg`** off the Tailwind rainbow/slate onto the brand ramp (F4) — it's the one asset visibly from a different palette than the site.
- **Rewrite alt text** on `how-it-works.svg` (`README.md:114`) from "How engineering-board works" to a real flow summary; add a caption under the landing CSS demo marking it **illustrative** (F7).
- **Add light+dark captures** whenever you screenshot `board.html` — the page is theme-aware (`board-view.sh:277-286`); ship both so the shot matches the viewer's mode.
- **Keep new screenshots to shipping behavior only** (F8) — no Conductor/roadmap features pictured as if live.
- **Weight budget:** the CSS demo is free (no image); the biggest first-paint risk is any raster you add — export screenshots as optimized PNG/WebP and lazy-load anything below the fold.

---

_Report only. **Which visuals would you like me to make?** My recommendation:
start with #1 (embed a real `board.html` screenshot — S) and #3's recolor of
`how-it-works.svg` (M), since both use assets that already exist and fix the two
places where the product most conspicuously fails to show itself. #2 (the PR-diff
proof) is the highest-value net-new capture. Note that the F4 recolor overlaps
open items already logged in COLOR.md / BRAND-COHERENCE.md — worth doing once,
together._
