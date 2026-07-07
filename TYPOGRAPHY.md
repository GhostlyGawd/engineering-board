# Typography Audit

> **Update — fixes applied (v1.6.0).** F2 **applied** — sub-11px micro-text raised
> to the new `--eb-fs-2xs` (11px) floor. F1/F3 **applied in part** — the board view
> now declares the `--eb-fs-*` scale, unifies its body to 16px (`--eb-fs-base`), and
> routes its primary text roles through tokens. The mid-tier metadata mapping (F1
> remainder), the landing raw-size snap (F5), and resolving the remaining
> defined-but-unused tokens (F4) are **deferred**.

> Read-only pass over the two rendered surfaces and the token source. Every
> number below is measured and cited. The deliverable is a **smaller** system:
> ~20 distinct UI font-sizes collapse onto a 10-step scale, and the type tokens
> that already exist start doing the work the surfaces currently hardcode.

**Sources.** Landing `docs/index.html` (`<style>` 30–166); board view
`hooks/scripts/board-view.sh` (heredoc 262–347, mirrored in
`engineering-board/eb-self/board.html`); tokens `brand/tokens.css`.

**Fonts loaded: none.** Both surfaces use the system stack only —
`--eb-font-sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto…`
and `--eb-font-mono: ui-monospace, "SF Mono", "JetBrains Mono"…`
(`brand/tokens.css:36–39`). No `@font-face`, no Google Fonts, no `.woff`
anywhere in the repo. **Font payload = 0 KB** — no FOUT/FOIT, no weights to
subset. This is a genuine strength; the "font economics" below is therefore
about the *token* system, not download bytes.

---

## 1. The inventory (measured)

### Font-size — the sprawl

| rem | ≈px@16 | Count | Where | Token? |
|---|---|---|---|---|
| `.58rem` | 9.3 | 1 | board `.conf` (`bv:333`) | ✗ raw |
| `.6rem` | 9.6 | 2 | board `.badge`,`.rec` (`bv:319,335`) | ✗ raw |
| `.62rem` | 9.9 | 3 | board `.tag`,`.prio` (`bv:313,315`) | ✗ raw |
| `.66rem` | 10.6 | 1 | board `.kind` (`bv:328`) | ✗ raw |
| `.68rem` | 10.9 | 2 | landing `.card .cid` (`ix:114`); board `.affects` (`bv:311`) | ✗ raw |
| `.7rem` | 11.2 | 2 | board `.col-h`,`.cid` (`bv:298,304`) | ✗ raw |
| `.72rem` | 11.5 | 4 | landing `.proof`,`.col-h` (`ix:111,132`); board `details.more` (`bv:308`) | ✗ raw |
| `.78rem` | 12.5 | 3 | landing `.nav-links a`,`.card`,`table thead` (`ix:88,113,143`) | ✗ raw |
| `.8rem` | 12.8 | 10 | landing `.eyebrow`+6 more (`ix:72,107…`); board `.summary`,`.lane-h`,`.empty` (`bv:288,322,321`) | ✗ raw |
| `.82rem` | 13.1 | 2 | board `.ltitle`,`.lane li` (`bv:332,327`) | ✗ raw |
| `.85rem` | 13.6 | 1 | board `.ctitle` (`bv:310`) | ✗ raw |
| `.875rem` (`--eb-fs-sm`) | 14 | 5 | landing nav/btn/vp/table/footer | ✓ sm |
| `15px` | 15 | 1 | board `body` base (`bv:284`) | ✗ raw px |
| `1rem` (`--eb-fs-base`) | 16 | 3 | landing `body`, btn-primary, lead p | ✓ base |
| `1.05rem` | 16.8 | 1 | board `.lane-h-learn` (`bv:325`) | ✗ raw |
| `1.125rem` (`--eb-fs-md`) | 18 | 1 | landing `.vp h3` (`ix:130`) | ✓ md |
| `1.375rem` (`--eb-fs-lg`) | 22 | 2 | landing tagline, lead h3 | ✓ lg |
| `1.5rem` | 24 | 1 | board `.board-head h1` (`bv:287`) | ✗ raw |
| `clamp→2.25rem` (`--eb-fs-2xl`) | 36 | 1 | landing `section h2` (`ix:125`) | ✓ 2xl |
| `clamp→3.75rem` (`--eb-fs-4xl`) | 60 | 1 | landing `.hero h1` (`ix:92`) | ✓ 4xl |

*(`ix`=index.html, `bv`=board-view.sh.)*

**Distinct UI font-sizes: ~20.** Of these, the **landing** touches 6 token
steps (sm/base/md/lg/2xl/4xl) plus 4 off-scale raws; the **board view uses
zero tokens** — all 13 of its sizes are hand-set raw `rem`/`px`, and **none
lands on a token value.** The scale exists in `brand/tokens.css`; the flagship
surface reinvents it from scratch.

### Weight — disciplined (a strength)
`400` (implicit body), `600` (9×: headings, eyebrow, btn, col-h, lead), `700`
(2×: `.yes` cells `ix:145`, `.prio` `bv:315`). **Three weights, all real** (the
system stack ships true 400/600/700 — no faux-bold). Nothing to fix except
that none reference `--eb-fw-regular/medium/semibold`.

### Line-height — 5 distinct
`1.15` headings (`ix:69`), `1.3` `.ltitle` (`bv:332`), `1.35` `.ctitle`
(`bv:310`), `1.5` board body (`bv:284`), `1.6` landing body (`ix:65`).
Reasonable roles; drifts slightly from the token values (tight 1.1 / snug 1.28
/ body 1.6, `tokens.css:51–53`), which no surface references.

### Letter-spacing — 5 distinct
`.14em` eyebrow (`ix:72`), `.1em` uppercase labels (3×), `.05em` kind/conf
(2×), `-.01em` (2×), `-.02em` headings (2×). Coherent; the two tracking tokens
(`tokens.css:58–59`) are unused.

### Measure (line length) — good
`.hero h1{max-width:16ch}` (`ix:92`), `.hero .tagline{max-width:34ch}`
(`ix:93`), `section .sub{max-width:46ch}` (`ix:126`). Body prose sits at
34–46ch; board cards are grid-narrow so their titles wrap short. No
viewport-wide paragraphs. Keep.

---

## 2. The proposed scale (smaller, and actually used)

Keep the existing 9-step token scale; add **one** metadata step below `xs`
(dense chips legitimately need sub-14px), floor readability at ~11px, and route
**both** surfaces through it. Nothing else is invented.

| Token | rem | px | Role |
|---|---|---|---|
| `--eb-fs-2xs` *(new)* | `.6875rem` | 11 | dense metadata floor: tags, prio, conf, rec, cid |
| `--eb-fs-xs` | `.75rem` | 12 | captions: affects, proof, col-h, kind |
| `--eb-fs-sm` | `.875rem` | 14 | secondary body: nav, buttons, table, notes |
| `--eb-fs-base` | `1rem` | 16 | body copy — **both** surfaces |
| `--eb-fs-md` | `1.125rem` | 18 | card titles, sub-headings, learnings heading |
| `--eb-fs-lg` | `1.375rem` | 22 | tagline, board `h1` |
| `--eb-fs-xl` | `1.75rem` | 28 | *(currently unused — reserve or delete)* |
| `--eb-fs-2xl` | `2.25rem` | 36 | section `h2` |
| `--eb-fs-3xl` | `3rem` | 48 | *(currently unused — reserve or delete)* |
| `--eb-fs-4xl` | `3.75rem` | 60 | hero `h1` |

### Mapping today → proposed (the deletions)

- `.58/.6/.62` → **2xs** (raises 9–10px chips to 11px) — collapses 3 → 1
- `.66/.68/.7/.72` → **xs** (12px) — collapses 4 → 1
- `.78/.8/.82/.85` → **sm** (14px), except `.85` `.ctitle` → **base/md** — collapses 4 → 1–2
- `15px` board body → **base** (16px) — removes the base-size split (F3)
- `1.05rem` learnings heading → **md** (18px)
- `1.5rem` board `h1` → **lg** (22px)

**Result: ~20 distinct sizes → 10 tokens (9 existing + `2xs`)**, and the board
view goes from **13 raw values → token references only**. Roughly **10
font-size values deleted** and one base-size inconsistency removed.

---

## 3. Findings (ranked by reading improved per change)

### F1 — The board view is off-scale entirely · **High**
All 13 of the board's font-sizes are hand-set raw `rem`/`px`
(`board-view.sh:283–335`); not one references a token, and none coincides with
a token value. This is the flagship "the board is the database" surface and the
single largest source of scale sprawl. **Fix:** define the size tokens in the
board heredoc's `:root` (it currently defines colors but *no* `--eb-fs-*`) and
replace the raws per the map above. Biggest coherence win for the least
conceptual change.

### F2 — Micro-text sits below the readable floor · **High**
Ten distinct sizes fall between `.58rem` and `.8rem`; the smallest —
`.conf .58rem` (≈9.3px, `bv:333`), `.badge/.rec .6rem` (`bv:319,335`),
`.tag/.prio .62rem` (`bv:313,315`) — render at 9–10px. At a 320px viewport the
board's tags/badges are hard to read. **Fix:** the `2xs` floor (11px) plus the
`.66–.72 → xs` collapse; no chip drops below 11px.

### F3 — Two base reading sizes · **Medium**
Landing body is `--eb-fs-base` = 16px (`ix:65`); board body is `15px`
(`bv:284`) — the only px root size in the product, and off-token. The same
"paragraph" renders at two sizes across surfaces, and every board `rem` computes
against a 16px root while its body inherits 15px. **Fix:** board `body` →
`font-size:var(--eb-fs-base)`.

### F4 — The type-token vocabulary is defined but unconsumed · **Medium** (economics)
`brand/tokens.css` defines weights (`--eb-fw-regular/medium/semibold`, 55–57),
line-heights (`--eb-lh-tight/snug/body`, 51–53), tracking
(`--eb-tracking-tight/wide`, 58–59) and sizes `--eb-fs-xs/xl/3xl` — and
**every one has zero uses on either surface** (verified). The surfaces hardcode
`600`, `1.15`, `-.02em`, `.8rem` instead. So the "single source of truth" does
not source the type. `--eb-fs-xs` is even dropped from the landing's inlined
token copy (`ix:41` starts at `sm`). **Fix:** either consume these tokens or
delete the dead ones — pick one direction so the token file stops lying.

### F5 — Landing's four off-scale raws · **Low**
`.68/.72/.78/.8rem` (`ix:114,111,88,72…`) sit between `xs` and `sm`. Fold into
`xs`/`sm` per the map. Small, but removes the last of the raw sprawl.

### Strengths (keep)
- **0 KB font payload** (system stack) — nothing loaded, nothing to subset.
- **Disciplined weights** — 3 real weights, no faux-bold.
- **Controlled measure** — 16/34/46ch caps; no viewport-wide prose.
- **Fluid display type on landing** — `clamp()` on `h1`/`h2` (`ix:92,125`)
  scales 320px→4k. (Only the board lacks this — it is all fixed.)

---

## 4. Font economics

| Item | Loaded | Used | Reclaim |
|---|---|---|---|
| Web fonts (woff/ttf) | **none** | n/a | 0 KB — already optimal |
| Font weights shipped | system 400/600/700 | 400/600/700 | none wasted |
| `--eb-fs-*` size tokens | 9 defined | 6 used (landing), 0 (board) | delete/reserve `xl`,`3xl`; `xs` unused |
| `--eb-fw-*` weight tokens | 3 defined | **0 used** | dead until consumed |
| `--eb-lh-*` line-height tokens | 3 defined | **0 used** | dead until consumed |
| `--eb-tracking-*` tokens | 2 defined | **0 used** | dead until consumed |
| Distinct raw font-sizes | — | ~14 off-scale | ~10 collapsible onto the scale |

There are **no download bytes to reclaim** — the win is deleting ~10 redundant
font-size values and resolving ~8 defined-but-unused type tokens, so the type
system shrinks to one 10-step scale that both surfaces reference.

*Adjacent (not UI type, noted for completeness):* the diagram SVGs set type
independently — `docs/how-it-works.svg` alone uses ~15 pixel sizes (16–54) and
a generic `monospace` family; `brand/wordmark-*.svg` correctly reuse the system
sans stack. The illustrations are artwork, outside the running-text system, but
`how-it-works.svg`'s size spread is its own small sprawl if it is ever edited.

---

**Report only.** Which should I fix — F1 (board on-scale), F2 (readable
floor), F3 (unify base), F4 (resolve dead tokens), F5, all, or none? I'll wait
for your call before changing anything.
