#!/usr/bin/env python3
"""Audit deployed landing links and canonical board provenance."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple, cast


FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
SOURCE_URL = re.compile(
    r"^https://github\.com/GhostlyGawd/engineering-board/blob/"
    r"(?P<revision>[0-9a-f]{40})/engineering-board/eb-self/"
    r"(?P<source>(?:bugs|features|questions|observations|learnings|hypotheses)/"
    r"[^/?#]+\.md)$"
)
ENTRY_ID = re.compile(r"^[BFQOLH][0-9]{3}$")


class AuditError(RuntimeError):
    """A stable public-audit failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code} {message}")
        self.code = code


@dataclass(frozen=True)
class RedirectHop:
    source: str
    status: int
    target: str


@dataclass(frozen=True)
class FetchResult:
    url: str
    status: int
    redirects: List[RedirectHop]
    body: bytes


class AnchorParser(HTMLParser):
    """Collect anchors and exact fragment identifiers from one document."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: List[Dict[str, str]] = []
        self.ids: Dict[str, int] = {}
        self._anchor: Optional[Dict[str, object]] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids[element_id] = self.ids.get(element_id, 0) + 1
        if tag != "a":
            return
        classes = (values.get("class") or "").split()
        self._anchor = {
            "href": values.get("href") or "",
            "text": [],
            "classes": " ".join(classes),
        }

    def handle_data(self, data: str) -> None:
        if self._anchor is None:
            return
        chunks = self._anchor["text"]
        assert isinstance(chunks, list)
        chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self._anchor is None:
            return
        chunks = self._anchor["text"]
        assert isinstance(chunks, list)
        self.anchors.append(
            {
                "href": str(self._anchor["href"]),
                "text": " ".join("".join(chunks).split()),
                "classes": str(self._anchor["classes"]),
            }
        )
        self._anchor = None


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        request: urllib.request.Request,
        file_pointer: object,
        code: int,
        message: str,
        headers: object,
        new_url: str,
    ) -> None:
        del request, file_pointer, code, message, headers, new_url
        return None


def origin(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise AuditError("E_UNSAFE_URL", f"unsafe HTTPS URL refused: {url}")
    host = parsed.hostname.lower()
    port = f":{parsed.port}" if parsed.port not in (None, 443) else ""
    return f"https://{host}{port}"


def normalize_url(value: str, base: str) -> str:
    if not value or any(ord(character) < 32 for character in value):
        raise AuditError("E_UNSAFE_URL", "empty or control-bearing URL refused")
    joined = urllib.parse.urljoin(base, value)
    parsed = urllib.parse.urlsplit(joined)
    normalized_origin = origin(joined)
    path = parsed.path or "/"
    return urllib.parse.urlunsplit(
        (
            "https",
            normalized_origin[len("https://") :],
            path,
            parsed.query,
            parsed.fragment,
        )
    )


def resource_for(
    policy: Mapping[str, Any],
    url: str,
) -> Mapping[str, Any]:
    parsed = urllib.parse.urlsplit(url)
    normalized_origin = origin(url)
    resources = cast(List[Mapping[str, Any]], policy["resources"])
    matches = [
        rule
        for rule in resources
        if rule["origin"] == normalized_origin
        and re.fullmatch(rule["path_pattern"], parsed.path or "/")
        and re.fullmatch(rule["query_pattern"], parsed.query)
    ]
    if len(matches) != 1:
        raise AuditError(
            "E_POLICY",
            f"URL must match exactly one tracked resource, found {len(matches)}: {url}",
        )
    return matches[0]


def validate_fetch(result: FetchResult, rule: Mapping[str, Any]) -> None:
    permitted = set(rule["permitted_redirect_origins"])
    if len(result.redirects) > rule["max_redirect_hops"]:
        raise AuditError(
            "E_REDIRECT_HOPS",
            f"{rule['id']} exceeded its redirect limit",
        )
    for hop in result.redirects:
        if origin(hop.target) not in permitted:
            raise AuditError(
                "E_REDIRECT_ORIGIN",
                f"{rule['id']} redirected to unapproved origin {origin(hop.target)}",
            )
    if origin(result.url) not in permitted:
        raise AuditError(
            "E_REDIRECT_ORIGIN",
            f"{rule['id']} terminated on unapproved origin {origin(result.url)}",
        )
    if result.status not in rule["accepted_terminal_statuses"]:
        raise AuditError(
            "E_STATUS",
            f"{rule['id']} returned terminal status {result.status}",
        )
    marker = rule["content_marker"].encode("utf-8")
    if marker not in result.body:
        raise AuditError(
            "E_MARKER",
            f"{rule['id']} did not contain its declared content marker",
        )


def fetch_url(
    url: str,
    rule: Mapping[str, Any],
    *,
    user_agent: str,
    timeout: int,
    maximum_bytes: int,
) -> FetchResult:
    opener = urllib.request.build_opener(NoRedirect())
    current = urllib.parse.urldefrag(url)[0]
    redirects: List[RedirectHop] = []
    while True:
        request = urllib.request.Request(
            current,
            headers={
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.1",
            },
        )
        response: Any
        try:
            response = opener.open(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            response = exc
        status = int(response.getcode())
        if 300 <= status <= 399:
            target = response.headers.get("Location")
            response.close()
            if not target:
                raise AuditError("E_REDIRECT", f"redirect without Location: {current}")
            normalized_target = normalize_url(target, current)
            redirects.append(RedirectHop(current, status, normalized_target))
            if len(redirects) > int(rule["max_redirect_hops"]):
                raise AuditError(
                    "E_REDIRECT_HOPS",
                    f"{rule['id']} exceeded its redirect limit",
                )
            current = urllib.parse.urldefrag(normalized_target)[0]
            continue
        body = response.read(maximum_bytes + 1)
        response.close()
        if len(body) > maximum_bytes:
            raise AuditError(
                "E_RESPONSE_SIZE",
                f"{rule['id']} exceeded the response-byte limit",
            )
        return FetchResult(current, status, redirects, body)


def audit_board(
    board: bytes,
    revision: str,
    source_loader: Callable[[str], bytes],
    generated_board: bytes,
) -> Dict[str, Any]:
    if not FULL_SHA.fullmatch(revision):
        raise AuditError("E_REVISION", "expected revision must be one full SHA")
    displayed = re.findall(
        rb"Generated from <code>([0-9a-f]{40})</code>",
        board,
    )
    if displayed != [revision.encode("ascii")]:
        raise AuditError(
            "E_REVISION",
            "board must display the expected full source SHA exactly once",
        )
    if board != generated_board:
        raise AuditError(
            "E_GENERATED_BYTES",
            "deployed board bytes differ from independent canonical generation",
        )

    parser = AnchorParser()
    parser.feed(board.decode("utf-8"))
    source_links: List[Dict[str, str]] = []
    for anchor in parser.anchors:
        match = SOURCE_URL.fullmatch(urllib.parse.urldefrag(anchor["href"])[0])
        if not match:
            continue
        if match.group("revision") != revision:
            raise AuditError(
                "E_SOURCE_REVISION",
                f"source link is not pinned to displayed revision: {anchor['href']}",
            )
        entry_id = anchor["text"]
        if not ENTRY_ID.fullmatch(entry_id):
            raise AuditError(
                "E_SOURCE_ID",
                f"source link has a noncanonical identifier: {entry_id!r}",
            )
        source = match.group("source")
        source_bytes = source_loader(source)
        if not source_bytes:
            raise AuditError("E_SOURCE_MISSING", f"source path is unavailable: {source}")
        identifier = re.search(
            rb"(?m)^id:\s*([BFQOLH][0-9]{3})\s*$",
            source_bytes,
        )
        if identifier is None or identifier.group(1).decode("ascii") != entry_id:
            raise AuditError(
                "E_SOURCE_MARKER",
                f"source file does not contain the linked identifier: {source}",
            )
        source_links.append(
            {
                "id": entry_id,
                "path": source,
                "url": anchor["href"],
            }
        )
    if not source_links:
        raise AuditError("E_SOURCE_INVENTORY", "board contains no immutable source links")
    return {
        "board_sha256": hashlib.sha256(board).hexdigest(),
        "generated_sha256": hashlib.sha256(generated_board).hexdigest(),
        "source_link_count": len(source_links),
        "source_links": source_links,
    }


def audit(
    policy: Mapping[str, Any],
    landing_url: str,
    revision: str,
    *,
    fetch: Callable[[str, Mapping[str, Any]], FetchResult],
    source_loader: Callable[[str], bytes],
    generated_board: bytes,
) -> Dict[str, Any]:
    canonical_landing = normalize_url(landing_url, landing_url)
    landing_rule = resource_for(policy, canonical_landing)
    landing_result = fetch(urllib.parse.urldefrag(canonical_landing)[0], landing_rule)
    validate_fetch(landing_result, landing_rule)

    parser = AnchorParser()
    parser.feed(landing_result.body.decode("utf-8"))
    hrefs = [anchor["href"] for anchor in parser.anchors]
    if len(hrefs) != policy["landing"]["anchor_count"]:
        raise AuditError("E_ANCHOR_COUNT", "landing anchor count does not match policy")
    if sorted(set(hrefs)) != sorted(policy["landing"]["href_inventory"]):
        raise AuditError(
            "E_ANCHOR_INVENTORY",
            "landing href inventory does not match policy",
        )

    fetched: Dict[str, FetchResult] = {urllib.parse.urldefrag(canonical_landing)[0]: landing_result}
    records: List[Dict[str, Any]] = []
    for anchor in parser.anchors:
        normalized = normalize_url(anchor["href"], canonical_landing)
        rule = resource_for(policy, normalized)
        parsed = urllib.parse.urlsplit(normalized)
        if parsed.fragment:
            if parsed.fragment not in rule["fragment_targets"]:
                raise AuditError(
                    "E_FRAGMENT_POLICY",
                    f"fragment is not declared for {rule['id']}: {parsed.fragment}",
                )
            if rule["id"] == "landing" and parser.ids.get(parsed.fragment) != 1:
                raise AuditError(
                    "E_FRAGMENT_TARGET",
                    f"landing fragment is not unique: {parsed.fragment}",
                )
        request_url = urllib.parse.urldefrag(normalized)[0]
        result = fetched.get(request_url)
        if result is None:
            result = fetch(request_url, rule)
            validate_fetch(result, rule)
            fetched[request_url] = result
        records.append(
            {
                "href": anchor["href"],
                "normalized_url": normalized,
                "resource_id": rule["id"],
                "redirects": [
                    {
                        "source": hop.source,
                        "status": hop.status,
                        "target": hop.target,
                    }
                    for hop in result.redirects
                ],
                "terminal_status": result.status,
                "terminal_url": result.url,
                "marker_sha256": hashlib.sha256(rule["content_marker"].encode("utf-8")).hexdigest(),
            }
        )

    board_url = urllib.parse.urljoin(
        canonical_landing,
        policy["landing"].get("board_path", "/engineering-board/board.html"),
    )
    board_result = fetched.get(board_url)
    if board_result is None:
        board_rule = resource_for(policy, board_url)
        board_result = fetch(board_url, board_rule)
        validate_fetch(board_result, board_rule)
    board_audit = audit_board(
        board_result.body,
        revision,
        source_loader,
        generated_board,
    )
    return {
        "schema_version": "1",
        "landing_url": canonical_landing,
        "landing_sha256": hashlib.sha256(landing_result.body).hexdigest(),
        "revision": revision,
        "anchor_count": len(records),
        "unique_resource_count": len(fetched),
        "anchors": records,
        **board_audit,
    }


def git_bytes(repository: Path, revision: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repository), "show", f"{revision}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise AuditError(
            "E_SOURCE_MISSING",
            f"git source is unavailable at {revision}:{path}",
        )
    return completed.stdout


def safe_archive(repository: Path, revision: str, destination: Path) -> None:
    completed = subprocess.run(
        ["git", "-C", str(repository), "archive", "--format=tar", revision],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise AuditError("E_REVISION", "cannot archive the expected revision")
    with tarfile.open(fileobj=io.BytesIO(completed.stdout), mode="r:") as archive:
        for member in archive.getmembers():
            relative = PurePosixPath(member.name)
            if relative.is_absolute() or ".." in relative.parts:
                raise AuditError("E_ARCHIVE_PATH", "unsafe archive path refused")
            target = destination.joinpath(*relative.parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile():
                raise AuditError(
                    "E_ARCHIVE_TYPE",
                    f"non-regular archive member refused: {member.name}",
                )
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise AuditError("E_ARCHIVE_READ", f"cannot read {member.name}")
            target.write_bytes(source.read())


def generate_board(repository: Path, revision: str) -> bytes:
    with tempfile.TemporaryDirectory(prefix="engineering-board-public-audit-") as raw:
        checkout = Path(raw)
        safe_archive(repository, revision, checkout)
        environment = os.environ.copy()
        environment["CLAUDE_PROJECT_DIR"] = str(checkout)
        completed = subprocess.run(
            [
                "bash",
                str(checkout / "hooks" / "scripts" / "board-view.sh"),
                "eb-self",
                "--stdout",
                "--stamp",
                "--revision",
                revision,
                "--link-base",
                "https://github.com/GhostlyGawd/engineering-board/blob/"
                f"{revision}/engineering-board/eb-self/",
            ],
            cwd=checkout,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if completed.returncode != 0:
            diagnostic = completed.stderr.decode("utf-8", errors="replace").strip()
            raise AuditError(
                "E_GENERATION",
                f"independent canonical generation failed: {diagnostic}",
            )
        return completed.stdout


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit deployed landing links and canonical board provenance."
    )
    parser.add_argument(
        "--repository",
        type=Path,
        default=Path.cwd(),
        help="repository containing the expected source revision",
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path("support/web/public-link-policy.json"),
    )
    parser.add_argument("--landing-url")
    parser.add_argument("--expected-revision", required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    repository = args.repository.resolve()
    policy_path = args.policy if args.policy.is_absolute() else repository / args.policy
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    landing_url = args.landing_url or policy["landing"]["canonical_url"]
    crawl = policy["crawl"]

    def network_fetch(url: str, rule: Mapping[str, Any]) -> FetchResult:
        return fetch_url(
            url,
            rule,
            user_agent=crawl["user_agent"],
            timeout=int(crawl["timeout_seconds"]),
            maximum_bytes=int(crawl["max_response_bytes"]),
        )

    generated = generate_board(repository, args.expected_revision)
    result = audit(
        policy,
        landing_url,
        args.expected_revision,
        fetch=network_fetch,
        source_loader=lambda source: git_bytes(
            repository,
            args.expected_revision,
            f"engineering-board/eb-self/{source}",
        ),
        generated_board=generated,
    )
    result["policy_sha256"] = hashlib.sha256(policy_path.read_bytes()).hexdigest()
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"public-web-audit: {exc}", file=sys.stderr)
        raise SystemExit(1)
