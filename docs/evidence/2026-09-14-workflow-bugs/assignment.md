# B010 and B011 workflow correction assignment

- User outcome: continuing board work respects other sessions; acknowledged defects are captured without a second request.
- Repository: GhostlyGawd/engineering-board; project engineering-board; base 76197522a27fc6f6c1e2e3a45c83a6cecebc4fc6.
- Lead: root. Builders: b010_builder and b011_builder in separate worktrees. Independent reviewer starts from the requirements and pinned implementation revision.
- Claims: b010-owner-20260914 and b011-owner-20260914, held by the lead on behalf of their respective builders in the original dogfood repository.
- B010 scope: skills/board-triage/SKILL.md and focused claim verification. Resume only after exact current-session ownership is established. Foreign, stale or unknown ownership cannot cause takeover or status reset. Preserve atomic acquisition, contention handling, one owned entry per session, and safe overview of unrelated sessions. Align shell and MCP paths.
- B011 scope: skills/board-intake/SKILL.md and focused intake verification. Capture an acknowledged concrete defect before ending the turn, including mistakes made during read-only work. Preserve uncertainty for speculative candidates, project routing, deduplication, foreground promotion authorization and honest failure reporting.
- Builder-owned evidence: b010-builder.md and b011-builder.md in this directory; any new tests use distinct paths. Lead owns shared test-runner registration, release notes, integration and board closeout.
- Review lenses: correctness and workflow/concurrency safety. Challenge own/foreign/missing/stale claims and confirmed/uncertain/duplicate/unavailable-capture scenarios against existing tool behavior.
- Exclusions: no runtime orchestration redesign, automatic canonical promotion without authorization, new evaluation criteria, product-effect assertions or unrelated local prototype/research publication.
- Verification: focused scenario checks, relevant existing suites, complete portable suite on integrated source, independent review and CI before merge.
- Delivery: source fixes through the normal PR path with Unreleased notes. No immutable release in this batch; installation delivery remains a separate release boundary under docs/RELEASING.md.
- Evidence retention owner: lead; this repository directory. Cost and time-to-outcome are not measured.
- Existing authorization: user requested both actionable bugs; repository authorizes routine implementation and delivery. No new owner decision required for this scope.
- Stop conditions: claim contention, substantive unresolved review failures, or required CI failures hold the affected delivery.
