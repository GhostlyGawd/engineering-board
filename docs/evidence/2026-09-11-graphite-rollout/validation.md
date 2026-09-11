# Graphite rollout validation

Owner approved the working prototype and its rollout to the website, generated
board viewer, README and brand assets. Lead: graphite-rollout-root. Website
builder: rollout_website (F013). Viewer builder: audit_inventory_review (F014).
Independent reviewer: brief_review; it did not author implementation. Reviewed
source: f0353be12aa59f315a9a64f42da369db4fbe2ea6.

## Scope and design verification

A's composition, Graphite's dark/light palette and the approved wordmark-only
identity are applied to production sources. Site capture site-desktop.png was
visually compared with the accepted prototype's 01-desktop.png and wordmark-only
study at1448x1086. The site retains introduction/related findings, two-pane
investigation, source links and setup handoff. Added Board navigation points to
real project data; the example remains locally labeled synthetic. Mobile stacks
content without reducing semantic labels to unreadable sizes.

The normal viewer retains real Kanban, ranked investigations, hypotheses,
Learnings, questions, observations, stats and claims. It uses the same local
font and canonical tokens, embedded into deterministic single-file HTML. Source
IDs open canonical records; read-only/regeneration instructions and filter scope
are explicit. No installed source record is replaced by demonstration data.

Wordmarks and social SVGs use font outlines; PNGs are rendered from those SVGs.
The favicon is a textual eb abbreviation of the wordmark, not the rejected block
mark. BRAND.md records the identity and license. README uses the wordmark and a
fresh synthetic-example capture, with historical validation artwork below a
 disclosure. Validation SVG text was retained while its palette was neutralized.
No measured-effect claims or product/evaluation criteria changed.

## Checks

- Full portable suite: 23 pass, 0 fail. See full-tests.log.
- After the landmark correction: viewer55, token coherence15, website7 pass.
- Website Playwright matrix: desktop1448/mobile390, dark/light, clipboard exact
  contents, keyboard/recovery, ID/title/path search, empty/reset, all four example
  source roundtrips; no overflow/page errors/external asset requests.
- Desktop/mobile no-JavaScript paths remain readable and navigable.
- Four website axe4.13 scans: zero violations/incomplete. Lead axe4.12 confirms
  site and final board clean. Reviewer independently repeated board axe after
  fixing the one view-note landmark gap; original finding evidence retained.
- Independent reviewer clicked staged board B001 to its canonical GitHub record,
  observed metadata and confirmed destination. See independent-review.md.
- Site staging allowlists only public files. It regenerates board.html with
  an absolute GitHub source base and fails on renderer failure. It excludes
  design/evidence files and refuses nonempty staging output.

## Limits and release boundary

Validation is local Chromium/expert review, not user research or a universal
accessibility certification. Website publication is verified separately after
merge. A source and website rollout is not an immutable plugin release: changes
are recorded under Unreleased and the published1.14.0 package remains untouched.
No version, checksum or release-tag mutation was performed.

The staging preview used http://127.0.0.1:51330/. Source lives in the isolated
rollout branch; unrelated changes in the owner's original workspace were not
included. Lead owns retained source/scripts/screenshots and this evidence.
Agent cost and elapsed time: not measured.
