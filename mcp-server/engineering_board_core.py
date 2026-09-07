#!/usr/bin/env python3
"""Shared deterministic Engineering Board pattern-intelligence core.

The output is JSON-compatible YAML: JSON is a strict YAML 1.2 subset, which
keeps the file dependency-free and lets every consumer parse it deterministically.
The core emits structural facts and validates explicit, evidence-cited
hypothesis state. It does not generate causal prose or grant confirmation.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
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
SAFE_EVIDENCE_ID = re.compile(r"^[BFLOQ][0-9]+$")
SAFE_PATTERN_ID = re.compile(r"^P[0-9]{3,}$")
SAFE_HYPOTHESIS_ID = re.compile(r"^H[0-9]{3,}$")
SAFE_CLAIM_KEY = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SAFE_CLUSTER_FINGERPRINT = re.compile(r"^c-[0-9a-f]{16}$")
SAFE_CLAIM_FINGERPRINT = re.compile(r"^h-[0-9a-f]{16}$")
SAFE_SOURCE_FINGERPRINT = re.compile(r"^[0-9a-f]{64}$")
PATTERN_STATUSES = {"active", "merged", "retired"}
HYPOTHESIS_STATUSES = {
    "proposed",
    "confirmed",
    "weakened",
    "rejected",
    "split",
    "merged",
}
HYPOTHESIS_ACTIVE_STATUSES = {"proposed", "confirmed", "weakened"}
HYPOTHESIS_SECTIONS = (
    "Proposed root cause",
    "Supporting evidence",
    "Alternative explanations",
    "Counter-evidence",
    "Confidence basis",
    "Falsifier",
    "Outcome history",
)
GRAPH_SCHEMA_VERSION = "3"
RANKING_RULE_VERSION = "1"
CONTEXT_RANKING_RULE_VERSION = "2"
CONTEXT_CONTRACT_VERSION = "3"
CONTEXT_RESULT_LIMIT = 3
CONTEXT_TITLE_LIMIT = 160
CONTEXT_SUMMARY_LIMIT = 2000
CONTEXT_STOPWORDS = {
    "and",
    "are",
    "bug",
    "change",
    "debug",
    "does",
    "error",
    "failed",
    "failure",
    "fix",
    "for",
    "from",
    "how",
    "into",
    "not",
    "root",
    "that",
    "the",
    "this",
    "was",
    "what",
    "when",
    "where",
    "why",
    "with",
}
FIX_RESULTS = {"held", "failed", "partial", "inconclusive"}
OUTCOME_DISPOSITIONS = {
    "held": {"unchanged", "confirmed"},
    "failed": {"unchanged", "weakened", "rejected"},
    "partial": {"unchanged", "weakened", "split"},
    "inconclusive": {"unchanged", "weakened"},
}
LEARNING_OUTCOME_STATUSES = {
    "untested",
    "supported",
    "weakened",
    "contested",
}
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
        return [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]
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
            raise GraphError(f"{source}:{line_number}: malformed frontmatter line")
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
            key for key in ("id", "type", "status", "label", "created") if not frontmatter.get(key)
        ]
        if missing:
            raise GraphError(f"{relative}: missing required pattern field(s): {', '.join(missing)}")
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
            raise GraphError(f"{relative}: invalid pattern status {status!r}")
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
                    f"{record['source']}: merged pattern requires an existing merged_into P###"
                )
            if target == pattern_id:
                raise GraphError(f"{record['source']}: pattern cannot merge into itself")
        elif target:
            raise GraphError(f"{record['source']}: merged_into requires status: merged")

    for start in sorted(by_id):
        seen: set[str] = set()
        current = start
        while by_id[current]["status"] == "merged":
            if current in seen:
                raise GraphError(f"{by_id[start]['source']}: pattern merge cycle detected")
            seen.add(current)
            current = str(by_id[current]["merged_into"])

    return {"by_id": by_id, "by_token": by_token, "sources": sources}


def _resolved_pattern_id(pattern_id: str, registry: dict[str, Any]) -> tuple[str, str]:
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
            pattern_id, merged_resolution = _resolved_pattern_id(matched_id, registry)
            record = registry["by_id"][pattern_id]
            direct_record = registry["by_id"][matched_id]
            resolution = "exact-label" if label == direct_record["label"] else "alias"
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
            item["observed_labels"] = sorted(set(item["observed_labels"]) | {label})
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
        raise GraphError(f"entry {entry_id} not found uniquely on the selected board")
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


def plan_pattern_operation(board_dir: Path, action: str, params: dict[str, Any]) -> dict[str, Any]:
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
                if (normalized_alias := normalize_pattern_label(raw))
            }
        )
        for token in [label] + aliases:
            if token in registry["by_token"]:
                raise GraphError(
                    f"pattern label or alias {token!r} already belongs to "
                    f"{registry['by_token'][token]}"
                )
        highest = max([int(pattern_id[1:]) for pattern_id in registry["by_id"]] or [0])
        normalized = {
            "id": f"P{highest + 1:03d}",
            "label": label,
            "aliases": aliases,
            "definition": _oneline(params.get("definition") or f"Recurring failure mode: {label}."),
            "inclusion_evidence": _oneline(
                params.get("inclusion_evidence")
                or "Assign only when repository evidence identifies this failure mode."
            ),
            "exclusions": _oneline(
                params.get("exclusions") or "Do not assign from surface-language similarity alone."
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
            raise GraphError(f"pattern alias {alias!r} already belongs to {previous}")
        normalized = {"pattern_id": target_id, "alias": alias}
    elif action == "assign":
        entry_id = str(params.get("entry_id") or "")
        _find_entry_path(board_dir, entry_id)
        pattern_id, _ = _resolved_pattern_id(str(params.get("pattern_id") or ""), registry)
        normalized = {
            "entry_id": entry_id,
            "pattern_id": pattern_id,
            "reason": _oneline(params.get("reason") or "Explicit canonical pattern assignment."),
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
            raise GraphError("correct requires replace, with, and a non-empty reason")
        normalized = {
            "entry_id": entry_id,
            "replace": replacement,
            "with": target_id,
            "reason": reason,
        }
    else:
        raise GraphError("invalid pattern action; use create, alias, assign, or correct")

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
        raise GraphError("plan_stale: canonical inputs changed; request a fresh preview")
    operation = plan["operation"]
    now = _utc_now()

    if action == "create":
        patterns_dir = board_dir / "patterns"
        patterns_dir.mkdir(parents=True, exist_ok=True)
        path = patterns_dir / (f"{operation['id']}-{operation['label']}.md")
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
            aliases = sorted(set(_as_list(frontmatter.get("aliases"))) | {operation["alias"]})
            frontmatter["aliases"] = aliases
            history = (
                body.rstrip() + "\n\n" + f"- {now}: Added alias `{operation['alias']}` through "
                "an explicit apply action.\n"
            )
            _atomic_write(
                path,
                serialize_frontmatter(list(frontmatter.items())) + "\n\n" + history.lstrip(),
            )
            changed.append(record["source"])
        else:
            path = _find_entry_path(board_dir, operation["entry_id"])
            relative = path.relative_to(board_dir).as_posix()
            text = path.read_text(encoding="utf-8")
            frontmatter, body = parse_frontmatter(text, relative)
            pattern_ids = _as_list(frontmatter.get("pattern_ids"))
            if action == "assign":
                pattern_ids = sorted(set(pattern_ids) | {operation["pattern_id"]})
                history_line = (
                    f"- {now}: Assigned `{operation['pattern_id']}` — {operation['reason']}"
                )
            else:
                replacement = operation["replace"]
                if SAFE_PATTERN_ID.fullmatch(replacement):
                    pattern_ids = [item for item in pattern_ids if item != replacement]
                else:
                    replacement_label = normalize_pattern_label(replacement)
                    frontmatter["pattern"] = [
                        item
                        for item in _as_list(frontmatter.get("pattern"))
                        if normalize_pattern_label(item) != replacement_label
                    ]
                pattern_ids = sorted(set(pattern_ids) | {operation["with"]})
                history_line = (
                    f"- {now}: Replaced `{replacement}` with "
                    f"`{operation['with']}` — {operation['reason']}"
                )
            frontmatter["pattern_ids"] = pattern_ids
            if "## Pattern history" in body:
                body = body.rstrip() + "\n" + history_line + "\n"
            else:
                body = body.rstrip() + "\n\n## Pattern history\n\n" + history_line + "\n"
            _atomic_write(
                path,
                serialize_frontmatter(list(frontmatter.items())) + "\n\n" + body.lstrip(),
            )
            changed.append(relative)

    graph, cache_path = build_graph_cached(board_dir, project, _utc_now(), full=True)
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


def load_scratch_findings(board_dir: Path, session: str | None = None) -> list[dict[str, Any]]:
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
                fallback_fingerprint = hashlib.sha256(
                    json.dumps(
                        finding,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                        default=str,
                    ).encode("utf-8")
                ).hexdigest()[:16]
                item["scratch_id"] = str(
                    item.get("scratch_id") or f"scratch:{relative}:{fallback_fingerprint}"
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
            fingerprint_payload = {
                key: item.get(key)
                for key in (
                    "type",
                    "title",
                    "affects",
                    "evidence_quote",
                    "discovered",
                )
            }
            fingerprint = hashlib.sha256(
                json.dumps(
                    fingerprint_payload,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()[:16]
            item["scratch_id"] = f"mcp:{relative}:{fingerprint}"
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


def plan_promotion(board_dir: Path, project: str, session: str | None = None) -> dict[str, Any]:
    """Create a no-write, content-bound foreground promotion plan."""
    board_dir = board_dir.resolve()
    findings = load_scratch_findings(board_dir, session)
    registry = load_pattern_registry(board_dir)
    # Promotion identity and provenance span the complete canonical lifecycle.
    # Graph ranking remains open-entry-only through load_entries().
    entries = _load_all_entries(board_dir)
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
            if str(entry.get("type")) == entry_type and str(entry.get("id", "")).startswith(prefix)
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
        duplicate_id = existing_by_key.get((entry_type, title.casefold(), affects))
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
        pattern_labels = _as_list(finding.get("pattern") or finding.get("patterns"))
        proposed_entry = {
            "id": entry_id,
            "type": entry_type,
            "pattern": pattern_labels,
            "_source": finding["_source_file"],
        }
        resolved, unresolved = resolve_entry_patterns(proposed_entry, registry)
        base.update(
            {
                "disposition": "create",
                "entry_id": entry_id,
                "priority": "P2" if entry_type in {"bug", "feature"} else None,
                "pattern": pattern_labels,
                "pattern_ids": [
                    item["id"] for item in resolved if not item["id"].startswith("legacy:")
                ],
                "unresolved_patterns": unresolved,
                "discovered": _oneline(finding.get("discovered") or _utc_now()[:10]),
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
        "summary": dict(Counter(item["disposition"] for item in planned)),
    }


def _write_promoted_entry(board_dir: Path, item: dict[str, Any], now: str) -> str:
    """Atomically write one planned canonical entry and return its path."""
    subdir = PROMOTION_TYPES[item["type"]][0]
    directory = board_dir / subdir
    directory.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", item["title"].casefold()).strip("-")[:60] or "finding"
    path = directory / f"{item['entry_id']}-{slug}.md"
    if path.exists():
        raise GraphError(f"plan_stale: target already exists: {path.name}")
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
                *["> " + line if line else ">" for line in item["evidence"].splitlines()],
                "",
            ]
        )
    if item.get("pattern_ids"):
        body_parts.extend(
            [
                "## Pattern history",
                "",
                f"- {now}: Assigned "
                + ", ".join(f"`{pattern_id}`" for pattern_id in item["pattern_ids"])
                + " during explicit foreground promotion.",
                "",
            ]
        )
    _atomic_write(
        path,
        serialize_frontmatter(fields) + "\n\n" + "\n".join(body_parts).rstrip() + "\n",
    )
    return path.relative_to(board_dir).as_posix()


def _promotion_plan_for_apply(
    board_dir: Path,
    project: str,
    session: str | None,
    plan_id: str,
) -> dict[str, Any]:
    """Find the live plan that matches an apply request."""
    selectors: list[str | None] = [session]
    if session is None:
        sessions_dir = board_dir / "_sessions"
        if sessions_dir.is_dir():
            selectors.extend(
                selector
                for path in sorted(sessions_dir.glob("*.md"), key=lambda item: item.name)
                for selector in (path.name, path.stem)
            )

    for selector in selectors:
        try:
            candidate = plan_promotion(board_dir, project, selector)
        except GraphError:
            # A scoped preview excludes every other scratch file. Preserve
            # that isolation while recovering its selector from the plan id.
            if session is not None:
                raise
            continue
        if candidate["plan_id"] == plan_id:
            return candidate
    raise GraphError("plan_stale: scratch or canonical inputs changed; preview again")


def apply_promotion(
    board_dir: Path,
    project: str,
    session: str | None,
    plan_id: str,
    archive_sources: bool = True,
) -> dict[str, Any]:
    """Apply an unchanged plan, restoring an omitted preview selector."""
    board_dir = board_dir.resolve()
    # A plan id binds the exact selector string used during preview. Codex can
    # therefore apply that plan without repeating the optional session input.
    plan = _promotion_plan_for_apply(board_dir, project, session, plan_id)
    now = _utc_now()
    results: list[dict[str, Any]] = []
    final_by_file: dict[str, list[str]] = {}
    log_path = board_dir / "consolidation.log"

    for item in plan["findings"]:
        result = dict(item)
        disposition = item["disposition"]
        if disposition == "create":
            try:
                result["file"] = _write_promoted_entry(board_dir, item, now)
                disposition = "created"
            except OSError as exc:
                disposition = "deferred"
                result["reason"] = "write_error:" + _oneline(str(exc))[:160]
        receipt = {
            "scratch_id": item["scratch_id"],
            "disposition": (
                f"promoted_{item['entry_id']}" if disposition == "created" else disposition
            ),
            "consolidated_at": now,
            "source": item["source_file"],
        }
        with log_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, sort_keys=True) + "\n")
        result["disposition"] = disposition
        results.append(result)
        final_by_file.setdefault(item["source_file"], []).append(disposition)

    archived: list[str] = []
    if archive_sources:
        archive_dir = board_dir / "_sessions" / "_archive"
        for relative, dispositions in sorted(final_by_file.items()):
            if not dispositions or not all(
                value in {"created", "deduplicated", "already_applied"} for value in dispositions
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

    graph, cache_path = build_graph_cached(board_dir, project, _utc_now(), full=True)
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
                key for key in ("id", "type", "title", "discovered") if not frontmatter.get(key)
            ]
            if missing:
                raise GraphError(f"{relative}: missing required field(s): {', '.join(missing)}")
            entry_id = str(frontmatter["id"])
            if not SAFE_ID.fullmatch(entry_id):
                raise GraphError(f"{relative}: unsafe or unsupported id {entry_id!r}")
            if entry_id in seen_ids:
                raise GraphError(
                    f"{relative}: duplicate id {entry_id} also used by {seen_ids[entry_id]}"
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
    left_parts = [part for part in str(left or "").replace("\\", "/").strip("/").split("/") if part]
    right_parts = [
        part for part in str(right or "").replace("\\", "/").strip("/").split("/") if part
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
    tag_counts = Counter(tag for entry in entries for tag in _as_list(entry.get("tags")))
    universal_tags = {tag for tag, count in tag_counts.items() if count > len(entries) / 2}

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
            left_patterns = {item["id"]: item for item in left.get("_resolved_patterns", [])}
            right_patterns = {item["id"]: item for item in right.get("_resolved_patterns", [])}
            shared_pattern_ids = sorted(set(left_patterns) & set(right_patterns))
            if shared_pattern_ids:
                shared_labels = sorted(
                    {left_patterns[pattern_id]["label"] for pattern_id in shared_pattern_ids}
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
                                "field": left_patterns[pattern_id]["source_field"],
                                "source": str(left["_source"]),
                            }
                            for pattern_id in shared_pattern_ids
                        ]
                        + [
                            {
                                "entry": right_id,
                                "field": right_patterns[pattern_id]["source_field"],
                                "source": str(right["_source"]),
                            }
                            for pattern_id in shared_pattern_ids
                        ],
                    )
                )
            affects_prefix = _shared_affects_prefix(left.get("affects"), right.get("affects"))
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
                (set(_as_list(left.get("tags"))) & set(_as_list(right.get("tags"))))
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
            values = sorted(set(previous["value"].split(", ")) | set(edge["value"].split(", ")))
            previous["value"] = ", ".join(values)
            if edge.get("pattern_ids"):
                previous["pattern_ids"] = sorted(
                    set(previous.get("pattern_ids", [])) | set(edge["pattern_ids"])
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
                previous["evidence"] = [combined[key] for key in sorted(combined)]
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
    adjacency: dict[str, set[str]] = {node_id: set() for node_id in node_ids}
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
            edge for edge in edges if edge["from"] in member_set and edge["to"] in member_set
        ]
        pair_count = len({(edge["from"], edge["to"]) for edge in internal})
        possible = len(members) * (len(members) - 1) / 2
        pattern_ids = sorted(
            {
                pattern["id"]
                for member in members
                for pattern in entry_by_id[member].get("_resolved_patterns", [])
            }
        )
        patterns = sorted(
            {
                pattern["label"]
                for member in members
                for pattern in entry_by_id[member].get("_resolved_patterns", [])
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
                        if edge["kind"] == kind and value in edge["value"].split(", ")
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
        for key in ("priority", "status", "affects", "discovered"):
            if entry.get(key):
                node[key] = str(entry[key])
        for key in ("tags", "pattern"):
            values = _as_list(entry.get(key))
            if values:
                node[key] = values
        resolved_patterns = entry.get("_resolved_patterns", [])
        if resolved_patterns:
            node["pattern_ids"] = [item["id"] for item in resolved_patterns]
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
                        if edge["from"] in cluster["members"] and edge["to"] in cluster["members"]
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
        "drill_in": {cluster["id"]: cluster["members"] for cluster in clusters},
    }


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(content)
    os.replace(temporary, path)


def _utc_now() -> str:
    return (
        dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )


def _bounded_text(value: Any, field: str, maximum: int, *, required: bool = True) -> str:
    text = "" if value is None else _oneline(value)
    if required and not text:
        raise GraphError(f"{field} is required")
    if len(text) > maximum:
        raise GraphError(f"{field} exceeds {maximum} characters")
    return text


def _parse_sections(body: str, source: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in body.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            if current in sections:
                raise GraphError(f"{source}: duplicate section {current!r}")
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
        elif line.strip():
            raise GraphError(f"{source}: content appears before the first section")
    missing = [name for name in HYPOTHESIS_SECTIONS if name not in sections]
    if missing:
        raise GraphError(f"{source}: missing required section(s): {', '.join(missing)}")
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def _hypothesis_inventory_fingerprint(board_dir: Path, paths: list[Path] | None = None) -> str:
    digest = hashlib.sha256()
    hypotheses_dir = board_dir / "hypotheses"
    if paths is None:
        paths = (
            sorted(hypotheses_dir.glob("H*.md"), key=lambda path: path.name)
            if hypotheses_dir.is_dir()
            else []
        )
    for path in paths:
        relative = path.relative_to(board_dir).as_posix()
        if path.is_symlink():
            raise GraphError(f"{relative}: linked hypothesis record is not allowed")
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        try:
            digest.update(path.read_bytes())
        except OSError as exc:
            raise GraphError(f"{relative}: unable to read: {exc}") from exc
        digest.update(b"\0")
    return digest.hexdigest()


def load_hypothesis_registry(board_dir: Path) -> dict[str, Any]:
    """Load and validate canonical H### hypothesis records."""
    board_dir = board_dir.resolve()
    hypotheses_dir = board_dir / "hypotheses"
    if hypotheses_dir.is_symlink():
        raise GraphError("hypotheses: linked canonical directory is not allowed")
    paths = (
        sorted(hypotheses_dir.glob("*.md"), key=lambda path: path.name)
        if hypotheses_dir.is_dir()
        else []
    )
    by_id: dict[str, dict[str, Any]] = {}
    by_claim: dict[str, list[str]] = {}
    for path in paths:
        relative = path.relative_to(board_dir).as_posix()
        if path.is_symlink():
            raise GraphError(f"{relative}: linked hypothesis record is not allowed")
        try:
            resolved = path.resolve(strict=True)
            resolved.relative_to(hypotheses_dir.resolve())
            text = path.read_text(encoding="utf-8")
        except (OSError, ValueError) as exc:
            raise GraphError(f"{relative}: unsafe or unreadable record: {exc}") from exc
        frontmatter, body = parse_frontmatter(text, relative)
        required = (
            "id",
            "type",
            "status",
            "title",
            "claim_key",
            "claim_fingerprint",
            "cluster_fingerprint",
            "graph_source_fingerprint",
            "confidence",
            "derived_from",
            "created",
            "last_evaluated",
            "revision",
        )
        missing = [key for key in required if not frontmatter.get(key)]
        if missing:
            raise GraphError(
                f"{relative}: missing required hypothesis field(s): " + ", ".join(missing)
            )
        hypothesis_id = str(frontmatter["id"])
        if not SAFE_HYPOTHESIS_ID.fullmatch(hypothesis_id):
            raise GraphError(f"{relative}: unsafe hypothesis id {hypothesis_id!r}")
        if hypothesis_id in by_id:
            raise GraphError(f"{relative}: duplicate hypothesis id {hypothesis_id}")
        if str(frontmatter["type"]) != "hypothesis":
            raise GraphError(f"{relative}: type must be 'hypothesis'")
        status = str(frontmatter["status"])
        if status not in HYPOTHESIS_STATUSES:
            raise GraphError(f"{relative}: invalid hypothesis status {status!r}")
        claim_key = str(frontmatter["claim_key"])
        if not SAFE_CLAIM_KEY.fullmatch(claim_key):
            raise GraphError(f"{relative}: invalid claim_key {claim_key!r}")
        claim_fingerprint = str(frontmatter["claim_fingerprint"])
        if not SAFE_CLAIM_FINGERPRINT.fullmatch(claim_fingerprint):
            raise GraphError(f"{relative}: invalid claim_fingerprint {claim_fingerprint!r}")
        cluster_fingerprint = str(frontmatter["cluster_fingerprint"])
        if not SAFE_CLUSTER_FINGERPRINT.fullmatch(cluster_fingerprint):
            raise GraphError(f"{relative}: invalid cluster_fingerprint {cluster_fingerprint!r}")
        graph_fingerprint = str(frontmatter["graph_source_fingerprint"])
        if not SAFE_SOURCE_FINGERPRINT.fullmatch(graph_fingerprint):
            raise GraphError(f"{relative}: invalid graph_source_fingerprint")
        confidence = str(frontmatter["confidence"])
        if confidence not in {"low", "medium", "high"}:
            raise GraphError(f"{relative}: invalid confidence {confidence!r}")
        pattern_ids = sorted(set(_as_list(frontmatter.get("pattern_ids"))))
        if any(not SAFE_PATTERN_ID.fullmatch(item) for item in pattern_ids):
            raise GraphError(f"{relative}: invalid pattern_ids")
        if claim_fingerprint != _claim_fingerprint(claim_key, pattern_ids):
            raise GraphError(
                f"{relative}: claim_fingerprint does not match claim_key and pattern_ids"
            )
        derived_from = _as_list(frontmatter["derived_from"])
        if not derived_from or any(not SAFE_EVIDENCE_ID.fullmatch(item) for item in derived_from):
            raise GraphError(f"{relative}: invalid derived_from evidence ids")
        try:
            revision = int(str(frontmatter["revision"]))
        except ValueError as exc:
            raise GraphError(f"{relative}: revision must be an integer") from exc
        if revision < 1:
            raise GraphError(f"{relative}: revision must be at least 1")
        for date_field in ("created", "last_evaluated"):
            if _valid_date(frontmatter[date_field]) is None:
                raise GraphError(f"{relative}: invalid {date_field} date")
        sections = _parse_sections(body, relative)
        record = {
            "id": hypothesis_id,
            "source": relative,
            "frontmatter": frontmatter,
            "sections": sections,
            "status": status,
            "claim_key": claim_key,
            "claim_fingerprint": claim_fingerprint,
            "cluster_fingerprint": cluster_fingerprint,
            "graph_source_fingerprint": graph_fingerprint,
            "derived_from": sorted(set(derived_from)),
            "text": text,
        }
        by_id[hypothesis_id] = record
        by_claim.setdefault(claim_fingerprint, []).append(hypothesis_id)
    duplicate_claims = {fingerprint: ids for fingerprint, ids in by_claim.items() if len(ids) > 1}
    if duplicate_claims:
        fingerprint, ids = sorted(duplicate_claims.items())[0]
        raise GraphError(
            f"duplicate hypothesis claim fingerprint {fingerprint}: {', '.join(sorted(ids))}"
        )
    return {
        "by_id": by_id,
        "by_claim": {fingerprint: sorted(ids) for fingerprint, ids in sorted(by_claim.items())},
        "fingerprint": _hypothesis_inventory_fingerprint(board_dir, paths),
    }


def list_hypotheses(board_dir: Path, project: str) -> dict[str, Any]:
    """Return public H### summaries with derived merge references."""
    board_dir = board_dir.resolve()
    graph = build_graph(board_dir, project, _utc_now(), build_mode="full")
    registry = load_hypothesis_registry(board_dir)
    merged_from: dict[str, list[str]] = {}
    for hypothesis_id, record in registry["by_id"].items():
        target = str(record["frontmatter"].get("merged_into") or "")
        if target:
            merged_from.setdefault(target, []).append(hypothesis_id)
    hypotheses: list[dict[str, Any]] = []
    cluster_fingerprints = {
        str(cluster.get("fingerprint")) for cluster in graph.get("topology", {}).get("clusters", [])
    }
    for hypothesis_id, record in sorted(registry["by_id"].items()):
        frontmatter = record["frontmatter"]
        hypotheses.append(
            {
                "id": hypothesis_id,
                "status": record["status"],
                "title": str(frontmatter["title"]),
                "claim_key": record["claim_key"],
                "claim_fingerprint": record["claim_fingerprint"],
                "cluster_fingerprint": record["cluster_fingerprint"],
                "graph_source_fingerprint": record["graph_source_fingerprint"],
                "pattern_ids": sorted(_as_list(frontmatter.get("pattern_ids"))),
                "confidence": str(frontmatter["confidence"]),
                "derived_from": record["derived_from"],
                "affected_domains": sorted(_as_list(frontmatter.get("affected_domains"))),
                "supersedes": sorted(_as_list(frontmatter.get("supersedes"))),
                "split_claim_keys": sorted(_as_list(frontmatter.get("split_claim_keys"))),
                "merged_into": frontmatter.get("merged_into"),
                "merged_from": sorted(merged_from.get(hypothesis_id, [])),
                "created": str(frontmatter["created"]),
                "last_evaluated": str(frontmatter["last_evaluated"]),
                "revision": int(str(frontmatter["revision"])),
                "stale": (
                    record["graph_source_fingerprint"] != graph["source_fingerprint"]
                    or record["cluster_fingerprint"] not in cluster_fingerprints
                ),
                "source": record["source"],
            }
        )
    return {
        "project": project,
        "graph_source_fingerprint": graph["source_fingerprint"],
        "hypothesis_inventory_fingerprint": registry["fingerprint"],
        "hypotheses": hypotheses,
    }


def _valid_date(value: Any) -> dt.date | None:
    try:
        return dt.date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def rank_clusters(graph: dict[str, Any]) -> dict[str, Any]:
    """Rank deterministic clusters with transparent, non-causal components."""
    nodes = graph.get("nodes", {})
    corpus_dates = [
        parsed
        for node in nodes.values()
        if (parsed := _valid_date(node.get("discovered"))) is not None
    ]
    reference_date = max(corpus_dates) if corpus_dates else None
    severity_points = {"P0": 20, "P1": 15, "P2": 10, "P3": 5}
    ranked: list[dict[str, Any]] = []
    warnings: list[str] = []
    for cluster in graph.get("topology", {}).get("clusters", []):
        members = sorted(cluster.get("members", []))
        member_nodes = [nodes.get(member, {}) for member in members]
        recurrence = min(len(members), 5) * 5
        domains = sorted(
            {
                str(node.get("affects", "")).replace("\\", "/").strip("/").split("/", 1)[0]
                for node in member_nodes
                if str(node.get("affects", "")).strip("/")
            }
        )
        diversity = min(len(domains), 5) * 5
        severity = max(
            [severity_points.get(str(node.get("priority", "")), 0) for node in member_nodes] or [0]
        )
        member_dates = [
            parsed
            for node in member_nodes
            if (parsed := _valid_date(node.get("discovered"))) is not None
        ]
        recency = 0
        newest = max(member_dates) if member_dates else None
        if reference_date and newest:
            age = (reference_date - newest).days
            recency = 15 if age <= 7 else 10 if age <= 30 else 5 if age <= 90 else 0
        elif members:
            warnings.append(f"{cluster.get('fingerprint')}: missing valid discovered dates")
        canonical_count = sum(1 for node in member_nodes if _as_list(node.get("pattern_ids")))
        canonical_points = (10 * canonical_count) // len(members) if members else 0
        signal_kinds = sorted(
            {str(signal.get("kind")) for signal in cluster.get("signals", []) if signal.get("kind")}
        )
        evidence_quality = canonical_points + (5 if len(signal_kinds) >= 2 else 0)
        components = {
            "recurrence": recurrence,
            "domain_diversity": diversity,
            "severity": severity,
            "relative_recency": recency,
            "evidence_quality": evidence_quality,
        }
        ranked.append(
            {
                "cluster_id": cluster.get("id"),
                "cluster_fingerprint": cluster.get("fingerprint"),
                "members": members,
                "member_sources": {
                    member: str(nodes.get(member, {}).get("source", "")) for member in members
                },
                "pattern_ids": sorted(cluster.get("pattern_ids", [])),
                "patterns": sorted(cluster.get("patterns", [])),
                "affected_domains": domains,
                "signal_kinds": signal_kinds,
                "score": sum(components.values()),
                "components": components,
                "inputs": {
                    "member_count": len(members),
                    "domain_count": len(domains),
                    "highest_priority": next(
                        (
                            priority
                            for priority in ("P0", "P1", "P2", "P3")
                            if any(
                                str(node.get("priority", "")) == priority for node in member_nodes
                            )
                        ),
                        None,
                    ),
                    "newest_discovered": newest.isoformat() if newest else None,
                    "canonical_pattern_members": canonical_count,
                    "signal_kind_count": len(signal_kinds),
                },
            }
        )
    ranked.sort(key=lambda item: (-item["score"], item["cluster_fingerprint"]))
    return {
        "ranking_rule_version": RANKING_RULE_VERSION,
        "reference_discovered": (reference_date.isoformat() if reference_date else None),
        "ranked_clusters": ranked,
        "warnings": sorted(set(warnings)),
    }


def build_insights(
    board_dir: Path,
    project: str,
    cluster_fingerprint: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Return ranked clusters plus hypothesis and negative-memory references."""
    board_dir = board_dir.resolve()
    graph = build_graph(board_dir, project, _utc_now(), build_mode="full")
    ranking = rank_clusters(graph)
    registry = load_hypothesis_registry(board_dir)
    clusters = ranking["ranked_clusters"]
    if cluster_fingerprint:
        if not SAFE_CLUSTER_FINGERPRINT.fullmatch(cluster_fingerprint):
            raise GraphError("invalid cluster fingerprint")
        clusters = [
            cluster for cluster in clusters if cluster["cluster_fingerprint"] == cluster_fingerprint
        ]
        if not clusters:
            raise GraphError(f"cluster not found: {cluster_fingerprint}")
    if limit is not None:
        if limit < 1 or limit > 100:
            raise GraphError("limit must be between 1 and 100")
        clusters = clusters[:limit]
    references: dict[str, list[dict[str, Any]]] = {}
    negative_memory: list[dict[str, Any]] = []
    for hypothesis_id, record in sorted(registry["by_id"].items()):
        summary = {
            "id": hypothesis_id,
            "status": record["status"],
            "claim_key": record["claim_key"],
            "claim_fingerprint": record["claim_fingerprint"],
            "cluster_fingerprint": record["cluster_fingerprint"],
            "stale": (
                record["graph_source_fingerprint"] != graph["source_fingerprint"]
                or not any(
                    cluster.get("fingerprint") == record["cluster_fingerprint"]
                    for cluster in graph.get("topology", {}).get("clusters", [])
                )
            ),
            "source": record["source"],
        }
        references.setdefault(record["cluster_fingerprint"], []).append(summary)
        if record["status"] == "rejected":
            negative_memory.append(summary)
    for cluster in clusters:
        cluster["hypothesis_refs"] = references.get(cluster["cluster_fingerprint"], [])
    return {
        "project": project,
        "graph_source_fingerprint": graph["source_fingerprint"],
        "ranking_rule_version": ranking["ranking_rule_version"],
        "reference_discovered": ranking["reference_discovered"],
        "ranked_clusters": clusters,
        "negative_memory": negative_memory,
        "warnings": ranking["warnings"],
    }


def _load_all_entries(board_dir: Path) -> list[dict[str, Any]]:
    """Load canonical entries, including resolved entries, in stable order."""
    entries: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    board_real = board_dir.resolve()
    for subdir in ENTRY_SUBDIRS:
        root = board_dir / subdir
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.md"), key=lambda item: item.name):
            relative = path.relative_to(board_dir).as_posix()
            if path.is_symlink():
                raise GraphError(f"{relative}: linked entry is not allowed")
            try:
                path.resolve(strict=True).relative_to(board_real)
                text = path.read_text(encoding="utf-8")
            except (OSError, ValueError) as exc:
                raise GraphError(f"{relative}: unsafe or unreadable entry") from exc
            frontmatter, body = parse_frontmatter(text, relative)
            missing = [
                key for key in ("id", "type", "title", "discovered") if not frontmatter.get(key)
            ]
            if missing:
                raise GraphError(f"{relative}: missing required field(s): {', '.join(missing)}")
            entry_id = str(frontmatter["id"])
            if not SAFE_ID.fullmatch(entry_id):
                raise GraphError(f"{relative}: unsafe or unsupported id {entry_id!r}")
            if entry_id in seen:
                raise GraphError(
                    f"{relative}: duplicate id {entry_id} also used by {seen[entry_id]}"
                )
            seen[entry_id] = relative
            entry = dict(frontmatter)
            entry["_source"] = relative
            entry["_body"] = body
            entries.append(entry)
    return sorted(entries, key=lambda item: str(item["id"]))


def _body_section(body: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        body,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match else ""


def _load_learnings(board_dir: Path) -> dict[str, Any]:
    """Load canonical L### records and preserve their readable bodies."""
    root = board_dir / "learnings"
    by_id: dict[str, dict[str, Any]] = {}
    by_pattern: dict[str, str] = {}
    digest = hashlib.sha256()
    if not root.is_dir():
        return {"by_id": by_id, "by_pattern": by_pattern, "fingerprint": digest.hexdigest()}
    root_real = root.resolve()
    for path in sorted(root.glob("*.md"), key=lambda item: item.name):
        relative = path.relative_to(board_dir).as_posix()
        if path.is_symlink():
            raise GraphError(f"{relative}: linked Learning record is not allowed")
        try:
            path.resolve(strict=True).relative_to(root_real)
            text = path.read_text(encoding="utf-8")
        except (OSError, ValueError) as exc:
            raise GraphError(f"{relative}: unsafe or unreadable Learning") from exc
        frontmatter, body = parse_frontmatter(text, relative)
        learning_id = str(frontmatter.get("id") or "")
        if not re.fullmatch(r"L[0-9]{3,}", learning_id):
            raise GraphError(f"{relative}: invalid Learning id {learning_id!r}")
        if learning_id in by_id:
            raise GraphError(f"{relative}: duplicate Learning id {learning_id}")
        if str(frontmatter.get("type") or "") != "learning":
            raise GraphError(f"{relative}: type must be 'learning'")
        outcome_status = str(frontmatter.get("outcome_status") or "untested")
        if outcome_status not in LEARNING_OUTCOME_STATUSES:
            raise GraphError(f"{relative}: invalid outcome_status {outcome_status!r}")
        confidence = str(frontmatter.get("confidence") or "")
        if confidence not in {"low", "medium", "high"}:
            raise GraphError(f"{relative}: invalid confidence {confidence!r}")
        applies_to = sorted(
            {
                _normalize_context_path(value, "applies_to")
                for value in _as_list(frontmatter.get("applies_to"))
            }
        )
        pattern_tag = normalize_pattern_label(str(frontmatter.get("pattern_tag") or ""))
        pattern_ids = sorted(
            item
            for item in _as_list(frontmatter.get("pattern_ids"))
            if SAFE_PATTERN_ID.fullmatch(item)
        )
        record = {
            "id": learning_id,
            "source": relative,
            "frontmatter": frontmatter,
            "body": body,
            "title": str(frontmatter.get("title") or learning_id),
            "takeaway": _body_section(body, "Takeaway"),
            "derived_from": sorted(_as_list(frontmatter.get("derived_from"))),
            "pattern_tag": pattern_tag,
            "pattern_ids": pattern_ids,
            "applies_to": applies_to,
            "confidence": confidence,
            "outcome_status": outcome_status,
            "outcome_refs": sorted(_as_list(frontmatter.get("outcome_refs"))),
            "text": text,
        }
        by_id[learning_id] = record
        for token in pattern_ids + ([pattern_tag] if pattern_tag else []):
            if token in by_pattern and by_pattern[token] != learning_id:
                raise GraphError(f"{relative}: duplicate Learning pattern {token}")
            by_pattern[token] = learning_id
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(text.encode("utf-8"))
        digest.update(b"\0")
    return {
        "by_id": by_id,
        "by_pattern": by_pattern,
        "fingerprint": digest.hexdigest(),
    }


def _memory_source_fingerprint(
    graph_fingerprint: str,
    hypothesis_fingerprint: str,
    learning_fingerprint: str,
) -> str:
    return hashlib.sha256(
        "\0".join((graph_fingerprint, hypothesis_fingerprint, learning_fingerprint)).encode("utf-8")
    ).hexdigest()


def _normalize_context_path(
    value: Any,
    field: str,
    *,
    allow_root: bool = False,
) -> str:
    text = str(value or "").replace("\\", "/").strip()
    if not text or len(text) > 512:
        raise GraphError(f"{field} must contain 1 through 512 characters")
    if text.startswith("/") or re.match(r"^[A-Za-z]:", text):
        raise GraphError(f"{field} must be repository-relative")
    parts = [part for part in text.split("/") if part not in {"", "."}]
    if not parts:
        if allow_root:
            return "."
        raise GraphError(f"{field} contains an unsafe path")
    if any(part == ".." for part in parts):
        raise GraphError(f"{field} contains an unsafe path")
    return "/".join(parts)


def _path_has_segment_overlap(left: str, right: str) -> bool:
    left_parts = [part.casefold() for part in left.replace("\\", "/").split("/") if part]
    right_parts = [part.casefold() for part in right.replace("\\", "/").split("/") if part]
    if not left_parts or not right_parts:
        return False
    shorter, longer = (
        (left_parts, right_parts)
        if len(left_parts) <= len(right_parts)
        else (right_parts, left_parts)
    )
    return any(
        longer[index : index + len(shorter)] == shorter
        for index in range(len(longer) - len(shorter) + 1)
    )


def _path_is_in_scope(path: str, scope: str) -> bool:
    """Return true when a repository path is inside the declared scope."""
    path_parts = [part.casefold() for part in path.replace("\\", "/").split("/") if part]
    scope_parts = [part.casefold() for part in scope.replace("\\", "/").split("/") if part]
    if not path_parts or not scope_parts or len(scope_parts) > len(path_parts):
        return False
    return path_parts[: len(scope_parts)] == scope_parts


def _context_task_tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", value).casefold())
        if len(token) >= 3 and token not in CONTEXT_STOPWORDS
    }


def _bounded_context_text(value: Any, maximum: int) -> str:
    """Return one bounded line of untrusted canonical memory content."""
    return _oneline(value)[:maximum]


def _graph_distance(graph: dict[str, Any], starts: set[str], targets: set[str]) -> int | None:
    if starts & targets:
        return 0
    adjacency: dict[str, set[str]] = {}
    for edge in graph.get("edges", []):
        left = str(edge.get("from") or "")
        right = str(edge.get("to") or "")
        if left and right:
            adjacency.setdefault(left, set()).add(right)
            adjacency.setdefault(right, set()).add(left)
    frontier = set(starts)
    seen = set(starts)
    for distance in (1, 2):
        frontier = {
            neighbor
            for node in frontier
            for neighbor in adjacency.get(node, set())
            if neighbor not in seen
        }
        if frontier & targets:
            return distance
        seen.update(frontier)
    return None


def _encode_context_token(payload: dict[str, Any]) -> str:
    raw_payload = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    envelope = {
        "payload": payload,
        "checksum": hashlib.sha256(raw_payload.encode("utf-8")).hexdigest(),
    }
    raw = json.dumps(envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _decode_context_token(token: str) -> dict[str, Any]:
    token = str(token or "")
    if not token or len(token) > 16384 or not re.fullmatch(r"[A-Za-z0-9_-]+", token):
        raise GraphError("invalid context token")
    try:
        raw = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))
        envelope = json.loads(raw.decode("utf-8"))
        payload = envelope["payload"]
        checksum = envelope["checksum"]
    except (ValueError, KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GraphError("invalid context token") from exc
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if (
        not isinstance(payload, dict)
        or checksum != hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    ):
        raise GraphError("invalid context token checksum")
    return payload


def build_context(
    board_dir: Path,
    project: str,
    *,
    task: str = "",
    files: list[str] | None = None,
    entry_ids: list[str] | None = None,
    cwd: str = "",
    limit: int = CONTEXT_RESULT_LIMIT,
    result_kinds: set[str] | None = None,
) -> dict[str, Any]:
    """Return deterministic repository memory for one bounded context."""
    board_dir = board_dir.resolve()
    project = _bounded_text(project, "project", 160)
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 10:
        raise GraphError("limit must be between 1 and 10")
    allowed_result_kinds = {
        "cluster",
        "hypothesis",
        "learning",
        "negative_memory",
    }
    if result_kinds is None:
        normalized_result_kinds = allowed_result_kinds
    elif (
        not isinstance(result_kinds, set)
        or not result_kinds
        or not result_kinds <= allowed_result_kinds
    ):
        raise GraphError("result_kinds contains an unsupported memory kind")
    else:
        normalized_result_kinds = set(result_kinds)
    task = "" if task is None else str(task)
    if len(task) > 4000:
        raise GraphError("task exceeds 4000 characters")
    if files is None:
        files = []
    if not isinstance(files, list) or len(files) > 100:
        raise GraphError("files must be a list with at most 100 paths")
    normalized_files = sorted({_normalize_context_path(value, "files") for value in files})
    if entry_ids is None:
        entry_ids = []
    if not isinstance(entry_ids, list) or len(entry_ids) > 50:
        raise GraphError("entry_ids must be a list with at most 50 ids")
    normalized_entry_ids = sorted({str(value or "") for value in entry_ids})
    if any(not SAFE_ID.fullmatch(value) for value in normalized_entry_ids):
        raise GraphError("entry_ids contains an invalid canonical entry id")
    cwd_relative = ""
    if cwd:
        cwd_path = Path(str(cwd))
        repository_root = cache_path_for_board(board_dir, project).parents[4]
        try:
            if cwd_path.is_absolute():
                cwd_relative = cwd_path.resolve().relative_to(repository_root.resolve()).as_posix()
            else:
                cwd_relative = _normalize_context_path(str(cwd), "cwd", allow_root=True)
        except (OSError, ValueError) as exc:
            raise GraphError("cwd must be inside the repository") from exc
    if not task.strip() and not normalized_files and not normalized_entry_ids and not cwd_relative:
        raise GraphError("at least one context field is required")

    graph = build_graph(board_dir, project, _utc_now(), build_mode="full")
    ranking = rank_clusters(graph)
    patterns = load_pattern_registry(board_dir)
    hypotheses = load_hypothesis_registry(board_dir)
    learnings = _load_learnings(board_dir)
    all_entries = _load_all_entries(board_dir)
    entries_by_id = {str(entry["id"]): entry for entry in all_entries}
    missing_entries = [
        entry_id for entry_id in normalized_entry_ids if entry_id not in entries_by_id
    ]
    if missing_entries:
        raise GraphError(f"unknown context entry id(s): {', '.join(missing_entries)}")
    for entry in all_entries:
        resolved, _ = resolve_entry_patterns(entry, patterns)
        entry["_resolved_patterns"] = resolved
    source_fp = _memory_source_fingerprint(
        graph["source_fingerprint"],
        hypotheses["fingerprint"],
        learnings["fingerprint"],
    )
    explicit_pattern_ids = {
        match.upper() for match in re.findall(r"\bP[0-9]{3,}\b", task, flags=re.IGNORECASE)
    }
    normalized_task = normalize_pattern_label(task)
    for pattern_id, record in patterns["by_id"].items():
        if any(
            f"-{token}-" in f"-{normalized_task}-"
            for token in [record["label"]] + record["aliases"]
            if token
        ):
            explicit_pattern_ids.add(pattern_id)
    entry_pattern_ids = {
        pattern["id"]
        for entry_id in normalized_entry_ids
        for pattern in entries_by_id[entry_id].get("_resolved_patterns", [])
    }
    context_paths = list(normalized_files)
    if cwd_relative:
        context_paths.append(cwd_relative)
    context_paths.extend(
        _normalize_context_path(entries_by_id[entry_id].get("affects"), "entry affects")
        for entry_id in normalized_entry_ids
        if str(entries_by_id[entry_id].get("affects") or "").strip()
    )
    context_paths = sorted(set(context_paths))
    task_tokens = _context_task_tokens(task)
    entry_pattern_tags = {
        normalize_pattern_label(pattern)
        for entry_id in normalized_entry_ids
        for pattern in _as_list(entries_by_id[entry_id].get("pattern"))
        if normalize_pattern_label(pattern)
    }

    candidates: list[dict[str, Any]] = []
    ranked_by_fp = {str(item["cluster_fingerprint"]): item for item in ranking["ranked_clusters"]}
    for cluster_fp, cluster in sorted(ranked_by_fp.items()):
        pattern_ids = set(cluster.get("pattern_ids", []))
        pattern_labels = sorted({str(value) for value in cluster.get("patterns", []) if str(value)})
        members = set(cluster.get("members", []))
        affected_domains = sorted(
            {str(value) for value in cluster.get("affected_domains", []) if str(value)}
        )
        summary_parts = []
        if pattern_ids:
            summary_parts.append("Pattern IDs: " + ", ".join(sorted(pattern_ids)))
        if pattern_labels:
            summary_parts.append("Normalized patterns: " + ", ".join(pattern_labels))
        summary_parts.append("Members: " + ", ".join(sorted(members)))
        if affected_domains:
            summary_parts.append("Affected domains: " + ", ".join(affected_domains))
        candidates.append(
            {
                "kind": "cluster",
                "id": cluster_fp,
                "status": "active",
                "stale": False,
                "pattern_ids": pattern_ids,
                "pattern_tags": set(pattern_labels),
                "members": members,
                "applies_to": set(),
                "confidence": None,
                "title": _bounded_context_text(
                    " / ".join(pattern_labels) or f"Cluster {cluster_fp}",
                    CONTEXT_TITLE_LIMIT,
                ),
                "summary_kind": "cluster_scope",
                "summary": _bounded_context_text(
                    ". ".join(summary_parts) + ".",
                    CONTEXT_SUMMARY_LIMIT,
                ),
                "texts": pattern_labels,
                "source_refs": sorted(set(cluster.get("member_sources", {}).values())),
            }
        )
    cluster_fps = set(ranked_by_fp)
    for hypothesis_id, record in sorted(hypotheses["by_id"].items()):
        frontmatter = record["frontmatter"]
        rejected = record["status"] == "rejected"
        candidates.append(
            {
                "kind": "negative_memory" if rejected else "hypothesis",
                "id": hypothesis_id,
                "status": record["status"],
                "stale": (
                    record["graph_source_fingerprint"] != graph["source_fingerprint"]
                    or record["cluster_fingerprint"] not in cluster_fps
                ),
                "pattern_ids": set(_as_list(frontmatter.get("pattern_ids"))),
                "pattern_tags": set(),
                "members": set(record["derived_from"]),
                "applies_to": set(),
                "confidence": str(frontmatter.get("confidence") or ""),
                "title": _bounded_context_text(
                    frontmatter.get("title") or hypothesis_id,
                    CONTEXT_TITLE_LIMIT,
                ),
                "summary_kind": "proposed_root_cause",
                "summary": _bounded_context_text(
                    record["sections"].get("Proposed root cause", ""),
                    CONTEXT_SUMMARY_LIMIT,
                ),
                "texts": [
                    str(frontmatter.get("title") or ""),
                    record["claim_key"],
                    record["sections"].get("Proposed root cause", ""),
                ],
                "source_refs": [record["source"]]
                + [
                    str(entries_by_id.get(item, {}).get("_source") or "")
                    for item in record["derived_from"]
                ],
            }
        )
    for learning_id, record in sorted(learnings["by_id"].items()):
        learning_patterns = set(record["pattern_ids"])
        if not learning_patterns and record["pattern_tag"]:
            matched = patterns["by_token"].get(record["pattern_tag"])
            if matched:
                learning_patterns.add(matched)
        candidates.append(
            {
                "kind": "learning",
                "id": learning_id,
                "status": record["outcome_status"],
                "stale": False,
                "pattern_ids": learning_patterns,
                "pattern_tags": ({record["pattern_tag"]} if record["pattern_tag"] else set()),
                "members": set(record["derived_from"]),
                "applies_to": set(record["applies_to"]),
                "confidence": record["confidence"],
                "title": _bounded_context_text(
                    record["title"],
                    CONTEXT_TITLE_LIMIT,
                ),
                "summary_kind": "learning_takeaway",
                "summary": _bounded_context_text(
                    record["takeaway"],
                    CONTEXT_SUMMARY_LIMIT,
                ),
                "texts": [record["title"], record["takeaway"], record["pattern_tag"]],
                "source_refs": [record["source"]]
                + [
                    str(entries_by_id.get(item, {}).get("_source") or "")
                    for item in record["derived_from"]
                ],
            }
        )

    results: list[dict[str, Any]] = []
    for candidate in candidates:
        if candidate["kind"] not in normalized_result_kinds:
            continue
        components = {
            "canonical_pattern": 0,
            "affected_path": 0,
            "graph_proximity": 0,
            "intent_overlap": 0,
            "outcome_relevance": 0,
        }
        matched_signals: list[str] = []
        pattern_ids = set(candidate["pattern_ids"])
        pattern_tags = set(candidate["pattern_tags"])
        if pattern_ids & explicit_pattern_ids:
            components["canonical_pattern"] = 35
            matched_signals.append(
                "explicit-pattern:" + ",".join(sorted(pattern_ids & explicit_pattern_ids))
            )
        elif pattern_ids & entry_pattern_ids:
            components["canonical_pattern"] = 30 if candidate["kind"] == "learning" else 25
            matched_signals.append(
                "entry-pattern:" + ",".join(sorted(pattern_ids & entry_pattern_ids))
            )
        elif candidate["kind"] == "learning" and pattern_tags & entry_pattern_tags:
            components["canonical_pattern"] = 30
            matched_signals.append(
                "entry-pattern-tag:" + ",".join(sorted(pattern_tags & entry_pattern_tags))
            )
        member_entries = [
            entries_by_id[item] for item in sorted(candidate["members"]) if item in entries_by_id
        ]
        affected = sorted(
            {
                str(entry.get("affects") or "").replace("\\", "/").strip("/")
                for entry in member_entries
                if str(entry.get("affects") or "").strip("/")
            }
        )
        evidence_path_matches = sorted(
            {
                f"{context_path}~{affected_path}"
                for context_path in context_paths
                for affected_path in affected
                if _path_has_segment_overlap(context_path, affected_path)
            }
        )
        learning_scope_matches = sorted(
            {
                f"{context_path}~{scope_path}"
                for context_path in context_paths
                for scope_path in candidate["applies_to"]
                if _path_is_in_scope(context_path, scope_path)
            }
        )
        if evidence_path_matches or learning_scope_matches:
            components["affected_path"] = 30
        if learning_scope_matches:
            matched_signals.append("learning-applies-to:" + ",".join(learning_scope_matches[:5]))
        if evidence_path_matches:
            matched_signals.append("affected-path:" + ",".join(evidence_path_matches[:5]))
        distance = (
            _graph_distance(graph, set(normalized_entry_ids), set(candidate["members"]))
            if normalized_entry_ids
            else None
        )
        if distance is not None:
            components["graph_proximity"] = {0: 20, 1: 12, 2: 6}[distance]
            matched_signals.append(f"graph-distance:{distance}")
        candidate_tokens = _context_task_tokens(" ".join(candidate["texts"]))
        overlap = sorted(task_tokens & candidate_tokens)
        if overlap:
            components["intent_overlap"] = min(len(overlap) * 2, 10)
            matched_signals.append("intent:" + ",".join(overlap[:5]))
        if candidate["kind"] == "negative_memory" or candidate["status"] in {
            "confirmed",
            "supported",
        }:
            components["outcome_relevance"] = 5
            matched_signals.append("outcome:" + str(candidate["status"]))
        elif candidate["status"] in {"weakened", "contested"}:
            components["outcome_relevance"] = 2
            matched_signals.append("outcome:" + str(candidate["status"]))
        structural = (
            components["canonical_pattern"]
            + components["affected_path"]
            + components["graph_proximity"]
        )
        score = sum(components.values())
        if structural <= 0 or score < 30:
            continue
        why_parts = []
        if components["canonical_pattern"]:
            why_parts.append("It shares a canonical pattern with this context.")
        if learning_scope_matches:
            why_parts.append("Its declared Learning scope overlaps a context path.")
        if evidence_path_matches:
            why_parts.append("Its cited evidence overlaps a context path.")
        if components["graph_proximity"]:
            why_parts.append("Its evidence is near a selected entry in the graph.")
        if components["intent_overlap"]:
            why_parts.append("Its title or takeaway shares bounded task terms.")
        if components["outcome_relevance"]:
            why_parts.append("Its recorded outcome changes retrieval priority.")
        direct_negative = (
            candidate["kind"] == "negative_memory"
            and max(
                components["canonical_pattern"],
                components["affected_path"],
                components["graph_proximity"],
            )
            >= 20
        )
        results.append(
            {
                "kind": candidate["kind"],
                "id": candidate["id"],
                "status": candidate["status"],
                "title": candidate["title"],
                "summary_kind": candidate["summary_kind"],
                "summary": candidate["summary"],
                "confidence": candidate["confidence"],
                "stale": candidate["stale"],
                "score": score,
                "components": components,
                "matched_signals": matched_signals,
                "why": " ".join(why_parts),
                "source_refs": sorted({value for value in candidate["source_refs"] if value}),
                "_tie": (
                    0
                    if direct_negative
                    else 1
                    if candidate["kind"] == "hypothesis"
                    else 2
                    if candidate["kind"] == "learning"
                    else 3
                    if candidate["kind"] == "cluster"
                    else 4
                ),
            }
        )
    results.sort(key=lambda item: (-item["score"], item["_tie"], item["id"]))
    results = results[:limit]
    for item in results:
        item.pop("_tie", None)
    warnings = set(ranking["warnings"])
    if (
        task.strip()
        and not normalized_files
        and not normalized_entry_ids
        and not cwd_relative
        and not results
    ):
        warnings.add(
            "No memory was eligible from task text alone. Add files, entry_ids, "
            "or cwd to provide a structural signal."
        )
    request_digest = hashlib.sha256(
        json.dumps(
            {
                "project": project,
                "task_digest": hashlib.sha256(task.encode("utf-8")).hexdigest(),
                "files": normalized_files,
                "entry_ids": normalized_entry_ids,
                "cwd": cwd_relative,
                "limit": limit,
                "result_kinds": sorted(normalized_result_kinds),
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    context_material = {
        "request_digest": request_digest,
        "source_fingerprint": source_fp,
        "context_contract_version": CONTEXT_CONTRACT_VERSION,
        "ranking_rule_version": CONTEXT_RANKING_RULE_VERSION,
        "result_ids": [item["id"] for item in results],
    }
    context_fingerprint = (
        "ctx-"
        + hashlib.sha256(
            json.dumps(context_material, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()[:16]
    )
    return {
        "project": project,
        "context_fingerprint": context_fingerprint,
        "source_fingerprint": source_fp,
        "ranking_rule_version": CONTEXT_RANKING_RULE_VERSION,
        "context_contract_version": CONTEXT_CONTRACT_VERSION,
        "results": results,
        "warnings": sorted(warnings),
        "context_token": _encode_context_token(context_material),
    }


def _claim_fingerprint(claim_key: str, pattern_ids: list[str]) -> str:
    payload = {
        "claim_key": claim_key,
        "pattern_ids": sorted(set(pattern_ids)),
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"h-{digest}"


def _all_canonical_entry_ids(board_dir: Path) -> set[str]:
    result: set[str] = set()
    for subdir in ENTRY_SUBDIRS + ("learnings",):
        root = board_dir / subdir
        if not root.is_dir():
            continue
        for path in root.glob("*.md"):
            if path.is_symlink():
                raise GraphError(
                    f"{path.relative_to(board_dir).as_posix()}: linked evidence "
                    "record is not allowed"
                )
            frontmatter, _ = parse_frontmatter(
                path.read_text(encoding="utf-8"),
                path.relative_to(board_dir).as_posix(),
            )
            entry_id = str(frontmatter.get("id") or "")
            if SAFE_EVIDENCE_ID.fullmatch(entry_id):
                result.add(entry_id)
    return result


def _normalize_evidence_ids(
    values: Any, valid_ids: set[str], field: str, *, required: bool = True
) -> list[str]:
    ids = sorted(set(_as_list(values)))
    if required and not ids:
        raise GraphError(f"{field} requires at least one evidence id")
    invalid = [
        item for item in ids if not SAFE_EVIDENCE_ID.fullmatch(item) or item not in valid_ids
    ]
    if invalid:
        raise GraphError(f"{field} contains unknown evidence id(s): {', '.join(invalid)}")
    return ids


def _serialize_hypothesis(record: dict[str, Any]) -> str:
    frontmatter = record["frontmatter"]
    field_order = (
        "id",
        "type",
        "status",
        "title",
        "claim_key",
        "claim_fingerprint",
        "cluster_fingerprint",
        "graph_source_fingerprint",
        "pattern_ids",
        "confidence",
        "derived_from",
        "affected_domains",
        "supersedes",
        "split_claim_keys",
        "merged_into",
        "created",
        "last_evaluated",
        "revision",
    )
    fields = [(key, frontmatter.get(key)) for key in field_order if key in frontmatter]
    sections = record["sections"]
    body = "\n\n".join(
        f"## {name}\n\n{sections.get(name, '')}".rstrip() for name in HYPOTHESIS_SECTIONS
    )
    return serialize_frontmatter(fields) + "\n\n" + body + "\n"


def _encode_plan(payload: dict[str, Any]) -> tuple[str, str]:
    plan_id = _plan_id(payload)
    envelope = {"payload": payload, "plan_id": plan_id}
    raw = json.dumps(envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    token = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    return token, plan_id


def _decode_plan(token: str) -> dict[str, Any]:
    token = str(token or "")
    if not token or len(token) > 65536 or not re.fullmatch(r"[A-Za-z0-9_-]+", token):
        raise GraphError("invalid hypothesis plan token")
    try:
        raw = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))
        envelope = json.loads(raw.decode("utf-8"))
        payload = envelope["payload"]
        plan_id = envelope["plan_id"]
    except (ValueError, KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GraphError("invalid hypothesis plan token") from exc
    if (
        not isinstance(envelope, dict)
        or not isinstance(payload, dict)
        or plan_id != _plan_id(payload)
    ):
        raise GraphError("invalid hypothesis plan checksum")
    return dict(envelope)


def _cluster_by_fingerprint(graph: dict[str, Any], cluster_fingerprint: str) -> dict[str, Any]:
    if not SAFE_CLUSTER_FINGERPRINT.fullmatch(cluster_fingerprint):
        raise GraphError("invalid cluster fingerprint")
    for cluster in graph.get("topology", {}).get("clusters", []):
        if isinstance(cluster, dict) and cluster.get("fingerprint") == cluster_fingerprint:
            return dict(cluster)
    raise GraphError(f"cluster not found: {cluster_fingerprint}")


def _history_line(
    date: str,
    status: str,
    actor: str,
    evidence_ids: list[str],
    reason: str,
) -> str:
    evidence = ", ".join(evidence_ids) if evidence_ids else "none"
    return (
        f"- {date}: status `{status}` via explicit apply by `{actor}`; "
        f"evidence [{evidence}]; {reason}"
    )


def _append_history(sections: dict[str, str], line: str) -> dict[str, str]:
    updated = dict(sections)
    prior = updated.get("Outcome history", "").rstrip()
    updated["Outcome history"] = (prior + "\n" + line).strip()
    return updated


def _structured_outcomes(sections: dict[str, str]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in sections.get("Outcome history", "").splitlines():
        prefix = "- outcome-json: "
        if not line.startswith(prefix):
            continue
        try:
            event = json.loads(line[len(prefix) :])
        except json.JSONDecodeError as exc:
            raise GraphError("invalid structured outcome history") from exc
        required = {
            "event_id",
            "entry_id",
            "hypothesis_id",
            "fix_result",
            "hypothesis_disposition",
            "fix_summary",
            "evidence_ids",
            "observed_until",
            "actor",
            "context_used",
        }
        if not isinstance(event, dict) or not required.issubset(event):
            raise GraphError("incomplete structured outcome history")
        events.append(event)
    return events


def plan_hypothesis_operation(
    board_dir: Path,
    project: str,
    action: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Validate a hypothesis mutation and return a self-contained plan token."""
    board_dir = board_dir.resolve()
    action = str(action or "").strip().lower()
    if action not in {"propose", "evaluate", "reopen", "split", "merge"}:
        raise GraphError("invalid hypothesis action")
    graph = build_graph(board_dir, project, _utc_now(), build_mode="full")
    registry = load_hypothesis_registry(board_dir)
    valid_ids = _all_canonical_entry_ids(board_dir)
    date = _utc_now()[:10]
    operation: dict[str, Any]
    request: dict[str, Any]

    if action == "propose":
        cluster_fingerprint = _bounded_text(
            params.get("cluster_fingerprint"), "cluster_fingerprint", 18
        )
        cluster = _cluster_by_fingerprint(graph, cluster_fingerprint)
        claim_key = _bounded_text(params.get("claim_key"), "claim_key", 80)
        if not SAFE_CLAIM_KEY.fullmatch(claim_key):
            raise GraphError("claim_key must be lowercase kebab-case")
        title = _bounded_text(params.get("title"), "title", 160)
        root_cause = _bounded_text(params.get("root_cause"), "root_cause", 2000)
        confidence = _bounded_text(params.get("confidence"), "confidence", 6)
        if confidence not in {"low", "medium", "high"}:
            raise GraphError("confidence must be low, medium, or high")
        confidence_basis = _bounded_text(params.get("confidence_basis"), "confidence_basis", 800)
        falsifier = _bounded_text(params.get("falsifier"), "falsifier", 800)
        alternatives_raw = params.get("alternatives")
        if not isinstance(alternatives_raw, list) or not alternatives_raw:
            raise GraphError("alternatives requires at least one explanation")
        if len(alternatives_raw) > 5:
            raise GraphError("alternatives permits at most five explanations")
        alternatives = [_bounded_text(value, "alternative", 400) for value in alternatives_raw]
        counter_raw = params.get("counter_evidence", [])
        if not isinstance(counter_raw, list):
            raise GraphError("counter_evidence must be a list")
        counter_evidence = [_bounded_text(value, "counter_evidence", 400) for value in counter_raw]
        evidence_raw = params.get("supporting_evidence")
        if not isinstance(evidence_raw, list):
            raise GraphError("supporting_evidence must be a list")
        supporting: list[dict[str, str]] = []
        for item in evidence_raw:
            if not isinstance(item, dict):
                raise GraphError("each supporting evidence item must be an object")
            evidence_id = _bounded_text(item.get("id"), "evidence id", 16)
            if evidence_id not in valid_ids:
                raise GraphError(f"unknown supporting evidence id {evidence_id}")
            supporting.append(
                {
                    "id": evidence_id,
                    "reason": _bounded_text(item.get("reason"), "evidence reason", 400),
                }
            )
        required_members = sorted(cluster.get("members", []))
        supplied_members = sorted(item["id"] for item in supporting)
        if supplied_members != required_members or len(set(supplied_members)) != len(
            supplied_members
        ):
            raise GraphError("supporting_evidence must cite every cluster member exactly once")
        pattern_ids = sorted(cluster.get("pattern_ids", []))
        claim_fingerprint = _claim_fingerprint(claim_key, pattern_ids)
        existing = [
            registry["by_id"][hypothesis_id]
            for hypothesis_id in registry["by_claim"].get(claim_fingerprint, [])
        ]
        rejected = [record for record in existing if record["status"] == "rejected"]
        if rejected:
            record = rejected[0]
            return {
                "project": project,
                "action": action,
                "disposition": "blocked_by_negative_memory",
                "hypothesis_id": record["id"],
                "claim_fingerprint": claim_fingerprint,
                "rejecting_outcome": record["status"],
                "evaluated_evidence": record["derived_from"],
                "message": (f"{record['id']} rejected this claim; use reopen with new evidence"),
                "writes_canonical": False,
                "plan_token": None,
            }
        if existing:
            raise GraphError("duplicate_claim: " + ", ".join(record["id"] for record in existing))
        supersedes = sorted(set(_as_list(params.get("supersedes"))))
        for parent_id in supersedes:
            parent = registry["by_id"].get(parent_id)
            if (
                not parent
                or parent["status"] != "split"
                or claim_key not in _as_list(parent["frontmatter"].get("split_claim_keys"))
            ):
                raise GraphError(f"supersedes requires split parent authorizing {claim_key}")
        next_number = (
            max([int(hypothesis_id[1:]) for hypothesis_id in registry["by_id"]] or [0]) + 1
        )
        hypothesis_id = f"H{next_number:03d}"
        frontmatter = {
            "id": hypothesis_id,
            "type": "hypothesis",
            "status": "proposed",
            "title": title,
            "claim_key": claim_key,
            "claim_fingerprint": claim_fingerprint,
            "cluster_fingerprint": cluster_fingerprint,
            "graph_source_fingerprint": graph["source_fingerprint"],
            "pattern_ids": pattern_ids,
            "confidence": confidence,
            "derived_from": required_members,
            "affected_domains": sorted(cluster.get("affected_domains", [])),
            "supersedes": supersedes,
            "created": date,
            "last_evaluated": date,
            "revision": 1,
        }
        sections = {
            "Proposed root cause": root_cause,
            "Supporting evidence": "\n".join(
                f"- {item['id']}: {item['reason']}"
                for item in sorted(supporting, key=lambda item: item["id"])
            ),
            "Alternative explanations": "\n".join(f"- {value}" for value in alternatives),
            "Counter-evidence": (
                "\n".join(f"- {value}" for value in counter_evidence)
                if counter_evidence
                else "None found during this cited review."
            ),
            "Confidence basis": confidence_basis,
            "Falsifier": falsifier,
            "Outcome history": _history_line(
                date,
                "proposed",
                _bounded_text(params.get("actor"), "actor", 120),
                required_members,
                "Created from the selected deterministic cluster; not confirmed.",
            ),
        }
        target = f"hypotheses/{hypothesis_id}-{claim_key}.md"
        record = {"frontmatter": frontmatter, "sections": sections}
        request = {
            "cluster_fingerprint": cluster_fingerprint,
            "claim_key": claim_key,
            "title": title,
            "root_cause": root_cause,
            "supporting_evidence": supporting,
            "alternatives": alternatives,
            "counter_evidence": counter_evidence,
            "confidence": confidence,
            "confidence_basis": confidence_basis,
            "falsifier": falsifier,
            "supersedes": supersedes,
            "actor": _bounded_text(params.get("actor"), "actor", 120),
        }
        operation = {
            "action": action,
            "target": target,
            "id": hypothesis_id,
            "record": record,
        }
    else:
        hypothesis_id = _bounded_text(params.get("hypothesis_id"), "hypothesis_id", 16)
        record_current = registry["by_id"].get(hypothesis_id)
        if not record_current:
            raise GraphError(f"hypothesis not found: {hypothesis_id}")
        frontmatter = dict(record_current["frontmatter"])
        sections = dict(record_current["sections"])
        actor = _bounded_text(params.get("actor"), "actor", 120)
        reason_field = "new_evidence_reason" if action == "reopen" else "reason"
        reason = _bounded_text(params.get(reason_field), reason_field, 800)
        evidence_ids = _normalize_evidence_ids(
            params.get("evidence_ids"), valid_ids, "evidence_ids"
        )
        request = {
            "hypothesis_id": hypothesis_id,
            "actor": actor,
            reason_field: reason,
            "evidence_ids": evidence_ids,
        }
        current_status = record_current["status"]
        new_status: str
        if action == "evaluate":
            new_status = _bounded_text(params.get("status"), "status", 16)
            allowed = {
                "proposed": {"weakened", "confirmed", "rejected"},
                "weakened": {"proposed", "confirmed", "rejected"},
                "confirmed": {"weakened", "rejected"},
            }
            if new_status not in allowed.get(current_status, set()):
                raise GraphError(
                    f"unsupported hypothesis transition {current_status} -> {new_status}"
                )
            request["status"] = new_status
            requested_confidence = params.get("confidence")
            if requested_confidence is not None:
                confidence_value = _bounded_text(requested_confidence, "confidence", 6)
                if confidence_value not in {"low", "medium", "high"}:
                    raise GraphError("confidence must be low, medium, or high")
                frontmatter["confidence"] = confidence_value
                request["confidence"] = confidence_value
        elif action == "reopen":
            if current_status != "rejected":
                raise GraphError("reopen requires a rejected hypothesis")
            cluster_fingerprint = _bounded_text(
                params.get("cluster_fingerprint"),
                "cluster_fingerprint",
                18,
            )
            cluster = _cluster_by_fingerprint(graph, cluster_fingerprint)
            current_members = set(cluster.get("members", []))
            old_members = set(record_current["derived_from"])
            new_members = set(evidence_ids) - old_members
            if not new_members:
                raise GraphError("reopen requires at least one new evidence id")
            if not old_members.issubset(current_members) or not new_members.issubset(
                current_members
            ):
                raise GraphError("reopen cluster must contain retained and new evidence")
            frontmatter["cluster_fingerprint"] = cluster_fingerprint
            frontmatter["graph_source_fingerprint"] = graph["source_fingerprint"]
            frontmatter["pattern_ids"] = sorted(cluster.get("pattern_ids", []))
            frontmatter["affected_domains"] = sorted(cluster.get("affected_domains", []))
            frontmatter["derived_from"] = sorted(current_members)
            new_status = "proposed"
            request["cluster_fingerprint"] = cluster_fingerprint
        elif action == "split":
            if current_status not in {"proposed", "weakened", "rejected"}:
                raise GraphError(f"cannot split {current_status} hypothesis")
            claim_keys = sorted(set(_as_list(params.get("claim_keys"))))
            if len(claim_keys) < 2 or any(
                not SAFE_CLAIM_KEY.fullmatch(item) for item in claim_keys
            ):
                raise GraphError("split requires at least two unique kebab-case claim keys")
            frontmatter["split_claim_keys"] = claim_keys
            request["claim_keys"] = claim_keys
            new_status = "split"
        else:
            if current_status not in {"proposed", "weakened", "rejected"}:
                raise GraphError(f"cannot merge {current_status} hypothesis")
            target_id = _bounded_text(params.get("into"), "into", 16)
            target_record = registry["by_id"].get(target_id)
            if (
                target_id == hypothesis_id
                or not target_record
                or target_record["status"] not in HYPOTHESIS_ACTIVE_STATUSES
            ):
                raise GraphError("merge target must be a different active hypothesis")
            frontmatter["merged_into"] = target_id
            request["into"] = target_id
            new_status = "merged"
        if action in {"evaluate", "reopen"}:
            requested_cluster_fingerprint = params.get("cluster_fingerprint")
            stale = record_current["graph_source_fingerprint"] != graph["source_fingerprint"]
            if stale and action == "evaluate" and not requested_cluster_fingerprint:
                raise GraphError("stale hypothesis evaluation requires current cluster_fingerprint")
            if requested_cluster_fingerprint and action == "evaluate":
                cluster_value = _bounded_text(
                    requested_cluster_fingerprint,
                    "cluster_fingerprint",
                    18,
                )
                cluster = _cluster_by_fingerprint(graph, cluster_value)
                frontmatter["cluster_fingerprint"] = cluster_value
                frontmatter["graph_source_fingerprint"] = graph["source_fingerprint"]
                frontmatter["pattern_ids"] = sorted(cluster.get("pattern_ids", []))
                frontmatter["affected_domains"] = sorted(cluster.get("affected_domains", []))
                frontmatter["derived_from"] = sorted(
                    set(_as_list(frontmatter.get("derived_from"))) | set(cluster.get("members", []))
                )
                request["cluster_fingerprint"] = cluster_value
        frontmatter["status"] = new_status
        frontmatter["last_evaluated"] = date
        frontmatter["revision"] = int(str(frontmatter["revision"])) + 1
        history_reason = reason
        if record_current["graph_source_fingerprint"] != frontmatter.get(
            "graph_source_fingerprint"
        ):
            history_reason += (
                f" Rebound graph {record_current['graph_source_fingerprint'][:12]}"
                f" to {frontmatter['graph_source_fingerprint'][:12]}."
            )
        sections = _append_history(
            sections,
            _history_line(date, new_status, actor, evidence_ids, history_reason),
        )
        operation = {
            "action": action,
            "target": record_current["source"],
            "id": hypothesis_id,
            "record": {"frontmatter": frontmatter, "sections": sections},
        }

    target_path = (board_dir / operation["target"]).resolve()
    target_bytes_fingerprint = (
        hashlib.sha256(target_path.read_bytes()).hexdigest()
        if target_path.is_file() and not target_path.is_symlink()
        else "absent"
    )
    payload = {
        "version": 1,
        "project": project,
        "action": action,
        "request": request,
        "graph_source_fingerprint": graph["source_fingerprint"],
        "hypothesis_inventory_fingerprint": registry["fingerprint"],
        "target_bytes_fingerprint": target_bytes_fingerprint,
        "operation": operation,
    }
    token, plan_id = _encode_plan(payload)
    return {
        "project": project,
        "action": action,
        "operation": operation,
        "graph_source_fingerprint": graph["source_fingerprint"],
        "hypothesis_inventory_fingerprint": registry["fingerprint"],
        "plan_id": plan_id,
        "plan_token": token,
        "writes_canonical": False,
    }


def _hypothesis_lock_path(board_dir: Path, project: str) -> Path:
    cache_path = cache_path_for_board(board_dir, project)
    safe_project = re.sub(r"[^A-Za-z0-9._-]+", "-", project).strip("-")
    return cache_path.parents[3] / "locks" / "hypotheses" / f"{safe_project}.lock"


def apply_hypothesis_plan(board_dir: Path, project: str, plan_token: str) -> dict[str, Any]:
    """Revalidate and apply one content-bound hypothesis plan."""
    board_dir = board_dir.resolve()
    envelope = _decode_plan(plan_token)
    payload = envelope["payload"]
    if payload.get("project") != project:
        raise GraphError("hypothesis plan project mismatch")
    try:
        fresh = plan_hypothesis_operation(
            board_dir,
            project,
            str(payload.get("action") or ""),
            dict(payload.get("request") or {}),
        )
    except GraphError as exc:
        raise GraphError("plan_stale: canonical inputs changed; request a fresh preview") from exc
    if fresh.get("plan_id") != envelope["plan_id"]:
        raise GraphError("plan_stale: canonical inputs changed; request a fresh preview")
    lock_path = _hypothesis_lock_path(board_dir, project)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    acquired = False
    for _ in range(20):
        try:
            lock_path.mkdir()
            acquired = True
            break
        except FileExistsError:
            time.sleep(0.05)
    if not acquired:
        raise GraphError("lock_contended: retry the hypothesis apply")
    try:
        try:
            fresh = plan_hypothesis_operation(
                board_dir,
                project,
                str(payload.get("action") or ""),
                dict(payload.get("request") or {}),
            )
        except GraphError as exc:
            raise GraphError("plan_stale: canonical inputs changed after lock acquisition") from exc
        if fresh.get("plan_id") != envelope["plan_id"]:
            raise GraphError("plan_stale: canonical inputs changed after lock acquisition")
        operation = fresh["operation"]
        target = (board_dir / operation["target"]).resolve()
        hypotheses_dir = (board_dir / "hypotheses").resolve()
        try:
            target.relative_to(hypotheses_dir)
        except ValueError as exc:
            raise GraphError("unsafe hypothesis target path") from exc
        if target.is_symlink():
            raise GraphError("linked hypothesis target is not mutable")
        if operation["action"] == "propose" and target.exists():
            raise GraphError("plan_stale: hypothesis target already exists")
        content = _serialize_hypothesis(operation["record"])
        _atomic_write(target, content)
        return {
            "project": project,
            "action": operation["action"],
            "applied": True,
            "id": operation["id"],
            "changed": operation["target"],
            "plan_id": fresh["plan_id"],
            "graph_source_fingerprint": fresh["graph_source_fingerprint"],
            "hypothesis_inventory_fingerprint": load_hypothesis_registry(board_dir)["fingerprint"],
        }
    finally:
        try:
            lock_path.rmdir()
        except OSError:
            pass


def _learning_state(recurrence: int, events: list[dict[str, Any]]) -> tuple[str, str, str]:
    results = {str(event.get("fix_result") or "") for event in events}
    if "partial" in results or ("held" in results and "failed" in results):
        outcome_status = "contested"
    elif "held" in results:
        outcome_status = "supported"
    elif "failed" in results:
        outcome_status = "weakened"
    else:
        outcome_status = "untested"
    if outcome_status == "supported":
        confidence = "high" if recurrence >= 3 else "medium"
    elif outcome_status == "untested":
        confidence = "medium" if recurrence >= 3 else "low"
    else:
        confidence = "low"
    basis = (
        f"{recurrence} resolved source entr"
        f"{'y' if recurrence == 1 else 'ies'}; outcome state {outcome_status} "
        "from structured hypothesis fix results."
    )
    return outcome_status, confidence, basis


def _serialize_learning(record: dict[str, Any]) -> str:
    frontmatter = record["frontmatter"]
    field_order = (
        "id",
        "type",
        "subtype",
        "title",
        "discovered",
        "status",
        "confidence",
        "confidence_basis",
        "recurrence",
        "derived_from",
        "applies_to",
        "pattern_ids",
        "pattern_tag",
        "outcome_status",
        "outcome_refs",
    )
    fields = [
        (key, frontmatter.get(key)) for key in field_order if frontmatter.get(key) is not None
    ]
    return serialize_frontmatter(fields) + "\n\n" + str(record["body"]).strip() + "\n"


def plan_learning_feedback(board_dir: Path, project: str, pattern_id: str) -> dict[str, Any]:
    """Preview one outcome-aware pattern Learning update."""
    board_dir = board_dir.resolve()
    pattern_id = _bounded_text(pattern_id, "pattern_id", 128)
    patterns = load_pattern_registry(board_dir)
    if pattern_id.startswith("legacy:"):
        legacy_label = normalize_pattern_label(pattern_id.split(":", 1)[1])
        if not legacy_label:
            raise GraphError("legacy pattern label is empty")
        resolved_id = f"legacy:{legacy_label}"
        pattern = {"label": legacy_label}
    else:
        resolved_id, _ = _resolved_pattern_id(pattern_id, patterns)
        pattern = patterns["by_id"][resolved_id]
    entries = _load_all_entries(board_dir)
    resolved_sources: list[dict[str, Any]] = []
    for entry in entries:
        if str(entry.get("status") or "open") != "resolved":
            continue
        entry_patterns, _ = resolve_entry_patterns(entry, patterns)
        if resolved_id in {item["id"] for item in entry_patterns}:
            resolved_sources.append(entry)
    if not resolved_sources:
        raise GraphError(f"pattern {resolved_id} has no resolved canonical source entries")
    hypotheses = load_hypothesis_registry(board_dir)
    events: list[dict[str, Any]] = []
    outcome_refs: set[str] = set()
    for hypothesis_id, hypothesis in hypotheses["by_id"].items():
        if resolved_id not in _as_list(hypothesis["frontmatter"].get("pattern_ids")):
            continue
        hypothesis_events = _structured_outcomes(hypothesis["sections"])
        if hypothesis_events:
            outcome_refs.add(hypothesis_id)
            events.extend(hypothesis_events)
    outcome_status, confidence, confidence_basis = _learning_state(len(resolved_sources), events)
    learnings = _load_learnings(board_dir)
    existing_id = learnings["by_pattern"].get(resolved_id) or learnings["by_pattern"].get(
        pattern["label"]
    )
    existing = learnings["by_id"].get(existing_id) if existing_id else None
    derived_from = sorted(str(entry["id"]) for entry in resolved_sources)
    earliest = min(str(entry.get("discovered") or "1970-01-01") for entry in resolved_sources)
    if existing:
        frontmatter = dict(existing["frontmatter"])
        learning_id = existing["id"]
        target = existing["source"]
        body = existing["body"]
    else:
        next_number = max([int(item[1:]) for item in learnings["by_id"]] or [0]) + 1
        learning_id = f"L{next_number:03d}"
        target = f"learnings/{learning_id}-{pattern['label']}.md"
        frontmatter = {
            "id": learning_id,
            "type": "learning",
            "subtype": "pattern",
            "title": f"Recurring pattern: {pattern['label']}",
            "discovered": earliest,
            "status": "open",
        }
        body = (
            "## Takeaway\n\n"
            f"The `{pattern['label']}` pattern has surfaced across "
            f"{len(resolved_sources)} resolved entries. Review the cited "
            "resolutions before another local fix.\n\n"
            "## Sources\n\n"
            + "\n".join(
                f"- {entry['id']}: {entry['title']} ({entry['discovered']})"
                for entry in resolved_sources
            )
            + "\n\n## When this applies\n\n"
            "Use this Learning when a new finding shares the canonical pattern."
        )
    frontmatter.update(
        {
            "confidence": confidence,
            "confidence_basis": confidence_basis,
            "recurrence": len(resolved_sources),
            "derived_from": derived_from,
            "pattern_ids": ([resolved_id] if SAFE_PATTERN_ID.fullmatch(resolved_id) else []),
            "pattern_tag": pattern["label"],
            "outcome_status": outcome_status,
            "outcome_refs": sorted(outcome_refs),
        }
    )
    record = {"frontmatter": frontmatter, "body": body}
    content = _serialize_learning(record)
    target_path = (board_dir / target).resolve()
    current = (
        target_path.read_text(encoding="utf-8")
        if target_path.is_file() and not target_path.is_symlink()
        else None
    )
    if current == content:
        return {
            "project": project,
            "pattern_id": resolved_id,
            "learning_id": learning_id,
            "disposition": "already_up_to_date",
            "old": {
                "outcome_status": outcome_status,
                "confidence": confidence,
                "recurrence": len(resolved_sources),
            },
            "new": {
                "outcome_status": outcome_status,
                "confidence": confidence,
                "recurrence": len(resolved_sources),
            },
            "plan_token": None,
            "writes_canonical": False,
        }
    operation = {
        "action": "update" if existing else "create",
        "target": target,
        "id": learning_id,
        "record": record,
    }
    payload = {
        "version": 1,
        "kind": "learning_feedback",
        "project": project,
        "request": {"pattern_id": resolved_id},
        "graph_source_fingerprint": source_fingerprint(board_dir),
        "hypothesis_inventory_fingerprint": hypotheses["fingerprint"],
        "learning_inventory_fingerprint": learnings["fingerprint"],
        "operation": operation,
        "result_content_fingerprint": hashlib.sha256(content.encode("utf-8")).hexdigest(),
    }
    token, plan_id = _encode_plan(payload)
    return {
        "project": project,
        "pattern_id": resolved_id,
        "learning_id": learning_id,
        "operation": operation,
        "old": (
            {
                "outcome_status": existing["outcome_status"],
                "confidence": str(existing["frontmatter"].get("confidence") or "low"),
                "recurrence": int(str(existing["frontmatter"].get("recurrence") or 0)),
            }
            if existing
            else None
        ),
        "new": {
            "outcome_status": outcome_status,
            "confidence": confidence,
            "recurrence": len(resolved_sources),
        },
        "cited_sources": derived_from,
        "rationale": confidence_basis,
        "plan_id": plan_id,
        "plan_token": token,
        "writes_canonical": False,
    }


def _learning_lock_path(board_dir: Path, project: str) -> Path:
    cache_path = cache_path_for_board(board_dir, project)
    safe_project = re.sub(r"[^A-Za-z0-9._-]+", "-", project).strip("-")
    return cache_path.parents[3] / "locks" / "learnings" / f"{safe_project}.lock"


def apply_learning_plan(board_dir: Path, project: str, plan_token: str) -> dict[str, Any]:
    """Revalidate and atomically apply one pattern Learning plan."""
    board_dir = board_dir.resolve()
    envelope = _decode_plan(plan_token)
    payload = envelope["payload"]
    if payload.get("kind") != "learning_feedback" or payload.get("project") != project:
        raise GraphError("Learning plan project or kind mismatch")
    operation = dict(payload.get("operation") or {})
    target = (board_dir / str(operation.get("target") or "")).resolve()
    learnings_dir = (board_dir / "learnings").resolve()
    try:
        target.relative_to(learnings_dir)
    except ValueError as exc:
        raise GraphError("unsafe Learning target path") from exc
    expected_digest = str(payload.get("result_content_fingerprint") or "")
    if target.is_file() and not target.is_symlink():
        current_digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if current_digest == expected_digest:
            return {
                "project": project,
                "applied": False,
                "disposition": "already_applied",
                "id": operation.get("id"),
                "changed": operation.get("target"),
                "plan_id": envelope["plan_id"],
            }
    try:
        fresh = plan_learning_feedback(
            board_dir, project, str(payload.get("request", {}).get("pattern_id") or "")
        )
    except GraphError as exc:
        raise GraphError("plan_stale: canonical Learning inputs changed") from exc
    if fresh.get("plan_id") != envelope["plan_id"]:
        raise GraphError("plan_stale: canonical Learning inputs changed")
    lock_path = _learning_lock_path(board_dir, project)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock_path.mkdir()
    except FileExistsError as exc:
        raise GraphError("lock_contended: retry the Learning apply") from exc
    try:
        fresh = plan_learning_feedback(board_dir, project, str(payload["request"]["pattern_id"]))
        if fresh.get("plan_id") != envelope["plan_id"]:
            raise GraphError("plan_stale: canonical Learning inputs changed after lock acquisition")
        operation = fresh["operation"]
        target = (board_dir / operation["target"]).resolve()
        if target.is_symlink():
            raise GraphError("linked Learning target is not mutable")
        content = _serialize_learning(operation["record"])
        _atomic_write(target, content)
        return {
            "project": project,
            "applied": True,
            "action": operation["action"],
            "id": operation["id"],
            "changed": operation["target"],
            "plan_id": fresh["plan_id"],
            "learning_inventory_fingerprint": _load_learnings(board_dir)["fingerprint"],
        }
    finally:
        try:
            lock_path.rmdir()
        except OSError:
            pass


def plan_outcome(board_dir: Path, project: str, params: dict[str, Any]) -> dict[str, Any]:
    """Preview one explicit fix outcome without changing canonical state."""
    board_dir = board_dir.resolve()
    entry_id = _bounded_text(params.get("entry_id"), "entry_id", 16)
    hypothesis_id = _bounded_text(params.get("hypothesis_id"), "hypothesis_id", 16)
    fix_result = _bounded_text(params.get("fix_result"), "fix_result", 16)
    disposition = _bounded_text(
        params.get("hypothesis_disposition"),
        "hypothesis_disposition",
        16,
    )
    if fix_result not in FIX_RESULTS:
        raise GraphError("invalid fix_result")
    if disposition not in OUTCOME_DISPOSITIONS[fix_result]:
        raise GraphError(f"fix_result {fix_result} is incompatible with disposition {disposition}")
    fix_summary = _bounded_text(params.get("fix_summary"), "fix_summary", 1000)
    actor = _bounded_text(params.get("actor"), "actor", 120)
    observed_until = _bounded_text(params.get("observed_until"), "observed_until", 10)
    observed_date = _valid_date(observed_until)
    if observed_date is None:
        raise GraphError("observed_until must use ISO YYYY-MM-DD")
    valid_ids = _all_canonical_entry_ids(board_dir)
    evidence_ids = _normalize_evidence_ids(params.get("evidence_ids"), valid_ids, "evidence_ids")
    entries = {str(item["id"]): item for item in _load_all_entries(board_dir)}
    entry = entries.get(entry_id)
    if not entry:
        raise GraphError(f"entry not found: {entry_id}")
    discovered = _valid_date(entry.get("discovered"))
    if discovered and observed_date < discovered:
        raise GraphError("observed_until cannot precede entry discovery")
    if fix_result == "held" and (
        str(entry.get("status") or "open") != "resolved" or entry_id not in evidence_ids
    ):
        raise GraphError("held requires a resolved entry cited as completion evidence")
    graph = build_graph(board_dir, project, _utc_now(), build_mode="full")
    registry = load_hypothesis_registry(board_dir)
    hypothesis = registry["by_id"].get(hypothesis_id)
    if not hypothesis:
        raise GraphError(f"hypothesis not found: {hypothesis_id}")
    if hypothesis["status"] in {"merged", "split"}:
        raise GraphError("outcome requires an active or rejected hypothesis")
    patterns = load_pattern_registry(board_dir)
    entry_patterns, _ = resolve_entry_patterns(entry, patterns)
    entry_pattern_ids = {item["id"] for item in entry_patterns}
    hypothesis_pattern_ids = set(_as_list(hypothesis["frontmatter"].get("pattern_ids")))
    cluster_members: set[str] = set()
    for cluster in graph.get("topology", {}).get("clusters", []):
        if cluster.get("fingerprint") == hypothesis["cluster_fingerprint"]:
            cluster_members.update(cluster.get("members", []))
    allowed_entry = (
        entry_id in hypothesis["derived_from"]
        or entry_id in cluster_members
        or bool(entry_pattern_ids & hypothesis_pattern_ids)
    )
    if not allowed_entry:
        raise GraphError("entry is not a cited source, cluster member, or same-pattern neighbor")
    context_used = params.get("context_used", False)
    if not isinstance(context_used, bool):
        raise GraphError("context_used must be a boolean")
    context_token = str(params.get("context_token") or "")
    context_reference: dict[str, Any] | None = None
    if context_used and not context_token:
        raise GraphError("context_used requires context_token")
    if context_token:
        token_payload = _decode_context_token(context_token)
        surfaced = set(_as_list(token_payload.get("result_ids")))
        if hypothesis_id not in surfaced and hypothesis["cluster_fingerprint"] not in surfaced:
            raise GraphError("context token did not surface the target hypothesis")
        learnings = _load_learnings(board_dir)
        current_source = _memory_source_fingerprint(
            graph["source_fingerprint"],
            registry["fingerprint"],
            learnings["fingerprint"],
        )
        context_reference = {
            "context_fingerprint": "ctx-"
            + hashlib.sha256(
                json.dumps(token_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()[:16],
            "source_fingerprint": str(token_payload.get("source_fingerprint") or ""),
            "source_state": (
                "current" if token_payload.get("source_fingerprint") == current_source else "stale"
            ),
            "verified": True,
        }
    event_base = {
        "entry_id": entry_id,
        "hypothesis_id": hypothesis_id,
        "fix_result": fix_result,
        "hypothesis_disposition": disposition,
        "fix_summary": fix_summary,
        "evidence_ids": evidence_ids,
        "observed_until": observed_until,
        "actor": actor,
        "context_used": context_used,
        "context_reference": context_reference,
    }
    event_id = (
        "out-"
        + hashlib.sha256(
            json.dumps(
                event_base, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()[:16]
    )
    event = {"event_id": event_id, **event_base}
    existing_events = _structured_outcomes(hypothesis["sections"])
    if any(item.get("event_id") == event_id for item in existing_events):
        return {
            "project": project,
            "action": "outcome",
            "disposition": "already_applied",
            "event_id": event_id,
            "hypothesis_id": hypothesis_id,
            "plan_token": None,
            "writes_canonical": False,
        }
    frontmatter = dict(hypothesis["frontmatter"])
    if disposition != "unchanged":
        frontmatter["status"] = disposition
    frontmatter["last_evaluated"] = _utc_now()[:10]
    frontmatter["revision"] = int(str(frontmatter["revision"])) + 1
    sections = _append_history(
        hypothesis["sections"],
        "- outcome-json: "
        + json.dumps(event, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
    )
    operation = {
        "action": "outcome",
        "target": hypothesis["source"],
        "id": hypothesis_id,
        "event_id": event_id,
        "record": {"frontmatter": frontmatter, "sections": sections},
    }
    plan_request = {
        "entry_id": entry_id,
        "hypothesis_id": hypothesis_id,
        "fix_result": fix_result,
        "hypothesis_disposition": disposition,
        "fix_summary": fix_summary,
        "evidence_ids": evidence_ids,
        "observed_until": observed_until,
        "actor": actor,
        "context_used": context_used,
        "context_token": context_token,
    }
    predicted_feedback = []
    for pattern_id in sorted(hypothesis_pattern_ids):
        resolved_count = 0
        for candidate in entries.values():
            if str(candidate.get("status") or "open") != "resolved":
                continue
            candidate_patterns, _ = resolve_entry_patterns(candidate, patterns)
            if pattern_id in {item["id"] for item in candidate_patterns}:
                resolved_count += 1
        pattern_events = [
            outcome
            for other_id, other in registry["by_id"].items()
            if pattern_id in _as_list(other["frontmatter"].get("pattern_ids"))
            for outcome in _structured_outcomes(other["sections"])
            if not (other_id == hypothesis_id and outcome.get("event_id") == event_id)
        ]
        status, confidence, basis = _learning_state(resolved_count, pattern_events + [event])
        predicted_feedback.append(
            {
                "pattern_id": pattern_id,
                "outcome_status": status,
                "confidence": confidence,
                "rationale": basis,
                "applies_after_outcome": True,
            }
        )
    payload = {
        "version": 1,
        "kind": "outcome",
        "project": project,
        "request": plan_request,
        "event_id": event_id,
        "operation": operation,
    }
    token, plan_id = _encode_plan(payload)
    return {
        "project": project,
        "action": "outcome",
        "event": event,
        "operation": operation,
        "learning_feedback": predicted_feedback,
        "plan_id": plan_id,
        "plan_token": token,
        "writes_canonical": False,
    }


def apply_outcome_plan(board_dir: Path, project: str, plan_token: str) -> dict[str, Any]:
    """Revalidate and atomically apply one explicit H### fix outcome."""
    board_dir = board_dir.resolve()
    envelope = _decode_plan(plan_token)
    payload = envelope["payload"]
    if payload.get("kind") != "outcome" or payload.get("project") != project:
        raise GraphError("outcome plan project or kind mismatch")
    hypothesis_id = str(payload.get("operation", {}).get("id") or "")
    current = load_hypothesis_registry(board_dir)["by_id"].get(hypothesis_id)
    if current and any(
        event.get("event_id") == payload.get("event_id")
        for event in _structured_outcomes(current["sections"])
    ):
        return {
            "project": project,
            "applied": False,
            "disposition": "already_applied",
            "id": hypothesis_id,
            "event_id": payload.get("event_id"),
            "plan_id": envelope["plan_id"],
        }
    try:
        fresh = plan_outcome(board_dir, project, dict(payload.get("request") or {}))
    except GraphError as exc:
        raise GraphError("plan_stale: canonical outcome inputs changed") from exc
    if fresh.get("plan_id") != envelope["plan_id"]:
        raise GraphError("plan_stale: canonical outcome inputs changed")
    lock_path = _hypothesis_lock_path(board_dir, project)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock_path.mkdir()
    except FileExistsError as exc:
        raise GraphError("lock_contended: retry the outcome apply") from exc
    try:
        fresh = plan_outcome(board_dir, project, dict(payload["request"]))
        if fresh.get("plan_id") != envelope["plan_id"]:
            raise GraphError("plan_stale: canonical outcome inputs changed after lock acquisition")
        operation = fresh["operation"]
        target = (board_dir / operation["target"]).resolve()
        hypotheses_dir = (board_dir / "hypotheses").resolve()
        try:
            target.relative_to(hypotheses_dir)
        except ValueError as exc:
            raise GraphError("unsafe hypothesis outcome target path") from exc
        if target.is_symlink():
            raise GraphError("linked hypothesis target is not mutable")
        _atomic_write(target, _serialize_hypothesis(operation["record"]))
    finally:
        try:
            lock_path.rmdir()
        except OSError:
            pass
    learning_feedback = []
    pattern_ids = _as_list(operation["record"]["frontmatter"].get("pattern_ids"))
    for pattern_id in pattern_ids:
        try:
            learning_feedback.append(plan_learning_feedback(board_dir, project, pattern_id))
        except GraphError as exc:
            learning_feedback.append(
                {
                    "pattern_id": pattern_id,
                    "error": "learning_feedback_unavailable",
                    "detail": str(exc),
                }
            )
    return {
        "project": project,
        "action": "outcome",
        "applied": True,
        "id": operation["id"],
        "event_id": operation["event_id"],
        "changed": operation["target"],
        "plan_id": fresh["plan_id"],
        "hypothesis_inventory_fingerprint": load_hypothesis_registry(board_dir)["fingerprint"],
        "learning_feedback": learning_feedback,
    }


def build_value_report(board_dir: Path, project: str) -> dict[str, Any]:
    """Derive product-value counts only from canonical outcome history."""
    board_dir = board_dir.resolve()
    hypotheses = load_hypothesis_registry(board_dir)
    learnings = _load_learnings(board_dir)
    hypotheses_with_outcomes = 0
    confirmed_systemic_fixes = 0
    useful_resurfacing_events = 0
    for hypothesis in hypotheses["by_id"].values():
        events = _structured_outcomes(hypothesis["sections"])
        if events:
            hypotheses_with_outcomes += 1
        if (
            hypothesis["status"] == "confirmed"
            and len(_as_list(hypothesis["frontmatter"].get("affected_domains"))) >= 2
            and any(
                event.get("fix_result") == "held"
                and event.get("hypothesis_disposition") == "confirmed"
                for event in events
            )
        ):
            confirmed_systemic_fixes += 1
        useful_resurfacing_events += sum(
            1
            for event in events
            if event.get("context_used") is True
            and isinstance(event.get("context_reference"), dict)
            and event["context_reference"].get("verified") is True
        )
    learning_outcomes = dict.fromkeys(sorted(LEARNING_OUTCOME_STATUSES), 0)
    for learning in learnings["by_id"].values():
        learning_outcomes[learning["outcome_status"]] += 1
    return {
        "project": project,
        "hypotheses_with_structured_outcomes": hypotheses_with_outcomes,
        "learning_outcomes": learning_outcomes,
        "confirmed_systemic_fixes": confirmed_systemic_fixes,
        "useful_resurfacing_events": useful_resurfacing_events,
        "source": "canonical H### outcome history and L### outcome fields",
    }


def curate_learning_feedback(
    board_dir: Path, project: str, min_recurrence: int = 3
) -> dict[str, Any]:
    """Apply eligible pattern Learning plans sequentially for an authorized PM."""
    if isinstance(min_recurrence, bool) or not isinstance(min_recurrence, int):
        raise GraphError("min_recurrence must be an integer")
    if min_recurrence < 1:
        raise GraphError("min_recurrence must be at least 1")
    patterns = load_pattern_registry(board_dir)
    counts: Counter[str] = Counter()
    for entry in _load_all_entries(board_dir):
        if str(entry.get("status") or "open") != "resolved":
            continue
        resolved, _ = resolve_entry_patterns(entry, patterns)
        counts.update(item["id"] for item in resolved)
    applied: list[dict[str, Any]] = []
    promoted: list[dict[str, Any]] = []
    updated: list[dict[str, Any]] = []
    pending: list[str] = []
    failed: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for pattern_id in sorted(counts):
        tag = (
            pattern_id.split(":", 1)[1]
            if pattern_id.startswith("legacy:")
            else patterns["by_id"][pattern_id]["label"]
        )
        if counts[pattern_id] < min_recurrence:
            skipped.append(
                {
                    "pattern_id": pattern_id,
                    "tag": tag,
                    "reason": (
                        f"recurrence_below_threshold ({counts[pattern_id]} < {min_recurrence})"
                    ),
                }
            )
            continue
        try:
            preview = plan_learning_feedback(board_dir, project, pattern_id)
            if not preview.get("plan_token"):
                skipped.append(
                    {
                        "pattern_id": pattern_id,
                        "tag": tag,
                        "learning_id": preview.get("learning_id"),
                        "reason": preview.get("disposition", "no_change"),
                    }
                )
                continue
            receipt = apply_learning_plan(board_dir, project, str(preview["plan_token"]))
            applied.append(receipt)
            compatibility = {
                "id": receipt["id"],
                "tag": tag,
                "recurrence": preview["new"]["recurrence"],
                "derived_from": preview["cited_sources"],
            }
            if receipt["action"] == "create":
                promoted.append(compatibility)
            else:
                compatibility["recurrence_was"] = preview["old"]["recurrence"]
                compatibility["recurrence_now"] = preview["new"]["recurrence"]
                updated.append(compatibility)
        except GraphError as exc:
            failed.append({"pattern_id": pattern_id, "detail": str(exc)})
            pending.extend(item for item in sorted(counts) if item > pattern_id)
            break
    return {
        "project": project,
        "min_recurrence": min_recurrence,
        "applied": applied,
        "promoted": promoted,
        "updated": updated,
        "pending": pending,
        "failed": failed,
        "skipped": skipped,
        "partial": bool(applied and (pending or failed)),
    }


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
    return repository_root / ".engineering-board" / "cache" / "graph" / safe_project / "state.json"


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
        cache_path.resolve() if cache_path is not None else cache_path_for_board(board_dir, project)
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
        raise GraphError("source_changed: canonical Markdown changed during graph build")
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
            cache_path=(Path(args.cache_path) if args.cache_path else None),
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
