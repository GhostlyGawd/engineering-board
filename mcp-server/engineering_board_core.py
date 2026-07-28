#!/usr/bin/env python3
"""Shared deterministic Engineering Board pattern and graph core.

The output is JSON-compatible YAML: JSON is a strict YAML 1.2 subset, which
keeps the file dependency-free and lets every consumer parse it deterministically.
Interpretation does not belong here; this module emits structural facts only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import unicodedata
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
SAFE_PATTERN_ID = re.compile(r"^P[0-9]{3,}$")
PATTERN_STATUSES = {"active", "merged", "retired"}
GRAPH_SCHEMA_VERSION = "2"
PROMOTION_TYPES = {
    "bug": ("bugs", "B"),
    "feature": ("features", "F"),
    "question": ("questions", "Q"),
    "observation": ("observations", "O"),
}


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


def normalize_pattern_label(value: str) -> str:
    """Return the stable comparison form for a readable pattern label."""
    text = unicodedata.normalize("NFKC", str(value or "")).casefold().strip()
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"[^\w-]+", "-", text, flags=re.UNICODE)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def load_pattern_registry(board_dir: Path) -> dict[str, Any]:
    """Load and validate repository-owned P### pattern records."""
    patterns_dir = board_dir / "patterns"
    by_id: dict[str, dict[str, Any]] = {}
    by_token: dict[str, str] = {}
    sources: list[str] = []
    if not patterns_dir.is_dir():
        return {"by_id": by_id, "by_token": by_token, "sources": sources}

    board_real = board_dir.resolve()
    for path in sorted(patterns_dir.glob("*.md"), key=lambda item: item.name):
        relative = path.relative_to(board_dir).as_posix()
        if path.is_symlink():
            raise GraphError(f"{relative}: linked pattern record is not allowed")
        try:
            resolved = path.resolve(strict=True)
            resolved.relative_to(board_real)
        except (OSError, ValueError) as exc:
            raise GraphError(f"{relative}: unsafe pattern record path") from exc
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise GraphError(f"{relative}: unable to read: {exc}") from exc
        frontmatter, body = parse_frontmatter(text, relative)
        missing = [
            key
            for key in ("id", "type", "status", "label", "created")
            if not frontmatter.get(key)
        ]
        if missing:
            raise GraphError(
                f"{relative}: missing required pattern field(s): "
                f"{', '.join(missing)}"
            )
        pattern_id = str(frontmatter["id"])
        if not SAFE_PATTERN_ID.fullmatch(pattern_id):
            raise GraphError(f"{relative}: unsafe pattern id {pattern_id!r}")
        if pattern_id in by_id:
            raise GraphError(
                f"{relative}: duplicate pattern id {pattern_id} also used by "
                f"{by_id[pattern_id]['source']}"
            )
        if str(frontmatter["type"]) != "pattern":
            raise GraphError(f"{relative}: type must be 'pattern'")
        status = str(frontmatter["status"])
        if status not in PATTERN_STATUSES:
            raise GraphError(
                f"{relative}: invalid pattern status {status!r}"
            )
        label = normalize_pattern_label(str(frontmatter["label"]))
        if not label:
            raise GraphError(f"{relative}: label normalizes to an empty value")
        aliases = sorted(
            {
                normalized
                for alias in _as_list(frontmatter.get("aliases"))
                if (normalized := normalize_pattern_label(alias))
            }
        )
        record = dict(frontmatter)
        record.update(
            {
                "id": pattern_id,
                "label": label,
                "aliases": aliases,
                "status": status,
                "source": relative,
                "body": body,
            }
        )
        by_id[pattern_id] = record
        sources.append(relative)

    for pattern_id, record in sorted(by_id.items()):
        for token in [record["label"]] + record["aliases"]:
            previous = by_token.get(token)
            if previous and previous != pattern_id:
                raise GraphError(
                    f"{record['source']}: normalized label or alias {token!r} "
                    f"already belongs to {previous}"
                )
            by_token[token] = pattern_id

    for pattern_id, record in sorted(by_id.items()):
        target = str(record.get("merged_into") or "")
        if record["status"] == "merged":
            if not SAFE_PATTERN_ID.fullmatch(target) or target not in by_id:
                raise GraphError(
                    f"{record['source']}: merged pattern requires an existing "
                    "merged_into P###"
                )
            if target == pattern_id:
                raise GraphError(
                    f"{record['source']}: pattern cannot merge into itself"
                )
        elif target:
            raise GraphError(
                f"{record['source']}: merged_into requires status: merged"
            )

    for start in sorted(by_id):
        seen: set[str] = set()
        current = start
        while by_id[current]["status"] == "merged":
            if current in seen:
                raise GraphError(
                    f"{by_id[start]['source']}: pattern merge cycle detected"
                )
            seen.add(current)
            current = str(by_id[current]["merged_into"])

    return {"by_id": by_id, "by_token": by_token, "sources": sources}


def _resolved_pattern_id(
    pattern_id: str, registry: dict[str, Any]
) -> tuple[str, str]:
    """Resolve a canonical or merged pattern id to its durable active target."""
    by_id = registry["by_id"]
    if pattern_id not in by_id:
        raise GraphError(f"unknown pattern id {pattern_id}")
    current = pattern_id
    resolution = "canonical-id"
    while by_id[current]["status"] == "merged":
        current = str(by_id[current]["merged_into"])
        resolution = "merged-id"
    if by_id[current]["status"] == "retired":
        raise GraphError(f"pattern id {pattern_id} resolves to retired {current}")
    return current, resolution


def resolve_entry_patterns(
    entry: dict[str, Any], registry: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Resolve one entry without converting suggestions into canonical truth."""
    resolved: dict[str, dict[str, Any]] = {}
    unresolved: list[dict[str, Any]] = []
    observed = _as_list(entry.get("pattern"))
    explicit_ids = _as_list(entry.get("pattern_ids"))

    if explicit_ids:
        for raw_id in explicit_ids:
            pattern_id, resolution = _resolved_pattern_id(raw_id, registry)
            record = registry["by_id"][pattern_id]
            resolved[pattern_id] = {
                "id": pattern_id,
                "label": record["label"],
                "observed_labels": sorted(
                    {
                        normalize_pattern_label(label)
                        for label in observed
                        if normalize_pattern_label(label)
                    }
                ),
                "resolution": resolution,
                "source_field": "pattern_ids",
            }
        return [resolved[key] for key in sorted(resolved)], unresolved

    for raw_label in observed:
        label = normalize_pattern_label(raw_label)
        if not label:
            continue
        matched_id = registry["by_token"].get(label)
        if matched_id:
            pattern_id, merged_resolution = _resolved_pattern_id(
                matched_id, registry
            )
            record = registry["by_id"][pattern_id]
            direct_record = registry["by_id"][matched_id]
            resolution = (
                "exact-label"
                if label == direct_record["label"]
                else "alias"
            )
            if merged_resolution == "merged-id":
                resolution = "merged-alias"
            item = resolved.setdefault(
                pattern_id,
                {
                    "id": pattern_id,
                    "label": record["label"],
                    "observed_labels": [],
                    "resolution": resolution,
                    "source_field": "pattern",
                },
            )
            item["observed_labels"] = sorted(
                set(item["observed_labels"]) | {label}
            )
            continue
        legacy_id = f"legacy:{label}"
        resolved[legacy_id] = {
            "id": legacy_id,
            "label": label,
            "observed_labels": [label],
            "resolution": "legacy",
            "source_field": "pattern",
        }
        unresolved.append(
            {
                "entry": str(entry.get("id", "")),
                "label": label,
                "identity": legacy_id,
                "source": str(entry.get("_source", "")),
            }
        )
    return [resolved[key] for key in sorted(resolved)], sorted(
        unresolved,
        key=lambda item: (item["entry"], item["label"]),
    )


def source_fingerprint(board_dir: Path) -> str:
    """Hash every canonical entry and pattern record in stable path order."""
    digest = hashlib.sha256()
    paths: list[Path] = []
    for subdir in ENTRY_SUBDIRS:
        root = board_dir / subdir
        if root.is_dir():
            paths.extend(root.glob("*.md"))
    patterns_dir = board_dir / "patterns"
    if patterns_dir.is_dir():
        paths.extend(patterns_dir.glob("*.md"))
    for path in sorted(paths, key=lambda item: item.relative_to(board_dir).as_posix()):
        relative = path.relative_to(board_dir).as_posix()
        if path.is_symlink():
            raise GraphError(f"{relative}: linked canonical source is not allowed")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        try:
            digest.update(path.read_bytes())
        except OSError as exc:
            raise GraphError(f"{relative}: unable to read: {exc}") from exc
        digest.update(b"\0")
    return digest.hexdigest()


def _oneline(value: Any) -> str:
    """Collapse every universal line separator in an untrusted scalar."""
    return re.sub(
        r"[\r\n\t\f\v\x1c-\x1f\x85\u2028\u2029]+",
        " ",
        str(value),
    ).strip()


def serialize_frontmatter(fields: list[tuple[str, Any]]) -> str:
    """Serialize the flat board schema without permitting line injection."""
    output = ["---"]
    for key, value in fields:
        if value is None:
            continue
        if isinstance(value, list):
            items = [_oneline(item) for item in value if _oneline(item)]
            if not items:
                continue
            output.append(f"{key}: [{', '.join(items)}]")
        else:
            output.append(f"{key}: {_oneline(value)}")
    output.append("---")
    return "\n".join(output)


def _find_entry_path(board_dir: Path, entry_id: str) -> Path:
    if not SAFE_ID.fullmatch(entry_id):
        raise GraphError(f"unsafe or unsupported entry id {entry_id!r}")
    matches = [
        path
        for subdir in ENTRY_SUBDIRS
        for path in (board_dir / subdir).glob(f"{entry_id}*.md")
        if path.is_file()
    ]
    if len(matches) != 1:
        raise GraphError(
            f"entry {entry_id} not found uniquely on the selected board"
        )
    path = matches[0]
    if path.is_symlink():
        raise GraphError(f"{path.name}: linked entry is not mutable")
    return path


def _plan_id(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def plan_pattern_operation(
    board_dir: Path, action: str, params: dict[str, Any]
) -> dict[str, Any]:
    """Validate a pattern mutation and bind it to current canonical state."""
    board_dir = board_dir.resolve()
    action = str(action or "").strip()
    registry = load_pattern_registry(board_dir)
    normalized: dict[str, Any] = {}

    if action == "create":
        label = normalize_pattern_label(str(params.get("label") or ""))
        if not label:
            raise GraphError("create requires a non-empty pattern label")
        aliases = sorted(
            {
                normalized_alias
                for raw in _as_list(params.get("aliases"))
                if (
                    normalized_alias := normalize_pattern_label(raw)
                )
            }
        )
        for token in [label] + aliases:
            if token in registry["by_token"]:
                raise GraphError(
                    f"pattern label or alias {token!r} already belongs to "
                    f"{registry['by_token'][token]}"
                )
        highest = max(
            [int(pattern_id[1:]) for pattern_id in registry["by_id"]] or [0]
        )
        normalized = {
            "id": f"P{highest + 1:03d}",
            "label": label,
            "aliases": aliases,
            "definition": _oneline(
                params.get("definition")
                or f"Recurring failure mode: {label}."
            ),
            "inclusion_evidence": _oneline(
                params.get("inclusion_evidence")
                or "Assign only when repository evidence identifies this "
                "failure mode."
            ),
            "exclusions": _oneline(
                params.get("exclusions")
                or "Do not assign from surface-language similarity alone."
            ),
        }
    elif action == "alias":
        pattern_id = str(params.get("pattern_id") or "")
        target_id, _ = _resolved_pattern_id(pattern_id, registry)
        alias = normalize_pattern_label(str(params.get("alias") or ""))
        if not alias:
            raise GraphError("alias requires a non-empty label")
        previous = registry["by_token"].get(alias)
        if previous and previous != pattern_id:
            raise GraphError(
                f"pattern alias {alias!r} already belongs to {previous}"
            )
        normalized = {"pattern_id": target_id, "alias": alias}
    elif action == "assign":
        entry_id = str(params.get("entry_id") or "")
        _find_entry_path(board_dir, entry_id)
        pattern_id, _ = _resolved_pattern_id(
            str(params.get("pattern_id") or ""), registry
        )
        normalized = {
            "entry_id": entry_id,
            "pattern_id": pattern_id,
            "reason": _oneline(
                params.get("reason")
                or "Explicit canonical pattern assignment."
            ),
        }
    elif action == "correct":
        entry_id = str(params.get("entry_id") or "")
        _find_entry_path(board_dir, entry_id)
        replacement = str(params.get("replace") or "")
        target_id, _ = _resolved_pattern_id(
            str(params.get("with") or params.get("pattern_id") or ""),
            registry,
        )
        reason = _oneline(params.get("reason") or "")
        if not replacement or not reason:
            raise GraphError(
                "correct requires replace, with, and a non-empty reason"
            )
        normalized = {
            "entry_id": entry_id,
            "replace": replacement,
            "with": target_id,
            "reason": reason,
        }
    else:
        raise GraphError(
            "invalid pattern action; use create, alias, assign, or correct"
        )

    payload = {
        "action": action,
        "operation": normalized,
        "source_fingerprint": source_fingerprint(board_dir),
    }
    return {
        "action": action,
        "operation": normalized,
        "source_fingerprint": payload["source_fingerprint"],
        "plan_id": _plan_id(payload),
        "writes_canonical": False,
    }


def apply_pattern_operation(
    board_dir: Path,
    project: str,
    action: str,
    params: dict[str, Any],
    plan_id: str,
) -> dict[str, Any]:
    """Apply one unchanged pattern plan and rebuild derived graph state."""
    board_dir = board_dir.resolve()
    plan = plan_pattern_operation(board_dir, action, params)
    if plan["plan_id"] != plan_id:
        raise GraphError(
            "plan_stale: canonical inputs changed; request a fresh preview"
        )
    operation = plan["operation"]
    now = _utc_now()

    if action == "create":
        patterns_dir = board_dir / "patterns"
        patterns_dir.mkdir(parents=True, exist_ok=True)
        path = patterns_dir / (
            f"{operation['id']}-{operation['label']}.md"
        )
        if path.exists():
            raise GraphError(f"pattern record already exists: {path.name}")
        content = (
            serialize_frontmatter(
                [
                    ("id", operation["id"]),
                    ("type", "pattern"),
                    ("status", "active"),
                    ("label", operation["label"]),
                    ("aliases", operation["aliases"]),
                    ("created", now[:10]),
                ]
            )
            + "\n\n## Definition\n\n"
            + operation["definition"]
            + "\n\n## Inclusion evidence\n\n"
            + operation["inclusion_evidence"]
            + "\n\n## Exclusions\n\n"
            + operation["exclusions"]
            + "\n\n## History\n\n"
            + f"- {now}: Created through an explicit pattern apply action.\n"
        )
        _atomic_write(path, content)
        changed = [path.relative_to(board_dir).as_posix()]
    else:
        registry = load_pattern_registry(board_dir)
        changed = []
        if action == "alias":
            record = registry["by_id"][operation["pattern_id"]]
            path = board_dir / record["source"]
            text = path.read_text(encoding="utf-8")
            frontmatter, body = parse_frontmatter(text, record["source"])
            aliases = sorted(
                set(_as_list(frontmatter.get("aliases")))
                | {operation["alias"]}
            )
            frontmatter["aliases"] = aliases
            history = (
                body.rstrip()
                + "\n\n"
                + f"- {now}: Added alias `{operation['alias']}` through "
                "an explicit apply action.\n"
            )
            _atomic_write(
                path,
                serialize_frontmatter(list(frontmatter.items()))
                + "\n\n"
                + history.lstrip(),
            )
            changed.append(record["source"])
        else:
            path = _find_entry_path(board_dir, operation["entry_id"])
            relative = path.relative_to(board_dir).as_posix()
            text = path.read_text(encoding="utf-8")
            frontmatter, body = parse_frontmatter(text, relative)
            pattern_ids = _as_list(frontmatter.get("pattern_ids"))
            if action == "assign":
                pattern_ids = sorted(
                    set(pattern_ids) | {operation["pattern_id"]}
                )
                history_line = (
                    f"- {now}: Assigned `{operation['pattern_id']}` — "
                    f"{operation['reason']}"
                )
            else:
                replacement = operation["replace"]
                if SAFE_PATTERN_ID.fullmatch(replacement):
                    pattern_ids = [
                        item for item in pattern_ids if item != replacement
                    ]
                else:
                    replacement_label = normalize_pattern_label(replacement)
                    frontmatter["pattern"] = [
                        item
                        for item in _as_list(frontmatter.get("pattern"))
                        if normalize_pattern_label(item) != replacement_label
                    ]
                pattern_ids = sorted(
                    set(pattern_ids) | {operation["with"]}
                )
                history_line = (
                    f"- {now}: Replaced `{replacement}` with "
                    f"`{operation['with']}` — {operation['reason']}"
                )
            frontmatter["pattern_ids"] = pattern_ids
            if "## Pattern history" in body:
                body = body.rstrip() + "\n" + history_line + "\n"
            else:
                body = (
                    body.rstrip()
                    + "\n\n## Pattern history\n\n"
                    + history_line
                    + "\n"
                )
            _atomic_write(
                path,
                serialize_frontmatter(list(frontmatter.items()))
                + "\n\n"
                + body.lstrip(),
            )
            changed.append(relative)

    graph, cache_path = build_graph_cached(
        board_dir, project, _utc_now(), full=True
    )
    _atomic_write(
        board_dir / "GRAPH.yml",
        json.dumps(graph, ensure_ascii=False, indent=2) + "\n",
    )
    return {
        "action": action,
        "applied": True,
        "plan_id": plan_id,
        "changed": changed,
        "source_fingerprint": graph["source_fingerprint"],
        "graph": "GRAPH.yml",
        "cache": str(cache_path),
    }


def load_scratch_findings(
    board_dir: Path, session: str | None = None
) -> list[dict[str, Any]]:
    """Read extractor JSON and MCP Markdown scratch as untrusted evidence."""
    sessions_dir = board_dir / "_sessions"
    findings: list[dict[str, Any]] = []
    if not sessions_dir.is_dir():
        return findings
    for path in sorted(sessions_dir.glob("*.md"), key=lambda item: item.name):
        if session and session not in {path.name, path.stem}:
            continue
        relative = path.relative_to(board_dir).as_posix()
        if path.is_symlink():
            raise GraphError(f"{relative}: linked scratch file is not allowed")
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise GraphError(f"{relative}: unable to read: {exc}") from exc

        decoder = json.JSONDecoder()
        index = 0
        parsed_json = False
        position = 0
        while position < len(text):
            if text[position] != "{":
                position += 1
                continue
            try:
                obj, consumed = decoder.raw_decode(text[position:])
            except (TypeError, ValueError, json.JSONDecodeError):
                position += 1
                continue
            position += consumed
            if not isinstance(obj, dict):
                continue
            for finding in obj.get("findings") or []:
                if not isinstance(finding, dict):
                    continue
                parsed_json = True
                item = dict(finding)
                item["_source_file"] = relative
                item["_source_index"] = index
                item["_source_format"] = "extractor-json"
                item["scratch_id"] = str(
                    item.get("scratch_id")
                    or f"scratch:{relative}:{index}"
                )
                findings.append(item)
                index += 1

        if parsed_json or not path.name.startswith("mcp-"):
            continue
        blocks = re.split(r"(?m)^## ", text)
        for block in blocks[1:]:
            lines = block.splitlines()
            if not lines:
                continue
            header = lines[0]
            match = re.match(
                r"(?P<timestamp>[^—]+)\s+—\s+(?P<kind>[^:]+):\s*(?P<title>.+)",
                header,
            )
            if not match:
                continue
            fields: dict[str, str] = {}
            evidence: list[str] = []
            for line in lines[1:]:
                if line.startswith("- ") and ":" in line:
                    key, value = line[2:].split(":", 1)
                    fields[key.strip()] = value.strip()
                elif line.startswith(">"):
                    evidence.append(line[1:].lstrip())
            item = {
                "scratch_id": f"mcp:{relative}:{index}",
                "type": fields.get("kind") or match.group("kind").strip(),
                "confidence": "explicit",
                "title": match.group("title").strip(),
                "affects": fields.get("affects"),
                "evidence_quote": "\n".join(evidence).strip(),
                "discovered": match.group("timestamp").strip()[:10],
                "pattern": [],
                "_source_file": relative,
                "_source_index": index,
                "_source_format": "mcp-markdown",
            }
            findings.append(item)
            index += 1
    return sorted(
        findings,
        key=lambda item: (
            item["_source_file"],
            int(item["_source_index"]),
            item["scratch_id"],
        ),
    )


def plan_promotion(
    board_dir: Path, project: str, session: str | None = None
) -> dict[str, Any]:
    """Create a no-write, content-bound foreground promotion plan."""
    board_dir = board_dir.resolve()
    findings = load_scratch_findings(board_dir, session)
    registry = load_pattern_registry(board_dir)
    entries = load_entries(board_dir)
    existing_by_key = {
        (
            str(entry.get("type", "")),
            _oneline(entry.get("title", "")).casefold(),
            _oneline(entry.get("affects", "")),
        ): str(entry["id"])
        for entry in entries
    }
    existing_provenance = {
        value: str(entry["id"])
        for entry in entries
        for value in _as_list(entry.get("promoted_from"))
    }
    counters: dict[str, int] = {}
    for entry_type, (subdir, prefix) in PROMOTION_TYPES.items():
        values = [
            int(entry["id"][1:])
            for entry in entries
            if str(entry.get("type")) == entry_type
            and str(entry.get("id", "")).startswith(prefix)
        ]
        counters[prefix] = max(values or [0])

    planned: list[dict[str, Any]] = []
    for finding in findings:
        scratch_id = str(finding["scratch_id"])
        entry_type = str(finding.get("type") or "").casefold()
        title = _oneline(finding.get("title") or "")
        affects = _oneline(finding.get("affects") or "")
        base = {
            "scratch_id": scratch_id,
            "source_file": finding["_source_file"],
            "source_index": finding["_source_index"],
            "type": entry_type,
            "title": title,
            "affects": affects or None,
        }
        if scratch_id in existing_provenance:
            base.update(
                {
                    "disposition": "already_applied",
                    "entry_id": existing_provenance[scratch_id],
                }
            )
            planned.append(base)
            continue
        if entry_type not in PROMOTION_TYPES or not title:
            base.update(
                {
                    "disposition": "rejected",
                    "reason": "invalid finding type or empty title",
                }
            )
            planned.append(base)
            continue
        duplicate_id = existing_by_key.get(
            (entry_type, title.casefold(), affects)
        )
        if duplicate_id:
            base.update(
                {
                    "disposition": "deduplicated",
                    "entry_id": duplicate_id,
                }
            )
            planned.append(base)
            continue

        prefix = PROMOTION_TYPES[entry_type][1]
        counters[prefix] += 1
        entry_id = f"{prefix}{counters[prefix]:03d}"
        pattern_labels = _as_list(
            finding.get("pattern") or finding.get("patterns")
        )
        proposed_entry = {
            "id": entry_id,
            "type": entry_type,
            "pattern": pattern_labels,
            "_source": finding["_source_file"],
        }
        resolved, unresolved = resolve_entry_patterns(
            proposed_entry, registry
        )
        base.update(
            {
                "disposition": "create",
                "entry_id": entry_id,
                "priority": "P2"
                if entry_type in {"bug", "feature"}
                else None,
                "pattern": pattern_labels,
                "pattern_ids": [
                    item["id"]
                    for item in resolved
                    if not item["id"].startswith("legacy:")
                ],
                "unresolved_patterns": unresolved,
                "discovered": _oneline(
                    finding.get("discovered") or _utc_now()[:10]
                ),
                "evidence": str(finding.get("evidence_quote") or ""),
            }
        )
        existing_by_key[(entry_type, title.casefold(), affects)] = entry_id
        planned.append(base)

    payload = {
        "project": project,
        "session": session,
        "source_fingerprint": source_fingerprint(board_dir),
        "findings": planned,
    }
    return {
        **payload,
        "plan_id": _plan_id(payload),
        "writes_canonical": False,
        "summary": dict(
            Counter(item["disposition"] for item in planned)
        ),
    }


def _write_promoted_entry(
    board_dir: Path, item: dict[str, Any], now: str
) -> str:
    """Atomically write one planned canonical entry and return its path."""
    subdir = PROMOTION_TYPES[item["type"]][0]
    directory = board_dir / subdir
    directory.mkdir(parents=True, exist_ok=True)
    slug = re.sub(
        r"[^a-z0-9]+", "-", item["title"].casefold()
    ).strip("-")[:60] or "finding"
    path = directory / f"{item['entry_id']}-{slug}.md"
    if path.exists():
        raise GraphError(
            f"plan_stale: target already exists: {path.name}"
        )
    fields: list[tuple[str, Any]] = [
        ("id", item["entry_id"]),
        ("type", item["type"]),
    ]
    if item["type"] in {"bug", "feature", "question"}:
        fields.append(("status", "open"))
    if item["type"] in {"bug", "feature"}:
        fields.extend(
            [
                ("needs", "tdd"),
                ("priority", item["priority"]),
            ]
        )
    fields.extend(
        [
            ("title", item["title"]),
            ("affects", item.get("affects")),
            ("discovered", item["discovered"]),
            ("discovered_at", now),
            ("promoted_from", [item["scratch_id"]]),
            ("pattern", item.get("pattern")),
            ("pattern_ids", item.get("pattern_ids")),
        ]
    )
    body_parts = [f"# {item['title']}", ""]
    if item["type"] in {"bug", "feature", "question"}:
        body_parts.extend(
            [
                "## Done when",
                "",
                "- [ ] Define and verify the completion criterion.",
                "",
            ]
        )
    if item.get("evidence"):
        body_parts.extend(
            [
                "## Evidence",
                "",
                *[
                    "> " + line if line else ">"
                    for line in item["evidence"].splitlines()
                ],
                "",
            ]
        )
    if item.get("pattern_ids"):
        body_parts.extend(
            [
                "## Pattern history",
                "",
                f"- {now}: Assigned "
                + ", ".join(
                    f"`{pattern_id}`"
                    for pattern_id in item["pattern_ids"]
                )
                + " during explicit foreground promotion.",
                "",
            ]
        )
    _atomic_write(
        path,
        serialize_frontmatter(fields)
        + "\n\n"
        + "\n".join(body_parts).rstrip()
        + "\n",
    )
    return path.relative_to(board_dir).as_posix()


def apply_promotion(
    board_dir: Path,
    project: str,
    session: str | None,
    plan_id: str,
    archive_sources: bool = True,
) -> dict[str, Any]:
    """Apply an unchanged promotion plan with idempotent per-finding receipts."""
    board_dir = board_dir.resolve()
    plan = plan_promotion(board_dir, project, session)
    if plan["plan_id"] != plan_id:
        raise GraphError(
            "plan_stale: scratch or canonical inputs changed; preview again"
        )
    now = _utc_now()
    results: list[dict[str, Any]] = []
    final_by_file: dict[str, list[str]] = {}
    log_path = board_dir / "consolidation.log"

    for item in plan["findings"]:
        result = dict(item)
        disposition = item["disposition"]
        if disposition == "create":
            try:
                result["file"] = _write_promoted_entry(
                    board_dir, item, now
                )
                disposition = "created"
            except OSError as exc:
                disposition = "deferred"
                result["reason"] = (
                    "write_error:"
                    + _oneline(str(exc))[:160]
                )
        receipt = {
            "scratch_id": item["scratch_id"],
            "disposition": (
                f"promoted_{item['entry_id']}"
                if disposition == "created"
                else disposition
            ),
            "consolidated_at": now,
            "source": item["source_file"],
        }
        with log_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(
                json.dumps(receipt, ensure_ascii=False, sort_keys=True)
                + "\n"
            )
        result["disposition"] = disposition
        results.append(result)
        final_by_file.setdefault(item["source_file"], []).append(disposition)

    archived: list[str] = []
    if archive_sources:
        archive_dir = board_dir / "_sessions" / "_archive"
        for relative, dispositions in sorted(final_by_file.items()):
            if not dispositions or not all(
                value in {"created", "deduplicated", "already_applied"}
                for value in dispositions
            ):
                continue
            source = board_dir / relative
            if not source.is_file() or source.is_symlink():
                continue
            archive_dir.mkdir(parents=True, exist_ok=True)
            stamp = now.replace(":", "").replace("-", "")
            target = archive_dir / f"{source.stem}-{stamp}{source.suffix}"
            os.replace(source, target)
            archived.append(target.relative_to(board_dir).as_posix())

    graph, cache_path = build_graph_cached(
        board_dir, project, _utc_now(), full=True
    )
    _atomic_write(
        board_dir / "GRAPH.yml",
        json.dumps(graph, ensure_ascii=False, indent=2) + "\n",
    )
    return {
        "applied": True,
        "plan_id": plan_id,
        "results": results,
        "summary": dict(Counter(item["disposition"] for item in results)),
        "archived": archived,
        "board_rebuild_required": True,
        "source_fingerprint": graph["source_fingerprint"],
        "graph": "GRAPH.yml",
        "cache": str(cache_path),
    }


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
    evidence: list[dict[str, str]] | None = None,
    pattern_ids: list[str] | None = None,
) -> dict[str, Any]:
    edge = {
        "from": source,
        "to": target,
        "kind": kind,
        "value": value,
        "weight": weight,
    }
    if pattern_ids:
        edge["pattern_ids"] = sorted(set(pattern_ids))
    if evidence:
        edge["evidence"] = sorted(
            evidence,
            key=lambda item: (
                item.get("entry", ""),
                item.get("field", ""),
                item.get("source", ""),
            ),
        )
    return edge


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
                    edges.append(
                        _edge(
                            source,
                            target,
                            kind,
                            field,
                            3,
                            evidence=[
                                {
                                    "entry": source,
                                    "field": field,
                                    "source": str(entry["_source"]),
                                }
                            ],
                        )
                    )

    for index, left in enumerate(entries):
        for right in entries[index + 1 :]:
            left_id, right_id = str(left["id"]), str(right["id"])
            left_patterns = {
                item["id"]: item for item in left.get("_resolved_patterns", [])
            }
            right_patterns = {
                item["id"]: item for item in right.get("_resolved_patterns", [])
            }
            shared_pattern_ids = sorted(
                set(left_patterns) & set(right_patterns)
            )
            if shared_pattern_ids:
                shared_labels = sorted(
                    {
                        left_patterns[pattern_id]["label"]
                        for pattern_id in shared_pattern_ids
                    }
                )
                edges.append(
                    _edge(
                        left_id,
                        right_id,
                        "shared-pattern",
                        ", ".join(shared_labels),
                        2,
                        pattern_ids=shared_pattern_ids,
                        evidence=[
                            {
                                "entry": left_id,
                                "field": left_patterns[pattern_id][
                                    "source_field"
                                ],
                                "source": str(left["_source"]),
                            }
                            for pattern_id in shared_pattern_ids
                        ]
                        + [
                            {
                                "entry": right_id,
                                "field": right_patterns[pattern_id][
                                    "source_field"
                                ],
                                "source": str(right["_source"]),
                            }
                            for pattern_id in shared_pattern_ids
                        ],
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
                        evidence=[
                            {
                                "entry": left_id,
                                "field": "affects",
                                "source": str(left["_source"]),
                            },
                            {
                                "entry": right_id,
                                "field": "affects",
                                "source": str(right["_source"]),
                            },
                        ],
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
                        evidence=[
                            {
                                "entry": left_id,
                                "field": "tags",
                                "source": str(left["_source"]),
                            },
                            {
                                "entry": right_id,
                                "field": "tags",
                                "source": str(right["_source"]),
                            },
                        ],
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
            if edge.get("pattern_ids"):
                previous["pattern_ids"] = sorted(
                    set(previous.get("pattern_ids", []))
                    | set(edge["pattern_ids"])
                )
            if edge.get("evidence"):
                combined = {
                    (
                        item.get("entry", ""),
                        item.get("field", ""),
                        item.get("source", ""),
                    ): item
                    for item in previous.get("evidence", []) + edge["evidence"]
                }
                previous["evidence"] = [
                    combined[key] for key in sorted(combined)
                ]
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
        pattern_ids = sorted(
            {
                pattern["id"]
                for member in members
                for pattern in entry_by_id[member].get(
                    "_resolved_patterns", []
                )
            }
        )
        patterns = sorted(
            {
                pattern["label"]
                for member in members
                for pattern in entry_by_id[member].get(
                    "_resolved_patterns", []
                )
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
            signal = {
                "kind": kind,
                "value": value,
                "members": sorted(signal_members),
            }
            if kind == "shared-pattern":
                signal["pattern_ids"] = sorted(
                    {
                        pattern_id
                        for edge in internal
                        if edge["kind"] == kind
                        and value in edge["value"].split(", ")
                        for pattern_id in edge.get("pattern_ids", [])
                    }
                )
            signals.append(signal)
        fingerprint_input = {
            "members": members,
            "edges": [
                {
                    "from": edge["from"],
                    "to": edge["to"],
                    "kind": edge["kind"],
                    "pattern_ids": edge.get("pattern_ids", []),
                }
                for edge in internal
            ],
        }
        fingerprint = hashlib.sha256(
            json.dumps(
                fingerprint_input,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()[:16]
        clusters.append(
            {
                "id": f"C{len(clusters) + 1:03d}",
                "fingerprint": f"c-{fingerprint}",
                "members": members,
                "pattern_ids": pattern_ids,
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
    build_mode: str = "full",
) -> dict[str, Any]:
    """Build the complete deterministic graph document."""
    registry = load_pattern_registry(board_dir)
    entries = load_entries(board_dir)
    unresolved_patterns: list[dict[str, Any]] = []
    for entry in entries:
        resolved, unresolved = resolve_entry_patterns(entry, registry)
        entry["_resolved_patterns"] = resolved
        unresolved_patterns.extend(unresolved)
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
        resolved_patterns = entry.get("_resolved_patterns", [])
        if resolved_patterns:
            node["pattern_ids"] = [
                item["id"] for item in resolved_patterns
            ]
            node["resolved_patterns"] = resolved_patterns
        nodes[str(entry["id"])] = node

    pattern_members: dict[str, dict[str, Any]] = {}
    for entry in entries:
        for pattern in entry.get("_resolved_patterns", []):
            item = pattern_members.setdefault(
                pattern["id"],
                {"label": pattern["label"], "members": []},
            )
            item["members"].append(str(entry["id"]))

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
    for pattern_id, pattern_data in sorted(pattern_members.items()):
        members = pattern_data["members"]
        if len(members) >= 2:
            findings.append(
                {
                    "type": "pattern-recurrence",
                    "pattern_id": pattern_id,
                    "pattern": pattern_data["label"],
                    "count": len(members),
                    "members": sorted(members),
                }
            )

    return {
        "schema_version": GRAPH_SCHEMA_VERSION,
        "generated_at": generated_at,
        "source_fingerprint": source_fingerprint(board_dir),
        "build_mode": build_mode,
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
        "unresolved_patterns": sorted(
            unresolved_patterns,
            key=lambda item: (item["entry"], item["label"]),
        ),
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


def cache_path_for_board(board_dir: Path, project: str) -> Path:
    """Return the repository-local disposable graph-cache path."""
    safe_project = re.sub(r"[^A-Za-z0-9._-]+", "-", project).strip("-")
    if not safe_project:
        raise GraphError("project name cannot identify a graph cache")
    resolved = board_dir.resolve()
    repository_root = None
    for candidate in [resolved] + list(resolved.parents):
        if (
            (candidate / ".git").exists()
            or (candidate / "engineering-board" / "BOARD-ROUTER.md").is_file()
            or (candidate / "docs" / "boards" / "BOARD-ROUTER.md").is_file()
        ):
            repository_root = candidate
            break
    if repository_root is None:
        repository_root = resolved.parent
    return (
        repository_root
        / ".engineering-board"
        / "cache"
        / "graph"
        / safe_project
        / "state.json"
    )


def build_graph_cached(
    board_dir: Path,
    project: str,
    generated_at: str,
    full: bool = False,
    cache_path: Path | None = None,
) -> tuple[dict[str, Any], Path]:
    """Build graph facts and use only a source-equivalent disposable cache."""
    board_dir = board_dir.resolve()
    cache_path = (
        cache_path.resolve()
        if cache_path is not None
        else cache_path_for_board(board_dir, project)
    )
    before = source_fingerprint(board_dir)

    if not full and cache_path.is_file() and not cache_path.is_symlink():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            graph = cached["graph"]
            if (
                cached.get("schema_version") == GRAPH_SCHEMA_VERSION
                and cached.get("source_fingerprint") == before
                and graph.get("source_fingerprint") == before
            ):
                graph = dict(graph)
                graph["generated_at"] = generated_at
                graph["build_mode"] = "incremental"
                return graph, cache_path
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            pass

    graph = build_graph(
        board_dir,
        project,
        generated_at,
        build_mode="full" if full else "incremental",
    )
    after = source_fingerprint(board_dir)
    if before != after or graph["source_fingerprint"] != after:
        raise GraphError(
            "source_changed: canonical Markdown changed during graph build"
        )
    cache_payload = {
        "schema_version": GRAPH_SCHEMA_VERSION,
        "source_fingerprint": after,
        "graph": graph,
    }
    _atomic_write(
        cache_path,
        json.dumps(cache_payload, ensure_ascii=False, indent=2) + "\n",
    )
    return graph, cache_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--board-dir", required=True)
    parser.add_argument("--project", default="board")
    parser.add_argument("--output", required=True)
    parser.add_argument("--json-output")
    parser.add_argument("--generated-at")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--cache-path")
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
        graph, cache_path = build_graph_cached(
            board_dir,
            args.project,
            args.generated_at or _utc_now(),
            full=args.full,
            cache_path=(
                Path(args.cache_path) if args.cache_path else None
            ),
        )
    except GraphError as exc:
        print(json.dumps({"error": "invalid_graph_input", "detail": str(exc)}), file=sys.stderr)
        return 2

    serialized = json.dumps(graph, ensure_ascii=False, indent=2) + "\n"
    if source_fingerprint(board_dir) != graph["source_fingerprint"]:
        print(
            json.dumps(
                {
                    "error": "source_changed",
                    "detail": "canonical Markdown changed before graph replace",
                }
            ),
            file=sys.stderr,
        )
        return 2
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
                "unresolved_patterns": len(graph["unresolved_patterns"]),
                "source_fingerprint": graph["source_fingerprint"],
                "build_mode": graph["build_mode"],
                "cache": str(cache_path),
                "output": str(output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
