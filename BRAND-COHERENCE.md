# Brand Coherence Audit

> **Note on filename.** This brief's default output is `BRAND.md`, but that path
> already holds the **brand identity document** (the deck / source of truth).
> To avoid clobbering it, this audit is written to `BRAND-COHERENCE.md`; it
> *reads* `BRAND.md` as the stated identity and judges what actually ships
> against it.

> Read-only pass. Judges what ships — files and surfaces — not what the deck
> intended. Headline: the **core identity is genuinely coherent and
> product-true** and holds tightly across logo, wordmark, favicon, UI, and
> motifs; the identity **breaks in exactly one place — the explainer diagrams**,
> which import a cool multi-hue, gradient-using illustration style from a
> different visual world (and, in doing so, violate the brand's own written
> "no gradient" rule).

**Sources.** Identity: `BRAND.md`, `README.md`. Graphic DNA: `brand/tokens.css`,
the two UI surfaces. Assets: `brand/*` (+`motifs/`), `docs/*.svg`,
`docs/assets/*`.

---

## 1. The identity, as shipped

**In one sentence:** *A restrained, warm-monochrome kanban identity — ink/paper
plus a single amber "card-in-promotion" accent, quiet and gradient-free — that
is expressed literally in the product's own geometry (columns, cards, an amber
card crossing the gutter) and holds across the logo, wordmark, favicon, UI, and
motifs; it fractures only in the explainer diagrams, which wander into cool
Tailwind slate + a violet/blue/emerald/red rainbow with gradients.*

The deck (`BRAND.md`) claims "premium through restraint… near-monochrome
ink/paper base, one warm accent," and "Not sci-fi… no gradients, no neon, no
glow… no circuit-board or space imagery" (`BRAND.md:3,8`). The **UI honors this
exactly** — zero gradients on either surface (verified), two neutrals + one
amber, quiet card shadows. The **diagrams do not** (F1, F2). So the identity as
*shipped* is: coherent everywhere a user interacts, incoherent everywhere a user
is *taught* (the README diagrams).

---

## 2. Asset census

| Class | Files | Palette / DNA | Coherence |
|---|---|---|---|
| **Logomark** | `logomark-{light,dark}.svg` (viewBox 32) | ink + amber; card `rx 1.6/1.8`, `stroke-width 1`; the "Promote" mark (two neutral columns, a gutter, one amber card straddling it) | ✅ on-concept, matches deck Study A |
| **Wordmark** | `wordmark-{light,dark}.svg` (viewBox 340×64) | **identical** mark group + "engineering·board", amber `·`, system-sans 25/600 | ✅ byte-for-byte same mark as logomark |
| **Favicon** | `favicon.svg` + `favicon-{16,32,48,180}.png` | simplified **2-card** mark on a rounded-ink square (`rx 7`), cards `rx 2`, dark-amber `#E6A94E` | ⚠️ legit small-size reduction, but different radii (`2` vs `1.6/1.8`) + a container the logo lacks (F4) |
| **OG / social** | `social-preview.{svg,png}` (1280×640) | mark + `stroke-width 1/2.5`, `rx 2.5/4/5/8/9` | ⚠️ more radii/stroke variety than the marks |
| **Motifs** | `motifs/{card-flow,columns,state-pipeline}.svg` | **`currentColor`** (themeable) + amber on the terminal/resolved state; `stroke-width 1/1.5/2` | ✅ on-brand, themeable, product-true |
| **Diagrams** | `how-it-works.svg` (1200×**1990**), `board-demo.svg` (720×300) | **cool slate + violet/blue/emerald/red**, **gradient(s)**, `rx 5/7/10/14/16/28`, `stroke-width 1/2/5/6` | ❌ the drift (F1, F2); both live in **README** |
| **Icons** | *(none — no icon library)* | unicode glyphs only: `▸ ↻ × · —` | ✅ nothing to be inconsistent; minimalist by choice |

**Duplicate copies:** `brand/` and `docs/assets/` each keep `favicon.svg`,
`favicon-32/180.png`, `logomark-{light,dark}.svg`, `social-preview.png`.
Verified **byte-identical** today — no drift yet, but hand-synced with no build
step (F5, a latent risk).

**Graphic DNA (UI):** radii `--eb-radius-sm/card/lg/pill` = `6/10/16/999`
(`tokens.css:68–71`), used — but the surfaces also emit raw `3px`, `4px`, `50%`
(focus, prio pill, dot). Shadows: `--eb-shadow-card` (quiet, 2-layer) used ×4;
the board card instead hardcodes a **different** single-layer shadow
(`0 1px 2px …,.05`, `bv:302`); `--eb-shadow-lift` is **defined but unused**.
**No gradients** anywhere in the UI — matches the rule.

---

## 3. Findings (ranked by user-facing visibility)

### F1 — The explainer diagrams are a different brand · **High**
`docs/how-it-works.svg` and `docs/board-demo.svg` — both embedded in
**`README.md`** (the most-read surface) — render in cool Tailwind **slate**
(`#0F172A`/`#334155`/`#64748B`/`#94A3B8`…) plus a **violet/indigo/blue/emerald/
red** rainbow (see `COLOR.md §1B`), with radii (`5–28`) and stroke widths
(`1/2/5/6`) unrelated to the marks. A reader who meets the warm-amber wordmark
at the top of the README then scrolls into a cool-slate rainbow diagram sees two
products. This is the single largest coherence break — each color is fine; the
*collage* is the problem.

### F2 — The diagram violates the brand's own "no gradient" rule · **High**
`BRAND.md:8` and `:140–141` state "no gradient… anywhere." `how-it-works.svg`
ships a `linearGradient` (`headerGrad`) plus 14 drop-shadow filter uses
(`url(#shadow)`). This is a direct claim-vs-shipped contradiction, and it's in
the README. Removing the gradient + heavy shadow filters realigns the diagram
with the stated "not sci-fi" restraint.

### F3 — Graphic DNA fragments across asset tiers · **Medium**
There is no single radius or stroke signature: UI radii `6/10/16` (+raw
`3/4/50%`); mark radii `1.6/1.8/2/7`; motif radii `3`; diagram radii
`5/7/10/14/16/28` — ~15 distinct corner radii with nothing shared between tiers.
Stroke widths span `1/1.5/2/2.5/5/6`. Even the card **shadow** differs (board's
one-off vs `--eb-shadow-card`). Each tier is internally OK, but "radius + shadow
as a signature" (lens 3) isn't true across the system.

### F4 — Favicon drifts from the logomark · **Low**
`favicon.svg` is a 2-card reduction on a rounded-ink square (`rx 7`), cards at
`rx 2` — vs the logomark's 5-element Promote mark at `rx 1.6/1.8` with no
container. Simplifying for 16px is *correct*, but the specific radii differ and
the reduction is undocumented, so up close the favicon reads as a slightly
different mark. Pick the reduction deliberately (and note it in `BRAND.md`).

### F5 — Duplicated brand files are hand-synced · **Low**
Six assets are maintained in both `brand/` and `docs/assets/`. Byte-identical
now, but nothing enforces it — this is exactly the "duplicate logo files quietly
drifting apart" hazard (lens 7), pre-drift. Add a sync step or a guard test.

### F6 — Amber isn't themed in themeable contexts · **Info**
The `state-pipeline` motif and the focus ring (`STATES.md F1`) hardcode the
light amber `#9A5B00` even where `currentColor`/theme-switching is expected, so
on dark backgrounds they use the lower-contrast amber. The two-tint amber system
exists; it just isn't applied in a few SVG/UI spots.

### Distinctiveness — strong (a real asset)
Swap the logo and the product is **still identifiable**: the "one amber card in
motion among neutral settled cards" is a genuinely ownable, product-true element,
and it recurs — logomark, wordmark, `state-pipeline` accent-on-resolved, the
landing's `.card.live` crossing columns, the board's amber P1/live accents. The
warm-monochrome + single-amber also reads as *not* the default dev-tool
blue/purple. The identity has a spine; F1/F2 are where a limb wandered off.

---

## 4. The coherence kit (the decisions that make it one thing)

1. **One illustration palette.** Redraw `how-it-works.svg` + `board-demo.svg` on
   the token neutrals + amber; if a diagram truly needs categorical encoding,
   choose **one** second hue, tokenize it, and reuse it — never ad-hoc slate/
   violet. (Same root as `COLOR.md F1`.)
2. **Honor "no gradient" everywhere.** Remove the `headerGrad` gradient and the
   heavy `#shadow` filters from `how-it-works.svg`.
3. **One radius DNA.** Map every asset's corners onto ≤4 radii proportional to
   the UI's `6/10/16`; fold the raw UI `3px`/`4px` into the token set.
4. **One or two stroke widths** for all line-art (e.g. `1.5` + a bold `2.5`),
   applied across motifs *and* diagrams.
5. **One card shadow.** Board uses `--eb-shadow-card`; either use
   `--eb-shadow-lift` or delete it.
6. **Theme the amber.** Use `currentColor`/a themed var for accents in themeable
   SVGs and the focus ring, so amber = accent/accent-dark per background
   everywhere (closes F6 + `STATES.md F1`).
7. **Sanction the favicon reduction.** Align its radii or document it in
   `BRAND.md` as the official small-size mark.
8. **Guard the duplicates.** A sync step or a `brand/ == docs/assets/` test so
   the copies can't drift.

---

**A pattern across all six audits.** Every report in this batch found the same
root: a real token system in `brand/tokens.css` that the surfaces (especially
the board view and the SVGs) **don't consume** — dead type/weight/spacing/motion
tokens, a warm palette the diagrams ignore, an amber that doesn't theme. The
highest-leverage single project is a **token-adoption pass** that makes one
system actually source every surface. That is the natural input to a roadmap
synthesis.

---

**Report only.** Which do I fix — F1 (repaint the diagrams), F2 (kill the
gradient), F3 (radius/stroke DNA), F4 (favicon), F5 (duplicate guard), F6, all,
or none? I'll hold until you decide.
