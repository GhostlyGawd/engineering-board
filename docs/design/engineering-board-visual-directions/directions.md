# Three visual directions

Latest owner direction: A's layout and hierarchy selected. The prior C choice
was explicitly corrected. A's palette, typography and finish were rejected as
insufficiently polished/premium and are reopened in F010. No production styling
target is selected. See ../engineering-board-a-refinement/ for the next round.

F009, Step 3. Approved brief: [design brief](../engineering-board-redesign-brief.md).
Owner approved September 10, 2026. No visual target selected. Images are concept
mockups, not screenshots of implemented behavior or real project evidence.

## Current options

| Option | Concept sheet | Main tradeoff |
| --- | --- | --- |
| A — Continuity | [View A](a-continuity-v2.png) | Familiar identity and approachable hierarchy; smaller departure. |
| B — Sourcebook | [View B](b-sourcebook-v2.png) | Strongest expression of inspectable repository records; more technical. |
| C — Trace | [View C](c-trace.png) | Strong simultaneous evidence inspection; greater information density. |

Recommend A as the starting point for broad onboarding and brand continuity.
B is the strongest alternative if the source record should define the identity.
C favors frequent investigation work. The owner selects the dominant direction.

## Research and source roles

Three style searches: precise monochrome editorial software; developer-tool
typography/product screenshots; Linear dark developer tool. Thirty previews
returned; three full styles retrieved and inspected. Full responses retained
in [refero-styles.md](refero-styles.md).

| Source | ID | Bounded role |
| --- | --- | --- |
| Factory, https://factory.ai | f1ed1d46-4e76-41fe-a9f8-3017e55dc6ee | A: split introduction and flat, ruled information hierarchy only. |
| SST, https://sst.dev | 7b6c53c7-7145-476e-aed8-f2367eef3adb | B: white canvas, mono headline and source record as primary explanatory media. |
| Linear, https://linear.app | 554b801c-3b31-4086-a7e5-ae613cdd618b | C: compact dark surfaces, type, restrained primary action treatment. |
| Existing BRAND.md and audit captures | repository-owned | A: dominant palette, familiar mark, sans type and restrained geometry. All: truthful state and accessible presentation. |

Product screen/flow research is recorded separately in
[pattern-research.md](pattern-research.md). References are ingredients, not a
request to reproduce their product architecture or branding.

Source quality: Factory's response contains malformed `#ef6f2` and a dark-on-dark
button specification; neither is adopted. Its hover-only link guidance is not
adopted. SST conflicts about transparent installation buttons; use a solid white
surface, outlined button and dark interactive text. Low-contrast metadata tokens
are omitted where they would harm readability. These omissions follow the
approved accessibility brief, not an unverified compliance claim.

## Shared content and state

Every sheet contains a landing introduction and investigation view. Same headline:
“Connect findings. Inspect the evidence.” Supporting text: “Repository memory
for engineering agents.” Actions: “Start with Codex” and “Explore example.”
Client handoff: “Ask Codex to initialize Engineering Board in this repository.”
Expected result: “A repository-owned Markdown board.” This follows the README;
no new command syntax is invented for the concept.

Case: visibly labeled “Synthetic example”. Three findings: B001 “Worker skips a
review-ready entry”, B002 “Board shows the wrong lane”, B003 “Ready-work list
omits the entry”. These follow the existing contained demo's scenario.
Hypothesis H001: “Lifecycle rules differ across adapters.” State: “Proposed”.
Evidence: “Three findings share a lifecycle-state pattern.” Alternative:
“Independent filtering errors.” Falsifier: “All adapters use the same rule.”
Outcome: “No outcome recorded.” Source action: “Open source record.”

These short labels are proposed copy. Relationship facts and a proposed cause
remain separate. No fabricated statistics, confirmed results or diagnosis gains.

## A — Continuity

Primary foundation: current Engineering Board brand. Preserve paper #FAF9F5,
ink #17191E, legible amber #9A5B00, compact card-promotion mark, system sans,
generous outer margins, restrained 10px card corners. Borrow only Factory's
split hero and flat ruled content hierarchy. Use amber for the existing mark,
primary navigation/action/focus roles; do not use it as proof of a cause.

Composition: left-aligned introduction with a compact related-findings preview
beside it; below, a wide investigation pane with readable evidence cards and a
source sidebar. Media: functional synthetic example, no decorative illustration.
Reject: sci-fi effects, generic metrics, excessive cards, new source color palette.
Distinctive trait: familiar amber link between a finding and its source.
Tradeoff: strongest continuity, smaller perceived change.

## B — Sourcebook

Primary foundation: SST. Preserve white #FFFFFF, jet #111111 headings, graphite
#403F53 body, IBM Plex Mono-style 48px headline, Rubik-style body, source-first
split hero (record left, headline right), 8px source frame, 4px controls. Links
use #303055 with visible underlines. Syntax colors stay inside the source excerpt;
no colored badges or page background borrowed from code tokens.

Borrow only Factory's horizontal rules for supporting evidence lists. Lower
view: a document with numbered findings in a left index and a wide readable
hypothesis record on the right. Mark reduced to monochrome for this alternative.
Media: Markdown-like record and readable evidence, no photographs or decoration.
Reject: cream canvas, amber accents, pill dashboard cards, colored syntax outside
code. Distinctive trait: the repository record is the hero image.
Tradeoff: strongest transparency, less familiar brand and more technical first impression.

## C — Trace

Primary foundation: Linear style. Preserve #08090A canvas, #0F1011/#161718
surfaces, #F7F8F8 primary type, #D0D6E0 supporting type, #323334 rules, Inter
type and mono identifiers, compact 8px rhythm and 6px controls. Lime #E4F222
is restricted to primary action backgrounds with dark text. Omit decorative
violets, glows, gradients, and success hues; the case is still proposed.

Borrow only Linear's issue-detail pattern: separate item identity, narrative
evidence, and metadata. Upper section: concise centered introduction and clear
actions. Lower view: selected finding list, hypothesis narrative, supporting
source pane simultaneously visible. Text labels carry epistemic state; the
brand mark is monochrome. Media: framed synthetic investigation workspace.
Reject: invented analytics, decorative node cloud, bright status badges, low
contrast metadata. Distinctive trait: follow evidence without losing the selected
finding. Tradeoff: strongest inspection focus, greater density for first-time users.

## Decision ledger

| Decision | Source / role | Why |
| --- | --- | --- |
| Same content and Proposed state | approved brief and existing synthetic demo | Make comparison about design, keep evidence honest. |
| Different composition, type, and density | primary reference per direction | Avoid three palette swaps of one generic interface. |
| A keeps original visual foundation | existing brand, approved evolutionary option | Preserve recognition while improving hierarchy. |
| B leads with a record | SST code-media role + canonical Markdown constraint | Show what the user owns and can inspect. |
| C keeps list, detail and sources visible | Linear screen role | Support tracing and return context. |
| Codex handoff included | audit gap, README first-use instruction | Connect installation to a visible first result. |
| Contrast-sensitive source rules omitted | audit B017, approved brief | Avoid importing known usability hazards. |

## Delivery and limits

One independent image per direction using built-in Image Gen; prompts retained
in prompts.json. Compare at the same sheet dimensions. Generated typography
and illustrative controls are design intent, not exact tokens, accessible
components, or verified interactions. The selected direction needs responsive,
keyboard, source navigation and both-theme verification in the later prototype.
No shipped assets or product code change in this phase. Owner chooses one
dominant direction before implementation; do not average all three.

Independent review requested corrections to A/B marks, amber proposed-state
badges in A, and local synthetic labels on the upper previews. These were
addressed through one targeted Image Gen edit per affected sheet, retained as
v2 siblings. Original sheets remain research history, not current options.
See [review](../../evidence/2026-09-10-visual-options-review.md).

All sheets are 1448 × 1086 (4:3). Exact color values, flat fills, logo geometry,
text rendering and font metrics in raster concepts are approximate; canonical
vector artwork and locked tokens govern the eventual implementation. A's amber
rendering is brighter than its specified token. B's code excerpt is schematic
synthetic content, not a schema example to copy into a real repository.
C's finding breadcrumb must become an explicit selected-finding label beside
the H001 record identity in the prototype. Recovery copy and unseen states
remain part of the approved prototype scope, not demonstrated by these sheets.
