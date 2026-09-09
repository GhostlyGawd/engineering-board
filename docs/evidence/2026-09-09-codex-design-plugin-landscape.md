# Codex Design Tool and Plugin Landscape

## Decision summary

Q002 should advance a **zero-incremental-cost stack only**. Every arm must run under an entitlement already included in the current Codex account or under free/open-source software that creates no seat, subscription, add-on, usage, hosting, or commercial-license charge. A free trial that converts, a limited credit grant that invites purchase, a contact-sales feature, and any capability that requires an upgrade are ineligible.

The recommended canary is:

1. **Workflow and code-native direction:** plain Codex as Control A; the current Product Design workflow as Control B only with its included local/browser capabilities; then pinned Taste Skill and UI/UX Pro Max as free instruction-only challengers, with Stark as a narrower reserve. Product Design must not invoke Sites publishing, paid connectors, or any capability outside the current entitlement.
2. **Editable round trip:** pinned Penpot MCP at version 2.15.0 or later, using Penpot’s free cloud tier or a self-hosted instance whose infrastructure is already available at no incremental cost. This is the path that makes C6 achievable without a paid Figma Full seat or Code Connect.[^19][^41][^48]
3. **Conditional exploration:** Google Stitch may run only after a same-day receipt proves the current account can complete the whole assigned task for $0. Figma Starter may supply optional read-only context only after the same proof; it is not a scored write or round-trip arm, and Code Connect is prohibited. Quota exhaustion stops either path as an arm failure; it never authorizes an upgrade or purchase.[^18][^37][^38]
4. **Local verification:** Storybook, shadcn, Playwright, axe-core, and Pa11y. These free/open-source tools ground components and verify implementation, responsiveness, and accessibility.[^28][^29][^30][^32][^34]

Brand-production evaluation should use synthetic brand specifications, repository-native HTML/CSS/SVG assets, freely licensed local assets, and native Codex ImageGen as a fixed capability in every applicable arm. The owner has confirmed that ImageGen is included in current Codex access. Official OpenAI documentation says built-in image generation uses `gpt-image-2`, counts against normal Codex usage limits, and consumes those limits about 3–5 times faster on average than comparable non-image turns.[^36] Do not set `OPENAI_API_KEY` or switch to the paid Image API for larger batches. Normal included-limit exhaustion stops or defers the affected matched run without purchasing capacity. Creative Production may orchestrate the workflow only when its complete non-ImageGen tool path is already included. Canva, Adobe, Higgsfield, Runway, and other paid external image services are excluded from scored use.

No source found demonstrates that any shortlisted plugin materially improves current Codex across this full task set. The strongest external evidence instead warns against assuming improvement. OpenSkillEval evaluated more than 600 tasks and 30 open skills and found that popular skills often failed to beat the no-skill agent consistently, with effects depending on model and harness.[^2] UI Bench’s separate, LLM-judged study found Anthropic’s `frontend-design` skill improved one Claude model by 1.7 points but reduced another by 1.8 points over ten landing-page variations.[^3] Those are directional studies, not evidence about the candidates on this host. A controlled canary is therefore required.

This report fixes the free-only task corpus and proposes scoring and stopping rules. **The project owner still must approve the success criteria and weights before any live evaluation starts.** The zero-cost eligibility gate is an additional hard gate and cannot be waived by a canary operator.

## Scope and evidence standard

The sweep was current on **2026-09-09** and covered tools that could materially change Codex work in graphic design, UI, UX, visual branding, screenshot-to-code, prototype iteration, visual critique, accessibility, and round-trip design/code editing. It included:

- Codex plugins with a `.codex-plugin/plugin.json` manifest;
- portable Agent Skills or Claude plugin skills that can be installed or adapted for Codex;
- MCP servers that expose design canvases, component registries, browsers, or test engines;
- adjacent hosted design/code APIs that Codex can call but that are not Codex plugins.

The categories below are intentionally strict.

| Label | Meaning | Typical authority and risk |
|---|---|---|
| **Codex plugin** | An installable bundle with a Codex manifest. It can contain skills, apps, MCP configuration, agents, commands, hooks, or assets. | Inspect every bundled surface; installing a plugin can add executable or remote capabilities. OpenAI’s public examples use `.codex-plugin/plugin.json` as the required manifest.[^4] |
| **Agent Skill** | A `SKILL.md` instruction package, optionally with scripts, references, and assets. | Often portable, but host-specific tool names and paths may need adaptation. The open Agent Skills specification defines this layout and warns that `allowed-tools` support varies by client.[^5] |
| **MCP server** | A local or remote tool server. It is a capability endpoint, not a design methodology. | Review auth, tool permissions, network binding, data sent to the server, and package pinning. |
| **Connector/app** | A hosted account integration exposed through Codex. It may be bundled in a plugin alongside skills. | OAuth/account scope and service data policy dominate. |
| **Adjacent service/API** | A design or code-generation product Codex can invoke by API, CLI, or browser, without a Codex plugin bundle. | Do not describe it as a plugin. Compare its output as an external benchmark or specialist tool. |
| **Deterministic test layer** | Browser automation, component tests, visual regression, or accessibility rules. | It verifies outcomes; it should not receive credit for initial visual originality. |

Evidence markers used in the tables:

- **V** — vendor or maintainer documentation establishes availability or a claimed capability.
- **M** — measured result with a stated corpus or method. Results remain limited to that study’s models, prompts, and judges.
- **O** — directly observed on the research host through local manifests or `codex plugin list`.
- **U** — unmeasured analytical judgment or a claim that still needs the canary.

Public GitHub manifests lagged this host’s remote catalog on 2026-09-09. `codex plugin list` under Codex CLI 0.153.4 reported Figma 2.0.21 and Product Design 0.1.54, while the public OpenAI plugin repository reported 2.0.20 and 0.1.52 respectively.[^6] The report uses the host catalog version for availability and the public repository for inspectable behavior. Catalog availability can vary by account, platform, and region; this host snapshot is evidence of availability here, not a universal entitlement. Version drift is itself a reason to pin the exact evaluated package and retain its bytes.

### Supported Codex surfaces

Plugin availability depends on the Codex surface. Official OpenAI documentation says plugins can be installed and used for Codex through the ChatGPT desktop app and through the Codex CLI plugin browser. The Codex IDE extension does not support plugin bundles.[^58]

| Surface | Plugin-bundle support | Evaluation consequence |
|---|---|---|
| Codex in the ChatGPT desktop app | Supported through the Plugins directory | Use only for a capability that passes the zero-cost entitlement gate; paid connector workflows remain excluded |
| Codex CLI | Supported through `/plugins`; start a new session after installation | Valid primary environment for local skills, MCP-backed plugins, and isolated repository trials |
| Codex IDE extension | Not supported | Do not generalize a desktop/CLI plugin result to IDE use. A separately configured MCP server or copied skill is a different arm and must be labeled, versioned, and scored separately. |

The initial canary should run locally in Codex CLI when possible. A desktop-only capability can enter only after its zero-cost entitlement is proved and retained; no paid connector cohort is part of Q002.

## Landscape taxonomy

### Workflow and design-direction skills

These tools change how Codex frames and executes work. They generally do not add a new canvas or authoritative design data.

| Candidate | Accurate category | Availability and evidence | Material capability | Main limitation |
|---|---|---|---|---|
| **OpenAI Product Design 0.1.54** | First-party Codex plugin; skill-only on this host | Installed and enabled (**O**); public 0.1.52 manifest and README (**V**) | Briefing, image-based directions, screenshot-to-code, URL cloning, screenshot-backed UX/accessibility audit, design QA | Eligible only through capabilities already included in current access; disable Sites publishing and paid connectors; native ImageGen is fixed in applicable arms[^1][^36] |
| **OpenAI Build Web Apps 0.1.2** | First-party Codex plugin; skill bundle | Public Codex manifest (**V**); not installed on this host (**O**) | Image-first frontend concepting, shadcn composition, browser verification, app integration | Broad full-stack scope overlaps Product Design; “10/10” fidelity is an instruction, not a demonstrated metric[^7] |
| **Anthropic `frontend-design`** | First-party Anthropic Agent Skill / Claude plugin; adaptable to Codex | Public skill repository; Agent Skills format (**V**) | Strong visual-direction prompt covering typography, palette, motion, composition, and avoidance of generic defaults | Written and demonstrated for Claude; effects vary by model, and no current Codex trial was found[^8] |
| **Anthropic `web-artifacts-builder`** | First-party Anthropic Agent Skill; adaptable | Public skill with React/Tailwind/shadcn scaffold and bundler (**V**) | Multi-file artifact scaffold and single-HTML packaging | Solves Claude artifact packaging, not general repository UI work; redundant in a normal Codex repo[^8] |
| **Taste Skill v2 experimental** | Community portable Agent Skill pack | Public repository; explicitly references Codex (**V**) | Opinionated anti-generic visual rules, adjustable variance/motion/density, redesign and image-reference skills | Experimental; rule rigidity and React/Next coupling have open portability criticism; no controlled Codex result[^9] |
| **UI/UX Pro Max 2.13.0** | Community portable Agent Skill plus installer/search scripts | Manifest lists Codex; searchable local datasets (**V**) | Palettes, type pairings, UX rules, chart guidance, styles, and stack-specific implementation patterns | Large prescriptive taxonomy may override real product context; open regression reports; executable installer/search surface needs review[^10] |
| **Stark (`f0d010c/stark`)** | Community Codex/Claude plugin and skill library | Has a Codex manifest (**V**) | Platform routing, product-flow decision brief, native idioms, design tokens, and required rendered evidence | New/community-maintained; no comparative results found; name can be confused with Stark’s commercial accessibility skills[^11] |
| **Vercel Web Interface Guidelines** | First-party Vercel guidelines plus portable review skill | MIT repo and `npx skills add` path (**V**) | Concrete web interaction, responsive, typography, form, content, and accessibility review checklist | Primarily a review/checklist layer; Vercel-specific copy preferences are not universal[^12] |
| **Stark accessibility skills** | Vendor Agent Skills, portable to Codex | Stark announced five discipline-specific skills for Codex and peers on 2026-09-03 (**V**) | Accessibility guidance separated for design, frontend, mobile, backend, and program work | Instructions are not a rendered accessibility test engine; very new and unmeasured[^13] |

### Canvas, brand, and visual-production tools

These tools add a design workspace, account data, or generated visual artifacts.

| Candidate | Accurate category | Availability and evidence | Material capability | Main limitation |
|---|---|---|---|---|
| **Figma 2.0.21** | First-party Figma Codex plugin: skills plus connector/app | Remote Codex catalog, not installed (**O**); public plugin 2.0.20 (**V**) | Read design context, generate code, write native Figma structures, Code Connect, design-system rules, web/code-to-canvas workflows | **Excluded from scored write/round-trip use:** writing requires a paid Full seat and Code Connect has paid plan/library constraints. Optional Starter read-only context must pass the $0 gate[^14][^37][^38] |
| **Canva 14.0.0** | First-party Canva Codex plugin: skills plus connector/app | Remote Codex catalog, not installed (**O**); public manifest and Canva Codex install docs (**V**) | Brand checks, template autofill, resize, editing, feedback, comments, exports, asset/library search | **Excluded from Q002 scored use:** requested workflows have plan ambiguity or paid constraints, and Canva’s MCP usage policy also restricts model evaluation[^15][^39][^44] |
| **OpenAI Creative Production 0.1.25** | First-party Codex plugin: proprietary skills, app, and MCP board | Remote catalog, not installed (**O**); public manifest (**V**) | Campaign concepts, mood boards, product placements, ads, social variants, reusable styles; can orchestrate ImageGen/Figma/Canva | Native ImageGen stays fixed; Creative Production is eligible only if its remaining plugin/app/MCP path is included in current access, with Figma/Canva disabled[^16] |
| **Adobe 8.0.0** | First-party Adobe connector plugin with Codex skills | Public OpenAI plugin manifest (**V**); the local CLI exposed an opaque 8.0.0 app row rather than a named Adobe row (**O**) | Photo retouching, batch image edits, Express templates, social assets, video reframing, Creative Cloud search, PDFs | **Excluded from Q002:** account tiers and premium features conflict with the zero-incremental-cost constraint[^17][^47] |
| **Google Stitch plugin suite** | Google Labs Code Codex marketplace plugins plus remote MCP/SDK | Public Codex install path; repo disclaims official product support (**V**) | Generate/edit screens from text or images, code-to-design, DESIGN.md import/export, design systems, variants, iterative build loop | Conditional only: run after proving current $0 entitlement and quota; quota exhaustion is a failed arm, never a purchase trigger[^18] |
| **Penpot MCP** | Official open-source design platform MCP; not a Codex plugin by itself | MCP integrated into the main Penpot repo; former repo archived 2026-02-03 (**V**) | Query, transform, and create Penpot design content via the Plugin API; self-hostable canvas and open formats | Primary free C6 path; require >=2.15.0, loopback or isolated networking, and existing no-incremental-cost hosting[^19][^41][^48] |
| **Builder Code/Fusion MCP** | Vendor remote MCP and adjacent hosted visual IDE | Streamable HTTP MCP, OAuth, Builder org scope (**V**) | Start/continue design-grounded code agent runs, branches, previews, message history, design systems, and repo-linked visual iteration | **Excluded from Q002:** paid credits/upgrades and a second hosted workspace violate the selected cost boundary[^20][^49] |
| **Anima MCP** | Vendor remote MCP and adjacent code-generation service | Public remote endpoint and docs (**V**) | Figma-to-code for React/HTML and UI libraries, website/prompt/codebase playgrounds, Git-backed playground iteration | **Excluded from Q002:** metered free usage and paid/Enterprise capabilities cannot support an upgrade-free adoption plan[^21][^50] |
| **Webflow MCP 2.0** | First-party remote MCP for a hosted visual site builder | Public docs explicitly list Codex; v2.0 released 2026-07-21 (**V**) | Create/edit elements, styles, components, variables, breakpoints, branches, assets, custom code, CMS, and analytics | **Excluded from Q002:** useful production features span paid site/workspace plans; no paid publishing target is in scope[^22][^51] |
| **21st Codex plugin / MCP** | Vendor self-hosted Codex marketplace plugin plus remote MCP | Public Codex plugin repo and remote endpoint (**V**) | Search/get/install/publish curated components and themes; generate component variants; design-token sync | **Excluded from Q002:** metered copies and paid AI tiers are incompatible with the adoption constraint[^23][^53] |
| **Framelink Figma Context MCP** | Community local Figma MCP; not the official Figma plugin | Public package/repository (**V**) | Read-focused Figma context and image export for clients without the official connector | Redundant now that Figma has a first-party server; versions <=0.6.2 had command-injection RCE, fixed in 0.6.3[^54] |
| **v0** | Adjacent Vercel hosted design/code service and API; not a Codex design plugin | Public SDK/API and Vercel plugin skill guidance (**V**) | Image input, web UI generation, preview, GitHub sync, visual Design Mode with edits committed to source | **Excluded from Q002:** credit-backed use and paid tiers cannot enter the scored or adoption plan[^24][^52] |
| **screenshot-to-code** | Community self-hosted application; not a plugin | MIT repo with active model support (**V**) | Screenshot, mockup, Figma, text, and experimental video to HTML/CSS/React/Vue/Ionic/SVG; parallel model variants | BYOK keys and screenshots are sent to selected model providers; QA checklist is not an external quality result[^25] |
| **Higgsfield** | Vendor connector/app with Codex skill/MCP bundle in public repo | Remote catalog app 1.5.0; public plugin 1.2.1 (**O/V**) | Image/video generation, photo restyling, still animation, product ads, narrated explainers | **Excluded from Q002:** hosted commercial generation and enterprise-only no-train terms do not fit the selected boundary[^26][^56] |
| **Runway** | Vendor app/connector in the Codex remote catalog | Recommended but uninstalled on this host (**O**) | Specialist generative image/video production | **Excluded from Q002:** commercial hosted generation is outside the free-only plan |
| **HyperFrames 0.1.2 / Remotion 1.0.7** | Code-native Codex video plugin bundles | Public manifests; remote catalog uninstalled (**O/V**) | HTML/React-based motion graphics, website-to-video, programmable brand motion | Excluded from Q002 when Remotion’s commercial licensing would be triggered; motion/video is outside the first canary[^27] |

### Component-context and verification tools

| Candidate | Accurate category | Availability and evidence | Material capability | Main limitation |
|---|---|---|---|---|
| **Storybook MCP (`@storybook/addon-mcp`)** | Official local MCP addon; preview | Storybook 10.6 docs (**V**) | Gives agents component APIs, examples, stories, previews, interaction tests, and accessibility checks; supports repair/retest loops | Component manifest coverage varies by framework; API is explicitly preview; requires a maintained Storybook[^28] |
| **shadcn MCP** | Official local MCP over component registries | Docs include manual Codex config (**V**) | Browse, inspect, and install public/private registry components and blocks; supports auth headers | Installing registry code mutates the repo and imports supply-chain/licensing risk; `@latest` is unpinned in examples[^29] |
| **Playwright MCP** | Official Microsoft local browser MCP | Public repo/package (**V**) | Accessibility snapshots, screenshots, interaction, device emulation, console/network inspection, isolated profiles | Browser access is not a security boundary; snapshots contain untrusted page text; screenshots and automated semantics do not equal UX judgment[^30] |
| **Chrome DevTools MCP** | Official Chrome DevTools local MCP | Public repo/package (**V**) | Live Chrome control, DOM/screenshot inspection, console/network debugging, performance traces | Exposes browser contents and mutation to the MCP client; usage statistics default on unless disabled[^31] |
| **axe-core / `@axe-core/playwright`** | Open-source deterministic test library | Deque-maintained, free (**V/M-vendor**) | WCAG 2.0–2.2 rules in normal browser tests; machine-readable violations | Deque estimates it finds 57% of WCAG issues on average; manual testing remains necessary[^32] |
| **Deque axe MCP / plugin** | Vendor MCP plus Claude plugin skills, adaptable to Codex | Public plugin repo and Docker image (**V**) | Analyze → remediate → verify loop with expert guidance and Advanced Rules | **Excluded from Q002:** requires the contact-sales Web Bundle and consumes AI credits[^33] |
| **Pa11y** | Open-source CLI/test library | Public repo, Node 20/22/24 for v9 (**V**) | URL-based WCAG checks, axe or HTML_CodeSniffer runners, actions, screenshots, CI exit codes | Deterministic supplement, not design critique; needs explicit state/action coverage[^34] |
| **Chromatic** | Adjacent hosted visual regression/review service | Public pricing and Storybook integration (**V**) | Cross-browser visual snapshots, interaction/a11y tests, UI review, hosted Storybook | **Excluded from Q002:** paid usage beyond an allowance and upgrade pressure conflict with the adoption boundary[^35] |
| **OpenAI Plugin Eval 0.1.2** | First-party Codex plugin static analyzer and benchmark harness | Remote catalog, available but not installed (**O**); public README (**V**) | Deterministic manifest/skill checks, budget explanation, isolated `codex exec` benchmark scaffolding, artifact retention, usage telemetry | It supplies infrastructure and telemetry; it is not a validated visual-quality judge or scientific evaluation contract[^55] |

## Free-only shortlist comparison

Scores are **pre-canary fit judgments**, not measured product scores: 1 is weak, 3 is useful with gaps, and 5 is unusually strong for the criterion. Eligibility is determined before scoring and is not itself a quality score.

| Candidate | Native Codex fit | Visual generation | Brand/design-system grounding | UX critique | Screenshot/design-to-code | Responsive/a11y proof | Round trip | Setup burden | Free-only disposition |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Plain Codex | 5 | 3 | 3 | 3 | 4 | 4 | 1 | 1 | Control A |
| Product Design, current included capabilities only | 5 | 4 | 3 | 5 | 5 | 4 | 2 | 1 | Control B after entitlement receipt; no Sites or paid connectors |
| Taste Skill | 4 | 3 | 2 | 2 | 2 | 3 | 1 | 1 | Free instruction-skill arm |
| UI/UX Pro Max basic/local | 4 | 3 | 4 | 4 | 2 | 4 | 1 | 2 | Free instruction-skill arm; pin and inspect scripts |
| Stark | 5 | 3 | 4 | 4 | 2 | 4 | 1 | 2 | Free narrower reserve |
| Penpot MCP >=2.15.0 | 3 | 3 | 4 | 2 | 3 | 2 | 5 | 5 | Free editable-canvas and C6 arm |
| Stitch plugins | 5 | 5 | 5 | 3 | 4 | 3 | 4 | 3 | Conditional $0 arm only after entitlement/quota proof |
| Figma Starter read-only | 4 | 1 | 4 | 1 | 3 | 1 | 1 | 2 | Optional unscored context check; no writes or Code Connect |
| Native Codex ImageGen (`gpt-image-2`) | 5 | 5 | 3 | 1 | 1 | 1 | 1 | 1 | Fixed included capability in all applicable arms; normal Codex limits apply |
| Creative Production | 5 | 5 | 4 | 3 | 1 | 1 | 2 | 1 | Conditional only if its non-ImageGen tool path is already included |
| Storybook + shadcn + Playwright + axe-core/Pa11y | 4 | 1 | 5 | 2 | 2 | 5 | 2 | 3 | Free local QA augmentation |

All other landscape entries are historical context or excluded alternatives. Penpot carries the editable-canvas comparison and C6. Figma Starter can inform a read-only context check but cannot compete for write, Code Connect, or round-trip scores.

## Candidate evidence and practical interpretation

### OpenAI-native workflows

Product Design is the most complete in-host workflow. Its public README explicitly covers image-based ideation, screenshot and URL implementation, screenshot-backed UX/accessibility audits, browser annotation, visual comparison, and sharing.[^1] The installed 0.1.54 manifest adds no app or MCP registration of its own; it coordinates host capabilities. In Q002, Control B may use local repository work, the currently included browser workflow, and native ImageGen wherever the matched task calls for images. Sites publishing and Figma/Canva or any other paid connector path are prohibited.

Build Web Apps overlaps substantially, but its goal is a broader frontend application build. The published skill mandates a generated visual concept, extracts a design system, implements the accepted image, and visually compares the browser render.[^7] It is a candidate when the task is “ship the app,” while Product Design is clearer when the main goal is design exploration, audit, cloning, or a reviewable prototype.

Creative Production supplies a persistent review board and focuses on marketing visuals. Its public manifest includes skills, an app, and an MCP server, unlike Product Design’s skill-only bundle.[^16] Native ImageGen is already approved and fixed; Creative Production itself is eligible only when the current Codex plan includes its remaining plugin, app, and MCP path with no metered charge or upgrade. Otherwise it is excluded rather than replaced with Adobe or Canva.

The built-in ImageGen skill is a native capability, not a separate marketplace plugin. The owner’s decision and current native availability establish eligibility without a separate zero-cost receipt. OpenAI documents that it uses `gpt-image-2`, counts against normal Codex usage limits, and uses those limits 3–5 times faster on average than similar non-image turns, depending on quality and size.[^36] Keep ImageGen fixed across every applicable matched arm. If normal included limits are exhausted, stop or defer the affected matched run. Never set `OPENAI_API_KEY`, call the paid Image API, or buy capacity to continue.

### Figma, Canva, Stitch, and Penpot

Figma has a strong semantic handoff story, but its write path and Code Connect do not fit the owner’s zero-incremental-cost decision. Its official MCP returns layout, variables, components, and screenshots, while write-to-canvas can create or update native structures.[^14] Q002 may use only Figma Starter read tools when a retained entitlement receipt proves the full read task is available for $0. It receives no write, Code Connect, or C6 score.

The write-to-canvas path is still beta. Figma documents a 20 KB response limit, no image-asset import, no custom fonts, and manual component publication before Code Connect completes.[^14] The canary must score cleanup work and unsupported assets instead of treating a successful tool call as a finished design.

The cost and access boundaries are decisive. Starter read calls are quota-limited; writing through agents requires a Full seat; and Code Connect templates have paid-plan constraints.[^37][^38] Any Starter quota exhaustion is a failed optional check. The operator must not start a trial, add a seat, or upgrade a plan to continue.

Canva remains useful historical context, but it is excluded from Q002. Its most relevant brand workflows have plan/eligibility ambiguity, and its published MCP policy restricts use of Canva-sourced materials in external model evaluation.[^39][^44] The free-only plan therefore uses synthetic `DESIGN.md` rules, token files, reusable HTML/CSS/SVG templates, and local exports.

Stitch is a conditional challenger. Google Labs Code publishes three marketplace plugins—design, build, and utilities—with explicit Codex installation. The pack includes text/image generation, code-to-design, design systems, DESIGN.md exchange, variants, and a page-by-page iteration loop.[^18] These are vendor claims, and no controlled Stitch-with-Codex study was found. Before each run, the operator must prove the current account has a $0 entitlement and enough remaining quota for the complete task. An unknown entitlement, exhausted quota, trial prompt, billing prompt, or upgrade request makes the arm ineligible or failed without purchase.

Penpot is the required free editable-canvas path. It is MPL-2.0, can be self-hosted, uses SVG/CSS/HTML/JSON, and offers native design tokens.[^41] Its official MCP can query, transform, and create design objects, providing the editable round trip needed for C6. Use the free cloud tier or infrastructure already available at no incremental cost; do not procure hosting for the trial.[^48] The standalone MCP repository was archived when its code moved into Penpot, and versions before 2.15.0 had a high-severity unauthenticated code-execution vulnerability.[^19] Pin version 2.15.0 or later and bind it to loopback or an isolated network.

### Community instruction skills

Taste Skill is a compact, forceful attempt to diversify model output. Its v2 changelog explicitly marks the current default experimental and uses three control dials for design variance, motion intensity, and density.[^9] That makes it easy to form a fixed arm, but its large set of bans can improve novelty while harming domain fit. An open issue also documents naming mismatches between installation keys and skill frontmatter. Pinning a commit and invoking the exact `design-taste-frontend` skill avoids drift.

UI/UX Pro Max offers much more reference data: its 2026-09-06 manifest claims 79 styles, 192 palettes, 74 font pairings, 119 UX guidelines, 25 chart types, and 22 stacks, with Codex as a supported platform.[^10] It is a plausible brand/system assistant, but it must be treated as executable third-party code. A critical Tailwind config injection affected version 2.5.0 and earlier, and a later audit reported unverified release downloads and `@latest` dependency execution; recent issues also report install defects and visual regression.[^42] Use 2.13.0 or a pinned later reviewed commit, install into an isolated canary workspace, and do not accept its internal style counts or generated “design system” as evidence of quality.

Stark is a smaller alternative organized around product behavior and platform idiom. It requires a decision brief before code, then rendered evidence and a repair pass.[^11] Its progressive reference loading is attractive for token control. It lacks comparative results and should enter only if the first two community arms are close or both fail.

Anthropic’s `frontend-design` remains a useful reference arm because it is first-party and portable under the Agent Skills structure. Anthropic’s article shows paired examples using the same prompts, but supplies no blinded human study or quantitative result.[^8] A community benchmark reported an 18/18 versus 5/18 rule-check result across three tasks, but its six assertions mostly encode the skill’s own rules, such as avoiding common fonts and purple gradients; this measures compliance with the prompt, not general UX or brand quality.[^43] UI Bench’s mixed effect is stronger evidence that the result depends on model, brief, and evaluator.[^3] It belongs in an optional reference run, not the primary Codex shortlist.

### Component and browser grounding

Storybook MCP and shadcn MCP reduce hallucinated component APIs. Storybook can expose documented components and stories, preview agent-generated stories, and run interaction and accessibility tests.[^28] Shadcn can search and install items from public, third-party, or private registries and supports explicit Codex configuration.[^29] Together they answer two different questions: “What does our design system actually support?” and “What reusable implementation can we inspect before adding?”

Playwright MCP provides the runtime proof: named accessibility-tree elements for reliable interaction, screenshots, device emulation, console messages, network inspection, and isolated browser profiles.[^30] It should run with a fresh isolated profile and an output directory under the retained evidence bundle. Its origin allow/block lists are convenience controls rather than a security boundary, and web page text must be treated as untrusted input. Chrome DevTools MCP is better when performance traces and deep network/console diagnosis matter, but it exposes all browser content to the client and enables anonymous usage statistics by default.[^31] Playwright is the safer default for the fixed UI canary; use Chrome DevTools only for a separately authorized diagnostic.

Automated accessibility must be scored separately from human accessibility review. Axe-core’s maintainer says it finds about 57% of WCAG issues on average, leaving incomplete/manual cases.[^32] The free stack combines axe-core and/or Pa11y with keyboard and zoom tests. Deque’s MCP is excluded because access requires the sales-priced Axe DevTools for Web Bundle.[^33]

## Setup, security, and data-access review

| Tool/lane | Setup and credentials | Data and write scope | Required control before evaluation |
|---|---|---|---|
| Plain Codex / Product Design / Taste / Stark | Local skills/plugin; community packs may include scripts | Repository files and commands allowed by the Codex session | Pin package/commit; inspect `SKILL.md`, scripts, hooks, and manifest; Product Design uses no Sites or paid connector; retain eligibility receipt |
| UI/UX Pro Max basic/local | Copied skill or pinned installer; local search scripts | Writes skill files and generated project files; historic installer/generator defects | Pin >=2.13.0 reviewed commit; verify checksum; prohibit arbitrary plugin names and `@latest`; enable no paid add-on |
| Penpot MCP | Local MCP + Penpot plugin; free cloud or already-funded self-host | Can create and transform editable design objects | Require >=2.15.0; loopback/firewall or isolated host; synthetic file; no paid hosting or upgrade |
| Stitch, conditional | Existing $0 account entitlement; remote MCP/plugin | Sends synthetic prompts, images, code, and design files to Stitch | Same-day $0/quota receipt before each run; pin plugin; stop on quota, trial, billing, or upgrade prompt |
| Figma Starter, optional read-only | Starter account + OAuth | Read-only context from a synthetic file | Same-day $0/quota receipt; prohibit writes, Full/Dev seats, Code Connect, and C6 scoring; stop on quota |
| Native Codex ImageGen | Current native Codex access; no separate receipt beyond the recorded owner decision and availability check | Generated synthetic images/assets in every applicable arm | Fix `gpt-image-2` use across matched arms; never set `OPENAI_API_KEY` or use the paid Image API; stop/defer on normal included-limit exhaustion |
| Creative Production, conditional | Existing Codex entitlement only | Optional review board and orchestration around the fixed ImageGen capability | Prove its non-ImageGen path is included; stop on paywall or upgrade prompt without purchase |
| Storybook / shadcn | Local addon/CLI and allowlisted free registries | Component manifests, stories, tests, and inspected registry code | Bind locally; pin versions; inspect code/license before install; capture dependency diff |
| Playwright / axe-core / Pa11y | Local packages and isolated browser | Local rendered DOM, screenshots, interactions, accessibility results | Synthetic fixtures, fresh profile, localhost, pinned versions, retained machine-readable output |

The excluded set is Canva, Adobe, paid Figma writes and Code Connect, Builder, Anima, paid Webflow features, v0, paid 21st use, paid Chromatic use, Deque MCP, Higgsfield, Runway, and any Remotion use that triggers commercial licensing. Their historical evidence remains in the landscape to explain the boundary; none may appear in an arm, advancement decision, or recommended production stack.

## Published pricing snapshot

Prices are public US list prices observed on 2026-09-09, excluding tax and promotions unless stated. This table is historical exclusion evidence, not a shopping list. “$0” is insufficient by itself: the complete canary task and plausible adoption workflow must remain available with no purchase, converting trial, paid seat, add-on, or forced upgrade.

| Product | Published price relevant to this evaluation | Important limit or ambiguity |
|---|---|---|
| Product Design / Build Web Apps / Creative Production | No standalone plugin price found | Eligible only for capabilities already included in current access; no Sites publishing; gate Creative Production’s non-ImageGen path and connected capabilities independently |
| Native Codex ImageGen / paid Image API | Native `gpt-image-2` generation counts against included general Codex usage limits | Fixed in applicable arms with no separate receipt; prohibit `OPENAI_API_KEY` and paid API fallback; included-limit exhaustion stops or defers the run[^36] |
| Figma | Starter $0; paid Full/Dev/Organization/Enterprise tiers | Optional Starter read-only context only; paid writes and Code Connect are excluded[^37][^38] |
| Canva | Free $0; Pro $180/year individual; Business $250/year/person; Enterprise contact sales | Codex AI Connector eligibility and general MCP plan table conflict; Brand/autofill capabilities vary[^46] |
| Adobe | Connector allows a guest start; Creative Cloud Pro individual regular $69.99/mo annual billed monthly; teams $99.99/license/mo; Firefly Pro $19.99/mo | Promotional prices vary; plugin feature entitlements were not mapped publicly to every plan[^47] |
| Stitch | No separate Stitch/MCP price verified; Google describes Stitch as experimental and globally available | Conditional only after a current $0 entitlement/quota receipt; unknown or exhausted quota stops the arm |
| Penpot Cloud | Professional $0; paid cloud and Private Server tiers also exist | Use Professional $0 or existing self-host infrastructure only; no trial-specific hosting purchase[^48] |
| Builder Code | Free $0 with 60 monthly agent credits; Pro $24/user/mo with 500; Team $40/user/mo with 500; Enterprise custom; extra 500 credits $25 | AI training on Free; opt-out on paid; Privacy Mode Enterprise only[^49] |
| Anima | Free includes 5 daily chat messages, 5 design imports/clones, and 5 Figma-plugin generations; Enterprise starts at $500/mo annual | Public parser did not expose all middle-tier prices; one generation includes MCP codegen[^50] |
| Webflow | Starter site $0; Basic $15/mo annual; Premium $25/mo annual; Workspace Full seat $39/mo annual; Team $2,500/mo annual contract | Site and Workspace plans are separate; MCP included even on Starter site but actions depend on workspace/site permissions[^51] |
| v0 | Free $0 with $5 credits; Plus $30/user/mo; Business $100/user/mo; Enterprise custom | API/model usage draws credits; Premium $20 legacy plan is closing to new users[^52] |
| 21st | Two free component copies/day; Builder $8/mo quarterly or $6/mo annual; Builder+AI starts $20/mo quarterly or $15/mo annual | Code retrieval/generation is metered; component licenses vary by item[^53] |
| Storybook, shadcn, Playwright, axe-core, Pa11y | Open-source/free software | Use local pinned packages and allowlisted free registries; internal labor/compute are recorded operational metrics |
| Chromatic | Free: 5,000 billed snapshots/month; public page shows higher tiers but current parser did not expose dollar amounts | Do not budget a paid tier without a checkout quote[^35] |
| Deque axe MCP | Included in Axe DevTools for Web Bundle; contact sales | No public dollar price; remediation uses AI credits[^33] |
| Taste, UI/UX Pro Max, Stark, Anthropic skills | Open-source/free to install | Review, pinning, model tokens, and supply-chain controls remain internal costs |

## Recommended staged stack

### Stage 0: preserve the current baseline

Run the zero-cost eligibility gate before creating any arm. **Control A** is plain Codex with candidate design plugins and skills disabled. **Control B** is Product Design 0.1.54 using only capabilities already included in current access: local repository operations, the included browser workflow, and native ImageGen. ImageGen is fixed identically in Controls A and B and every other applicable matched arm; it requires no separate zero-cost receipt beyond the recorded owner decision and current native availability. Sites publishing and paid connectors remain disabled. Browser automation and deterministic tests are common evaluation infrastructure and receive no design-quality credit.

For every candidate other than native ImageGen, retain a `zero-cost-receipt.json` containing the product and capability, account plan, price shown, trial state, renewal/conversion state, remaining quota, payment method requirement, checked URL or UI/API evidence, UTC timestamp, checker, and evidence hash. `eligible` is true only when the complete run is available for $0 with no purchase, paid seat, subscription, add-on, commercial-license trigger, or converting trial. For ImageGen, record the owner decision, current native availability, `gpt-image-2`, and included-limit consumption. Run every eligible stochastic arm three times. Exhaustion of an external candidate’s free quota, a paywall, or an upgrade prompt is a failed arm and stops it without purchase or rerun. Exhaustion of normal Codex limits stops or defers the affected matched ImageGen runs; do not set `OPENAI_API_KEY` or switch to the paid API.

### Stage 1: small lane-specific canaries

Run three isolated comparisons:

1. **Code-native direction:** Control A, Control B, plain Codex plus pinned Taste Skill, and plain Codex plus pinned UI/UX Pro Max. Each arm has the same fixed built-in capabilities and test harness; the design instruction layer is the only intended difference. If one community skill wins, a later factorial arm may test Product Design plus that skill. If budget permits, add Stark before unblinding.
2. **Editable canvas:** Penpot >=2.15.0 versus the winning no-canvas code-native workflow on the same synthetic product, design system, and screen set. Penpot alone performs and is scored on C6. Stitch may join as a conditional exploratory canvas arm only after passing the same-day $0 gate. Figma Starter may be logged as an optional unscored read-only context check; it cannot write, use Code Connect, or receive C6 credit.
3. **Free brand and asset production:** plain Codex using the synthetic brand spec, repository-native HTML/CSS/SVG workflow, and native ImageGen is the control. Product Design uses the same materials and the same fixed ImageGen capability. Creative Production may join only if its non-ImageGen path passes the entitlement gate. Adobe, Canva, and every paid external image service do not run.

The lead should randomize opaque arm IDs and the independent verifier should grade without knowing the tool. A separate operations reviewer can grade setup/security because blinding is impossible there.

### Stage 2: add grounding and QA to finalists

Take the best code-native workflow and add local Storybook, shadcn restricted to allowlisted free registries, Playwright, and axe-core/Pa11y. Compare finalist alone versus finalist+QA on screenshot-to-code and responsive/accessibility tasks. No hosted visual-regression or paid accessibility service enters this stage.

### Stage 3: production adoption

Adopt the smallest stack that clears the owner-approved thresholds:

- plain Codex as the always-available control;
- Product Design as workflow router only through already-included capabilities;
- one free instruction skill only if it shows a repeatable gain;
- Penpot >=2.15.0 for editable design/code round trips;
- Stitch only while a current $0 entitlement remains verified;
- repository-native HTML/CSS/SVG, synthetic brand specs, and native ImageGen as the fixed asset-production stack;
- Creative Production only while its non-ImageGen path remains included;
- local Storybook, shadcn, Playwright, axe-core, and Pa11y for verification.

Avoid installing multiple broad design-direction skills globally. Conflicting rules increase context, make causal attribution impossible, and can cause the model to satisfy style prohibitions rather than the product brief.

## Fixed canary suite

The following corpus is fixed for the first evaluation. Store all fixtures under a retained, checksum-addressed evidence directory before execution. The fixture package must contain every prompt, synthetic brand/design asset, screenshot, seed defect, expected interaction, viewport, allowed package list, scoring sheet, and blind arm map. The six task prompts must not name a candidate.

### Evidence destination and retention

The canonical destination is `evaluation/design-plugin-canary-v1/` in this repository. Create a successor Engineering Board evaluation entry before execution; its accountable lead is the retention owner. Until that person is named on the entry, the trial cannot start. Use this structure:

```text
evaluation/design-plugin-canary-v1/
  protocol.md
  manifest.json
  native-imagegen-availability.json
  zero-cost-receipts/<opaque-arm-id>.json
  SHA256SUMS
  fixtures/<task>/
  arms/<opaque-arm-id>/manifest.json
  runs/<opaque-arm-id>/<task>/<replicate>/
  scores/<reviewer-id>/
  report.md
```

`manifest.json` must record the protocol version, base commit, candidate source and exact version/commit, retained package hash, Codex/model/reasoning configuration, environment, permissions, task and replicate IDs, start/end times, input and output hashes, the candidate’s zero-cost receipt hash when applicable, the native ImageGen owner-decision/availability hash, observed quota, tool receipts, scorer versions, and completion/failure state. `native-imagegen-availability.json` records the owner decision, current native availability, `gpt-image-2`, normal included-limit treatment, and the prohibition on `OPENAI_API_KEY` or paid API fallback; it is not a separate eligibility receipt. Keep the sanitized protocol, fixtures, eligibility receipts, manifests, outputs that determine scores, screenshots, reviewer sheets, and final report in version control for at least 12 months after the adoption decision. Removal before that date requires a recorded product-owner decision. Credentials, session cookies, payment details, customer data, and unsanitized browser profiles are never retained.

Generate and verify the inventory from the repository root after every accepted evidence update:

```sh
find evaluation/design-plugin-canary-v1 -type f ! -name SHA256SUMS -print \
  | LC_ALL=C sort \
  | while IFS= read -r file; do shasum -a 256 "$file"; done \
  > evaluation/design-plugin-canary-v1/SHA256SUMS
shasum -a 256 -c evaluation/design-plugin-canary-v1/SHA256SUMS
```

Before scoring, a verifier must retrieve the evidence from a fresh clone at the recorded commit, run the checksum verification, open at least one render and one machine-readable result from every arm/task, and record that retrieval in `report.md`. If an artifact cannot be retained in the repository, its durable object-store URI, retention expiry, owner, size, and SHA-256 must appear in `manifest.json`, and the verifier must fetch and hash it before the run is eligible.

### Lane mapping and matched baselines

Do not compute one leaderboard across tools that perform different jobs. Score only the applicable tasks in each lane, normalize within that lane, and report non-applicable dimensions as `N/A`, never zero.

| Lane | Arms and matched baseline | Scored canaries | Proposed advancement gates |
|---|---|---|---|
| Workflow / code-native direction | Control A is the causal baseline; Control B shows the current installed workflow; Taste, UI/UX Pro Max, and optional Stark each replace the design-instruction layer | C1, C2, C3, C4, C5; 90 raw points | No global hard-gate failure; C4 at least 70%; normalized lane score at least 75; at least 5 points over Control A or a capability win it cannot perform |
| Editable canvas | Patched isolated Penpot is the scored editable-canvas arm; the winning code-native workflow is the no-canvas reference for C4; eligible Stitch is optional and conditional | C1, C2, C4, C6; 85 raw points | Valid $0 receipt; no global hard-gate failure; Penpot C6 at least 70%; C4 at least 70%; normalized lane score at least 75 |
| Free brand/asset production | Plain Codex with synthetic brand specs, repository-native HTML/CSS/SVG, and fixed native ImageGen is the baseline; Product Design is the included-capability comparison; Creative Production joins only if its non-ImageGen path is eligible | C1 and C2; 35 raw points | Recorded owner decision/current ImageGen availability plus valid $0 receipt for any additional candidate; no global hard-gate failure; C2 at least 80%; normalized lane score at least 75 |
| QA augmentation | Winning code-native workflow without augmentation is the baseline; compare with local Storybook/shadcn/Playwright/axe-core/Pa11y under the same prompt and budget | C4 and C5; 40 raw points | Valid $0 receipt; no global hard-gate failure; no deterministic regression; normalized lane score improves by at least 5 points or closes a prespecified critical gap |

Thresholds remain proposed owner decisions. Cross-lane totals are prohibited because they would reward or punish missing capabilities instead of measuring the intended role.

### Shared controls

- **Base:** one pinned repository commit with React, TypeScript, Vite, an allowlisted package lock, a small existing component library, Storybook fixtures, and deterministic synthetic data.
- **Model:** one pinned Codex model snapshot and reasoning effort for all Codex arms. External services record their model but do not enter the same causal claim.
- **Runs:** three fresh runs per arm/task with isolated worktrees, browser profiles, design files, and service projects. No carryover memory.
- **Eligibility:** a hashed `zero-cost-receipt.json` exists before each candidate arm starts and proves no purchase, paid seat, subscription, add-on, converting trial, hosting charge, commercial-license trigger, or required upgrade. Native ImageGen is exempt from this receipt because the owner has approved its current included access; retain that decision and an availability check instead.
- **Image capability:** native ImageGen using `gpt-image-2` is fixed in all applicable matched arms. Do not set `OPENAI_API_KEY`, call the paid Image API, or substitute an external paid image service.[^36]
- **Budget:** fixed wall-clock, tool-call, token, and $0 quota ceilings. External-candidate quota failure is scored and stops that arm. Normal Codex included-limit exhaustion stops or defers affected matched ImageGen runs. Neither case permits buying capacity. Only an unrelated, prespecified local infrastructure failure may be retried.
- **Evidence:** prompts, event logs, stdout/stderr, zero-cost and tool receipts, screenshots at all viewports, accessibility output, code diff, dependency diff, editable-canvas export/link receipt, and reviewer sheets.
- **Review:** opaque arm labels; two independent visual/UX reviewers plus automated checks. The operations/security reviewer is unblinded and scores only setup, permissions, policy, reliability, time, and cost. Resolve material disagreement by review against the fixture and rubric, not by averaging incompatible interpretations.
- **Contamination:** synthetic names, logos, product copy, images, and design files created for the trial. No customer data, proprietary production library, or unlicensed community component.

### Scoring and aggregation

Score every replicate independently. A task failure, timeout, external-candidate quota exhaustion, or missing reviewable artifact receives zero for that replicate and remains in the aggregate; only a prespecified unrelated local infrastructure failure may be retried. Normal Codex included-limit exhaustion pauses or defers the complete affected matched set so ImageGen availability does not selectively penalize one arm. The task score for an arm is the median of its three replicate scores. Sum the applicable median task scores and normalize by that lane’s raw-point denominator. Report the three raw scores, median, failure count, elapsed time, token/tool usage, and included/free-quota consumption; do not report only the median. One failed replicate prevents advancement, even when the numeric median passes.

Two blinded reviewers independently score every human-judged item using anchored examples frozen in `protocol.md`. They also make a pairwise preference judgment against the matched baseline for C1, C2, and the visual portion of C4. If their per-item scores differ by more than two points on a ten-point equivalent scale, or their pairwise preferences conflict, a third blinded reviewer adjudicates from the retained artifact and rubric. The adjudicated score replaces that item; incompatible judgments are not averaged. An AI judge may be recorded as exploratory data but cannot replace the human visual/UX reviewers.

| Canary | Automated or fixture-grounded scorer | Blinded human scorer | Operations scorer |
|---|---|---|---|
| C1 visual generation | Exact copy, dimensions, asset integrity, file/editability receipt, and three-output completeness | Hierarchy/craft, brief resonance, coherent distinctness, pairwise preference | Generation failures, time, tokens, free quota |
| C2 brand adherence | Token/color/font/logo-clear-space rules, required legal copy, prohibited-pattern checks, output sizes | Voice, photo treatment, cross-format coherence, accessible adaptation, pairwise preference | Account/plan constraints and export reliability |
| C3 UX audit | Seeded-issue recall and false-positive count against the sealed issue ledger; evidence-link completeness | Harm prioritization, actionability, confidence calibration, correct handling of intentional non-issues | Browse/tool failures and elapsed effort |
| C4 screenshot-to-code | Frozen-browser renders, exact text/element recall, Playwright interactions/states, component/token-use checks, dependency and asset inventory | Layout/detail fidelity and pairwise preference. Pixel/perceptual differences remain separate diagnostics, not the sole grade. | Build reliability, time, tokens, tool calls |
| C5 responsive/accessibility repair | Playwright viewport/keyboard/zoom/reduced-motion checks, axe/Pa11y output, regression tests, screenshot inventory | Brand preservation and usability of repaired states | Test/setup failures and elapsed effort |
| C6 round-trip editing | Penpot canvas structure/export receipt, component linkage, semantic-token check, bounded code diff, unrelated snapshot, final browser checks | Editability, design coherence, and whether the approved canvas change is faithfully reflected | OAuth/tool failures, mutation audit, time and free quota |

### C1 — visual generation

**Prompt:** Create three distinct launch directions for a fictional cooperative travel app from a 250-word brief and four synthetic product images, then select and refine one direction into a desktop landing-page concept and 1:1 campaign tile.

**Required output:** three visibly distinct concepts; selection rationale tied to audience and brief; refined editable or code-native source; 1440×1000 and 1080×1080 renders; exact supplied headline and CTA.

**Seeded traps:** a tempting generic purple-gradient example in the mood references; one product image with transparent edges; exact copy containing punctuation and a price.

**Proposed 15 points:** brief/semantic fidelity 4; visual hierarchy and craft 4; distinctness without arbitrary novelty 3; image/text integrity 2; editability and evidence completeness 2.

### C2 — brand adherence

**Prompt:** Extend the selected direction into a pricing page, email header, and three social sizes using the supplied synthetic `DESIGN.md`, repository token files, logo clear-space rules, type scale, six semantic color tokens, photo treatment, voice rules, and prohibited patterns.

**Required output:** all formats; token/component mapping; no logo redraw; exact legal line; reusable source rather than flattened UI text.

**Seeded traps:** visually plausible off-brand teal; an obsolete logo in the repository; one contrast-invalid permitted brand pairing; conflicting decorative example that the written brand rule overrides.

**Proposed 20 points:** brand-rule compliance 8; cross-format consistency 4; correct source precedence 3; accessible brand adaptation 3; editability 2.

### C3 — UX audit

**Prompt:** Audit a five-step account-recovery flow in a running local fixture, prioritize findings, and propose bounded fixes with evidence.

**Ground truth:** twelve seeded issues across discoverability, misleading status, destructive-action recovery, error copy, keyboard order, focus visibility, screen-reader names, touch target, mobile overflow, contrast, loading feedback, and a dead end. Three visually unusual choices are intentional non-issues.

**Required output:** current-run screenshots for each step, finding-to-step links, severity/confidence, screenshot-observable versus interaction/test evidence, and acknowledgement of what cannot be proved.

**Proposed 15 points:** seeded-issue recall 5; precision/non-issue avoidance 3; prioritization by user harm 2; evidence traceability 3; accessibility limits and actionable fixes 2.

### C4 — screenshot-to-code

**Prompt:** Implement a responsive analytics screen from paired 1440 px and 390 px screenshots plus a short interaction clip. Use the existing component library and preserve the supplied data/state semantics.

**Required output:** repository code, working tabs/filter/drawer, loading/empty/error states, no screenshot-as-UI, and render evidence at both target sizes.

**Seeded traps:** one chart must stay semantic; mobile changes order rather than merely stacking; an existing button component has a non-obvious prop; an asset must be cropped with CSS rather than redrawn.

**Proposed 25 points:** visual similarity 8; interaction/state fidelity 5; component/design-token reuse 4; responsive behavior 4; maintainability and asset correctness 2; evidence completeness 2.

### C5 — responsive and accessibility repair

**Prompt:** Repair a deliberately flawed checkout at 320, 768, 1440, and 1920 px without changing its brand direction or business behavior.

**Ground truth:** horizontal overflow, covered focus, inaccessible modal, lost mobile navigation, invalid labels, low contrast, missing reduced-motion handling, keyboard-inaccessible custom select, layout shift, and 200% zoom clipping.

**Required output:** code diff, Playwright interaction evidence, axe/Pa11y report, keyboard trace, reduced-motion check, zoom check, and screenshots at four viewports.

**Proposed 15 points:** deterministic issue resolution 6; keyboard/focus/modal behavior 3; responsive/zoom behavior 3; brand preservation 1; no new regressions 2. Automated clean output alone cannot earn more than 8/15.

### C6 — round-trip editing

**Prompt:** Using Penpot >=2.15.0 on the free/self-hosted eligible path, move the pricing screen from code to the editable canvas, change plan emphasis and mobile card order in Penpot, then apply the approved edits back to the repository while preserving component semantics and unrelated code. An eligible Stitch arm may run the same prompt separately; Figma Starter is read-only and cannot attempt or score this task.

**Required output:** editable canvas objects/components, before/after canvas renders, bounded source diff, unchanged unrelated snapshot, final browser renders, and an audit trail linking the approved canvas changes to code.

**Seeded traps:** a component instance must remain linked; canvas order and DOM reading order differ on mobile; one requested color change must use a semantic token; a nearby unrequested section must remain byte-identical.

**Proposed 25 points:** native editability/semantic structure 6; canvas-to-code fidelity 6; design-system/component linkage 4; bounded diff/no collateral change 3; responsive/reading order 3; audit trail and reversibility 3.

### Proposed totals and stopping rules

Use the lane denominators above and normalize each lane to 100 after the owner approves weights. Do not publish a cross-lane winner. Select a stack by combining the winner, if any, from each role that the team actually needs. The common hard gates are:

- no critical security/control failure;
- a valid zero-cost eligibility receipt for each candidate capability used, except native ImageGen, whose owner approval and current availability are recorded instead;
- zero incremental monetary cost for every run and for the recommended adoption path;
- no trial conversion, payment-method requirement, paid seat, subscription, add-on, paid hosting, commercial-license trigger, or upgrade;
- immediate arm failure and stop on external-candidate quota exhaustion, paywall, billing prompt, or upgrade prompt, with no purchase or paid retry;
- stop or defer the complete affected matched set on normal Codex/ImageGen included-limit exhaustion; never set `OPENAI_API_KEY`, invoke the paid Image API, or purchase capacity;
- no use of real customer or production design data;
- no unresolved high-severity seeded accessibility issue;
- exact required copy and logos must survive;
- the applicable lane-specific task floors and normalized threshold in the lane table;
- improvement over that lane’s matched baseline of at least 5 normalized points with no incremental monetary cost and no more than 20% median time regression, or a documented capability win the baseline cannot perform;
- no arm may advance if one of its three runs fails to produce a reviewable artifact.

These thresholds and the dimension weights are a **proposal, not an approved evaluation contract**. The owner must decide whether to value craft, brand fidelity, semantic code, round-trip editability, time, and cost in this proportion. After approval, freeze a versioned scoring JSON before any run and prohibit post-result weight changes.

## Limits and unresolved questions

1. No shortlisted tool has a controlled, independently replicated study on the current Codex model and these tasks. Vendor screenshots and testimonials show possibility, not expected improvement.
2. The remote Codex catalog changed ahead of the public plugin repository. Exact evaluated bytes must be retained; a name/version alone is insufficient.
3. Product Design, Creative Production, Figma Starter reads, and Stitch have account- or quota-dependent eligibility. Absence of a complete, current $0 receipt excludes the candidate arm; external quota exhaustion fails it without purchase. Native ImageGen is already approved under current Codex access and needs only the recorded owner decision and availability check.
4. Figma writes and Code Connect, Canva scored use, Adobe, Builder, Anima, paid Webflow features, v0, paid 21st use, paid Chromatic use, Deque MCP, Higgsfield, Runway, and commercially licensed Remotion use are historical exclusions, not future advancement options under Q002.
5. Stitch is fast-moving and experimental. A passing smoke test does not prove that the complete canary or adoption period remains available for $0.
6. Penpot’s security advisory is resolved only by pinning version 2.15.0 or later and verifying network binding. Do not evaluate an unspecified `latest` package.
7. Visual judges can reward novelty while missing product harm. The rubric includes seeded non-issues, task-grounded UX defects, component semantics, and deterministic accessibility checks to counter that bias.
8. Automated accessibility tools cover only part of WCAG. The suite measures keyboard, zoom, responsive behavior, and known semantic issues but cannot claim conformance.
9. Entitlements, quotas, and license terms can change. Capture a dated zero-cost receipt before every candidate arm and re-check it before adoption. For native ImageGen, record current availability and consumption against normal Codex limits; if those limits run out, stop or defer without API fallback or purchase.

## Sources

[^1]: OpenAI. “[Product Design plugin README](https://github.com/openai/role-specific-plugins/blob/main/plugins/product-design/README.md).” Accessed September 9, 2026; OpenAI. “[Product Design audit skill](https://github.com/openai/role-specific-plugins/blob/main/plugins/product-design/skills/audit/SKILL.md).” Accessed September 9, 2026.
[^2]: Jiahao Ying et al. “[OpenSkillEval: Automatically Auditing the Open Skill Ecosystem for LLM Agents](https://arxiv.org/abs/2605.23657).” arXiv:2605.23657, May 2026; [replication repository](https://github.com/ALEX-nlp/OpenSkillEval).
[^3]: UI Bench. “[Design Evaluation](https://ui-bench.dev/ux-judge).” Accessed September 9, 2026. Eighty landing-page designs were judged by Composer 2.5; skill deltas cover Claude, not Codex.
[^4]: OpenAI. “[OpenAI Plugins](https://github.com/openai/plugins).” Accessed September 9, 2026.
[^5]: Agent Skills. “[Specification](https://agentskills.io/specification).” Accessed September 9, 2026.
[^6]: Local observation: `codex --version` returned `codex-cli 0.153.4`; `codex plugin list` on September 9, 2026 returned `figma@openai-curated-remote 2.0.21`, `product-design@openai-curated-remote 0.1.54`, `canva@openai-curated-remote 14.0.0`, `creative-production@openai-curated-remote 0.1.25`, `build-web-apps@openai-curated-remote 0.1.2`, `hyperframes@openai-curated-remote 0.1.2`, and `remotion@openai-curated-remote 1.0.7`. Compare OpenAI’s public [Figma 2.0.20 manifest](https://github.com/openai/plugins/blob/main/plugins/figma/.codex-plugin/plugin.json) and [Product Design 0.1.52 manifest](https://github.com/openai/plugins/blob/main/plugins/product-design/.codex-plugin/plugin.json).
[^7]: OpenAI. “[Build Web Apps manifest](https://github.com/openai/plugins/blob/main/plugins/build-web-apps/.codex-plugin/plugin.json)” and “[Frontend App Builder skill](https://github.com/openai/plugins/blob/main/plugins/build-web-apps/skills/frontend-app-builder/SKILL.md).” Accessed September 9, 2026.
[^8]: Anthropic. “[Improving frontend design through Skills](https://claude.com/blog/improving-frontend-design-through-skills).” November 2025; Anthropic. “[Skills repository](https://github.com/anthropics/skills).” Accessed September 9, 2026.
[^9]: Leonxlnx. “[Taste Skill](https://github.com/leonxlnx/taste-skill)” and “[Changelog](https://github.com/Leonxlnx/taste-skill/blob/main/CHANGELOG.md).” Accessed September 9, 2026.
[^10]: NextLevelBuilder. “[UI/UX Pro Max skill manifest](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/skill.json).” Version 2.13.0, September 6, 2026.
[^11]: f0d010c. “[Stark](https://github.com/f0d010c/stark).” Accessed September 9, 2026.
[^12]: Vercel Labs. “[Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines).” Accessed September 9, 2026.
[^13]: Stark. “[Five accessibility skills for each discipline](https://www.getstark.co/blog/stark-skills/).” September 3, 2026.
[^14]: Figma. “[Figma MCP Server Guide](https://github.com/figma/mcp-server-guide)” and “[Write to canvas](https://developers.figma.com/docs/figma-mcp-server/write-to-canvas/).” Accessed September 9, 2026; OpenAI/Figma. “[Figma Codex plugin manifest](https://github.com/openai/plugins/blob/main/plugins/figma/.codex-plugin/plugin.json).” Version 2.0.20.
[^15]: OpenAI/Canva. “[Canva Codex plugin manifest](https://github.com/openai/plugins/blob/main/plugins/canva/.codex-plugin/plugin.json).” Version 14.0.0; Canva. “[Canva Agent Skills](https://github.com/canva-sdks/canva-skills).” Accessed September 9, 2026.
[^16]: OpenAI. “[Creative Production manifest](https://github.com/openai/plugins/blob/main/plugins/creative-production/.codex-plugin/plugin.json)” and “[README](https://github.com/openai/plugins/blob/main/plugins/creative-production/README.md).” Version 0.1.25.
[^17]: OpenAI/Adobe. “[Adobe Codex plugin manifest](https://github.com/openai/plugins/blob/main/plugins/adobe/.codex-plugin/plugin.json).” Version 8.0.0.
[^18]: Google Labs Code. “[Stitch Design Skills](https://github.com/google-labs-code/stitch-skills)” and “[Stitch SDK](https://github.com/google-labs-code/stitch-sdk).” Accessed September 9, 2026.
[^19]: Penpot. “[Official Penpot MCP](https://github.com/penpot/penpot-mcp).” Archived February 3, 2026 after integration into the main repository; Penpot. “[GHSA-22qr-rp27-j9wm: MCP REPL server unauthenticated RCE](https://github.com/penpot/penpot/security/advisories/GHSA-22qr-rp27-j9wm).” Patched in 2.15.0, May 19, 2026.
[^20]: Builder.io. “[Builder Code MCP server](https://www.builder.io/c/docs/fusion-mcp-server)” and “[Fusion](https://www.builder.io/fusion/).” Accessed September 9, 2026.
[^21]: Anima. “[Anima MCP](https://docs.animaapp.com/docs/anima-mcp)” and “[MCP server guide](https://github.com/AnimaApp/mcp-server-guide/blob/main/anima/SKILL.md).” Accessed September 9, 2026.
[^22]: Webflow. “[Webflow MCP server](https://developers.webflow.com/mcp/reference/overview)” and “[MCP v2.0.1 changelog](https://developers.webflow.com/home/changelog/2026/7/21).” July 21, 2026.
[^23]: 21st.dev. “[21st Codex plugin](https://github.com/21st-dev/codex-plugin)” and “[Magic MCP migration](https://github.com/21st-dev/magic-mcp).” Accessed September 9, 2026.
[^24]: Vercel. “[v0 SDK](https://github.com/vercel/v0-sdk),” “[v0 quickstart](https://v0.dev/docs/quickstart),” and “[v0 Model API](https://v0.dev/docs/v0-model-api).” Accessed September 9, 2026.
[^25]: Abi Raja. “[screenshot-to-code](https://github.com/abi/screenshot-to-code).” MIT-licensed repository, accessed September 9, 2026.
[^26]: OpenAI/Higgsfield. “[Higgsfield Codex plugin manifest](https://github.com/openai/plugins/blob/main/plugins/higgsfield/.codex-plugin/plugin.json).” Public version 1.2.1; local remote catalog app version 1.5.0 observed September 9, 2026.
[^27]: OpenAI/HeyGen. “[HyperFrames plugin](https://github.com/openai/plugins/tree/main/plugins/hyperframes).” Accessed September 9, 2026; OpenAI. “[Remotion plugin](https://github.com/openai/plugins/tree/main/plugins/remotion).” Accessed September 9, 2026.
[^28]: Storybook. “[MCP server overview](https://storybook.js.org/docs/ai/mcp/overview).” Version 10.6 documentation, accessed September 9, 2026.
[^29]: shadcn/ui. “[MCP Server](https://ui.shadcn.com/docs/mcp)” and “[Registry introduction](https://ui.shadcn.com/docs/registry).” Accessed September 9, 2026.
[^30]: Microsoft. “[Playwright MCP](https://github.com/microsoft/playwright-mcp)” and “[Playwright MCP installation](https://github.com/microsoft/playwright.dev/blob/main/mcp/installation.mdx).” Accessed September 9, 2026.
[^31]: Chrome DevTools. “[Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp).” Accessed September 9, 2026.
[^32]: Deque. “[axe-core](https://github.com/dequelabs/axe-core).” Accessed September 9, 2026.
[^33]: Deque. “[Axe Accessibility plugin](https://github.com/dequelabs/axe-accessibility),” “[Axe DevTools pricing](https://www.deque.com/axe/devtools/pricing/),” and “[Axe MCP Server](https://www.deque.com/axe/mcp-server/).” Accessed September 9, 2026.
[^34]: Pa11y. “[Pa11y](https://github.com/pa11y/pa11y).” Accessed September 9, 2026.
[^35]: Chromatic. “[Pricing](https://www.chromatic.com/pricing).” Accessed September 9, 2026.
[^36]: OpenAI. “[Image generation](https://learn.chatgpt.com/docs/image-generation).” Accessed September 9, 2026. The page states that built-in image generation uses `gpt-image-2`, counts toward general Codex usage limits, and consumes included limits 3–5 times faster on average than similar non-image turns; it identifies `OPENAI_API_KEY` as the separately priced API path for larger batches, which Q002 prohibits.
[^37]: Figma. “[Plans and pricing](https://www.figma.com/pricing/)” and “[Rate limits & access](https://developers.figma.com/docs/figma-mcp-server/rate-limits-access/).” Accessed September 9, 2026.
[^38]: OpenAI/Figma. “[Code Connect skill](https://github.com/openai/plugins/blob/main/plugins/figma/skills/figma-code-connect/SKILL.md).” Accessed September 9, 2026.
[^39]: Canva. “[Canva MCP](https://www.canva.dev/docs/mcp/)” and “[Connect AI assistants to Canva](https://www.canva.com/help/mcp-agent-setup/).” Accessed September 9, 2026.
[^40]: Google Labs. “[Introducing vibe design with Stitch](https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-ai-ui-design/).” March 18, 2026; Google Labs. “[Stitch’s DESIGN.md format is now open source](https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-design-md/).” April 21, 2026.
[^41]: Penpot. “[Penpot repository](https://github.com/penpot/penpot).” Accessed September 9, 2026.
[^42]: NextLevelBuilder. “[Tailwind Config Generator Code Injection Leading to RCE](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/issues/246).” Fixed after 2.5.0; “[Automated audit](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/issues/289).” April 2026; “[UI/UX Skill Degrades Website Design](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/issues/446).” August 16, 2026. Issue reports are evidence of reported defects, not independent confirmation of general quality.
[^43]: Dani Z. “[frontend-design skill benchmark](https://github.com/dani-z/frontend-design-skill-benchmark).” Accessed September 9, 2026.
[^44]: Canva. “[MCP usage policy](https://www.canva.dev/docs/mcp/usage-policy/).” Accessed September 9, 2026.
[^45]: Builder.io. “[How Builder Uses AI](https://www.builder.io/c/docs/ai-use)” and “[Privacy Mode](https://www.builder.io/c/docs/privacy-mode/).” Accessed September 9, 2026.
[^46]: Canva. “[Plans and pricing](https://www.canva.com/pricing/).” Accessed September 9, 2026.
[^47]: Adobe. “[Creative Cloud plans](https://www.adobe.com/creativecloud/plans.html)” and “[Adobe Express pricing](https://www.adobe.com/express/pricing).” Accessed September 9, 2026.
[^48]: Penpot. “[Transparent pricing](https://penpot.app/pricing).” Accessed September 9, 2026.
[^49]: Builder.io. “[Pricing](https://www.builder.io/pricing).” Accessed September 9, 2026.
[^50]: Anima. “[Pricing](https://www.animaapp.com/pricing).” Accessed September 9, 2026.
[^51]: Webflow. “[Plans and pricing](https://webflow.com/pricing)” and “[May 2026 pricing update](https://help.webflow.com/hc/en-us/articles/51059955082387-Updated-pricing-and-simplified-plans-for-May-2026).” Accessed September 9, 2026.
[^52]: Vercel. “[v0 pricing](https://v0.dev/docs/pricing).” Accessed September 9, 2026.
[^53]: 21st.dev. “[Introducing 21st membership](https://21st.dev/blog/introducing-21st-membership).” June 23, updated July 21, 2026.
[^54]: GitHub Advisory Database. “[GHSA-gxw4-4fc5-9gr5: figma-developer-mcp command injection](https://github.com/advisories/GHSA-gxw4-4fc5-9gr5).” Affected <=0.6.2; patched in 0.6.3, September 2025.
[^55]: OpenAI. “[Plugin Eval README](https://github.com/openai/plugins/blob/main/plugins/plugin-eval/README.md).” Accessed September 9, 2026. Local `codex plugin list` reported version 0.1.2 available but not installed.
[^56]: Higgsfield. “[Privacy Policy](https://higgsfield.ai/privacy-policy).” Effective August 27, 2026; Higgsfield. “[Enterprise](https://higgsfield.ai/enterprise).” Accessed September 9, 2026.
[^57]: 21st Labs. “[Terms of Service](https://mcp.21st.dev/terms).” Last updated July 20, 2026.
[^58]: OpenAI. “[Plugins](https://learn.chatgpt.com/docs/plugins).” Accessed September 9, 2026. The page states that Codex users can install plugins through the ChatGPT desktop app or Codex CLI and that the Codex IDE extension does not support plugins.
