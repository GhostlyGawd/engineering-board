#!/usr/bin/env python3
"""Foundation portability, support-matrix, and validator-lock regressions."""

from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from evaluation.harness import EvaluationError, _atomic_text  # noqa: E402
from scripts import validator_resources  # noqa: E402
from scripts.platform_contract import (  # noqa: E402
    validate_repository_contract,
    validate_schema_instance,
    validate_windows_relative_path,
    windows_path_is_within,
)


RESOURCE_RUNNER = ROOT / "scripts" / "validator_resources.py"
PLATFORM_MATRIX = ROOT / "support" / "platform-matrix.json"


class FoundationPortabilityTests(unittest.TestCase):
    def test_default_macos_temporary_directory_accepts_system_alias(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-platform-alias-") as temp:
            output = Path(temp) / "result.json"
            _atomic_text(output, "{}\n")
            self.assertEqual(output.read_text(encoding="utf-8"), "{}\n")

    def test_user_symlink_ancestor_is_rejected_before_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-platform-linked-") as temp:
            base = Path(temp)
            outside = base / "outside"
            outside.mkdir()
            linked = base / "linked"
            linked.symlink_to(outside, target_is_directory=True)
            output = linked / "result.json"
            with self.assertRaisesRegex(EvaluationError, "linked path"):
                _atomic_text(output, "must not escape\n")
            self.assertFalse((outside / "result.json").exists())

    @unittest.skipUnless(os.name == "nt", "native Windows junction test")
    def test_windows_junction_ancestor_is_rejected_before_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-platform-junction-") as temp:
            base = Path(temp)
            outside = base / "outside"
            outside.mkdir()
            junction = base / "junction"
            subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(outside)],
                check=True,
                capture_output=True,
                text=True,
            )
            output = junction / "result.json"
            with self.assertRaisesRegex(EvaluationError, "linked path"):
                _atomic_text(output, "must not escape\n")
            self.assertFalse((outside / "result.json").exists())

    def test_windows_path_variants_remain_contained(self) -> None:
        self.assertTrue(
            windows_path_is_within(
                r"C:\REPO\engineering-board\entry.md", r"c:\repo"
            )
        )
        self.assertFalse(
            windows_path_is_within(r"C:\repository\entry.md", r"C:\repo")
        )
        for value in (
            r"C:\outside\entry.md",
            r"\\server\share\entry.md",
            r"..\entry.md",
            r"folder/../entry.md",
            r"CON",
            r"folder\NUL.txt",
            r"folder:stream",
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_windows_relative_path(value)
        self.assertEqual(
            validate_windows_relative_path(r"folder\child/entry.md"),
            "folder/child/entry.md",
        )

    def test_support_matrix_schema_docs_and_ci_are_coherent(self) -> None:
        result = validate_repository_contract(ROOT)
        self.assertEqual(result["schema_version"], "1")
        self.assertEqual(
            set(result["required_rows"]),
            {
                "linux-x86_64-bash",
                "macos-arm64-bash",
                "windows-x86_64-cmd",
                "windows-x86_64-powershell",
            },
        )
        matrix = json.loads(PLATFORM_MATRIX.read_text(encoding="utf-8"))
        self.assertEqual(matrix["limits"]["validator_sessions"], 2)
        self.assertEqual(matrix["limits"]["ports"], [4173, 4318])
        schema = json.loads(
            (ROOT / "support" / "platform-matrix.schema.json").read_text(
                encoding="utf-8"
            )
        )
        invalid = dict(matrix)
        invalid["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "unexpected property"):
            validate_schema_instance(invalid, schema)

    def test_platform_neutral_mcp_stdio_lifecycle(self) -> None:
        requests = [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                },
            },
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
            },
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "ping",
            },
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/list",
            },
        ]
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "mcp-server" / "engineering_board_mcp.py"),
            ],
            input="".join(json.dumps(item) + "\n" for item in requests),
            text=True,
            capture_output=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        responses = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual([item["id"] for item in responses], [1, 2, 3])
        initialize = responses[0]["result"]
        self.assertEqual(initialize["protocolVersion"], "2025-06-18")
        self.assertEqual(initialize["serverInfo"]["name"], "engineering-board")
        self.assertEqual(responses[1]["result"], {})
        self.assertEqual(len(responses[2]["result"]["tools"]), 19)


class ValidatorResourceTests(unittest.TestCase):
    def test_windows_pid_liveness_never_sends_signal(self) -> None:
        with (
            mock.patch.object(validator_resources.os, "name", "nt"),
            mock.patch.object(
                validator_resources,
                "_windows_pid_is_alive",
                return_value=True,
            ) as windows_probe,
            mock.patch.object(
                validator_resources.os,
                "kill",
                side_effect=AssertionError("Windows liveness sent a signal"),
            ),
        ):
            self.assertTrue(validator_resources._pid_is_alive(1234))
        windows_probe.assert_called_once_with(1234)

    def run_resource(
        self,
        state_root: Path,
        *args: str,
        timeout: float = 10,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(RESOURCE_RUNNER),
                "--state-root",
                str(state_root),
                *args,
            ],
            text=True,
            capture_output=True,
            timeout=timeout,
        )

    @staticmethod
    def wait_for_lock_count(state_root: Path, count: int) -> None:
        deadline = time.monotonic() + 5
        session_root = state_root / "sessions"
        while time.monotonic() < deadline:
            if len(list(session_root.glob("slot-*"))) == count:
                return
            time.sleep(0.05)
        raise AssertionError(f"did not observe {count} validator session locks")

    def test_global_validator_sessions_cap_at_two(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-validator-cap-") as temp:
            state_root = Path(temp)
            holders = [
                subprocess.Popen(
                    [
                        sys.executable,
                        str(RESOURCE_RUNNER),
                        "--state-root",
                        str(state_root),
                        "run",
                        "--label",
                        f"holder-{index}",
                        "--",
                        sys.executable,
                        "-c",
                        "import time; time.sleep(1.5)",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                for index in (1, 2)
            ]
            try:
                self.wait_for_lock_count(state_root, 2)
                denied = self.run_resource(
                    state_root,
                    "run",
                    "--label",
                    "third",
                    "--",
                    sys.executable,
                    "-c",
                    "print('must not run')",
                )
                self.assertNotEqual(denied.returncode, 0)
                self.assertIn("global validator capacity", denied.stderr)
                self.assertNotIn("must not run", denied.stdout)
            finally:
                for holder in holders:
                    holder.communicate(timeout=5)

    def test_exclusive_resource_fails_visibly_when_occupied(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-validator-exclusive-") as temp:
            state_root = Path(temp)
            holder = subprocess.Popen(
                [
                    sys.executable,
                    str(RESOURCE_RUNNER),
                    "--state-root",
                    str(state_root),
                    "run",
                    "--label",
                    "aggregate-holder",
                    "--exclusive",
                    "aggregate",
                    "--",
                    sys.executable,
                    "-c",
                    "import time; time.sleep(1.5)",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                deadline = time.monotonic() + 5
                lock = state_root / "exclusive" / "aggregate"
                while time.monotonic() < deadline and not lock.is_dir():
                    time.sleep(0.05)
                self.assertTrue(lock.is_dir())
                denied = self.run_resource(
                    state_root,
                    "run",
                    "--label",
                    "aggregate-contender",
                    "--exclusive",
                    "aggregate",
                    "--",
                    sys.executable,
                    "-c",
                    "print('must not run')",
                )
                self.assertNotEqual(denied.returncode, 0)
                self.assertIn("exclusive resource is occupied", denied.stderr)
                self.assertNotIn("must not run", denied.stdout)
            finally:
                holder.communicate(timeout=5)

    def test_child_failure_propagates_original_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-validator-failure-") as temp:
            failed = self.run_resource(
                Path(temp),
                "run",
                "--label",
                "failing-child",
                "--",
                sys.executable,
                "-c",
                "import sys; print('original failure', file=sys.stderr); sys.exit(7)",
            )
            self.assertEqual(failed.returncode, 7)
            self.assertIn("original failure", failed.stderr)

    def test_occupied_ports_fail_without_replacing_listener_then_retry(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eb-validator-ports-") as temp:
            state_root = Path(temp)
            for port in (4173, 4318):
                with self.subTest(port=port):
                    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    listener.bind(("127.0.0.1", port))
                    listener.listen(1)
                    try:
                        denied = self.run_resource(
                            state_root,
                            "run",
                            "--label",
                            f"occupied-{port}",
                            "--exclusive",
                            f"port-{port}",
                            "--",
                            sys.executable,
                            "-c",
                            "print('must not run')",
                        )
                        self.assertNotEqual(denied.returncode, 0)
                        self.assertIn(f"127.0.0.1:{port} is occupied", denied.stderr)
                        self.assertGreaterEqual(listener.fileno(), 0)
                    finally:
                        listener.close()
                    retried = self.run_resource(
                        state_root,
                        "run",
                        "--label",
                        f"retry-{port}",
                        "--exclusive",
                        f"port-{port}",
                        "--",
                        sys.executable,
                        "-c",
                        "print('retry passed')",
                    )
                    self.assertEqual(retried.returncode, 0, retried.stderr)
                    self.assertIn("retry passed", retried.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
