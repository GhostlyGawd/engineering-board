#!/usr/bin/env python3
"""Internal application coverage implementation for the test selector."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, cast, Sequence


POSIX_COVERAGE_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("bash", "tests/orchestration/automated.sh"),
    ("bash", "tests/claims/automated.sh"),
    ("bash", "tests/smoke/automated.sh"),
    ("bash", "tests/modes/automated.sh"),
    ("bash", "tests/permissions/automated.sh"),
    ("bash", "tests/release-preparation.sh"),
    ("bash", "tests/session-start/automated.sh"),
    ("bash", "tests/prompt-guard/automated.sh"),
    ("bash", "tests/view/automated.sh"),
    ("bash", "tests/security/reject-filter.sh"),
)
PORTABLE_COVERAGE_COMMANDS: tuple[tuple[str, ...], ...] = (
    (sys.executable, "tests/platform/test_foundation_portability.py"),
    (sys.executable, "tests/bootstrap/test_bootstrap_dev.py"),
    (sys.executable, "tests/evaluation/test_harness.py"),
    (sys.executable, "mcp-server/test_mcp_server.py"),
)


class CoverageGateError(Exception):
    """A deterministic coverage collection or threshold failure."""


def _tool_root(root: Path) -> Path:
    configured = os.environ.get("ENGINEERING_BOARD_DEV_TOOLS")
    if configured:
        return Path(configured).expanduser().resolve()
    return root / ".engineering-board" / "dev-tools"


def _coverage_executable(root: Path) -> Path:
    tool_root = _tool_root(root)
    suffix = ".exe" if os.name == "nt" else ""
    python_bin = "Scripts" if os.name == "nt" else "bin"
    executable = tool_root / "python-tools" / python_bin / f"coverage{suffix}"
    if not executable.is_file():
        raise CoverageGateError(
            f"missing pinned coverage tool at {executable}; run the repository bootstrap"
        )
    return executable


def _load_policy(root: Path) -> dict[str, Any]:
    path = root / "support" / "quality" / "coverage-policy.json"
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CoverageGateError(f"coverage policy is invalid: {exc}") from exc
    if policy.get("schema_version") != "1":
        raise CoverageGateError("coverage policy schema_version must be 1")
    applications = policy.get("applications")
    if not isinstance(applications, list) or not applications:
        raise CoverageGateError("coverage policy must declare application scopes")
    return cast(dict[str, Any], policy)


def _run(
    command: Sequence[str | Path],
    *,
    root: Path,
    environment: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(value) for value in command],
        cwd=root,
        env=environment,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def _git(root: Path, *arguments: str) -> str:
    result = _run(("git", "-C", root, *arguments), root=root, environment=os.environ.copy())
    if result.returncode != 0:
        raise CoverageGateError(
            f"cannot determine changed-line identity: git {' '.join(arguments)}"
        )
    return result.stdout.strip()


def _base_and_head(root: Path) -> tuple[str, str]:
    head = _git(root, "rev-parse", "HEAD")
    explicit = os.environ.get("ENGINEERING_BOARD_COVERAGE_BASE")
    candidates = [explicit] if explicit else []
    github_base = os.environ.get("GITHUB_BASE_REF")
    if github_base:
        candidates.append(f"origin/{github_base}")
    if os.environ.get("CI"):
        candidates.append("origin/main")
    candidates.append("HEAD^")
    for candidate in candidates:
        if not candidate:
            continue
        probe = _run(
            ("git", "-C", root, "rev-parse", "--verify", f"{candidate}^{{commit}}"),
            root=root,
            environment=os.environ.copy(),
        )
        if probe.returncode != 0:
            continue
        base = _git(root, "merge-base", candidate, head)
        if base != head:
            return base, head
    return head, head


def _changed_lines(root: Path, base: str, head: str) -> dict[str, set[int]]:
    if base == head:
        return {}
    diff = _git(root, "diff", "--unified=0", f"{base}...{head}", "--", "*.py")
    changed: dict[str, set[int]] = {}
    current = ""
    new_line = 0
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
            changed.setdefault(current, set())
            continue
        if line.startswith("@@"):
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            new_line = int(match.group(1)) if match else 0
            continue
        if not current:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            changed[current].add(new_line)
            new_line += 1
        elif line.startswith(" "):
            new_line += 1
    return changed


def _percent(covered: int, measured: int) -> float:
    return 100.0 if measured == 0 else (100.0 * covered / measured)


def _summary(values: Sequence[dict[str, Any]]) -> tuple[int, int, int, int]:
    covered_lines = sum(int(value["summary"]["covered_lines"]) for value in values)
    measured_lines = sum(int(value["summary"]["num_statements"]) for value in values)
    covered_branches = sum(int(value["summary"]["covered_branches"]) for value in values)
    measured_branches = sum(int(value["summary"]["num_branches"]) for value in values)
    return covered_lines, measured_lines, covered_branches, measured_branches


def _decision(label: str, measured: float, threshold: float) -> bool:
    passed = measured >= threshold
    print(
        f"quality-gate: coverage {label}: {'pass' if passed else 'fail'} "
        f"measured={measured:.2f}% threshold={threshold:.2f}%"
    )
    return passed


def _write_evidence(
    root: Path,
    report: dict[str, Any],
    decisions: dict[str, Any],
) -> None:
    output = root / ".engineering-board" / "validation" / "coverage"
    output.mkdir(parents=True, exist_ok=True)
    (output / "coverage.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "summary.json").write_text(
        json.dumps(decisions, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _collect_report(
    root: Path,
    policy: dict[str, Any],
    executable: Path,
    environment: dict[str, str],
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="engineering-board-coverage-") as temporary:
        temp = Path(temporary)
        data_file = temp / ".coverage"
        config = temp / "coveragerc"
        omitted_paths = [
            str(path) for path in policy.get("measurement", {}).get("omitted_paths", [])
        ]
        config_text = (
            "[run]\n"
            "branch = True\n"
            "parallel = True\n"
            "patch = subprocess\n"
            "source =\n"
            "    evaluation\n"
            "    hooks/scripts\n"
            "    mcp-server\n"
            "    scripts\n"
            "omit =\n" + "".join(f"    {path}\n" for path in omitted_paths) + "[report]\n"
            "skip_empty = True\n"
        )
        config.write_text(config_text, encoding="utf-8")
        driver = temp / "driver.py"
        commands = PORTABLE_COVERAGE_COMMANDS
        if os.name != "nt":
            commands = POSIX_COVERAGE_COMMANDS + commands
        driver.write_text(
            "import os, subprocess, sys\n"
            f"commands = {commands!r}\n"
            "environment = os.environ.copy()\n"
            "for command in commands:\n"
            "    result = subprocess.run(command, env=environment, "
            "text=True, encoding='utf-8', errors='replace', "
            "capture_output=True, check=False)\n"
            "    if result.returncode:\n"
            "        sys.stdout.write(result.stdout)\n"
            "        sys.stderr.write(result.stderr)\n"
            "        raise SystemExit(result.returncode)\n",
            encoding="utf-8",
        )
        environment["COVERAGE_FILE"] = str(data_file)
        environment["COVERAGE_PROCESS_START"] = str(config)
        collected = _run(
            (executable, "run", f"--rcfile={config}", driver),
            root=root,
            environment=environment,
        )
        if collected.returncode != 0:
            if collected.stdout:
                print(collected.stdout, end="")
            if collected.stderr:
                print(collected.stderr, end="", file=sys.stderr)
            raise CoverageGateError(
                f"coverage test collection failed with exit {collected.returncode}"
            )
        combined = _run(
            (executable, "combine", f"--rcfile={config}", temp),
            root=root,
            environment=environment,
        )
        if combined.returncode != 0:
            raise CoverageGateError("coverage data combination failed")
        report_path = temp / "coverage.json"
        reported = _run(
            (executable, "json", f"--rcfile={config}", "-o", report_path),
            root=root,
            environment=environment,
        )
        if reported.returncode != 0:
            raise CoverageGateError("coverage JSON report generation failed")
        report = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(report, dict):
        raise CoverageGateError("coverage JSON report must be an object")
    return cast(dict[str, Any], report)


def run_coverage(root: Path) -> None:
    root = root.resolve()
    policy = _load_policy(root)
    executable = _coverage_executable(root)
    environment = os.environ.copy()
    tool_root = _tool_root(root)
    python_bin = tool_root / "python-tools" / ("Scripts" if os.name == "nt" else "bin")
    environment["PATH"] = os.pathsep.join((str(python_bin), environment.get("PATH", "")))
    environment["PYTHONUTF8"] = "1"
    report = _collect_report(root, policy, executable, environment)
    omitted_paths = [str(path) for path in policy.get("measurement", {}).get("omitted_paths", [])]
    files = {
        path: value
        for path, value in report["files"].items()
        if not any(
            path.startswith(pattern) if pattern.endswith("/") else path == pattern
            for pattern in omitted_paths
        )
    }
    values = list(files.values())
    covered_lines, measured_lines, covered_branches, measured_branches = _summary(values)
    passes = [
        _decision(
            "total lines",
            _percent(covered_lines, measured_lines),
            float(policy["total"]["line_percent"]),
        ),
        _decision(
            "total branches",
            _percent(covered_branches, measured_branches),
            float(policy["total"]["branch_percent"]),
        ),
    ]
    application_results: list[dict[str, Any]] = []
    for application in policy["applications"]:
        prefixes = tuple(str(path) for path in application["paths"])
        app_values = [value for path, value in files.items() if path.startswith(prefixes)]
        app_line_covered, app_lines, app_branch_covered, app_branches = _summary(app_values)
        line_percent = _percent(app_line_covered, app_lines)
        branch_percent = _percent(app_branch_covered, app_branches)
        line_pass = _decision(
            f"application {application['id']} lines",
            line_percent,
            float(application["line_percent"]),
        )
        branch_pass = _decision(
            f"application {application['id']} branches",
            branch_percent,
            float(application["branch_percent"]),
        )
        passes.extend((line_pass, branch_pass))
        application_results.append(
            {
                "id": application["id"],
                "line_percent": line_percent,
                "branch_percent": branch_percent,
                "passed": line_pass and branch_pass,
            }
        )

    base, head = _base_and_head(root)
    changed = _changed_lines(root, base, head)
    changed_measured = 0
    changed_covered = 0
    uncovered: list[str] = []
    for path, lines in changed.items():
        value = files.get(path)
        if value is None:
            continue
        executable_lines = set(value["executed_lines"]) | set(value["missing_lines"])
        relevant = lines & executable_lines
        missing = relevant & set(value["missing_lines"])
        changed_measured += len(relevant)
        changed_covered += len(relevant) - len(missing)
        if missing:
            uncovered.append(f"{path}:{','.join(str(line) for line in sorted(missing))}")
    changed_percent = _percent(changed_covered, changed_measured)
    changed_threshold = float(policy["changed_lines"]["line_percent"])
    changed_pass = changed_percent >= changed_threshold
    suffix = f" uncovered={'; '.join(uncovered)}" if uncovered else ""
    print(
        f"quality-gate: coverage changed-lines: {'pass' if changed_pass else 'fail'} "
        f"measured={changed_percent:.2f}% threshold={changed_threshold:.2f}% "
        f"base={base} head={head} lines={changed_covered}/{changed_measured}{suffix}"
    )
    passes.append(changed_pass)
    decisions = {
        "schema_version": "1",
        "base": base,
        "head": head,
        "total": {
            "line_percent": _percent(covered_lines, measured_lines),
            "branch_percent": _percent(covered_branches, measured_branches),
        },
        "applications": application_results,
        "changed_lines": {
            "covered": changed_covered,
            "measured": changed_measured,
            "percent": changed_percent,
            "uncovered": uncovered,
        },
        "passed": all(passes),
    }
    _write_evidence(root, report, decisions)
    if not all(passes):
        raise CoverageGateError("one or more coverage thresholds failed")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    arguments = parser.parse_args(argv)
    try:
        run_coverage(arguments.root)
        return 0
    except CoverageGateError as exc:
        print(f"coverage-gate: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
