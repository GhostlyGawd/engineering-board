#!/usr/bin/env python3
"""Security, determinism, and local-QA tests for the generated board."""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
from typing import Dict, List, Optional, Tuple
import unittest
import urllib.request


class DocumentAudit(HTMLParser):
    """Collect active-content and visible-text evidence structurally."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: List[str] = []
        self.attributes: List[Tuple[str, str, Optional[str]]] = []
        self.text: List[str] = []
        self.script_sources: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        self.tags.append(tag)
        for name, value in attrs:
            self.attributes.append((tag, name, value))
            if tag == "script" and name == "src" and value:
                self.script_sources.append(value)

    def handle_data(self, data: str) -> None:
        self.text.append(data)


class GeneratorSecurityLocalQATest(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
        cls.view = cls.root / "hooks" / "scripts" / "board-view.sh"
        cls.qa = cls.root / "scripts" / "serve_qa.py"
        cls.policy_path = cls.root / "support" / "web" / "generated-board-policy.json"

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="eb-view-security-")
        self.project = Path(self.temp.name) / "project"
        board = self.project / "engineering-board" / "demo"
        for name in ("bugs", "features", "questions", "observations", "learnings"):
            (board / name).mkdir(parents=True, exist_ok=True)
        (self.project / "engineering-board" / "BOARD-ROUTER.md").write_text(
            "# Board Router\n\n"
            "| project | path | affects prefix |\n"
            "|---------|------|----------------|\n"
            "| demo | engineering-board/demo | demo/ |\n",
            encoding="utf-8",
            newline="\n",
        )
        (board / "BOARD.md").write_text(
            "# demo — Board\n\n## Open\n",
            encoding="utf-8",
            newline="\n",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    @property
    def board(self) -> Path:
        return self.project / "engineering-board" / "demo"

    def write_entry(self, relative: str, fields: Dict[str, str]) -> None:
        lines = ["---"]
        for key, value in fields.items():
            lines.append(f"{key}: {value}")
        lines.extend(["---", "## Done when", "- safe", ""])
        path = self.board / relative
        path.write_text("\n".join(lines), encoding="utf-8", newline="\n")

    def run_view(
        self,
        *args: str,
        env_updates: Optional[Dict[str, str]] = None,
    ) -> subprocess.CompletedProcess[bytes]:
        env = os.environ.copy()
        env["CLAUDE_PROJECT_DIR"] = str(self.project)
        if env_updates:
            env.update(env_updates)
        return subprocess.run(
            ["bash", str(self.view), "demo", *args],
            cwd=self.root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_adversarial_fields_are_visible_but_inert(self) -> None:
        payload = (
            "<script>globalThis.EB_PWNED=1</script>"
            "<img src=x onerror=alert(1)>"
            " javascript: data:text/html srcdoc= onload= style=`x`"
        )
        self.write_entry(
            "bugs/B001.md",
            {
                "id": "B001",
                "type": "bug",
                "title": payload,
                "status": "blocked",
                "priority": "P0",
                "affects": '../../outside" onmouseover="alert(1)',
                "needs": "tdd",
                "pattern": f"[alpha, {payload}]",
                "parent": payload,
                "blocked_by": f"[{payload}]",
            },
        )
        claims = self.board / "_claims" / "B001"
        claims.mkdir(parents=True)
        (claims / "owner.txt").write_text(
            f"session_id: {payload}\n",
            encoding="utf-8",
            newline="\n",
        )
        (self.board / "_claims" / "_reclaimed.log").write_text(
            json.dumps({"entry_id": payload, "reclaimed_at": payload}) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        runtime = self.project / ".engineering-board"
        runtime.mkdir()
        (runtime / "active-workers.json").write_text(
            json.dumps([{"session_id": payload, "mode": payload, "discipline": payload}]),
            encoding="utf-8",
            newline="\n",
        )

        result = self.run_view("--stdout")
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        document = result.stdout.decode("utf-8")
        parser = DocumentAudit()
        parser.feed(document)
        self.assertEqual(parser.tags.count("html"), 1)
        self.assertEqual(parser.tags.count("head"), 1)
        self.assertEqual(parser.tags.count("body"), 1)
        self.assertFalse(parser.script_sources)
        self.assertFalse(
            {"iframe", "object", "embed", "svg", "math", "link", "base"} & set(parser.tags)
        )
        for tag, name, value in parser.attributes:
            self.assertFalse(name.lower().startswith("on"), (tag, name, value))
            if name.lower() in {"href", "src", "action", "formaction"} and value:
                lowered = value.strip().lower()
                self.assertFalse(lowered.startswith(("javascript:", "data:")))
        visible = "".join(parser.text)
        self.assertIn("<script>globalThis.EB_PWNED=1</script>", visible)
        self.assertNotIn("<img src=x onerror=alert(1)>", document)
        self.assertNotIn('onmouseover="alert(1)', document)

    def test_stdout_write_locale_link_and_revision_bytes_are_deterministic(
        self,
    ) -> None:
        self.write_entry(
            "bugs/B001.md",
            {
                "id": "B001",
                "type": "bug",
                "title": "locale-stable card",
                "status": "open",
                "priority": "P1",
                "affects": "src/a.py",
                "needs": "tdd",
                "pattern": "[zeta, alpha]",
            },
        )
        first = self.run_view("--stdout", env_updates={"LC_ALL": "C"})
        second = self.run_view("--stdout", env_updates={"LC_ALL": "en_US.UTF-8"})
        self.assertEqual(first.returncode, 0, first.stderr.decode())
        self.assertEqual(second.returncode, 0, second.stderr.decode())
        self.assertEqual(first.stderr, b"")
        self.assertEqual(second.stderr, b"")
        self.assertEqual(first.stdout, second.stdout)
        self.assertNotIn(str(self.project).encode(), first.stdout)

        original_b001 = (self.board / "bugs" / "B001.md").read_bytes()
        self.write_entry(
            "bugs/B002.md",
            {
                "id": "B002",
                "type": "bug",
                "title": "enumeration-stable card",
                "status": "open",
                "priority": "P2",
                "affects": "src/b.py",
                "needs": "review",
            },
        )
        original_b002 = (self.board / "bugs" / "B002.md").read_bytes()
        enumeration_first = self.run_view("--stdout")
        (self.board / "bugs" / "B001.md").unlink()
        (self.board / "bugs" / "B002.md").unlink()
        (self.board / "bugs" / "B002.md").write_bytes(original_b002)
        (self.board / "bugs" / "B001.md").write_bytes(original_b001)
        enumeration_second = self.run_view("--stdout")
        self.assertEqual(enumeration_first.stdout, enumeration_second.stdout)
        inputs_before = self.input_hashes()

        argument = self.run_view("--stdout", "--link-base", "https://example.test/repository/")
        environment = self.run_view(
            "--stdout",
            env_updates={"EB_VIEW_LINK_BASE": "https://example.test/repository/"},
        )
        self.assertEqual(argument.stdout, environment.stdout)

        write = self.run_view()
        self.assertEqual(write.returncode, 0, write.stderr.decode())
        self.assertEqual((self.board / "board.html").read_bytes(), enumeration_second.stdout)
        self.assertEqual(inputs_before, self.input_hashes())

        revision = "0123456789abcdef0123456789abcdef01234567"
        stamped = self.run_view("--stdout", "--stamp", "--revision", revision)
        self.assertEqual(stamped.returncode, 0, stamped.stderr.decode())
        self.assertIn(revision.encode(), stamped.stdout)
        self.assertNotIn(revision[:12].encode() + b"</code>", stamped.stdout)

    def test_invalid_generation_preserves_previous_output_and_inputs(self) -> None:
        previous = b"prior-good-board\n"
        output = self.board / "board.html"
        output.write_bytes(previous)
        inputs_before = self.input_hashes()
        bad_flag = self.run_view("--unknown")
        self.assertEqual(bad_flag.returncode, 2)
        self.assertIn(b"E_USAGE", bad_flag.stderr)
        self.assertEqual(output.read_bytes(), previous)
        bad_link = self.run_view("--link-base", "javascript:alert(1)")
        self.assertEqual(bad_link.returncode, 2)
        self.assertIn(b"E_LINK_BASE", bad_link.stderr)
        self.assertEqual(output.read_bytes(), previous)
        bad_revision = self.run_view("--stamp", "--revision", "deadbeef")
        self.assertEqual(bad_revision.returncode, 2)
        self.assertIn(b"E_REVISION", bad_revision.stderr)
        self.assertEqual(output.read_bytes(), previous)
        self.assertEqual(inputs_before, self.input_hashes())

    def test_empty_and_malformed_optional_inputs_use_policy_markers(self) -> None:
        policy = json.loads(self.policy_path.read_text(encoding="utf-8"))
        markers = policy["markers"]
        (self.board / "_claims" / "broken").mkdir(parents=True)
        (self.board / "_claims" / "broken" / "owner.txt").write_bytes(b"\xff\x00")
        (self.board / "_claims" / "_reclaimed.log").write_text(
            "not-json\n", encoding="utf-8", newline="\n"
        )
        runtime = self.project / ".engineering-board"
        runtime.mkdir()
        (runtime / "active-workers.json").write_text("{", encoding="utf-8", newline="\n")
        result = self.run_view("--stdout")
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        document = result.stdout.decode("utf-8")
        for key in (
            "empty_board",
            "analysis_unavailable",
            "claims_empty",
            "reclaims_empty",
            "workers_empty",
        ):
            self.assertIn(markers[key], document)

    def test_missing_required_board_fails_without_output_damage(self) -> None:
        output = self.board / "board.html"
        output.write_bytes(b"prior-good-board\n")
        (self.board / "BOARD.md").unlink()
        result = self.run_view()
        self.assertEqual(result.returncode, 3)
        self.assertIn(b"E_REQUIRED_INPUT", result.stderr)
        self.assertIn(b"/board-rebuild", result.stderr)
        self.assertEqual(output.read_bytes(), b"prior-good-board\n")

    def test_policy_and_platform_declare_only_canonical_qa_commands(self) -> None:
        policy = json.loads(self.policy_path.read_text(encoding="utf-8"))
        matrix = json.loads(
            (self.root / "support" / "platform-matrix.json").read_text(encoding="utf-8")
        )
        self.assertEqual(policy["local_qa"]["posix_command"], "bash scripts/serve-qa.sh")
        self.assertEqual(policy["local_qa"]["windows_command"], "python scripts\\serve_qa.py")
        self.assertEqual(matrix["local_qa"], policy["local_qa"])
        help_result = subprocess.run(
            ["bash", str(self.root / "scripts" / "serve-qa.sh"), "--help"],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
        )
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("127.0.0.1:4173", help_result.stdout)

    def test_qa_server_refuses_foreign_listener_then_retries_and_stops(self) -> None:
        holder = subprocess.Popen(
            [
                sys.executable,
                "-c",
                (
                    "import socket,time;"
                    "s=socket.socket();"
                    "s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);"
                    "s.bind(('127.0.0.1',4173));s.listen();"
                    "print('ready',flush=True);time.sleep(30)"
                ),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert holder.stdout is not None
        self.assertEqual(holder.stdout.readline().strip(), "ready")
        try:
            denied = subprocess.run(
                ["bash", str(self.root / "scripts" / "serve-qa.sh")],
                cwd=self.root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
                check=False,
            )
            self.assertEqual(denied.returncode, 75)
            self.assertIn("E_PORT_CONFLICT", denied.stderr)
            self.assertIsNone(holder.poll())
        finally:
            holder.send_signal(signal.SIGTERM)
            holder.wait(timeout=5)
            if holder.stdout is not None:
                holder.stdout.close()
            if holder.stderr is not None:
                holder.stderr.close()

        server = subprocess.Popen(
            ["bash", str(self.root / "scripts" / "serve-qa.sh")],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert server.stderr is not None
        ready = self.read_until(server, "qa-server: READY", timeout=15)
        self.assertIn(f"pid={server.pid}", ready)
        self.assertIn("address=127.0.0.1:4173", ready)
        try:
            with urllib.request.urlopen("http://127.0.0.1:4173/", timeout=5) as response:
                landing = response.read()
                self.assertEqual(response.status, 200)
            with urllib.request.urlopen(
                "http://127.0.0.1:4173/engineering-board/board.html",
                timeout=5,
            ) as response:
                board = response.read()
                self.assertEqual(response.status, 200)
            with urllib.request.urlopen(
                "http://127.0.0.1:4173/engineering-board/bugs/"
                "B001-sessionstart-on2-blockedby-loop-exceeds-10s-time.md",
                timeout=5,
            ) as response:
                source = response.read()
                self.assertEqual(response.status, 200)
                self.assertEqual(response.headers.get_content_charset(), "utf-8")
            self.assertIn(b"engineering-board", landing)
            self.assertIn(b"eb-self", board)
            self.assertIn(b"id: B001", source)
            stopped = subprocess.run(
                [sys.executable, str(self.qa), "--stop"],
                cwd=self.root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
                check=False,
            )
            self.assertEqual(stopped.returncode, 0, stopped.stderr)
            server.wait(timeout=10)
            self.assertFalse(self.port_accepts())
            self.assertFalse((self.root / ".engineering-board" / "qa" / "server.json").exists())
            state_root = Path(self.temp.name) / "post-server-locks"
            retried = subprocess.run(
                [
                    sys.executable,
                    str(self.root / "scripts" / "validator_resources.py"),
                    "--state-root",
                    str(state_root),
                    "run",
                    "--label",
                    "post-qa-retry",
                    "--exclusive",
                    "port-4173",
                    "--",
                    sys.executable,
                    "-c",
                    "print('retry passed')",
                ],
                cwd=self.root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
                check=False,
            )
            self.assertEqual(retried.returncode, 0, retried.stderr)
            self.assertIn("retry passed", retried.stdout)
        finally:
            if server.poll() is None:
                server.send_signal(signal.SIGTERM)
            server.wait(timeout=5)
            if server.stdout is not None:
                server.stdout.close()
            if server.stderr is not None:
                server.stderr.close()

    def input_hashes(self) -> Dict[str, str]:
        hashes: Dict[str, str] = {}
        for path in sorted(self.board.rglob("*")):
            if not path.is_file() or path.name == "board.html":
                continue
            hashes[str(path.relative_to(self.board))] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
        return hashes

    @staticmethod
    def read_until(process: subprocess.Popen[str], marker: str, timeout: float) -> str:
        assert process.stderr is not None
        deadline = time.monotonic() + timeout
        lines: List[str] = []
        while time.monotonic() < deadline:
            line = process.stderr.readline()
            if line:
                lines.append(line)
                if marker in line:
                    return "".join(lines)
            elif process.poll() is not None:
                break
            else:
                time.sleep(0.05)
        raise AssertionError(
            f"server did not report {marker!r}; rc={process.poll()} output={lines!r}"
        )

    @staticmethod
    def port_accepts() -> bool:
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        probe.settimeout(0.2)
        try:
            return probe.connect_ex(("127.0.0.1", 4173)) == 0
        finally:
            probe.close()


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]], verbosity=2)
