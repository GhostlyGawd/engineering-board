# F011 independent prototype review

Decision: **Pass for the assigned source and browser correctness scope**, with one nonblocking mobile text-spacing observation below. This is not an installation, release, production-accessibility, or diagnosis-effect approval.

Reviewer: `prototype_verifier`, a fresh agent context. Read AGENTS.md, docs/DEVELOPMENT.md, and contract.md before source inspection; did not read the author's result reports before forming this assessment. Started at `ebb575197339372c4edb9c283d432f6141ffd9c7`; final reviewed source is `bed2360f30bcf9f345c224df4f9a10403339c0ad`. The only intervening source change adds `role="group"` to the labelled relationship container in generator and HTML. The complete browser matrix ran after that change. Verified prototype bytes match the preview worktree and each of the six served HTML documents matches repository bytes. Retained SHA-256 inventory: [verifier-hashes.json](verifier-hashes.json).

## Evidence and results

- `python3 prototypes/graphite/check.py` exited 0: all local targets/anchors/assets exist; four no-script records remain present; fixture bytes match; missing-target and hidden-record challenges are rejected; raw fixture markup is escaped.
- Used `npx --yes agent-browser@0.37.1 --session eb-prototype-review` independently to inspect desktop, search/select B002, open its source and return, then switch to 390×844/light, enter nonsense and recover through Clear search. Closed only this reviewer browser session.
- `uv run --with playwright python docs/evidence/2026-09-11-graphite-prototype/verifier-browser.py` exited 0 using local Chrome for Testing 153. The retained script accepts `AXE_PATH` for a local axe-core 4.13.0 installation. Its [complete results](verifier-results.json) cover 1448×1086 and 390×844 in both dark/light, plus both widths with JavaScript disabled.
- At each JS-enabled width/theme: Start with Codex reaches installation; both clipboard controls announce copied, commands match the clipboard, and no install success is claimed. Recovery disclosure opens with Enter and explains restart/connection checks. Search by B002, title and path gives the intended result; nonsense shows empty feedback; reset restores all findings and focuses the input.
- Keyboard Enter selects each finding and overview, moves focus to the visible record with an outline, and preserves `aria-current` for the finding. All B001–B003/H001 source links and explicit return links work. Space opens original-Markdown disclosures. Source pages retain Synthetic example / Read-only and show the intended IDs. Theme survives navigation. Skip to content works.
- H001 explicitly labels a proposed hypothesis, pattern evidence, an alternative, a falsifier, and No outcome recorded. Source language explicitly avoids confirmed-cause claims. The prototype explains that commands execute in the user's terminal and cannot install or change a repository.
- All four JS-enabled home scans using axe-core 4.13.0 returned **0 violations and 0 incomplete checks**. No page JavaScript errors, external asset requests, or horizontal document overflow occurred in these paths. Source pages also had no horizontal overflow with original Markdown expanded. Code wraps and remains reachable through normal page scrolling.
- With JavaScript disabled, all four core panels are visible, enhancement-only controls disappear, installation remains reachable, and all four source roundtrips work at both widths.

Inspected the actual A3 image and graphite-wordmark-only identity image using `view_image`, then actual desktop and mobile captures. The implementation retains the left introduction/right relationship diagram at desktop, lower findings/detail panes, achromatic palette, and lowercase compact wordmark without a block symbol. The mobile arrangement stacks these into readable controls and records. The lead owns the full combined visual comparison QA.

Retained screenshots include [desktop viewport](verifier-desktop.png), [mobile recovery and focus](verifier-mobile-recovered.png), [mobile source light](verifier-mobile-source-light.png), and `verifier-{1448,390}-{dark,light,nojs}.png` full pages.

## Nonblocking observation

At mobile width, hiding `<br>` removes the separator in two short passages: “Your first board.A lasting record.” and “Three findings.One pattern to investigate.” This is visible in the mobile captures and does not prevent identification, navigation or recovery. Recommend preserving a space when collapsing those line breaks. No material source/browser requirement failure was found.

## Limits

This is expert validation in local Chromium, not a user comprehension study, exhaustive browser/assistive-technology coverage, or accessibility certification. Automated axe scans here cover the home page in four width/theme states; source navigation and disclosures received behavioral/manual checks. Actual `board_init` validation and full source-to-design comparison belong to the lead's separate evidence. No fresh Codex installation, actual repository write through this UI, production B016/B017 fix, publication, or effect metric was claimed. Agent cost and elapsed time: not measured.

## Final delta review — 796e50b

Final decision: **Pass**, including the mobile text-spacing correction, at `796e50b56797165975fca214a4af18c47e719f16`. The nonblocking observation above is resolved.

Independently verified that `build.py` and `index.html` differ from the matrix-tested `bed2360` only by adding one space immediately after each `<br>`. Both repository files exactly match their preview-worktree copies and the corresponding bytes served at localhost. A fresh agent-browser session at 390×844 reports “Your first board. A lasting record.” and “Three findings. One pattern to investigate.”; document width remains 390. Closed that reviewer session. This targeted delta check is sufficient for this text-only correction; the earlier behavioral matrix remains the evidence for unchanged interactions.

[Final delta and hashes](verifier-final-delta.json):

- `build.py`: SHA-256 `19e078f120939300436f09700daa71192e00469bd5e262d45cbc6d1cc8b42618`
- `index.html`: SHA-256 `65c1837e423617ee2232c86f729b8a79e33caaa7dd87c2fff5c4819336787e99`
