---
id: B001
type: bug
status: resolved
needs: tdd
priority: P1
title: Evaluation harness rejects macOS system temp paths
affects: evaluation/harness.py
discovered: 2026-09-08
discovered_at: 2026-09-08T23:50:02Z
promoted_from: [mcp:_sessions/mcp-2026-09-08.md:bd7cb0c9df491211]
---

# Evaluation harness rejects macOS system temp paths

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> Also affects tests/evaluation/test_harness.py. bash tests/run-all.sh produced 20 passing suites and one failing suite. evaluation-harness had 2 failures and 13 errors because tempfile paths under /var resolve through macOS /private/var and _reject_linked_path reports 'linked path is not allowed: /var'. Priority: P1. Done when the full suite passes on macOS while still rejecting attacker-controlled symlink traversal.

## Done when

- [ ] The full suite passes on macOS while still rejecting attacker-controlled symlink traversal.

Affected implementation and regression-test paths: `evaluation/harness.py` and `tests/evaluation/test_harness.py`.

## Comments

- **codex-b001-20260908** 2026-09-09T00:26:43Z: Claimed for TDD implementation. Reproduce the macOS /var to /private/var alias failure, preserve symlink-traversal rejection, and run the full suite.
- **codex-b001-20260908** 2026-09-09T00:31:05Z: Resolved after the full macOS suite passed 21/21 and targeted linked-path regressions passed 3/3.

## Resolution evidence

Allowed only the root-owned `/var -> /private/var` and `/tmp -> /private/tmp` system aliases while retaining rejection for every other symlink component. Added a macOS regression covering both the allowed system alias and a rejected attacker-controlled descendant symlink.

Verification on macOS:
- `python3 -m unittest ...test_root_owned_system_temp_alias_is_not_an_attacker_link ...test_prepare_refuses_existing_or_linked_output ...test_load_rejects_linked_run_and_tampered_evidence -v` — 3/3 passed.
- `bash tests/evaluation/automated.sh` — 23/23 passed.
- `bash tests/run-all.sh` — 21/21 suites passed.
