---
id: Q002
type: question
title: Which Codex design plugins should enter a canary evaluation?
discovered: 2026-09-09
status: resolved
source: Owner requested a deep web sweep of plugins that improve Codex graphic design, UI, UX, and visual-branding work, with a comparative test plan.
affects: docs/evidence/2026-09-09-codex-design-plugin-landscape.md
---

## Done when

- [ ] The landscape distinguishes installable Codex plugins from skills, MCP servers, browser tools, and adjacent products.
- [ ] Each shortlisted approach has current primary-source evidence for availability, capabilities, setup, data access, pricing when published, and material limitations.
- [ ] A comparison matrix scores options against fixed, reviewable criteria without treating vendor claims as measured quality.
- [ ] A canary suite covers visual generation, brand-system adherence, UI/UX critique, screenshot-to-code fidelity, responsive behavior, accessibility, and round-trip editing.
- [ ] The report recommends a staged shortlist and defines evidence capture, stopping rules, and an independent scoring process before any live trial.

## Comments

- **root-design-plugin-research-20260909** 2026-09-09T17:04:56Z: Lead claimed research. Scope: current Codex-compatible plugins, skills, MCP servers, browser/UI tools, and adjacent design systems; evidence artifact at docs/evidence/2026-09-09-codex-design-plugin-landscape.md. Proposed evaluation criteria remain subject to owner approval before a live trial.
- **root-design-plugin-research-20260909** 2026-09-09T17:37:39Z: Independent verifier required corrections: add plain-Codex control, lane-specific gates, official Codex surface limitation, concrete retained-evidence path, and explicit scorer/aggregation protocol. Lead applied all five to artifact SHA-256 1e9fbf6999f18caee8866690c6e4f1bceb5ae1d706c3d0f2eac726de50578f04; reverification requested.
- **root-design-plugin-research-20260909** 2026-09-09T17:43:37Z: Independent verifier passed corrected artifact SHA-256 f0ba7e748547b2c6b76e9cbd3c1c40ce288970b3576d85c39ba69af3aeff419b after rechecking all acceptance criteria and the corrected Figma rate-limit matrix. All 90 unique cited URLs returned HTTP 2xx/3xx during lead verification. O004 records the durable finding.
- **root-design-free-only-20260909** 2026-09-09T17:52:11Z: Owner decision: evaluation and adoption must use only zero-incremental-cost tools and capabilities. Exclude every feature that requires a paid plan, paid seat, paid add-on, converting trial, or sales contract. Existing Codex capabilities are eligible only when already included without an upgrade. Revise shortlist, canaries, gates, and recommendations accordingly.
- **root-design-free-only-20260909** 2026-09-09T18:06:55Z: Independent verifier passed free-only revision SHA-256 b3191c7ec6da4ac37bc04bc6a30fdf3154131039055d39126741e5a94bd26e4c. It confirmed zero-cost eligibility is a hard owner gate, paid features are excluded from scored/adoption paths, Penpot >=2.15.0 supplies the free round-trip path, and local OSS tools supply QA.
- **root-design-native-imagegen-20260909** 2026-09-09T18:10:34Z: Owner clarification: Codex native ImageGen is approved as a fixed capability in all applicable free-only canary arms because it is included in current Codex access. Use only built-in ImageGen under normal Codex usage limits; do not configure OPENAI_API_KEY, call the paid Image API, or purchase capacity. Included-limit exhaustion stops or defers the run.
- **root-design-native-imagegen-20260909** 2026-09-09T18:16:38Z: Independent verifier passed report SHA-256 3356a15322afcaaebb3cc7d96af2ba0107a6c0e1f4917532282f4731a4c76143. Native ImageGen is fixed across applicable arms, normal included-limit exhaustion stops/defers the matched set, and paid API/key fallback is prohibited.
- **root-design-native-imagegen-20260909** 2026-09-09T18:17:59Z: Resolved after owner confirmed full alignment with the free-only plan once native Codex ImageGen was defined and fixed across applicable arms; independent verification passed report and board integration.

## Answer

The verified answer is recorded in `docs/evidence/2026-09-09-codex-design-plugin-landscape.md` at SHA-256 `f0ba7e748547b2c6b76e9cbd3c1c40ce288970b3576d85c39ba69af3aeff419b`.

- Use a layered stack rather than one cross-category winner: workflow/direction, editable canvas, brand production, and QA.
- Start with a true design-plugin-disabled Codex control and the installed Product Design workflow as separate baselines.
- First canaries: Product Design, Taste, UI/UX Pro Max; Figma, Stitch, patched Penpot; Creative Production and Adobe; then Storybook/shadcn/Playwright/axe as an additive QA layer.
- Keep Canva outside scored evaluation pending confirmation that the proposed use complies with its MCP evaluation restriction.
- Score only lane-applicable tasks, retain evidence at `evaluation/design-plugin-canary-v1/`, and freeze owner-approved weights before any live trial.

Durable Finding: O004.

## Free-only answer (supersedes prior answer)

Owner decision: use and plan only zero-incremental-cost capabilities. The revised, independently verified report is `docs/evidence/2026-09-09-codex-design-plugin-landscape.md` at SHA-256 `b3191c7ec6da4ac37bc04bc6a30fdf3154131039055d39126741e5a94bd26e4c`.

Eligible plan:

- Control A: plain Codex.
- Control B: Product Design using only capabilities already included in current access; Sites and paid connectors are disabled.
- Free instruction challengers: pinned Taste Skill and UI/UX Pro Max basic, with Stark as reserve.
- Free editable canvas: Penpot >=2.15.0 on its $0 cloud plan or existing self-host infrastructure.
- Conditional only after a same-day whole-task $0 receipt: Stitch, Figma Starter read-only, Creative Production, and ImageGen. Quota exhaustion stops the arm without purchase.
- Local QA: Storybook, allowlisted free shadcn registries, Playwright, axe-core, and Pa11y.

Paid or upgrade-dependent Figma writes/Code Connect, Canva scored use, Adobe, Builder, Anima, Webflow paid features, v0, paid 21st/Chromatic/Deque, Higgsfield, Runway, commercial Remotion use, and Sites publishing are excluded from canary arms and adoption.

## Native ImageGen clarification (supersedes conditional ImageGen wording)

Owner-approved native Codex ImageGen is a fixed capability in every applicable matched canary arm. The revised, independently verified report is `docs/evidence/2026-09-09-codex-design-plugin-landscape.md` at SHA-256 `3356a15322afcaaebb3cc7d96af2ba0107a6c0e1f4917532282f4731a4c76143`.

- Built-in ImageGen uses `gpt-image-2` and counts against normal Codex usage limits.
- It requires no separate zero-cost receipt beyond this owner decision and a current native-availability record.
- Keep ImageGen identical across every applicable matched arm so it does not confound design-skill comparisons.
- If included Codex/ImageGen limits are exhausted, stop or defer the complete affected matched set.
- Never set `OPENAI_API_KEY`, invoke the paid Image API, purchase capacity, or substitute a paid external image service.
- Creative Production remains a separate conditional candidate; its non-ImageGen plugin/app/MCP path must pass the whole-task $0 eligibility gate.

## Finding

The owner selected a zero-incremental-cost Codex design stack and approved native Codex ImageGen as a fixed capability. Built-in ImageGen means `gpt-image-2` through Codex; it counts against normal included Codex usage limits and must never fall back to `OPENAI_API_KEY`, the paid Image API, purchased capacity, or a paid external image service.

The canary uses plain Codex and Product Design as controls, free pinned Taste Skill and UI/UX Pro Max as instruction challengers, Penpot >=2.15.0 for editable canvas round trips, and local Storybook/shadcn/Playwright/axe-core/Pa11y for QA. Paid or upgrade-dependent capabilities are excluded. ImageGen remains identical across every applicable matched arm; if included limits are exhausted, the complete affected matched set stops or defers.

Evidence: independently verified report `docs/evidence/2026-09-09-codex-design-plugin-landscape.md`, SHA-256 `3356a15322afcaaebb3cc7d96af2ba0107a6c0e1f4917532282f4731a4c76143`; durable observation O004; official OpenAI Image Generation documentation cited in report footnote 36.
