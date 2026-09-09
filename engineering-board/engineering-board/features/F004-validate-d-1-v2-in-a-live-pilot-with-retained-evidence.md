---
id: F004
type: feature
status: in_progress
needs: tdd
priority: P2
title: Validate D.1 v2 in a live pilot with retained evidence
affects: evaluation/
discovered: 2026-09-09
discovered_at: 2026-09-09T14:07:48Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:6017666468c845c0]
parent: F002
---

# Validate D.1 v2 in a live pilot with retained evidence

## Done when

- [ ] Before launch, independently review a predeclared non-scored plan with pinned source/client/model, tasks, comparisons, stopping rules and durable artifact destination.
- [ ] Preserve retrievable exact inputs, responses, start/end receipts and blind semantic review, including absent-memory and negative controls.
- [ ] Report memory-use quality separately from emitted ordering and preserve invalid or unfavorable outcomes.
- [ ] Record limitations and the release decision without silently changing historical thresholds or corpus locks.

## Evidence

> Follow-up delivery scope for F002 after independent B004-B007 source corrections. Complete when a reviewed predeclared non-scored campaign pins source/client/model/tasks/comparisons, stopping rules and a durable retrievable evidence destination; preserves exact prompts/responses/receipts and blind semantic review; includes absent/negative controls; reports memory-use quality separately from output ordering, limitations and the release decision. Historical thresholds and corpus locks are not changed by this task. No live result is claimed by the current synthetic implementation tests.

## Comments

- **measurement-cycle-closeout** 2026-09-09T14:10:08Z: Only live study and release decision remain after B004-B007 source correction and independent verification. Preserve current measurement/semantic limits, comparison and artifacts before launch; no result is implied by source completion.
- **lead-workflow-pilot-20260909** 2026-09-09T14:52:02Z: Lead owns claim on behalf of design_workflow_cases (cases/**, cases.json; isolated worktree), build_workflow_runner (runner.py/tests; isolated worktree), and read-only review_workflow_protocol. Prelaunch review found label leakage and retention/input-check mismatches; builders correcting before any live calls. Protocol and direct-Learning ledger retained under docs/evidence/workflow-pilot-2026-09-09/. Assisted MCP mechanism pilot explicitly excludes natural-host activation and customer-value claims.
- **lead-workflow-pilot-20260909** 2026-09-09T15:00:45Z: Final artifact acceptance held: installed1.13.5 actual board_context rejects H101 fixture fingerprint. No live calls. Retain rejected preparation campaign/ manifest dfd906... in Git c1d5f91. Fixture designer correcting canonical fields and adding source/released actual retrieval checks across all4 cases; new preparation will use campaign-v2, not edit/reuse rejected inputs. Full22 deterministic suites passed but were insufficient to establish released retrieval usability.

## Approved workflow-value study direction

Owner approved the product-value review recommendation: distinguish procedural Learning use from proposed-hypothesis investigation; compare ordinary repository work, selected historical evidence, and Engineering Board retrieval through a supported host workflow; judge useful investigation, coverage, patch correctness and overhead separately from response ordering. Fresh synthetic pilot tasks will be explicitly labeled, not represented as customer or independently sampled real-world incidents. Historical D.1 gates and corpus locks remain unchanged. Source instrumentation alone is not the product-value outcome.
