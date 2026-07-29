#!/usr/bin/env python3
"""Deterministic tests for the Milestone D.1 evaluation harness."""

from __future__ import annotations

import copy
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
    build_context_evidence,
    load_run,
    prepare_run,
    record_attempt,
    score_run,
    validate_corpus,
    write_report,
)


POSITIVE_CATEGORIES = {"recurring-bug", "cross-domain-shared-cause"}


class EvaluationHarnessTests(unittest.TestCase):
    corpus_path = ROOT / "evaluation" / "evidence-corpus.json"
    calibration_corpus_path = ROOT / "evaluation" / "calibration-corpus.json"
    contracts_path = ROOT / "evaluation" / "client-contracts.json"
    source_commit = "e26149bf505ea7f5ae2d95294a8a108e6b3c429f"
    context_evidence: dict | None = None

    def make_config(
        self,
        directory: Path,
        run_id: str = "test-run",
        contracts_path: Path | None = None,
    ) -> Path:
        if self.__class__.context_evidence is None:
            self.__class__.context_evidence = build_context_evidence(
                ROOT, self.corpus_path, self.source_commit
            )
        evidence = self.__class__.context_evidence
        assert evidence is not None
        fingerprints = {
            case_id: brief["context_fingerprint"]
            for case_id, brief in evidence["briefs"].items()
        }
        contracts = json.loads(
            (contracts_path or self.contracts_path).read_text(encoding="utf-8")
        )
        profiles = {
            name: {
                "client_version": f"{name}-test-1",
                "model_identifier": f"model-{name}-test",
                "instructions_sha256": "b" * 64,
                "tools_sha256": "c" * 64,
            }
            for name in contracts["profiles"]
        }
        value = {
            "schema_version": "3",
            "run_id": run_id,
            "source_commit": self.source_commit,
            "trial_policy": "d1-client-neutral-v2",
            "profiles": profiles,
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
        surfaced_memories = (
            [
                {"id": item["id"], "rank": rank}
                for rank, item in enumerate(trial["context_brief"]["results"], start=1)
            ]
            if context
            else []
        )
        expected_memory_rank = next(
            (
                item["rank"]
                for item in surfaced_memories
                if item["id"] == expected_memory
            ),
            None,
        )
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
            "surfaced_memories": surfaced_memories,
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
                    "context_fingerprint": trial["context_brief"][
                        "context_fingerprint"
                    ],
                    "expected_memory_rank": expected_memory_rank,
                    "irrelevant_memory_count": 0,
                    "rejected_memory_treatment": "not_surfaced",
                    "lexical_decoy_treatment": (
                        "ignored"
                        if case["category"] == "lexical-decoy"
                        else "not_applicable"
                    ),
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
        self.assertEqual(summary["corpus_id"], "d1-product-effect")
        self.assertEqual(summary["corpus_role"], "evidence")
        self.assertEqual(summary["corpus_version"], 3)
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

    def test_calibration_corpus_validates_but_cannot_prepare_scored_run(self) -> None:
        summary = validate_corpus(ROOT, self.calibration_corpus_path)
        self.assertEqual(summary["corpus_role"], "calibration")
        with tempfile.TemporaryDirectory(prefix="eb-eval-calibration-") as temp:
            base = Path(temp)
            with self.assertRaisesRegex(
                EvaluationError, "locked evidence corpus"
            ):
                prepare_run(
                    ROOT,
                    self.calibration_corpus_path,
                    self.contracts_path,
                    self.make_config(base),
                    base / "run",
                )

    def test_corpus_rejects_category_drift_and_path_escape(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-corpus-") as temp:
            copied = Path(temp) / "evaluation"
            shutil.copytree(ROOT / "evaluation", copied)
            corpus_path = copied / "evidence-corpus.json"
            value = json.loads(corpus_path.read_text(encoding="utf-8"))
            value["cases"][0]["category"] = "independent-issue"
            corpus_path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(EvaluationError, "category allocation"):
                validate_corpus(copied.parent, corpus_path)

            value = json.loads(self.corpus_path.read_text(encoding="utf-8"))
            value["locked"] = False
            corpus_path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(EvaluationError, "invalid corpus lock"):
                validate_corpus(copied.parent, corpus_path)

            value = json.loads(self.corpus_path.read_text(encoding="utf-8"))
            value["cases"][0]["canonical_evidence"][0]["path"] = "../escape.md"
            corpus_path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(EvaluationError, "unsafe relative path"):
                validate_corpus(copied.parent, corpus_path)

    def test_evidence_corpus_rejects_visible_scoring_oracles(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-leakage-") as temp:
            copied = Path(temp) / "evaluation"
            shutil.copytree(ROOT / "evaluation", copied)
            corpus_path = copied / "evidence-corpus.json"
            value = json.loads(corpus_path.read_text(encoding="utf-8"))
            case = value["cases"][0]
            evidence_path = (
                copied
                / value["evidence_root"]
                / case["canonical_evidence"][0]["path"]
            )
            evidence_path.write_text(
                evidence_path.read_text(encoding="utf-8")
                + "\nThe paths use one shared canonical region-code boundary.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(EvaluationError, "oracle terms"):
                validate_corpus(copied.parent, corpus_path)

            evidence_path.write_text(
                (
                    ROOT
                    / "evaluation"
                    / value["evidence_root"]
                    / case["canonical_evidence"][0]["path"]
                ).read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            case["task"] = case["expected_systemic_cause"]
            corpus_path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(
                EvaluationError, "expected systemic cause"
            ):
                validate_corpus(copied.parent, corpus_path)

            case["task"] = "Inspect the reported behavior."
            case["title"] = case["expected_relevant_memory"]
            corpus_path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(EvaluationError, "expected memory id"):
                validate_corpus(copied.parent, corpus_path)

            case["title"] = "A sanitized title"
            case["scoring"]["information_gap"] = ""
            corpus_path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(EvaluationError, "information_gap"):
                validate_corpus(copied.parent, corpus_path)

    def test_evidence_context_surfaces_expected_negative_memory(self) -> None:
        evidence = build_context_evidence(
            ROOT, self.corpus_path, self.source_commit
        )
        expected = {"D1-C05": "H105", "D1-C06": "H106"}
        for case_id, memory_id in expected.items():
            result_ids = [
                item["id"] for item in evidence["briefs"][case_id]["results"]
            ]
            self.assertIn(memory_id, result_ids)

    def test_prepare_builds_48_isolated_arms_with_equal_pair_controls(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-plan-") as temp:
            run_dir = self.prepare(Path(temp))
            manifest = load_run(run_dir)
            self.assertEqual(manifest["corpus_id"], "d1-product-effect")
            self.assertEqual(manifest["corpus_version"], 3)
            self.assertEqual(
                manifest["corpus_digest"],
                validate_corpus(ROOT, self.corpus_path)["digest"],
            )
            self.assertEqual(len(manifest["trials"]), 48)
            reference = [
                t for t in manifest["trials"] if t["profile_role"] == "reference"
            ]
            self.assertEqual(len(reference), 48)
            self.assertEqual(
                len({trial["workspace"] for trial in manifest["trials"]}), 48
            )
            pairs: dict[str, list[dict]] = {}
            for trial in manifest["trials"]:
                pairs.setdefault(trial["pair_key"], []).append(trial)
                self.assertTrue((run_dir / trial["workspace"] / "input.json").is_file())
            self.assertEqual(len(pairs), 24)
            for pair in pairs.values():
                self.assertEqual({item["arm"] for item in pair}, {"baseline", "context"})
                baseline = next(item for item in pair if item["arm"] == "baseline")
                context = next(item for item in pair if item["arm"] == "context")
                self.assertEqual(
                    baseline["controlled_inputs"], context["controlled_inputs"]
                )
                self.assertEqual(baseline["repository"], context["repository"])
                for item in pair:
                    repository = (
                        run_dir
                        / item["workspace"]
                        / item["repository"]["path"]
                        / "engineering-board"
                        / "d1-evaluation"
                    )
                    self.assertTrue(
                        (repository / "hypotheses").is_dir()
                    )
                self.assertIsNone(baseline["context_brief"])
                self.assertIsNotNone(context["context_brief"])
                self.assertIn("context_fingerprint", context["context_brief"])
                self.assertIn("results", context["context_brief"])
                self.assertNotIn(
                    "expected_relevant_memory", context["context_brief"]
                )
                self.assertNotIn("rejected_memories", context["context_brief"])

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

    def test_complete_reference_run_passes_all_product_gates(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-pass-") as temp:
            run_dir = self.prepare(Path(temp))
            self.record_complete_run(run_dir)
            score = score_run(run_dir)
            self.assertTrue(score["overall_pass"])
            self.assertEqual(score["reference"]["positive_context_denominator"], 12)
            self.assertEqual(score["reference"]["context_rate_percent"], 100.0)
            self.assertEqual(score["reference"]["baseline_rate_percent"], 0.0)
            self.assertEqual(score["replications"], {})
            self.assertEqual(score["false_positive_count"], 0)
            self.assertEqual(score["missing_trial_arms"], [])

    def test_optional_replication_does_not_change_reference_gate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-replication-") as temp:
            base = Path(temp)
            contracts_path = base / "client-contracts.json"
            contracts = json.loads(self.contracts_path.read_text(encoding="utf-8"))
            contracts["profiles"]["other-client"] = {
                "role": "replication",
                "affects_product_gate": False,
                "client_id": "other-client",
                "transport": "mcp-stdio",
                "repetitions": 1,
                "required_pins": [
                    "client_version",
                    "model_identifier",
                    "instructions_sha256",
                    "tools_sha256",
                ],
            }
            contracts_path.write_text(
                json.dumps(contracts, indent=2) + "\n", encoding="utf-8"
            )
            run_dir = base / "run"
            prepare_run(
                ROOT,
                self.corpus_path,
                contracts_path,
                self.make_config(base, contracts_path=contracts_path),
                run_dir,
            )
            manifest = load_run(run_dir)
            cases = {case["id"]: case for case in manifest["corpus"]["cases"]}
            for trial in manifest["trials"]:
                if trial["profile_role"] != "reference":
                    continue
                record_attempt(
                    run_dir,
                    trial["trial_key"],
                    self.scored_attempt(trial, cases[trial["case_id"]]),
                )
            score = score_run(run_dir)
            self.assertFalse(score["replications"]["other-client"]["complete"])
            self.assertEqual(
                len(score["missing_replication_arms"]["other-client"]), 16
            )
            self.assertTrue(score["gates"]["outcome_loop_matches"])
            self.assertTrue(score["gates"]["reference_complete"])
            self.assertTrue(score["overall_pass"])

    def test_threshold_and_false_positive_failures_remain_visible(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-fail-") as temp:
            run_dir = self.prepare(Path(temp))
            manifest = load_run(run_dir)
            positive_context = [
                trial
                for trial in manifest["trials"]
                if trial["profile_role"] == "reference"
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
            self.assertFalse(score["gates"]["reference_absolute_rate"])
            self.assertFalse(score["gates"]["zero_negative_conclusions"])
            self.assertIn(negative_context["case_id"], score["failed_cases"])

    def test_incomplete_run_reports_missing_arms(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-eval-incomplete-") as temp:
            run_dir = self.prepare(Path(temp))
            score = score_run(run_dir)
            self.assertFalse(score["overall_pass"])
            self.assertEqual(len(score["missing_trial_arms"]), 48)
            self.assertFalse(score["gates"]["reference_complete"])

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
