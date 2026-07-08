# Social Proof & Credibility — engineering-board

_Read-only pass, 2026-07-08. Mission: audit the evidence this product offers a
**skeptical stranger** — proof that it's real, works, and is safe to let near their
repo — and find where doubt wins. Claims persuade no one; proof does._

**The honest starting point (sets the whole strategy):** adoption is genuinely
near-zero. `docs/metrics.csv` records **0 stars, 0 forks, 11 `.mcpb` downloads**
(2026-07-06). So the credible path is **not** social proof (there are no users to
quote and no stars to show) — it's the three kinds of proof this product *has
actually earned*: **it builds itself in public (dogfooding), it's engineered with
visible rigor (CI + tests + zero-dep), and it's independently listed (MCP
Registry, Releases).** Every recommendation below obeys the rule: **real proof
only — never fabricate, borrow, or imply trust it hasn't earned.**

---

## 1 — Proof inventory

| Signal | Where it lives | Claim it backs | How credible |
|---|---|---|---|
| **Dogfooding — the live board** `README.md:24,199`; `docs/index.html:253`; `board.html` | Top of README, compare section, footer | "It works / it's real / it's used" | **Strongest asset.** Real, verifiable, rare — the product visibly runs itself, republished every merge. Underplayed. |
| **CI / tests badge** `README.md:18` | README badge row only | "It's tested / reliable" | High — links to live GitHub Actions runs. Verifiable. Absent from the landing. |
| **Engineering numbers** ("14 suites", "103 checks", "11 tools", "zero dependencies") `README.md:30,166,187` | README body | "Quality / low-risk to adopt" | High for a technical evaluator; these are the *right* numbers given adoption is ~0. Stranded in prose. |
| **MCP Registry listing** `docs/index.html:298` | Landing **footer** | "Independently indexed / legitimate" | Genuine third-party signal — buried in the lowest-attention zone. |
| **GitHub Releases + CHANGELOG** `docs/index.html:297,300`; `CHANGELOG.md` (44 KB) | Footer / repo | "Maintained / shipping cadence" | High — real, dated, substantial. Footer-stranded. |
| **Version badge (v1.6.0)** `README.md:17` | README badge row | "Active development" | Medium — reads as activity, not adoption. |
| **License (MIT)** `README.md:16`; `docs/index.html:293` | Badge + footer | "Free / no lock-in" | High but low-visibility (footer only). |
| **Honest comparison table** `README.md:157-168`; `docs/index.html:239-253` | README + landing | "Differentiated / we're not hiding rivals" | High credibility *as a method* — links every competitor. But shows **rivals'** ★, none of its own. |
| **SECURITY.md** (untrusted-data model + red-teamed injection corpus) `README.md:198` | Community section link | "Safe to run" | High and differentiating — invisible on conversion surfaces. |
| **Named maker** | — | "A real person stands behind it" | **Missing.** Only the pseudonymous handle "GhostlyGawd" (in URLs). No name, face, role, or bio anywhere. |
| **Testimonials / user quotes / logos / ratings / usage counts** | — | "Others trust it" | **Missing — and correctly so** (none exist yet; must not be invented). |
| **`docs/metrics.csv`** | Committed, public in-repo (not linked) | intended: adoption | **Trust landmine — see F1.** Shows 0/0 and literal 403 error blobs. |

**Pattern:** the product's real proof is **quality + dogfooding + third-party
listing**, and almost all of it is **stranded** (badge row, prose, footer) — none
sits beside the claim it backs or at the moment of decision.

---

## 2 — Findings

Format: **lens · location · the doubt left unanswered · the fix · effort (S/M/L).**

### F1 — `docs/metrics.csv` is a public trust landmine (0 stars + literal error blobs)
- **Lens:** Freshness & honesty (7) · Numbers that reassure (6, inverted)
- **Location:** `docs/metrics.csv` — the single row reads `stars=0, forks=0`, with the clone/view columns containing raw `{"message":"Resource not accessible by integration",…"status":"403"}` error JSON, and `mcpb_downloads=11`.
- **Doubt:** A curious evaluator who browses the repo (developers do) finds a committed "metrics" file that (a) confirms **zero adoption** and (b) is visibly **broken** (403 blobs where numbers should be). A metric that shrinks under scrutiny costs more trust than no metric. It's not linked from the landing — but it's public.
- **Fix:** Either **fix the collector's permissions** so the traffic fields populate and gate the file behind non-zero data, or **stop committing it** until the numbers reassure (keep it in a private/gitignored path). Never surface it as proof while it reads 0/0/403. _(This is "proof not credible" — remove the liability before adding assets.)_
- **Effort: S.**

### F2 — Dogfooding — the one strong proof — is underplayed and never at the decision
- **Lens:** Proof beside the claim (1) · Proof at the decision (3) · Specific over generic (2)
- **Location:** Mentioned as an aside in the compare paragraph (`docs/index.html:253` "see this repo's own live board") and the README footer roadmap (`README.md:199` "We run our own board"). It is **not** in the hero, **not** beside the "it works" claims, and **not** at the Install CTA.
- **Doubt:** "Does anyone actually use this?" — the honest, powerful answer ("the maintainers build the entire product on it, in public, and you can watch the board move on every merge") is buried where the skeptic won't look. This is the proof that substitutes for the testimonials it doesn't have.
- **Fix:** Promote dogfooding to a **headline credibility band**: a short "Built on itself — in public" strip with a live `board.html` screenshot/link (per SHOWCASE.md F1), placed near the hero and repeated at Install. Specific framing: "Every feature in this repo was captured, tracked, and shipped through this board — here it is, live."
- **Effort: M** (copy + one screenshot).

### F3 — No reassurance in eyeshot at the Install decision
- **Lens:** Proof at the decision (3) · Risk reversal (4)
- **Location:** The Install cards (`docs/index.html:257-288`) carry only technical notes — "Installing the plugin also registers the MCP server…" (`:269`) and "Pure python3, zero dependencies. 11 tools over stdio." (`:284`). No social proof, no security link, no "free/MIT/no-lock-in," no CI/dogfooding signal at the exact moment the visitor decides to paste a command.
- **Doubt:** At the point of "do I run this in my repo?", the fears are "is it safe / maintained / reversible?" — and nothing within eyeshot answers them. All the reassurance lives at the top of the README or in the footer.
- **Fix:** Add a compact trust row directly under the Install cards: **CI passing · zero-dependency · MIT (uninstall leaves plain markdown) · built on its own board · [security posture]**. Put the reassurance where the fear is.
- **Effort: S.**

### F4 — No human stands behind a tool that writes to your repo
- **Lens:** Credibility of the source (5)
- **Location:** The only identity anywhere is the pseudonymous handle "GhostlyGawd," and only inside URLs (`README.md:6` refs, `docs/index.html:8`). No name, face, role, "why I built this," or contact.
- **Doubt:** "Who made this, and why should I trust them with agent-write access to my code?" An entirely faceless project reads as either abandoned-experiment or fly-by-night — the exact opposite of what an autonomous-agent tool needs.
- **Fix:** Add a genuine maker presence — a short "Who builds this" note (even under a consistent pseudonym is fine; **do not fabricate a real name**) with the motivation, a link to the maker's GitHub, and the honest "solo, open-source, built in public" framing. Authenticity, not invented authority.
- **Effort: S.**

### F5 — Real third-party & maintenance signals are footer-stranded
- **Lens:** Proof beside the claim (1) · Numbers that reassure (6)
- **Location:** MCP Registry listing (`docs/index.html:298`), Releases (`:297`), CHANGELOG (`:300`) — all in the footer; the CI/tests badge lives only in the README badge row (`README.md:18`), absent from the landing entirely.
- **Doubt:** "Is this maintained and legitimate, or a dead weekend repo?" The answers (independently registered, published releases, a 44 KB changelog, green CI) exist but sit in the two lowest-attention zones and never appear on the landing where the skeptic forms the impression.
- **Fix:** Surface the maintenance/legitimacy signals up-page: put the **CI/tests badge and "listed on the MCP Registry" on the landing** (near the hero or compare), and cite cadence ("shipping since 1.2.0 — see the changelog") where the "younger project" fairness note currently sits.
- **Effort: S.**

### F6 — The only ★ on the page is a competitor's; own-traction absence reads as weakness
- **Lens:** Numbers that reassure (6) · Specific over generic (2)
- **Location:** `docs/index.html:253` / `README.md:168` — "Backlog.md is the category leader (~5.9k★)"; engineering-board shows no count of its own, and the fairness note concedes "younger and not yet on a public marketplace."
- **Doubt:** Side-by-side, the visitor reads "5.9k★ vs (nothing, admits it's new)" = "the losing option." The honest response is **not** to invent stars but to **change the axis**: compete on rigor and dogfooding, not popularity.
- **Fix:** Where own-traction would go, substitute earned proof: "Built on its own board · green CI · zero-dependency · MIT." Reframe the fairness note from deficit ("not yet on a marketplace") to trajectory ("new and shipping fast — v1.6.0, published releases, weekly changelog"). Keep the competitor ★ (honest) but stop letting it stand unanswered.
- **Effort: S.** _(Coordinates with CRO.md C6.)_

### F7 — SECURITY.md (a genuine differentiator) is invisible where trust is decided
- **Lens:** Security & transparency signals (8)
- **Location:** `SECURITY.md` (untrusted-data model + a red-teamed prompt-injection corpus — per `state.md`, a real strength) is linked once, deep in the README "Community & support" list (`README.md:198`). Nothing on the landing.
- **Doubt:** For a tool that runs hooks and auto-writes files, "could a poisoned input make the agent do something bad?" is a top fear — and the product has an unusually strong, specific answer that it never shows the cautious visitor.
- **Fix:** Surface a one-line security cue at the Install decision and in the footer trust row, linking `SECURITY.md`: "Hardened against prompt injection — scratch content is treated as data, never instructions." A rare cue most competitors can't make.
- **Effort: S.** _(Coordinates with CRO.md C7.)_

### What's already credible (protect it)
- **The comparison method is honest and verifiable** — every rival linked, a candid "where they're better" note (`README.md:168`). This honesty *is* credibility; don't sacrifice it to look bigger.
- **Engineering rigor is real and specific** — 14 test suites, 103 MCP checks, zero runtime deps, protocol 2025-06-18. These are the reassuring numbers to lean on.
- **Dogfooding is a genuinely rare proof** — most tools can't show themselves running themselves. It just needs to be moved to the front.

---

## 3 — Proof at the decision (what to place, in order)

There's no signup or checkout — the decisions are **(a) keep reading**, **(b) trust
the comparison**, and **(c) paste the install command**. Place proof at each:

1. **At the hero (decision: keep reading).** A slim credibility band under the CTA:
   **"Built on its own board, in public · green CI · zero-dependency · MIT."** One
   line, all true, converts an anonymous landing into a serious one.
2. **At the comparison (decision: believe the differentiation).** Replace the
   unanswered ★ gap with earned proof (F6) and add "listed on the MCP Registry"
   (F5) beside the table — legitimacy where the rival-count doubt forms.
3. **At the Install cards (decision: run it) — the most important.** A trust row
   directly beneath the commands (F3 + F7): **CI passing · MIT, uninstall leaves
   plain markdown · hardened against prompt injection ([security]) · see the live
   board it runs.** Put the reassurance where the fear is.
4. **In the footer.** Keep Registry/Releases/Changelog, and add the maker note (F4)
   so the "who's behind this" answer exists for anyone who scrolls to check.

---

## 4 — Proof to earn (collect these — don't fake them)

Ranked by credibility-per-effort, all honest to pursue:

1. **A real usage story you can show** — the fastest legitimate proof: publish a
   short "how we shipped v1.6.0 on our own board" walkthrough (the git history and
   live board already contain it). Turns dogfooding into a case study using data
   you already have. **Low effort, high credibility.**
2. **Fix and grow the metrics, then show them** (F1) — repair the traffic
   collector; once stars/clones/downloads are non-trivial and non-embarrassing,
   surface *only* the ones that reassure. Until then, show none.
3. **Independent validation** — a listing on awesome-claude-code / awesome-mcp
   lists, or an MCP-directory review (PulseMCP/Glama/mcp.so already syndicate the
   registry entry per `state.md`). Third-party inclusion beats self-assertion.
4. **First real testimonials** — once anyone uses it, ask for one verifiable quote
   with a name + GitHub link. **One credible named quote outweighs ten anonymous
   stars.** Never invent these; a fabricated testimonial that unravels destroys the
   honesty the comparison table earns.
5. **A maker identity with continuity** — even pseudonymous, a consistent voice
   (a devlog, release notes signed by the maker, a "why I built this") accrues
   trust over time. Authenticity compounds; borrowed authority doesn't.

---

_Report only. **Which fixes would you like me to make?** Recommendation, in order:
**F1** (defuse the metrics.csv landmine — it's a live liability), then **F3 + F7**
(a trust row with the security cue at the Install decision), then **F2** (promote
dogfooding to a headline band, with the SHOWCASE.md F1 screenshot). **F4** (maker
note) and **F5/F6** (surface CI + Registry, reframe the fairness note) are quick
copy edits that coordinate with CRO.md C6/C7. Everything here uses proof the
product has actually earned — nothing fabricated._
