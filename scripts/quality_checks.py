"""Pinned, non-rewriting checks behind the stable quality gate."""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable, Sequence


IGNORED_DIRECTORIES = {
    ".engineering-board",
    ".git",
    "__pycache__",
    "dist",
    "node_modules",
}
PYTHON_DIRECTORIES = ("scripts", "hooks/scripts", "mcp-server", "evaluation", "tests")
ANALYSIS_DIRECTORIES = ("scripts", "hooks/scripts", "mcp-server", "evaluation")
ANALYSIS_EXCLUSIONS = {"mcp-server/test_mcp_server.py"}
TYPED_PATHS = (
    "scripts/platform_contract.py",
    "scripts/quality_checks.py",
    "scripts/quality_gate.py",
    "scripts/validator_resources.py",
    "hooks/scripts/board_demo.py",
    "mcp-server/engineering_board_core.py",
)
EXPECTED_TYPING_POLICY = {
    "schema_version": "1",
    "tool": "mypy",
    "strict": True,
    "applications": [
        {
            "id": "root-plugin",
            "typed_paths": [
                "hooks/scripts/board_demo.py",
                "scripts/platform_contract.py",
                "scripts/quality_checks.py",
                "scripts/quality_gate.py",
                "scripts/validator_resources.py",
            ],
            "staged_exclusions": [
                "evaluation/harness.py",
                "hooks/scripts/board-context.py",
                "hooks/scripts/board-graph-build.py",
                "hooks/scripts/board-insights.py",
                "hooks/scripts/board-intake.py",
                "hooks/scripts/board-outcome.py",
                "hooks/scripts/board_reject_check.py",
                "scripts/aggregate_ci_evidence.py",
                "scripts/bootstrap_ci_evidence.py",
                "scripts/bootstrap_dev.py",
                "scripts/platform_test.py",
                "scripts/prepare-release.py",
            ],
        },
        {
            "id": "mcp-server",
            "typed_paths": ["mcp-server/engineering_board_core.py"],
            "staged_exclusions": ["mcp-server/engineering_board_mcp.py"],
        },
    ],
}
COMPLEXITY_LIMIT = 20
COMPLEXITY_ALLOWANCES = {
    "evaluation/harness.py::score_run": 58,
    "evaluation/harness.py::validate_corpus": 72,
    "hooks/scripts/board-context.py::main": 22,
    "mcp-server/engineering_board_core.py::_load_learnings": 23,
    "mcp-server/engineering_board_core.py::build_clusters": 24,
    "mcp-server/engineering_board_core.py::build_context": 123,
    "mcp-server/engineering_board_core.py::build_edges": 28,
    "mcp-server/engineering_board_core.py::load_hypothesis_registry": 32,
    "mcp-server/engineering_board_core.py::load_pattern_registry": 30,
    "mcp-server/engineering_board_core.py::load_scratch_findings": 26,
    "mcp-server/engineering_board_core.py::plan_hypothesis_operation": 64,
    "mcp-server/engineering_board_core.py::plan_learning_feedback": 29,
    "mcp-server/engineering_board_core.py::plan_outcome": 43,
    "mcp-server/engineering_board_core.py::plan_pattern_operation": 32,
    "mcp-server/engineering_board_core.py::plan_promotion": 25,
    "mcp-server/engineering_board_core.py::rank_clusters": 31,
    "mcp-server/engineering_board_mcp.py::build_open_section": 21,
    "mcp-server/engineering_board_mcp.py::tool_board_create_entry": 48,
    "mcp-server/engineering_board_mcp.py::tool_board_update_entry": 52,
    "scripts/platform_contract.py::validate_repository_contract": 25,
    "scripts/platform_contract.py::validate_schema_instance": 30,
    "scripts/prepare-release.py::plan_text_changes": 29,
}
LARGE_FILE_LIMIT = 250_000
LARGE_FILE_ALLOWANCES = {
    ".goal/evidence/G4-lighthouse-live-mirror.report.json": 600_000,
    ".goal/evidence/G4-lighthouse.report.json": 600_000,
}
GENERATED_STRUCTURED_ARTIFACTS = {
    ".goal/evidence/G4-lighthouse-live-mirror.report.json",
    ".goal/evidence/G4-lighthouse.report.json",
}
INTENTIONALLY_INVALID_JSON = {
    "tests/permissions/fixtures/settings-invalid.json",
}
TEXT_EXTENSIONS = {
    ".json",
    ".jsonc",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".yaml",
    ".yml",
}


class QualityError(Exception):
    def __init__(self, message: str, exit_code: int = 1):
        super().__init__(message)
        self.exit_code = exit_code


@dataclass(frozen=True)
class Toolchain:
    root: Path
    platform_key: str

    @property
    def windows(self) -> bool:
        return self.platform_key.startswith("windows-")

    def executable(self, tool: str) -> Path:
        suffix = ".exe" if self.windows else ""
        python_bin = "Scripts" if self.windows else "bin"
        node_suffix = ".cmd" if self.windows else ""
        locations = {
            "actionlint": self.root / "python-tools" / python_bin / f"actionlint{suffix}",
            "check-jsonschema": self.root
            / "python-tools"
            / python_bin
            / f"check-jsonschema{suffix}",
            "jscpd": self.root / "node-tools" / "node_modules" / ".bin" / f"jscpd{node_suffix}",
            "markdownlint-cli2": self.root
            / "node-tools"
            / "node_modules"
            / ".bin"
            / f"markdownlint-cli2{node_suffix}",
            "mypy": self.root / "python-tools" / python_bin / f"mypy{suffix}",
            "radon": self.root / "python-tools" / python_bin / f"radon{suffix}",
            "ruff": self.root / "python-tools" / python_bin / f"ruff{suffix}",
            "shellcheck": self.root / "python-tools" / python_bin / f"shellcheck{suffix}",
            "shfmt": self.root / "python-tools" / python_bin / f"shfmt{suffix}",
            "vulture": self.root / "python-tools" / python_bin / f"vulture{suffix}",
            "yamllint": self.root / "python-tools" / python_bin / f"yamllint{suffix}",
        }
        path = locations[tool]
        if not path.is_file():
            raise QualityError(
                f"missing pinned tool {tool} at {path}; run: "
                + (
                    "python scripts/bootstrap_dev.py"
                    if os.name == "nt"
                    else "bash scripts/bootstrap-dev.sh"
                ),
                2,
            )
        return path

    def environment(self) -> dict[str, str]:
        value = os.environ.copy()
        node_bin = self.root / "node" / ("." if self.windows else "bin")
        entries = [
            str(self.root / "bin"),
            str(self.root / "python-tools" / ("Scripts" if self.windows else "bin")),
            str(self.root / "node-tools" / "node_modules" / ".bin"),
            str(node_bin),
        ]
        value["PATH"] = os.pathsep.join(entries + [value.get("PATH", "")])
        value["PYTHONUTF8"] = "1"
        return value


class QualityRunner:
    def __init__(self, root: Path):
        self.root = root
        self.toolchain = Toolchain(self._tool_root(), self._platform_key())
        self.environment = self.toolchain.environment()

    def _platform_key(self) -> str:
        system = os.name
        if system == "nt":
            return "windows-x86_64"
        return "darwin-arm64" if sys.platform == "darwin" else "linux-x86_64"

    def _tool_root(self) -> Path:
        configured = os.environ.get("ENGINEERING_BOARD_DEV_TOOLS")
        if configured:
            return Path(configured).expanduser().resolve()
        return self.root / ".engineering-board" / "dev-tools"

    def _stage(self, name: str) -> None:
        stage_log = os.environ.get("ENGINEERING_BOARD_QUALITY_STAGE_LOG")
        if stage_log:
            path = Path(stage_log)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as stream:
                stream.write(name + "\n")
        print(f"quality-gate: start {name}", flush=True)

    def _run(
        self,
        name: str,
        command: Sequence[str | Path],
        *,
        capture: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        self._stage(name)
        result = subprocess.run(
            [str(value) for value in command],
            cwd=self.root,
            env=self.environment,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=capture,
            check=False,
        )
        if capture and result.returncode != 0:
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
        if result.returncode != 0:
            raise QualityError(f"{name} failed with exit {result.returncode}")
        print(f"quality-gate: pass {name}", flush=True)
        return result

    def _run_batched(
        self,
        name: str,
        command: Sequence[str | Path],
        items: Sequence[str | Path],
        *,
        max_command_chars: int | None = None,
    ) -> None:
        limit = max_command_chars or (7_000 if self.toolchain.windows else 120_000)
        prefix = [str(value) for value in command]
        batches: list[list[str]] = []
        batch: list[str] = []
        batch_chars = sum(len(value) + 3 for value in prefix)
        for item_value in items:
            item = str(item_value)
            item_chars = len(item) + 3
            if batch and batch_chars + item_chars > limit:
                batches.append(batch)
                batch = []
                batch_chars = sum(len(value) + 3 for value in prefix)
            if batch_chars + item_chars > limit:
                raise QualityError(f"{name} input path exceeds the command-length limit: {item}")
            batch.append(item)
            batch_chars += item_chars
        if batch:
            batches.append(batch)

        self._stage(name)
        for values in batches:
            result = subprocess.run(
                [*prefix, *values],
                cwd=self.root,
                env=self.environment,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            if result.returncode != 0:
                raise QualityError(f"{name} failed with exit {result.returncode}")
        print(f"quality-gate: pass {name}", flush=True)

    def _files(self, suffixes: set[str], directories: Iterable[str] = (".",)) -> list[Path]:
        found: set[Path] = set()
        for relative in directories:
            base = self.root / relative
            if not base.exists():
                continue
            for path in base.rglob("*"):
                if (
                    path.is_file()
                    and path.suffix.lower() in suffixes
                    and not any(part in IGNORED_DIRECTORIES for part in path.parts)
                ):
                    found.add(path)
        return sorted(found)

    def _relative(self, paths: Iterable[Path]) -> list[str]:
        return [path.relative_to(self.root).as_posix() for path in paths]

    def _python_files(self) -> list[Path]:
        return self._files({".py"}, PYTHON_DIRECTORIES)

    def _shell_files(self) -> list[Path]:
        return self._files({".sh"})

    def _analysis_python(self) -> list[Path]:
        return [
            path
            for path in self._files({".py"}, ANALYSIS_DIRECTORIES)
            if path.relative_to(self.root).as_posix() not in ANALYSIS_EXCLUSIONS
        ]

    def _validate_structured_format(self) -> None:
        self._stage("structured-format")
        failures: list[str] = []
        for path in self._files({".json", ".jsonc", ".yaml", ".yml"}):
            data = path.read_bytes()
            relative = path.relative_to(self.root).as_posix()
            if relative in GENERATED_STRUCTURED_ARTIFACTS:
                continue
            if data and not data.endswith(b"\n"):
                failures.append(f"{relative}: final newline required")
            for number, line in enumerate(data.decode("utf-8").splitlines(), start=1):
                if line != line.rstrip():
                    failures.append(f"{relative}:{number}: trailing whitespace")
        if failures:
            raise QualityError("structured-format failed:\n" + "\n".join(failures))
        print("quality-gate: pass structured-format", flush=True)

    def format(self) -> None:
        python_files = self._relative(self._python_files())
        shell_files = self._relative(self._shell_files())
        markdown_files = self._relative(self._files({".md"}))
        self._run(
            "python-format",
            [
                self.toolchain.executable("ruff"),
                "format",
                "--check",
                "--config",
                "support/quality/ruff.toml",
                *python_files,
            ],
        )
        self._run(
            "shell-format",
            [
                self.toolchain.executable("shfmt"),
                "-d",
                "-i",
                "2",
                "-ci",
                *shell_files,
            ],
        )
        self._run_batched(
            "markdown-format",
            [
                self.toolchain.executable("markdownlint-cli2"),
                "--config",
                "support/quality/markdownlint.jsonc",
            ],
            markdown_files,
        )
        self._validate_structured_format()

    def _validate_json(self) -> None:
        self._stage("json")
        for path in self._files({".json"}):
            relative = path.relative_to(self.root).as_posix()
            if relative in INTENTIONALLY_INVALID_JSON:
                continue
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise QualityError(f"json failed: {relative}: {exc}") from exc
        print("quality-gate: pass json", flush=True)

    def _validate_naming(self) -> None:
        self._stage("naming")
        valid = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
        failures: list[str] = []
        for path in [*self._python_files(), *self._shell_files()]:
            if path.name == "__init__.py":
                continue
            if valid.fullmatch(path.stem) is None:
                failures.append(
                    f"{path.relative_to(self.root).as_posix()}: "
                    "file stem must match ^[a-z0-9][a-z0-9_-]*$"
                )
        if failures:
            raise QualityError("naming failed:\n" + "\n".join(failures))
        print("quality-gate: pass naming", flush=True)

    @staticmethod
    def _radon_blocks(values: list[dict[str, Any]]) -> Iterable[dict[str, Any]]:
        for value in values:
            yield value
            methods = value.get("methods")
            if isinstance(methods, list):
                yield from QualityRunner._radon_blocks(methods)
            closures = value.get("closures")
            if isinstance(closures, list):
                yield from QualityRunner._radon_blocks(closures)

    def _validate_complexity(self) -> None:
        result = self._run(
            "complexity",
            [
                self.toolchain.executable("radon"),
                "cc",
                "-j",
                *self._relative(self._analysis_python()),
            ],
            capture=True,
        )
        report = json.loads(result.stdout)
        failures: list[str] = []
        for path, raw_blocks in report.items():
            if not isinstance(raw_blocks, list):
                continue
            for block in self._radon_blocks(raw_blocks):
                complexity = block.get("complexity")
                name = block.get("name")
                line = block.get("lineno")
                if not isinstance(complexity, int) or not isinstance(name, str):
                    continue
                if complexity <= COMPLEXITY_LIMIT:
                    continue
                key = f"{path}::{name}"
                allowance = COMPLEXITY_ALLOWANCES.get(key)
                if allowance is None or complexity > allowance:
                    failures.append(
                        f"{path}:{line}: complexity {complexity} exceeds "
                        f"threshold {COMPLEXITY_LIMIT}; baseline allowance={allowance}"
                    )
        if failures:
            raise QualityError("complexity failed:\n" + "\n".join(failures))

    def _validate_large_files(self) -> None:
        self._stage("large-files")
        failures: list[str] = []
        for path in self._files(TEXT_EXTENSIONS):
            relative = path.relative_to(self.root).as_posix()
            size = path.stat().st_size
            limit = LARGE_FILE_ALLOWANCES.get(relative, LARGE_FILE_LIMIT)
            if size > limit:
                failures.append(f"{relative}: measured {size} bytes exceeds threshold {limit}")
        if failures:
            raise QualityError("large-files failed:\n" + "\n".join(failures))
        print("quality-gate: pass large-files", flush=True)

    def lint(self) -> None:
        python_files = self._relative(self._python_files())
        shell_files = self._relative(self._shell_files())
        yaml_files = self._relative(self._files({".yaml", ".yml"}))
        workflows = self._relative(self._files({".yml", ".yaml"}, (".github/workflows",)))
        analysis_python = self._relative(self._analysis_python())
        self._run(
            "python-lint",
            [
                self.toolchain.executable("ruff"),
                "check",
                "--config",
                "support/quality/ruff.toml",
                *python_files,
            ],
        )
        self._run(
            "shellcheck",
            [
                self.toolchain.executable("shellcheck"),
                "--severity=error",
                "--shell=bash",
                *shell_files,
            ],
        )
        self._run(
            "yaml",
            [
                self.toolchain.executable("yamllint"),
                "-c",
                "support/quality/yamllint.yml",
                *yaml_files,
            ],
        )
        self._validate_json()
        self._run(
            "json-schema-metaschema",
            [
                self.toolchain.executable("check-jsonschema"),
                "--check-metaschema",
                "support/platform-matrix.schema.json",
                "evaluation/trial-response.schema.json",
            ],
        )
        self._run(
            "json-schema-instance",
            [
                self.toolchain.executable("check-jsonschema"),
                "--schemafile",
                "support/platform-matrix.schema.json",
                "support/platform-matrix.json",
            ],
        )
        self._run(
            "workflows",
            [self.toolchain.executable("actionlint"), "-color", *workflows],
        )
        self._validate_naming()
        self._validate_complexity()
        self._run(
            "dead-code",
            [
                self.toolchain.executable("vulture"),
                *analysis_python,
                "--min-confidence",
                "90",
            ],
        )
        self._run(
            "duplicate-code",
            [
                self.toolchain.executable("jscpd"),
                "--min-lines",
                "20",
                "--min-tokens",
                "100",
                "--threshold",
                "0",
                "--reporters",
                "console",
                "--format",
                "python",
                *analysis_python,
            ],
        )
        self._validate_large_files()

    def typecheck(self) -> None:
        policy_path = self.root / "support" / "quality" / "typing-policy.json"
        try:
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise QualityError(f"typing-policy failed: {exc}") from exc
        if policy != EXPECTED_TYPING_POLICY:
            raise QualityError(
                "typing-policy failed: strict settings or staged exclusions "
                "changed outside the approved policy"
            )
        for application in policy["applications"]:
            app_id = application["id"]
            typed = ", ".join(application["typed_paths"])
            print(f"quality-gate: type scope {app_id}: {typed}")
            for path in application["staged_exclusions"]:
                print(f"quality-gate: staged type exclusion {app_id}: {path}")
        self._run(
            "strict-typecheck",
            [
                self.toolchain.executable("mypy"),
                "--strict",
                "--python-version",
                "3.14",
                "--show-error-codes",
                *TYPED_PATHS,
            ],
        )

    def test(self, workers: int) -> None:
        support_row = os.environ.get("ENGINEERING_BOARD_SUPPORT_ROW", "")
        native_shell = os.environ.get("ENGINEERING_BOARD_NATIVE_SHELL")
        if native_shell is None:
            if support_row.endswith("-cmd"):
                native_shell = "cmd"
            elif support_row.endswith("-powershell"):
                native_shell = "powershell"
            else:
                native_shell = "bash"
        self._run(
            "platform-test",
            [
                sys.executable,
                "scripts/platform_test.py",
                "--workers",
                str(workers),
                "--shell",
                native_shell,
            ],
        )

    @staticmethod
    def _fixture_field(text: str, field: str) -> str:
        match = re.search(
            rf"^\s*(?:-\s*)?{re.escape(field)}:\s*(.+)$",
            text,
            re.MULTILINE,
        )
        return match.group(1).strip() if match else ""

    def security(self) -> None:
        self._stage("reject-filter")
        module_path = self.root / "hooks" / "scripts" / "board_reject_check.py"
        spec = importlib.util.spec_from_file_location("quality_reject_filter", module_path)
        if spec is None or spec.loader is None:
            raise QualityError("reject-filter failed: cannot load canonical filter")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        reject_finding = getattr(module, "reject_finding")
        adversarial = sorted((self.root / "tests/fixtures/adversarial-paste").glob("adv-*.md"))
        benign = sorted((self.root / "tests/fixtures/benign-findings").glob("benign-*.md"))
        if len(adversarial) < 30 or len(benign) < 20:
            raise QualityError(
                f"reject-filter corpus shrank: adversarial={len(adversarial)}, benign={len(benign)}"
            )
        failures: list[str] = []
        for path, should_reject in [
            *((path, True) for path in adversarial),
            *((path, False) for path in benign),
        ]:
            text = path.read_text(encoding="utf-8")
            title_match = re.search(r"^#\s*(.+)$", text, re.MULTILINE)
            tags = [
                value.strip().strip("\"'")
                for value in self._fixture_field(text, "tags").strip("[]").split(",")
                if value.strip()
            ]
            finding = {
                "title": title_match.group(1).strip() if title_match else "",
                "evidence_quote": self._fixture_field(text, "evidence_quote").strip('"'),
                "affects": self._fixture_field(text, "affects"),
                "tags": tags,
            }
            verdict = reject_finding(finding)
            rejected = verdict is not None
            if rejected != should_reject:
                failures.append(
                    f"{path.relative_to(self.root).as_posix()}: "
                    f"expected {'reject' if should_reject else 'accept'}, got {verdict}"
                )
        if failures:
            raise QualityError("reject-filter failed:\n" + "\n".join(failures))
        print(
            "quality-gate: pass reject-filter "
            f"(adversarial={len(adversarial)}, benign={len(benign)})",
            flush=True,
        )

    def package(self) -> None:
        command = (
            "import pathlib,sys;"
            "root=pathlib.Path.cwd();"
            "sys.path.insert(0,str(root/'mcp-server'));"
            "import test_mcp_server as tests;"
            "tests.suite_distribution()"
        )
        self._run("mcp-distribution", [sys.executable, "-c", command])

    def run(self, selector: str, workers: int) -> int:
        if selector == "format":
            self.format()
        elif selector == "lint":
            self.lint()
        elif selector == "typecheck":
            self.typecheck()
        elif selector == "test":
            self.test(workers)
        elif selector == "security":
            self.security()
        elif selector == "package":
            self.package()
        elif selector == "all":
            self.format()
            self.lint()
            self.typecheck()
            self.test(workers)
            self.security()
            self.package()
        else:
            raise QualityError(f"unknown selector {selector!r}", 2)
        print(f"quality-gate: selector {selector} passed", flush=True)
        return 0
