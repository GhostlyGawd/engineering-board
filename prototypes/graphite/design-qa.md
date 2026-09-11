# Graphite prototype design QA

final result: passed

Scope: local prototype of the approved A layout, Graphite palette and wordmark-only
identity. Source checked at 796e50b; this document does not approve a public rollout.

## Source and rendered evidence

- Layout source: ../../docs/design/engineering-board-a-refinement/a3-graphite.png.
- Identity override: ../../docs/design/engineering-board-a-refinement/identity/graphite-wordmark-only.png.
- Capture directory: ../../docs/evidence/2026-09-11-graphite-prototype/.
- Full comparison: comparison.png, generated from comparison.html; source and
  implementation each 1448 × 1086, native image density. The combined capture
  is 2952 × 1174 including captions and gutters.
- Focused typography comparison: type-comparison.png. It places the identity
  specimen's application crop and implemented header together at native pixel
  density. The specimen is a type reference, not the same screen state; no exact
  pixel-equivalence claim is made for it.
- Default desktop: 01-desktop.png. Investigation, source, install, empty, light,
  mobile and mobile-source captures are numbered 02 through 08. Independent
  captures and matrices are retained alongside them.
- CSS viewports: 1448 × 1086 desktop and 390 × 844 mobile, device scale 1.
  Mobile is an adaptation because no mobile mockup was approved.

## Five fidelity surfaces

1. **Typography.** Manrope variable is the locally served, OFL-licensed substitute
   for the generated grotesk. Lowercase wordmark uses 800 weight; display uses
   500 at 60px desktop; readable evidence text uses 14px; identifiers are mono.
   The three-block mark is absent. The combined type inspection preserves strong
   wordmark / medium heading / regular evidence hierarchy. Exact generated font
   outlines are not reproducible type specifications. Further optical wordmark
   tuning is P3 and does not block this prototype.
2. **Layout and rhythm.** Desktop keeps the split introduction, visible related
   findings, two-pane investigation, thin borders and subdued selection. Hero
   divider moved from about y652 to y520 after correction, near the reference's
   y490. One masthead replaces the mockup's duplicated two-screen headers. Added
   search, overview, theme and installation are approved functional scope. These
   integrations explain remaining spacing differences. At mobile, findings and
   diagram stack rather than compressing evidence to unreadable labels.
3. **Colors and tokens.** Flat #08090A/#141516 surfaces, #F7F8F8/#D0D6E0 text,
   neutral badges and selection, #34343A rules. The implementation omits raster
   texture and uneven illumination. Light theme preserves hierarchy and state.
   Four home axe scans found no contrast or other violations/incomplete checks;
   this is bounded evidence, not certification.
4. **Assets and icons.** Wordmark is live type, not a raster logo; no rejected
   symbol returns. Tabler's locally retained file and navigation icons provide
   matching outline weight. The relation graphic consists of accessible linked
   record UI and connectors, not a screenshot placeholder. Refero permits
   code-native functional diagrams; there is no photographic or decorative asset
   in the selected design that needs bitmap generation.
5. **Copy and content.** Approved headline, subtitle, initialization instruction
   and expected board result are preserved. Three synthetic findings, proposed
   cause, evidence, alternative, falsifier and no-outcome state are distinct.
   Source pages show original bundled Markdown and return to the chosen record.
   H001 is explicitly illustrative. Instructions never report successful
   installation from a copy action.

## Comparison history

- Initial desktop screenshot showed a hero about 160px taller than the reference
  and forced two-line hypothesis title. P2: pushed required evidence down and
  weakened composition. Removed extra hero prose/eyebrow, tightened header/hero
  spacing and removed forced title break. Corrected capture 01-desktop.png and
  combined comparison show all core hypothesis fields in the viewport.
- Initial mobile used tiny diagram/badge text. P2: difficult evidence reading.
  Increased semantic labels/body and stacked the diagram; 07-mobile.png shows
  the revised layout, with mobile source text also checked at 390px.
- Axe initially reported an incomplete check for a labelled generic div. Added
  role=group to the relationship container. Final four scans have no incomplete
  or violation results.
- Independent reviewer found missing word spaces when mobile hides line breaks.
  Added literal spaces in generator and generated HTML; targeted final review
  at 796e50b confirms corrected visible text and no overflow.

## Interaction evidence and limits

Lead's eight scenario checks and fresh independent review cover CTAs, search by
ID/title/path, selection, no-results reset, all four source-record roundtrips,
clipboard exact content, recovery disclosures, keyboard focus and skip link,
theme persistence, and desktop/mobile no-JavaScript navigation. No page errors
or external asset requests were observed. All local links/assets are checked by
check.py, including adversarial missing-page/hidden-content/escaping checks.

Core board_init succeeded in a disposable directory and repeated without new
creations. The existing connected Codex MCP also initialized and listed a project
in a separate disposable directory; actual Codex installation was not repeated. The prototype does not
write a board, talk to an agent, or fix the public B016/B017 deployment. No
diagnosis benefit, user-preference result, cross-browser coverage or exhaustive
assistive-technology compliance is claimed.

No actionable P0/P1/P2 finding remains within this prototype scope. P3 optical
wordmark refinement may follow the user's hands-on review. Source and browser
independence is documented in independent-review.md and verifier-final-delta.json.
