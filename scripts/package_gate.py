#!/usr/bin/env python3
"""Build and validate reproducible Engineering Board distributions."""

from __future__ import annotations

import argparse
import gzip
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
from typing import Any, NoReturn
import zipfile

from package_contract import (
    DIST_NAME,
    PackageGateError,
    artifact_sbom,
    file_sha256,
    load_json,
    validate_archive_entries,
    validate_manifests,
    validate_sbom,
)
from package_runtime import (
    MCP_PROTOCOL_VERSION,
    find_python,
    mcpb_smoke,
    run_command,
    runtime_smoke,
    tool_path,
)


FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
FIXED_FILE_MODE = 0o644


def _safe_tar_files(path: Path) -> list[tuple[str, bytes]]:
    values: list[tuple[str, bytes]] = []
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile():
                raise PackageGateError(f"sdist contains non-file entry: {member.name}")
            if member.name.startswith("/") or ".." in Path(member.name).parts:
                raise PackageGateError(f"sdist contains unsafe entry: {member.name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise PackageGateError(f"cannot read sdist entry: {member.name}")
            values.append((member.name, stream.read()))
    return values


def normalize_sdist(source: Path, destination: Path) -> None:
    entries = _safe_tar_files(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(
                fileobj=compressed,
                mode="w",
                format=tarfile.PAX_FORMAT,
            ) as archive:
                for name, data in sorted(entries):
                    info = tarfile.TarInfo(name)
                    info.mode = FIXED_FILE_MODE
                    info.mtime = 0
                    info.size = len(data)
                    archive.addfile(info, io.BytesIO(data))


def _build_mcpb(root: Path, destination: Path) -> None:
    sources = {
        "LICENSE": root / "LICENSE",
        "manifest.json": root / "mcp-server" / "manifest.json",
        "mcp-server/README.md": root / "mcp-server" / "README.md",
        "mcp-server/engineering_board_core.py": root / "mcp-server" / "engineering_board_core.py",
        "mcp-server/engineering_board_mcp.py": root / "mcp-server" / "engineering_board_mcp.py",
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, source in sorted(sources.items()):
            if not source.is_file():
                raise PackageGateError(f"MCP bundle source is missing: {source}")
            info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = FIXED_FILE_MODE << 16
            archive.writestr(info, source.read_bytes())


def _build_python_artifacts(
    root: Path,
    uv: Path,
    destination: Path,
    environment: dict[str, str],
) -> tuple[Path, Path]:
    source = destination / "source"
    shutil.copytree(root / "mcp-server", source)
    raw = destination / "raw"
    raw.mkdir()
    run_command(
        [
            uv,
            "build",
            "--offline",
            "--no-cache",
            "--no-python-downloads",
            "--no-create-gitignore",
            "--out-dir",
            raw,
            source,
        ],
        cwd=root,
        environment=environment,
        label="Python package build",
    )
    wheels = sorted(raw.glob("*.whl"))
    sdists = sorted(raw.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise PackageGateError(
            f"Python package build produced {len(wheels)} wheels and {len(sdists)} sdists"
        )
    wheel = destination / wheels[0].name
    sdist = destination / sdists[0].name
    shutil.copy2(wheels[0], wheel)
    normalize_sdist(sdists[0], sdist)
    return wheel, sdist


def _archive_entries(path: Path, kind: str) -> set[str]:
    if kind in {"wheel", "mcpb"}:
        with zipfile.ZipFile(path) as archive:
            return set(archive.namelist())
    return {name for name, _data in _safe_tar_files(path)}


def _metadata_text(path: Path, kind: str, version: str) -> str:
    if kind == "wheel":
        name = f"{DIST_NAME}-{version}.dist-info/METADATA"
        with zipfile.ZipFile(path) as archive:
            return archive.read(name).decode("utf-8")
    prefix = f"{DIST_NAME}-{version}"
    with tarfile.open(path, "r:gz") as archive:
        stream = archive.extractfile(f"{prefix}/PKG-INFO")
        if stream is None:
            raise PackageGateError("sdist has no PKG-INFO")
        return stream.read().decode("utf-8")


def _validate_python_metadata(path: Path, kind: str, version: str) -> None:
    metadata = _metadata_text(path, kind, version)
    for expected in (
        "Name: engineering-board-mcp\n",
        f"Version: {version}\n",
        "Requires-Python: >=3.8\n",
    ):
        if expected not in metadata:
            raise PackageGateError(f"{kind} metadata missing {expected.strip()}")
    if "Requires-Dist:" in metadata:
        raise PackageGateError(f"{kind} declares a runtime dependency")


def _schema_validate_sbom(
    sbom: Path,
    dev_python: Path,
    root: Path,
    environment: dict[str, str],
) -> None:
    code = (
        "from pathlib import Path;"
        "from cyclonedx.schema import SchemaVersion;"
        "from cyclonedx.validation.json import JsonStrictValidator;"
        "import sys;"
        "error=JsonStrictValidator(SchemaVersion.V1_6).validate_str("
        "Path(sys.argv[1]).read_text(encoding='utf-8'),all_errors=True);"
        "errors=list(error) if error is not None else [];"
        "print('\\n'.join(str(item) for item in errors));"
        "raise SystemExit(1 if errors else 0)"
    )
    run_command(
        [dev_python, "-c", code, sbom],
        cwd=root,
        environment=environment,
        label=f"SBOM schema validation for {sbom.name}",
    )


def _publish_evidence(source: Path, target: Path) -> None:
    staged = target.with_name(target.name + ".new")
    if staged.exists():
        shutil.rmtree(staged)
    shutil.copytree(source, staged)
    if target.exists():
        shutil.rmtree(target)
    staged.replace(target)


def _validate_repeated_builds(
    builds: list[dict[str, Path]],
    version: str,
) -> None:
    for kind in ("wheel", "sdist", "mcpb"):
        first = builds[0][kind]
        second = builds[1][kind]
        if first.name != second.name or first.read_bytes() != second.read_bytes():
            raise PackageGateError(f"{kind} is not byte reproducible")
        validate_archive_entries(kind, _archive_entries(first, kind), version)
        if kind in {"wheel", "sdist"}:
            _validate_python_metadata(first, kind, version)


def _validate_source_pin(root: Path, mcpb: Path) -> tuple[str, bool]:
    built_digest = file_sha256(mcpb)
    server = load_json(root / "mcp-server" / "server.json")
    pinned_digest = server["packages"][0]["fileSha256"]
    matches = built_digest == pinned_digest
    if not matches:
        changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
        unreleased = changelog.partition("## [Unreleased]")[2].partition("\n## [")[0]
        if not unreleased.strip():
            raise PackageGateError(
                "MCP bundle checksum differs from server.json without an Unreleased note"
            )
    return str(pinned_digest), matches


def _write_package_evidence(
    *,
    root: Path,
    temporary: Path,
    artifacts_by_kind: dict[str, Path],
    version: str,
    runtime_versions: list[str],
    interpreters: dict[str, Path],
    pinned_digest: str,
    pin_matches_source: bool,
    dev_python: Path,
    environment: dict[str, str],
) -> dict[str, Any]:
    evidence = temporary / "evidence"
    evidence.mkdir()
    artifacts: list[dict[str, str]] = []
    for kind in ("wheel", "sdist", "mcpb"):
        artifact = artifacts_by_kind[kind]
        shutil.copy2(artifact, evidence / artifact.name)
        digest = file_sha256(artifact)
        sbom_data = artifact_sbom(
            artifact_name=artifact.name,
            artifact_kind=kind,
            version=version,
            digest=digest,
        )
        validate_sbom(
            sbom_data,
            expected_digest=digest,
            expected_version=version,
        )
        sbom = evidence / f"{artifact.name}.cdx.json"
        sbom.write_bytes(sbom_data)
        _schema_validate_sbom(sbom, dev_python, root, environment)
        artifacts.append(
            {
                "kind": kind,
                "name": artifact.name,
                "sha256": digest,
                "sbom": sbom.name,
                "sbom_sha256": file_sha256(sbom),
            }
        )
    report = {
        "schema_version": "1",
        "version": version,
        "protocol_version": MCP_PROTOCOL_VERSION,
        "runtime_versions": runtime_versions,
        "runtime_interpreters": {
            version_key: str(path) for version_key, path in interpreters.items()
        },
        "artifacts": artifacts,
        "mcpb_pinned_sha256": pinned_digest,
        "mcpb_pin_matches_source": pin_matches_source,
        "runtime_dependencies": [],
    }
    (evidence / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _publish_evidence(
        evidence,
        root / ".engineering-board" / "validation" / "package",
    )
    return report


def run_package_gate(root: Path, tool_root: Path) -> dict[str, Any]:
    version = validate_manifests(root)
    uv = tool_path(tool_root, "uv")
    dev_python = tool_path(tool_root, "python")
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONHASHSEED": "0",
            "PYTHONUTF8": "1",
            "SOURCE_DATE_EPOCH": "315532800",
            "UV_NO_PROGRESS": "1",
            "UV_PYTHON_DOWNLOADS": "never",
            "UV_PYTHON_INSTALL_DIR": str(tool_root / "python"),
        }
    )
    matrix = load_json(root / "support" / "platform-matrix.json")
    python_contract = matrix.get("tools", {}).get("python")
    if not isinstance(python_contract, dict):
        raise PackageGateError("platform matrix has no Python contract")
    runtime_versions = [
        str(python_contract.get("minimum")),
        str(python_contract.get("current")),
    ]

    with tempfile.TemporaryDirectory(prefix="engineering-board-package-") as temp:
        temporary = Path(temp)
        builds: list[dict[str, Path]] = []
        for number in (1, 2):
            build_root = temporary / f"build-{number}"
            build_root.mkdir()
            wheel, sdist = _build_python_artifacts(
                root,
                uv,
                build_root,
                environment,
            )
            mcpb = build_root / "engineering-board-mcp.mcpb"
            _build_mcpb(root, mcpb)
            builds.append({"wheel": wheel, "sdist": sdist, "mcpb": mcpb})
        _validate_repeated_builds(builds, version)
        pinned_digest, pin_matches_source = _validate_source_pin(
            root,
            builds[0]["mcpb"],
        )

        interpreters = {
            runtime: find_python(uv, runtime, root, environment) for runtime in runtime_versions
        }
        runtime_root = temporary / "runtimes"
        runtime_root.mkdir()
        for runtime, interpreter in interpreters.items():
            for kind in ("wheel", "sdist"):
                runtime_smoke(
                    root=root,
                    uv=uv,
                    runtime=runtime,
                    interpreter=interpreter,
                    artifact=builds[0][kind],
                    kind=kind,
                    destination=runtime_root,
                    environment=environment,
                )
            mcpb_smoke(
                runtime=runtime,
                interpreter=interpreter,
                artifact=builds[0]["mcpb"],
                destination=runtime_root,
            )
        return _write_package_evidence(
            root=root,
            temporary=temporary,
            artifacts_by_kind=builds[0],
            version=version,
            runtime_versions=runtime_versions,
            interpreters=interpreters,
            pinned_digest=pinned_digest,
            pin_matches_source=pin_matches_source,
            dev_python=dev_python,
            environment=environment,
        )


class PackageArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(2, f"package-gate: error: {message}\n")


def main(argv: list[str] | None = None) -> int:
    parser = PackageArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--tool-root", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        report = run_package_gate(
            arguments.root.resolve(),
            arguments.tool_root.resolve(),
        )
    except (OSError, PackageGateError, zipfile.BadZipFile, tarfile.TarError) as exc:
        print(f"package-gate: {exc}", file=sys.stderr)
        return 1
    for artifact in report["artifacts"]:
        print(
            "package-gate: artifact "
            f"{artifact['kind']} {artifact['name']} sha256={artifact['sha256']}"
        )
    print("package-gate: runtimes " + ", ".join(str(value) for value in report["runtime_versions"]))
    print("package-gate: manifests, archives, installs, MCP stdio, and SBOMs passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
