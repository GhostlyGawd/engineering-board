#!/usr/bin/env python3
"""Build deterministic Engineering Board graph facts from Markdown entries.

The output is JSON-compatible YAML: JSON is a strict YAML 1.2 subset, which
keeps the file dependency-free and lets every consumer parse it deterministically.
Interpretation does not belong here; this module emits structural facts only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ENTRY_SUBDIRS = ("bugs", "features", "questions", "observations")
HARD_RELATIONSHIPS = {
    "blocked_by": "blocked-by",
    "superseded_by": "superseded-by",
    "merged_into": "merged-into",
    "contradicts": "contradicts",
}
SAFE_ID = re.compile(r"^[BFOQ][0-9]+$")


class GraphError(Exception):
    """A typed, user-correctable graph input failure."""


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [
            item.strip().strip("'\"")
            for item in inner.split(",")
            if item.strip()
        ]
    if value in {"null", "~"}:
        return None
    return value.strip("'\"")


def parse_frontmatter(text: str, source: str) -> tuple[dict[str, Any], str]:
    """Parse the flat frontmatter subset used by Engineering Board entries."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise GraphError(f"{source}: missing opening frontmatter delimiter")
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise GraphError(f"{source}: missing closing frontmatter delimiter") from exc

    frontmatter: dict[str, Any] = {}
    for line_number, line in enumerate(lines[1:end], 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise GraphError(
                f"{source}:{line_number}: malformed frontmatter line"
            )
        key, value = line.split(":", 1)
        key = key.strip()
        if not key:
            raise GraphError(f"{source}:{line_number}: empty frontmatter key")
        frontmatter[key] = _parse_scalar(value)
    return frontmatter, "\n".join(lines[end + 1 :])


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return sorted({str(item).strip() for item in value if str(item).strip()})
    text = str(value).strip()
    return [text] if text else []


def load_entries(board_dir: Path) -> list[dict[str, Any]]:
    """Load and validate open graphable entries in stable source-path order."""
    entries: list[dict[str, Any]] = []
    seen_ids: dict[str, str] = {}
    for subdir in ENTRY_SUBDIRS:
        root = board_dir / subdir
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.md"), key=lambda item: item.name):
            relative = path.relative_to(board_dir).as_posix()
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as exc:
                raise GraphError(f"{relative}: unable to read: {exc}") from exc
            frontmatter, body = parse_frontmatter(text, relative)
            missing = [
                key
                for key in ("id", "type", "title", "discovered")
                if not frontmatter.get(key)
            ]
            if missing:
                raise GraphError(
                    f"{relative}: missing required field(s): {', '.join(missing)}"
                )
            entry_id = str(frontmatter["id"])
            if not SAFE_ID.fullmatch(entry_id):
                raise GraphError(f"{relative}: unsafe or unsupported id {entry_id!r}")
            if entry_id in seen_ids:
                raise GraphError(
                    f"{relative}: duplicate id {entry_id} also used by "
                    f"{seen_ids[entry_id]}"
                )
            seen_ids[entry_id] = relative
            if str(frontmatter.get("status", "open")) == "resolved":
                continue
            entry = dict(frontmatter)
            entry["_source"] = relative
            entry["_body"] = body
            entries.append(entry)
    return sorted(entries, key=lambda entry: str(entry["id"]))


def _affects_domain(value: Any) -> str | None:
    text = str(value or "").replace("\\", "/").strip("/")
    return text.split("/", 1)[0] if text else None


def _shared_affects_prefix(left: Any, right: Any) -> str | None:
    left_parts = [
        part for part in str(left or "").replace("\\", "/").strip("/").split("/")
        if part
    ]
    right_parts = [
        part for part in str(right or "").replace("\\", "/").strip("/").split("/")
        if part
    ]
    shared: list[str] = []
    for left_part, right_part in zip(left_parts, right_parts):
        if left_part != right_part:
            break
        shared.append(left_part)
    return "/".join(shared) + "/" if shared else None


def _edge(
    source: str,
    target: str,
    kind: str,
    value: str,
    weight: int,
) -> dict[str, Any]:
    return {
        "from": source,
        "to": target,
        "kind": kind,
        "value": value,
        "weight": weight,
    }


def build_edges(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build stable explicit and shared-signal edges."""
    ids = {str(entry["id"]) for entry in entries}
    edges: list[dict[str, Any]] = []
    tag_counts = Counter(
        tag for entry in entries for tag in _as_list(entry.get("tags"))
    )
    universal_tags = {
        tag for tag, count in tag_counts.items() if count > len(entries) / 2
    }

    for entry in entries:
        source = str(entry["id"])
        for field, kind in HARD_RELATIONSHIPS.items():
            for target in _as_list(entry.get(field)):
                if target in ids:
                    edges.append(_edge(source, target, kind, field, 3))

    for index, left in enumerate(entries):
        for right in entries[index + 1 :]:
            left_id, right_id = str(left["id"]), str(right["id"])
            shared_patterns = sorted(
                set(_as_list(left.get("pattern")))
                & set(_as_list(right.get("pattern")))
            )
            if shared_patterns:
                edges.append(
                    _edge(
                        left_id,
                        right_id,
                        "shared-pattern",
                        ", ".join(shared_patterns),
                        2,
                    )
                )
            affects_prefix = _shared_affects_prefix(
                left.get("affects"), right.get("affects")
            )
            if affects_prefix:
                edges.append(
                    _edge(
                        left_id,
                        right_id,
                        "shared-affects-prefix",
                        affects_prefix,
                        2,
                    )
                )
            shared_tags = sorted(
                (
                    set(_as_list(left.get("tags")))
                    & set(_as_list(right.get("tags")))
                )
                - universal_tags
            )
            if shared_tags:
                edges.append(
                    _edge(
                        left_id,
                        right_id,
                        "shared-tag",
                        ", ".join(shared_tags),
                        1,
                    )
                )

    unique: dict[tuple[str, str, str], dict[str, Any]] = {}
    for edge in edges:
        source, target = sorted((edge["from"], edge["to"]))
        edge["from"], edge["to"] = source, target
        key = (source, target, edge["kind"])
        previous = unique.get(key)
        if previous is None or edge["weight"] > previous["weight"]:
            unique[key] = edge
        elif edge["weight"] == previous["weight"]:
            values = sorted(
                set(previous["value"].split(", ")) | set(edge["value"].split(", "))
            )
            previous["value"] = ", ".join(values)
    return sorted(
        unique.values(),
        key=lambda edge: (
            edge["from"],
            edge["to"],
            -int(edge["weight"]),
            edge["kind"],
            edge["value"],
        ),
    )


def _components(node_ids: list[str], edges: list[dict[str, Any]]) -> list[list[str]]:
    adjacency = {node_id: set() for node_id in node_ids}
    for edge in edges:
        adjacency[edge["from"]].add(edge["to"])
        adjacency[edge["to"]].add(edge["from"])
    components: list[list[str]] = []
    unseen = set(node_ids)
    while unseen:
        start = min(unseen)
        stack = [start]
        members: list[str] = []
        while stack:
            node = stack.pop()
            if node not in unseen:
                continue
            unseen.remove(node)
            members.append(node)
            stack.extend(sorted(adjacency[node] & unseen, reverse=True))
        components.append(sorted(members))
    return sorted(components, key=lambda members: members[0])


def build_clusters(
    entries: list[dict[str, Any]], edges: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[str]]:
    """Return multi-node connected components and isolated ids."""
    entry_by_id = {str(entry["id"]): entry for entry in entries}
    components = _components(sorted(entry_by_id), edges)
    clusters: list[dict[str, Any]] = []
    isolated: list[str] = []
    for members in components:
        if len(members) == 1:
            isolated.extend(members)
            continue
        member_set = set(members)
        internal = [
            edge
            for edge in edges
            if edge["from"] in member_set and edge["to"] in member_set
        ]
        pair_count = len({(edge["from"], edge["to"]) for edge in internal})
        possible = len(members) * (len(members) - 1) / 2
        patterns = sorted(
            {
                pattern
                for member in members
                for pattern in _as_list(entry_by_id[member].get("pattern"))
            }
        )
        domains = sorted(
            {
                domain
                for member in members
                if (domain := _affects_domain(entry_by_id[member].get("affects")))
            }
        )
        signals: list[dict[str, Any]] = []
        signal_groups: dict[tuple[str, str], set[str]] = {}
        for edge in internal:
            for value in edge["value"].split(", "):
                signal_groups.setdefault((edge["kind"], value), set()).update(
                    (edge["from"], edge["to"])
                )
        for (kind, value), signal_members in sorted(signal_groups.items()):
            signals.append(
                {
                    "kind": kind,
                    "value": value,
                    "members": sorted(signal_members),
                }
            )
        clusters.append(
            {
                "id": f"C{len(clusters) + 1:03d}",
                "members": members,
                "patterns": patterns,
                "affected_domains": domains,
                "signals": signals,
                "density": round(pair_count / possible, 2) if possible else 0.0,
            }
        )
    return clusters, sorted(isolated)


def build_graph(
    board_dir: Path,
    project: str,
    generated_at: str,
) -> dict[str, Any]:
    """Build the complete deterministic graph document."""
    entries = load_entries(board_dir)
    edges = build_edges(entries)
    clusters, isolated = build_clusters(entries, edges)

    nodes: dict[str, dict[str, Any]] = {}
    for entry in entries:
        node: dict[str, Any] = {
            "type": str(entry["type"]),
            "title": str(entry["title"]),
            "source": str(entry["_source"]),
        }
        for key in ("priority", "status", "affects"):
            if entry.get(key):
                node[key] = str(entry[key])
        for key in ("tags", "pattern"):
            values = _as_list(entry.get(key))
            if values:
                node[key] = values
        nodes[str(entry["id"])] = node

    pattern_members: dict[str, list[str]] = {}
    for entry in entries:
        for pattern in _as_list(entry.get("pattern")):
            pattern_members.setdefault(pattern, []).append(str(entry["id"]))

    findings: list[dict[str, Any]] = []
    for cluster in clusters:
        findings.append(
            {
                "type": "dense-cluster",
                "cluster_id": cluster["id"],
                "members": cluster["members"],
                "density": cluster["density"],
                "shared_dimensions": {"patterns": cluster["patterns"]},
                "internal_edges": len(
                    {
                        (edge["from"], edge["to"])
                        for edge in edges
                        if edge["from"] in cluster["members"]
                        and edge["to"] in cluster["members"]
                    }
                ),
            }
        )
    for node_id in isolated:
        findings.append({"type": "isolated-node", "node": node_id})
    for pattern, members in sorted(pattern_members.items()):
        if len(members) >= 2:
            findings.append(
                {
                    "type": "pattern-recurrence",
                    "pattern": pattern,
                    "count": len(members),
                    "members": sorted(members),
                }
            )

    return {
        "generated_at": generated_at,
        "project": project,
        "entries_analyzed": {
            "open": len(entries),
            "archived": 0,
            "total": len(entries),
        },
        "nodes": nodes,
        "edges": edges,
        "topology": {
            "clusters": clusters,
            "isolated": isolated,
            "cross_cluster_bridges": [],
        },
        "findings": findings,
        "read_order": [cluster["id"] for cluster in clusters] + isolated,
        "drill_in": {
            cluster["id"]: cluster["members"] for cluster in clusters
        },
    }


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--board-dir", required=True)
    parser.add_argument("--project", default="board")
    parser.add_argument("--output", required=True)
    parser.add_argument("--json-output")
    parser.add_argument("--generated-at")
    args = parser.parse_args(argv)

    board_dir = Path(args.board_dir).resolve()
    output = Path(args.output).resolve()
    if not board_dir.is_dir():
        print(
            json.dumps(
                {
                    "error": "board_not_found",
                    "path": str(board_dir),
                }
            ),
            file=sys.stderr,
        )
        return 2
    try:
        graph = build_graph(
            board_dir,
            args.project,
            args.generated_at or _utc_now(),
        )
    except GraphError as exc:
        print(json.dumps({"error": "invalid_graph_input", "detail": str(exc)}), file=sys.stderr)
        return 2

    serialized = json.dumps(graph, ensure_ascii=False, indent=2) + "\n"
    _atomic_write(output, serialized)
    if args.json_output:
        _atomic_write(Path(args.json_output).resolve(), serialized)
    print(
        json.dumps(
            {
                "project": graph["project"],
                "nodes": len(graph["nodes"]),
                "edges": len(graph["edges"]),
                "clusters": len(graph["topology"]["clusters"]),
                "findings": len(graph["findings"]),
                "output": str(output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
