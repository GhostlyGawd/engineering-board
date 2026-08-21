#!/usr/bin/env python3
"""Packaging contract regressions."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock
import zipfile


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import package_gate  # noqa: E402
import package_runtime  # noqa: E402
from package_gate import (  # noqa: E402
    PackageGateError,
    artifact_sbom,
    normalize_sdist,
    validate_archive_entries,
    validate_manifests,
    validate_sbom,
)

BACKEND_PATH = ROOT / "mcp-server" / "engineering_board_build_backend.py"
BACKEND_SPEC = importlib.util.spec_from_file_location(
    "engineering_board_build_backend_coverage",
    BACKEND_PATH,
)
if BACKEND_SPEC is None or BACKEND_SPEC.loader is None:
    raise RuntimeError(f"cannot load build backend from {BACKEND_PATH}")
build_backend = importlib.util.module_from_spec(BACKEND_SPEC)
BACKEND_SPEC.loader.exec_module(build_backend)


class PackageGateTests(unittest.TestCase):
    @staticmethod
    def copy_package_source(destination: Path) -> Path:
        source = destination / "mcp-server"
        shutil.copytree(ROOT / "mcp-server", source)
        return source

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

    def test_build_backend_emits_reproducible_wheel_sdist_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb backend ") as temp:
            temporary = Path(temp)
            source = self.copy_package_source(temporary)
            output = temporary / "output"
            output.mkdir()
            metadata = temporary / "metadata"
            metadata.mkdir()
            with mock.patch.object(build_backend, "ROOT", source):
                self.assertEqual(build_backend.get_requires_for_build_wheel({"ignored": True}), [])
                self.assertEqual(build_backend.get_requires_for_build_sdist({}), [])
                dist_info = build_backend.prepare_metadata_for_build_wheel(
                    str(metadata),
                    {"ignored": True},
                )
                wheel_name = build_backend.build_wheel(
                    str(output),
                    {"ignored": True},
                    str(metadata / dist_info),
                )
                sdist_name = build_backend.build_sdist(str(output), {"ignored": True})

                second = temporary / "second"
                second.mkdir()
                second_wheel = build_backend.build_wheel(str(second))
                second_sdist = build_backend.build_sdist(str(second))

            self.assertEqual(
                (output / wheel_name).read_bytes(),
                (second / second_wheel).read_bytes(),
            )
            self.assertEqual(
                (output / sdist_name).read_bytes(),
                (second / second_sdist).read_bytes(),
            )
            metadata_text = (metadata / dist_info / "METADATA").read_text(encoding="utf-8")
            self.assertIn("Name: engineering-board-mcp", metadata_text)
            self.assertIn("Requires-Python: >=3.8", metadata_text)
            with zipfile.ZipFile(output / wheel_name) as archive:
                names = set(archive.namelist())
                self.assertIn(f"{dist_info}/RECORD", names)
                self.assertTrue(
                    all(
                        item.date_time == build_backend.FIXED_ZIP_TIME
                        for item in archive.infolist()
                    )
                )
            with tarfile.open(output / sdist_name, "r:gz") as archive:
                self.assertTrue(all(member.mtime == 0 for member in archive.getmembers()))

            broken = temporary / "broken"
            shutil.copytree(source, broken)
            (broken / "pyproject.toml").write_text("[build-system]\nrequires = []\n")
            with mock.patch.object(build_backend, "ROOT", broken):
                with self.assertRaisesRegex(RuntimeError, r"no \[project\]"):
                    build_backend.build_wheel(str(output))

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

    def test_package_archive_helpers_cover_safe_and_invalid_inputs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb package helpers ") as temp:
            temporary = Path(temp)
            source = self.copy_package_source(temporary)
            wheel_directory = temporary / "wheel"
            wheel_directory.mkdir()
            with mock.patch.object(build_backend, "ROOT", source):
                wheel_name = build_backend.build_wheel(str(wheel_directory))
                sdist_name = build_backend.build_sdist(str(wheel_directory))
            wheel = wheel_directory / wheel_name
            sdist = wheel_directory / sdist_name
            mcpb = temporary / "engineering-board-mcp.mcpb"
            fixture_root = temporary / "root"
            (fixture_root / "mcp-server").mkdir(parents=True)
            for relative in (
                "LICENSE",
                "mcp-server/README.md",
                "mcp-server/manifest.json",
                "mcp-server/engineering_board_core.py",
                "mcp-server/engineering_board_mcp.py",
            ):
                target = fixture_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            package_gate._build_mcpb(fixture_root, mcpb)

            self.assertEqual(
                package_gate._archive_entries(wheel, "wheel"),
                set(zipfile.ZipFile(wheel).namelist()),
            )
            self.assertEqual(
                package_gate._archive_entries(mcpb, "mcpb"),
                {
                    "LICENSE",
                    "manifest.json",
                    "mcp-server/README.md",
                    "mcp-server/engineering_board_core.py",
                    "mcp-server/engineering_board_mcp.py",
                },
            )
            self.assertIn(
                "Name: engineering-board-mcp",
                package_gate._metadata_text(sdist, "sdist", "1.13.4"),
            )
            package_gate._validate_python_metadata(wheel, "wheel", "1.13.4")
            package_gate._validate_python_metadata(sdist, "sdist", "1.13.4")

            unsafe = temporary / "unsafe.tar.gz"
            with tarfile.open(unsafe, "w:gz") as archive:
                directory = tarfile.TarInfo("directory")
                directory.type = tarfile.DIRTYPE
                archive.addfile(directory)
            with self.assertRaisesRegex(PackageGateError, "non-file entry"):
                package_gate._safe_tar_files(unsafe)

            traversal = temporary / "traversal.tar.gz"
            with tarfile.open(traversal, "w:gz") as archive:
                data = b"unsafe"
                entry = tarfile.TarInfo("../escape")
                entry.size = len(data)
                archive.addfile(entry, io.BytesIO(data))
            with self.assertRaisesRegex(PackageGateError, "unsafe entry"):
                package_gate._safe_tar_files(traversal)

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

    def test_source_pin_and_evidence_publication_are_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb package evidence ") as temp:
            fixture = Path(temp)
            (fixture / "mcp-server").mkdir()
            artifact = fixture / "bundle.mcpb"
            artifact.write_bytes(b"bundle")
            digest = hashlib.sha256(b"bundle").hexdigest()
            (fixture / "mcp-server" / "server.json").write_text(
                json.dumps({"packages": [{"fileSha256": digest}]}),
                encoding="utf-8",
            )
            self.assertEqual(
                package_gate._validate_source_pin(fixture, artifact),
                (digest, True),
            )

            (fixture / "mcp-server" / "server.json").write_text(
                json.dumps({"packages": [{"fileSha256": "0" * 64}]}),
                encoding="utf-8",
            )
            (fixture / "CHANGELOG.md").write_text("## [Unreleased]\n\n- Changed.\n")
            self.assertEqual(
                package_gate._validate_source_pin(fixture, artifact),
                ("0" * 64, False),
            )
            (fixture / "CHANGELOG.md").write_text("## [Unreleased]\n\n")
            with self.assertRaisesRegex(PackageGateError, "without an Unreleased note"):
                package_gate._validate_source_pin(fixture, artifact)

            source = fixture / "evidence"
            source.mkdir()
            (source / "report.json").write_text("{}\n", encoding="utf-8")
            target = fixture / "published"
            package_gate._publish_evidence(source, target)
            self.assertEqual((target / "report.json").read_text(encoding="utf-8"), "{}\n")
            (source / "report.json").write_text('{"updated": true}\n', encoding="utf-8")
            package_gate._publish_evidence(source, target)
            self.assertIn("updated", (target / "report.json").read_text(encoding="utf-8"))

    def test_runtime_helpers_use_bounded_portable_processes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb package runtime ") as temp:
            temporary = Path(temp)
            completed = package_runtime.run_command(
                [sys.executable, "-c", "print('ok')"],
                cwd=temporary,
                environment=os.environ.copy(),
                label="successful command",
            )
            self.assertEqual(completed.stdout.strip(), "ok")
            with self.assertRaisesRegex(PackageGateError, "failed with exit 7"):
                package_runtime.run_command(
                    [sys.executable, "-c", "raise SystemExit(7)"],
                    cwd=temporary,
                    environment=os.environ.copy(),
                    label="failing command",
                )

            server = temporary / "fake_mcp.py"
            calls = temporary / "calls.jsonl"
            server.write_text(
                "import json, sys\n"
                "from pathlib import Path\n"
                "for line in sys.stdin:\n"
                "    value=json.loads(line)\n"
                "    if 'id' not in value:\n"
                "        continue\n"
                "    method=value['method']\n"
                "    if method=='initialize':\n"
                "        result={'protocolVersion':'2025-06-18'}\n"
                "    elif method=='ping':\n"
                "        result={}\n"
                "    elif method=='tools/list':\n"
                "        result={'tools':[{} for _ in range(19)]}\n"
                "    else:\n"
                "        with open(sys.argv[1], 'a', encoding='utf-8', newline='\\n') as stream:\n"
                "            stream.write(value['params']['name']+'\\n')\n"
                "        if value['params']['name']=='board_graph':\n"
                "            arguments=value['params']['arguments']\n"
                "            root=Path(arguments['root'])\n"
                "            project=arguments['project']\n"
                "            graph=root/'engineering-board'/project/'GRAPH.yml'\n"
                "            cache=root/'.engineering-board'/'cache'/'graph'/project/'state.json'\n"
                "            for path in (graph, cache):\n"
                "                path.parent.mkdir(parents=True, exist_ok=True)\n"
                "                path.write_bytes('Graph café ↳ package smoke\\n'.encode('utf-8'))\n"
                "        result={'content':[],'isError':False}\n"
                "    print(json.dumps({'jsonrpc':'2.0','id':value['id'],'result':result}),flush=True)\n",
                encoding="utf-8",
            )
            package_runtime._rpc_smoke(
                [sys.executable, server, calls],
                temporary,
                "fake MCP",
            )
            self.assertEqual(
                calls.read_text(encoding="utf-8").splitlines(),
                ["board_init", "board_create_entry", "board_graph"],
            )

    def test_graph_output_diagnostics_name_each_path_and_byte_condition(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb graph diagnostics ") as temp:
            repository = Path(temp)
            project = "package-smoke"
            graph_path = repository / "engineering-board" / project / "GRAPH.yml"
            cache_path = (
                repository / ".engineering-board" / "cache" / "graph" / project / "state.json"
            )
            graph_path.parent.mkdir(parents=True)
            cache_path.parent.mkdir(parents=True)
            graph_path.write_bytes(b"\xff\r")
            graph_path.with_name(graph_path.name + ".tmp.123").write_bytes(b"residue")
            cache_path.with_name(cache_path.name + ".tmp").write_bytes(b"residue")

            with self.assertRaises(PackageGateError) as raised:
                package_runtime._validate_graph_outputs(
                    repository,
                    project,
                    "Python 3.8 wheel",
                )

            diagnostic = str(raised.exception)
            for expected in (
                "GRAPH.yml",
                str(graph_path),
                "invalid UTF-8",
                "marker missing",
                "CR count 1, expected 0",
                "terminal LF count 0, expected 1",
                "temporary sibling residue",
                "cache state.json",
                str(cache_path),
                "missing output",
            ):
                with self.subTest(expected=expected):
                    self.assertIn(expected, diagnostic)

    def test_graph_output_diagnostics_require_exactly_one_terminal_lf(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb graph exact lf ") as temp:
            repository = Path(temp)
            project = "package-smoke"
            marker = "Graph café ↳ package smoke"
            graph_path = repository / "engineering-board" / project / "GRAPH.yml"
            cache_path = (
                repository / ".engineering-board" / "cache" / "graph" / project / "state.json"
            )
            for path in (graph_path, cache_path):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((marker + "\n").encode("utf-8"))

            package_runtime._validate_graph_outputs(
                repository,
                project,
                "Python 3.8 wheel",
            )
            cache_path.write_bytes((marker + "\n\n").encode("utf-8"))
            with self.assertRaisesRegex(
                PackageGateError,
                r"cache state\.json .*terminal LF count 2, expected 1",
            ):
                package_runtime._validate_graph_outputs(
                    repository,
                    project,
                    "Python 3.8 wheel",
                )

    def test_runtime_install_and_tool_helpers_are_portable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb runtime helpers ") as temp:
            temporary = Path(temp)
            tool_root = temporary / "tools"
            (tool_root / "bin").mkdir(parents=True)
            python_tools = tool_root / "python-tools" / ("Scripts" if os.name == "nt" else "bin")
            python_tools.mkdir(parents=True)
            uv = tool_root / "bin" / ("uv.exe" if os.name == "nt" else "uv")
            python_tool = python_tools / ("python.exe" if os.name == "nt" else "python")
            uv.write_text("", encoding="utf-8")
            python_tool.write_text("", encoding="utf-8")
            self.assertEqual(package_runtime.tool_path(tool_root, "uv"), uv)
            self.assertEqual(package_runtime.tool_path(tool_root, "python"), python_tool)
            with self.assertRaisesRegex(PackageGateError, "unknown package tool"):
                package_runtime.tool_path(tool_root, "unknown")
            uv.unlink()
            with self.assertRaisesRegex(PackageGateError, "missing pinned package tool"):
                package_runtime.tool_path(tool_root, "uv")

            runtime_root = temporary / "runtime"
            interpreter = runtime_root / "cpython" / "bin" / "python"
            interpreter.parent.mkdir(parents=True)
            interpreter.write_text("", encoding="utf-8")
            completed = subprocess.CompletedProcess([], 0, str(interpreter) + "\n", "")
            with mock.patch.object(package_runtime, "run_command", return_value=completed):
                self.assertEqual(
                    package_runtime.find_python(
                        Path("uv"),
                        "3.14.7",
                        temporary,
                        {"UV_PYTHON_INSTALL_DIR": str(runtime_root)},
                    ),
                    interpreter,
                )
            outside = temporary / "outside-python"
            outside.write_text("", encoding="utf-8")
            outside_completed = subprocess.CompletedProcess([], 0, str(outside) + "\n", "")
            with (
                mock.patch.object(package_runtime, "run_command", return_value=outside_completed),
                self.assertRaisesRegex(PackageGateError, "no pinned interpreter"),
            ):
                package_runtime.find_python(
                    Path("uv"),
                    "3.14.7",
                    temporary,
                    {"UV_PYTHON_INSTALL_DIR": str(runtime_root)},
                )

            destination = temporary / "destination"
            destination.mkdir()
            artifact = temporary / "artifact.whl"
            artifact.write_bytes(b"wheel")

            def fake_command(
                command: object,
                **_kwargs: object,
            ) -> subprocess.CompletedProcess[str]:
                values = [str(value) for value in command]  # type: ignore[arg-type]
                if "venv" in values:
                    venv = Path(values[-1])
                    scripts = venv / ("Scripts" if os.name == "nt" else "bin")
                    scripts.mkdir(parents=True)
                    (scripts / ("python.exe" if os.name == "nt" else "python")).write_text(
                        "",
                        encoding="utf-8",
                    )
                    (
                        scripts
                        / (
                            "engineering-board-mcp.exe"
                            if os.name == "nt"
                            else "engineering-board-mcp"
                        )
                    ).write_text("", encoding="utf-8")
                return subprocess.CompletedProcess(values, 0, "", "")

            with (
                mock.patch.object(package_runtime, "run_command", side_effect=fake_command),
                mock.patch.object(package_runtime, "_installed_metadata"),
                mock.patch.object(package_runtime, "_rpc_smoke") as rpc,
            ):
                package_runtime.runtime_smoke(
                    root=temporary,
                    uv=Path("uv"),
                    runtime="3.14.7",
                    interpreter=interpreter,
                    artifact=artifact,
                    kind="wheel",
                    destination=destination,
                    environment={},
                )
                rpc.assert_called_once()

            mcpb = temporary / "bundle.mcpb"
            with zipfile.ZipFile(mcpb, "w") as archive:
                archive.writestr("mcp-server/engineering_board_mcp.py", "print('fixture')\n")
            with mock.patch.object(package_runtime, "_rpc_smoke") as rpc:
                package_runtime.mcpb_smoke(
                    runtime="3.14.7",
                    interpreter=interpreter,
                    artifact=mcpb,
                    destination=destination,
                )
                rpc.assert_called_once()


if __name__ == "__main__":
    unittest.main()
