# Independent review — B010/B011

- Reviewer: workflow_verifier, independent from both builders, fresh context. Read requirements and runtime contracts before implementation; did not read builder conclusions.
- Revision: ad6a8854144088d511b748f0d982071e35c82276.
- Requirement sources: AGENTS.md, docs/DEVELOPMENT.md, maintainers/templates/review.md, and assignment.md in this directory.
- Lenses: correctness and workflow/concurrency safety.
- Scope: revised skills, focused tests, test registration, and existing claim/capture/promotion contracts. Reviewer made no repository, board, or external mutations; tests use isolated temporary fixtures.

## Findings

No blocking requirement defects found.

### B010

The gate distinguishes board status from current-session authority. It covers exact session identity, delegated ownership, router-resolved paths, duplicate IDs across projects, claims on entries still open, multiple owned claims, missing/malformed/future/stale records, and unavailable filesystem access. Foreign work remains available for overview without permitting fix research, takeover, release, or status reset. Unrelated foreign claims permit acquisition of separate ready work.

Acquisition matches both implementations: exit 0 acquires; exit 1 includes same-session replay contention; exit 2 does not reclaim. Subsequent ownership and eligibility checks precede status changes. Heartbeat guidance acknowledges the missing MCP heartbeat API and existing OneDrive detection differences.

Evidence: skills/board-triage/SKILL.md, MCP claim/release/status implementations, shell acquire and heartbeat implementations.

### B011

The confirmed-defect trigger includes acknowledged read-only workflow mistakes and requires scratch capture before the final response. It preserves speculative selection, uncertain causes, explicit capture pauses, routing, duplicate receipts, and honest failure reporting. Canonical promotion remains separately authorized through preview/apply. MCP guidance uses supported parameters and warns that a daily inbox may include unrelated findings. Shell guidance inherits the same trigger and retains the validated writer.

Evidence: skills/board-intake/SKILL.md, MCP capture/promotion handlers and schemas, shell scratch writer.

## Independent checks

Both commands exited 0:

- PYTHONDONTWRITEBYTECODE=1 python3 tests/triage-ownership/test_claim_contract.py — MCP and shell fresh acquisition, foreign contention, own replay, separate work, stale claims, missing owners, and unchanged entry/claim bytes.
- PYTHONDONTWRITEBYTECODE=1 python3 tests/b011-intake-contract.py — five tests: scratch-before-apply, uncertain observation, canonical deduplication, missing target, write failure.

Manual adversarial walkthrough covered ambiguous identity/routing, cross-project ownership, own claimed-open entries, multiple claims, future timestamps, missing inspection capability, shared-inbox authorization, uncertain append outcomes, and status-update failure.

## Verdict

PASS for the scoped source correction. No correction requested and no remaining blocker within review scope.

This establishes instruction clarity and compatibility with existing tool contracts. Executable tests do not measure whether an agent follows the prose. Full-suite/CI results remain lead delivery checks. Installed release behavior and improved real-world compliance are not established. Lead records CI, integration, and delivery before resolution.

## Integration recheck

Independent workflow_verifier rechecked 34e5a9798f932d04c63f85894636d8b8d548a6f3 after the first full run exposed B020: run-all appends a repository-root argument, which direct unittest entrypoints interpreted as a selector. All 23 original suites passed in that run; the two new registrations failed.

The correction adds a shell wrapper that accepts the root, quotes paths, and propagates failures with set -e. From /tmp the reviewer ran `PYTHONDONTWRITEBYTECODE=1 bash /tmp/eb-workflow-bugs-20260914/tests/workflow-contracts.sh /tmp/eb-workflow-bugs-20260914`: exit 0, claim test and all five intake tests pass. Verdict PASS, no remaining correction blocker. Earlier product-skill review still applies. Full-suite and CI remain separate lead checks.
