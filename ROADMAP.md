# Roadmap Synthesis — engineering-board

_Synthesis, not re-auditing (2026-07-08). Merges every audit report at repo root
into one deduplicated, dependency-aware, sequenced roadmap. Every item traces to a
source report — no new findings are smuggled in._

**Scope note:** this roadmap carries only the **open** work. Items already shipped
are excluded (IMPROVEMENTS.md's 14 — built; the design batch's headline fixes —
v1.5.1/v1.6.0; the Experience Optimization safe fixes — PR #87). The pool is the
**deferred/skipped residue** across all reports, recalibrated onto one scale.

---

## 1 — Sources

**Audit reports found (open items extracted):**

| Report | Family | Open residue pulled in |
|---|---|---|
| `COMPREHENSION.md` | Experience | F7 (board.html framing), F9 (SessionStart copy) — in-product copy |
| `SHOWCASE.md` | Experience | F1/F2 (real screenshots), F3 (capture GIF), F4 (diagram recolor), F5 (outcome visuals) |
| `CRO.md` | Experience | (shipped in PR #87; residual A/B items only) |
| `PROOF.md` | Experience | (shipped; metrics landmine fixed) |
| `ACTIVATION.md` | Experience | A1 (capture confirmation), A2 (seed first-win) |
| `RETENTION.md` | Experience | R1 (ungate loop), R2 (scratch accuracy), R4 (accrual), R5 (mode TTL), R7 (/board-stats) |
| `FIXLOG.md` | Fixer log | the deferred/skipped table + the version-bump/release follow-up |
| `HIERARCHY.md` | Design | (v1.5.1/v1.6.0 shipped; residuals minor) |
| `TYPOGRAPHY.md` | Design | F1 remainder (mid-tier board type-scale) |
| `COLOR.md` | Design | F1 (explainer-diagram repaint) |
| `LAYOUT.md` | Design | F1/F4/F5 (4px spacing, fluid lanes, gap-ownership) |
| `STATES.md` | Design | (shipped) |
| `BRAND-COHERENCE.md` | Design | BRAND F1 (diagram off-brand) |
| `IMPROVEMENTS.md` | Product | #8/#9 (MCP parity + testable run-driver), #11 (demo GIF), #12 (Conductor supervisor), B057 (scratch undercount) |

**Not audits (context only):** `NEXT-PHASE.md` — a **closed** v1.0.0 planning archive,
explicitly not carried forward; `README`, `ARCHITECTURE`, `BRAND`, `SECURITY`,
`CHANGELOG`, `state.md` — docs/policy, not backlogs.

**Reports missing — the audit to run next:** every report here audits **UX,
marketing, and visual surfaces**. Nothing audits the **engine** — the ~20
`hooks/scripts/*.sh` + `python3` + the MCP server — for correctness, debt, or
performance. `IMPROVEMENTS.md B057` (a real counting bug) and `#9` ("`/board-run`
lacks test coverage") are hints that latent script bugs exist and are unmapped.
**Run a BUGS / technical-debt audit of the shell+python engine next** — it would
change the technical half of this roadmap the most. (Runner-up: a TESTING audit,
given the flagship command is under-covered.)

---

## 2 — Unified backlog (deduped)

Impact / Effort / Risk recalibrated across **all** reports onto one scale.
Every row cites its source report(s); merged duplicates noted in §5.

| id | Item | Sources | Impact | Effort | Risk | Depends on |
|---|---|---|:--:|:--:|:--:|---|
| **RM-1** | Cut the next release (ship the merged `/pm-start`+`/board-run` UX; re-pin `server.json` digest) | FIXLOG (version-bump deferred) | M | S | L | — |
| **RM-2** | Fix `count_scratch_findings` multi-finding undercount | IMPROVEMENTS B057 · RETENTION R2 | M | S | L | — |
| **RM-3** | Seed sample entry + `/board-run SAMPLE` guided first-win | ACTIVATION A2/A6 · IMPROVEMENTS #11 | **H** | M | M | — |
| **RM-4** | Ungate the learnings loop (auto-consolidate/promote outside PM mode) | RETENTION R1/R2 | **H** | L | **H** | RM-16 |
| **RM-5** | First-capture confirmation line (quiet ≠ silent) | ACTIVATION A1 | M | M | M | — |
| **RM-6** | SessionStart accrual line + local `/board-stats` | RETENTION R4/R7 | M | L | L | RM-4 |
| **RM-7** | `board.html` self-framing header + rename opaque `eb-self` label | COMPREHENSION F7 | M | M | L | — |
| **RM-8** | SessionStart: lead value, demote mode jargon | COMPREHENSION F9 | M | S | L | — |
| **RM-9** | Recolor `how-it-works.svg` to the brand ramp + promote above the fold | SHOWCASE F4 · COLOR F1 · BRAND F1 | **H** | M | M | — |
| **RM-10** | Real `board.html` screenshot embedded in the hero | SHOWCASE F1/F2 | **H** | M | L | — |
| **RM-11** | Terminal demo GIF (setup → capture → pm-start → board-run) | SHOWCASE F3 · IMPROVEMENTS #11 | M | L | M | RM-3 |
| **RM-12** | PR-diff proof image + outcome visuals (memory/locking) | SHOWCASE F2/F5 | M | M | L | — |
| **RM-13** | 4px spacing scale + fluid lanes + gap-ownership | LAYOUT F1/F4/F5 | M | L | M | — |
| **RM-14** | Mid-tier board type-scale mapping | TYPOGRAPHY F1 (remainder) | L | M | L | RM-13 |
| **RM-15** | Conductor cross-session supervisor (RFC 0001 remaining half) | IMPROVEMENTS #12 · README roadmap | **H** | XL | **H** | RM-4, RM-16 |
| **RM-16** | MCP `board_setup` parity + extract `/board-run` into a testable script | IMPROVEMENTS #8/#9 | M | M | M | — |
| **RM-17** | Mode-persistence TTL / `/board-mode reset` | RETENTION R5 | L | M | L | — |

---

## 3 — Themes (root causes worth one structural fix)

1. **The self-driving loop is invisible and gated.** ACTIVATION (capture is silent,
   no seed) and RETENTION (learnings accrue only for PM power-users) are the same
   root cause: the capture → promote → learn loop demands too much manual mode
   ceremony, so casual users never see value or reach the moat. **One structural
   direction** — make the loop low-ceremony and visible — subsumes RM-3, RM-4, RM-5,
   RM-6, and RM-2. Fix the loop, not five surfaces.

2. **The marketing surfaces got the clarity; the product didn't.** PR #87 fixed the
   landing + README (who-it's-for, "fills itself", define "finding"), but the same
   gaps persist *inside* the product — the SessionStart banner and `board.html`
   still speak in mode/pipeline jargon and show an opaque `eb-self` label. RM-7 +
   RM-8 port the won clarity into the surfaces users actually live in.

3. **The explainer diagram is off-brand *and* under-shown — flagged by three reports.**
   SHOWCASE F4, COLOR F1, and BRAND-COHERENCE all point at `how-it-works.svg`'s
   rainbow/slate palette and late placement. **One asset fix (RM-9)** closes all
   three. Highest-consensus item on the board.

4. **A product that pitches "visible" never shows itself.** SHOWCASE's core finding:
   zero real screenshots exist. RM-10/11/12 are one asset pass — the screenshot, the
   PR-diff proof, the demo GIF — that turns the central claim from told to shown.

5. **The flagship command has no test coverage, which blocks the vision.** RM-16
   (extract `/board-run` into a testable driver) is a small enabler that de-risks both
   RM-4 (ungate the loop) and RM-15 (the Conductor supervisor). Test-debt reduction
   that makes two big bets cheaper — do it before them, not after.

---

## 4 — Three milestones

### Now (1–2 weeks) — ship what's built, fix the consensus item, port clarity
**RM-1** (cut the release) · **RM-9** (recolor the diagram) · **RM-7** (board.html
self-framing) · **RM-2** (B057 scratch-count fix).
_Story: deliver the already-built command UX to installs, fix the one asset three
audits agree on, carry the PR-#87 comprehension win into the product, and correct an
honesty bug in the status line. Cheap, high-trust, and balanced — release hygiene +
brand + comprehension + correctness, no architectural risk._

### Next (a month) — the activation + retention engine
**RM-16** (testable run-driver) → **RM-4** (ungate the loop) · **RM-3** (seed
first-win) · **RM-5** (capture confirmation) · **RM-10** (real screenshot) · **RM-8**
(SessionStart copy).
_Story: build the loop that makes people stay. Land RM-16 first so the architectural
ungate (RM-4) ships on a tested driver instead of blind; pair the seed first-win
(RM-3, cheap, high-impact) with the capture confirmation (RM-5) so a newcomer both
sees the pipeline work and knows capture fired. Interleave the real screenshot
(RM-10, growth) so the month isn't pure plumbing._

### Later — measure, finish the assets, deepen the system, take the big bet
**RM-6** (accrual + /board-stats) · **RM-11** (demo GIF) · **RM-12** (proof visuals) ·
**RM-13/14** (spacing + type scale) · **RM-17** (mode TTL) · **RM-15** (Conductor
supervisor).
_Story: once the loop produces value (RM-4), measure it (RM-6) and finish showing it
(RM-11/12). Deepen the design system (RM-13/14) as steady polish. The Conductor
supervisor (RM-15) is the largest, riskiest bet and lands last — deliberately, on top
of a matured, tested, ungated loop rather than ahead of it._

**Balance check:** each milestone interleaves risk-reduction (RM-2, RM-16, RM-17),
growth (RM-9/10 visuals, RM-3 activation), and retention (RM-4/5/6) — neither a
pure-hardening nor a pure-growth quarter.

---

## 5 — Merge log (nothing lost)

- **RM-9** = SHOWCASE F4 **+** COLOR F1 **+** BRAND-COHERENCE (BRAND F1) — the
  `how-it-works.svg` recolor. Three reports, one asset; kept all three framings
  (off-brand palette · WCAG/color · brand-rule). Highest-consensus item.
- **RM-11** = SHOWCASE F3 (HOLD-A3) **+** IMPROVEMENTS #11 — the terminal demo GIF;
  SHOWCASE frames it as "show the mechanic," IMPROVEMENTS as a launch-conversion asset.
- **RM-2** = IMPROVEMENTS B057 **+** RETENTION R2 — the scratch-count undercount; both
  point at the SessionStart pending line misstating volume.
- **RM-6** = RETENTION R4 (accrual line) **+** R7 (/board-stats) — one local
  self-instrumentation surface, merged (same reads: `learnings/`, `ARCHIVE.md`,
  `consolidation.log`, git history).
- **RM-16** = IMPROVEMENTS #8 (MCP `board_setup` parity) **+** #9 (testable
  `/board-run` driver) — merged as the "make the flagship command testable + at MCP
  parity" enabler.
- **RM-3 ↔ RM-11** kept separate (seed entry vs recorded GIF) but sequenced together —
  the seed makes a clean, reproducible demo to record.

**Priority disagreements ruled:**
- _SHOWCASE ranks the real screenshot (RM-10) as its #1 visual; the recolor (RM-9) is
  "one of several."_ **Ruled: RM-9 first.** A fix to an existing on-page asset flagged
  by three reports outranks a net-new capture flagged by one — coherence debt compounds
  on every visitor, and RM-9 is lower-risk.
- _ACTIVATION's "one change" (seed, RM-3) vs RETENTION's "one hook" (ungate, RM-4) —
  each is its report's single top pick._ **Ruled: both in Next, RM-3 before RM-4.**
  They're complementary (first-win vs repeat-value); RM-3 is cheaper and unblocks the
  demo GIF, while RM-4 is architectural and waits on the RM-16 test harness.

---

_Report only — no code changed. **Want me to adjust the sequence** (e.g. pull the
Conductor supervisor forward, or push the design-system depth earlier), or take
`Now`-milestone items into a build? My recommendation: run the missing **engine
BUGS/debt audit** before committing to `Next`, since it's the one blind spot that
could reorder the technical half._
