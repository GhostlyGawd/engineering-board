#!/usr/bin/env python3
"""Contained lifecycle for the Engineering Board pattern-intelligence demo."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


RUN_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,79}$")
HYPOTHESIS_FILE = "hypotheses/H001-lifecycle-semantics-are-duplicated-across-adapters.md"


class DemoError(Exception):
    """A typed demo lifecycle failure."""

    def __init__(self, code: str, detail: str, exit_code: int = 2):
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.exit_code = exit_code


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    os.replace(temporary, path)


def _atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(value, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def _is_link(path: Path) -> bool:
    if path.is_symlink():
        return True
    isjunction = getattr(os.path, "isjunction", None)
    return bool(isjunction and isjunction(path))


def _assert_contained(base: Path, target: Path) -> None:
    base_real = base.resolve()
    target_real = target.resolve(strict=False)
    try:
        target_real.relative_to(base_real)
    except ValueError as exc:
        raise DemoError(
            "path_escape",
            f"{target} resolves outside {base}",
            3,
        ) from exc


def _assert_no_links(base: Path, target: Path) -> None:
    _assert_contained(base, target)
    current = base.resolve()
    relative = target.resolve(strict=False).relative_to(current)
    for part in relative.parts:
        current = current / part
        if current.exists() and _is_link(current):
            raise DemoError(
                "linked_path_refused",
                f"linked or reparse-point path refused: {current}",
                3,
            )


def _flatten(value: Any, limit: int = 600) -> str:
    text = " ".join(str(value or "").replace("\x00", "").split())
    if not text:
        raise DemoError("invalid_hypothesis", "required text is empty")
    if len(text) > limit:
        raise DemoError(
            "invalid_hypothesis",
            f"required text exceeds {limit} characters",
        )
    return text


def _slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return result[:72] or "hypothesis"


class DemoStore:
    def __init__(self, project_dir: Path, plugin_root: Path):
        self.project_dir = project_dir.resolve()
        self.plugin_root = plugin_root.resolve()
        self.base = (
            self.project_dir
            / ".engineering-board"
            / "demo"
            / "pattern-intelligence"
        )
        _assert_contained(self.project_dir, self.base)
        _assert_no_links(self.project_dir, self.base)

    def run_dir(self, run_id: str) -> Path:
        if not RUN_ID.fullmatch(run_id):
            raise DemoError("invalid_run_id", f"unsafe run id: {run_id!r}")
        target = self.base / run_id
        _assert_no_links(self.project_dir, target)
        return target

    @staticmethod
    def manifest_path(run_dir: Path) -> Path:
        return run_dir / "manifest.json"

    def load_manifest(self, run_dir: Path) -> dict[str, Any]:
        path = self.manifest_path(run_dir)
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise DemoError(
                "manifest_unreadable",
                f"unable to read {path}: {exc}",
                3,
            ) from exc
        if not isinstance(value, dict) or value.get("run_id") != run_dir.name:
            raise DemoError("manifest_invalid", f"invalid manifest at {path}", 3)
        return value

    def write_manifest(self, run_dir: Path, manifest: dict[str, Any]) -> None:
        _atomic_json(self.manifest_path(run_dir), manifest)

    def track(self, run_dir: Path, manifest: dict[str, Any], relative: str) -> None:
        path = run_dir / relative
        _assert_contained(run_dir, path)
        if not path.is_file() or _is_link(path):
            raise DemoError("artifact_missing", f"expected regular file: {relative}")
        manifest.setdefault("files", {})[relative] = _sha256(path)

    def verify(self, run_dir: Path, manifest: dict[str, Any]) -> list[str]:
        _assert_no_links(self.project_dir, run_dir)
        mismatches: list[str] = []
        expected = set(manifest.get("files", {}))
        actual: set[str] = set()
        for root, directories, files in os.walk(run_dir, topdown=True, followlinks=False):
            root_path = Path(root)
            for directory in list(directories):
                path = root_path / directory
                if _is_link(path):
                    mismatches.append(
                        f"linked path: {path.relative_to(run_dir).as_posix()}"
                    )
                    directories.remove(directory)
            for filename in files:
                path = root_path / filename
                relative = path.relative_to(run_dir).as_posix()
                if relative == "manifest.json":
                    continue
                actual.add(relative)
                if _is_link(path):
                    mismatches.append(f"linked file: {relative}")
                    continue
                expected_hash = manifest.get("files", {}).get(relative)
                if expected_hash and _sha256(path) != expected_hash:
                    mismatches.append(f"modified: {relative}")
        for relative in sorted(expected - actual):
            mismatches.append(f"missing: {relative}")
        for relative in sorted(actual - expected):
            mismatches.append(f"unexpected: {relative}")
        return sorted(set(mismatches))


def _new_run_id(requested: str | None = None) -> str:
    if requested:
        if not RUN_ID.fullmatch(requested):
            raise DemoError("invalid_run_id", f"unsafe run id: {requested!r}")
        return requested
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{secrets.token_hex(4)}"


def _copy_fixtures(source: Path, run_dir: Path) -> list[str]:
    if not source.is_dir():
        raise DemoError("fixture_missing", f"demo fixtures missing: {source}")
    copied: list[str] = []
    for path in sorted(source.rglob("*")):
        if path.is_dir():
            continue
        if _is_link(path):
            raise DemoError("fixture_link_refused", f"linked fixture refused: {path}")
        relative = path.relative_to(source)
        destination = run_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        copied.append(relative.as_posix())
    return copied


def create_demo(
    store: DemoStore,
    requested_run_id: str | None,
) -> dict[str, Any]:
    run_id = _new_run_id(requested_run_id)
    run_dir = store.run_dir(run_id)
    if run_dir.exists():
        try:
            existing = store.load_manifest(run_dir)
            mismatches = store.verify(run_dir, existing)
        except DemoError:
            mismatches = ["manifest unavailable"]
        if not mismatches and existing.get("status") in {
            "awaiting_hypothesis",
            "hypothesis_ready",
            "complete",
        }:
            return {
                "status": existing["status"],
                "run_id": run_id,
                "run_dir": str(run_dir),
                "reused": True,
                "graph": str(run_dir / "GRAPH.yml"),
                "hypothesis_request": str(run_dir / "hypothesis-request.json"),
            }
        run_id = f"{run_id}-{secrets.token_hex(3)}"
        run_dir = store.run_dir(run_id)

    run_dir.mkdir(parents=True, exist_ok=False)
    fixture_root = (
        store.plugin_root / "references" / "demo" / "pattern-intelligence"
    )
    copied = _copy_fixtures(fixture_root, run_dir)
    manifest: dict[str, Any] = {
        "schema_version": "1",
        "run_id": run_id,
        "demo": "pattern-intelligence",
        "synthetic": True,
        "created_at": _utc_now(),
        "status": "fixtures_ready",
        "files": {},
    }
    for relative in copied:
        store.track(run_dir, manifest, relative)
    store.write_manifest(run_dir, manifest)

    graph_script = store.plugin_root / "hooks" / "scripts" / "board-graph-build.py"
    process = subprocess.run(
        [
            sys.executable,
            str(graph_script),
            "--board-dir",
            str(run_dir),
            "--project",
            "pattern-intelligence-demo",
            "--output",
            str(run_dir / "GRAPH.yml"),
            "--json-output",
            str(run_dir / "graph.json"),
            "--generated-at",
            manifest["created_at"],
        ],
        cwd=str(store.project_dir),
        capture_output=True,
        text=True,
        check=False,
        timeout=20,
    )
    if process.returncode != 0:
        manifest["status"] = "graph_failed"
        manifest["failure"] = process.stderr.strip()[-1000:]
        for relative in ("GRAPH.yml", "graph.json"):
            if (run_dir / relative).is_file():
                store.track(run_dir, manifest, relative)
        store.write_manifest(run_dir, manifest)
        raise DemoError(
            "graph_failed",
            manifest["failure"] or f"graph builder exit {process.returncode}",
        )
    store.track(run_dir, manifest, "GRAPH.yml")
    store.track(run_dir, manifest, "graph.json")

    graph = json.loads((run_dir / "graph.json").read_text(encoding="utf-8"))
    clusters = graph.get("topology", {}).get("clusters", [])
    if len(clusters) != 1:
        manifest["status"] = "graph_failed"
        manifest["failure"] = f"expected one candidate cluster, got {len(clusters)}"
        store.write_manifest(run_dir, manifest)
        raise DemoError("graph_failed", manifest["failure"])
    request = {
        "schema_version": "1",
        "run_id": run_id,
        "synthetic": True,
        "cluster": clusters[0],
        "required_status": "proposed",
        "required_evidence_ids": clusters[0]["members"],
        "required_fields": [
            "title",
            "root_cause",
            "supporting_evidence",
            "alternatives",
            "falsifier",
        ],
    }
    _atomic_json(run_dir / "hypothesis-request.json", request)
    store.track(run_dir, manifest, "hypothesis-request.json")
    manifest["status"] = "awaiting_hypothesis"
    store.write_manifest(run_dir, manifest)
    return {
        "status": "awaiting_hypothesis",
        "run_id": run_id,
        "run_dir": str(run_dir),
        "reused": False,
        "graph": str(run_dir / "GRAPH.yml"),
        "hypothesis_request": str(run_dir / "hypothesis-request.json"),
    }


def _validated_hypothesis(
    payload: Any,
    request: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise DemoError("invalid_hypothesis", "hypothesis payload must be an object")
    title = _flatten(payload.get("title"), 160)
    root_cause = _flatten(payload.get("root_cause"))
    falsifier = _flatten(payload.get("falsifier"))
    alternatives_raw = payload.get("alternatives")
    if not isinstance(alternatives_raw, list) or not alternatives_raw:
        raise DemoError(
            "invalid_hypothesis",
            "alternatives must contain at least one explanation",
        )
    alternatives = [_flatten(value, 400) for value in alternatives_raw[:5]]
    evidence_raw = payload.get("supporting_evidence")
    if not isinstance(evidence_raw, list):
        raise DemoError(
            "invalid_hypothesis",
            "supporting_evidence must be a list",
        )
    evidence: list[dict[str, str]] = []
    for item in evidence_raw:
        if not isinstance(item, dict):
            raise DemoError(
                "invalid_hypothesis",
                "each supporting evidence item must be an object",
            )
        evidence.append(
            {
                "id": _flatten(item.get("id"), 20),
                "reason": _flatten(item.get("reason"), 400),
            }
        )
    required = sorted(request["required_evidence_ids"])
    supplied = sorted({item["id"] for item in evidence})
    if supplied != required:
        raise DemoError(
            "invalid_hypothesis",
            f"supporting evidence must cite exactly: {', '.join(required)}",
        )
    return {
        "title": title,
        "root_cause": root_cause,
        "supporting_evidence": sorted(evidence, key=lambda item: item["id"]),
        "alternatives": alternatives,
        "falsifier": falsifier,
    }


def write_hypothesis(
    store: DemoStore,
    run_id: str,
    payload: Any,
) -> dict[str, Any]:
    run_dir = store.run_dir(run_id)
    manifest = store.load_manifest(run_dir)
    mismatches = store.verify(run_dir, manifest)
    if mismatches:
        raise DemoError(
            "run_changed",
            "demo run changed; preserve and restart: " + "; ".join(mismatches),
            3,
        )
    if manifest.get("status") not in {"awaiting_hypothesis", "hypothesis_ready"}:
        raise DemoError(
            "invalid_state",
            f"cannot write hypothesis while status is {manifest.get('status')!r}",
        )
    request = json.loads(
        (run_dir / "hypothesis-request.json").read_text(encoding="utf-8")
    )
    hypothesis = _validated_hypothesis(payload, request)
    cluster = request["cluster"]
    created = manifest["created_at"][:10]
    title_yaml = json.dumps(hypothesis["title"], ensure_ascii=False)
    lines = [
        "---",
        "id: H001",
        "type: hypothesis",
        "status: proposed",
        f"title: {title_yaml}",
        f"cluster_id: {cluster['id']}",
        f"patterns: [{', '.join(cluster['patterns'])}]",
        "confidence: medium",
        f"derived_from: [{', '.join(request['required_evidence_ids'])}]",
        f"affected_domains: [{', '.join(cluster['affected_domains'])}]",
        f"created: {created}",
        f"last_evaluated: {created}",
        "---",
        "",
        "## Proposed root cause",
        "",
        hypothesis["root_cause"],
        "",
        "## Supporting evidence",
        "",
    ]
    lines.extend(
        f"- {item['id']}: {item['reason']}"
        for item in hypothesis["supporting_evidence"]
    )
    lines.extend(["", "## Alternative explanations", ""])
    lines.extend(f"- {value}" for value in hypothesis["alternatives"])
    lines.extend(
        [
            "",
            "## Falsifier",
            "",
            hypothesis["falsifier"],
            "",
            "## Outcome history",
            "",
            (
                f"- {created}: Proposed from synthetic cluster {cluster['id']}; "
                "not confirmed."
            ),
            "",
        ]
    )
    hypothesis_path = run_dir / HYPOTHESIS_FILE
    _atomic_text(hypothesis_path, "\n".join(lines))
    store.track(run_dir, manifest, HYPOTHESIS_FILE)
    manifest["status"] = "hypothesis_ready"
    store.write_manifest(run_dir, manifest)
    return {
        "status": "hypothesis_ready",
        "run_id": run_id,
        "run_dir": str(run_dir),
        "hypothesis": str(hypothesis_path),
    }


def finalize_demo(
    store: DemoStore,
    run_id: str,
    visual_path: Path,
) -> dict[str, Any]:
    run_dir = store.run_dir(run_id)
    manifest = store.load_manifest(run_dir)
    if manifest.get("status") not in {"hypothesis_ready", "complete"}:
        raise DemoError(
            "invalid_state",
            f"cannot finalize while status is {manifest.get('status')!r}",
        )
    visual_path = visual_path.resolve()
    _assert_contained(run_dir, visual_path)
    relative = visual_path.relative_to(run_dir).as_posix()
    store.track(run_dir, manifest, relative)
    manifest["status"] = "complete"
    store.write_manifest(run_dir, manifest)
    return {
        "status": "complete",
        "run_id": run_id,
        "run_dir": str(run_dir),
        "graph": str(run_dir / "GRAPH.yml"),
        "hypothesis": str(run_dir / HYPOTHESIS_FILE),
        "visual": str(visual_path),
        "cleanup": f"/board-demo --clean {run_id}",
    }


def clean_demo(store: DemoStore, run_id: str) -> dict[str, Any]:
    run_dir = store.run_dir(run_id)
    manifest = store.load_manifest(run_dir)
    mismatches = store.verify(run_dir, manifest)
    if mismatches:
        raise DemoError(
            "cleanup_refused",
            "fingerprint mismatch: " + "; ".join(mismatches),
            3,
        )
    files = sorted(manifest.get("files", {}), key=lambda value: value.count("/"), reverse=True)
    removed: list[str] = []
    for relative in files:
        path = run_dir / relative
        _assert_contained(run_dir, path)
        path.unlink()
        removed.append(relative)
    store.manifest_path(run_dir).unlink()
    for root, directories, _files in os.walk(run_dir, topdown=False):
        for directory in directories:
            (Path(root) / directory).rmdir()
    run_dir.rmdir()
    return {
        "status": "cleaned",
        "run_id": run_id,
        "removed_files": sorted(removed),
        "recoverable": False,
    }


def status_demo(store: DemoStore, run_id: str) -> dict[str, Any]:
    run_dir = store.run_dir(run_id)
    manifest = store.load_manifest(run_dir)
    mismatches = store.verify(run_dir, manifest)
    return {
        "status": manifest.get("status"),
        "run_id": run_id,
        "run_dir": str(run_dir),
        "mismatches": mismatches,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--plugin-root", required=True)
    subparsers = parser.add_subparsers(dest="command", required=True)
    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("--run-id")
    hypothesis_parser = subparsers.add_parser("hypothesis")
    hypothesis_parser.add_argument("run_id")
    finalize_parser = subparsers.add_parser("finalize")
    finalize_parser.add_argument("run_id")
    finalize_parser.add_argument("visual")
    clean_parser = subparsers.add_parser("clean")
    clean_parser.add_argument("run_id")
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("run_id")
    args = parser.parse_args(argv)

    try:
        store = DemoStore(Path(args.project_dir), Path(args.plugin_root))
        if args.command == "create":
            result = create_demo(store, args.run_id)
        elif args.command == "hypothesis":
            try:
                payload = json.load(sys.stdin)
            except json.JSONDecodeError as exc:
                raise DemoError(
                    "invalid_hypothesis_json",
                    f"hypothesis input is not valid JSON: {exc}",
                ) from exc
            result = write_hypothesis(store, args.run_id, payload)
        elif args.command == "finalize":
            result = finalize_demo(store, args.run_id, Path(args.visual))
        elif args.command == "clean":
            result = clean_demo(store, args.run_id)
        else:
            result = status_demo(store, args.run_id)
    except DemoError as exc:
        print(
            json.dumps(
                {"error": exc.code, "detail": exc.detail},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return exc.exit_code
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
