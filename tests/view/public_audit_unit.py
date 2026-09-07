#!/usr/bin/env python3
"""Deterministic branch coverage for the public deployment auditor."""

from __future__ import annotations

import argparse
import contextlib
import email.message
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "audit_public_web.py"
sys.path.insert(0, str(ROOT / "scripts"))
import audit_public_web  # noqa: E402


REVISION = "0123456789abcdef0123456789abcdef01234567"
OTHER_REVISION = "89abcdef0123456789abcdef0123456789abcdef"
LANDING_URL = "https://example.test/engineering-board/"
BOARD_URL = "https://example.test/engineering-board/board.html"


class FakeResponse:
    """Small urllib response double with observable lifecycle."""

    def __init__(
        self,
        status: int,
        body: bytes = b"",
        *,
        location: Optional[str] = None,
    ) -> None:
        self.status = status
        self.body = body
        self.headers: Dict[str, str] = {}
        if location is not None:
            self.headers["Location"] = location
        self.closed = False
        self.read_limit: Optional[int] = None

    def getcode(self) -> int:
        return self.status

    def read(self, maximum: int = -1) -> bytes:
        self.read_limit = maximum
        return self.body if maximum < 0 else self.body[:maximum]

    def close(self) -> None:
        self.closed = True


class ScriptedOpener:
    def __init__(self, outcomes: List[object]) -> None:
        self.outcomes = list(outcomes)
        self.requests: List[urllib.request.Request] = []
        self.timeouts: List[int] = []

    def open(self, request: urllib.request.Request, timeout: int) -> object:
        self.requests.append(request)
        self.timeouts.append(timeout)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def resource(
    identifier: str,
    *,
    path_pattern: str = r"^/engineering-board/$",
    marker: str = "required marker",
    fragments: Optional[List[str]] = None,
    max_hops: int = 1,
    statuses: Optional[List[int]] = None,
    permitted_origins: Optional[List[str]] = None,
) -> Dict[str, object]:
    return {
        "id": identifier,
        "origin": "https://example.test",
        "path_pattern": path_pattern,
        "query_pattern": "^$",
        "permitted_redirect_origins": permitted_origins or ["https://example.test"],
        "max_redirect_hops": max_hops,
        "accepted_terminal_statuses": statuses or [200],
        "content_marker": marker,
        "fragment_targets": fragments or [],
    }


def source_url(revision: str = REVISION) -> str:
    return (
        "https://github.com/GhostlyGawd/engineering-board/blob/"
        f"{revision}/engineering-board/eb-self/bugs/B001-example.md"
    )


def board_bytes(
    *,
    revision: str = REVISION,
    link_revision: str = REVISION,
    link_text: str = "B001",
    include_source: bool = True,
) -> bytes:
    link = (
        f'<a class="cid" href="{source_url(link_revision)}">{link_text}</a>'
        if include_source
        else ""
    )
    return (f"<h1>eb-self</h1> Generated from <code>{revision}</code>.{link}").encode()


def policy_for(landing: bytes, hrefs: List[str]) -> Dict[str, object]:
    del landing
    return {
        "landing": {
            "canonical_url": LANDING_URL,
            "board_path": "/engineering-board/board.html",
            "anchor_count": len(hrefs),
            "href_inventory": hrefs,
        },
        "crawl": {
            "user_agent": "audit-test/1",
            "timeout_seconds": 3,
            "max_response_bytes": 1024,
        },
        "resources": [
            resource("landing", marker='id="product-marker"', fragments=["why"]),
            resource(
                "board",
                path_pattern=r"^/engineering-board/board\.html$",
                marker="<h1>eb-self</h1>",
            ),
        ],
    }


class PublicAuditUnitTest(unittest.TestCase):
    def assert_audit_error(self, code: str, action: Any) -> audit_public_web.AuditError:
        with self.assertRaises(audit_public_web.AuditError) as raised:
            action()
        self.assertEqual(raised.exception.code, code)
        self.assertTrue(str(raised.exception).startswith(f"{code} "))
        return raised.exception

    def test_url_normalization_and_resource_matching_are_closed(self) -> None:
        self.assertEqual(
            audit_public_web.origin("https://EXAMPLE.test:443/path"),
            "https://example.test",
        )
        self.assertEqual(
            audit_public_web.origin("https://example.test:8443/path"),
            "https://example.test:8443",
        )
        self.assertEqual(
            audit_public_web.normalize_url(
                "../board.html?view=all#why",
                "https://EXAMPLE.test/engineering-board/docs/",
            ),
            "https://example.test/engineering-board/board.html?view=all#why",
        )
        for unsafe in (
            "",
            "https://example.test/\nnext",
            "http://example.test/",
            "https://user@example.test/",
        ):
            with self.subTest(unsafe=unsafe):
                self.assert_audit_error(
                    "E_UNSAFE_URL",
                    lambda value=unsafe: audit_public_web.normalize_url(
                        value,
                        LANDING_URL,
                    ),
                )
        parsed_with_password = mock.Mock(
            scheme="https",
            hostname="example.test",
            username=None,
            password="placeholder",
        )
        with mock.patch.object(
            audit_public_web.urllib.parse,
            "urlsplit",
            return_value=parsed_with_password,
        ):
            self.assert_audit_error(
                "E_UNSAFE_URL",
                lambda: audit_public_web.origin(LANDING_URL),
            )

        tracked = resource("landing")
        self.assertEqual(
            audit_public_web.resource_for({"resources": [tracked]}, LANDING_URL)["id"],
            "landing",
        )
        self.assert_audit_error(
            "E_POLICY",
            lambda: audit_public_web.resource_for({"resources": []}, LANDING_URL),
        )
        self.assert_audit_error(
            "E_POLICY",
            lambda: audit_public_web.resource_for(
                {"resources": [tracked, dict(tracked)]},
                LANDING_URL,
            ),
        )
        self.assertIsNone(
            audit_public_web.NoRedirect().redirect_request(
                urllib.request.Request(LANDING_URL),
                object(),
                302,
                "found",
                object(),
                BOARD_URL,
            )
        )

    def test_fetch_validation_rejects_each_policy_violation(self) -> None:
        rule = resource("landing", max_hops=0)
        hop = audit_public_web.RedirectHop(LANDING_URL, 302, BOARD_URL)
        self.assert_audit_error(
            "E_REDIRECT_HOPS",
            lambda: audit_public_web.validate_fetch(
                audit_public_web.FetchResult(BOARD_URL, 200, [hop], b"required marker"),
                rule,
            ),
        )

        redirect_rule = resource("landing")
        audit_public_web.validate_fetch(
            audit_public_web.FetchResult(
                BOARD_URL,
                200,
                [hop],
                b"required marker",
            ),
            redirect_rule,
        )
        evil_hop = audit_public_web.RedirectHop(
            LANDING_URL,
            302,
            "https://evil.test/path",
        )
        self.assert_audit_error(
            "E_REDIRECT_ORIGIN",
            lambda: audit_public_web.validate_fetch(
                audit_public_web.FetchResult(
                    LANDING_URL,
                    200,
                    [evil_hop],
                    b"required marker",
                ),
                redirect_rule,
            ),
        )
        self.assert_audit_error(
            "E_REDIRECT_ORIGIN",
            lambda: audit_public_web.validate_fetch(
                audit_public_web.FetchResult(
                    "https://evil.test/path",
                    200,
                    [],
                    b"required marker",
                ),
                redirect_rule,
            ),
        )
        self.assert_audit_error(
            "E_STATUS",
            lambda: audit_public_web.validate_fetch(
                audit_public_web.FetchResult(LANDING_URL, 503, [], b"required marker"),
                redirect_rule,
            ),
        )
        self.assert_audit_error(
            "E_MARKER",
            lambda: audit_public_web.validate_fetch(
                audit_public_web.FetchResult(LANDING_URL, 200, [], b"other"),
                redirect_rule,
            ),
        )

    def test_fetch_url_handles_redirects_http_errors_and_size_limits(self) -> None:
        redirect = FakeResponse(302, location="board.html#top")
        terminal = FakeResponse(200, b"required marker")
        opener = ScriptedOpener([redirect, terminal])
        with mock.patch.object(
            audit_public_web.urllib.request,
            "build_opener",
            return_value=opener,
        ):
            result = audit_public_web.fetch_url(
                f"{LANDING_URL}#start",
                resource("landing", max_hops=1),
                user_agent="audit-test/1",
                timeout=7,
                maximum_bytes=64,
            )
        self.assertEqual(result.url, BOARD_URL)
        self.assertEqual(result.status, 200)
        self.assertEqual(result.body, b"required marker")
        self.assertEqual(len(result.redirects), 1)
        self.assertEqual(result.redirects[0].target, f"{BOARD_URL}#top")
        self.assertEqual(opener.timeouts, [7, 7])
        self.assertEqual(
            opener.requests[0].get_header("User-agent"),
            "audit-test/1",
        )
        self.assertEqual(terminal.read_limit, 65)
        self.assertTrue(redirect.closed)
        self.assertTrue(terminal.closed)

        headers = email.message.Message()
        http_error = urllib.error.HTTPError(
            LANDING_URL,
            404,
            "not found",
            headers,
            io.BytesIO(b"missing"),
        )
        error_opener = ScriptedOpener([http_error])
        with mock.patch.object(
            audit_public_web.urllib.request,
            "build_opener",
            return_value=error_opener,
        ):
            error_result = audit_public_web.fetch_url(
                LANDING_URL,
                resource("landing"),
                user_agent="audit-test/1",
                timeout=3,
                maximum_bytes=64,
            )
        self.assertEqual(error_result.status, 404)
        self.assertEqual(error_result.body, b"missing")

        missing_location = FakeResponse(302)
        with mock.patch.object(
            audit_public_web.urllib.request,
            "build_opener",
            return_value=ScriptedOpener([missing_location]),
        ):
            self.assert_audit_error(
                "E_REDIRECT",
                lambda: audit_public_web.fetch_url(
                    LANDING_URL,
                    resource("landing"),
                    user_agent="audit-test/1",
                    timeout=3,
                    maximum_bytes=64,
                ),
            )
        self.assertTrue(missing_location.closed)

        too_many = FakeResponse(302, location=BOARD_URL)
        with mock.patch.object(
            audit_public_web.urllib.request,
            "build_opener",
            return_value=ScriptedOpener([too_many]),
        ):
            self.assert_audit_error(
                "E_REDIRECT_HOPS",
                lambda: audit_public_web.fetch_url(
                    LANDING_URL,
                    resource("landing", max_hops=0),
                    user_agent="audit-test/1",
                    timeout=3,
                    maximum_bytes=64,
                ),
            )

        oversized = FakeResponse(200, b"12345")
        with mock.patch.object(
            audit_public_web.urllib.request,
            "build_opener",
            return_value=ScriptedOpener([oversized]),
        ):
            self.assert_audit_error(
                "E_RESPONSE_SIZE",
                lambda: audit_public_web.fetch_url(
                    LANDING_URL,
                    resource("landing"),
                    user_agent="audit-test/1",
                    timeout=3,
                    maximum_bytes=4,
                ),
            )
        self.assertTrue(oversized.closed)

    def test_board_provenance_rejects_every_mismatch(self) -> None:
        self.assert_audit_error(
            "E_REVISION",
            lambda: audit_public_web.audit_board(
                b"",
                "short",
                lambda _path: b"",
                b"",
            ),
        )
        deployed = board_bytes()
        self.assert_audit_error(
            "E_GENERATED_BYTES",
            lambda: audit_public_web.audit_board(
                deployed,
                REVISION,
                lambda _path: b"",
                deployed + b"\n",
            ),
        )
        wrong_link_revision = board_bytes(link_revision=OTHER_REVISION)
        self.assert_audit_error(
            "E_SOURCE_REVISION",
            lambda: audit_public_web.audit_board(
                wrong_link_revision,
                REVISION,
                lambda _path: b"---\nid: B001\n---\n",
                wrong_link_revision,
            ),
        )
        wrong_identifier = board_bytes(link_text="not-an-id")
        self.assert_audit_error(
            "E_SOURCE_ID",
            lambda: audit_public_web.audit_board(
                wrong_identifier,
                REVISION,
                lambda _path: b"---\nid: B001\n---\n",
                wrong_identifier,
            ),
        )
        self.assert_audit_error(
            "E_SOURCE_MISSING",
            lambda: audit_public_web.audit_board(
                deployed,
                REVISION,
                lambda _path: b"",
                deployed,
            ),
        )
        self.assert_audit_error(
            "E_SOURCE_MARKER",
            lambda: audit_public_web.audit_board(
                deployed,
                REVISION,
                lambda _path: b"---\nid: B002\n---\n",
                deployed,
            ),
        )
        no_sources = board_bytes(include_source=False)
        self.assert_audit_error(
            "E_SOURCE_INVENTORY",
            lambda: audit_public_web.audit_board(
                no_sources,
                REVISION,
                lambda _path: b"",
                no_sources,
            ),
        )
        with_untracked_link = deployed + b'<a href="https://example.test/docs">Docs</a>'
        result = audit_public_web.audit_board(
            with_untracked_link,
            REVISION,
            lambda _path: b"---\nid: B001\n---\n",
            with_untracked_link,
        )
        self.assertEqual(result["source_link_count"], 1)

    def test_landing_inventory_fragment_and_board_fallback_rejections(self) -> None:
        landing = (
            '<div id="product-marker"></div><section id="why"></section><a href="#why">Why</a>'
        ).encode()
        board = board_bytes()
        policy = policy_for(landing, ["#why"])
        responses = {
            LANDING_URL: audit_public_web.FetchResult(LANDING_URL, 200, [], landing),
            BOARD_URL: audit_public_web.FetchResult(BOARD_URL, 200, [], board),
        }
        calls: List[str] = []

        def fetch(url: str, _rule: Mapping[str, Any]) -> audit_public_web.FetchResult:
            calls.append(url)
            return responses[url]

        result = audit_public_web.audit(
            policy,
            LANDING_URL,
            REVISION,
            fetch=fetch,
            source_loader=lambda _path: b"---\nid: B001\n---\n",
            generated_board=board,
        )
        self.assertEqual(calls, [LANDING_URL, BOARD_URL])
        self.assertEqual(result["unique_resource_count"], 1)
        self.assertEqual(result["source_link_count"], 1)

        count_policy = policy_for(landing, ["#why"])
        count_policy["landing"]["anchor_count"] = 2  # type: ignore[index]
        self.assert_audit_error(
            "E_ANCHOR_COUNT",
            lambda: audit_public_web.audit(
                count_policy,
                LANDING_URL,
                REVISION,
                fetch=fetch,
                source_loader=lambda _path: b"",
                generated_board=board,
            ),
        )

        inventory_policy = policy_for(landing, ["#other"])
        self.assert_audit_error(
            "E_ANCHOR_INVENTORY",
            lambda: audit_public_web.audit(
                inventory_policy,
                LANDING_URL,
                REVISION,
                fetch=fetch,
                source_loader=lambda _path: b"",
                generated_board=board,
            ),
        )

        undeclared = (
            '<div id="product-marker"></div><section id="other"></section>'
            '<a href="#other">Other</a>'
        ).encode()
        undeclared_policy = policy_for(undeclared, ["#other"])
        undeclared_responses = {
            LANDING_URL: audit_public_web.FetchResult(
                LANDING_URL,
                200,
                [],
                undeclared,
            )
        }
        self.assert_audit_error(
            "E_FRAGMENT_POLICY",
            lambda: audit_public_web.audit(
                undeclared_policy,
                LANDING_URL,
                REVISION,
                fetch=lambda url, _rule: undeclared_responses[url],
                source_loader=lambda _path: b"",
                generated_board=board,
            ),
        )

        duplicate = (
            '<div id="product-marker"></div><section id="why"></section>'
            '<section id="why"></section><a href="#why">Why</a>'
        ).encode()
        duplicate_policy = policy_for(duplicate, ["#why"])
        duplicate_responses = {
            LANDING_URL: audit_public_web.FetchResult(
                LANDING_URL,
                200,
                [],
                duplicate,
            )
        }
        self.assert_audit_error(
            "E_FRAGMENT_TARGET",
            lambda: audit_public_web.audit(
                duplicate_policy,
                LANDING_URL,
                REVISION,
                fetch=lambda url, _rule: duplicate_responses[url],
                source_loader=lambda _path: b"",
                generated_board=board,
            ),
        )

    def test_duplicate_resources_are_fetched_once(self) -> None:
        landing = (
            '<div id="product-marker"></div>'
            '<a href="/engineering-board/board.html">Board one</a>'
            '<a href="/engineering-board/board.html">Board two</a>'
        ).encode()
        board = board_bytes()
        hrefs = [
            "/engineering-board/board.html",
            "/engineering-board/board.html",
        ]
        policy = policy_for(landing, hrefs)
        policy["landing"]["href_inventory"] = [  # type: ignore[index]
            "/engineering-board/board.html"
        ]
        calls: List[str] = []
        responses = {
            LANDING_URL: audit_public_web.FetchResult(LANDING_URL, 200, [], landing),
            BOARD_URL: audit_public_web.FetchResult(BOARD_URL, 200, [], board),
        }

        def fetch(url: str, _rule: Mapping[str, Any]) -> audit_public_web.FetchResult:
            calls.append(url)
            return responses[url]

        result = audit_public_web.audit(
            policy,
            LANDING_URL,
            REVISION,
            fetch=fetch,
            source_loader=lambda _path: b"---\nid: B001\n---\n",
            generated_board=board,
        )
        self.assertEqual(calls, [LANDING_URL, BOARD_URL])
        self.assertEqual(result["anchor_count"], 2)
        self.assertEqual(len(result["anchors"]), 2)

    def test_git_archive_and_generation_faults_are_stable(self) -> None:
        success = subprocess.CompletedProcess([], 0, stdout=b"source", stderr=b"")
        with mock.patch.object(audit_public_web.subprocess, "run", return_value=success):
            self.assertEqual(
                audit_public_web.git_bytes(ROOT, REVISION, "path.md"),
                b"source",
            )
        failure = subprocess.CompletedProcess([], 1, stdout=b"", stderr=b"missing")
        with mock.patch.object(audit_public_web.subprocess, "run", return_value=failure):
            self.assert_audit_error(
                "E_SOURCE_MISSING",
                lambda: audit_public_web.git_bytes(ROOT, REVISION, "path.md"),
            )

        with tempfile.TemporaryDirectory() as raw:
            destination = Path(raw) / "checkout"
            self.assert_audit_error(
                "E_REVISION",
                lambda: self.run_safe_archive(failure, destination),
            )

            safe_tar = self.make_tar({"dir/": None, "dir/file.txt": b"content"})
            self.run_safe_archive(
                subprocess.CompletedProcess([], 0, stdout=safe_tar, stderr=b""),
                destination,
            )
            self.assertEqual(
                (destination / "dir" / "file.txt").read_bytes(),
                b"content",
            )

            unsafe_tar = self.make_tar({"../escape.txt": b"escape"})
            self.assert_audit_error(
                "E_ARCHIVE_PATH",
                lambda: self.run_safe_archive(
                    subprocess.CompletedProcess([], 0, stdout=unsafe_tar, stderr=b""),
                    destination,
                ),
            )

            link_tar = self.make_tar({"link": ("symlink", "target")})
            self.assert_audit_error(
                "E_ARCHIVE_TYPE",
                lambda: self.run_safe_archive(
                    subprocess.CompletedProcess([], 0, stdout=link_tar, stderr=b""),
                    destination,
                ),
            )

            member = tarfile.TarInfo("file.txt")
            member.size = 1
            fake_archive = mock.MagicMock()
            fake_archive.__enter__.return_value = fake_archive
            fake_archive.__exit__.return_value = None
            fake_archive.getmembers.return_value = [member]
            fake_archive.extractfile.return_value = None
            with (
                mock.patch.object(
                    audit_public_web.subprocess,
                    "run",
                    return_value=subprocess.CompletedProcess(
                        [],
                        0,
                        stdout=b"tar",
                        stderr=b"",
                    ),
                ),
                mock.patch.object(
                    audit_public_web.tarfile,
                    "open",
                    return_value=fake_archive,
                ),
            ):
                self.assert_audit_error(
                    "E_ARCHIVE_READ",
                    lambda: audit_public_web.safe_archive(
                        ROOT,
                        REVISION,
                        destination,
                    ),
                )

        generated = subprocess.CompletedProcess(
            [],
            0,
            stdout=b"<html>generated</html>",
            stderr=b"",
        )
        with (
            mock.patch.object(audit_public_web, "safe_archive") as archive,
            mock.patch.object(
                audit_public_web.subprocess,
                "run",
                return_value=generated,
            ) as run,
        ):
            self.assertEqual(
                audit_public_web.generate_board(ROOT, REVISION),
                b"<html>generated</html>",
            )
        archive.assert_called_once()
        command = run.call_args.args[0]
        self.assertEqual(command[0], "bash")
        self.assertIn("--revision", command)
        self.assertIn(REVISION, command)
        self.assertEqual(
            run.call_args.kwargs["env"]["CLAUDE_PROJECT_DIR"],
            str(run.call_args.kwargs["cwd"]),
        )

        generation_failure = subprocess.CompletedProcess(
            [],
            1,
            stdout=b"",
            stderr=b"bad \xff diagnostic\n",
        )
        with (
            mock.patch.object(audit_public_web, "safe_archive"),
            mock.patch.object(
                audit_public_web.subprocess,
                "run",
                return_value=generation_failure,
            ),
        ):
            error = self.assert_audit_error(
                "E_GENERATION",
                lambda: audit_public_web.generate_board(ROOT, REVISION),
            )
        self.assertIn("bad \ufffd diagnostic", str(error))

    def test_main_writes_deterministic_output_and_injects_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            policy_path = root / "policy.json"
            output = root / "nested" / "audit.json"
            policy = {
                "landing": {"canonical_url": LANDING_URL},
                "crawl": {
                    "user_agent": "audit-test/1",
                    "timeout_seconds": 9,
                    "max_response_bytes": 1234,
                },
            }
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            args = argparse.Namespace(
                repository=root,
                policy=policy_path,
                landing_url=None,
                expected_revision=REVISION,
                output=output,
            )
            fetch_result = audit_public_web.FetchResult(
                LANDING_URL,
                200,
                [],
                b"landing",
            )

            def fake_audit(
                received_policy: Mapping[str, Any],
                landing_url: str,
                revision: str,
                *,
                fetch: Any,
                source_loader: Any,
                generated_board: bytes,
            ) -> Dict[str, object]:
                self.assertEqual(received_policy, policy)
                self.assertEqual(landing_url, LANDING_URL)
                self.assertEqual(revision, REVISION)
                self.assertEqual(generated_board, b"generated")
                self.assertEqual(
                    fetch(LANDING_URL, resource("landing")),
                    fetch_result,
                )
                self.assertEqual(
                    source_loader("bugs/B001-example.md"),
                    b"source",
                )
                return {"schema_version": "1", "revision": revision}

            stdout = io.StringIO()
            with (
                mock.patch.object(audit_public_web, "parse_args", return_value=args),
                mock.patch.object(
                    audit_public_web,
                    "generate_board",
                    return_value=b"generated",
                ),
                mock.patch.object(
                    audit_public_web,
                    "fetch_url",
                    return_value=fetch_result,
                ) as fetch_url,
                mock.patch.object(
                    audit_public_web,
                    "git_bytes",
                    return_value=b"source",
                ) as git_bytes,
                mock.patch.object(audit_public_web, "audit", side_effect=fake_audit),
                contextlib.redirect_stdout(stdout),
            ):
                self.assertEqual(audit_public_web.main(), 0)
                args.output = None
                stdout_without_output = io.StringIO()
                with contextlib.redirect_stdout(stdout_without_output):
                    self.assertEqual(audit_public_web.main(), 0)

            payload = stdout.getvalue()
            self.assertEqual(output.read_text(encoding="utf-8"), payload)
            self.assertEqual(stdout_without_output.getvalue(), payload)
            decoded = json.loads(payload)
            self.assertEqual(decoded["revision"], REVISION)
            self.assertEqual(
                decoded["policy_sha256"],
                audit_public_web.hashlib.sha256(policy_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(fetch_url.call_count, 2)
            self.assertEqual(fetch_url.call_args.kwargs["user_agent"], "audit-test/1")
            self.assertEqual(fetch_url.call_args.kwargs["timeout"], 9)
            self.assertEqual(fetch_url.call_args.kwargs["maximum_bytes"], 1234)
            self.assertEqual(git_bytes.call_count, 2)
            git_bytes.assert_called_with(
                root.resolve(),
                REVISION,
                "engineering-board/eb-self/bugs/B001-example.md",
            )

    def test_cli_reports_top_level_file_and_json_errors_without_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            missing = self.run_cli(root, root / "missing.json")
            self.assertEqual(missing.returncode, 1)
            self.assertEqual(missing.stdout, "")
            self.assertTrue(missing.stderr.startswith("public-web-audit: "))
            self.assertIn("missing.json", missing.stderr)

            invalid = root / "invalid.json"
            invalid.write_text("{", encoding="utf-8")
            malformed = self.run_cli(root, invalid)
            self.assertEqual(malformed.returncode, 1)
            self.assertEqual(malformed.stdout, "")
            self.assertTrue(malformed.stderr.startswith("public-web-audit: "))
            self.assertIn("Expecting property name", malformed.stderr)

    @staticmethod
    def run_cli(root: Path, policy_path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--repository",
                str(root),
                "--policy",
                str(policy_path),
                "--expected-revision",
                REVISION,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    @staticmethod
    def run_safe_archive(
        completed: subprocess.CompletedProcess[bytes],
        destination: Path,
    ) -> None:
        with mock.patch.object(
            audit_public_web.subprocess,
            "run",
            return_value=completed,
        ):
            audit_public_web.safe_archive(ROOT, REVISION, destination)

    @staticmethod
    def make_tar(entries: Mapping[str, object]) -> bytes:
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w:") as archive:
            for name, value in entries.items():
                member = tarfile.TarInfo(name)
                if value is None:
                    member.type = tarfile.DIRTYPE
                    archive.addfile(member)
                elif isinstance(value, tuple):
                    member.type = tarfile.SYMTYPE
                    member.linkname = str(value[1])
                    archive.addfile(member)
                else:
                    assert isinstance(value, bytes)
                    member.size = len(value)
                    archive.addfile(member, io.BytesIO(value))
        return stream.getvalue()


if __name__ == "__main__":
    unittest.main(verbosity=2)
