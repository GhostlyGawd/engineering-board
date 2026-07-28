#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"

python3 - "$ROOT" <<'PY'
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "mcp-server"))

from engineering_board_core import (
    GraphError,
    apply_pattern_operation,
    build_graph_cached,
    load_pattern_registry,
    plan_pattern_operation,
)
import engineering_board_core as core
from engineering_board_mcp import (
    call_tool,
    tool_board_create_entry,
    tool_board_graph,
    tool_board_init,
    tool_board_patterns,
    tool_board_promote_findings,
)

checks = 0

with tempfile.TemporaryDirectory(prefix="eb-milestone-b-") as tmp:
    repo = Path(tmp)
    project = "atlas"
    tool_board_init({"root": str(repo), "project": project})
    board = repo / "engineering-board" / project

    create = plan_pattern_operation(
        board,
        "create",
        {
            "label": "Duplicated State Contract",
            "aliases": ["split-brain-state"],
            "definition": "One contract is implemented by separate mutable stores.",
        },
    )
    assert create["writes_canonical"] is False
    apply_pattern_operation(
        board, project, "create",
        {
            "label": "Duplicated State Contract",
            "aliases": ["split-brain-state"],
            "definition": "One contract is implemented by separate mutable stores.",
        },
        create["plan_id"],
    )
    checks += 1

    cli = root / "hooks" / "scripts" / "board-intake.py"
    preview = subprocess.run(
        [
            sys.executable, str(cli),
            "--board-dir", str(board), "--project", project,
            "pattern", "--action", "alias",
            "--pattern-id", "P001", "--alias", "dual-state-contract",
        ],
        check=True, text=True, capture_output=True,
    )
    alias_plan = json.loads(preview.stdout)
    applied = subprocess.run(
        [
            sys.executable, str(cli),
            "--board-dir", str(board), "--project", project,
            "pattern", "--action", "alias",
            "--pattern-id", "P001", "--alias", "dual-state-contract",
            "--apply", alias_plan["plan_id"],
        ],
        check=True, text=True, capture_output=True,
    )
    assert json.loads(applied.stdout)["applied"] is True
    assert load_pattern_registry(board)["by_token"]["dual-state-contract"] == "P001"
    checks += 1

    bug = tool_board_create_entry(
        {
            "root": str(repo), "project": project, "type": "bug",
            "title": "Renderer and API disagree about state",
            "priority": "P1", "affects": "src/render.py",
            "pattern": ["dual-state-contract"],
            "done_when": ["One state contract drives both surfaces."],
        }
    )
    bug_text = Path(repo / bug["file"]).read_text(encoding="utf-8")
    assert "pattern_ids: [P001]" in bug_text
    checks += 1

    second = tool_board_patterns(
        {
            "root": str(repo), "project": project, "action": "create",
            "label": "Boundary Confusion",
        }
    )
    tool_board_patterns(
        {
            "root": str(repo), "project": project, "action": "create",
            "label": "Boundary Confusion", "apply": second["plan_id"],
        }
    )
    correction = tool_board_patterns(
        {
            "root": str(repo), "project": project, "action": "correct",
            "entry_id": bug["id"], "replace": "P001", "with": "P002",
            "reason": "Repository evidence identifies the boundary failure.",
        }
    )
    tool_board_patterns(
        {
            "root": str(repo), "project": project, "action": "correct",
            "entry_id": bug["id"], "replace": "P001", "with": "P002",
            "reason": "Repository evidence identifies the boundary failure.",
            "apply": correction["plan_id"],
        }
    )
    bug_text = Path(repo / bug["file"]).read_text(encoding="utf-8")
    assert "pattern_ids: [P002]" in bug_text
    assert "## Pattern history" in bug_text and "Repository evidence" in bug_text
    checks += 1

    pattern_path = next((board / "patterns").glob("P002-*.md"))
    original_id_line = "id: P002"
    renamed = pattern_path.read_text(encoding="utf-8").replace(
        "label: boundary-confusion", "label: ownership-boundary-confusion"
    )
    pattern_path.write_text(renamed, encoding="utf-8")
    registry = load_pattern_registry(board)
    assert registry["by_id"]["P002"]["label"] == "ownership-boundary-confusion"
    assert original_id_line in renamed
    checks += 1

    merged = renamed.replace(
        "status: active", "status: merged\nmerged_into: P001"
    )
    pattern_path.write_text(merged, encoding="utf-8")
    registry = load_pattern_registry(board)
    assert registry["by_id"]["P002"]["status"] == "merged"
    checks += 1

    before = sorted(p.relative_to(board).as_posix() for p in board.rglob("*.md"))
    try:
        plan_pattern_operation(
            board, "create", {"label": "dual-state-contract"}
        )
        raise AssertionError("duplicate alias was accepted")
    except GraphError:
        pass
    after = sorted(p.relative_to(board).as_posix() for p in board.rglob("*.md"))
    assert before == after
    checks += 1

    legacy = tool_board_create_entry(
        {
            "root": str(repo), "project": project, "type": "observation",
            "title": "Legacy label remains visible",
            "pattern": ["unreviewed-surface-similarity"],
            "body": "Evidence only.",
        }
    )
    full = tool_board_graph(
        {"root": str(repo), "project": project, "full": True}
    )["graph"]
    assert any(
        item["entry"] == legacy["id"]
        and item["identity"] == "legacy:unreviewed-surface-similarity"
        for item in full["unresolved_patterns"]
    )
    assert full["nodes"][bug["id"]]["pattern_ids"] == ["P001"]
    checks += 1

    incremental = tool_board_graph(
        {"root": str(repo), "project": project}
    )["graph"]
    left = copy.deepcopy(full)
    right = copy.deepcopy(incremental)
    for value in (left, right):
        value.pop("generated_at", None)
        value.pop("build_mode", None)
    assert left == right
    cache_files = list((repo / ".engineering-board" / "cache").rglob("state.json"))
    assert len(cache_files) == 1
    cache_files[0].unlink()
    rebuilt, _ = build_graph_cached(board, project, "2030-01-01T00:00:00Z")
    assert rebuilt["source_fingerprint"] == full["source_fingerprint"]
    checks += 1

    protected_cache = repo / ".engineering-board" / "cache" / "race.json"
    protected_cache.parent.mkdir(parents=True, exist_ok=True)
    protected_cache.write_text("prior-cache\n", encoding="utf-8")
    original_build = core.build_graph
    entry_path = Path(repo / bug["file"])
    def mutating_build(*args, **kwargs):
        graph = original_build(*args, **kwargs)
        entry_path.write_text(
            entry_path.read_text(encoding="utf-8") + "\n<!-- race -->\n",
            encoding="utf-8",
        )
        return graph
    core.build_graph = mutating_build
    try:
        try:
            build_graph_cached(
                board, project, "2030-01-01T00:00:00Z",
                full=True, cache_path=protected_cache,
            )
            raise AssertionError("source change during build was accepted")
        except GraphError as exc:
            assert "source_changed" in str(exc)
        assert protected_cache.read_text(encoding="utf-8") == "prior-cache\n"
    finally:
        core.build_graph = original_build
    checks += 1

    sessions = board / "_sessions"
    sessions.mkdir(exist_ok=True)
    scratch = sessions / "foreground-test.md"
    findings = {
        "findings": [
            {
                "scratch_id": "S-new",
                "type": "feature",
                "title": "Expose a clustered pattern view",
                "affects": "src/patterns.py",
                "pattern": ["dual-state-contract"],
                "evidence_quote": "Clusters connect distant symptoms.",
            },
            {
                "scratch_id": "S-batch-duplicate",
                "type": "feature",
                "title": "Expose a clustered pattern view",
                "affects": "src/patterns.py",
            },
            {
                "scratch_id": "S-existing",
                "type": "bug",
                "title": "Renderer and API disagree about state",
                "affects": "src/render.py",
            },
            {
                "scratch_id": "S-invalid",
                "type": "learning",
                "title": "Unreviewed semantic claim",
            },
        ]
    }
    scratch.write_text(json.dumps(findings) + "\n", encoding="utf-8")
    promotion = tool_board_promote_findings(
        {
            "root": str(repo), "project": project,
            "session": scratch.name,
        }
    )
    assert promotion["summary"] == {
        "create": 1, "deduplicated": 2, "rejected": 1
    }
    applied_promotion = tool_board_promote_findings(
        {
            "root": str(repo), "project": project,
            "session": scratch.name, "apply": promotion["plan_id"],
        }
    )
    assert applied_promotion["summary"] == {
        "created": 1, "deduplicated": 2, "rejected": 1
    }
    assert scratch.is_file(), "rejected finding must preserve its source file"
    checks += 1

    partial = sessions / "partial-write.md"
    partial.write_text(
        json.dumps(
            {
                "findings": [
                    {
                        "scratch_id": "S-io-ok",
                        "type": "observation",
                        "title": "First partial finding",
                    },
                    {
                        "scratch_id": "S-io-fail",
                        "type": "observation",
                        "title": "Second partial finding",
                    },
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    partial_plan = core.plan_promotion(board, project, partial.name)
    original_writer = core._write_promoted_entry
    def injected_writer(board_dir, item, now):
        if item["scratch_id"] == "S-io-fail":
            raise OSError("injected write failure")
        return original_writer(board_dir, item, now)
    core._write_promoted_entry = injected_writer
    try:
        partial_result = core.apply_promotion(
            board, project, partial.name, partial_plan["plan_id"]
        )
    finally:
        core._write_promoted_entry = original_writer
    assert partial_result["summary"] == {"created": 1, "deferred": 1}
    assert partial.is_file()
    retry = core.plan_promotion(board, project, partial.name)
    assert retry["summary"] == {"already_applied": 1, "create": 1}
    checks += 1

    linked = sessions / "linked.md"
    link_supported = True
    try:
        linked.symlink_to(scratch)
    except OSError:
        link_supported = False
    if link_supported:
        linked_result = call_tool(
            "board_promote_findings",
            {
                "root": str(repo), "project": project,
                "session": linked.name,
            },
        )
        assert linked_result["isError"] is True
        assert "linked scratch file" in linked_result["content"][0]["text"]
        checks += 1

    stale = tool_board_patterns(
        {
            "root": str(repo), "project": project, "action": "alias",
            "pattern_id": "P001", "alias": "stale-preview",
        }
    )
    p1 = next((board / "patterns").glob("P001-*.md"))
    p1.write_text(
        p1.read_text(encoding="utf-8") + "\n<!-- changed -->\n",
        encoding="utf-8",
    )
    stale_result = call_tool(
        "board_patterns",
        {
            "root": str(repo), "project": project, "action": "alias",
            "pattern_id": "P001", "alias": "stale-preview",
            "apply": stale["plan_id"],
        },
    )
    assert stale_result["isError"] is True
    assert "plan_stale" in stale_result["content"][0]["text"]
    checks += 1

    tools_result = call_tool(
        "board_graph",
        {"root": str(repo), "project": project, "full": True},
    )
    assert tools_result["isError"] is False
    final_graph = json.loads(tools_result["content"][0]["text"])["graph"]
    p1_cluster = next(
        cluster
        for cluster in final_graph["topology"]["clusters"]
        if "P001" in cluster["pattern_ids"]
    )
    evidence_summary = {
        "canonical_pattern": "P001",
        "cluster_fingerprint": p1_cluster["fingerprint"],
        "members": p1_cluster["members"],
        "source_fingerprint": final_graph["source_fingerprint"][:16],
        "unresolved": len(final_graph["unresolved_patterns"]),
    }
    checks += 1

print("milestone-b-pattern-pipeline: %d checks passed" % checks)
print("evidence: " + json.dumps(evidence_summary, sort_keys=True))
PY
