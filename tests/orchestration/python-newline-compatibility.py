#!/usr/bin/env python3
"""Regression coverage for Python 3.8-compatible atomic text writers."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import ModuleType
from typing import Callable
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = ROOT / "mcp-server" / "engineering_board_core.py"
DEMO_PATH = ROOT / "hooks" / "scripts" / "board_demo.py"


def load_module(name: str, path: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise AssertionError(f"unable to load {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def assert_atomic_write(
    module: ModuleType,
    writer: Callable[[Path], None],
    target: Path,
    expected: bytes,
) -> None:
    real_replace = os.replace
    replacements: list[tuple[Path, Path]] = []

    def checked_replace(source: os.PathLike[str], destination: os.PathLike[str]) -> None:
        source_path = Path(source)
        destination_path = Path(destination)
        assert source_path == target.with_name(target.name + ".tmp")
        assert destination_path == target
        assert source_path.read_bytes() == expected
        replacements.append((source_path, destination_path))
        real_replace(source_path, destination_path)

    with mock.patch.object(module.os, "replace", side_effect=checked_replace):
        writer(target)

    assert replacements == [(target.with_name(target.name + ".tmp"), target)]
    assert target.read_bytes() == expected
    assert b"\r" not in expected
    assert not target.with_name(target.name + ".tmp").exists()


def main() -> int:
    core_source = CORE_PATH.read_text(encoding="utf-8")
    demo_source = DEMO_PATH.read_text(encoding="utf-8")
    assert 'write_text(content, encoding="utf-8", newline="\\n")' not in core_source
    assert 'write_text(value, encoding="utf-8", newline="\\n")' not in demo_source

    core = load_module("newline_compat_core", CORE_PATH)
    demo = load_module("newline_compat_demo", DEMO_PATH)
    with tempfile.TemporaryDirectory(prefix="eb-newline-compat-") as temporary:
        root = Path(temporary)
        assert_atomic_write(
            core,
            lambda target: core._atomic_write(target, "café ↳ graph\nsecond line\n"),
            root / "core" / "state.json",
            "café ↳ graph\nsecond line\n".encode("utf-8"),
        )
        assert_atomic_write(
            demo,
            lambda target: demo._atomic_json(
                target,
                {"marker": "café ↳ demo", "lines": ["first", "second"]},
            ),
            root / "demo" / "manifest.json",
            (
                json.dumps(
                    {"marker": "café ↳ demo", "lines": ["first", "second"]},
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n"
            ).encode("utf-8"),
        )
        assert_atomic_write(
            demo,
            lambda target: demo._atomic_text(target, "café ↳ hypothesis\nsecond line\n"),
            root / "demo" / "hypothesis.md",
            "café ↳ hypothesis\nsecond line\n".encode("utf-8"),
        )

    print("python-newline-compatibility: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
