# Color & Contrast Audit

> **Update — fixes applied (v1.6.0).** F2 (Done recede via muted color, not the
> opacity that composited metadata to 2.69:1) and F3 (faint→muted on the recessed
> surface) are **applied**. F1 is **partial** — the diagram's gradient is gone
> (BRAND F2) but the full rainbow→mono repaint is **deferred**. F4/F5 (amber
> overload; dead `--eb-accent-strong`) are **noted/deferred**.

> Read-only pass. Every color carries its value + file; every ratio below is
> **computed** (WCAG 2.x relative-luminance), not quoted from the brand deck.
> Headline: the two UI surfaces are unusually token-disciplined and the token
> file's contrast claims all verify — but (a) tertiary text on the recessed
> surface fails AA, (b) the opacity-`.6` Done column pushes card metadata far
> below AA, and (c) the illustration SVGs ship a **second, unrelated palette**
> (cool Tailwind slate + a violet/blue/emerald/red rainbow) that has nothing to
> do with the warm-neutral + single-amber brand.

**Sources.** Landing `docs/index.html`; board `hooks/scripts/board-view.sh`
(mirror `board.html`); tokens `brand/tokens.css`; assets `brand/*.svg`,
`docs/*.svg`.

---

## 1. The real palette (clustered)

### A. UI surfaces — coherent, token-driven (a strength)
Every value below is a defined token; hardcoded bypasses are flagged.

| Cluster | Values (light → dark) | Role |
|---|---|---|
| **Background** | `#FAF9F5` paper → `#17191E` ink | page bg (`--eb-bg`) |
| **Surface** | `#F1F0EA` → `#1E2127` | recessed panels/columns (`--eb-surface`) |
| **Card** | `#FFFFFF` → `#23262D` | elevated cards (`--eb-card`) |
| **Border** | `#E3E1D9` → `#2A2D34` | hairlines (`--eb-line`/`-dark`) |
| **Text** | `#17191E` → `#ECEBE6` | primary (`--eb-text`) |
| **Text muted** | `#5B6068` → `#9EA3AB` | secondary (`--eb-text-muted`) |
| **Text faint** | `#6C717A` → `#83888F` | tertiary (`--eb-text-faint`) |
| **Accent (amber)** | `#9A5B00` → `#E6A94E` | brand/link/primary/P1/"live"/high-conf |
| **Accent pressed** | `#7E4A00` (light only) | `--eb-accent-strong` — **defined, unused** |
| **Danger (red)** | `#B23A2E` → `#E4685A` | blocked/P0/destructive |
| *(hardcoded)* | `pre` color `#ECEBE6` + dark bg `#0F1114` (`ix:155–156`) | code block — bypasses tokens |
| *(print-only)* | `#000000` `#333333` `#BBBBBB` `#FFFFFF` (`bv:339`) | `@media print` override |

**~11 semantic clusters, ~20 hexes, almost all tokenized.** Off-token bypasses:
just `#0F1114`, the hardcoded `#ECEBE6` on `pre`, and the print grays. Sprawl
here is **low** — the system is real.

### B. Illustration SVGs — a whole second palette (the problem)
`docs/how-it-works.svg` (and to a lesser degree `board-demo.svg`,
`social-preview.svg`) introduce **~40 more hexes** on no shared system:

| Family | Sample values | Notes |
|---|---|---|
| **Cool slate grays** | `#0F172A` `#334155` `#475569` `#64748B` `#94A3B8` `#CBD5E1` `#E2E8F0` `#F1F5F9` | Tailwind *slate* — **cool**, vs the brand's **warm** grays |
| **Violet/indigo** | `#7C3AED` `#5B21B6` `#8B5CF6` `#6D28D9` `#4F46E5` `#4338CA` `#EDE9FE` `#C7D2FE` | not a brand hue at all |
| **Blue** | `#1E40AF` `#2563EB` `#3B82F6` `#DBEAFE` | categorical |
| **Emerald/green** | `#059669` `#10B981` `#047857` `#166534` `#DCFCE7` | "success" — a meaning the UI never uses |
| **Red** | `#EF4444` `#991B1B` `#FEE2E2` | different reds from `--eb-danger` |
| **Cyan** | `#155E75` `#CFFAFE` | categorical |

The brand marks that *are* on-system — `wordmark-*.svg`, `logomark-*.svg`,
`favicon.svg` — correctly use amber `#9A5B00`/`#E6A94E` + ink/paper. The
**diagrams** are the drift.

---

## 2. Contrast table (computed)

AA thresholds: **4.5:1** normal text, **3:1** large/UI. Token-file claims all
reproduced exactly (✓ verified).

| Pair · where | Ratio | AA |
|---|---|---|
| text on paper — body | **16.69** | ✓ |
| text on surface | 15.40 | ✓ |
| text on card | 17.58 | ✓ |
| muted on paper | **6.01** | ✓ |
| muted on surface — `.col-h` (`bv:298`) | 5.54 | ✓ |
| muted on card — cid/affects/tags | 6.33 | ✓ |
| faint on paper | **4.66** | ✓ (barely) |
| **faint on SURFACE — table `thead`/`.no`/`.proof` (`ix:143,147,132`)** | **4.30** | ✗ **FAIL** |
| accent on paper — link/eyebrow/`.yes` | **5.15** | ✓ |
| accent on surface — `.yes` in compare table (`ix:145` on `:224` bg) | 4.75 | ✓ (thin) |
| on-accent(paper) on accent — btn / `.prio.p1` | **5.15** | ✓ |
| on-accent(paper) on danger — `.prio.p0` fill | 5.63 | ✓ |
| danger on paper — blocked badge | **5.63** | ✓ |
| **dimmed `.ctitle` — Done card `opacity:.6` (`bv:295`)** | **4.78** | ✓ (thin) |
| **dimmed `.cid`/metadata — Done card `opacity:.6`** | **2.69** | ✗ **FAIL** |
| text on ink — body (dark) | **14.73** | ✓ |
| muted on ink (dark) | **6.93** | ✓ |
| muted on card (dark) | 5.97 | ✓ |
| faint on ink (dark) | **4.93** | ✓ |
| faint on surface (dark) | 4.52 | ✓ (barely) |
| accent on ink (dark) | **8.50** | ✓ |
| on-accent(ink) on danger — `.prio.p0` dark | 5.38 | ✓ |
| danger on ink (dark) | **5.38** | ✓ |
| **dimmed metadata — Done card dark `opacity:.6`** | **3.06** | ✗ **FAIL** |
| — borders (`--eb-line`) on any bg | 1.10–1.31 | (decorative hairline — by design) |

---

## 3. Findings (ranked by user harm)

### F1 — Two palettes ship in one product · **High** (coherence)
The UI is warm-neutral + one amber accent; the diagram SVGs
(`docs/how-it-works.svg` foremost) are **cool slate + violet + blue + emerald +
red** — ~40 hexes on Tailwind's system, zero of them brand tokens (§1B). A
visitor who reads the landing page and then opens the explainer diagram sees
two different products. `#0F172A` slate lives a click away from `#17191E` ink;
`#059669` emerald asserts a "success" color the product itself never defines.
**Highest-surface-area drift**, even though each diagram color is individually
fine.

### F2 — The opacity-`.6` Done column fails AA on metadata · **High** (contrast)
`.col-done .card{opacity:.6}` (`bv:295`) group-composites every Done card over
the column surface. Computed: the title survives at **4.78** (light) but the
`.cid`, `.affects`, and `.tag` metadata drop to **2.69:1** (light) / **3.06:1**
(dark) — well under 4.5. On the eb-self board that is **58 of 70 cards**
(`board.html`). Hover/focus-within restores it, but keyboard-idle and
touch-scan states read sub-AA. Opacity de-emphasis is the wrong tool: it dims
*contrast*, which accessibility counts, regardless of "importance."

### F3 — Tertiary text on the recessed surface fails AA · **Medium** (contrast)
`--eb-text-faint #6C717A` is AA on paper (**4.66**) but only **4.30** on
`--eb-surface #F1F0EA` — and it is used there: compare-table `thead th`
(`ix:143`), `.no` cells (`ix:147`), and `.vp .proof` on the surface-bg cards
(`ix:132`), all at 14px or smaller. The token comment claims "4.66 on paper" —
true, but the color is *deployed* on surface, where it fails.

### F4 — Amber is semantically overloaded (but never collides) · **Low**
One hue carries brand, link, primary action, "Yes/present," P1 priority,
"live/in-motion," learnings-moat, and high-confidence. It reads as "the
highlighted/active thing" everywhere, so it is coherent, not contradictory —
but "P1 priority" and "this is a link" being the same amber can momentarily
confuse. Red, by contrast, cleanly means danger everywhere (blocked/P0). No
red/green collision exists because **green is absent from the UI** — it lives
only in the diagrams (F1).

### F5 — Dead / hardcoded state colors · **Low**
`--eb-accent-strong #7E4A00` (the pressed-state token, `tokens.css:20`) is
**defined but unused** — no `:active`/pressed rule references it; hovers are
transforms/underlines. And `pre` hardcodes `#ECEBE6` + `#0F1114` (`ix:155–156`)
instead of tokens. Buttons have **no `:disabled` color** (the demo Play button
toggles `disabled` but only changes its label). Small, but it means the
interactive-state color vocabulary is partly aspirational.

### Strengths (keep)
- **Token-file contrast claims are all accurate** (verified above) — rare.
- **Genuine dark mode** — separate hue/lightness-tuned values per role, not a
  filter; `on-accent` and `danger` flip correctly; logo/wordmark have
  `-light`/`-dark` variants.
- **Color is never the sole signal** — P0–P3, Yes/No, blocked, high all carry a
  text label or shape (focus outline, dot) beside the hue.
- **UI palette sprawl is low** — ~4 off-token values total.

---

## 4. The token proposal (smallest palette that covers today)

The UI already *has* the right set; the proposal is mostly **rules + two fixes**,
not new shades (meaning first).

**Keep (per theme):** `bg · surface · card · line · text · text-muted ·
text-faint · accent · accent-strong · danger`. That's the whole system — 10
roles. Add nothing categorical; if the product ever needs "success," define
**one** `--eb-success` token rather than importing the diagram's emerald.

**Fixes mapped from today:**
1. **F3 — semantic rule, no new shade:** faint is for tertiary text **on `bg`
   only**; on `surface`, step up to `--eb-text-muted` (5.54, passes). Or nudge
   `--eb-text-faint` to ~`#656A72` so it clears 4.5 on surface too — but the
   rule is cleaner.
2. **F2 — recede Done with color, not opacity:** drop `opacity:.6`; instead set
   Done card title → `--eb-text-muted` and metadata → `--eb-text-faint` at full
   opacity (both AA on `card`). Same "quieter" read, contrast preserved.
3. **F5 — consume or delete `--eb-accent-strong`;** tokenize `pre` as
   `--eb-code-bg`/`--eb-code-text`.
4. **F1 — one palette for artwork:** redraw the diagrams on the token neutrals +
   amber (and one deliberate second hue if a diagram genuinely needs
   categorical encoding — chosen once, added to tokens, not ad-hoc Tailwind).
   Ensure diagrams have a dark-mode story like the logos do.

**Data-viz note:** the product ships **no runtime charts** — the only
categorical color is in static diagrams. There is no chart palette to make
consistent yet; if charts arrive, derive a categorical ramp from the brand once
(see the repo's `dataviz` guidance) rather than reaching for slate/violet again.

---

**Report only.** Which do I fix — F1 (unify the diagram palette), F2 (Done
recede without opacity), F3 (faint-on-surface), F4, F5, all, or none? I'll hold
until you decide.
