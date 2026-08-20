#!/usr/bin/env python3
"""Pinned bootstrap and devcontainer contract regressions."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts import bootstrap_ci_evidence, bootstrap_dev

MANIFEST = ROOT / "support" / "dev-tools" / "toolchain.json"
DEVCONTAINER = ROOT / ".devcontainer" / "devcontainer.json"
DOCKERFILE = ROOT / ".devcontainer" / "Dockerfile"
WINDOWS_WORKFLOW = ROOT / ".github" / "workflows" / "windows.yml"
TEST_WORKFLOW = ROOT / ".github" / "workflows" / "test.yml"
EXPECTED_TOOLS = {
    "actionlint",
    "check-jsonschema",
    "coverage",
    "cyclonedx-py",
    "jscpd",
    "markdownlint-cli2",
    "mypy",
    "node",
    "npm",
    "pip-audit",
    "pre-commit",
    "pyright",
    "pytest",
    "python",
    "radon",
    "ruff",
    "shellcheck",
    "shfmt",
    "syft",
    "uv",
    "vulture",
    "yamllint",
    "zizmor",
}


def tree_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    if not root.exists():
        return digest.hexdigest()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


class BootstrapManifestTests(unittest.TestCase):
    def test_manifest_is_complete_and_fully_pinned(self) -> None:
        value = bootstrap_dev.load_manifest(MANIFEST)
        self.assertEqual(value["schema_version"], "1")
        tools = value["tools"]
        self.assertEqual({tool["id"] for tool in tools}, EXPECTED_TOOLS)
        self.assertEqual(len(tools), len(EXPECTED_TOOLS))
        for tool in tools:
            self.assertRegex(tool["version"], r"^[0-9]+(?:\.[0-9]+){1,3}$")
            self.assertNotIn("latest", json.dumps(tool).lower())
        for artifact in value["artifacts"]:
            self.assertRegex(artifact["sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(artifact["url"].startswith("https://"))
            self.assertNotIn("/latest/", artifact["url"])

    def test_mcp_runtime_metadata_remains_dependency_free(self) -> None:
        pyproject = (ROOT / "mcp-server" / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("dependencies = []", pyproject)
        self.assertNotIn("support/dev-tools", pyproject)


class BootstrapCliTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "bootstrap_dev.py"), *arguments],
            cwd=ROOT.parent,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_help_and_unknown_option_are_actionable(self) -> None:
        help_result = self.run_cli("--help")
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("--check", help_result.stdout)
        self.assertIn("--install-root", help_result.stdout)

        rejected = self.run_cli("--not-a-bootstrap-option")
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("--not-a-bootstrap-option", rejected.stderr)
        self.assertIn("usage:", rejected.stderr.lower())

    def test_missing_installation_names_exact_recovery_without_marker(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb bootstrap missing ") as temp:
            install_root = Path(temp) / "tool root"
            before = tree_fingerprint(install_root)
            result = self.run_cli("--check", "--install-root", str(install_root))
            after = tree_fingerprint(install_root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("development toolchain is not installed", result.stderr)
            self.assertIn("bash scripts/bootstrap-dev.sh", result.stderr)
            self.assertEqual(before, after)
            self.assertFalse((install_root / ".complete.json").exists())

    def test_native_windows_recovery_uses_python_entry_point(self) -> None:
        with mock.patch.object(
            bootstrap_dev.platform, "system", return_value="Windows"
        ):
            self.assertEqual(
                bootstrap_dev.recovery_command(),
                "python scripts/bootstrap_dev.py",
            )
        with mock.patch.object(bootstrap_dev.platform, "system", return_value="Darwin"):
            self.assertEqual(
                bootstrap_dev.recovery_command(),
                "bash scripts/bootstrap-dev.sh",
            )

        manifest = bootstrap_dev.load_manifest(MANIFEST)
        with tempfile.TemporaryDirectory(
            prefix="eb bootstrap windows recovery "
        ) as temp:
            install_root = Path(temp)
            with (
                mock.patch.object(
                    bootstrap_dev.platform,
                    "system",
                    return_value="Windows",
                ),
                self.assertRaisesRegex(
                    bootstrap_dev.BootstrapError,
                    r"run: python scripts/bootstrap_dev\.py",
                ),
            ):
                bootstrap_dev.check_installation(ROOT, install_root, manifest)

    def test_check_is_network_free_and_read_only(self) -> None:
        manifest = bootstrap_dev.load_manifest(MANIFEST)
        expected = {tool["id"]: tool["version"] for tool in manifest["tools"]}
        with tempfile.TemporaryDirectory(prefix="eb bootstrap check ") as temp:
            install_root = Path(temp)
            marker = install_root / ".complete.json"
            marker.write_text(
                json.dumps(
                    {
                        "schema_version": "1",
                        "manifest_sha256": bootstrap_dev.file_sha256(MANIFEST),
                        "platform": bootstrap_dev.platform_key(),
                    },
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            before = tree_fingerprint(install_root)

            def fake_run(tool: dict[str, object], _: Path) -> str:
                return str(expected[str(tool["id"])])

            with mock.patch.object(
                bootstrap_dev,
                "download_artifact",
                side_effect=AssertionError("check attempted network access"),
            ):
                inventory = bootstrap_dev.check_installation(
                    ROOT,
                    install_root,
                    manifest,
                    command_runner=fake_run,
                )
            after = tree_fingerprint(install_root)
            self.assertEqual(inventory, expected)
            self.assertEqual(before, after)


class DevcontainerContractTests(unittest.TestCase):
    def test_devcontainer_uses_pinned_image_and_workspace_contract(self) -> None:
        config = json.loads(DEVCONTAINER.read_text(encoding="utf-8"))
        self.assertEqual(config["workspaceFolder"], "/workspaces/engineering-board")
        self.assertEqual(config["remoteUser"], "vscode")
        self.assertEqual(
            config["postCreateCommand"], "bash scripts/bootstrap-dev.sh --check"
        )
        self.assertEqual(config["build"]["dockerfile"], "Dockerfile")
        self.assertEqual(config["build"]["context"], "..")

        dockerfile = DOCKERFILE.read_text(encoding="utf-8")
        self.assertNotIn(":latest", dockerfile)
        self.assertGreaterEqual(dockerfile.count("@sha256:"), 3)
        self.assertIn("USER vscode", dockerfile)
        self.assertNotIn(".config/engineering-board", dockerfile)
        self.assertNotIn("github-app.pem", dockerfile)

    def test_docker_context_excludes_private_and_host_runtime_files(self) -> None:
        dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
        for pattern in (
            ".git",
            ".engineering-board",
            ".env",
            "*.pem",
            "*.key",
            ".DS_Store",
        ):
            self.assertIn(pattern, dockerignore)


class WorkflowEvidenceContractTests(unittest.TestCase):
    def test_windows_evidence_manifest_records_required_decisions(self) -> None:
        inventory = json.dumps({"python": "3.14.0", "ruff": "0.12.12"}) + "\n"
        results = [
            subprocess.CompletedProcess([], 0, inventory, ""),
            subprocess.CompletedProcess([], 0, inventory, ""),
            subprocess.CompletedProcess([], 0, inventory, ""),
            subprocess.CompletedProcess([], 0, inventory, ""),
            subprocess.CompletedProcess(
                [],
                2,
                "",
                (
                    "bootstrap-dev: development toolchain is not installed; "
                    "run: python scripts/bootstrap_dev.py"
                ),
            ),
            subprocess.CompletedProcess(
                [],
                2,
                "",
                "usage: bootstrap_dev.py\nunrecognized arguments: "
                "--not-a-bootstrap-option",
            ),
        ]
        with tempfile.TemporaryDirectory(prefix="eb windows evidence ") as temp:
            output = Path(temp) / "powershell.json"
            with (
                mock.patch.object(
                    sys,
                    "argv",
                    [
                        "bootstrap_ci_evidence.py",
                        "--shell",
                        "powershell",
                        "--output",
                        str(output),
                    ],
                ),
                mock.patch.object(
                    bootstrap_ci_evidence,
                    "_run",
                    side_effect=results,
                ),
                mock.patch.object(
                    bootstrap_ci_evidence,
                    "_git",
                    side_effect=["", "a" * 40, ""],
                ),
                mock.patch.object(
                    bootstrap_ci_evidence,
                    "_clone_checkout",
                    return_value=subprocess.CompletedProcess([], 0, "", ""),
                ),
                mock.patch.object(
                    bootstrap_ci_evidence,
                    "_git_at",
                    side_effect=["", ""],
                ),
                mock.patch.object(
                    bootstrap_ci_evidence.platform,
                    "system",
                    return_value="Windows",
                ),
            ):
                exit_code = bootstrap_ci_evidence.main()

            evidence = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 0)
            self.assertTrue(evidence["overall_pass"])
            self.assertEqual(evidence["source_commit"], "a" * 40)
            self.assertEqual(evidence["native_shell"], "powershell")
            self.assertEqual(
                [stage["exit_code"] for stage in evidence["stages"]],
                [0, 0, 0, 0, 2, 2],
            )
            self.assertEqual(
                [stage["name"] for stage in evidence["stages"]],
                [
                    "clean-install",
                    "offline-read-only-check",
                    "spaced-checkout-offline-check",
                    "second-bootstrap",
                    "missing-installation",
                    "unknown-option",
                ],
            )
            self.assertEqual(
                len({stage["inventory_sha256"] for stage in evidence["stages"][:4]}),
                1,
            )

    def test_windows_workflow_retains_complete_bootstrap_evidence(self) -> None:
        workflow = WINDOWS_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("push:\n    branches: [main]", workflow)
        self.assertIn("scripts/bootstrap_ci_evidence.py", workflow)
        self.assertIn("--shell powershell", workflow)
        self.assertIn("--shell cmd", workflow)
        self.assertIn(
            ".engineering-board/validation/bootstrap/*.json",
            workflow,
        )
        self.assertIn(
            ".engineering-board/validation/platform/*.json",
            workflow,
        )
        self.assertIn("foundation-windows-evidence-${{ matrix.support_row }}", workflow)
        self.assertIn("retention-days:", workflow)

    def test_aggregate_workflow_retains_exact_head_result(self) -> None:
        workflow = TEST_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("push:\n    branches: [main]", workflow)
        self.assertIn("scripts/aggregate_ci_evidence.py", workflow)
        self.assertIn(
            ".engineering-board/validation/aggregate/run-all.json",
            workflow,
        )
        self.assertIn("aggregate-result-linux-x86_64-bash", workflow)
        self.assertIn("if: always()", workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
