# Milestone D.1 harness implementation evidence: 2026-07-29

## Scope

This change implements the repository-only evaluation harness that Gate 2
authorized. It adds the frozen eight-case corpus, client contracts, isolated
trial planner, attempt recorder, scorer, bounded report writer, and deterministic
tests.

The harness does not execute Claude Code or Codex CLI. This change does not run
the live paired trials. It does not calibrate production ranking. It does not
establish that Engineering Board improves general productivity or agent
diagnosis.

## Contract clarification

The primary rate gates use only the four positive cases: recurring bugs and
cross-domain shared causes. Three repetitions produce 12 context trials and 12
baseline trials for these rate denominators.

Lexical-decoy and independent-issue cases do not enter the positive-case rate.
They use the separate gate that permits zero durable systemic conclusions.
This separation makes the accepted positive-effect and false-positive
requirements consistent.

## Lifecycle evidence matrix

| Sequence | Failure injection | Expected semantic outcome | Durable evidence | Test |
|---|---|---|---|---|
| Corpus validation | Change one category allocation | Validation stops before case semantics | Typed error and unchanged corpus | `test_corpus_rejects_category_drift_and_path_escape` |
| Corpus validation | Use an evidence path with `..` | Validation rejects the unsafe relative path | Typed error | `test_corpus_rejects_category_drift_and_path_escape` |
| Run preparation | None | Planner creates 32 pairs and 64 isolated arms | Fingerprinted manifest and workspace inputs | `test_prepare_builds_64_isolated_arms_with_equal_pair_controls` |
| Pair construction | Compare baseline and context inputs | Controlled inputs are equal; only context receives the brief | Pair records in the manifest | `test_prepare_builds_64_isolated_arms_with_equal_pair_controls` |
| Run preparation | Use an existing or linked output | Planner makes no output mutation | Typed error | `test_prepare_refuses_existing_or_linked_output` |
| Run loading | Use a linked run or modify copied case evidence | Loader rejects the run before scoring | Typed error and original manifest | `test_load_rejects_linked_run_and_tampered_evidence` |
| Attempt recording | Record a scored result and then retry | Recorder rejects the retry | First scored record and typed error | `test_record_enforces_scored_retry_and_one_replacement` |
| Attempt recording | Record one infrastructure failure and one replacement | Recorder preserves both attempts and their relation | Two restricted record files | `test_record_enforces_scored_retry_and_one_replacement` |
| Attempt recording | Request a second replacement | Recorder rejects the third attempt | Two prior records and typed error | `test_record_enforces_scored_retry_and_one_replacement` |
| Context recording | Supply the wrong context fingerprint | Recorder rejects the result | Typed error and unchanged records | `test_record_rejects_wrong_context_fingerprint` |
| Complete scoring | Supply all conforming results | All product and compatibility gates pass | Structured score | `test_complete_run_passes_all_product_and_compatibility_gates` |
| Product-effect scoring | Put four of 12 positive context trials below the threshold | Absolute-rate gate fails | Failed gate and case evidence | `test_threshold_and_false_positive_failures_remain_visible` |
| Negative-case scoring | Add a durable conclusion to a lexical decoy | Zero-conclusion gate fails | False-positive count and failed case | `test_threshold_and_false_positive_failures_remain_visible` |
| Incomplete scoring | Record no results | Completeness gate fails and lists all 64 arms | Missing-arm list | `test_incomplete_run_reports_missing_arms` |
| Report writing | Supply a complete conforming run | Writer publishes bounded per-case evidence and limitations | JSON and Markdown reports | `test_report_is_bounded_and_contains_failed_cases` |
| Report writing | Use a linked report output | Writer rejects the link before it writes either report | Typed error and unchanged link target | `test_report_refuses_linked_output_without_partial_write` |
| Command interface | Validate the frozen corpus | Command returns the case count and stable digest | JSON standard output | `test_cli_validate_reports_the_corpus_digest` |

## Verification evidence

- Focused harness suite: PASS, 13 tests.
- Corpus allocation: PASS, eight cases and two cases in each category.
- Python compatibility boundary: the harness uses the standard library and
  supports the declared Python 3.8 or later runtime.
- Complete repository suite: PASS, 19 of 19 suites.
- Implementation pull request: [#110](https://github.com/GhostlyGawd/engineering-board/pull/110).
- Tested branch commit: `7858f97f7437dfd356f5811b68bbb2765562071c`.
- Pull-request continuous integration: PASS. Both `run-all` checks passed.
- Merged implementation commit:
  `85c7ef1f7e0c7b45348cbff6e028b6f64862aafc`.
- Merged-main continuous integration: PASS,
  [tests run 30426727416](https://github.com/GhostlyGawd/engineering-board/actions/runs/30426727416).

The focused tests verify the repository-owned harness contract. They do not
validate a live Claude Code plugin run or a live Codex CLI MCP run. Those
integrations require authenticated clients, pinned model access, and an
authorized dated evidence run.

## Documentation alignment

Changed in this implementation:

- `docs/PRODUCT_EVOLUTION_SPEC.md`
- `docs/evidence/2026-07-29-milestone-d1-product-proof-contract.md`
- `evaluation/README.md`
- `ARCHITECTURE.md`
- `SECURITY.md`
- `README.md`
- `ROADMAP.md`
- `CHANGELOG.md`

Reviewed and unaffected:

- Plugin commands, hooks, MCP tools, package manifests, permission manifests,
  release versions, checksums, and published bundles. The `evaluation/`
  directory is repository-only and is outside the plugin and MCP bundle inputs.
- Historical release evidence. Each historical report remains an immutable
  record of its dated release boundary.

## Next evidence boundary

The next authorized product step is the dated paired evidence run. Before that
run starts, record exact source, client, model, instructions, tools, policy,
and context fingerprints in its manifest. Do not change the frozen baseline
during the run. Preserve every failed case.
