# Engineering Board brand

Current direction: **Graphite, wordmark only**. Approved by the owner after
reviewing the working prototype on 2026-09-11. The three-block mark and
ink/paper/amber identity are superseded.

## Identity

The name carries the identity. Use lowercase **engineering board** in interface
headers; use the stacked wordmark where the name is the main visual. Do not
place a separate symbol beside it. The compact `eb` favicon is a textual
abbreviation for small browser contexts, not a replacement logo or block mark.

The product is repository memory for engineering agents. Show the connection
between findings and their evidence. A relationship or investigation rank does
not establish a root cause. Proposed, confirmed, rejected and recorded outcome
states must remain readable as text, without relying on color.

## Typography

Manrope is the locally stored, SIL Open Font License typeface used by the approved
prototype. It is a production substitute for generated lettering, not a custom
font. The font and license live under `brand/fonts/`.

- Wordmark: weight 800, compact optical spacing. Use outlined SVG for portable
  brand assets and live text with the local font for UI headers.
- Display: weight 500, approximately 60px on desktop, responsive wrapping.
- Reading: weight 400, 14–16px with comfortable line-height.
- IDs, paths and commands: system monospace. Keep mono out of ordinary prose.

Outlined wordmarks have no font runtime dependency. Do not stretch them.
Keep clear space of at least half a lowercase letter height around the name.
Use the horizontal variant in headers and stacked variant for large branding.

## Color and surfaces

`brand/tokens.css` is canonical. The website publishes an exact generated copy
as `docs/assets/brand.css`; the viewer embeds it and the local font into its
self-contained HTML. Do not maintain independent hard-coded copies.

Graphite is the default: #08090A canvas, #141516 panels, #F7F8F8 primary text,
#D0D6E0 reading text, #A5AAB3 secondary labels and #34343A borders. Light mode
uses #FAFAFA canvas, white panels, #151619 primary text and dark neutral labels.
Selection uses a neutral surface and visible rule. Primary controls use a clear
outline; inline links have an underline. No amber, neon, decorative gradients,
glows or colored status badges are part of this identity.

Flat surfaces, restrained 6–8px corners, deliberate margins and typography
provide hierarchy. Keep metadata subordinate without making it unreadably small.
All keyboard controls need visible focus. Verify rendered contrast and states
in both themes; this document is not an accessibility certification.

## Assets and reproduction

- `wordmark-{dark,light}.svg`: horizontal name.
- `wordmark-stacked-{dark,light}.svg`: two-line name.
- `logomark-{dark,light}.svg`: compatibility filenames containing the wordmark.
- `favicon.svg` and PNG sizes: typographic `eb` abbreviation.
- `social-preview.svg` and PNG: outlined name, headline and description.
- `fonts/`: Manrope variable font and OFL license.

Run `uv run --with fonttools --with brotli python scripts/build-brand.py` to
rebuild vector assets. `scripts/render-brand.py` renders PNG derivatives with
local Chromium. These dependencies are for asset authoring only.

Functional product diagrams can use linked record UI and simple connecting
lines. Label synthetic examples locally. Historical validation diagrams retain
their original facts and dates when their palette is updated. Do not decorate
the product with fabricated performance metrics or proof of causality.

## Voice

Plain, specific, technical. Lead with what the user can do, then explain the
mechanism. Preserve the owner-approved controlled-English constraints. No hype,
emoji in product copy, or unsupported effectiveness claims. Do not claim formal
ASD-STE100 compliance without separate qualified verification.

## Evidence

Research, concepts and prototype are retained under `docs/design/` and
`docs/evidence/2026-09-11-graphite-prototype/`. Dated rollout evidence records
rendered verification; prior brand audits are historical context.
