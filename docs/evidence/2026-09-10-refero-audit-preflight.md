# Engineering Board redesign: step 1 preflight

Update: the owner authorized an open-source browser fallback. Browser setup now
works, and the captured first-pass audit is in
[the report](2026-09-10-refero-audit/report.md). The original blocker below is
retained as history, not current status.

Board entry: engineering-board/F007. Accountable owner: refero-audit-20260910-root.
Source revision: b423a159e2107ee4c06e4a899e9fbf1bd01a70dd, with pre-existing workspace changes.
Session local date: 2026-09-10; board service receipts use 2026-09-11 UTC.

## Scope and acceptance

Audit the current website, README and installation path, agent command journey,
and HTML board viewer before defining a design brief. Capture the current
discover → start → inspect evidence → understand next action journey. Retain
numbered screenshots, observations, strengths, friction, accessibility risks,
and independent review. Tie findings to captured evidence and separate source
observations from usability hypotheses. No product implementation, branding
selection, release, deployment, or evaluation-success changes are in this step.

## Capture status

Browser runtime setup succeeded. Browser selection returned `No browser is
available`. After reading runtime troubleshooting, one discovery call returned
`[]`. No screenshots or interaction tests were possible. This document is an
audit preflight, not a completed visual or usability audit. Saved Product Design
context preflight found no saved context. Refero tools are exposed; reference
research and design selection have not started.

## Source inventory and capture plan

| Step | Source | Capture and question |
| --- | --- | --- |
| 1. Discover | `docs/index.html`, `README.md` | Website and rendered README: can a visitor identify the product purpose and next action? |
| 2. Start | Website install section, README quickstart, `mcp-server/README.md` | Follow one client path into the first useful result; observe instructions and recovery. |
| 3. Inspect | `commands/board-view.md`, `hooks/scripts/board-view.sh` | Capture a freshly generated board, search/filter states, and entry-source navigation. |
| 4. Understand evidence | Viewer pattern-intelligence section and hypothesis detail commands | Observe how proposed causes, evidence, alternatives, and next actions are communicated. |

The public website URL referenced in source is
https://ghostlygawd.github.io/engineering-board/. Its current deployment has
not been observed. Existing checked-in screenshots and the older coherence
audit are context only, not evidence from this audit run.

## Questions to investigate

- BRAND.md explains the mark through promotion across workflow columns; the
  README and website describe pattern memory and root-cause investigation.
  Does the identity help users understand that current purpose?
- The website source places multiple milestone proof illustrations before
  installation. Does that sequence explain value or require too much context?
- The viewer is documented as a derived, read-only surface. Can a user tell
  when it needs regeneration and where an investigation action belongs?

These are research questions, not demonstrated user failures. Preserve the
owner-approved controlled-English constraints and qualify all product-effect
claims during later design work.

## Resume

Connect a browser to this session, then capture the numbered journey before
writing visual findings. Review current sources and any intervening changes.
After the evidence-backed audit is complete, present it for the next step:
the short design brief. Independent source-review results are recorded on F007.

No implementation tests were needed. User task outcomes, agent cost, and elapsed
time are not measured. Product and brand files were not changed.
