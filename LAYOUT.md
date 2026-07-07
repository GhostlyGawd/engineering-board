# Spacing & Layout Audit

> Read-only pass; every gap has its pixels. Two headlines pull in opposite
> directions: the **patch layer is empty** — no negative margins, no
> absolute-position hacks, no `!important` anywhere (genuinely disciplined
> layout machinery) — yet the **4px spacing scale is used nowhere** (all nine
> `--eb-sp-*` tokens: 0 uses), so real spacing is hand-set in `rem` and roughly
> half the distinct values fall off the grid. Good bones, no system on top.

**Sources.** Landing `docs/index.html`; board `hooks/scripts/board-view.sh`
(mirror `board.html`); tokens `brand/tokens.css` (`--eb-sp-1…9` at 62–64,
`--eb-maxw` 65).

---

## 1. The spacing census

**Scale-token adoption: 0/9.** Verified — `--eb-sp-1` through `--eb-sp-9` are
each referenced **zero** times on either surface; only `--eb-maxw` is used
(once, `ix:71`). The 4px scale exists in the token file and does no work.

**Distinct spacing values in use: ~22** (padding + margin + gap, in `rem`):

| On the .25rem (4px) grid | Off the grid |
|---|---|
| `.25` (4) · `.5` (8) · `.75` (12) · `1` (16) · `1.25` (20) · `1.5` (24) · `2` (32) · `2.5` (40) · `3` (48) · `5` (80) | `.05` (0.8) · `.2` (3.2) · `.3` (4.8) · `.35` (5.6) · `.4` (6.4) · `.55` (8.8) · `.6` (9.6) · `.7` (11.2) · `.85` (13.6) · `.9` (14.4) · `1.2` (19.2) · `1.4` (22.4) |
| **10 on-scale** | **12 off-scale** |

The off-grid values cluster in the **board's dense cards** — `.card{padding:.55rem .6rem}`
(`bv:302`), `.cardhead{margin-bottom:.25rem}`, `.prio{padding:.05rem .3rem}`
(`bv:315`), `.tag{padding:.05rem .4rem}` — and in the **landing's** button/label
paddings — `.btn{padding:.7rem 1.2rem}` (`ix:96`), `.theme-btn{padding:.3rem .7rem}`
(`ix:87`), `.eyebrow`/`.card` at `.4`/`.85`/`.9`. These are eyeballed, not
snapped: `.55rem × .6rem` is neither 8px nor 12px. This is the brief's "13px
gap between two 16px siblings," in `rem`.

**The patch layer — inventoried, and empty (a strength):**

| Debt marker | Count | Notes |
|---|---|---|
| Negative margins | **0** | none |
| `position:absolute` / `fixed` | **0** | only `position:sticky` on the nav (`ix:78`) — legitimate |
| `!important` | **0** | none |
| `transform` nudges | **0 layout** | the `translateY` uses are the btn-lift hover (`ix:100`), reveal (`ix:163`), and settle keyframe (`ix:120`) — intentional motion, not position patches |

Nothing to delete here. The layout composes cleanly with grid + flex.

---

## 2. Alignment & container findings

**Container widths — three, unshared:**

| Container | Width | Selector |
|---|---|---|
| Landing `.wrap` (nav, hero, sections) | **72rem** = `--eb-maxw` | `ix:71` |
| Landing hero demo | **60rem** | `.demo` `ix:104` |
| Board `.board` + `footer` | **80rem** | `bv:285,337` |

The two surfaces don't share a page width (72 vs 80rem), and the hero demo
(60rem, centered) is inset ~6rem from the hero text above it (which uses the
72rem `.wrap`), so the demo's left/right edges **don't share a line** with the
eyebrow/h1/CTA stacked over it — a visible optical step at wide viewports.

**Gutters — unshared:** landing `.wrap{padding:0 1.5rem}` = **24px** (`ix:71`);
board `body{padding:2rem 1.25rem}` = **20px** (`bv:284`). Same product, two
edge insets on mobile.

**Breakpoints — five, only one shared:**

| Surface | Breakpoints |
|---|---|
| Landing | `640px` (`ix:88`), `720px` (`ix:151`), `520px` (`ix:138`) |
| Board | `820px` (`bv:290`), `520px` (`bv:291`) |

`520px` is the only common line; the rest are per-surface. There is no shared
responsive system — each surface picked its own thresholds.

**Grids (machinery is otherwise clean):** `repeat(4,1fr)` board + hero demo;
`repeat(2,1fr)` at breakpoints; `auto-fit,minmax(240px,1fr)` for `.vp`;
`auto-fill,minmax(15rem,1fr)` for learnings. Sensible patterns, no float hacks.

---

## 3. Density verdicts (per screen)

| Screen | Density | Chosen or accidental? |
|---|---|---|
| **Landing — hero/sections** | Airy: `section{padding:4rem 0}` (`ix:124`), hero `5rem/3rem`, cards `1.5rem` | **Chosen** ✓ — correct for a marketing/onboarding surface |
| **Landing — compare table** | Medium: `th,td{padding:.6rem .5rem}` (`ix:141`) | **Chosen** ✓ — readable data density |
| **Board — cards/columns** | Dense: card `.55rem .6rem`, gaps `.5–.7rem`, col `.6rem` | **Chosen** ✓ — correct for a triage/kanban view |
| **Board — empty active lanes** | Canyon: two 25%-width columns showing only `.empty{—}` | **Accidental** ✗ — see F4 |

Density is well-matched to each screen's job — a real strength. The one break
is the empty-lane whitespace, and that's a fill-state artifact of the fixed
4-column grid, not a density choice.

**Proximity semantics — respected:** within-group gaps are consistently
smaller than between-group. `.cardhead{margin-bottom:.25rem}` < `.card{margin-bottom:.5rem}`
(inside a card tighter than between cards, `bv:302–303`); `.tags{margin-top:.35rem}`
inside the card < column `gap:.7rem` between cards (`bv:289,312`). The values
are off-scale but the *relationships* are correct.

---

## 4. Fixes (ranked by screens straightened per token adopted)

### F1 — Adopt the 4px scale that already exists · **High**
All spacing is hand-set; ~12 of ~22 distinct values are off-grid (§1). **Fix:**
route spacing through `--eb-sp-*` and snap the off-grid values to the nearest
step — `.3/.35 → .25/.5`, `.55/.6 → .5`, `.7 → .75`, `.85/.9 → .75/1`,
`1.2 → 1.25`, `1.4 → 1.5`. Collapses ~22 values to ~9 scale steps across ~40
declarations. One token set, forty edits go away. (Same "defined-but-unused
token" pattern this repo shows for type and weight tokens — a single adoption
pass could close all three.)

### F2 — One container geometry for both surfaces · **High**
Three widths (72/60/80rem), two gutters (24/20px), five breakpoints. **Fix:**
apply `var(--eb-maxw)` to the board too (or, if the 4-column board genuinely
needs more room, add a deliberate `--eb-maxw-wide` token instead of a bare
`80rem`); tokenize the gutter (`--eb-sp-5` = 24px) and use it on both; reduce to
a shared 2–3 breakpoint set (e.g. `520 / 768 / 1024`). Makes the two surfaces
read as one product.

### F3 — Align the hero demo to the hero text · **Low**
The 60rem demo (`ix:104`) is inset from the 72rem hero `.wrap`. **Fix:** either
match the demo to `--eb-maxw`, or intentionally inset the whole hero text block
to the same 60rem so the edges share a line — pick one so the vertical edge is
deliberate, not a 6rem step.

### F4 — Fluid or collapsing lanes (also HIERARCHY F4) · **Medium**
`.cols{grid-template-columns:repeat(4,1fr)}` (`bv:289`) reserves 25% for each
lane even when empty, producing canyon whitespace on the common To-do+Done
board. **Fix:** `auto-fit` with a `minmax` floor, or collapse empty lanes to
min-content, so present work uses the width. This is the layout home for the
attention finding raised in `HIERARCHY.md`.

### F5 — Compose gaps in the parent, consistently · **Low**
Landing grids compose with `gap` (parent-owned, disciplined); board cards
self-space with `margin-bottom:.5rem` (`bv:302`, component-owned). **Fix:** give
the column `display:flex;flex-direction:column;gap:.5rem` and drop the card
margin — one ownership model.

### Patches to delete
**None** — the debt inventory (§1) is empty. Note it as the baseline to protect.

---

**Report only.** Which do I fix — F1 (adopt the scale), F2 (one container),
F3, F4 (fluid lanes), F5, all, or none? I'll hold until you say.
