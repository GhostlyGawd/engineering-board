#!/usr/bin/env python3
"""Quality command contract regressions."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from quality_checks import QualityRunner  # noqa: E402


PYTHON_ENTRY = ROOT / "scripts" / "quality_gate.py"
BASH_ENTRY = ROOT / "scripts" / "quality-gate.sh"
STABLE_SELECTORS = ("format", "lint", "typecheck", "test", "security", "package", "all")
PINNED_TOOLS = ROOT / ".engineering-board" / "dev-tools"


class QualityCommandContractTests(unittest.TestCase):
    def run_python(
        self,
        *arguments: str,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(PYTHON_ENTRY), *arguments],
            cwd=ROOT,
            env=environment,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )

    def run_bash(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(BASH_ENTRY), *arguments],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )

    def run_fixture(
        self,
        fixture: Path,
        selector: str,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["ENGINEERING_BOARD_DEV_TOOLS"] = str(PINNED_TOOLS)
        return self.run_python(
            "--root",
            str(fixture),
            selector,
            environment=environment,
        )

    def test_help_is_discoverable_and_equivalent(self) -> None:
        python_help = self.run_python("--help")
        self.assertEqual(python_help.returncode, 0, python_help.stderr)
        if os.name != "nt":
            bash_help = self.run_bash("--help")
            self.assertEqual(bash_help.returncode, 0, bash_help.stderr)
            self.assertEqual(bash_help.stdout, python_help.stdout)
        for selector in STABLE_SELECTORS:
            self.assertIn(selector, python_help.stdout)
        self.assertIn("--workers", python_help.stdout)
        self.assertIn("PowerShell", python_help.stdout)
        self.assertIn("cmd.exe", python_help.stdout)

    def test_guidance_matrix_and_application_inventory_are_exact(self) -> None:
        bash_commands = [
            "bash scripts/quality-gate.sh format",
            "bash scripts/quality-gate.sh lint",
            "bash scripts/quality-gate.sh typecheck",
            "bash scripts/quality-gate.sh test --workers 2",
            "bash scripts/quality-gate.sh security",
            "bash scripts/quality-gate.sh package",
            "bash scripts/quality-gate.sh all --workers 2",
            "bash tests/run-all.sh",
        ]
        guidance = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                ROOT / "AGENTS.md",
                ROOT / "CONTRIBUTING.md",
                ROOT / "README.md",
                ROOT / "docs" / "SUPPORTED_PLATFORMS.md",
            )
        )
        for command in bash_commands:
            self.assertIn(command, guidance)
        self.assertIn("python scripts/quality_gate.py lint", guidance)
        self.assertIn(r"python scripts\quality_gate.py lint", guidance)
        self.assertIn("coverage invocation", guidance)
        self.assertIn("Git Bash", guidance)
        self.assertIn("WSL", guidance)

        matrix = json.loads((ROOT / "support" / "platform-matrix.json").read_text(encoding="utf-8"))
        expected_surfaces = {
            "format",
            "lint",
            "package",
            "quality-all",
            "quality-test",
            "security",
            "typecheck",
        }
        for row in matrix["platforms"]:
            surfaces = {surface["id"]: surface["command"] for surface in row["surfaces"]}
            self.assertTrue(expected_surfaces <= surfaces.keys(), row["id"])
            if row["os"]["family"] == "windows":
                self.assertTrue(
                    all(
                        "quality_gate.py" in surfaces[surface]
                        and "bash" not in surfaces[surface].lower()
                        for surface in expected_surfaces
                    )
                )
            else:
                self.assertTrue(
                    all(
                        "bash scripts/quality-gate.sh" in surfaces[surface]
                        for surface in expected_surfaces
                    )
                )

        policy = json.loads(
            (ROOT / "support" / "quality" / "typing-policy.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [application["id"] for application in policy["applications"]],
            ["root-plugin", "mcp-server"],
        )
        self.assertIn(
            "mcp-server/engineering_board_core.py",
            policy["applications"][1]["typed_paths"],
        )
        wrapper = BASH_ENTRY.read_text(encoding="utf-8")
        self.assertIn('exec python3 "$SCRIPT_DIR/quality_gate.py" "$@"', wrapper)

    def test_standing_ci_workflows_are_bounded_to_validation_events(self) -> None:
        for workflow_name in ("test.yml", "windows.yml"):
            with self.subTest(workflow=workflow_name):
                workflow = (ROOT / ".github" / "workflows" / workflow_name).read_text(
                    encoding="utf-8"
                )
                self.assertIn(
                    "  pull_request:\n    types: [opened, synchronize]\n",
                    workflow,
                )
                self.assertIn("\npermissions:\n  contents: read\n", workflow)
                self.assertNotIn("pull_request_target", workflow)
                self.assertNotIn("\n    secrets:", workflow)
                self.assertNotIn("\n    environment:", workflow)

    def test_long_tool_inputs_are_batched_with_utf8_output(self) -> None:
        runner = QualityRunner.__new__(QualityRunner)
        runner.root = ROOT
        runner.environment = {}
        items = [f"docs/{number:03d}-{'x' * 25}.md" for number in range(12)]
        completed = subprocess.CompletedProcess([], 0, "", "")
        with (
            mock.patch.object(runner, "_stage"),
            mock.patch("quality_checks.subprocess.run", return_value=completed) as run,
        ):
            runner._run_batched(
                "markdown-format",
                ["markdownlint-cli2", "--config", "support/quality/markdownlint.jsonc"],
                items,
                max_command_chars=160,
            )

        self.assertGreater(run.call_count, 1)
        flattened: list[str] = []
        for call in run.call_args_list:
            command = call.args[0]
            self.assertLessEqual(sum(len(value) + 3 for value in command), 160)
            self.assertEqual(call.kwargs["encoding"], "utf-8")
            self.assertEqual(call.kwargs["errors"], "replace")
            flattened.extend(command[3:])
        self.assertEqual(flattened, items)

    def test_clean_format_lint_type_security_and_package_selectors_pass(self) -> None:
        environment = os.environ.copy()
        environment["ENGINEERING_BOARD_DEV_TOOLS"] = str(PINNED_TOOLS)
        for selector in ("format", "lint", "typecheck", "security", "package"):
            with self.subTest(selector=selector):
                result = self.run_python(selector, environment=environment)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(
                    f"quality-gate: selector {selector} passed",
                    result.stdout,
                )

    def test_invalid_invocations_start_no_stage_or_artifact(self) -> None:
        invalid = (
            (),
            ("unknown-selector",),
            ("lint", "--not-a-quality-option"),
            ("test", "--workers"),
            ("test", "--workers", "0"),
            ("test", "--workers", "-1"),
            ("test", "--workers", "many"),
            ("lint", "--workers", "2"),
        )
        validation_before = self.tree_digest(ROOT / ".engineering-board" / "validation")
        dist_before = self.tree_digest(ROOT / "dist")
        with tempfile.TemporaryDirectory(prefix="eb quality invalid ") as temp:
            temp_root = Path(temp)
            for index, arguments in enumerate(invalid):
                with self.subTest(arguments=arguments):
                    stage_log = temp_root / f"stage-{index}.log"
                    environment = os.environ.copy()
                    environment["ENGINEERING_BOARD_QUALITY_STAGE_LOG"] = str(stage_log)
                    result = self.run_python(*arguments, environment=environment)
                    self.assertNotEqual(result.returncode, 0)
                    diagnostic = result.stderr
                    self.assertIn("usage:", diagnostic.lower())
                    if arguments:
                        invalid_value = arguments[-1]
                        self.assertIn(invalid_value, diagnostic)
                    self.assertFalse(stage_log.exists())
                    self.assertFalse((temp_root / ".engineering-board" / "validation").exists())
                    self.assertFalse((temp_root / "dist").exists())
        self.assertEqual(
            validation_before,
            self.tree_digest(ROOT / ".engineering-board" / "validation"),
        )
        self.assertEqual(dist_before, self.tree_digest(ROOT / "dist"))

    @staticmethod
    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def tree_digest(path: Path) -> str:
        digest = hashlib.sha256()
        if not path.exists():
            return digest.hexdigest()
        for child in sorted(path.rglob("*")):
            relative = child.relative_to(path).as_posix()
            digest.update(relative.encode("utf-8"))
            if child.is_file():
                digest.update(child.read_bytes())
        return digest.hexdigest()

    @staticmethod
    def copy_repository(destination: Path) -> Path:
        fixture = destination / "quality fixture"
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

    def assert_fixture_failure(
        self,
        fixture: Path,
        selector: str,
        paths: tuple[Path, ...],
        *tokens: str,
    ) -> None:
        before = {path: self.digest(path) for path in paths}
        result = self.run_fixture(fixture, selector)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        diagnostic = result.stdout + result.stderr
        for token in tokens:
            self.assertIn(token, diagnostic)
        after = {path: self.digest(path) for path in paths}
        self.assertEqual(before, after, f"{selector} rewrote a failing fixture")

    def test_representative_format_and_lint_violations_are_non_rewriting(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb quality families ") as temp:
            fixture = self.copy_repository(Path(temp))

            python_format = fixture / "scripts" / "format_fixture.py"
            python_format.write_text('value={"key":1}\n', encoding="utf-8")
            self.assert_fixture_failure(
                fixture,
                "format",
                (python_format,),
                "format_fixture.py",
                "would be reformatted",
            )
            python_format.unlink()

            shell_format = fixture / "scripts" / "format-fixture.sh"
            shell_format.write_text(
                "#!/usr/bin/env bash\nif true;then echo ok;fi\n",
                encoding="utf-8",
            )
            self.assert_fixture_failure(
                fixture,
                "format",
                (shell_format,),
                "format-fixture.sh",
                "quality-gate: shell-format failed",
            )
            shell_format.unlink()

            markdown = fixture / "docs" / "format-fixture.md"
            markdown.write_text("# Fixture \n", encoding="utf-8")
            self.assert_fixture_failure(
                fixture,
                "format",
                (markdown,),
                "format-fixture.md:1",
                "MD009",
            )
            markdown.unlink()

            yaml_path = fixture / "support" / "quality-fixture.yml"
            yaml_path.write_text("key:\n  broken: [\n", encoding="utf-8")
            self.assert_fixture_failure(
                fixture,
                "lint",
                (yaml_path,),
                "quality-fixture.yml",
                "syntax",
            )
            yaml_path.unlink()

            json_path = fixture / "support" / "quality-fixture.json"
            json_path.write_text('{"broken": }\n', encoding="utf-8")
            self.assert_fixture_failure(
                fixture,
                "lint",
                (json_path,),
                "quality-fixture.json",
                "Expecting value",
            )
            json_path.unlink()

            workflow = fixture / ".github" / "workflows" / "quality-fixture.yml"
            workflow.write_text(
                "name: broken\non: push\njobs:\n  build:\n    runs-on: ubuntu-latest\n"
                "    steps:\n      - run: ${{ unknown.context }}\n",
                encoding="utf-8",
            )
            self.assert_fixture_failure(
                fixture,
                "lint",
                (workflow,),
                "quality-fixture.yml",
                "undefined variable",
            )
            workflow.unlink()

            python_lint = fixture / "scripts" / "lint_fixture.py"
            python_lint.write_text("print(undefined_name)\n", encoding="utf-8")
            self.assert_fixture_failure(
                fixture,
                "lint",
                (python_lint,),
                "lint_fixture.py:1",
                "F821",
            )
            python_lint.unlink()

            shell_lint = fixture / "scripts" / "lint-fixture.sh"
            shell_lint.write_text(
                '#!/usr/bin/env bash\nif [ "$value" = ]; then\n  echo broken\nfi\n',
                encoding="utf-8",
            )
            self.assert_fixture_failure(
                fixture,
                "lint",
                (shell_lint,),
                "lint-fixture.sh",
                "SC",
            )
            shell_lint.unlink()

            naming = fixture / "scripts" / "BadName.py"
            naming.write_text('"""Naming fixture."""\n', encoding="utf-8")
            self.assert_fixture_failure(
                fixture,
                "lint",
                (naming,),
                "BadName.py",
                "file stem must match",
            )
            naming.unlink()

            complexity = fixture / "scripts" / "complexity_fixture.py"
            branches = "\n".join(
                f"    if value == {number}:\n        return {number}" for number in range(22)
            )
            complexity.write_text(
                '"""Complexity fixture."""\n\n'
                "def too_complex(value: int) -> int:\n"
                f"{branches}\n"
                "    return -1\n",
                encoding="utf-8",
            )
            self.assert_fixture_failure(
                fixture,
                "lint",
                (complexity,),
                "complexity_fixture.py",
                "threshold 20",
            )
            complexity.unlink()

            dead_code = fixture / "scripts" / "dead_code_fixture.py"
            dead_code.write_text(
                '"""Dead-code fixture."""\n\nif False:\n    print("unreachable")\n',
                encoding="utf-8",
            )
            self.assert_fixture_failure(
                fixture,
                "lint",
                (dead_code,),
                "dead_code_fixture.py",
                "unsatisfiable 'if' condition",
            )
            dead_code.unlink()

            duplicate_a = fixture / "scripts" / "duplicate_a.py"
            duplicate_b = fixture / "scripts" / "duplicate_b.py"
            duplicate_body = (
                '"""Duplicate fixture."""\n\n'
                "def normalize(value: int) -> int:\n"
                + "\n".join(f"    value += {number}" for number in range(25))
                + "\n    return value\n"
            )
            duplicate_a.write_text(duplicate_body, encoding="utf-8")
            duplicate_b.write_text(duplicate_body, encoding="utf-8")
            self.assert_fixture_failure(
                fixture,
                "lint",
                (duplicate_a, duplicate_b),
                "duplicate_a.py",
                "duplicate_b.py",
                "Clone found",
            )
            duplicate_a.unlink()
            duplicate_b.unlink()

            large_file = fixture / "scripts" / "large_file.py"
            large_file.write_text("#" * 250_001 + "\n", encoding="utf-8")
            self.assert_fixture_failure(
                fixture,
                "lint",
                (large_file,),
                "large_file.py",
                "measured",
                "threshold",
            )

    def test_type_errors_and_policy_broadening_fail(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb quality typing ") as temp:
            fixture = self.copy_repository(Path(temp))
            typed_path = fixture / "scripts" / "quality_gate.py"
            original = typed_path.read_text(encoding="utf-8")
            typed_path.write_text(
                original + '\n_injected_type_error: int = "wrong"\n',
                encoding="utf-8",
            )
            self.assert_fixture_failure(
                fixture,
                "typecheck",
                (typed_path,),
                "quality_gate.py",
                "Incompatible types",
            )
            typed_path.write_text(original, encoding="utf-8")

            policy_path = fixture / "support" / "quality" / "typing-policy.json"
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
            policy["applications"][0]["staged_exclusions"].append("scripts/quality_gate.py")
            policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
            self.assert_fixture_failure(
                fixture,
                "typecheck",
                (policy_path,),
                "typing-policy failed",
                "changed outside the approved policy",
            )


if __name__ == "__main__":
    unittest.main()
