# Product-pattern research for F009

Research date: September 10, 2026. Scope: hierarchy and first-use handoff for
the approved visual exploration. These are proposed adaptations, not shipped
capabilities or a selected design. The lead owns the separate style locks.

## References and source roles

| Reference | ID and retrieval | Bounded source role |
| --- | --- | --- |
| [Linear issue detail](https://refero.design/pages/0549946f-24c8-4478-a9bd-f74ddc0c55dd) | Screen `0549946f-24c8-4478-a9bd-f74ddc0c55dd`; full metadata and full screenshot retrieved and visually inspected | Reading hierarchy: navigation/context, primary record, secondary properties, attachments and activity. No authority over branding or editable controls. |
| [OpenAI developer onboarding and API key setup](https://refero.design/flows/4178) | Flow `4178`; full flow retrieved after search `developer tool onboarding first project setup`. Returned metadata reports 26 screens; returned step narrative contains 20 labeled steps. | Journey logic only: setup leads directly to an executable first-use example and onward destination. No authority over product authentication, billing, API keys or visual identity. |

The Linear screenshot puts the title and explanation above attachments and
related sub-issues in a broad center column. Properties occupy a separate right
column; navigation and breadcrumb retain context. The darker, narrower property
surface stays subordinate to the main reading area. Those are observed source
patterns; the Engineering Board changes below are inferences from those patterns
and the approved brief.

The onboarding flow's steps 14–18 move from setup to an immediately usable
example. Step 16 pairs the newly available resource with a copy control and
usage snippet; steps 17–18 switch example language without restarting setup.
Step 20 returns to documentation with a code example still visible. This is a
historical design reference, not current OpenAI product guidance.

## Five concrete adaptations

1. **Make the record the visual center.** In the investigation example, lead with
   the finding/hypothesis title and plain explanation. Place supporting source
   links directly below the claim they support. Use a compact context region for
   the repository, example label and return link. This adapts Linear's main
   record hierarchy without importing a large workspace sidebar.
2. **Separate status from content.** Use a subordinate properties region for
   record ID, record kind and explicit state. Keep investigation priority and
   causal status separately named. Preserve “Proposed hypothesis” as text, not
   only a color. Linear supplies the content/properties split; the approved
   brief supplies the uncertainty distinctions. At narrow widths, place these
   properties near the heading in reading order, rather than preserving three
   cramped columns.
3. **Show linked evidence as records, not a decorative graph.** Adapt Linear's
   compact attachment and related-item rows to findings and source records:
   visible ID, descriptive title and destination. Keep the alternative and
   falsifier in the reading sequence beside the proposed explanation. Every
   concept uses the same synthetic case and a visible “Synthetic example”
   label. Source records must have a clear return path in the later prototype.
4. **Finish installation with one next action and its expected result.** Adapt
   flow 4178's immediate example handoff to the existing Codex instruction to
   ask the agent to initialize the active repository. Show the supported prompt
   beside a short description of what the user should see. Keep other client
   paths secondary and separately labeled. Do not invent a new slash command
   or mark initialization successful merely because the instructions are shown.
5. **Give the handoff a recovery and continuation route.** Beneath the first-use
   instruction, reserve concise recovery guidance for an initialization failure
   and a continuation into the labeled investigation example. The source flow
   provides explicit system responses and a documentation exit; the approved
   brief requires recovery and a first useful result. Exact recovery wording
   must be verified against the installed adapter during prototype work.

## Guardrails for visual mockups

The viewer is a read-only, offline inspection surface. Omit comment composers,
editable status dropdowns, assignee controls, invite buttons and account menus
from the Linear reference. Omit signup, API-key generation and purchase steps
from the onboarding reference. Do not imply live collaboration, automatic
causal proof, or that opening a design concept changes repository state.

This research supports concept composition and later prototype behavior; it
does not establish usability results, install success, or defect resolution.
