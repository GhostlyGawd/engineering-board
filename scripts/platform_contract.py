#!/usr/bin/env python3
"""Validate the machine-readable platform contract without dependencies."""

from __future__ import annotations

import argparse
import json
import ntpath
from pathlib import Path, PureWindowsPath
import re
from typing import Any


REQUIRED_TOOLS = {"python", "node", "git", "claude-code", "codex-cli"}
REQUIRED_ROWS = {
    "linux-x86_64-bash",
    "macos-arm64-bash",
    "windows-x86_64-cmd",
    "windows-x86_64-powershell",
}
WINDOWS_RESERVED_NAMES = {
    "AUX",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "CON",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
    "NUL",
    "PRN",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_windows_relative_path(value: str) -> str:
    """Return a normalized safe relative Windows path or reject it."""
    _require(bool(value), "Windows path is empty")
    _require("\x00" not in value, "Windows path contains NUL")
    path = PureWindowsPath(value)
    _require(not path.is_absolute() and not path.drive and not path.root, "Windows path is absolute")
    normalized_parts: list[str] = []
    for part in path.parts:
        _require(part not in {".", ".."}, "Windows path traverses its root")
        _require(":" not in part, "Windows path contains a stream or drive separator")
        stem = part.rstrip(" .").split(".", 1)[0].upper()
        _require(stem not in WINDOWS_RESERVED_NAMES, "Windows path uses a reserved name")
        _require(part == part.rstrip(" ."), "Windows path has a trailing dot or space")
        normalized_parts.append(part)
    _require(bool(normalized_parts), "Windows path is empty")
    return "/".join(normalized_parts)


def windows_path_is_within(path: str, root: str) -> bool:
    """Compare Windows paths with drive, separator, and case normalization."""
    normalized_path = ntpath.normcase(ntpath.normpath(path))
    normalized_root = ntpath.normcase(ntpath.normpath(root))
    try:
        return ntpath.commonpath([normalized_path, normalized_root]) == normalized_root
    except ValueError:
        return False


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"{path} root must be an object")
    return value


def validate_schema_instance(
    instance: Any,
    schema: dict[str, Any],
    *,
    root_schema: dict[str, Any] | None = None,
    location: str = "$",
) -> None:
    """Validate the JSON-Schema subset used by the platform contract."""
    root_schema = root_schema or schema
    reference = schema.get("$ref")
    if reference is not None:
        _require(
            isinstance(reference, str) and reference.startswith("#/"),
            f"{location}: unsupported schema reference",
        )
        target: Any = root_schema
        for part in reference[2:].split("/"):
            _require(isinstance(target, dict) and part in target, f"{location}: missing schema reference {reference}")
            target = target[part]
        _require(isinstance(target, dict), f"{location}: invalid schema reference {reference}")
        validate_schema_instance(
            instance,
            target,
            root_schema=root_schema,
            location=location,
        )
        return

    if "const" in schema:
        _require(instance == schema["const"], f"{location}: value does not match const")
    if "enum" in schema:
        _require(instance in schema["enum"], f"{location}: value is not in enum")

    expected_type = schema.get("type")
    if expected_type == "object":
        _require(isinstance(instance, dict), f"{location}: expected object")
    elif expected_type == "array":
        _require(isinstance(instance, list), f"{location}: expected array")
    elif expected_type == "string":
        _require(isinstance(instance, str), f"{location}: expected string")
    elif expected_type == "boolean":
        _require(isinstance(instance, bool), f"{location}: expected boolean")
    elif expected_type == "integer":
        _require(
            isinstance(instance, int) and not isinstance(instance, bool),
            f"{location}: expected integer",
        )

    if isinstance(instance, dict):
        required = schema.get("required", [])
        _require(isinstance(required, list), f"{location}: invalid required schema")
        for key in required:
            _require(key in instance, f"{location}: missing required property {key}")
        properties = schema.get("properties", {})
        _require(isinstance(properties, dict), f"{location}: invalid properties schema")
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            child_schema = properties.get(key)
            if child_schema is None:
                if additional is False:
                    raise ValueError(f"{location}: unexpected property {key}")
                if isinstance(additional, dict):
                    child_schema = additional
            if isinstance(child_schema, dict):
                validate_schema_instance(
                    value,
                    child_schema,
                    root_schema=root_schema,
                    location=f"{location}.{key}",
                )

    if isinstance(instance, list):
        minimum = schema.get("minItems")
        if minimum is not None:
            _require(len(instance) >= minimum, f"{location}: too few items")
        if schema.get("uniqueItems"):
            serialized = [json.dumps(item, sort_keys=True) for item in instance]
            _require(len(serialized) == len(set(serialized)), f"{location}: items are not unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, value in enumerate(instance):
                validate_schema_instance(
                    value,
                    item_schema,
                    root_schema=root_schema,
                    location=f"{location}[{index}]",
                )

    if isinstance(instance, str):
        minimum_length = schema.get("minLength")
        if minimum_length is not None:
            _require(len(instance) >= minimum_length, f"{location}: string is too short")
        pattern = schema.get("pattern")
        if pattern is not None:
            _require(re.search(pattern, instance) is not None, f"{location}: string does not match pattern")


def validate_repository_contract(root: Path) -> dict[str, Any]:
    """Validate matrix shape and coherence with docs and CI."""
    matrix_path = root / "support" / "platform-matrix.json"
    schema_path = root / "support" / "platform-matrix.schema.json"
    matrix = _load_object(matrix_path)
    schema = _load_object(schema_path)
    _require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "schema draft is not pinned")
    validate_schema_instance(matrix, schema)
    _require(matrix.get("$schema") == "./platform-matrix.schema.json", "matrix does not reference its schema")
    _require(matrix.get("schema_version") == "1", "unsupported platform matrix schema")

    tools = matrix.get("tools")
    _require(isinstance(tools, dict), "matrix tools must be an object")
    _require(set(tools) == REQUIRED_TOOLS, "matrix tool inventory is incomplete")
    for name, versions in tools.items():
        _require(isinstance(versions, dict), f"{name} versions must be an object")
        _require(
            isinstance(versions.get("minimum"), str)
            and isinstance(versions.get("current"), str),
            f"{name} requires minimum and current versions",
        )

    platforms = matrix.get("platforms")
    _require(isinstance(platforms, list), "matrix platforms must be an array")
    row_ids = [row.get("id") for row in platforms if isinstance(row, dict)]
    _require(len(row_ids) == len(set(row_ids)), "platform row ids must be unique")
    required_rows = {
        row["id"] for row in platforms if isinstance(row, dict) and row.get("required")
    }
    _require(required_rows == REQUIRED_ROWS, "required platform rows are incomplete")

    allowed_skips = set(matrix.get("permitted_skip_reasons", []))
    for row in platforms:
        _require(isinstance(row, dict), "platform row must be an object")
        _require(row.get("native_shell") in {"bash", "cmd", "powershell"}, f"invalid native shell for {row.get('id')}")
        _require(row.get("architecture") in {"arm64", "x86_64"}, f"invalid architecture for {row.get('id')}")
        row_tools = row.get("tools")
        _require(isinstance(row_tools, list) and set(row_tools) <= set(tools), f"unknown tool in {row.get('id')}")
        surfaces = row.get("surfaces")
        _require(isinstance(surfaces, list) and surfaces, f"{row.get('id')} has no surfaces")
        for surface in surfaces:
            skips = surface.get("permitted_skip_reasons")
            _require(isinstance(skips, list) and set(skips) <= allowed_skips, f"invalid skip reason in {row.get('id')}")
            _require(isinstance(surface.get("command"), str) and surface["command"], f"missing command in {row.get('id')}")
        if row["os"]["family"] == "windows":
            command_text = "\n".join(surface["command"] for surface in surfaces)
            _require("platform_test.py" in command_text, f"{row['id']} must use the Python launcher")
            _require("bash" not in command_text.lower(), f"{row['id']} cannot use Bash as native evidence")

    limits = matrix.get("limits")
    _require(isinstance(limits, dict), "matrix limits must be an object")
    _require(limits.get("validator_sessions") == 2, "validator session limit must be two")
    _require(limits.get("exclusive_resources") == ["aggregate", "browser", "otlp"], "exclusive resources are incomplete")
    _require(limits.get("ports") == [4173, 4318], "exclusive ports are incomplete")
    _require(limits.get("mcp_fanout") == 5, "MCP fan-out must be five")
    _require(limits.get("claude_fanout") == 3, "Claude fan-out must be three")

    docs = (root / "docs" / "SUPPORTED_PLATFORMS.md").read_text(encoding="utf-8")
    workflows = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((root / ".github" / "workflows").glob("*.yml"))
    )
    for row_id in sorted(required_rows):
        _require(row_id in docs, f"documentation omits platform row {row_id}")
    for row in platforms:
        if row.get("ci_required"):
            _require(row["id"] in workflows, f"CI omits required platform row {row['id']}")
            _require(row["runner"] in workflows, f"CI omits runner {row['runner']}")
    _require("Git Bash" in docs and "WSL" in docs, "compatibility environments are not documented")
    _require(
        re.search(r"Git Bash.+not native Windows", docs, re.IGNORECASE | re.DOTALL)
        is not None,
        "Git Bash is not classified separately",
    )

    return {
        "schema_version": matrix["schema_version"],
        "required_rows": sorted(required_rows),
        "tool_count": len(tools),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root",
    )
    args = parser.parse_args()
    result = validate_repository_contract(args.root.resolve())
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
