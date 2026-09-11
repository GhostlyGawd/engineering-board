# Independent Graphite rollout review

Reviewer: `brief_review`. Date: 2026-09-11.
Initial source: `c9f542b31b2f67ceee982dfb94d1a758931fa15e`.
Final reviewed source: `f0353be12aa59f315a9a64f42da369db4fbe2ea6`.
Worktree: `/tmp/eb-graphite-rollout`; staged site: `http://127.0.0.1:51330`.

**Verdict: bounded pass after correction.** No unresolved material finding in
this source and local website review. This does not establish deployed or
released installation behavior, a full accessibility certification, or improved
agent diagnoses.

## Scope and independence

Read the owner-approved rollout requirements, AGENTS.md and DEVELOPMENT.md,
then inspected the source diff against upstream/main before reading builder
outputs. Reviewed the website, source examples, guide, README changes, brand
sources and generators, viewer changes, Pages staging/workflow and relevant
regression tests. The approved wordmark-only image was visually inspected.
No product or board files were edited by the reviewer.

## Evidence

- Independently ran `bash tests/site/automated.sh`, `bash tests/token-coherence.sh`
  and `bash tests/view/automated.sh` at the initial revision: exit 0; respectively
  7 tests, 15 checks and 55 checks passed. Coverage includes canonical token
  embedding, self-contained font and reduced-fixture fallback, hostile title
  and claim escaping, deterministic output, source links, staging allowlist,
  occupied-output refusal and renderer-failure behavior.
- Source inspection confirms the public build regenerates the actual board,
  copies named public files plus `assets/` and `example/`, and does not publish
  the sibling design/evidence/prototype directories. Existing output is not
  deleted. No new runtime database, service, or agent orchestration is introduced.
- Browser matrix captured site and actual board at 1448 and 390 pixels, dark
  and light. All eight states had one main landmark and no document overflow.
  Visually inspected desktop-dark/site, mobile-light/site, desktop-light/board,
  mobile-dark/board against the approved identity: the Graphite palette,
  typography and wordmark-only hierarchy carry through. The favicon source
  derives typographic `eb` from the wordmark font, not the rejected block symbol.
- Clicked synthetic B001, opened its HTML source, returned to the selected
  record, and exercised search no-results and reset. Tested actual board search
  and no-results. No page errors were reported. See
  [browser results](review-browser-results.json) and `review-*.png` captures.
- Clicked the actual board B001 link. GitHub loaded its named Markdown record
  and rendered the B001 metadata, rather than the former Pages 404. See
  [GitHub snapshot](review-github-B001.txt). This verifies that particular
  destination; it is not exhaustive verification of external GitHub links.
- At 390px with JavaScript disabled, both pages retain readable main content,
  hide the theme control and avoid document overflow. Source inspection and
  focused tests preserve the viewer's offline baseline and static evidence.
- README/assets adopt the approved identity. The synthetic/public and actual
  project board remain distinct. Proposed hypotheses, alternatives, falsifiers,
  no-outcome state and score-not-confidence language retain uncertainty. Product
  diagnosis-effect criteria remain unchanged. Changelog entries are Unreleased;
  this review does not claim a new plugin version.

## Finding and correction

At the initial revision, independent axe-core 4.12.1 reported one moderate
best-practice `region` violation: `.view-note` was before the main landmark.
See [initial board scan](review-board-a11y.json). This was a remaining part of
B017 and prevented a clean accessibility completion claim.

The lead's final revision moves `<main id="main">` ahead of this guidance in
the generator and committed board. Independently inspected the exact two-file
delta, then reopened the regenerated staged board and reran axe: **zero
violations and zero incomplete checks**. See
[final board scan](review-board-a11y-final.json). The site scan also returned
zero violations and zero incomplete checks: [site scan](review-site-a11y.json).
The full browser matrix predates this small landmark correction; its source
safety conclusions remain applicable. The final scan verifies the changed
requirement directly.

## Limits

This was a focused source, security-boundary and browser review. It did not run
an exhaustive release suite, an installed client walkthrough, a screen reader,
a full keyboard traversal, or every populated hypothesis lifecycle state.
Axe results concern the tested default rendered states, not every theme/state
combination. The staged real board has no multi-entry clusters; populated
uncertainty behavior is supported here by synthetic source inspection and
viewer regression checks. Broader product-effect claims need their existing
separate evidence. Agent cost and elapsed time were not measured.

Only reviewer browser session `eb-rollout-review` and its temporary no-JS
context were used; the reviewer session was closed.
