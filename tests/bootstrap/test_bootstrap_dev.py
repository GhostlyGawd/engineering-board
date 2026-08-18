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

from scripts import bootstrap_dev

MANIFEST = ROOT / "support" / "dev-tools" / "toolchain.json"
DEVCONTAINER = ROOT / ".devcontainer" / "devcontainer.json"
DOCKERFILE = ROOT / ".devcontainer" / "Dockerfile"
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
