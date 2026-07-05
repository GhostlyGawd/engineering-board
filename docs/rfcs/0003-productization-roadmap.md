# RFC 0003 — Productization roadmap: distribution, retention, community, monetization

_Status: Living. Written during the product-improvement loop, 2026-07-05. Supersedes
scattered "next steps" notes in `.goal/`; this is the single ranked roadmap._

The mechanics work (v1.2.0 shipped dual-distributed, branded, tested) and the
experience has been hardened across twelve improvement cycles. What remains is not
more core features — it is turning a working tool into an adopted, sustained
product. This RFC records the decided sequence and the reasoning, so the work is
deliberate rather than reactive.

The frame is five levers, in dependency order. Each names the persona, the current
gap (measured, not imagined), the smallest shippable slice, and — for rejected
ideas — why we said no. A decided "no" is a deliverable.

## Lever 1 — Ship the queued release (1.3.0)

**Gap.** ~40 merged fixes since 1.2.0 (twelve hardening cycles) reach zero installs
until the version increases — users only receive fixes when `plugin.json` /
`marketplace.json` bump. The improvement loop is one confirming clean cycle from
convergence.

**Slice.** Run the C13 confirming DISCOVER sweep; if clean under the documented
severity rubric, bump both manifests to 1.3.0 in lockstep, promote the CHANGELOG
`[Unreleased]` heading, and add the `FINAL_REPORT.md` closing section. The git tag
itself stays human-gated (the sandbox relay rejects tag pushes — BLOCKERS B2).

**Why first.** Every other lever assumes users can receive the current code. This
one unblocks the rest.

## Lever 2 — Execute distribution (mostly human-gated)

**Gap.** The product is installable only from its own repo marketplace. All other
channels are prepared but unsubmitted (`.goal/LAUNCH.md`). Distribution, not
features, is the adoption bottleneck.

**Slice.** Prepare every artifact the autonomous run *can* produce — a `server.json`
for the official MCP Registry and a `smithery.yaml` for Smithery — so each human
submission is a single command. Keep `LAUNCH.md` the authoritative checklist:
awesome-claude-code (issue), Claude community marketplace (`claude plugin validate`
→ form), MCP Registry (auto-syndicates to PulseMCP/Glama/mcp.so), Smithery,
awesome-mcp-servers. Repo metadata (description, topics, social preview) and tag
pushes are Settings-UI / push-rights steps a human runs.

**Why second.** No point optimizing retention for users who can't find the product.

## Lever 3 — Retention: first-run visibility + pipeline continuation

**Gap (measured, on the `eb-self` board).** The first captured finding is invisible
(**B005** — buried in `_sessions/`, no confirmation); advancing one entry through
`tdd → review → validate` needs a session restart per discipline (**B006**); a
validator pass dead-ends with nothing telling the user to resolve (**B007**). A new
user's first impression is "did anything happen?" followed by "the pipeline feels
broken." That is the churn cliff.

**Slice.** Make capture emit a one-line, throttled confirmation ("captured N
finding(s) → `/pm-start` to promote"); make a validator pass point explicitly at
`/board-resolve`; document (and where cheap, smooth) the per-discipline continuation
so it reads as a designed primitive rather than a bug. These are the highest-leverage
UX fixes because they sit on the exact path from install to felt value.

**Why not the Conductor here.** RFC 0001's always-on orchestrator would subsume
B006/B007 by driving disciplines automatically — but it needs infrastructure this
run cannot stand up (cross-session supervision, spawned observable sessions, PR
credentials). It stays a Draft RFC and the honest roadmap headline, not a slice we
pretend to ship. We fix the friction directly instead.

## Lever 4 — Community scaffolding (currently at zero)

**Gap.** `.github/` holds only two workflows. No `CONTRIBUTING.md`, issue/PR
templates, `SECURITY.md`, `CODE_OF_CONDUCT.md`, or `FUNDING.yml`. For an
OSS-maintainer-targeted tool this is a credibility and contribution gap.

**Slice.** Add the standard health files. Two are more than boilerplate here:
- **`SECURITY.md`** turns twelve cycles of adversarial hardening (a documented
  reject-filter corpus, an accepted-residual boundary, a severity rubric) into a
  public trust signal — unusual for an agent tool and directly on-message.
- **`CONTRIBUTING.md`** advertises the real contributor-friendliness asset: the test
  suite is bash + `python3` only, no install step.
- Make the `eb-self` board the honest public roadmap — "our roadmap is run by the
  product" is both true and the best possible demo of what the product does.

## Lever 5 — Retention moat: surface Learnings at the moment of need (F003)

**Gap.** Learnings (`L###`) are the stated moat — durable, in-repo memory that makes
the product smarter about *your* repo over time — but they are currently inert files
nobody reads. The compounding value is invisible, so it can't drive retention.

**Slice.** Surface matched Learnings where a user actually is: at session start
(SessionStart hook summary) and in `/board-view`. The mechanic that makes uninstalling
costly is "it visibly knows things about my codebase now" — that only works if the
knowledge is shown.

## Monetization (sequenced after adoption, not built here)

Recorded for direction, deliberately **not** implemented in this run — there is no
user base to monetize until Levers 1–2 land, and premature paywalls would break the
positioning. When the time comes, the shape that fits an MIT git-native tool:

1. **GitHub Sponsors / `FUNDING.yml`** — zero cost, ships in Lever 4 as a signal.
2. **Open-core around the Conductor.** The plugin/MCP board stays free (it is the
   wedge and the moat); the hosted, always-on orchestrator — the part that needs
   infrastructure and supervision — is the natural paid tier. "Free board, paid
   autonomous workforce."
3. **Team tier** — a cross-repo board hub aggregating many committed boards into one
   read-only dashboard, org-wide Learnings, SSO/audit. Because state is committed
   markdown, the dashboard is a pure *reader*: convenience is billable without ever
   holding the customer's data hostage. That is on-brand — "the board is the database"
   means the customer always owns the database.

**Rejected:** paywalling the plugin itself or per-seat licensing the markdown format.
Either would destroy the differentiator that is the entire product.

## Sequence

| # | Lever | This run ships | Human-gated remainder |
|---|---|---|---|
| 1 | Release 1.3.0 | manifests + CHANGELOG + report | tag push + GitHub Release |
| 2 | Distribution | `server.json`, `smithery.yaml`, LAUNCH refresh | submissions, repo settings |
| 3 | Retention UX | B005 / B006 / B007 fixes + tests | — |
| 4 | Community | health files, SECURITY, FUNDING | enable Discussions |
| 5 | Learnings surfacing | F003 slice + tests | — |
| — | Monetization | direction recorded | all build/business steps |

Levers 2–5 batch into a 1.4.0 release once landed.
