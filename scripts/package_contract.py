"""Manifest, archive, checksum, and SBOM contracts for package validation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable


DIST_NAME = "engineering_board_mcp"
PACKAGE_NAME = "engineering-board-mcp"
MCPB_ENTRIES = {
    "LICENSE",
    "manifest.json",
    "mcp-server/README.md",
    "mcp-server/engineering_board_core.py",
    "mcp-server/engineering_board_mcp.py",
}


class PackageGateError(Exception):
    """Actionable packaging contract failure."""


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PackageGateError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise PackageGateError(f"{path}: JSON root must be an object")
    return value


def _project_section(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^\[project\]\s*$(.*?)(?=^\[|\Z)", text)
    if match is None:
        raise PackageGateError(f"{path}: missing [project] table")
    return match.group(1)


def project_string(path: Path, name: str) -> str:
    match = re.search(
        rf'(?m)^{re.escape(name)}\s*=\s*"([^"]+)"\s*$',
        _project_section(path),
    )
    if match is None:
        raise PackageGateError(f"{path}: missing project.{name}")
    return match.group(1)


def require_equal(label: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise PackageGateError(f"{label}: expected {expected!r}, got {actual!r}")


def _validate_plugin_manifests(root: Path) -> str:
    plugin = load_json(root / ".claude-plugin" / "plugin.json")
    codex = load_json(root / ".codex-plugin" / "plugin.json")
    claude_market = load_json(root / ".claude-plugin" / "marketplace.json")
    codex_market = load_json(root / ".agents" / "plugins" / "marketplace.json")
    name = plugin.get("name")
    version = plugin.get("version")
    if not isinstance(name, str) or not name:
        raise PackageGateError("Claude plugin manifest has no product name")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise PackageGateError("Claude plugin manifest has no semantic version")
    require_equal("Codex plugin name", codex.get("name"), name)
    require_equal("Codex plugin version", codex.get("version"), version)
    require_equal("Codex skills path", codex.get("skills"), "./skills/")
    require_equal("Codex MCP path", codex.get("mcpServers"), "./codex-mcp.json")
    require_equal("Codex hooks path", codex.get("hooks"), "./hooks/codex-hooks.json")

    claude_entries = claude_market.get("plugins")
    codex_entries = codex_market.get("plugins")
    if not isinstance(claude_entries, list) or len(claude_entries) != 1:
        raise PackageGateError("Claude marketplace must contain exactly one plugin")
    if not isinstance(codex_entries, list) or len(codex_entries) != 1:
        raise PackageGateError("Codex marketplace must contain exactly one plugin")
    claude_entry = claude_entries[0]
    codex_entry = codex_entries[0]
    if not isinstance(claude_entry, dict) or not isinstance(codex_entry, dict):
        raise PackageGateError("marketplace plugin entries must be objects")
    require_equal("Claude marketplace source", claude_entry.get("source"), "./")
    require_equal("Claude marketplace version", claude_entry.get("version"), version)
    require_equal(
        "Codex marketplace source",
        codex_entry.get("source"),
        {
            "source": "url",
            "url": "https://github.com/GhostlyGawd/engineering-board.git",
            "ref": f"v{version}",
        },
    )
    require_equal("Codex marketplace version", codex_entry.get("version"), version)
    if "policy" in claude_entry:
        raise PackageGateError("Claude marketplace contains Codex-only policy")
    require_equal(
        "Codex marketplace policy",
        codex_entry.get("policy"),
        {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
    )
    return version


def _validate_published_bundle_pin(root: Path, version: str, checksum: str) -> None:
    evidence_files = sorted(
        (root / "docs" / "evidence").glob(f"*-v{version}-release*validation*.md")
    )
    recorded: set[str] = set()
    for path in evidence_files:
        for match in re.finditer(
            r"(?m)^\| Bundle identity \|[^\n]*?([0-9a-f]{64})[^\n]*$",
            path.read_text(encoding="utf-8"),
        ):
            recorded.add(match.group(1))
    if checksum not in recorded:
        raise PackageGateError(
            "MCP Registry package checksum does not match immutable release evidence"
        )


def _validate_mcp_manifests(root: Path, version: str) -> None:
    manifest = load_json(root / "mcp-server" / "manifest.json")
    server = load_json(root / "mcp-server" / "server.json")
    require_equal("MCP bundle version", manifest.get("version"), version)
    require_equal(
        "MCP bundle entry point",
        manifest.get("server", {}).get("entry_point")
        if isinstance(manifest.get("server"), dict)
        else None,
        "mcp-server/engineering_board_mcp.py",
    )
    require_equal("MCP Registry version", server.get("version"), version)
    packages = server.get("packages")
    if not isinstance(packages, list) or len(packages) != 1:
        raise PackageGateError("MCP Registry manifest must contain exactly one package")
    package = packages[0]
    if not isinstance(package, dict):
        raise PackageGateError("MCP Registry package must be an object")
    require_equal("MCP Registry package version", package.get("version"), version)
    require_equal(
        "MCP Registry package transport",
        package.get("transport"),
        {"type": "stdio"},
    )
    identifier = package.get("identifier")
    if not isinstance(identifier, str) or f"/releases/download/v{version}/" not in identifier:
        raise PackageGateError("MCP Registry package URL has a stale release version")
    checksum = package.get("fileSha256")
    if not isinstance(checksum, str) or re.fullmatch(r"[0-9a-f]{64}", checksum) is None:
        raise PackageGateError("MCP Registry package checksum is not SHA-256")
    _validate_published_bundle_pin(root, version, checksum)


def _validate_python_manifest(root: Path, version: str) -> None:
    pyproject = root / "mcp-server" / "pyproject.toml"
    require_equal("Python package name", project_string(pyproject, "name"), PACKAGE_NAME)
    require_equal("Python package version", project_string(pyproject, "version"), version)
    if "dependencies = []" not in _project_section(pyproject):
        raise PackageGateError("Python package must declare zero runtime dependencies")
    build_text = pyproject.read_text(encoding="utf-8")
    for token in (
        "requires = []",
        'build-backend = "engineering_board_build_backend"',
        'backend-path = ["."]',
    ):
        if token not in build_text:
            raise PackageGateError(f"Python build metadata is not self-contained: missing {token}")
    if (root / "mcp-server" / "LICENSE").read_bytes() != (root / "LICENSE").read_bytes():
        raise PackageGateError("MCP package license differs from the repository license")


def validate_manifests(root: Path) -> str:
    version = _validate_plugin_manifests(root)
    _validate_mcp_manifests(root, version)
    _validate_python_manifest(root, version)
    return version


def expected_archive_entries(kind: str, version: str) -> set[str]:
    if kind == "wheel":
        dist_info = f"{DIST_NAME}-{version}.dist-info"
        return {
            "engineering_board_core.py",
            "engineering_board_mcp.py",
            f"{dist_info}/METADATA",
            f"{dist_info}/RECORD",
            f"{dist_info}/WHEEL",
            f"{dist_info}/entry_points.txt",
            f"{dist_info}/licenses/LICENSE",
            f"{dist_info}/top_level.txt",
        }
    if kind == "sdist":
        prefix = f"{DIST_NAME}-{version}"
        return {
            f"{prefix}/LICENSE",
            f"{prefix}/PKG-INFO",
            f"{prefix}/README.md",
            f"{prefix}/engineering_board_build_backend.py",
            f"{prefix}/engineering_board_core.py",
            f"{prefix}/engineering_board_mcp.py",
            f"{prefix}/pyproject.toml",
        }
    if kind == "mcpb":
        return set(MCPB_ENTRIES)
    raise PackageGateError(f"unknown archive kind: {kind}")


def validate_archive_entries(kind: str, entries: Iterable[str], version: str) -> None:
    actual = set(entries)
    expected = expected_archive_entries(kind, version)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing:
        raise PackageGateError(f"{kind}: missing archive entry: {missing[0]}")
    if unexpected:
        raise PackageGateError(f"{kind}: unexpected archive entry: {unexpected[0]}")


def artifact_sbom(
    *,
    artifact_name: str,
    artifact_kind: str,
    version: str,
    digest: str,
) -> bytes:
    value = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "version": 1,
        "metadata": {
            "component": {
                "type": "file",
                "bom-ref": f"artifact:{artifact_name}",
                "name": artifact_name,
                "version": version,
                "hashes": [{"alg": "SHA-256", "content": digest}],
                "properties": [
                    {
                        "name": "engineering-board:artifact-kind",
                        "value": artifact_kind,
                    }
                ],
            }
        },
        "components": [
            {
                "type": "application",
                "bom-ref": f"pkg:pypi/{PACKAGE_NAME}@{version}",
                "name": PACKAGE_NAME,
                "version": version,
                "purl": f"pkg:pypi/{PACKAGE_NAME}@{version}",
            }
        ],
    }
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def validate_sbom(data: bytes, *, expected_digest: str, expected_version: str) -> None:
    try:
        value = json.loads(data)
    except json.JSONDecodeError as exc:
        raise PackageGateError(f"SBOM is invalid JSON: {exc}") from exc
    require_equal("SBOM format", value.get("bomFormat"), "CycloneDX")
    require_equal("SBOM specification", value.get("specVersion"), "1.6")
    component = value.get("metadata", {}).get("component")
    if not isinstance(component, dict):
        raise PackageGateError("SBOM has no metadata component")
    require_equal("SBOM artifact version", component.get("version"), expected_version)
    require_equal(
        "SBOM artifact digest",
        component.get("hashes"),
        [{"alg": "SHA-256", "content": expected_digest}],
    )
