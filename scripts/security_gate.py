"""Fail-closed dependency, secret, workflow, pin, and checksum checks."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Callable, Sequence


IGNORED_DIRECTORIES = {
    ".engineering-board",
    ".git",
    "__pycache__",
    "dist",
    "node_modules",
}
TEXT_SUFFIXES = {
    ".json",
    ".jsonc",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".yaml",
    ".yml",
}
SECRET_PATTERNS = (
    ("SECRET-GITHUB-PAT", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("SECRET-GITHUB-TOKEN", re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}")),
    ("SECRET-AWS-ACCESS-KEY", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("SECRET-SLACK-TOKEN", re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}")),
    (
        "SECRET-PRIVATE-KEY",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
)
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class SecurityGateError(Exception):
    """One security family failed closed."""


def _run(
    command: Sequence[str | Path],
    *,
    root: Path,
    environment: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(value) for value in command],
        cwd=root,
        env=environment,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def _tool_path(tool_root: Path, name: str) -> Path:
    suffix = ".exe" if os.name == "nt" else ""
    python_bin = "Scripts" if os.name == "nt" else "bin"
    locations = {
        "pip-audit": tool_root / "python-tools" / python_bin / f"pip-audit{suffix}",
        "uv": tool_root / "bin" / f"uv{suffix}",
        "zizmor": tool_root / "python-tools" / python_bin / f"zizmor{suffix}",
    }
    path = locations[name]
    if not path.is_file():
        raise SecurityGateError(
            f"missing pinned security tool {name}; run the repository bootstrap"
        )
    return path


def _json_from_output(text: str) -> Any:
    for marker in ("[", "{"):
        offset = text.find(marker)
        if offset >= 0:
            try:
                return json.loads(text[offset:])
            except json.JSONDecodeError:
                continue
    raise SecurityGateError("security tool returned invalid structured output")


def _dependency_audit(root: Path, tool_root: Path, environment: dict[str, str]) -> None:
    with tempfile.TemporaryDirectory(prefix="engineering-board-audit-") as temporary:
        requirements = Path(temporary) / "requirements.txt"
        exported = _run(
            (
                _tool_path(tool_root, "uv"),
                "export",
                "--directory",
                root / "support" / "dev-tools" / "python",
                "--frozen",
                "--no-hashes",
                "--no-annotate",
                "--no-header",
                "--no-emit-project",
            ),
            root=root,
            environment=environment,
        )
        if exported.returncode != 0:
            raise SecurityGateError("DEPENDENCY-LOCK-EXPORT failed closed")
        requirements.write_text(exported.stdout, encoding="utf-8")
        audit_inputs = [requirements]
        fixture_value = environment.get("ENGINEERING_BOARD_SECURITY_DEPENDENCY_INPUT")
        if fixture_value:
            fixture = (root / fixture_value).resolve()
            try:
                fixture.relative_to(root)
            except ValueError as exc:
                raise SecurityGateError("DEPENDENCY-FIXTURE path escapes repository") from exc
            if not fixture.is_file():
                raise SecurityGateError("DEPENDENCY-FIXTURE is not a regular file")
            audit_inputs.append(fixture)
        reports: list[dict[str, Any]] = []
        for audit_input in audit_inputs:
            audited = _run(
                (
                    _tool_path(tool_root, "pip-audit"),
                    "--requirement",
                    audit_input,
                    "--no-deps",
                    "--disable-pip",
                    "--strict",
                    "--format",
                    "json",
                    "--progress-spinner",
                    "off",
                    "--timeout",
                    "20",
                ),
                root=root,
                environment=environment,
            )
            try:
                report = _json_from_output(audited.stdout)
            except SecurityGateError as exc:
                raise SecurityGateError(
                    f"DEPENDENCY-AUDIT-ERROR exit={audited.returncode}; "
                    "vulnerability service failed closed"
                ) from exc
            if not isinstance(report, dict):
                raise SecurityGateError("DEPENDENCY-AUDIT-ERROR report must be an object")
            reports.append(report)
            if audited.returncode not in {0, 1}:
                raise SecurityGateError(f"DEPENDENCY-AUDIT-ERROR exit={audited.returncode}")
    vulnerabilities: list[str] = []
    for report in reports:
        for dependency in report.get("dependencies", []):
            name = dependency.get("name", "unknown")
            version = dependency.get("version", "unknown")
            for vulnerability in dependency.get("vulns", []):
                advisory = vulnerability.get("id", "unknown-advisory")
                fixes = ",".join(vulnerability.get("fix_versions", [])) or "none-published"
                vulnerabilities.append(
                    f"DEPENDENCY-VULNERABILITY {name}=={version} advisory={advisory} fix={fixes}"
                )
    if vulnerabilities:
        raise SecurityGateError("\n".join(vulnerabilities))


def _text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if (
            path.is_file()
            and path.suffix.lower() in TEXT_SUFFIXES
            and not any(part in IGNORED_DIRECTORIES for part in path.parts)
        ):
            files.append(path)
    return sorted(files)


def _secret_scan(root: Path, _tool_root: Path, _environment: dict[str, str]) -> None:
    failures: list[str] = []
    for path in _text_files(root):
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for rule, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    failures.append(f"{rule} {relative}:{line_number}: <redacted>")
    if failures:
        raise SecurityGateError("\n".join(failures))


def _zizmor_location(finding: dict[str, Any]) -> str:
    for location in finding.get("locations", []):
        symbolic = location.get("symbolic", {})
        key = symbolic.get("key", {}).get("Local", {})
        path = key.get("verbatim_path")
        point = symbolic.get("location", {}).get("start_point", {})
        if path:
            return f"{path}:{int(point.get('row', 0)) + 1}"
    return ".github/workflows"


def _workflow_risks(root: Path, tool_root: Path, environment: dict[str, str]) -> None:
    result = _run(
        (
            _tool_path(tool_root, "zizmor"),
            "--persona",
            "regular",
            "--min-severity",
            "high",
            "--min-confidence",
            "high",
            "--offline",
            "--format",
            "json",
            "--no-progress",
            ".github/workflows",
        ),
        root=root,
        environment=environment,
    )
    findings = _json_from_output(result.stdout)
    active = [finding for finding in findings if not finding.get("ignored")]
    if active:
        raise SecurityGateError(
            "\n".join(
                f"WORKFLOW-{finding.get('ident', 'unknown')} "
                f"{_zizmor_location(finding)}: {finding.get('desc', 'workflow risk')}"
                for finding in active
            )
        )
    if result.returncode != 0:
        raise SecurityGateError(f"WORKFLOW-AUDIT-ERROR exit={result.returncode}")


def _immutable_pins(root: Path, _tool_root: Path, _environment: dict[str, str]) -> None:
    failures: list[str] = []
    uses_pattern = re.compile(r"(?m)^\s*(?:-\s*)?uses:\s*['\"]?([^'\"\s#]+)")
    for path in sorted((root / ".github" / "workflows").glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        for match in uses_pattern.finditer(text):
            reference = match.group(1)
            if reference.startswith("./") or reference.startswith("docker://"):
                continue
            _, separator, revision = reference.rpartition("@")
            if not separator or FULL_SHA.fullmatch(revision) is None:
                line = text.count("\n", 0, match.start()) + 1
                failures.append(
                    f"WORKFLOW-unpinned-uses {path.relative_to(root).as_posix()}:{line}: "
                    "action reference must use a full commit SHA"
                )
    if failures:
        raise SecurityGateError("\n".join(failures))


def _supply_chain_policy(
    root: Path,
    _tool_root: Path,
    _environment: dict[str, str],
) -> None:
    failures: list[str] = []
    manifest_path = root / "support" / "dev-tools" / "toolchain.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SecurityGateError(f"SUPPLY-MANIFEST invalid: {exc}") from exc
    for artifact in manifest.get("artifacts", []):
        url = str(artifact.get("url", ""))
        if "/latest/" in url or "/main/" in url or "/master/" in url:
            failures.append(
                f"SUPPLY-MUTABLE-URL {artifact.get('id', 'unknown')}: mutable download URL"
            )
        if not url.startswith("https://"):
            failures.append(
                f"SUPPLY-INSECURE-URL {artifact.get('id', 'unknown')}: HTTPS is required"
            )
        if SHA256.fullmatch(str(artifact.get("sha256", ""))) is None:
            failures.append(
                f"SUPPLY-MISSING-CHECKSUM {artifact.get('id', 'unknown')}: SHA-256 is required"
            )

    for path in sorted((root / ".github" / "workflows").glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        if re.search(r"releases/(?:latest|download/latest)", text):
            failures.append(
                f"SUPPLY-MUTABLE-URL {path.relative_to(root).as_posix()}: mutable download URL"
            )
        if re.search(r"curl\b[^\n|]*\|\s*(?:sh|bash|tar)\b", text):
            failures.append(
                f"SUPPLY-PIPE-EXEC {path.relative_to(root).as_posix()}: "
                "download must be verified before execution or extraction"
            )
    if failures:
        raise SecurityGateError("\n".join(failures))


def _checksum_integrity(root: Path, tool_root: Path, environment: dict[str, str]) -> None:
    result = _run(
        (
            sys.executable,
            root / "scripts" / "bootstrap_dev.py",
            "--check",
            "--root",
            root,
            "--install-root",
            tool_root,
        ),
        root=root,
        environment=environment,
    )
    if result.returncode != 0:
        raise SecurityGateError(
            "SUPPLY-CHECKSUM-DRIFT manifest checksum or installed inventory mismatch"
        )

    policy_path = root / "support" / "quality" / "supply-chain-policy.json"
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SecurityGateError(f"SUPPLY-POLICY invalid: {exc}") from exc
    if policy.get("schema_version") != "1":
        raise SecurityGateError("SUPPLY-POLICY schema_version must be 1")
    release_workflow = (root / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    failures: list[str] = []
    for download in policy.get("downloads", []):
        identifier = download.get("id", "unknown")
        url = str(download.get("url", ""))
        checksum = str(download.get("sha256", ""))
        if SHA256.fullmatch(checksum) is None:
            failures.append(f"SUPPLY-MISSING-CHECKSUM {identifier}")
        if "/latest/" in url or not url.startswith("https://"):
            failures.append(f"SUPPLY-MUTABLE-URL {identifier}: mutable download URL")
        if url not in release_workflow or checksum not in release_workflow:
            failures.append(
                f"SUPPLY-POLICY-DRIFT {identifier}: release workflow does not match policy"
            )
    if failures:
        raise SecurityGateError("\n".join(failures))


def _reject_filter(root: Path, _tool_root: Path, _environment: dict[str, str]) -> None:
    module_path = root / "hooks" / "scripts" / "board_reject_check.py"
    spec = importlib.util.spec_from_file_location("quality_reject_filter", module_path)
    if spec is None or spec.loader is None:
        raise SecurityGateError("reject-filter cannot load canonical filter")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    reject_finding = getattr(module, "reject_finding")
    adversarial = sorted((root / "tests/fixtures/adversarial-paste").glob("adv-*.md"))
    benign = sorted((root / "tests/fixtures/benign-findings").glob("benign-*.md"))
    if len(adversarial) < 30 or len(benign) < 20:
        raise SecurityGateError(
            f"reject-filter corpus shrank: adversarial={len(adversarial)}, benign={len(benign)}"
        )
    failures: list[str] = []

    def field_pattern(field: str) -> re.Pattern[str]:
        return re.compile(
            rf"^\s*(?:-\s*)?{re.escape(field)}:\s*(.+)$",
            re.MULTILINE,
        )

    for path, should_reject in [
        *((path, True) for path in adversarial),
        *((path, False) for path in benign),
    ]:
        text = path.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s*(.+)$", text, re.MULTILINE)
        tag_match = field_pattern("tags").search(text)
        quote_match = field_pattern("evidence_quote").search(text)
        affects_match = field_pattern("affects").search(text)
        finding = {
            "title": title_match.group(1).strip() if title_match else "",
            "evidence_quote": quote_match.group(1).strip().strip('"') if quote_match else "",
            "affects": affects_match.group(1).strip() if affects_match else "",
            "tags": [
                value.strip().strip("\"'")
                for value in (tag_match.group(1).strip("[]").split(",") if tag_match else [])
                if value.strip()
            ],
        }
        rejected = reject_finding(finding) is not None
        if rejected != should_reject:
            failures.append(
                f"{path.relative_to(root).as_posix()}: expected "
                f"{'reject' if should_reject else 'accept'}"
            )
    if failures:
        raise SecurityGateError("\n".join(failures))


def _tree_digest(paths: Sequence[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def run_security(root: Path, tool_root: Path, environment: dict[str, str]) -> None:
    families: tuple[
        tuple[str, Callable[[Path, Path, dict[str, str]], None]],
        ...,
    ] = (
        ("dependency-audit", _dependency_audit),
        ("secret-scan", _secret_scan),
        ("workflow-risks", _workflow_risks),
        ("immutable-pins", _immutable_pins),
        ("supply-chain-policy", _supply_chain_policy),
        ("checksum-integrity", _checksum_integrity),
        ("reject-filter", _reject_filter),
    )
    protected = [
        path
        for path in (
            root / "support" / "dev-tools" / "toolchain.json",
            root / "support" / "dev-tools" / "python" / "pyproject.toml",
            root / "support" / "dev-tools" / "python" / "uv.lock",
            root / "support" / "quality" / "supply-chain-policy.json",
        )
        if path.is_file()
    ]
    before = _tree_digest(protected)
    failures: list[str] = []
    for name, family in families:
        print(f"quality-gate: start security family {name}", flush=True)
        try:
            family(root, tool_root, environment)
        except SecurityGateError as exc:
            failures.append(name)
            print(f"quality-gate: fail security family {name}: {exc}", file=sys.stderr)
        else:
            print(f"quality-gate: pass security family {name}", flush=True)
    if before != _tree_digest(protected):
        failures.append("manifest-immutability")
        print(
            "quality-gate: fail security family manifest-immutability: "
            "security checks modified protected manifests",
            file=sys.stderr,
        )
    if failures:
        raise SecurityGateError("security families failed: " + ", ".join(failures))
