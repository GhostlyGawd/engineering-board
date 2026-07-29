#!/usr/bin/env python3
"""Deterministic tests for the Milestone D.1 evaluation harness."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from evaluation.harness import (  # noqa: E402
    EvaluationError,
    load_run,
    prepare_run,
    record_attempt,
    score_run,
    validate_corpus,
    write_report,
)


POSITIVE_CATEGORIES = {"recurring-bug", "cross-domain-shared-cause"}


class EvaluationHarnessTests(unittest.TestCase):
    corpus_path = ROOT / "evaluation" / "corpus.json"
    contracts_path = ROOT / "evaluation" / "client-contracts.json"

    def make_config(self, directory: Path, run_id: str = "test-run") -> Path:
        corpus = json.loads(self.corpus_path.read_text(encoding="utf-8"))
        fingerprints = {
            case["id"]: f"ctx-{hashlib.sha256(case['id'].encode()).hexdigest()[:24]}"
            for case in corpus["cases"]
        }
        value = {
            "schema_version": "1",
            "run_id": run_id,
            "source_commit": "a" * 40,
            "trial_policy": "d1-gate2-v1",
            "profiles": {
                "primary": {
                    "client_version": "claude-code-test-1",
                    "model_identifier": "model-primary-test",
                    "instructions_sha256": "b" * 64,
                    "tools_sha256": "c" * 64,
                },
                "compatibility": {
                    "client_version": "codex-cli-test-1",
                    "model_identifier": "model-compat-test",
                    "instructions_sha256": "d" * 64,
                    "tools_sha256": "e" * 64,
                },
            },
            "context_fingerprints": fingerprints,
        }
        path = directory / "run-config.json"
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        return path

    def prepare(self, directory: Path, run_id: str = "test-run") -> Path:
        output = directory / "run"
        prepare_run(
            ROOT,
            self.corpus_path,
            self.contracts_path,
            self.make_config(directory, run_id),
            output,
        )
        return output

    @staticmethod
    def scored_attempt(trial: dict, case: dict, **overrides: object) -> dict:
        positive = case["category"] in POSITIVE_CATEGORIES
        context = trial["arm"] == "context"
        systemic = bool(positive and context)
        expected_memory = case["expected_relevant_memory"]
        attempt: dict[str, object] = {
            "schema_version": "1",
            "attempt_id": "attempt-1",
            "state": "scored",
            "replacement_for": None,
            "first_proposed_correction": "Inspect the declared case evidence.",
            "first_stated_cause": (
                case["expected_systemic_cause"] or "No shared systemic cause."
            ),
            "canonical_citations": (
                [case["canonical_evidence"][0]["id"]] if systemic else []
            ),
            "surfaced_memories": (
                [{"id": expected_memory, "rank": 1}]
                if context and expected_memory
                else []
            ),
            "final_diagnosis": (
                case["expected_systemic_cause"] or "The issue is independent."
            ),
            "systemic_before_local": systemic,
            "classification_evidence": "The classification follows the case contract.",
            "reviewer": "test-reviewer",
            "durable_systemic_conclusion": bool(systemic),
        }
        if context:
            attempt.update(
                {
                    "context_fingerprint": trial["context_brief"]["fingerprint"],
                    "expected_memory_rank": 1 if expected_memory else None,
                    "irrelevant_memory_count": 0,
                    "rejected_memory_treatment": "not_surfaced",
                    "lexical_decoy_treatment": (
                        "ignored"
                        if case["category"] == "lexical-decoy"
                        else "not_applicable"
                    ),
                    "outcome_loop": {
                        "expected_effect": case["scoring"][
                            "expected_outcome_effect"
                        ],
                        "observed_effect": case["scoring"][
                            "expected_outcome_effect"
                        ],
                        "before_rank": 2 if expected_memory else None,
                        "after_rank": 1 if expected_memory else None,
                        "matches_expected": True,
                    },
                }
            )
        attempt.update(overrides)
        return attempt

    def record_complete_run(
        self,
        run_dir: Path,
        overrides: dict[str, dict[str, object]] | None = None,
    ) -> None:
        manifest = load_run(run_dir)
        cases = {case["id"]: case for case in manifest["corpus"]["cases"]}
        overrides = overrides or {}
        for trial in manifest["trials"]:
            attempt = self.scored_attempt(trial, cases[trial["case_id"]])
            attempt.update(overrides.get(trial["trial_key"], {}))
            record_attempt(run_dir, trial["trial_key"], attempt)

    def test_corpus_contract_has_balanced_sanitized_cases(self) -> None:
        summary = validate_corpus(ROOT, self.corpus_path)
        self.assertEqual(summary["case_count"], 8)
        self.assertEqual(
            summary["category_counts"],
            {
                "cross-domain-shared-cause": 2,
                "independent-issue": 2,
                "lexical-decoy": 2,
                "recurring-bug": 2,
            },
        )
        self.assertEqual(len(summary["digest"]), 64)

    def test_corpus_rejects_category_drift_and_path_escape(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-corpus-") as temp:
            copied = Path(temp) / "evaluation"
            shutil.copytree(ROOT / "evaluation", copied)
            corpus_path = copied / "corpus.json"
            value = json.loads(corpus_path.read_text(encoding="utf-8"))
            value["cases"][0]["category"] = "independent-issue"
            corpus_path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(EvaluationError, "category allocation"):
                validate_corpus(copied.parent, corpus_path)

            value = json.loads(self.corpus_path.read_text(encoding="utf-8"))
            value["cases"][0]["canonical_evidence"][0]["path"] = "../escape.md"
            corpus_path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(EvaluationError, "unsafe relative path"):
                validate_corpus(copied.parent, corpus_path)

    def test_prepare_builds_64_isolated_arms_with_equal_pair_controls(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-plan-") as temp:
            run_dir = self.prepare(Path(temp))
            manifest = load_run(run_dir)
            self.assertEqual(len(manifest["trials"]), 64)
            primary = [t for t in manifest["trials"] if t["profile"] == "primary"]
            compatibility = [
                t for t in manifest["trials"] if t["profile"] == "compatibility"
            ]
            self.assertEqual(len(primary), 48)
            self.assertEqual(len(compatibility), 16)
            self.assertEqual(
                len({trial["workspace"] for trial in manifest["trials"]}), 64
            )
            pairs: dict[str, list[dict]] = {}
            for trial in manifest["trials"]:
                pairs.setdefault(trial["pair_key"], []).append(trial)
                self.assertTrue((run_dir / trial["workspace"] / "input.json").is_file())
            self.assertEqual(len(pairs), 32)
            for pair in pairs.values():
                self.assertEqual({item["arm"] for item in pair}, {"baseline", "context"})
                baseline = next(item for item in pair if item["arm"] == "baseline")
                context = next(item for item in pair if item["arm"] == "context")
                self.assertEqual(
                    baseline["controlled_inputs"], context["controlled_inputs"]
                )
                self.assertIsNone(baseline["context_brief"])
                self.assertIsNotNone(context["context_brief"])

    def test_prepare_refuses_existing_or_linked_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-path-") as temp:
            base = Path(temp)
            run_dir = self.prepare(base)
            with self.assertRaisesRegex(EvaluationError, "already exists"):
                prepare_run(
                    ROOT,
                    self.corpus_path,
                    self.contracts_path,
                    self.make_config(base, "second-run"),
                    run_dir,
                )
            linked = base / "linked"
            linked.symlink_to(base / "elsewhere", target_is_directory=True)
            with self.assertRaisesRegex(EvaluationError, "linked path"):
                prepare_run(
                    ROOT,
                    self.corpus_path,
                    self.contracts_path,
                    self.make_config(base, "linked-run"),
                    linked / "run",
                )


    def test_load_rejects_linked_run_and_tampered_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-integrity-") as temp:
            base = Path(temp)
            run_dir = self.prepare(base)
            linked = base / "run-link"
            linked.symlink_to(run_dir, target_is_directory=True)
            with self.assertRaisesRegex(EvaluationError, "linked path"):
                load_run(linked)

            manifest = load_run(run_dir)
            trial = manifest["trials"][0]
            workspace = run_dir / trial["workspace"]
            trial_input = json.loads(
                (workspace / "input.json").read_text(encoding="utf-8")
            )
            evidence_path = workspace / trial_input["evidence"][0]["path"]
            evidence_path.write_text("tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(EvaluationError, "evidence fingerprint"):
                load_run(run_dir)
    def test_record_enforces_scored_retry_and_one_replacement(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-retry-") as temp:
            run_dir = self.prepare(Path(temp))
            trial = load_run(run_dir)["trials"][0]
            failure = {
                "schema_version": "1",
                "attempt_id": "attempt-1",
                "state": "infrastructure_failure",
                "replacement_for": None,
                "failure_reason": "The client process did not start.",
            }
            record_attempt(run_dir, trial["trial_key"], failure)
            replacement = copy.deepcopy(failure)
            replacement.update(
                {
                    "attempt_id": "attempt-2",
                    "replacement_for": "attempt-1",
                    "failure_reason": "The replacement client also did not start.",
                }
            )
            record_attempt(run_dir, trial["trial_key"], replacement)
            third = copy.deepcopy(replacement)
            third["attempt_id"] = "attempt-3"
            third["replacement_for"] = "attempt-2"
            with self.assertRaisesRegex(EvaluationError, "replacement limit"):
                record_attempt(run_dir, trial["trial_key"], third)

            other = load_run(run_dir)["trials"][1]
            case = next(
                item
                for item in load_run(run_dir)["corpus"]["cases"]
                if item["id"] == other["case_id"]
            )
            scored = self.scored_attempt(other, case)
            record_attempt(run_dir, other["trial_key"], scored)
            retry = copy.deepcopy(scored)
            retry["attempt_id"] = "attempt-2"
            retry["replacement_for"] = "attempt-1"
            with self.assertRaisesRegex(EvaluationError, "scored trial"):
                record_attempt(run_dir, other["trial_key"], retry)

    def test_record_rejects_wrong_context_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-record-") as temp:
            run_dir = self.prepare(Path(temp))
            manifest = load_run(run_dir)
            trial = next(t for t in manifest["trials"] if t["arm"] == "context")
            case = next(c for c in manifest["corpus"]["cases"] if c["id"] == trial["case_id"])
            result = self.scored_attempt(
                trial, case, context_fingerprint="ctx-wrong-fingerprint"
            )
            with self.assertRaisesRegex(EvaluationError, "context fingerprint"):
                record_attempt(run_dir, trial["trial_key"], result)

    def test_complete_run_passes_all_product_and_compatibility_gates(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-pass-") as temp:
            run_dir = self.prepare(Path(temp))
            self.record_complete_run(run_dir)
            score = score_run(run_dir)
            self.assertTrue(score["overall_pass"])
            self.assertEqual(score["primary"]["positive_context_denominator"], 12)
            self.assertEqual(score["primary"]["context_rate_percent"], 100.0)
            self.assertEqual(score["primary"]["baseline_rate_percent"], 0.0)
            self.assertEqual(score["false_positive_count"], 0)
            self.assertEqual(score["missing_trial_arms"], [])

    def test_threshold_and_false_positive_failures_remain_visible(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-fail-") as temp:
            run_dir = self.prepare(Path(temp))
            manifest = load_run(run_dir)
            positive_context = [
                trial
                for trial in manifest["trials"]
                if trial["profile"] == "primary"
                and trial["arm"] == "context"
                and trial["category"] in POSITIVE_CATEGORIES
            ]
            negative_context = next(
                trial
                for trial in manifest["trials"]
                if trial["arm"] == "context"
                and trial["category"] == "lexical-decoy"
            )
            overrides = {
                trial["trial_key"]: {
                    "systemic_before_local": False,
                    "durable_systemic_conclusion": False,
                    "canonical_citations": [],
                }
                for trial in positive_context[:4]
            }
            overrides[negative_context["trial_key"]] = {
                "durable_systemic_conclusion": True
            }
            self.record_complete_run(run_dir, overrides)
            score = score_run(run_dir)
            self.assertFalse(score["overall_pass"])
            self.assertFalse(score["gates"]["primary_absolute_rate"])
            self.assertFalse(score["gates"]["zero_negative_conclusions"])
            self.assertIn(negative_context["case_id"], score["failed_cases"])

    def test_incomplete_run_reports_missing_arms(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-incomplete-") as temp:
            run_dir = self.prepare(Path(temp))
            score = score_run(run_dir)
            self.assertFalse(score["overall_pass"])
            self.assertEqual(len(score["missing_trial_arms"]), 64)
            self.assertFalse(score["gates"]["complete_evidence"])

    def test_report_is_bounded_and_contains_failed_cases(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-report-") as temp:
            run_dir = self.prepare(Path(temp))
            self.record_complete_run(run_dir)
            paths = write_report(run_dir)
            report = Path(paths["markdown"]).read_text(encoding="utf-8")
            self.assertIn("does not establish general productivity", report)
            self.assertIn("## Per-case evidence", report)
            self.assertIn("## Limitations", report)
            self.assertNotIn("raw_prompt", report)
            self.assertTrue(Path(paths["json"]).is_file())


    def test_report_refuses_linked_output_without_partial_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-report-link-") as temp:
            base = Path(temp)
            run_dir = self.prepare(base)
            protected = base / "protected.md"
            protected.write_text("protected\n", encoding="utf-8")
            (run_dir / "report.md").symlink_to(protected)
            with self.assertRaisesRegex(EvaluationError, "linked path"):
                write_report(run_dir)
            self.assertEqual(protected.read_text(encoding="utf-8"), "protected\n")
            self.assertFalse((run_dir / "report.json").exists())
    def test_cli_validate_reports_the_corpus_digest(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "evaluation" / "harness.py"),
                "validate",
                "--root",
                str(ROOT),
                "--corpus",
                str(self.corpus_path),
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["case_count"], 8)
        self.assertEqual(len(payload["digest"]), 64)


if __name__ == "__main__":
    unittest.main(verbosity=2)
