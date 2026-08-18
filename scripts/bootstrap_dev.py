#!/usr/bin/env python3
# ruff: noqa: UP006, UP035, UP045
"""Provision and verify the repository-pinned development toolchain."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# The stable bootstrap must parse on the supported Python 3.8 minimum.
# Keep typing aliases instead of Python 3.9+ built-in generic syntax.

SCHEMA_VERSION = "1"
SUPPORTED_PLATFORMS = {
    ("Darwin", "arm64"): "darwin-arm64",
    ("Linux", "x86_64"): "linux-x86_64",
    ("Linux", "amd64"): "linux-x86_64",
    ("Windows", "AMD64"): "windows-x86_64",
    ("Windows", "x86_64"): "windows-x86_64",
}


class BootstrapError(RuntimeError):
    """Actionable bootstrap failure."""


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise BootstrapError(message)


def load_manifest(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BootstrapError(f"cannot read toolchain manifest {path}: {exc}") from exc
    _require(isinstance(value, dict), "toolchain manifest root must be an object")
    _require(
        value.get("schema_version") == SCHEMA_VERSION,
        "unsupported toolchain manifest schema",
    )
    tools = value.get("tools")
    artifacts = value.get("artifacts")
    _require(isinstance(tools, list) and tools, "toolchain manifest has no tools")
    _require(
        isinstance(artifacts, list) and artifacts,
        "toolchain manifest has no artifacts",
    )
    seen = set()
    for tool in tools:
        _require(isinstance(tool, dict), "tool entry must be an object")
        identifier = tool.get("id")
        _require(
            isinstance(identifier, str) and identifier not in seen,
            f"duplicate or invalid tool id: {identifier!r}",
        )
        seen.add(identifier)
        _require(
            isinstance(tool.get("version"), str)
            and re.fullmatch(r"[0-9]+(?:\.[0-9]+){1,3}", tool["version"]) is not None,
            f"{identifier}: version must be exact",
        )
        _require(
            tool.get("provider")
            in {"artifact", "node", "node-package", "python", "uv"},
            f"{identifier}: unsupported provider",
        )
        _require(
            isinstance(tool.get("executable"), str) and tool["executable"],
            f"{identifier}: executable is missing",
        )
        _require(
            isinstance(tool.get("version_args"), list),
            f"{identifier}: version_args must be an array",
        )
    for artifact in artifacts:
        _require(isinstance(artifact, dict), "artifact entry must be an object")
        _require(
            artifact.get("platform") in SUPPORTED_PLATFORMS.values(),
            f"unsupported artifact platform: {artifact.get('platform')!r}",
        )
        _require(
            isinstance(artifact.get("url"), str)
            and artifact["url"].startswith("https://")
            and "/latest/" not in artifact["url"],
            f"{artifact.get('id')}: artifact URL is not immutable",
        )
        _require(
            isinstance(artifact.get("sha256"), str)
            and re.fullmatch(r"[0-9a-f]{64}", artifact["sha256"]) is not None,
            f"{artifact.get('id')}: artifact checksum is invalid",
        )
    value["_manifest_path"] = path
    return value


def platform_key() -> str:
    key = (platform.system(), platform.machine())
    selected = SUPPORTED_PLATFORMS.get(key)
    if selected is None:
        raise BootstrapError(
            "unsupported bootstrap host "
            f"{key[0]}/{key[1]}; supported hosts are Darwin/arm64, "
            "Linux/x86_64, and Windows/x86_64"
        )
    return selected


def _is_windows(selected_platform: str) -> bool:
    return selected_platform.startswith("windows-")


def _python_bin(install_root: Path, selected_platform: str) -> Path:
    if _is_windows(selected_platform):
        return install_root / "python-tools" / "Scripts" / "python.exe"
    return install_root / "python-tools" / "bin" / "python"


def _provider_command(
    tool: Dict[str, Any],
    install_root: Path,
    selected_platform: str,
) -> Path:
    executable = tool["executable"]
    provider = tool["provider"]
    windows = _is_windows(selected_platform)
    if provider == "python":
        directory = "Scripts" if windows else "bin"
        suffix = ".exe" if windows else ""
        return install_root / "python-tools" / directory / f"{executable}{suffix}"
    if provider == "node":
        if windows:
            suffix = ".cmd" if executable == "npm" else ".exe"
            return install_root / "node" / f"{executable}{suffix}"
        return install_root / "node" / "bin" / executable
    if provider == "node-package":
        suffix = ".cmd" if windows else ""
        return (
            install_root
            / "node-tools"
            / "node_modules"
            / ".bin"
            / f"{executable}{suffix}"
        )
    suffix = ".exe" if windows else ""
    return install_root / "bin" / f"{executable}{suffix}"


def _run_tool_version(
    tool: Dict[str, Any],
    install_root: Path,
    selected_platform: str,
) -> str:
    command = _provider_command(tool, install_root, selected_platform)
    if not command.is_file():
        raise BootstrapError(
            f"missing pinned tool {tool['id']} {tool['version']} at {command}; "
            "run: bash scripts/bootstrap-dev.sh"
        )
    environment = os.environ.copy()
    path_entries = [
        str(install_root / "bin"),
        str(_python_bin(install_root, selected_platform).parent),
        str(install_root / "node-tools" / "node_modules" / ".bin"),
        str(
            install_root / "node"
            if _is_windows(selected_platform)
            else install_root / "node" / "bin"
        ),
    ]
    environment["PATH"] = os.pathsep.join(path_entries + [environment.get("PATH", "")])
    version_command = [str(command), *tool["version_args"]]
    expected_output_version = tool["version"]
    if "package" in tool:
        expected_output_version = tool["package_version"]
        version_command = [
            str(_python_bin(install_root, selected_platform)),
            "-c",
            (
                "import importlib.metadata,sys;"
                "print(importlib.metadata.version(sys.argv[1]))"
            ),
            tool["package"],
        ]
    result = subprocess.run(
        version_command,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    if result.returncode != 0:
        raise BootstrapError(
            f"{tool['id']} version check exited {result.returncode}: {output}; "
            "run: bash scripts/bootstrap-dev.sh"
        )
    expected = expected_output_version
    if re.search(rf"(?<![0-9.]){re.escape(expected)}(?![0-9.])", output) is None:
        raise BootstrapError(
            f"{tool['id']} version mismatch: expected {expected}, got "
            f"{output or '<empty output>'}; run: bash scripts/bootstrap-dev.sh"
        )
    return tool["version"]


def check_installation(
    root: Path,
    install_root: Path,
    manifest: Dict[str, Any],
    *,
    command_runner: Optional[Callable[[Dict[str, Any], Path], str]] = None,
) -> Dict[str, str]:
    del root
    marker = install_root / ".complete.json"
    if not marker.is_file():
        raise BootstrapError(
            f"development toolchain is not installed at {install_root}; "
            "run: bash scripts/bootstrap-dev.sh"
        )
    try:
        completed = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BootstrapError(
            f"toolchain completion marker is invalid: {exc}; "
            "run: bash scripts/bootstrap-dev.sh"
        ) from exc
    manifest_path = manifest["_manifest_path"]
    expected_digest = file_sha256(manifest_path)
    if completed.get("manifest_sha256") != expected_digest:
        raise BootstrapError(
            "toolchain manifest changed after installation; "
            "run: bash scripts/bootstrap-dev.sh"
        )
    selected_platform = platform_key()
    if completed.get("platform") != selected_platform:
        raise BootstrapError(
            f"toolchain was installed for {completed.get('platform')}, "
            f"not {selected_platform}; run: bash scripts/bootstrap-dev.sh"
        )
    inventory: Dict[str, str] = {}
    for tool in manifest["tools"]:
        if command_runner is None and tool.get("verify") == "file-sha256":
            command = _provider_command(tool, install_root, selected_platform)
            if not command.is_file():
                raise BootstrapError(
                    f"missing pinned tool {tool['id']} {tool['version']} at "
                    f"{command}; run: bash scripts/bootstrap-dev.sh"
                )
            expected_file = completed.get("file_sha256", {}).get(tool["id"])
            actual_file = file_sha256(command)
            if expected_file != actual_file:
                raise BootstrapError(
                    f"{tool['id']} executable checksum mismatch; "
                    "run: bash scripts/bootstrap-dev.sh"
                )
            version = tool["version"]
        elif command_runner is None:
            version = _run_tool_version(tool, install_root, selected_platform)
        else:
            version = command_runner(tool, install_root)
        inventory[tool["id"]] = version
    return dict(sorted(inventory.items()))


def download_artifact(
    artifact: Dict[str, Any],
    destination: Path,
) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / Path(artifact["url"]).name
    if archive.is_file() and file_sha256(archive) == artifact["sha256"]:
        return archive
    temporary = archive.with_name(f".{archive.name}.download")
    temporary.unlink(missing_ok=True)
    try:
        with urllib.request.urlopen(  # noqa: SIM117
            artifact["url"], timeout=120
        ) as response:
            with temporary.open("wb") as stream:
                shutil.copyfileobj(response, stream)
    except Exception as exc:
        temporary.unlink(missing_ok=True)
        raise BootstrapError(
            f"download failed for {artifact['id']} {artifact['version']}: {exc}; "
            "check network access and rerun: bash scripts/bootstrap-dev.sh"
        ) from exc
    actual = file_sha256(temporary)
    if actual != artifact["sha256"]:
        temporary.unlink(missing_ok=True)
        raise BootstrapError(
            f"checksum mismatch for {artifact['id']} {artifact['version']}: "
            f"expected {artifact['sha256']}, got {actual}; remove {archive} "
            "and rerun: bash scripts/bootstrap-dev.sh"
        )
    os.replace(temporary, archive)
    return archive


def _safe_member_path(name: str, strip_components: int) -> Optional[Path]:
    parts = Path(name.replace("\\", "/")).parts
    if len(parts) <= strip_components:
        return None
    relative = Path(*parts[strip_components:])
    if relative.is_absolute() or ".." in relative.parts:
        raise BootstrapError(f"archive contains unsafe path: {name}")
    return relative


def _extract_archive(
    archive: Path,
    destination: Path,
    strip_components: int,
) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as source:
            for member in source.infolist():
                relative = _safe_member_path(member.filename, strip_components)
                if relative is None:
                    continue
                target = destination / relative
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with source.open(member) as incoming, target.open("wb") as outgoing:
                    shutil.copyfileobj(incoming, outgoing)
    else:
        with tarfile.open(archive, mode="r:*") as source:
            for member in source.getmembers():
                relative = _safe_member_path(member.name, strip_components)
                if relative is None:
                    continue
                target = destination / relative
                if member.issym():
                    linked = (target.parent / member.linkname).resolve()
                    try:
                        linked.relative_to(destination.resolve())
                    except ValueError as exc:
                        raise BootstrapError(
                            f"archive link escapes destination: {member.name}"
                        ) from exc
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.symlink_to(member.linkname)
                    continue
                if member.islnk():
                    raise BootstrapError(
                        f"archive contains unsupported hard link: {member.name}"
                    )
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                if not member.isfile():
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                incoming = source.extractfile(member)
                if incoming is None:
                    raise BootstrapError(f"cannot extract archive member {member.name}")
                with incoming, target.open("wb") as outgoing:
                    shutil.copyfileobj(incoming, outgoing)
                target.chmod(member.mode & 0o777)


def _artifact(
    manifest: Dict[str, Any],
    identifier: str,
    selected_platform: str,
) -> Dict[str, Any]:
    matches = [
        artifact
        for artifact in manifest["artifacts"]
        if artifact["id"] == identifier and artifact["platform"] == selected_platform
    ]
    _require(
        len(matches) == 1,
        f"toolchain manifest needs one {identifier} artifact for {selected_platform}",
    )
    return matches[0]


def _run_install(
    command: List[str],
    *,
    environment: Dict[str, str],
    attempts: int = 1,
) -> None:
    result: Optional[subprocess.CompletedProcess[str]] = None
    for _ in range(attempts):
        result = subprocess.run(
            command,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            return
    assert result is not None
    diagnostic = (result.stdout + "\n" + result.stderr).strip()
    raise BootstrapError(
        f"installation command failed with exit {result.returncode}: "
        f"{' '.join(command)}: {diagnostic}; correct the reported prerequisite or "
        "network error and rerun: bash scripts/bootstrap-dev.sh"
    )


def _atomic_json(path: Path, value: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=path.parent,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def install_toolchain(
    root: Path,
    install_root: Path,
    manifest: Dict[str, Any],
) -> Dict[str, str]:
    selected_platform = platform_key()
    install_root.mkdir(parents=True, exist_ok=True)
    marker = install_root / ".complete.json"
    marker.unlink(missing_ok=True)
    cache = install_root / "downloads"
    bin_root = install_root / "bin"
    bin_root.mkdir(parents=True, exist_ok=True)

    uv_artifact = _artifact(manifest, "uv", selected_platform)
    uv_archive = download_artifact(uv_artifact, cache)
    uv_stage = install_root / ".uv-stage"
    shutil.rmtree(uv_stage, ignore_errors=True)
    _extract_archive(uv_archive, uv_stage, uv_artifact["strip_components"])
    uv_source = uv_stage / ("uv.exe" if _is_windows(selected_platform) else "uv")
    _require(uv_source.is_file(), "uv archive did not contain the uv executable")
    uv_target = bin_root / uv_source.name
    shutil.copy2(uv_source, uv_target)
    uv_target.chmod(uv_target.stat().st_mode | stat.S_IXUSR)
    shutil.rmtree(uv_stage)

    environment = os.environ.copy()
    environment.update(
        {
            "UV_CACHE_DIR": str(install_root / "cache" / "uv"),
            "UV_NO_PROGRESS": "1",
            "UV_PYTHON_INSTALL_DIR": str(install_root / "python"),
            "UV_SYSTEM_PYTHON": "0",
        }
    )
    python_version = manifest["python_version"]
    _run_install(
        [
            str(uv_target),
            "python",
            "install",
            python_version,
            "--install-dir",
            str(install_root / "python"),
            "--no-bin",
            "--no-registry",
        ],
        environment=environment,
    )
    environment["UV_PROJECT_ENVIRONMENT"] = str(install_root / "python-tools")
    _run_install(
        [
            str(uv_target),
            "sync",
            "--frozen",
            "--no-install-project",
            "--project",
            str(root / "support" / "dev-tools" / "python"),
            "--python",
            python_version,
        ],
        environment=environment,
    )

    node_artifact = _artifact(manifest, "node", selected_platform)
    node_archive = download_artifact(node_artifact, cache)
    node_root = install_root / "node"
    shutil.rmtree(node_root, ignore_errors=True)
    _extract_archive(
        node_archive,
        node_root,
        node_artifact["strip_components"],
    )
    node_tool = next(tool for tool in manifest["tools"] if tool["id"] == "node")
    node_command = _provider_command(node_tool, install_root, selected_platform)
    _require(node_command.is_file(), "Node.js archive did not contain node")
    npm_tool = next(tool for tool in manifest["tools"] if tool["id"] == "npm")
    npm_command = _provider_command(npm_tool, install_root, selected_platform)
    node_project = install_root / "node-tools"
    shutil.rmtree(node_project, ignore_errors=True)
    node_project.mkdir(parents=True)
    shutil.copy2(
        root / "support" / "dev-tools" / "node" / "package.json",
        node_project / "package.json",
    )
    shutil.copy2(
        root / "support" / "dev-tools" / "node" / "package-lock.json",
        node_project / "package-lock.json",
    )
    node_environment = environment.copy()
    node_environment["npm_config_cache"] = str(install_root / "cache" / "npm")
    node_environment["PATH"] = (
        str(node_command.parent) + os.pathsep + node_environment.get("PATH", "")
    )
    _run_install(
        [
            str(npm_command),
            "ci",
            "--ignore-scripts",
            "--no-audit",
            "--no-fund",
            "--prefix",
            str(node_project),
        ],
        environment=node_environment,
        attempts=3,
    )

    syft_artifact = _artifact(manifest, "syft", selected_platform)
    syft_archive = download_artifact(syft_artifact, cache)
    syft_stage = install_root / ".syft-stage"
    shutil.rmtree(syft_stage, ignore_errors=True)
    _extract_archive(syft_archive, syft_stage, syft_artifact["strip_components"])
    syft_source = syft_stage / (
        "syft.exe" if _is_windows(selected_platform) else "syft"
    )
    _require(syft_source.is_file(), "Syft archive did not contain syft")
    syft_target = bin_root / syft_source.name
    shutil.copy2(syft_source, syft_target)
    syft_target.chmod(syft_target.stat().st_mode | stat.S_IXUSR)
    shutil.rmtree(syft_stage)

    inventory: Dict[str, str] = {}
    for tool in manifest["tools"]:
        if tool.get("verify") == "file-sha256":
            command = _provider_command(tool, install_root, selected_platform)
            _require(
                command.is_file(),
                f"missing pinned tool {tool['id']} at {command}",
            )
            inventory[tool["id"]] = tool["version"]
        else:
            inventory[tool["id"]] = _run_tool_version(
                tool,
                install_root,
                selected_platform,
            )
    inventory = dict(sorted(inventory.items()))
    executable_hashes = {
        tool["id"]: file_sha256(
            _provider_command(tool, install_root, selected_platform)
        )
        for tool in manifest["tools"]
        if tool.get("verify") == "file-sha256"
    }
    _atomic_json(
        marker,
        {
            "schema_version": SCHEMA_VERSION,
            "manifest_sha256": file_sha256(manifest["_manifest_path"]),
            "platform": selected_platform,
            "inventory": inventory,
            "file_sha256": executable_hashes,
        },
    )
    return inventory


def _default_install_root(root: Path) -> Path:
    configured = os.environ.get("ENGINEERING_BOARD_DEV_TOOLS")
    if configured:
        return Path(configured).expanduser().resolve()
    return root / ".engineering-board" / "dev-tools"


def _print_inventory(inventory: Dict[str, str]) -> None:
    print(json.dumps(inventory, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the installed inventory without downloads or writes",
    )
    parser.add_argument(
        "--install-root",
        type=Path,
        help="override the ignored development-tool installation directory",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()
    root = args.root.resolve()
    manifest_path = root / "support" / "dev-tools" / "toolchain.json"
    try:
        manifest = load_manifest(manifest_path)
        install_root = (
            args.install_root.expanduser().resolve()
            if args.install_root is not None
            else _default_install_root(root)
        )
        if args.check:
            inventory = check_installation(root, install_root, manifest)
        else:
            try:
                inventory = check_installation(root, install_root, manifest)
            except BootstrapError:
                inventory = install_toolchain(root, install_root, manifest)
        _print_inventory(inventory)
        return 0
    except BootstrapError as exc:
        print(f"bootstrap-dev: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
