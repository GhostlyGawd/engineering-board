---
id: F005
type: feature
status: resolved
needs: validate
priority: P2
title: Expose a read-only hypothesis-detail route from retrieved H records
affects: mcp-server/engineering_board_mcp.py
discovered: 2026-09-09
discovered_at: 2026-09-09T15:39:59Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:a2370914218122c4]
parent: F004
---

# Expose a read-only hypothesis-detail route from retrieved H records

## Done when

- [x] A retrieved canonical H id has a discoverable read-only path to its full claim, status, provenance, alternatives and falsifier.
- [x] Existing B/F/Q/O/L entry reads retain their contracts; missing or malformed H records return clear, tested errors.
- [x] Successful and failed reads leave board, archive, graph and runtime state unchanged; no implicit hypothesis confirmation or outcome write occurs.
- [x] Independent tests and an installed retrieve-to-detail workflow verify the route; release state and observed usefulness are reported separately.

## Evidence

> F004 retained pilot TRACE-REVIEW: a3fdbe22065a4868 and c33139a00c714707 retrieved proposed H101/H102 summaries but did not receive full alternatives/falsifiers. Released1.13.5 board_get_entry(H-id) returns not found; board_hypotheses list returns metadata and source references, not full body. Local Markdown remains supported. Candidate bounded improvement: inspect one canonical H with status/provenance/alternatives/falsifier, discoverable from context; no state mutation, auto-confirmation, or success-counter change. Completion should verify H and legacy entry reads, malformed/missing handling, read-only byte invariance and installed workflow; assess actual usefulness separately.

## Comments

- **lead-workflow-pilot-20260909** 2026-09-09T15:43:06Z: Next bounded product task from the completed synthetic pilot, not implemented here. Local Markdown remains supported; add a discoverable read-only detail route without implicit causal confirmation. Future value validation must test normal installed activation and less-obvious real tasks rather than reusing these synthetic outcomes as efficacy proof.
- **lead-hypothesis-details-20260909** 2026-09-09T15:54:08Z: Lead owns this claim on behalf of build_hypothesis_details, working in /private/tmp/eb-hypothesis-details-20260909 on build/hypothesis-details from cad55eb. Builder owns MCP implementation/tests only; lead owns docs, retained smoke and release integration. A fresh independent verifier will review correctness, read-only security and discoverability before delivery. Release target is compatible-feature batch 1.14.0, not a D.1 pass or product-value claim.
- **lead-hypothesis-details-20260909** 2026-09-09T16:06:21Z: Source and read-only evidence passed, but unpacked MCP bundle initialize reports0.0.0 rather than1.14.0. Release held on B009 before tag/publication. Retain failed bundle-smoke.json; a separately claimed identity correction will be reviewed, followed by coordinated checksum refresh, all gates and installed verification.
- **lead-hypothesis-details-20260909** 2026-09-09T16:19:07Z: B009 release identity blocker corrected and independently verified. Refreshed1.14.0 full suite and strict gate pass. Actual marketplace publication and fresh installed-host verification remain before F005 closeout.
- **lead-hypothesis-details-20260909** 2026-09-09T16:42:02Z: Latest CI caught the B009 regression test's platform assumption; product handshake succeeds with correct version but test expects different fallback. Release held until corrected portable test and latest CI pass.
- **lead-hypothesis-details-20260909** 2026-09-09T16:49:26Z: PR175 merged as eb275b68369b04bbbc944a584f869fc07dcf05b3 afterlatestCIgreen. MainCIpassed and releaseworkflow34379065314 dispatched for exactSHA/tagv1.14.0 with registry+PyPI. Await actual publication and installed verification.
- **release-closeout-1.14.0** 2026-09-09T16:53:44Z: Codex update complete: installed cache1.14.0 HEAD matches exact release eb275b6; fresh installed MCP H101/H102 detail and missing-id checks pass with version1.14.0 and unchanged inventories. Codex 19-tool/host-boundary validation passes. Claude and PyPI installed probes also pass; all publication channels verified. Active host sessions may require restart. Final release-validation evidence is committed through a separate closeout PR.

## Approved implementation scope

Owner approved F005 after the retained workflow pilot. Extend a read-only detail route for canonical H records, preserving full claim/status/provenance/alternatives/falsifier, legacy entry-read contracts, clear missing/malformed errors, and no write or confirmation side effects. Lead session lead-hypothesis-details-20260909 owns implementation coordination and bounded builder assignment. Evidence and independent correctness/security/UX review precede closeout. No evaluation threshold, outcome counter, or agent-organization expansion.

## Released and installed verification

Released v1.14.0 from exact main/tag commit
eb275b68369b04bbbc944a584f869fc07dcf05b3 via PR175 and workflow 34379065314.
GitHub asset and MCP Registry match SHA-256
0b259fac619543308043f804dd5d5b49612cf018fcf61209e72f3f752d66cc67;
PyPI 1.14.0 wheel/sdist are present and unyanked. Latest PR CI and merged-main
CI pass all 22 suites; independent F005/B009 reviews passed and the MCP suite
passed 382 checks on Python 3.12.

Updated Codex and Claude plugins and a fresh public PyPI installation return
runtime 1.14.0 and exact H101/H102 details with unchanged repository inventories.
Codex cache HEAD and both hosts' runtime/manifest files match the tagged source.
Receipts are in docs/evidence/f005-hypothesis-details-2026-09-09/; the final
release record is docs/evidence/2026-09-09-v1.14.0-release-validation.md.
Existing sessions may still run their old MCP process until restart.

No product-effect, time-saved or D.1-pass claim is made; historical thresholds
and frozen evidence are unchanged.
