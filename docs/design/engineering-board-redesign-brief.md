# Engineering Board redesign brief

Status: approved by the owner in chat on September 10, 2026. Step 2; F008.
Approval covers the brief as the basis for three visual directions; no visual
option or implementation target has been selected. Proposed wording below is
retained as the exact reviewed brief; its audience, intent, scope and design
acceptance checks are now accepted for exploration.
Scope of this deliverable: design intent, not a selected visual direction.

## Purpose and audience

Make Engineering Board easier to understand, start using, and inspect when an
engineering agent encounters a recurring problem.

Proposed primary audience: developers and maintainers who use coding agents
and want useful repository context to survive across sessions. Design the human
experience for the person choosing, configuring, and reviewing the tool; preserve
the structured evidence that agents consume. Use Codex for the first onboarding
walkthrough, with clearly separated Claude Code and standalone MCP paths.

Working product description, for messaging exploration:

> Repository memory that connects engineering findings and keeps the evidence
> behind a proposed root cause within reach.

Lead with memory and investigation. Explain repository-owned Markdown as the
mechanism that makes the record inspectable and portable. Treat improved
diagnosis as the intended benefit, not an established performance claim.

## Brand intent

Proposed character: precise, trustworthy, and useful during real engineering
work. The memorable idea is **a finding connected to earlier evidence**.
Typography, hierarchy, source links, and understandable states should express it.

Keep the name Engineering Board. Use the current compact mark and restrained
visual family as a baseline to evaluate. Explore one evolutionary direction and
two distinct alternatives before choosing a palette, type system, mark treatment,
or layout. Each must work for both the public introduction and dense evidence
inspection. Existing BRAND.md remains current until a replacement is selected.

The plain technical voice, truthful examples, and distinction between evidence
and inference carry forward. Preserve the owner-approved controlled-English
requirements; any proposed copy remains draft until the direction is selected.

## Core journey and scope

**Understand the purpose → choose a client → reach a first useful result →
find related evidence → inspect a proposed cause and its sources → understand
the next investigation action.**

First prototype: a landing-page introduction and installation handoff, paired
with one read-only investigation-browsing journey using the same concrete case.
Show a clearly labeled synthetic example with findings, their relationship,
a proposed hypothesis, supporting evidence, an alternative, and a falsifier.
Include a source-record destination and a clear return path. The real project
board stays visibly separate from demonstration data.

For the Codex handoff, build on the existing README instruction to ask the agent
to initialize the active repository. Specify the expected visible result and
how to recover if initialization fails. Verify any additional first-use prompt
against the installed adapter before presenting it as supported.

After prototype validation, extend the selected system to the normal board,
README, command response presentation, diagrams, logo variants, favicon, and
social preview. Address the audited link and accessibility defects during the
relevant implementation slices; they remain open as B016 and B017.

## Proposed acceptance checks

| User outcome | Evidence required before calling the redesign successful |
| --- | --- |
| Understand the purpose | A fresh reviewer can describe what is retained, who uses it, and how to inspect the evidence without coaching. Record their answers; distinguish expert review from user research. |
| Start using it | Run the Codex first-use path in a disposable repository. Confirm a visible result and understandable recovery instructions; inventory the other client paths separately. |
| Reach evidence | Every link in the selected example reaches its intended record and supports returning to the investigation. Recheck the deployed B001 regression. |
| Interpret uncertainty | Reviewer distinguishes relationship facts, investigation priority, proposed causes, confirmed results, and rejected memory in representative states. Status must remain visible without relying on color. |
| Use the interface | Verify keyboard focus/order, code scrolling, light/dark contrast, no-results feedback, empty states, and layout at 390px and 1440px. Combine automated checks with manual interaction. |
| Recognize one product | Compare the selected direction across the introduction, board, README and assets; document any differences required by the host or content. |

These are proposed design acceptance checks. They do not replace or relax the
existing diagnosis-effect evaluation gates. Passing them would not establish
better agent diagnoses or a full accessibility certification.

## Accepted constraints and research handoff

Repository-owned Markdown remains canonical. Derived views remain explainable,
rebuildable and usable offline. Preserve the self-contained, read-only viewer,
its useful no-JavaScript baseline, existing adapter differences, and explicit
mutation boundaries. No required account, service, database, cross-repository
aggregation, or new orchestration layer is part of this redesign.

Next, use Refero styles for three visual directions, screens for evidence and
state presentation, and flows for onboarding/navigation. Retrieve full references
before designing. Compare all three directions on identical content and states;
record each direction's dominant reference and bounded secondary influences.
The earlier preview searches are leads, not an approved reference lock.

Owner decision requested: accept or revise the audience, working promise,
brand intent, first prototype scope, and proposed acceptance checks as the basis
for the three-direction exploration. This does not select a visual option or
authorize a change to the product's accepted purpose.

## Sources and limits

- [Authoritative product direction](../PRODUCT_EVOLUTION_SPEC.md), sections 2–4:
  memory/investigation identity, epistemic boundaries, and product constraints.
- [Current README](../../README.md): client differences, first-use instructions,
  product capabilities, and limits on outcome claims.
- [F007 audit](../evidence/2026-09-10-refero-audit/report.md) and
  [independent review](../evidence/2026-09-10-refero-audit/review.md): observed
  broken evidence link, local installation handoff gap, empty live demonstration,
  mobile presentation, and accessibility findings.
- [Current brand](../../BRAND.md): baseline identity; its historical contrast
  claims do not override the audit's current rendered results.

Audience prioritization and brand intent are proposals. No user research or
new visual design was performed for this brief. Unobserved installed workflows
and populated investigation states require verification during prototyping.
