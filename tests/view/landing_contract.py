#!/usr/bin/env python3
"""Validate the tracked first-visit landing contract against source HTML."""

from __future__ import annotations

import hashlib
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class LandingParser(HTMLParser):
    """Collect the small structural inventory needed by the landing policy."""

    VOID_ELEMENTS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: Dict[str, Dict[str, object]] = {}
        self.headings: List[str] = []
        self.landmarks: List[str] = []
        self._stack: List[Tuple[str, Optional[str], List[str]]] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if tag in {"header", "nav", "main", "footer"}:
            self.landmarks.append(tag)
        if element_id:
            self.elements[element_id] = {
                "tag": tag,
                "attrs": values,
                "text": "",
            }
        if tag not in self.VOID_ELEMENTS:
            self._stack.append((tag, element_id, []))

    def handle_data(self, data: str) -> None:
        for _, _, chunks in self._stack:
            chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if not self._stack:
            return
        start_tag, element_id, chunks = self._stack.pop()
        if start_tag != tag:
            return
        text = "\n".join("".join(chunks).splitlines()).strip()
        if element_id and element_id in self.elements:
            self.elements[element_id]["text"] = text
        if tag in {"h1", "h2", "h3"}:
            self.headings.append(" ".join(text.split()))


def selector_id(selector: str) -> str:
    if not selector.startswith("#"):
        raise AssertionError(f"source inventory selector must be an id: {selector}")
    return selector[1:]


def normalized_text(value: object) -> str:
    return " ".join(str(value).split())


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    policy_path = root / "support" / "web" / "web-surface-policy.json"
    schema_path = root / "support" / "web" / "web-surface-policy.schema.json"
    source_path = root / "docs" / "index.html"

    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    source = source_path.read_text(encoding="utf-8")
    assert policy["$schema"] == "./web-surface-policy.schema.json"
    assert schema["properties"]["schema_version"]["const"] == policy["schema_version"]

    parser = LandingParser()
    parser.feed(source)

    for marker in policy["first_viewport"]["markers"]:
        element = parser.elements[selector_id(marker["selector"])]
        assert normalized_text(element["text"]) == normalized_text(marker["accessible_name"])

    for item in policy["first_viewport"]["focus_order"]:
        element = parser.elements[selector_id(item["selector"])]
        name = element["attrs"].get("aria-label") or element["text"]
        assert normalized_text(name).startswith(normalized_text(item["accessible_name"]))

    no_js = policy["no_javascript"]
    assert parser.landmarks == no_js["landmarks"]
    assert parser.headings == no_js["headings"]
    for link in no_js["links"]:
        element = parser.elements[selector_id(link["selector"])]
        assert element["tag"] == "a"
        assert normalized_text(element["text"]) == normalized_text(link["accessible_name"])
    for install in no_js["install_code"]:
        element = parser.elements[selector_id(install["selector"])]
        assert element["tag"] == "code"
        assert element["text"] == install["text"]

    navigation = policy["navigation"]
    assert navigation["fragment_ids"] == ["why", "compare", "install"]
    for fragment in navigation["fragment_ids"]:
        assert fragment in parser.elements
    assert f"section[id]{{scroll-margin-top:{navigation['scroll_margin_top_px']}px}}" in source
    assert navigation["board_path"] == "/engineering-board/board.html"

    required_source_contract = [
        'key="eb-theme", allowed={light:true,dark:true};',
        "try{return window.localStorage.getItem(key);}",
        "try{window.localStorage.setItem(key,value);}",
        'root.classList.add("js")',
        ".js .reveal{opacity:0;",
        '!("IntersectionObserver" in window)',
        "Promise.resolve().then(function(){",
        "navigator.clipboard.writeText(code.textContent)",
        ".catch(function(){reportCopyFailure(btn);});",
    ]
    for marker in required_source_contract:
        assert marker in source, f"missing landing enhancement contract: {marker}"

    policy_digest = hashlib.sha256(policy_path.read_bytes()).hexdigest()
    print(
        "landing-contract: PASS "
        f"policy_sha256={policy_digest} "
        f"markers={len(policy['first_viewport']['markers'])} "
        f"focus={len(policy['first_viewport']['focus_order'])} "
        f"install={len(no_js['install_code'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
