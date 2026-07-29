#!/usr/bin/env python3
"""Prepare and score deterministic Milestone D.1 evaluation runs."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any


CATEGORIES = {
    "recurring-bug",
    "cross-domain-shared-cause",
    "lexical-decoy",
    "independent-issue",
}
POSITIVE_CATEGORIES = {"recurring-bug", "cross-domain-shared-cause"}
NEGATIVE_CATEGORIES = CATEGORIES - POSITIVE_CATEGORIES
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class EvaluationError(ValueError):
    """Report an invalid evaluation artifact or operation."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"cannot read JSON file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvaluationError(f"JSON root must be an object: {path}")
    return value


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EvaluationError(message)


def _safe_relative(value: str) -> Path:
    path = Path(value)
    _require(bool(value) and not path.is_absolute() and ".." not in path.parts, f"unsafe relative path: {value}")
    return path


def _is_within(path: Path, parent: Path) -> bool:
    """Return true when path is inside parent on Python 3.8 or later."""
    return os.path.commonpath((str(path.resolve()), str(parent.resolve()))) == str(parent.resolve())


def _reject_linked_path(path: Path) -> None:
    current = path.absolute()
    for candidate in (current, *current.parents):
        if candidate.is_symlink():
            raise EvaluationError(f"linked path is not allowed: {candidate}")


def _atomic_text(path: Path, payload: str, exclusive: bool = False) -> None:
    _reject_linked_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if exclusive:
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as exc:
            raise EvaluationError(f"artifact already exists: {path}") from exc
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(payload)
        return
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(payload)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _atomic_json(path: Path, value: Any, exclusive: bool = False) -> None:
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    _atomic_text(path, payload, exclusive)


def validate_corpus(root: Path, corpus_path: Path) -> dict[str, Any]:
    """Validate the fixed eight-case corpus and return its fingerprint."""
    root = root.resolve()
    corpus_path = corpus_path.resolve()
    corpus = _read_json(corpus_path)
    _require(corpus.get("schema_version") == "1", "unsupported corpus schema version")
    cases = corpus.get("cases")
    _require(isinstance(cases, list) and len(cases) == 8, "corpus must contain exactly eight cases")
    allocation = Counter(case.get("category") for case in cases if isinstance(case, dict))
    expected = {category: 2 for category in CATEGORIES}
    _require(dict(allocation) == expected, f"invalid category allocation: {dict(allocation)}")
    evidence_root = _safe_relative(corpus.get("evidence_root", ""))
    evidence_base = corpus_path.parent / evidence_root
    _require(_is_within(evidence_base, root), "evidence root is outside the repository")
    counts: Counter[str] = Counter()
    ids: set[str] = set()
    for case in cases:
        _require(isinstance(case, dict), "each corpus case must be an object")
        case_id = case.get("id")
        category = case.get("category")
        _require(isinstance(case_id, str) and SAFE_NAME.fullmatch(case_id) is not None, "invalid case id")
        _require(case_id not in ids, f"duplicate case id: {case_id}")
        ids.add(case_id)
        _require(category in CATEGORIES, f"invalid category for {case_id}")
        counts[category] += 1
        for field in ("title", "task"):
            _require(isinstance(case.get(field), str) and bool(case[field].strip()), f"{case_id} requires {field}")
        files = case.get("files")
        _require(isinstance(files, list) and files and all(isinstance(item, str) for item in files), f"{case_id} requires files")
        evidence = case.get("canonical_evidence")
        _require(isinstance(evidence, list) and evidence, f"{case_id} requires canonical evidence")
        evidence_ids: set[str] = set()
        for item in evidence:
            _require(isinstance(item, dict) and isinstance(item.get("id"), str), f"invalid evidence for {case_id}")
            _require(item["id"] not in evidence_ids, f"duplicate evidence id for {case_id}")
            evidence_ids.add(item["id"])
            relative = _safe_relative(item.get("path", ""))
            source = evidence_base / relative
            _require(_is_within(source, evidence_base), f"unsafe relative path: {relative}")
            _reject_linked_path(source)
            _require(source.is_file(), f"missing evidence file: {source}")
        memory = case.get("expected_relevant_memory")
        cause = case.get("expected_systemic_cause")
        rejected = case.get("rejected_memories")
        scoring = case.get("scoring")
        _require(isinstance(rejected, list) and all(isinstance(item, str) for item in rejected), f"invalid rejected memories for {case_id}")
        _require(isinstance(scoring, dict) and isinstance(scoring.get("expected_outcome_effect"), str), f"invalid scoring contract for {case_id}")
        if category in POSITIVE_CATEGORIES:
            _require(isinstance(memory, str) and isinstance(cause, str), f"positive case {case_id} requires memory and cause")
            _require(scoring.get("durable_systemic_conclusion_allowed") is True, f"positive case {case_id} must allow a conclusion")
        else:
            _require(memory is None and cause is None, f"negative case {case_id} cannot define a systemic cause")
            _require(scoring.get("durable_systemic_conclusion_allowed") is False, f"negative case {case_id} cannot allow a conclusion")
        if category == "lexical-decoy":
            _require(bool(rejected), f"lexical decoy {case_id} requires a rejected memory")
        if category == "cross-domain-shared-cause":
            domains = {Path(item).parts[0] for item in files}
            _require(len(domains) >= 2, f"cross-domain case {case_id} requires two domains")
    _require(dict(counts) == expected, f"invalid category allocation: {dict(counts)}")
    return {"case_count": len(cases), "category_counts": dict(sorted(counts.items())), "digest": _digest(corpus)}


def _validate_contracts(value: dict[str, Any]) -> dict[str, Any]:
    _require(value.get("schema_version") == "1", "unsupported client contract schema")
    profiles = value.get("profiles")
    _require(isinstance(profiles, dict) and set(profiles) == {"primary", "compatibility"}, "client contracts require primary and compatibility profiles")
    expected = {"primary": ("claude-code-plugin", "plugin", 3), "compatibility": ("codex-cli-mcp", "mcp-stdio", 1)}
    for name, contract in profiles.items():
        client, transport, repetitions = expected[name]
        _require((contract.get("client_id"), contract.get("transport"), contract.get("repetitions")) == (client, transport, repetitions), f"invalid {name} client contract")
        _require(contract.get("required_pins") == ["client_version", "model_identifier", "instructions_sha256", "tools_sha256"], f"invalid {name} required pins")
    return profiles


def _validate_config(value: dict[str, Any], cases: list[dict[str, Any]], profiles: dict[str, Any]) -> None:
    _require(value.get("schema_version") == "1", "unsupported run configuration schema")
    _require(isinstance(value.get("run_id"), str) and SAFE_NAME.fullmatch(value["run_id"]) is not None, "invalid run id")
    _require(isinstance(value.get("source_commit"), str) and HEX40.fullmatch(value["source_commit"]) is not None, "source commit must be a lowercase 40-character SHA")
    _require(value.get("trial_policy") == "d1-gate2-v1", "invalid trial policy")
    configured = value.get("profiles")
    _require(isinstance(configured, dict) and set(configured) == set(profiles), "run profiles do not match client contracts")
    for name, contract in profiles.items():
        pins = configured[name]
        _require(isinstance(pins, dict), f"missing {name} profile pins")
        for pin in contract["required_pins"]:
            candidate = pins.get(pin)
            if pin.endswith("sha256"):
                _require(isinstance(candidate, str) and HEX64.fullmatch(candidate) is not None, f"invalid {name} {pin}")
            else:
                _require(isinstance(candidate, str) and bool(candidate.strip()), f"invalid {name} {pin}")
    fingerprints = value.get("context_fingerprints")
    _require(isinstance(fingerprints, dict) and set(fingerprints) == {case["id"] for case in cases}, "context fingerprints must cover every case")
    _require(all(isinstance(item, str) and bool(item.strip()) for item in fingerprints.values()), "invalid context fingerprint")


def prepare_run(root: Path, corpus_path: Path, contracts_path: Path, config_path: Path, output: Path) -> dict[str, Any]:
    """Create isolated baseline and context workspaces without running a client."""
    root = root.resolve()
    output = output.absolute()
    _reject_linked_path(output)
    _require(not output.exists(), f"output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    corpus_summary = validate_corpus(root, corpus_path)
    corpus = _read_json(corpus_path)
    contracts = _read_json(contracts_path)
    profiles = _validate_contracts(contracts)
    config = _read_json(config_path)
    _validate_config(config, corpus["cases"], profiles)
    stage = Path(tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent))
    try:
        trials: list[dict[str, Any]] = []
        evidence_base = corpus_path.resolve().parent / corpus["evidence_root"]
        for profile_name in ("primary", "compatibility"):
            contract = profiles[profile_name]
            for case in corpus["cases"]:
                for repetition in range(1, contract["repetitions"] + 1):
                    pair_key = f"{profile_name}-{case['id']}-r{repetition}"
                    controlled = {"task": case["task"], "files": case["files"], "evidence_ids": [item["id"] for item in case["canonical_evidence"]]}
                    for arm in ("baseline", "context"):
                        trial_key = f"{pair_key}-{arm}"
                        workspace = Path("workspaces") / trial_key
                        destination = stage / workspace
                        (destination / "evidence").mkdir(parents=True)
                        evidence_artifacts: list[dict[str, str]] = []
                        for item in case["canonical_evidence"]:
                            source = evidence_base / item["path"]
                            target = destination / "evidence" / Path(item["path"]).name
                            shutil.copyfile(source, target)
                            evidence_artifacts.append({"id": item["id"], "path": str(target.relative_to(destination)), "sha256": _file_digest(target)})
                        context_brief = None
                        if arm == "context":
                            context_brief = {"fingerprint": config["context_fingerprints"][case["id"]], "expected_relevant_memory": case["expected_relevant_memory"], "rejected_memories": case["rejected_memories"]}
                        trial_input = {"schema_version": "1", "trial_key": trial_key, "pair_key": pair_key, "profile": profile_name, "client": {"client_id": contract["client_id"], "transport": contract["transport"], **config["profiles"][profile_name]}, "case_id": case["id"], "category": case["category"], "repetition": repetition, "arm": arm, "controlled_inputs": controlled, "context_brief": context_brief, "evidence": evidence_artifacts}
                        _atomic_json(destination / "input.json", trial_input)
                        trials.append({**trial_input, "workspace": str(workspace), "input_sha256": _file_digest(destination / "input.json")})
        manifest = {"schema_version": "1", "run_id": config["run_id"], "source_commit": config["source_commit"], "trial_policy": config["trial_policy"], "corpus_digest": corpus_summary["digest"], "client_contracts_digest": _digest(contracts), "configuration_digest": _digest(config), "corpus": corpus, "trials": trials}
        manifest["manifest_fingerprint"] = _digest(manifest)
        _atomic_json(stage / "run-manifest.json", manifest)
        os.replace(stage, output)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return {"run_id": config["run_id"], "trial_arms": len(trials), "pairs": len(trials) // 2, "manifest": str(output / "run-manifest.json")}


def load_run(run_dir: Path) -> dict[str, Any]:
    """Load a run and verify its immutable planning artifacts."""
    run_dir = run_dir.absolute()
    _reject_linked_path(run_dir)
    run_dir = run_dir.resolve()
    manifest = _read_json(run_dir / "run-manifest.json")
    fingerprint = manifest.get("manifest_fingerprint")
    unsigned = dict(manifest)
    unsigned.pop("manifest_fingerprint", None)
    _require(fingerprint == _digest(unsigned), "run manifest fingerprint does not match")
    trials = manifest.get("trials")
    _require(isinstance(trials, list), "run manifest has no trials")
    keys: set[str] = set()
    for trial in trials:
        key = trial.get("trial_key")
        _require(isinstance(key, str) and SAFE_NAME.fullmatch(key) is not None and key not in keys, "invalid or duplicate trial key")
        keys.add(key)
        workspace = run_dir / _safe_relative(trial.get("workspace", ""))
        _reject_linked_path(workspace)
        input_path = workspace / "input.json"
        _require(input_path.is_file() and _file_digest(input_path) == trial.get("input_sha256"), f"trial input fingerprint does not match: {key}")
        trial_input = _read_json(input_path)
        for artifact in trial_input.get("evidence", []):
            artifact_path = workspace / _safe_relative(artifact.get("path", ""))
            _reject_linked_path(artifact_path)
            _require(
                artifact_path.is_file() and _file_digest(artifact_path) == artifact.get("sha256"),
                f"trial evidence fingerprint does not match: {key}",
            )
    return manifest


def _attempt_files(run_dir: Path, trial_key: str) -> list[Path]:
    directory = run_dir / "records" / trial_key
    if not directory.exists():
        return []
    _reject_linked_path(directory)
    paths = sorted(directory.glob("*.json"))
    for path in paths:
        _reject_linked_path(path)
        _require(path.is_file(), f"attempt artifact is not a file: {path}")
    return paths


def _validate_attempt(trial: dict[str, Any], case: dict[str, Any], attempt: dict[str, Any]) -> None:
    _require(attempt.get("schema_version") == "1", "unsupported attempt schema")
    _require(isinstance(attempt.get("attempt_id"), str) and SAFE_NAME.fullmatch(attempt["attempt_id"]) is not None, "invalid attempt id")
    _require(attempt.get("state") in {"scored", "infrastructure_failure"}, "invalid attempt state")
    if attempt["state"] == "infrastructure_failure":
        _require(isinstance(attempt.get("failure_reason"), str) and bool(attempt["failure_reason"].strip()), "infrastructure failure requires a reason")
        return
    for field in ("first_proposed_correction", "first_stated_cause", "final_diagnosis", "classification_evidence", "reviewer"):
        _require(isinstance(attempt.get(field), str) and bool(attempt[field].strip()), f"scored attempt requires {field}")
    for field in ("systemic_before_local", "durable_systemic_conclusion"):
        _require(isinstance(attempt.get(field), bool), f"scored attempt requires boolean {field}")
    citations = attempt.get("canonical_citations")
    memories = attempt.get("surfaced_memories")
    _require(isinstance(citations, list) and all(isinstance(item, str) for item in citations), "invalid canonical citations")
    _require(isinstance(memories, list), "invalid surfaced memories")
    for memory in memories:
        _require(isinstance(memory, dict) and isinstance(memory.get("id"), str) and isinstance(memory.get("rank"), int) and memory["rank"] >= 1, "invalid surfaced memory")
    if trial["arm"] == "baseline":
        _require(memories == [], "baseline arm cannot receive surfaced memories")
        return
    brief = trial["context_brief"]
    _require(attempt.get("context_fingerprint") == brief["fingerprint"], "context fingerprint does not match the trial")
    _require(attempt.get("expected_memory_rank") is None or isinstance(attempt.get("expected_memory_rank"), int), "invalid expected memory rank")
    _require(isinstance(attempt.get("irrelevant_memory_count"), int) and attempt["irrelevant_memory_count"] >= 0, "invalid irrelevant memory count")
    _require(attempt.get("rejected_memory_treatment") in {"not_surfaced", "rejected", "used"}, "invalid rejected memory treatment")
    _require(attempt.get("lexical_decoy_treatment") in {"ignored", "not_applicable", "used"}, "invalid lexical decoy treatment")
    outcome = attempt.get("outcome_loop")
    _require(isinstance(outcome, dict), "context attempt requires outcome loop evidence")
    _require(outcome.get("expected_effect") == case["scoring"]["expected_outcome_effect"], "outcome loop expected effect does not match the case")
    _require(isinstance(outcome.get("observed_effect"), str) and isinstance(outcome.get("matches_expected"), bool), "invalid outcome loop evidence")


def record_attempt(run_dir: Path, trial_key: str, attempt: dict[str, Any]) -> str:
    """Record one scored attempt or one permitted infrastructure replacement."""
    run_dir = run_dir.absolute()
    manifest = load_run(run_dir)
    run_dir = run_dir.resolve()
    trial = next((item for item in manifest["trials"] if item["trial_key"] == trial_key), None)
    _require(trial is not None, f"unknown trial key: {trial_key}")
    cases = {case["id"]: case for case in manifest["corpus"]["cases"]}
    existing = [_read_json(path) for path in _attempt_files(run_dir, trial_key)]
    _require(not any(item["state"] == "scored" for item in existing), "a scored trial cannot retry")
    if len(existing) >= 2:
        raise EvaluationError("infrastructure replacement limit is one attempt")
    if not existing:
        _require(attempt.get("replacement_for") is None, "initial attempt cannot replace another attempt")
    else:
        _require(existing[0]["state"] == "infrastructure_failure", "only an infrastructure failure can be replaced")
        _require(attempt.get("replacement_for") == existing[0]["attempt_id"], "replacement relation does not match the failed attempt")
    _require(all(item.get("attempt_id") != attempt.get("attempt_id") for item in existing), "duplicate attempt id")
    _validate_attempt(trial, cases[trial["case_id"]], attempt)
    path = run_dir / "records" / trial_key / f"{len(existing) + 1:02d}-{attempt['attempt_id']}.json"
    _atomic_json(path, attempt, exclusive=True)
    return str(path)


def _collect_results(run_dir: Path, manifest: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    scored: dict[str, dict[str, Any]] = {}
    invalid: list[dict[str, Any]] = []
    for trial in manifest["trials"]:
        for path in _attempt_files(run_dir, trial["trial_key"]):
            attempt = _read_json(path)
            if attempt.get("state") == "scored":
                scored[trial["trial_key"]] = attempt
            else:
                invalid.append({"trial_key": trial["trial_key"], "attempt_id": attempt.get("attempt_id"), "failure_reason": attempt.get("failure_reason"), "replacement_for": attempt.get("replacement_for")})
    return scored, invalid


def score_run(run_dir: Path) -> dict[str, Any]:
    """Score a run against the accepted D.1 product-effect gates."""
    run_dir = run_dir.absolute()
    manifest = load_run(run_dir)
    run_dir = run_dir.resolve()
    cases = {case["id"]: case for case in manifest["corpus"]["cases"]}
    scored, invalid = _collect_results(run_dir, manifest)
    missing = [trial["trial_key"] for trial in manifest["trials"] if trial["trial_key"] not in scored]
    primary_positive = [trial for trial in manifest["trials"] if trial["profile"] == "primary" and trial["category"] in POSITIVE_CATEGORIES]
    context_trials = [trial for trial in primary_positive if trial["arm"] == "context"]
    baseline_trials = [trial for trial in primary_positive if trial["arm"] == "baseline"]

    def rate(trials: list[dict[str, Any]]) -> float:
        if not trials or any(trial["trial_key"] not in scored for trial in trials):
            return 0.0
        successes = sum(bool(scored[trial["trial_key"]]["systemic_before_local"]) for trial in trials)
        return round(100.0 * successes / len(trials), 2)

    context_rate = rate(context_trials)
    baseline_rate = rate(baseline_trials)
    citation_total = 0
    citation_valid = 0
    rank_failures: set[str] = set()
    negative_failures: set[str] = set()
    outcome_failures: set[str] = set()
    failed_cases: set[str] = set()
    false_positive_count = 0
    per_case: dict[str, dict[str, Any]] = {
        case_id: {"category": case["category"], "scored_arms": 0, "systemic_before_local": 0, "durable_systemic_conclusions": 0, "failures": []}
        for case_id, case in cases.items()
    }
    for trial in manifest["trials"]:
        attempt = scored.get(trial["trial_key"])
        if attempt is None:
            per_case[trial["case_id"]]["failures"].append(f"missing:{trial['trial_key']}")
            failed_cases.add(trial["case_id"])
            continue
        case = cases[trial["case_id"]]
        summary = per_case[trial["case_id"]]
        summary["scored_arms"] += 1
        summary["systemic_before_local"] += int(attempt["systemic_before_local"])
        summary["durable_systemic_conclusions"] += int(attempt["durable_systemic_conclusion"])
        if attempt["systemic_before_local"]:
            citation_total += 1
            allowed = {item["id"] for item in case["canonical_evidence"]}
            if attempt["canonical_citations"] and set(attempt["canonical_citations"]).issubset(allowed):
                citation_valid += 1
            else:
                failed_cases.add(trial["case_id"])
                summary["failures"].append("canonical-citation")
        if trial["arm"] == "context":
            if case["category"] in POSITIVE_CATEGORIES:
                expected = case["expected_relevant_memory"]
                surfaced = next((item for item in attempt["surfaced_memories"] if item["id"] == expected), None)
                if surfaced is None or surfaced["rank"] > 3 or attempt.get("expected_memory_rank") != surfaced["rank"]:
                    rank_failures.add(trial["case_id"])
                    failed_cases.add(trial["case_id"])
                    summary["failures"].append("expected-memory-rank")
            if case["category"] in NEGATIVE_CATEGORIES and attempt["durable_systemic_conclusion"]:
                false_positive_count += 1
                negative_failures.add(trial["case_id"])
                failed_cases.add(trial["case_id"])
                summary["failures"].append("negative-systemic-conclusion")
            outcome = attempt.get("outcome_loop", {})
            if not outcome.get("matches_expected") or outcome.get("observed_effect") != outcome.get("expected_effect"):
                outcome_failures.add(trial["case_id"])
                failed_cases.add(trial["case_id"])
                summary["failures"].append("outcome-loop")
    complete = not missing
    citations_pass = complete and citation_total > 0 and citation_total == citation_valid
    gates = {
        "complete_evidence": complete,
        "primary_absolute_rate": complete and context_rate >= 75.0,
        "primary_improvement": complete and context_rate - baseline_rate >= 25.0,
        "canonical_citation_coverage": citations_pass,
        "expected_memory_rank": complete and not rank_failures,
        "zero_negative_conclusions": complete and not negative_failures,
        "outcome_loop_matches": complete and not outcome_failures,
        "compatibility_complete": complete and all(trial["trial_key"] in scored for trial in manifest["trials"] if trial["profile"] == "compatibility"),
    }
    if complete and (not gates["primary_absolute_rate"] or not gates["primary_improvement"]):
        failed_cases.update(case["id"] for case in cases.values() if case["category"] in POSITIVE_CATEGORIES)
    return {
        "schema_version": "1",
        "run_id": manifest["run_id"],
        "source_commit": manifest["source_commit"],
        "manifest_fingerprint": manifest["manifest_fingerprint"],
        "overall_pass": all(gates.values()),
        "gates": gates,
        "primary": {
            "positive_context_denominator": len(context_trials),
            "positive_baseline_denominator": len(baseline_trials),
            "context_rate_percent": context_rate,
            "baseline_rate_percent": baseline_rate,
            "improvement_percentage_points": round(context_rate - baseline_rate, 2),
        },
        "canonical_citation_coverage": {"valid": citation_valid, "total": citation_total, "percent": round(100.0 * citation_valid / citation_total, 2) if citation_total else 0.0},
        "false_positive_count": false_positive_count,
        "missing_trial_arms": missing,
        "invalid_attempts": invalid,
        "failed_cases": sorted(failed_cases),
        "per_case": per_case,
        "limitations": [
            "This bounded evaluation does not establish general productivity.",
            "The compatibility profile checks transport coverage and does not change the primary product-effect rate.",
            "The harness records supplied client results. It does not execute a live client.",
        ],
    }


def write_report(run_dir: Path) -> dict[str, str]:
    """Write bounded JSON and Markdown reports from recorded evidence."""
    run_dir = run_dir.absolute()
    score = score_run(run_dir)
    run_dir = run_dir.resolve()
    json_path = run_dir / "report.json"
    markdown_path = run_dir / "report.md"
    _reject_linked_path(json_path)
    _reject_linked_path(markdown_path)
    _atomic_json(json_path, score)
    status = "PASS" if score["overall_pass"] else "FAIL"
    lines = [
        "# Milestone D.1 evaluation report",
        "",
        f"- Run: `{score['run_id']}`",
        f"- Source commit: `{score['source_commit']}`",
        f"- Result: **{status}**",
        f"- Primary context rate: {score['primary']['context_rate_percent']}%",
        f"- Primary baseline rate: {score['primary']['baseline_rate_percent']}%",
        f"- Improvement: {score['primary']['improvement_percentage_points']} percentage points",
        f"- Negative-case durable conclusions: {score['false_positive_count']}",
        "",
        "## Gates",
        "",
    ]
    for name, passed in score["gates"].items():
        lines.append(f"- {'PASS' if passed else 'FAIL'}: `{name}`")
    lines.extend(["", "## Per-case evidence", ""])
    for case_id, item in score["per_case"].items():
        failures = ", ".join(item["failures"]) if item["failures"] else "none"
        lines.extend([
            f"### {case_id}",
            "",
            f"- Category: `{item['category']}`",
            f"- Scored arms: {item['scored_arms']}",
            f"- Systemic-before-local classifications: {item['systemic_before_local']}",
            f"- Durable systemic conclusions: {item['durable_systemic_conclusions']}",
            f"- Failures: {failures}",
            "",
        ])
    lines.extend(["## Limitations", ""])
    for limitation in score["limitations"]:
        lines.append(f"- {limitation}")
    lines.extend(["", "This report does not establish general productivity.", ""])
    _atomic_text(markdown_path, "\n".join(lines))
    return {"json": str(json_path), "markdown": str(markdown_path)}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate the fixed corpus")
    validate.add_argument("--root", required=True, type=Path)
    validate.add_argument("--corpus", required=True, type=Path)
    prepare = commands.add_parser("prepare", help="prepare an isolated run")
    prepare.add_argument("--root", required=True, type=Path)
    prepare.add_argument("--corpus", required=True, type=Path)
    prepare.add_argument("--contracts", required=True, type=Path)
    prepare.add_argument("--config", required=True, type=Path)
    prepare.add_argument("--output", required=True, type=Path)
    record = commands.add_parser("record", help="record one trial attempt")
    record.add_argument("--run", required=True, type=Path)
    record.add_argument("--trial", required=True)
    record.add_argument("--attempt", required=True, type=Path)
    score = commands.add_parser("score", help="score recorded evidence")
    score.add_argument("--run", required=True, type=Path)
    score.add_argument("--write-report", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "validate":
            result: Any = validate_corpus(args.root, args.corpus)
        elif args.command == "prepare":
            result = prepare_run(args.root, args.corpus, args.contracts, args.config, args.output)
        elif args.command == "record":
            result = {"record": record_attempt(args.run, args.trial, _read_json(args.attempt))}
        elif args.write_report:
            result = write_report(args.run)
        else:
            result = score_run(args.run)
    except EvaluationError as exc:
        _parser().error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
