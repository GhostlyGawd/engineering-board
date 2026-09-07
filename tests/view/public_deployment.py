#!/usr/bin/env python3
"""Repository contract for public Pages links and deployment provenance."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_public_web  # noqa: E402

LANDING = ROOT / "docs" / "index.html"
POLICY = ROOT / "support" / "web" / "public-link-policy.json"
SCHEMA = ROOT / "support" / "web" / "public-link-policy.schema.json"
WORKFLOW = ROOT / ".github" / "workflows" / "pages.yml"


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: List[Dict[str, str]] = []
        self._anchor: Optional[Dict[str, object]] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag != "a":
            return
        values = dict(attrs)
        self._anchor = {
            "id": values.get("id") or "",
            "href": values.get("href") or "",
            "text": [],
        }

    def handle_data(self, data: str) -> None:
        if self._anchor is not None:
            text = self._anchor["text"]
            assert isinstance(text, list)
            text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self._anchor is None:
            return
        text = self._anchor["text"]
        assert isinstance(text, list)
        self.anchors.append(
            {
                "id": str(self._anchor["id"]),
                "href": str(self._anchor["href"]),
                "text": " ".join("".join(text).split()),
            }
        )
        self._anchor = None


class PublicDeploymentContractTest(unittest.TestCase):
    def test_landing_anchor_inventory_has_a_versioned_policy(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(policy["$schema"], "./public-link-policy.schema.json")
        self.assertEqual(policy["schema_version"], "1")
        self.assertEqual(
            schema["properties"]["schema_version"]["const"],
            policy["schema_version"],
        )

        parser = AnchorParser()
        parser.feed(LANDING.read_text(encoding="utf-8"))
        self.assertEqual(len(parser.anchors), policy["landing"]["anchor_count"])
        self.assertEqual(
            sorted({anchor["href"] for anchor in parser.anchors}),
            sorted(policy["landing"]["href_inventory"]),
        )
        self.assertTrue(all(anchor["href"] for anchor in parser.anchors))
        self.assertEqual(
            len(policy["resources"]),
            len({resource["id"] for resource in policy["resources"]}),
        )

    def test_every_live_board_affordance_uses_the_canonical_pages_path(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        canonical_path = policy["landing"]["board_path"]
        parser = AnchorParser()
        parser.feed(LANDING.read_text(encoding="utf-8"))

        board_anchors = [
            anchor for anchor in parser.anchors if anchor["href"].endswith("board.html")
        ]
        self.assertGreaterEqual(len(board_anchors), 5)
        self.assertEqual(
            {anchor["href"] for anchor in board_anchors},
            {canonical_path},
        )

    def test_pages_workflow_generates_revision_pinned_board_at_deploy_time(
        self,
    ) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotRegex(workflow, r"(?m)^\s+push:\s*$")
        self.assertIn("environment:", workflow)
        self.assertIn("name: github-pages", workflow)
        self.assertIn('SOURCE_SHA="$(git rev-parse HEAD)"', workflow)
        self.assertIn(
            'test "${SOURCE_SHA}" = "${GITHUB_SHA}"',
            workflow,
        )
        self.assertIn(
            "bash hooks/scripts/board-view.sh eb-self --stdout",
            workflow,
        )
        self.assertIn('--stamp --revision "${SOURCE_SHA}"', workflow)
        self.assertIn(
            '--link-base "https://github.com/GhostlyGawd/engineering-board/blob/${SOURCE_SHA}/engineering-board/eb-self/"',
            workflow,
        )
        self.assertNotIn(
            "cp engineering-board/eb-self/board.html",
            workflow,
        )
        self.assertNotIn("git rev-parse --short", workflow)
        self.assertNotRegex(workflow, r"git push[^\n]*\+gh-pages")
        self.assertIn("git push origin HEAD:gh-pages", workflow)

    def test_fragment_navigation_recovers_below_the_sticky_header(self) -> None:
        source = LANDING.read_text(encoding="utf-8")
        self.assertIn("section[id]{scroll-margin-top:72px}", source)
        self.assertIn("function placeHashTarget()", source)
        self.assertIn(
            'window.addEventListener("hashchange",placeHashTarget)',
            source,
        )
        self.assertIn(
            'window.addEventListener("load",placeHashTarget)',
            source,
        )
        self.assertIn("placeHashTarget();", source)
        self.assertIn(
            'target.scrollIntoView({behavior:"instant",block:"start"})',
            source,
        )
        self.assertNotIn(
            "requestAnimationFrame(function(){target.scrollIntoView",
            source,
        )

    def test_public_audit_accepts_marked_resources_and_revision_pinned_sources(
        self,
    ) -> None:
        revision = "0123456789abcdef0123456789abcdef01234567"
        landing_url = "https://example.test/engineering-board/"
        board_url = "https://example.test/engineering-board/board.html"
        source_url = (
            "https://github.com/GhostlyGawd/engineering-board/blob/"
            f"{revision}/engineering-board/eb-self/bugs/B001-example.md"
        )
        landing = (
            '<div id="product-marker"></div><section id="why"></section>'
            '<a href="#why">Why</a>'
            '<a href="/engineering-board/board.html">Board</a>'
        ).encode()
        board = (
            f"<h1>eb-self</h1> Generated from <code>{revision}</code>."
            f'<a class="cid" href="{source_url}">B001</a>'
        ).encode()
        policy = {
            "landing": {
                "canonical_url": landing_url,
                "anchor_count": 2,
                "href_inventory": ["#why", "/engineering-board/board.html"],
            },
            "crawl": {"safe_schemes": ["https"]},
            "resources": [
                self.resource(
                    "landing",
                    "https://example.test",
                    r"^/engineering-board/$",
                    'id="product-marker"',
                    ["why"],
                ),
                self.resource(
                    "board",
                    "https://example.test",
                    r"^/engineering-board/board\.html$",
                    "<h1>eb-self</h1>",
                    [],
                ),
            ],
        }
        responses = {
            landing_url: audit_public_web.FetchResult(landing_url, 200, [], landing),
            board_url: audit_public_web.FetchResult(board_url, 200, [], board),
        }

        result = audit_public_web.audit(
            policy,
            landing_url,
            revision,
            fetch=lambda url, _rule: responses[url],
            source_loader=lambda path: (
                b"---\nid: B001\ntype: bug\n---\n" if path.endswith("B001-example.md") else b""
            ),
            generated_board=board,
        )

        self.assertEqual(result["revision"], revision)
        self.assertEqual(result["anchor_count"], 2)
        self.assertEqual(result["source_link_count"], 1)

    def test_public_audit_rejects_unsafe_redirect_marker_and_revision_drift(
        self,
    ) -> None:
        rule = self.resource(
            "landing",
            "https://example.test",
            r"^/engineering-board/$",
            "required marker",
            [],
        )
        with self.assertRaisesRegex(audit_public_web.AuditError, "E_UNSAFE_URL"):
            audit_public_web.normalize_url("javascript:alert(1)", "https://example.test/")
        with self.assertRaisesRegex(audit_public_web.AuditError, "E_REDIRECT_ORIGIN"):
            audit_public_web.validate_fetch(
                audit_public_web.FetchResult(
                    "https://evil.test/",
                    200,
                    [
                        audit_public_web.RedirectHop(
                            "https://example.test/engineering-board/",
                            302,
                            "https://evil.test/",
                        )
                    ],
                    b"required marker",
                ),
                rule,
            )
        with self.assertRaisesRegex(audit_public_web.AuditError, "E_MARKER"):
            audit_public_web.validate_fetch(
                audit_public_web.FetchResult(
                    "https://example.test/engineering-board/",
                    200,
                    [],
                    b"wrong body",
                ),
                rule,
            )
        with self.assertRaisesRegex(audit_public_web.AuditError, "E_REVISION"):
            audit_public_web.audit_board(
                b"<h1>eb-self</h1>",
                "0123456789abcdef0123456789abcdef01234567",
                lambda _path: b"",
                b"<h1>eb-self</h1>",
            )

    def test_real_canonical_revision_generation_is_self_consistent(self) -> None:
        revision = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout.strip()
        generated = audit_public_web.generate_board(ROOT, revision)
        result = audit_public_web.audit_board(
            generated,
            revision,
            lambda source: audit_public_web.git_bytes(
                ROOT,
                revision,
                f"engineering-board/eb-self/{source}",
            ),
            generated,
        )
        self.assertGreaterEqual(result["source_link_count"], 80)
        self.assertEqual(result["board_sha256"], result["generated_sha256"])

    @staticmethod
    def resource(
        identifier: str,
        origin: str,
        path_pattern: str,
        marker: str,
        fragments: List[str],
    ) -> Dict[str, object]:
        return {
            "id": identifier,
            "origin": origin,
            "path_pattern": path_pattern,
            "query_pattern": "^$",
            "permitted_redirect_origins": [origin],
            "max_redirect_hops": 1,
            "accepted_terminal_statuses": [200],
            "content_marker": marker,
            "fragment_targets": fragments,
        }


if __name__ == "__main__":
    unittest.main(verbosity=2)
