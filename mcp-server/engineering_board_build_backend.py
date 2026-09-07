"""Deterministic, zero-dependency PEP 517 backend for the MCP package."""

from __future__ import annotations

import base64
import csv
import gzip
import hashlib
import io
from pathlib import Path
import re
import tarfile
import zipfile


ROOT = Path(__file__).resolve().parent
PROJECT_NAME = "engineering-board-mcp"
MODULE_NAME = "engineering_board_mcp"
DIST_NAME = "engineering_board_mcp"
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
FIXED_MODE = 0o644
SOURCE_FILES = (
    "LICENSE",
    "README.md",
    "engineering_board_build_backend.py",
    "engineering_board_core.py",
    "engineering_board_mcp.py",
    "pyproject.toml",
)


def _project_section() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r"(?ms)^\[project\]\s*$(.*?)(?=^\[|\Z)", text)
    if match is None:
        raise RuntimeError("pyproject.toml has no [project] table")
    return match.group(1)


def _project_value(name: str) -> str:
    match = re.search(
        rf'(?m)^{re.escape(name)}\s*=\s*"([^"]+)"\s*$',
        _project_section(),
    )
    if match is None:
        raise RuntimeError(f"pyproject.toml has no string project.{name}")
    return match.group(1)


def _version() -> str:
    return _project_value("version")


def _metadata() -> bytes:
    version = _version()
    description = _project_value("description")
    return (
        "Metadata-Version: 2.4\n"
        f"Name: {PROJECT_NAME}\n"
        f"Version: {version}\n"
        f"Summary: {description}\n"
        "Home-page: https://ghostlygawd.github.io/engineering-board/\n"
        "Author: Acadia\n"
        "License-Expression: MIT\n"
        "License-File: LICENSE\n"
        "Requires-Python: >=3.8\n"
        "Project-URL: Repository, https://github.com/GhostlyGawd/engineering-board\n"
        "Project-URL: Documentation, "
        "https://github.com/GhostlyGawd/engineering-board/blob/main/mcp-server/README.md\n"
        "Project-URL: Changelog, "
        "https://github.com/GhostlyGawd/engineering-board/blob/main/CHANGELOG.md\n"
        "Classifier: Development Status :: 4 - Beta\n"
        "Classifier: Intended Audience :: Developers\n"
        "Classifier: License :: OSI Approved :: MIT License\n"
        "Classifier: Operating System :: OS Independent\n"
        "Classifier: Programming Language :: Python :: 3\n"
        "Classifier: Topic :: Software Development\n"
        "Keywords: mcp,mcp-server,kanban,multi-agent,agentic-workflow,claude-code\n"
        "\n" + (ROOT / "README.md").read_text(encoding="utf-8")
    ).encode("utf-8")


def _record_digest(data: bytes) -> str:
    encoded = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=")
    return "sha256=" + encoded.decode("ascii")


def _wheel_contents() -> dict[str, bytes]:
    version = _version()
    dist_info = f"{DIST_NAME}-{version}.dist-info"
    contents = {
        "engineering_board_core.py": (ROOT / "engineering_board_core.py").read_bytes(),
        "engineering_board_mcp.py": (ROOT / "engineering_board_mcp.py").read_bytes(),
        f"{dist_info}/METADATA": _metadata(),
        f"{dist_info}/WHEEL": (
            "Wheel-Version: 1.0\n"
            "Generator: engineering-board deterministic backend\n"
            "Root-Is-Purelib: true\n"
            "Tag: py3-none-any\n"
        ).encode("utf-8"),
        f"{dist_info}/entry_points.txt": (
            "[console_scripts]\nengineering-board-mcp = engineering_board_mcp:main\n"
        ).encode("utf-8"),
        f"{dist_info}/licenses/LICENSE": (ROOT / "LICENSE").read_bytes(),
        f"{dist_info}/top_level.txt": b"engineering_board_core\nengineering_board_mcp\n",
    }
    record_path = f"{dist_info}/RECORD"
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    for name in sorted(contents):
        data = contents[name]
        writer.writerow((name, _record_digest(data), str(len(data))))
    writer.writerow((record_path, "", ""))
    contents[record_path] = output.getvalue().encode("utf-8")
    return contents


def _write_wheel(path: Path) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(_wheel_contents().items()):
            info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = FIXED_MODE << 16
            archive.writestr(info, data)


def _sdist_contents() -> dict[str, bytes]:
    version = _version()
    prefix = f"{DIST_NAME}-{version}"
    contents = {f"{prefix}/{relative}": (ROOT / relative).read_bytes() for relative in SOURCE_FILES}
    contents[f"{prefix}/PKG-INFO"] = _metadata()
    return contents


def _write_sdist(path: Path) -> None:
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for name, data in sorted(_sdist_contents().items()):
                    info = tarfile.TarInfo(name)
                    info.mode = FIXED_MODE
                    info.mtime = 0
                    info.size = len(data)
                    archive.addfile(info, io.BytesIO(data))


def get_requires_for_build_wheel(
    config_settings: dict[str, object] | None = None,
) -> list[str]:
    del config_settings
    return []


def get_requires_for_build_sdist(
    config_settings: dict[str, object] | None = None,
) -> list[str]:
    del config_settings
    return []


def prepare_metadata_for_build_wheel(
    metadata_directory: str,
    config_settings: dict[str, object] | None = None,
) -> str:
    del config_settings
    version = _version()
    dist_info = f"{DIST_NAME}-{version}.dist-info"
    target = Path(metadata_directory) / dist_info
    target.mkdir(parents=True, exist_ok=False)
    (target / "METADATA").write_bytes(_metadata())
    (target / "WHEEL").write_text(
        "Wheel-Version: 1.0\n"
        "Generator: engineering-board deterministic backend\n"
        "Root-Is-Purelib: true\n"
        "Tag: py3-none-any\n",
        encoding="utf-8",
    )
    return dist_info


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, object] | None = None,
    metadata_directory: str | None = None,
) -> str:
    del config_settings, metadata_directory
    filename = f"{DIST_NAME}-{_version()}-py3-none-any.whl"
    target = Path(wheel_directory) / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    _write_wheel(target)
    return filename


def build_sdist(
    sdist_directory: str,
    config_settings: dict[str, object] | None = None,
) -> str:
    del config_settings
    filename = f"{DIST_NAME}-{_version()}.tar.gz"
    target = Path(sdist_directory) / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    _write_sdist(target)
    return filename
