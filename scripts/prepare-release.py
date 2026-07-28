#!/usr/bin/env python3
"""Prepare all versioned Engineering Board release surfaces."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any


SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ReleaseError(RuntimeError):
    """Report a release-preparation refusal."""


def parse_version(value: str) -> tuple[int, int, int]:
    """Return a stable Semantic Versioning tuple."""
    match = SEMVER_RE.fullmatch(value)
    if not match:
        raise ReleaseError(
            f"version {value!r} must use the stable MAJOR.MINOR.PATCH format"
        )
    return tuple(int(part) for part in match.groups())


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"cannot read JSON file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReleaseError(f"JSON file {path} must contain an object")
    return value


def dump_json(value: dict[str, Any]) -> str:
    """Render repository JSON with stable formatting."""
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    """Replace one required regular-expression match."""
    result, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise ReleaseError(f"cannot update {label}: expected one match, found {count}")
    return result


def update_changelog(text: str, version: str, release_date: str) -> str:
    """Move the Unreleased body into a dated version section."""
    pattern = re.compile(
        r"^## \[Unreleased\]\s*\n(?P<body>.*?)(?=^## \[)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise ReleaseError("CHANGELOG.md has no [Unreleased] section")
    body = match.group("body").strip()
    if not body:
        raise ReleaseError("CHANGELOG.md [Unreleased] has no release note")
    replacement = (
        "## [Unreleased]\n\n"
        f"## [{version}] — {release_date}\n\n"
        f"{body}\n\n"
    )
    return text[: match.start()] + replacement + text[match.end() :]


def update_pyproject(text: str, current: str, target: str) -> str:
    """Update the project version in pyproject.toml."""
    project = re.search(r"(?ms)^\[project\]\s*$(.*?)(?=^\[|\Z)", text)
    if not project:
        raise ReleaseError("mcp-server/pyproject.toml has no [project] table")
    body = project.group(1)
    updated, count = re.subn(
        rf'(?m)^version\s*=\s*"{re.escape(current)}"\s*$',
        f'version = "{target}"',
        body,
        count=1,
    )
    if count != 1:
        raise ReleaseError("cannot update the pyproject [project] version")
    return text[: project.start(1)] + updated + text[project.end(1) :]


def plan_text_changes(
    root: Path, target: str, release_date: str, bundle_sha: str | None
) -> tuple[str, dict[Path, str]]:
    """Return the current version and all prospective text changes."""
    plugin_path = root / ".claude-plugin" / "plugin.json"
    plugin = load_json(plugin_path)
    current = str(plugin.get("version", ""))
    if parse_version(target) <= parse_version(current):
        raise ReleaseError(
            f"target version {target} must be greater than current version {current}"
        )

    changes: dict[Path, str] = {}
    plugin["version"] = target
    changes[plugin_path] = dump_json(plugin)

    marketplace_path = root / ".claude-plugin" / "marketplace.json"
    marketplace = load_json(marketplace_path)
    entries = marketplace.get("plugins")
    if not isinstance(entries, list):
        raise ReleaseError("marketplace.json has no plugins list")
    matching = [
        entry
        for entry in entries
        if isinstance(entry, dict) and entry.get("name") == plugin.get("name")
    ]
    if len(matching) != 1:
        raise ReleaseError("marketplace.json must have one matching plugin entry")
    matching[0]["version"] = target
    changes[marketplace_path] = dump_json(marketplace)

    manifest_path = root / "mcp-server" / "manifest.json"
    manifest = load_json(manifest_path)
    manifest["version"] = target
    changes[manifest_path] = dump_json(manifest)

    server_path = root / "mcp-server" / "server.json"
    server = load_json(server_path)
    packages = server.get("packages")
    if not isinstance(packages, list) or len(packages) != 1:
        raise ReleaseError("server.json must have one package entry")
    package = packages[0]
    if not isinstance(package, dict):
        raise ReleaseError("server.json package entry must be an object")
    server["version"] = target
    package["version"] = target
    package["identifier"] = (
        "https://github.com/GhostlyGawd/engineering-board/releases/"
        f"download/v{target}/engineering-board-mcp.mcpb"
    )
    if bundle_sha is not None:
        if not SHA256_RE.fullmatch(bundle_sha):
            raise ReleaseError("prospective MCP bundle checksum is invalid")
        package["fileSha256"] = bundle_sha
    changes[server_path] = dump_json(server)

    pyproject_path = root / "mcp-server" / "pyproject.toml"
    changes[pyproject_path] = update_pyproject(
        pyproject_path.read_text(encoding="utf-8"), current, target
    )

    readme_path = root / "README.md"
    changes[readme_path] = replace_once(
        readme_path.read_text(encoding="utf-8"),
        rf"(img\.shields\.io/badge/version-){re.escape(current)}(-)",
        rf"\g<1>{target}\g<2>",
        "README version badge",
    )

    changelog_path = root / "CHANGELOG.md"
    changes[changelog_path] = update_changelog(
        changelog_path.read_text(encoding="utf-8"), target, release_date
    )
    return current, changes


def write_changes(changes: dict[Path, str]) -> None:
    """Write each planned text file with an atomic replace."""
    for path, text in changes.items():
        temporary = path.with_name(f".{path.name}.release-tmp")
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        os.replace(temporary, path)


def build_prospective_bundle(
    root: Path, target: str, release_date: str
) -> tuple[str, dict[Path, str]]:
    """Build the bundle from a temporary tree with prospective versions."""
    current, initial = plan_text_changes(root, target, release_date, None)
    with tempfile.TemporaryDirectory(prefix="engineering-board-release-") as temp:
        staged_root = Path(temp) / "repository"
        shutil.copytree(
            root,
            staged_root,
            ignore=shutil.ignore_patterns(".git", ".codeweb", "dist", "__pycache__"),
        )
        staged_changes = {
            staged_root / path.relative_to(root): text
            for path, text in initial.items()
        }
        write_changes(staged_changes)
        result = subprocess.run(
            ["bash", "mcp-server/build-mcpb.sh"],
            cwd=staged_root,
            check=False,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            raise ReleaseError(f"prospective MCP bundle build failed: {detail}")
        match = re.search(r"^sha256: ([0-9a-f]{64})$", result.stdout, re.MULTILINE)
        if not match:
            raise ReleaseError("prospective MCP bundle build returned no SHA-256")
        bundle_sha = match.group(1)
    _, final = plan_text_changes(root, target, release_date, bundle_sha)
    return current, final


def require_clean_worktree(root: Path) -> None:
    """Refuse an apply operation in a dirty Git worktree."""
    if not (root / ".git").exists():
        return
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise ReleaseError(f"cannot inspect Git worktree: {result.stderr.strip()}")
    if result.stdout.strip():
        raise ReleaseError("release apply requires a clean Git worktree")


def verify_applied_bundle(root: Path, expected_sha: str) -> None:
    """Rebuild the applied tree and compare its checksum."""
    result = subprocess.run(
        ["bash", "mcp-server/build-mcpb.sh"],
        cwd=root,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ReleaseError(f"applied MCP bundle build failed: {detail}")
    match = re.search(r"^sha256: ([0-9a-f]{64})$", result.stdout, re.MULTILINE)
    if not match or match.group(1) != expected_sha:
        actual = match.group(1) if match else "missing"
        raise ReleaseError(
            f"applied MCP bundle checksum {actual} does not match {expected_sha}"
        )


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Prepare all versioned Engineering Board release surfaces."
    )
    parser.add_argument("version", help="Target stable version, without a v prefix.")
    parser.add_argument(
        "--apply", action="store_true", help="Write the previewed release changes."
    )
    parser.add_argument(
        "--date",
        default=dt.datetime.now(dt.timezone.utc).date().isoformat(),
        help="Release date in YYYY-MM-DD format. Default: current UTC date.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--json", action="store_true", help="Print the result as JSON."
    )
    return parser


def main() -> int:
    """Run release preparation."""
    args = build_parser().parse_args()
    root = args.root.resolve()
    try:
        parse_version(args.version)
        try:
            dt.date.fromisoformat(args.date)
        except ValueError as exc:
            raise ReleaseError("--date must use YYYY-MM-DD format") from exc
        if args.apply:
            require_clean_worktree(root)
        current, changes = build_prospective_bundle(root, args.version, args.date)
        server = json.loads(changes[root / "mcp-server" / "server.json"])
        bundle_sha = server["packages"][0]["fileSha256"]
        if args.apply:
            write_changes(changes)
            verify_applied_bundle(root, bundle_sha)
        result = {
            "status": "applied" if args.apply else "preview",
            "current_version": current,
            "target_version": args.version,
            "release_date": args.date,
            "bundle_sha256": bundle_sha,
            "changed_files": [
                path.relative_to(root).as_posix() for path in sorted(changes)
            ],
        }
    except (OSError, ReleaseError) as exc:
        print(f"prepare-release: FAIL: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Release preparation: {result['status']}")
        print(f"Current version: {current}")
        print(f"Target version: {args.version}")
        print(f"Release date: {args.date}")
        print(f"MCP bundle SHA-256: {bundle_sha}")
        print("Changed files:")
        for path in result["changed_files"]:
            print(f"  - {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
