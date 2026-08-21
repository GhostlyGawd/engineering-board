#!/usr/bin/env python3
"""Validate exact application discovery, guidance, and freshness."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Dict, cast


ROOT = Path(__file__).resolve().parents[1]


class ApplicationContractError(Exception):
    """Application inventory or guidance is stale."""


@dataclass(frozen=True)
class Application:
    id: str
    root: Path
    guidance: Path
    required_sections: tuple[str, ...]


def _load_policy(root: Path) -> dict[str, Any]:
    path = root / "support" / "applications.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ApplicationContractError(f"support/applications.json: {exc}") from exc
    if value.get("schema_version") != "1":
        raise ApplicationContractError("support/applications.json: unsupported schema")
    applications = value.get("applications")
    if not isinstance(applications, list) or not applications:
        raise ApplicationContractError("support/applications.json: applications are required")
    return cast(Dict[str, Any], value)


def discover_applications(root: Path) -> tuple[Application, ...]:
    """Discover only declared canonical roots, never recursive lookalikes."""

    policy = _load_policy(root)
    discovered: list[Application] = []
    for raw in policy["applications"]:
        app_root = root / str(raw["root"])
        markers = tuple(app_root / str(marker) for marker in raw["markers"])
        present = all(marker.is_file() for marker in markers)
        partial = any(marker.exists() for marker in markers)
        if partial and not present:
            missing = [str(marker.relative_to(root)) for marker in markers if not marker.is_file()]
            raise ApplicationContractError(
                f"{raw['id']}: partial application markers; missing {', '.join(missing)}"
            )
        if not present:
            if raw.get("optional") is True:
                continue
            raise ApplicationContractError(f"{raw['id']}: required application is missing")
        discovered.append(
            Application(
                id=str(raw["id"]),
                root=app_root,
                guidance=root / str(raw["guidance"]),
                required_sections=tuple(str(value) for value in raw["required_sections"]),
            )
        )
    return tuple(discovered)


def _markdown_links(path: Path) -> tuple[str, ...]:
    text = path.read_text(encoding="utf-8")
    return tuple(re.findall(r"\[[^\]]+\]\(([^)]+)\)", text))


def _check_guidance(root: Path, application: Application) -> None:
    relative = application.guidance.relative_to(root).as_posix()
    if not application.guidance.is_file():
        raise ApplicationContractError(f"{relative}: guidance file is missing")
    text = application.guidance.read_text(encoding="utf-8")
    for section in application.required_sections:
        if section not in text:
            raise ApplicationContractError(f"{relative}: missing guidance section {section!r}")
    for raw_link in _markdown_links(application.guidance):
        target = raw_link.split("#", 1)[0]
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        resolved = (application.guidance.parent / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError as exc:
            raise ApplicationContractError(
                f"{relative}: local link escapes repository: {raw_link}"
            ) from exc
        if not resolved.exists():
            raise ApplicationContractError(f"{relative}: local link target is missing: {raw_link}")


def _count_tools(root: Path) -> int:
    source = (root / "mcp-server" / "engineering_board_mcp.py").read_text(encoding="utf-8")
    return source.count('"name": "board_')


def _count_commands(root: Path) -> int:
    return len(tuple((root / "commands").glob("*.md")))


def _count_legacy_suites(root: Path) -> int:
    value = json.loads((root / "support" / "legacy-suites.json").read_text(encoding="utf-8"))
    return len(value["suites"])


def _product_version(root: Path) -> str:
    value = json.loads((root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    version = value.get("version")
    if not isinstance(version, str):
        raise ApplicationContractError(".claude-plugin/plugin.json: version is missing")
    return version


def _check_freshness(root: Path, report: dict[str, object]) -> None:
    version = str(report["product_version"])
    major, minor, _patch = version.split(".")
    required_markers = (
        (
            "AGENTS.md",
            f"Current application inventory: {report['application_count']} applications",
        ),
        (
            "ARCHITECTURE.md",
            f"Current maintained compatibility inventory: "
            f"**{report['legacy_suite_count']} suites**",
        ),
        ("ARCHITECTURE.md", f"Current release line: **v{version}**"),
        ("SECURITY.md", f"Current minor release, {major}.{minor}.x"),
        ("README.md", f"version-{version}-"),
    )
    for relative, marker in required_markers:
        text = (root / relative).read_text(encoding="utf-8")
        if marker not in text:
            raise ApplicationContractError(
                f"{relative}: stale freshness marker; expected {marker!r}"
            )

    policy = _load_policy(root)
    for relative, name in policy["workflow_names"].items():
        text = (root / relative).read_text(encoding="utf-8")
        if re.search(rf"^name:\s*{re.escape(name)}\s*$", text, re.MULTILINE) is None:
            raise ApplicationContractError(f"{relative}: workflow name drift; expected {name!r}")
    pyproject = (root / "mcp-server" / "pyproject.toml").read_text(encoding="utf-8")
    if 'name = "engineering-board-mcp"' not in pyproject:
        raise ApplicationContractError("mcp-server/pyproject.toml: package name drift")
    server = json.loads((root / "mcp-server" / "server.json").read_text(encoding="utf-8"))
    if server.get("name") != "io.github.GhostlyGawd/engineering-board":
        raise ApplicationContractError("mcp-server/server.json: package name drift")


def audit_repository(root: Path) -> dict[str, object]:
    applications = discover_applications(root)
    for application in applications:
        _check_guidance(root, application)
    report: dict[str, object] = {
        "schema_version": "1",
        "applications": [application.id for application in applications],
        "application_count": len(applications),
        "product_version": _product_version(root),
        "tool_count": _count_tools(root),
        "command_count": _count_commands(root),
        "legacy_suite_count": _count_legacy_suites(root),
    }
    _check_freshness(root, report)
    return report


def shared_contract_fingerprint(root: Path) -> str:
    """Bind split and legacy aggregates to one application/shared-suite contract."""

    applications = [application.id for application in discover_applications(root)]
    suites = json.loads((root / "support" / "legacy-suites.json").read_text(encoding="utf-8"))
    portable_suites = [suite["id"] for suite in suites["suites"] if suite.get("portable") is True]
    value = {
        "applications": applications,
        "quality_stages": [
            "format",
            "lint",
            "typecheck",
            "test",
            "coverage",
            "security",
            "package",
        ],
        "portable_shared_suites": portable_suites,
    }
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def smoke_documented_commands(root: Path) -> list[dict[str, object]]:
    policy = _load_policy(root)
    results: list[dict[str, object]] = []
    platform_name = "windows" if os.name == "nt" else "posix"
    for raw in policy["documented_command_smokes"]:
        platforms = tuple(str(value) for value in raw["platforms"])
        if platform_name not in platforms:
            continue
        raw_command = tuple(str(value) for value in raw["command"])
        command = [sys.executable if value == "{python}" else str(value) for value in raw_command]
        result = subprocess.run(
            command,
            cwd=root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        results.append(
            {
                "command": " ".join(str(value) for value in raw_command),
                "exit_code": result.returncode,
                "platform": platform_name,
            }
        )
        if result.returncode != 0:
            raise ApplicationContractError(
                f"documented command failed ({result.returncode}): {' '.join(command)}\n"
                f"{result.stdout}{result.stderr}"
            )
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--smoke-commands", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    root = args.root.expanduser().resolve()
    try:
        report = audit_repository(root)
        commands = smoke_documented_commands(root) if args.smoke_commands else []
    except ApplicationContractError as exc:
        print(f"application-contract: {exc}", file=sys.stderr)
        return 1
    output = {
        **report,
        "applications": [
            {"id": application.id, "root": application.root.relative_to(root).as_posix()}
            for application in discover_applications(root)
        ],
        "documented_commands": commands,
        "documented_commands_pass": all(item["exit_code"] == 0 for item in commands),
        "shared_contract_fingerprint": shared_contract_fingerprint(root),
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(output, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(
        "application-contract: OK "
        f"(applications={report['application_count']} tools={report['tool_count']} "
        f"commands={report['command_count']} suites={report['legacy_suite_count']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
