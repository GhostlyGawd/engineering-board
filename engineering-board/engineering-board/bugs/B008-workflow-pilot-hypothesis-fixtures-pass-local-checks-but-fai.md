---
id: B008
type: bug
status: resolved
needs: validate
priority: P2
title: Workflow-pilot hypothesis fixtures pass local checks but fail released Board retrieval validation
affects: evaluation/workflow-pilot/cases/
discovered: 2026-09-09
discovered_at: 2026-09-09T15:39:59Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:4462d8a4672add9c]
parent: F004
---

# Workflow-pilot hypothesis fixtures pass local checks but fail released Board retrieval validation

## Done when

- [x] Correct both hypothesis fixtures to the canonical fingerprint and body-section contract.
- [x] Validate all four memories through actual Board retrieval on source and installed 1.13.5, without stale flags or errors.
- [x] Preserve rejected prepared bytes and independently accept a fresh corrected inventory before live execution.

## Evidence

> Independent final prelaunch review of prepared manifest dfd906090616c296b95ec545f5caefa21ea8549fb2b42ef618a044849c6ca5f5 called installed 1.13.5 board_context for H101 and received isError:true invalid claim_fingerprint 'synthetic-h101'. No live model trial launched. Existing fixture validation did not exercise canonical hypothesis parser/retrieval. Designer assigned correction and all-four-case retrieval regressions under F004; rejected preparation preserved in Git c1d5f91.

## Verified correction

Implemented under the lead-owned F004 claim on behalf of design_workflow_cases. Commit16b841997c017832ad5a84e399319f4a32a81685 corrects both H fingerprint/body contracts and adds actual retrieval validation for all4cases. Source and installed1.13.5 pass; independent final acceptance pins manifest977a6fba9682798a48934ef9d32c359a0ec7598a9fa0ba0bf9a6151390335bf4 before live execution. Rejected manifestdfd906... remains committed in campaign/. See docs/evidence/workflow-pilot-2026-09-09/FINAL-ACCEPTANCE.md and cases/validation-evidence.json. This is a fixture validation fix, not a released-server defect or product-value result.

## Comments

- **fixture-closeout-20260909** 2026-09-09T15:44:18Z: Correction implemented and independently verified under F004; all explicit criteria met. Source and installed retrieval tests pass; rejected prelaunch bytes preserved; corrected inventory independently accepted before the only live campaign. No released-server defect or product-value result inferred.
