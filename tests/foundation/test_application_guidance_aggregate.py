#!/usr/bin/env python3
"""Application guidance and aggregate compatibility regressions."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from aggregate_runner import AggregateRunner, Stage  # noqa: E402
from application_contract import (  # noqa: E402
    ApplicationContractError,
    audit_repository,
    discover_applications,
    shared_contract_fingerprint,
)


APPLICATION_ENTRY = ROOT / "scripts" / "application_contract.py"
LEGACY_ENTRY = ROOT / "scripts" / "legacy_run_all.py"


class ApplicationContractTests(unittest.TestCase):
    @staticmethod
    def copy_repository(destination: Path) -> Path:
        fixture = destination / "repository with spaces"
        shutil.copytree(
            ROOT,
            fixture,
            ignore=shutil.ignore_patterns(
                ".engineering-board",
                ".git",
                "__pycache__",
                "dist",
            ),
        )
        return fixture

    def test_discovery_uses_exact_canonical_roots_and_excludes_phantoms(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb application discovery ") as temp:
            fixture = self.copy_repository(Path(temp))
            phantom_roots = (
                fixture / "tests" / "fixtures" / "fake-plugin",
                fixture / ".engineering-board" / "runtime-plugin",
                fixture / "dist" / "built-plugin",
                fixture / "engineering-board" / "generated-board",
            )
            for phantom in phantom_roots:
                (phantom / ".claude-plugin").mkdir(parents=True)
                (phantom / ".claude-plugin" / "plugin.json").write_text(
                    '{"name":"phantom","version":"9.9.9"}\n',
                    encoding="utf-8",
                )
                (phantom / "pyproject.toml").write_text(
                    "[project]\nname='phantom'\nversion='9.9.9'\n",
                    encoding="utf-8",
                )

            self.assertEqual(
                [application.id for application in discover_applications(fixture)],
                ["root-plugin", "mcp-server"],
            )

            conductor = fixture / "conductor"
            conductor.mkdir()
            (conductor / "pyproject.toml").write_text(
                "[project]\nname='engineering-board-conductor'\nversion='0.1.0'\n",
                encoding="utf-8",
            )
            (conductor / "engineering_board_conductor.py").write_text(
                '"""Contained conductor fixture."""\n',
                encoding="utf-8",
            )
            self.assertEqual(
                [application.id for application in discover_applications(fixture)],
                ["root-plugin", "mcp-server", "conductor"],
            )

    def test_guidance_and_freshness_audit_passes_then_names_stale_surface(self) -> None:
        report = audit_repository(ROOT)
        self.assertEqual(report["applications"], ["root-plugin", "mcp-server"])
        self.assertEqual(report["application_count"], 2)
        self.assertEqual(report["product_version"], "1.13.4")
        self.assertEqual(report["tool_count"], 19)
        self.assertEqual(report["command_count"], 21)
        self.assertEqual(report["legacy_suite_count"], 26)
        self.assertRegex(shared_contract_fingerprint(ROOT), r"^[0-9a-f]{64}$")

        with tempfile.TemporaryDirectory(prefix="eb guidance stale ") as temp:
            fixture = self.copy_repository(Path(temp))
            guidance = fixture / "mcp-server" / "AGENTS.md"
            guidance.write_text(
                guidance.read_text(encoding="utf-8").replace(
                    "## Security boundaries",
                    "## Removed security boundaries",
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ApplicationContractError,
                r"mcp-server/AGENTS\.md: missing guidance section '## Security boundaries'",
            ):
                audit_repository(fixture)

    def test_documented_command_smokes_execute_from_unrelated_directory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb documented commands ") as temp:
            output = Path(temp) / "application-report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(APPLICATION_ENTRY),
                    "--root",
                    str(ROOT),
                    "--check",
                    "--smoke-commands",
                    "--output",
                    str(output),
                ],
                cwd=Path(temp),
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(report["documented_commands_pass"])
            self.assertEqual(
                {item["platform"] for item in report["documented_commands"]},
                {"windows" if os.name == "nt" else "posix"},
            )
            self.assertEqual(
                [item["id"] for item in report["applications"]],
                ["root-plugin", "mcp-server"],
            )


class AggregateRunnerTests(unittest.TestCase):
    def test_two_failures_preserve_later_diagnostics_skips_and_reruns(self) -> None:
        calls: list[str] = []

        def execute(stage: Stage) -> int:
            calls.append(stage.name)
            return {"format": 3, "test": 7}.get(stage.name, 0)

        stages = (
            Stage("format", ("quality-gate", "format"), "quality-gate format"),
            Stage("lint", ("quality-gate", "lint"), "quality-gate lint"),
            Stage("typecheck", ("quality-gate", "typecheck"), "quality-gate typecheck"),
            Stage("test", ("quality-gate", "test"), "quality-gate test"),
            Stage(
                "coverage",
                ("coverage",),
                "quality-gate test",
                dependencies=("test",),
            ),
            Stage("security", ("quality-gate", "security"), "quality-gate security"),
            Stage("package", ("quality-gate", "package"), "quality-gate package"),
        )
        report = AggregateRunner(stages, execute=execute).run()
        self.assertEqual(
            calls,
            ["format", "lint", "typecheck", "test", "security", "package"],
        )
        self.assertEqual(report.exit_code, 1)
        self.assertEqual(report.failed, ("format", "test"))
        self.assertEqual(report.skipped, ("coverage",))
        self.assertEqual(
            report.rerun_commands,
            ("quality-gate format", "quality-gate test"),
        )
        self.assertIn("dependency failed: test", report.results[4].diagnostic)
        self.assertTrue(all(result.duration_ns >= 0 for result in report.results))


class LegacyCompatibilityTests(unittest.TestCase):
    def test_forced_cp1252_forwards_unicode_and_writes_complete_reports(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb legacy utf8 ") as temp:
            temporary = Path(temp)
            fixture = temporary / "checkout with spaces"
            fixture.mkdir()
            stdout_marker = "suite stdout: ⊘ 雪 Ω"
            stderr_marker = "suite stderr: ↳ 火 λ"
            later_marker = "later suite: ✓"
            failure_source = (
                "import os; "
                'os.write(1, "suite stdout: \\u2298 \\u96ea \\u03a9\\n".encode("utf-8")); '
                'os.write(2, "suite stderr: \\u21b3 \\u706b \\u03bb\\n".encode("utf-8")); '
                "raise SystemExit(7)"
            )
            later_source = 'import os; os.write(1, "later suite: \\u2713\\n".encode("utf-8"))'
            manifest = fixture / "suites.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": "1",
                        "suites": [
                            {
                                "id": "unicode-failure",
                                "command": ["{python}", "-c", failure_source],
                                "portable": True,
                            },
                            {
                                "id": "later-pass",
                                "command": ["{python}", "-c", later_source],
                                "portable": True,
                            },
                            {
                                "id": "posix-only",
                                "command": ["bash", "-c", "exit 0"],
                                "portable": False,
                                "skip_reason": "posix-bash-only",
                            },
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            environment = os.environ.copy()
            environment["PYTHONIOENCODING"] = "cp1252:strict"
            environment["PYTHONUTF8"] = "0"
            environment.pop("ENGINEERING_BOARD_NATIVE_SHELL", None)
            fingerprints: list[tuple[str, str]] = []

            for shell_name in ("powershell", "cmd"):
                environment["ENGINEERING_BOARD_SUPPORT_ROW"] = f"windows-x86_64-{shell_name}"
                report_path = temporary / f"{shell_name}.json"
                result = subprocess.run(
                    [
                        sys.executable,
                        str(LEGACY_ENTRY),
                        "--root",
                        str(fixture),
                        "--manifest",
                        str(manifest),
                        "--portable-only",
                        "--report",
                        str(report_path),
                        "--state-root",
                        str(temporary / f"{shell_name}-locks"),
                    ],
                    cwd=temporary,
                    env=environment,
                    capture_output=True,
                    check=False,
                )

                self.assertEqual(result.returncode, 1, result.stderr.decode("utf-8"))
                stdout = result.stdout.decode("utf-8")
                stderr = result.stderr.decode("utf-8")
                self.assertEqual(result.stdout.count((stdout_marker + "\n").encode()), 1)
                self.assertEqual(result.stderr.count((stderr_marker + "\n").encode()), 1)
                self.assertIn(later_marker, stdout)
                self.assertNotIn("\ufffd", stdout + stderr)
                self.assertTrue(report_path.is_file())
                self.assertEqual(
                    list(temporary.glob(f".{report_path.name}.*")),
                    [],
                )

                report = json.loads(report_path.read_text(encoding="utf-8"))
                self.assertEqual(report["native_shell"], shell_name)
                self.assertEqual(report["passed"], 1)
                self.assertEqual(report["failed"], 1)
                self.assertEqual(report["skipped"], 1)
                self.assertEqual(report["suite_count"], 3)
                self.assertEqual(
                    [(item["id"], item["status"], item["exit_code"]) for item in report["results"]],
                    [
                        ("unicode-failure", "failed", 7),
                        ("later-pass", "passed", 0),
                        ("posix-only", "skipped", None),
                    ],
                )
                self.assertEqual(
                    report["results"][0]["rerun_command"],
                    " ".join([sys.executable, "-c", failure_source]),
                )
                self.assertEqual(report["repository_status_before"], "")
                self.assertEqual(report["repository_status_after"], "")
                self.assertTrue(report["repository_clean"])
                self.assertFalse(report["overall_pass"])
                fingerprints.append(
                    (
                        report["normalized_decision_fingerprint"],
                        report["artifact_fingerprint"],
                    )
                )

            self.assertEqual(fingerprints[0], fingerprints[1])

    def test_portable_runner_accepts_spaced_root_continues_and_is_repeatable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb legacy portable ") as temp:
            temporary = Path(temp)
            fixture = temporary / "checkout with spaces"
            fixture.mkdir()
            manifest = fixture / "suites.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": "1",
                        "suites": [
                            {
                                "id": "first-failure",
                                "command": [
                                    "{python}",
                                    "-c",
                                    "import sys; print('first root cause'); sys.exit(5)",
                                ],
                                "portable": True,
                            },
                            {
                                "id": "later-pass",
                                "command": [
                                    "{python}",
                                    "-c",
                                    "print('later diagnostic preserved')",
                                ],
                                "portable": True,
                            },
                            {
                                "id": "posix-only",
                                "command": ["bash", "-c", "exit 0"],
                                "portable": False,
                                "skip_reason": "posix-bash-only",
                            },
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            reports = []
            for index in (1, 2):
                report = temporary / f"report-{index}.json"
                result = subprocess.run(
                    [
                        sys.executable,
                        str(LEGACY_ENTRY),
                        "--root",
                        str(fixture),
                        "--manifest",
                        str(manifest),
                        "--portable-only",
                        "--report",
                        str(report),
                    ],
                    cwd=temporary,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("first root cause", result.stdout)
                self.assertIn("later diagnostic preserved", result.stdout)
                self.assertIn("[SKIP] posix-only: posix-bash-only", result.stdout)
                reports.append(json.loads(report.read_text(encoding="utf-8")))

            self.assertEqual(
                reports[0]["normalized_decision_fingerprint"],
                reports[1]["normalized_decision_fingerprint"],
            )
            self.assertEqual(
                reports[0]["artifact_fingerprint"],
                reports[1]["artifact_fingerprint"],
            )
            self.assertEqual(reports[0]["repository_status_before"], "")
            self.assertEqual(reports[0]["repository_status_after"], "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
