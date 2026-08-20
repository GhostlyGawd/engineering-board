#!/usr/bin/env python3
"""Deterministic multi-stage aggregate execution and reporting."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Callable, Iterable


@dataclass(frozen=True)
class Stage:
    """One independently diagnosable aggregate stage."""

    name: str
    command: tuple[str, ...]
    rerun_command: str
    applications: tuple[str, ...] = ("root-plugin", "mcp-server")
    dependencies: tuple[str, ...] = ()


@dataclass(frozen=True)
class StageResult:
    """Normalized result for one aggregate stage."""

    name: str
    status: str
    exit_code: int | None
    duration_ns: int
    applications: tuple[str, ...]
    diagnostic: str
    rerun_command: str


@dataclass(frozen=True)
class AggregateReport:
    """Complete aggregate decision."""

    results: tuple[StageResult, ...]
    shared_contract_fingerprint: str = ""

    @property
    def failed(self) -> tuple[str, ...]:
        return tuple(result.name for result in self.results if result.status == "failed")

    @property
    def skipped(self) -> tuple[str, ...]:
        return tuple(result.name for result in self.results if result.status == "skipped")

    @property
    def rerun_commands(self) -> tuple[str, ...]:
        return tuple(result.rerun_command for result in self.results if result.status == "failed")

    @property
    def exit_code(self) -> int:
        return 1 if self.failed else 0

    def as_dict(self) -> dict[str, object]:
        decisions = [
            {
                "name": result.name,
                "status": result.status,
                "exit_code": result.exit_code,
                "applications": list(result.applications),
            }
            for result in self.results
        ]
        return {
            "schema_version": "1",
            "overall_pass": self.exit_code == 0,
            "failed": list(self.failed),
            "skipped": list(self.skipped),
            "rerun_commands": list(self.rerun_commands),
            "normalized_decision_fingerprint": hashlib.sha256(
                json.dumps(decisions, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest(),
            "shared_contract_fingerprint": self.shared_contract_fingerprint,
            "stages": [
                {
                    "name": result.name,
                    "status": result.status,
                    "exit_code": result.exit_code,
                    "duration_ns": result.duration_ns,
                    "applications": list(result.applications),
                    "diagnostic": result.diagnostic,
                    "rerun_command": result.rerun_command,
                }
                for result in self.results
            ],
        }


class AggregateRunner:
    """Run all independent stages while preserving every diagnostic."""

    def __init__(
        self,
        stages: Iterable[Stage],
        *,
        execute: Callable[[Stage], int],
    ):
        self.stages = tuple(stages)
        self.execute = execute

    def run(self) -> AggregateReport:
        results: list[StageResult] = []
        decisions: dict[str, str] = {}
        for stage in self.stages:
            failed_dependencies = tuple(
                dependency
                for dependency in stage.dependencies
                if decisions.get(dependency) != "passed"
            )
            if failed_dependencies:
                diagnostic = "dependency failed: " + ", ".join(failed_dependencies)
                result = StageResult(
                    name=stage.name,
                    status="skipped",
                    exit_code=None,
                    duration_ns=0,
                    applications=stage.applications,
                    diagnostic=diagnostic,
                    rerun_command=stage.rerun_command,
                )
            else:
                started = time.monotonic_ns()
                diagnostic = ""
                try:
                    exit_code = self.execute(stage)
                except Exception as exc:  # aggregate boundary preserves later stages
                    exit_code = int(getattr(exc, "exit_code", 1))
                    diagnostic = str(exc)
                duration = time.monotonic_ns() - started
                result = StageResult(
                    name=stage.name,
                    status="passed" if exit_code == 0 else "failed",
                    exit_code=exit_code,
                    duration_ns=duration,
                    applications=stage.applications,
                    diagnostic=diagnostic,
                    rerun_command=stage.rerun_command,
                )
            decisions[stage.name] = result.status
            results.append(result)
        return AggregateReport(tuple(results))


def write_report(path: Path, report: AggregateReport) -> None:
    """Atomically write ignored aggregate evidence."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def print_report(report: AggregateReport) -> None:
    """Print stable stage decisions, durations, diagnostics, and reruns."""

    print("quality-gate: aggregate summary")
    for result in report.results:
        duration_ms = result.duration_ns / 1_000_000
        applications = ",".join(result.applications)
        print(
            f"quality-gate: {result.status} {result.name} "
            f"duration_ms={duration_ms:.3f} applications={applications}"
        )
        if result.diagnostic:
            print(f"quality-gate: diagnostic {result.name}: {result.diagnostic}")
    if report.failed:
        print("quality-gate: failed stages: " + ", ".join(report.failed))
        for command in report.rerun_commands:
            print(f"quality-gate: rerun: {command}")
    if report.skipped:
        print("quality-gate: skipped stages: " + ", ".join(report.skipped))
