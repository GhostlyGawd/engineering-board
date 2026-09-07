#!/usr/bin/env python3
"""Pinned bootstrap and devcontainer contract regressions."""

from __future__ import annotations

import hashlib
import json
import ntpath
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts import bootstrap_ci_evidence, bootstrap_dev

MANIFEST = ROOT / "support" / "dev-tools" / "toolchain.json"
DEVCONTAINER = ROOT / ".devcontainer" / "devcontainer.json"
DOCKERFILE = ROOT / ".devcontainer" / "Dockerfile"
TOOLCHAIN_SELECTOR = ROOT / ".devcontainer" / "select-toolchain.sh"
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
        self.assertEqual(value["python_runtimes"], ["3.8.20", "3.14.7"])
        self.assertEqual(value["python_version"], value["python_runtimes"][-1])
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
        self.assertEqual(
            {
                artifact["id"]
                for artifact in value["artifacts"]
                if artifact["platform"] == "linux-arm64"
            },
            {"node", "syft", "uv"},
        )

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
            self.assertIn(bootstrap_dev.recovery_command(), result.stderr)
            self.assertEqual(before, after)
            self.assertFalse((install_root / ".complete.json").exists())

    def test_native_windows_recovery_uses_python_entry_point(self) -> None:
        with mock.patch.object(bootstrap_dev.platform, "system", return_value="Windows"):
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
        with tempfile.TemporaryDirectory(prefix="eb bootstrap windows recovery ") as temp:
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

    def test_linux_arm64_platform_key_requires_exact_declared_posix_root(
        self,
    ) -> None:
        canonical = "/opt/engineering-board-runtime/linux-arm64"
        for machine in ("arm64", "aarch64"):
            with (
                self.subTest(machine=machine, configured=canonical),
                mock.patch.dict(
                    os.environ,
                    {"ENGINEERING_BOARD_DEV_TOOLS": canonical},
                    clear=False,
                ),
                mock.patch.object(
                    bootstrap_dev.platform,
                    "system",
                    return_value="Linux",
                ),
                mock.patch.object(
                    bootstrap_dev.platform,
                    "machine",
                    return_value=machine,
                ),
                mock.patch.object(
                    bootstrap_dev,
                    "Path",
                    side_effect=AssertionError("platform declaration used host-native Path"),
                ),
            ):
                self.assertEqual(bootstrap_dev.platform_key(), "linux-arm64")

        rejected_roots = (
            "",
            r"\opt\engineering-board-runtime\linux-arm64",
            r"C:\opt\engineering-board-runtime\linux-arm64",
            "opt/engineering-board-runtime/linux-arm64",
            "/opt/engineering-board-runtime/./linux-arm64",
            "/opt/engineering-board-runtime/linux-arm64/..",
            "/opt/engineering-board-runtime/linux-arm64/",
            "/tmp/linux-arm64",
        )
        for machine in ("arm64", "aarch64"):
            for configured in rejected_roots:
                with (
                    self.subTest(machine=machine, configured=configured),
                    mock.patch.dict(
                        os.environ,
                        {"ENGINEERING_BOARD_DEV_TOOLS": configured},
                        clear=False,
                    ),
                    mock.patch.object(
                        bootstrap_dev.platform,
                        "system",
                        return_value="Linux",
                    ),
                    mock.patch.object(
                        bootstrap_dev.platform,
                        "machine",
                        return_value=machine,
                    ),
                    mock.patch.object(
                        bootstrap_dev,
                        "Path",
                        side_effect=AssertionError("platform declaration used host-native Path"),
                    ),
                    self.assertRaisesRegex(
                        bootstrap_dev.BootstrapError,
                        f"unsupported bootstrap host Linux/{machine}",
                    ),
                ):
                    bootstrap_dev.platform_key()

    def test_declared_devcontainer_roots_use_posix_semantics_on_every_host(
        self,
    ) -> None:
        for root in (
            bootstrap_dev.DEVCONTAINER_LINUX_ARM64_ROOT,
            bootstrap_dev.DEVCONTAINER_LINUX_X86_64_ROOT,
        ):
            with self.subTest(root=root):
                self.assertIs(type(root), PurePosixPath)
                self.assertTrue(root.is_absolute())
                self.assertEqual(str(root), root.as_posix())
                self.assertEqual(ntpath.normpath(str(root)), str(root).replace("/", "\\"))

    def test_python_38_parses_posix_devcontainer_declarations(self) -> None:
        manifest = bootstrap_dev.load_manifest(MANIFEST)
        configured = os.environ.get("ENGINEERING_BOARD_DEV_TOOLS")
        install_root = (
            Path(configured).expanduser().resolve()
            if configured
            else ROOT / ".engineering-board" / "dev-tools"
        )
        selected_platform = bootstrap_dev.platform_key()
        uv = bootstrap_dev._provider_command(
            next(tool for tool in manifest["tools"] if tool["id"] == "uv"),
            install_root,
            selected_platform,
        )
        environment = os.environ.copy()
        environment.update(
            {
                "UV_PYTHON_DOWNLOADS": "never",
                "UV_PYTHON_INSTALL_DIR": str(install_root / "python"),
            }
        )
        located = subprocess.run(
            [str(uv), "python", "find", "3.8.20"],
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(located.returncode, 0, located.stdout + located.stderr)
        probe = subprocess.run(
            [
                located.stdout.strip(),
                "-c",
                (
                    "import runpy;"
                    f"values=runpy.run_path({str(ROOT / 'scripts' / 'bootstrap_dev.py')!r});"
                    "roots=(values['DEVCONTAINER_LINUX_ARM64_ROOT'],"
                    "values['DEVCONTAINER_LINUX_X86_64_ROOT']);"
                    "assert all(type(root).__name__ == 'PurePosixPath' for root in roots);"
                    "assert [str(root) for root in roots] == "
                    "['/opt/engineering-board-runtime/linux-arm64',"
                    "'/opt/engineering-board-runtime/linux-x86_64']"
                ),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(probe.returncode, 0, probe.stdout + probe.stderr)

    def test_deferred_checks_are_bounded_to_the_emulated_devcontainer_build(
        self,
    ) -> None:
        rejected = self.run_cli(
            "--defer-executable-checks",
            "--install-root",
            "/tmp/linux-x86_64",
        )
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("--defer-executable-checks", rejected.stderr)
        self.assertIn(
            "/opt/engineering-board-runtime/linux-x86_64",
            rejected.stderr,
        )
        self.assertNotIn(
            r"\opt\engineering-board-runtime\linux-x86_64",
            rejected.stderr,
        )

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
        self.assertEqual(config["postCreateCommand"], "bash scripts/bootstrap-dev.sh --check")
        self.assertEqual(config["build"]["dockerfile"], "Dockerfile")
        self.assertEqual(config["build"]["context"], "..")
        self.assertNotIn("options", config["build"])
        self.assertEqual(
            config["containerEnv"]["ENGINEERING_BOARD_DEV_TOOLS"],
            "/opt/engineering-board-runtime/current",
        )

        dockerfile = DOCKERFILE.read_text(encoding="utf-8")
        self.assertNotIn(":latest", dockerfile)
        self.assertGreaterEqual(dockerfile.count("@sha256:"), 3)
        self.assertIn("USER vscode", dockerfile)
        self.assertIn("GIT_CONFIG_KEY_0=safe.directory", dockerfile)
        self.assertIn("GIT_CONFIG_VALUE_0=/workspaces/engineering-board", dockerfile)
        self.assertIn("PYTHONDONTWRITEBYTECODE=1", dockerfile)
        self.assertIn('ENTRYPOINT ["/usr/local/bin/select-toolchain.sh"]', dockerfile)
        self.assertNotIn(".config/engineering-board", dockerfile)
        self.assertNotIn("github-app.pem", dockerfile)

    def test_devcontainer_arm64_toolchain_is_pinned_and_architecture_bounded(
        self,
    ) -> None:
        dockerfile = DOCKERFILE.read_text(encoding="utf-8")
        selector = TOOLCHAIN_SELECTOR.read_text(encoding="utf-8")
        for digest in (
            "a110e01da17f27ebb99b4ae5d8fab540071fcf7bc906b2c8df29c925bb5d9e36",
            "9e7720738fbcb12e8122beb5194cfa58ab0029c78c3ed39f8986aa68713e31bc",
            "4290d77f2efb22105839727af2a816a0aaba3ace690a10afd806e654bd78b1d3",
        ):
            self.assertIn(digest, dockerfile)
        self.assertGreaterEqual(dockerfile.count("FROM --platform=linux/arm64"), 3)
        self.assertGreaterEqual(dockerfile.count("FROM --platform=linux/amd64"), 3)
        self.assertIn("/opt/engineering-board-runtime/linux-arm64", dockerfile)
        self.assertIn("/opt/engineering-board-runtime/linux-x86_64", dockerfile)
        self.assertIn("/opt/engineering-board-native/usr/bin", dockerfile)
        self.assertIn("/proc/cpuinfo", selector)
        self.assertIn("asimd", selector)
        self.assertIn("linux-arm64", selector)
        self.assertIn("linux-x86_64", selector)
        self.assertIn("/opt/engineering-board-native/usr/bin", selector)
        self.assertIn(
            "GIT_EXEC_PATH=/opt/engineering-board-native/usr/lib/git-core",
            selector,
        )
        self.assertIn(
            'PATH="${runtime_root}/current/bin:'
            "${runtime_root}/current/python-tools/bin:"
            "${runtime_root}/current/node/bin:"
            "${runtime_root}/current/node-tools/node_modules/.bin"
            '${native_path:+:${native_path}}:${PATH}"',
            selector,
        )
        self.assertIn("--defer-executable-checks", dockerfile)
        self.assertIn("ln -sfn", selector)

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
                "usage: bootstrap_dev.py\nunrecognized arguments: --not-a-bootstrap-option",
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
        self.assertIn(
            "ref: ${{ github.event.pull_request.head.sha || github.sha }}",
            workflow,
        )
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
        self.assertIn(
            "ref: ${{ github.event.pull_request.head.sha || github.sha }}",
            workflow,
        )
        self.assertIn("scripts/aggregate_ci_evidence.py", workflow)
        self.assertIn(
            ".engineering-board/validation/aggregate/run-all.json",
            workflow,
        )
        self.assertIn("aggregate-result-linux-x86_64-bash", workflow)
        self.assertIn("if: always()", workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
