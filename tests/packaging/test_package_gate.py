#!/usr/bin/env python3
"""Packaging contract regressions."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from package_gate import (  # noqa: E402
    PackageGateError,
    artifact_sbom,
    normalize_sdist,
    validate_archive_entries,
    validate_manifests,
    validate_sbom,
)


class PackageGateTests(unittest.TestCase):
    def test_sbom_is_deterministic_and_binds_artifact_digest(self) -> None:
        digest = hashlib.sha256(b"wheel bytes").hexdigest()
        first = artifact_sbom(
            artifact_name="engineering_board_mcp-1.13.4-py3-none-any.whl",
            artifact_kind="wheel",
            version="1.13.4",
            digest=digest,
        )
        second = artifact_sbom(
            artifact_name="engineering_board_mcp-1.13.4-py3-none-any.whl",
            artifact_kind="wheel",
            version="1.13.4",
            digest=digest,
        )
        self.assertEqual(first, second)
        value = json.loads(first)
        self.assertEqual(value["bomFormat"], "CycloneDX")
        self.assertEqual(
            value["metadata"]["component"]["hashes"],
            [{"alg": "SHA-256", "content": digest}],
        )
        validate_sbom(first, expected_digest=digest, expected_version="1.13.4")
        with self.assertRaisesRegex(PackageGateError, "SBOM artifact digest"):
            validate_sbom(
                first,
                expected_digest="0" * 64,
                expected_version="1.13.4",
            )

    def test_normalized_sdist_is_byte_reproducible(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb sdist normalize ") as temp:
            root = Path(temp)
            source = root / "source.tar.gz"
            with tarfile.open(source, "w:gz") as archive:
                for name, data in (
                    ("engineering_board_mcp-1.13.4/pyproject.toml", b"[project]\n"),
                    ("engineering_board_mcp-1.13.4/README.md", b"# Package\n"),
                ):
                    info = tarfile.TarInfo(name)
                    info.size = len(data)
                    info.mtime = 1_800_000_000
                    archive.addfile(info, io.BytesIO(data))
            first = root / "first.tar.gz"
            second = root / "second.tar.gz"
            normalize_sdist(source, first)
            normalize_sdist(source, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_archive_allowlists_reject_runtime_credentials_and_omissions(self) -> None:
        version = "1.13.4"
        wheel_entries = {
            "engineering_board_core.py",
            "engineering_board_mcp.py",
            "engineering_board_mcp-1.13.4.dist-info/METADATA",
            "engineering_board_mcp-1.13.4.dist-info/WHEEL",
            "engineering_board_mcp-1.13.4.dist-info/entry_points.txt",
            "engineering_board_mcp-1.13.4.dist-info/licenses/LICENSE",
            "engineering_board_mcp-1.13.4.dist-info/top_level.txt",
            "engineering_board_mcp-1.13.4.dist-info/RECORD",
        }
        validate_archive_entries("wheel", wheel_entries, version)
        for unexpected in (
            ".engineering-board/claims/private.json",
            "credentials/token.txt",
            ".env",
        ):
            with self.subTest(unexpected=unexpected):
                with self.assertRaisesRegex(PackageGateError, "unexpected archive entry"):
                    validate_archive_entries(
                        "wheel",
                        wheel_entries | {unexpected},
                        version,
                    )
        with self.assertRaisesRegex(PackageGateError, "missing archive entry"):
            validate_archive_entries(
                "wheel",
                wheel_entries - {"engineering_board_core.py"},
                version,
            )

    def test_mcp_bundle_allowlist_is_exact(self) -> None:
        entries = {
            "LICENSE",
            "manifest.json",
            "mcp-server/README.md",
            "mcp-server/engineering_board_core.py",
            "mcp-server/engineering_board_mcp.py",
        }
        validate_archive_entries("mcpb", entries, "1.13.4")
        with self.assertRaisesRegex(PackageGateError, "unexpected archive entry"):
            validate_archive_entries(
                "mcpb",
                entries | {"mcp-server/.engineering-board/runtime.json"},
                "1.13.4",
            )

    def test_manifest_validation_rejects_stale_versions_and_checksums(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb package manifest ") as temp:
            fixture = Path(temp) / "fixture"
            for relative in (
                ".claude-plugin/plugin.json",
                ".claude-plugin/marketplace.json",
                ".codex-plugin/plugin.json",
                ".agents/plugins/marketplace.json",
                "mcp-server/manifest.json",
                "mcp-server/server.json",
                "mcp-server/pyproject.toml",
                "mcp-server/LICENSE",
                "docs/evidence/2026-08-16-v1.13.4-release-and-installed-validation.md",
                "LICENSE",
            ):
                source = ROOT / relative
                target = fixture / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            self.assertEqual(validate_manifests(fixture), "1.13.4")

            codex = fixture / ".codex-plugin/plugin.json"
            original_codex = codex.read_text(encoding="utf-8")
            codex.write_text(
                original_codex.replace('"version": "1.13.4"', '"version": "9.9.9"'),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(PackageGateError, "Codex plugin version"):
                validate_manifests(fixture)
            codex.write_text(original_codex, encoding="utf-8")

            server = fixture / "mcp-server/server.json"
            value = json.loads(server.read_text(encoding="utf-8"))
            value["packages"][0]["fileSha256"] = "not-a-sha256"
            server.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(PackageGateError, "checksum is not SHA-256"):
                validate_manifests(fixture)

            value["packages"][0]["fileSha256"] = "0" * 64
            server.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(
                PackageGateError,
                "checksum does not match immutable release evidence",
            ):
                validate_manifests(fixture)


if __name__ == "__main__":
    unittest.main()
