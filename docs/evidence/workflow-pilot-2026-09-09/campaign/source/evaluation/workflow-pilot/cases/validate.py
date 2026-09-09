"""Offline fixture satisfiability and harmful-scope mutation checks."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASELINES = {"L-useful-retries": 2, "L-control-precision": 1,
             "H-useful-catalog": 0, "H-control-identifiers": 1}
MUTATIONS = {
    "L-useful-retries": ('options.get("heartbeat") or 30',
                        '30 if options.get("heartbeat") is None else options["heartbeat"]'),
    "L-control-precision": ('format(value, ".2f")',
                           'format(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f")'),
    "H-useful-catalog": ('return [row["id"] for row in rows]',
                         'return sorted(row["id"] for row in rows)'),
    "H-control-identifiers": ('record["id"] == part_id',
                              'record["id"].strip().lower() == part_id.strip().lower()'),
}


def run(command, cwd):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                            text=True, timeout=15)
    return {"exit_code": result.returncode, "stdout": result.stdout,
            "stderr": result.stderr}


def validate():
    records = []
    manifest = json.loads((ROOT / "cases.json").read_text())
    for case in manifest["cases"]:
        with tempfile.TemporaryDirectory(prefix="workflow-fixture-validation-") as temporary:
            trial = Path(temporary) / "repo"
            shutil.copytree(ROOT / case["repo"], trial,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            command = [sys.executable, str(ROOT / case["grader"]), "--repo", str(trial)]
            public = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
            baseline_public = run(public, trial)
            baseline_hidden = run(command, trial)
            assert baseline_public["exit_code"] == 1, case["id"]
            assert json.loads(baseline_hidden["stdout"])["passed"] == BASELINES[case["id"]]
            for name in case["allowed_implementation_files"]:
                shutil.copyfile(ROOT / case["reference"] / name, trial / name)
            reference_public = run(public, trial)
            reference_hidden = run(command, trial)
            assert reference_public["exit_code"] == 0, reference_public
            assert reference_hidden["exit_code"] == 0, reference_hidden
            module = trial / case["allowed_implementation_files"][0]
            before, after = MUTATIONS[case["id"]]
            code = module.read_text()
            assert before in code, case["id"]
            module.write_text(code.replace(before, after, 1))
            mutation_hidden = run(command, trial)
            assert mutation_hidden["exit_code"] == 1, mutation_hidden
            checks = json.loads(mutation_hidden["stdout"])["checks"]
            negatives = [v for k, v in checks.items() if k.startswith("check_negative")]
            assert negatives and not all(v["passed"] for v in negatives), checks
            history = (ROOT / case["history"]).read_text()
            parity = []
            for path in sorted((ROOT / case["board"]).rglob("*.md")):
                body = path.read_text().split("---", 2)[2].strip()
                assert body in history, path
                start = history.index(body)
                parity.append({"board_path": str(path.relative_to(ROOT)),
                               "assertion_scope": "entire substantive Markdown body",
                               "history_path": case["history"],
                               "history_start_line": history[:start].count("\n") + 1,
                               "history_end_line": history[:start + len(body)].count("\n") + 1,
                               "extra_board_substantive_guidance": []})
            inventory = []
            visible_label_scan = []
            for directory in (case["repo"], case["board"], str(Path(case["history"]).parent)):
                for path in sorted((ROOT / directory).rglob("*")):
                    if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                        data = path.read_bytes()
                        forbidden = re.search(
                            rb"useful|control|irrelevant_scope|wrong_shared_cause|expected_actions|reference repair|hidden (?:test|check|evaluator)",
                            data, re.IGNORECASE)
                        assert forbidden is None, (path, forbidden.group() if forbidden else "")
                        visible_label_scan.append(str(path.relative_to(ROOT)))
                        inventory.append({"path": str(path.relative_to(ROOT)),
                                          "bytes": len(data),
                                          "sha256": hashlib.sha256(data).hexdigest()})
            records.append({"id": case["id"], "baseline_public": baseline_public,
                            "baseline_hidden": baseline_hidden,
                            "reference_public": reference_public,
                            "reference_hidden": reference_hidden,
                            "harmful_scope_mutation_hidden": mutation_hidden,
                            "information_parity": parity, "input_inventory": inventory,
                            "visible_condition_label_scan": {"passed": True,
                                                             "files": visible_label_scan}})
    return {"version": 1, "provenance": "authored synthetic fixtures; not live evaluation",
            "command": "python3 evaluation/workflow-pilot/cases/validate.py",
            "metadata_parity_note": "Board ids, type, title, source status, confidence, dates, and affected paths appear in history prose. Fingerprints, revision bookkeeping and pattern tags are representation metadata only; no extra engineering assertions. Procedural guidance and hypothesis discriminating checks are authored synthetic historical content present identically in both conditions.",
            "cases": records}


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
