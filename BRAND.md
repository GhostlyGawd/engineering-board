# Brand — engineering-board

The identity is **premium through restraint**: a near-monochrome ink/paper base,
one warm accent, generous whitespace, and geometry taken directly from the
product's own domain — columns, cards, and the promotion of work between states.
Nothing here is decorative for its own sake; the mark *is* the product.

> **Not sci-fi.** No gradients-for-gradients'-sake, no neon, no glow, no glitch,
> no circuit-board or space imagery. The confidence comes from typography,
> spacing, and a single deliberate accent — not from effects.

---

## 1. Direction studies (three explored, one chosen)

Quick studies, each a reduction of "a board that AI agents run themselves":

| # | Study | Idea | Verdict |
|---|---|---|---|
| **A** | **Promote** — a card crossing the gutter between two columns, in the accent | The literal core loop: work moving through states, autonomously. Encodes columns, cards, *and* motion in one glyph. | **Chosen.** Most "inevitable" given what the product does; legible from 16px to a hero. |
| B | **WIP bars** — vertical bars of varying height (column fill) | Reads as an analytics bar-chart, not a board; generic; says nothing about state transitions. | Rejected. |
| C | **Monogram** — an `e·b` ligature or a bracket enclosing cards | Monograms are interchangeable; a bracket is quiet but inert — no motion, no product soul. | Rejected. |

**Chosen rationale (A):** the board's defining act is *promotion* — a finding
captured, verified, and moved through `tdd → review → validate → resolved`. The
mark shows exactly that: two neutral columns of settled cards and one **amber
card mid-transition, straddling the gutter**. The accent is not arbitrary — it
marks *the one card in motion*, the thing the system is doing right now. That
makes the accent's meaning identical to the product's meaning.

---

## 2. Assets (`brand/`)

| Asset | Files |
|---|---|
| Logomark (light/dark) | `logomark-light.svg`, `logomark-dark.svg` |
| Wordmark lockup (light/dark) | `wordmark-light.svg`, `wordmark-dark.svg` |
| Favicon | `favicon.svg` + `favicon-16.png`, `favicon-32.png`, `favicon-48.png`, `favicon-180.png` (apple-touch) |
| Social preview (1280×640) | `social-preview.svg`, `social-preview.png` |
| Motifs | `motifs/columns.svg`, `motifs/card-flow.svg`, `motifs/state-pipeline.svg` |
| Design tokens | `tokens.css` — **single source of truth** for all styling |

Motifs use `currentColor` for structure so they adapt to the surrounding text
color when inlined; the accent is applied via the `.acc` class.

---

## 3. Color

Near-monochrome base + **one accent hue** (amber), tinted per theme so it stays
legible on both. The full palette lives in `brand/tokens.css`; do not hardcode
colors elsewhere.

| Token | Light | Dark | Role |
|---|---|---|---|
| `--eb-ink` / `--eb-paper` | `#17191E` / `#FAF9F5` | (swapped) | base neutral / off-white |
| `--eb-text` | `#17191E` | `#ECEBE6` | primary text |
| `--eb-text-muted` | `#5B6068` | `#9EA3AB` | secondary text |
| `--eb-text-faint` | `#6C717A` | `#83888F` | tertiary text |
| `--eb-accent` (light) / `--eb-accent-dark` | `#9A5B00` | `#E6A94E` | the accent — used for the in-transition card, links, focus |

### WCAG AA — verified

Every text/background pair passes WCAG AA (≥ 4.5:1 for body, ≥ 3:1 for large).
Computed with the WCAG relative-luminance formula; full table in
`.goal/evidence/G3-wcag-contrast.txt`. Highlights:

| Pair | Ratio |
|---|---|
| ink on paper (body) | 16.69 |
| muted on paper | 6.01 |
| faint on paper (tertiary) | 4.66 |
| accent on paper (link) | 5.15 |
| paper on ink (body, dark) | 14.73 |
| faint on ink (tertiary, dark) | 4.93 |
| accent on ink (link, dark) | 8.50 |

**0 pairs fail AA-body.** The accent doubles as a button fill: paper-on-accent
(light) = 5.15, ink-on-accent (dark) = 8.50.

---

## 4. Type

- **Sans:** `ui-sans-serif, system-ui, …` — a native grotesque on every
  platform. Chosen for premium neutrality *and* zero-latency loading (no web-font
  request), which keeps the landing page's Lighthouse performance high.
- **Mono:** `ui-monospace, "SF Mono", "JetBrains Mono", …` — for code moments
  (install commands, entry frontmatter, MCP tool names).
- Headings: semibold/bold, tight tracking (`-0.02em`). Eyebrow labels: uppercase,
  wide tracking (`0.06em`). Body: 1.6 line-height. Scale is a modular ramp
  (`--eb-fs-xs` → `--eb-fs-4xl`) in `tokens.css`.

---

## 5. Logo usage

- **Clear space:** keep at least the height of one card around the mark.
- **Minimum size:** logomark 16px; wordmark 120px wide.
- Use the **light** variants on paper/light surfaces, **dark** on ink/dark.
- The accent card is load-bearing — never recolor it to a neutral, never add a
  second accent, never place the mark on a busy photographic background.
- Don't stretch, rotate, add shadows/glows, or outline the wordmark text.

---

## 6. Motion principles

Motion communicates **state and hierarchy**, never decoration.

- **Vocabulary:** a card settling into a column (`ease-spring`, slight settle), a
  subtle reorder, staged reveals on scroll. These mirror what the board does.
- **Timing:** `--eb-dur-fast 150ms` / `--eb-dur-base 240ms` / `--eb-dur-slow
  360ms` — all within 150–400ms. Easing: `--eb-ease-out` for entrances,
  `--eb-ease-spring` (gentle overshoot) for a card landing.
- **No loops.** Nothing animates forever; motion resolves and stops.
- **`prefers-reduced-motion`:** every animation must be gated. Reduced-motion
  users get the final state instantly, with opacity-only fades at most.

---

## 7. Voice & tone

Confident, plain, technical. We describe what the product *does*, with evidence.

- **Do:** "The board is committed markdown you can diff." "Atomic claim-locking
  keeps parallel agents from colliding." Short sentences. Concrete nouns.
- **Don't:** hype words (revolutionary, magical, seamless, blazing-fast,
  game-changing), exclamation marks, or claims we can't back with a feature and a
  test. No emoji in product copy.
- Lowercase the product name in prose: `engineering-board`.
- Lead with the structural truth — *the board is the database* — then the
  mechanics.

---

## 8. Self-review against the binding direction

- **Premium through restraint** — ✅ two base neutrals + one accent; no gradient,
  neon, glow, or glitch anywhere; whitespace and type carry the weight.
- **Domain-derived geometry** — ✅ the mark, motifs, and social visual are all
  built from columns, cards, and the promotion of a card across a gutter — the
  product's real objects, not abstract tech clip-art.
- **Motion with purpose** — ✅ principles above map every animation to a board
  action; all gated on `prefers-reduced-motion`.
- **Not sci-fi** — ✅ warm amber (not cyan/blue), paper/ink (not black-glass),
  cards (not circuits or starfields).
