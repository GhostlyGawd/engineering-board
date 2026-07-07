# Interaction States & Motion Audit

> **Update — all of F1–F5 applied (v1.6.0).** F1 (dark-mode focus ring →
> `--eb-accent-dark`, the accessibility fix) on both surfaces; F2 (the board view
> gains a unified `:focus-visible` ring); F3 (`:active` pressed) + F4 (`:disabled`)
> on the landing buttons; F5 (board motion tokens `--eb-dur-fast`/`--eb-ease-out`,
> de-snapping the Done transition).

> Read-only pass; traced from real selectors and the landing page's JS, not a
> design file. The product has **no forms** — no inputs, selects, toggles, or
> textareas — so the error/success/loading half of the state matrix is N/A by
> construction, not by omission. What remains — buttons, links, a native
> disclosure, and one scripted demo — is mostly well-stated, with **one real
> accessibility defect**: the keyboard focus ring fails contrast in dark mode.

**Sources.** Landing `docs/index.html` (`<style>` + `<script>`); board
`hooks/scripts/board-view.sh` (mirror `board.html`). `ix`=index.html,
`bv`=board-view.sh.

---

## 1. The state matrix (species × states)

| Species | default | hover | focus-visible | active | disabled | loading/error |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| **Primary btn** — Install (`ix:97`) | ✓ | ✓ lift | ✓ global¹ | ✗ | ✗ | n/a |
| **Ghost btn** — GitHub / Play (`ix:99`) | ✓ | ✓ lift | ✓ global¹ | ✗ | ⚠ toggled, no style | ⚠ label-only |
| **Theme btn** (`ix:86`) | ✓ | ✗ none | ✓ global¹ | ✗ | n/a | n/a |
| **Text link** — body/footer (`ix:67`) | ✓ | ✓ underline | ✓ global¹ | ✗ | n/a | n/a |
| **Nav link** (`ix:84`) | ✓ muted | ✓ →text | ✓ global¹ | ✗ | n/a | n/a |
| **Card-id link** `a.cid` (`bv:305`) | ✓ | ✓ accent | ✓ explicit²+UA | ✗ | n/a | n/a |
| **Disclosure** `summary` (`bv:308`) | ✓ | ✓ accent | ✓ UA default² | native ✓ | n/a | n/a |
| **Dimmed Done card** (`bv:296`) | ✓ dim | ✓ opacity→1 | ✓ focus-within | n/a | n/a | n/a |
| **Inputs / selects / toggles** | — none exist in the product — |

¹ "global" = the landing's `:focus-visible{outline:2px solid var(--eb-accent)}`
(`ix:75`) — **broken in dark mode (F1)**.
² the **board is a separate document** and defines **no** global `:focus-visible`
— only `a.cid` is custom; `summary` falls back to the UA outline (F2).

**Empty / broken cells that matter:** `active` (empty everywhere), `disabled`
(broken on Play), and `focus-visible` in dark mode (broken — F1).

---

## 2. Focus & feedback findings (focus first — it is accessibility, not polish)

### F1 — The keyboard focus ring fails contrast in dark mode · **High (a11y)**
`:focus-visible{outline:2px solid var(--eb-accent)}` (`ix:75`) hardcodes the
**light** accent `#9A5B00` and has **no dark override** — unlike `.eyebrow`,
`.btn-primary`, `a`, etc., which all switch to `--eb-accent-dark`. Computed ring
contrast in dark mode:

| Ring on… | `#9A5B00` (today) | `#E6A94E` (dark accent) |
|---|---|---|
| ink `#17191E` | 3.24 ✓ (thin) | 8.50 ✓ |
| surface `#1E2127` | **2.97 ✗ FAIL** | 7.80 ✓ |
| card `#23262D` | **2.79 ✗ FAIL** | 7.32 ✓ |

Focusable elements in dark mode sit **on cards/surfaces** (every `a.cid` lives on
a `#23262D` card), so a keyboard user gets an under-visible ring exactly where
the controls are. **Fix:** give `:focus-visible` a dark override to
`--eb-accent-dark` (landing) and use `--eb-accent-cur` on the board — one rule,
takes 2.79 → 7.32.

### F2 — The board has no unified focus ring · **Medium (a11y)**
`board.html` is its own document and defines **no** global `:focus-visible`; its
`:root` never declares the accent tokens either. Only `a.cid` is styled
(`bv:306`, and it points at `--eb-accent-cur` which *is* defined). Native
`summary` and any future control fall back to the UA outline — visible, but
inconsistent with the landing's deliberate ring. **Fix (folds into F1):** add a
board `:focus-visible{outline:2px solid var(--eb-accent-cur);outline-offset:2px}`.

### F3 — No pressed state; clicks lack sub-100ms acknowledgment · **Medium**
There is **no `:active` rule anywhere** (verified). Buttons acknowledge a click
only via the resulting navigation/scroll or the demo's JS — no immediate pressed
feedback. Tellingly, `--eb-accent-strong #7E4A00`, the token *named* "pressed/
hover on light" (`tokens.css:20`), is **defined but unused** (also COLOR F5).
**Fix:** add `.btn:active{transform:translateY(0)}` + `background:var(--eb-accent-strong)`
for the primary; instant, on-brand press feedback.

### F4 — The one disabled state has no visual · **Medium**
The demo Play button is the only element that ever disables — JS sets
`btn.disabled=true` (`ix:348`) — but there is **no CSS `:disabled` rule**, so it
looks fully clickable while inert; its only "loading" cue is the label flip to
"▸ Playing". **Fix:** `.btn:disabled{opacity:.6;cursor:not-allowed}` (and keep
the label change as the honest loading text).

### Feedback / loading honesty (no defect)
Theme toggle is instant and rides the 240ms `body` color transition (`ix:66`) —
smooth, not jarring. There is **no async loading** in the product (static pages),
so there are no spinners to flash or skeletons to mismatch. The matrix's N/A
loading column is correct, not a gap.

---

## 3. Motion inventory

| Motion | Selector | Purpose | Duration / easing | Verdict |
|---|---|---|---|---|
| Theme cross-fade | `body` transition (`ix:66`) | **confirm** theme switch | 240ms `base` / ease-out | **Keep** |
| Button lift | `.btn` + `:hover` (`ix:96,100`) | **affordance** on hover | 150ms `fast` / ease-out | **Keep** |
| Card settle | `@keyframes settle` + `.card.moving` (`ix:119–120`) | **connect** — card entering a state column | 360ms `slow` / spring | **Keep** — the one signature motion; it *is* the product metaphor |
| Scroll reveal | `.reveal` (`ix:163–164`) | **orient** — staged entrance | 360ms `slow` / ease-out | **Keep** (or tune down — mildest decoration; already guarded) |
| Smooth anchor scroll | `html` (`ix:62`) | **orient** — in-page nav | UA / — | **Keep** |
| Board hover restore | `.col-done .card:hover` (`bv:296`), `a.cid:hover` (`bv:306`) | de-dim / confirm hover | **none — snaps** | **Tune** — add a 150ms transition |

**Durations** are 150 / 240 / 360ms — all inside the 100–360 band, all
tokenized (`--eb-dur-fast/base/slow`). **Easings** are two tokens
(`--eb-ease-out` for everything, `--eb-ease-spring` for the settle only). Every
animation has a job; none is gratuitous. This is **one motion vocabulary** — on
the landing. The **board defines no motion tokens at all** (its `:root`,
`bv:263–271`, has only color + font), which is why its hovers snap (F5-adjacent).

### Reduced motion — handled thoroughly (a strength)
Every animation is guarded: `scroll-behavior:auto` (`ix:63`), `.btn:hover` lift
off (`ix:101`), `.card.moving` off (`ix:121`), `.reveal` shown statically
(`ix:165`) — **and** the JS independently checks
`matchMedia("(prefers-reduced-motion: reduce)")` for both the demo (jumps
straight to resolved) and the reveal (adds `in` immediately). CSS *and* script
agree. Exemplary.

---

## 4. The motion tokens to standardize on

The landing's set is already correct; the action is to make it **global** and
retire the snap:

| Token | Value | Use for |
|---|---|---|
| `--eb-dur-fast` | 150ms | hover, **press (new `:active`)**, board de-dim |
| `--eb-dur-base` | 240ms | theme switch, state changes |
| `--eb-dur-slow` | 360ms | entrances (settle, reveal) only |
| `--eb-ease-out` | `cubic-bezier(.16,1,.30,1)` | default for all |
| `--eb-ease-spring` | `cubic-bezier(.34,1.4,.64,1)` | the card-settle only |

**Standardization action:** declare these five in the board heredoc `:root`
(currently absent) and route the board's snapping hovers through
`--eb-dur-fast`/`--eb-ease-out`. This is the same "adopt the tokens the landing
already defines" move that TYPOGRAPHY, COLOR, and LAYOUT each surfaced — one
cross-surface token-adoption pass would close the motion, type, color, and
spacing gaps together.

---

**Report only.** Which do I fix — F1 (dark focus ring — the a11y one), F2
(board focus ring), F3 (`:active`), F4 (`:disabled`), F5/motion tokens, all, or
none? I'll hold until you decide.
