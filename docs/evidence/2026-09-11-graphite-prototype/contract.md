# Graphite prototype: implementation and verification contract

F011. Owner approved the working prototype on 2026-09-11. Accountable lead and
claim: graphite-prototype-root. Builder: graphite_builder, isolated worktree
/tmp/eb-graphite-prototype, branch codex/graphite-prototype. Base commit
b423a159e2107ee4c06e4a899e9fbf1bd01a70dd. Builder owns prototypes/graphite;
lead supplies licensed local font/icon assets and owns integration/evidence.
Independent verifier reviews exact prototype hashes, source and browser states.

## Locked visual target

- A3 Graphite image: A's left introduction/right evidence diagram, lower
  two-pane findings/hypothesis view, achromatic dark palette.
- graphite-wordmark-only.png: lowercase heavy compact wordmark, no block mark,
  medium display weight, readable body and mono metadata.
- Combine the two-screen concept into a single home page: one masthead, example
  below hero, installation after example. This integration removes the duplicate
  masthead, not the intended hierarchy. Added states follow the approved brief.
- Theme default dark. A light theme must retain hierarchy and semantic clarity.
- Fonts: Manrope variable (OFL), matching the accepted single-storey-g geometric
  wordmark and display. Neutral small text, system mono record IDs. This is an
  identified production substitute, not a claim of a custom font.
- Icons: Tabler outline (MIT), matching the thin file/arrow controls. Assets and
  licenses retained locally; no brand symbol introduced.

## Architecture and scope

Use static HTML/CSS, local assets, and progressive JavaScript. The approved
self-contained/offline/no-JavaScript viewer constraint takes precedence over
a generic SPA starter. Functional finding cards/relationships remain HTML UI,
not an image of a dashboard. No auth, account, database, network API, real
repository writes, paid font, or generated raster logo is needed.

Prototype lives separately from public docs and normal board generator. Fixing
example source routes here does not fix published B016. Contrast improvements
here do not resolve production B017. No release or deployment in this step.

## Tasks and pass/fail checks

1. At 1448x1086, identify purpose, start route and example. All CTAs navigate.
2. Follow Start with Codex. Inspect/copy published setup commands and existing
   initialization prompt. Show expected result, restart/connection recovery,
   and link into example. Copy feedback means copied, never installed.
3. Explore the three-finding synthetic case. Search B002/title/path, choose an
   entry and read relevant information; enter nonsense, see empty feedback,
   reset and recover. Preserve selected-state visibility and keyboard access.
4. Open H001 and B001–B003 source records and return. Every local target exists,
   contains the intended record, and preserves Synthetic example / Read-only.
5. State what is known: explicit Proposed hypothesis, pattern evidence,
   alternative, falsifier, and No outcome recorded. No false confirmation.
6. Repeat main paths at 390x844 and in light theme. No hidden persistent controls,
   horizontal document overflow, clipped content, or unreadable small labels.
7. Test keyboard focus/order, scrolling code and disclosure navigation. Run axe
   scans and inspect results; incomplete checks are not passes.
8. Disable JavaScript: page/source/installation links and core case remain readable
   and navigable. Offline static assets should not need a CDN or hosted service.
9. Validate actual board_init using current core in a disposable local directory.
   Retain output/scaffold evidence. This does not assert a fresh Codex installation
   or observe an agent's interpretation of the instruction.
10. Build/serve, meaningful static/link checks, no browser errors, screenshots,
    combined source/implementation visual comparisons, and independent review.

No diagnosis-effect metric changes. No user comprehension study is claimed;
independent reviewer answers the intent/state questions as expert validation.
Prototype success means the scoped paths and design checks pass, not proof of
better engineering diagnoses or full accessibility certification.

## Retention and delivery

Screenshots, browser snapshots, core-init result, commands, review, hashes and
design QA are retained here or under prototypes/graphite. Lead owns retention.
Keep local preview running for owner inspection. Source rollout, publication
and the remaining brand assets are later work. Agent cost and elapsed time
will be reported only if available, otherwise not measured.
