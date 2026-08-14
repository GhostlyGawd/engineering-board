#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"

python3 - "$ROOT" <<'PY'
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "mcp-server"))

from engineering_board_core import (
    _decode_context_token,
    GraphError,
    apply_hypothesis_plan,
    apply_learning_plan,
    apply_outcome_plan,
    apply_pattern_operation,
    build_context,
    build_graph_cached,
    build_insights,
    build_value_report,
    load_hypothesis_registry,
    plan_hypothesis_operation,
    plan_outcome,
    plan_pattern_operation,
)
from engineering_board_mcp import (
    tool_board_context,
    tool_board_create_entry,
    tool_board_init,
    tool_board_outcomes,
    tool_board_update_entry,
)

checks = 0
with tempfile.TemporaryDirectory(prefix="eb-milestone-d-") as tmp:
    repo = Path(tmp)
    (repo / ".git").mkdir()
    project = "atlas"
    tool_board_init({"root": str(repo), "project": project})
    board = repo / "engineering-board" / project

    pattern_preview = plan_pattern_operation(
        board, "create", {"label": "Boundary Ownership"}
    )
    apply_pattern_operation(
        board,
        project,
        "create",
        {"label": "Boundary Ownership"},
        pattern_preview["plan_id"],
    )
    for title, affects in (
        ("API loses tenant boundary", "api/router.py"),
        ("UI loses tenant boundary", "ui/state.ts"),
    ):
        tool_board_create_entry(
            {
                "root": str(repo),
                "project": project,
                "type": "bug",
                "title": title,
                "priority": "P1",
                "affects": affects,
                "pattern": ["boundary-ownership"],
                "discovered": "2026-07-28",
                "done_when": ["The shared boundary is owned and verified."],
            }
        )

    cluster = build_insights(board, project)["ranked_clusters"][0]
    proposal = plan_hypothesis_operation(
        board,
        project,
        "propose",
        {
            "cluster_fingerprint": cluster["cluster_fingerprint"],
            "claim_key": "shared-boundary-has-no-owner",
            "title": "The shared boundary has no owner",
            "root_cause": "The API and UI rely on an implicit ownership boundary.",
            "supporting_evidence": [
                {"id": item, "reason": "The entry crosses the same boundary."}
                for item in cluster["members"]
            ],
            "alternatives": ["Two independent defects have similar symptoms."],
            "counter_evidence": [],
            "confidence": "medium",
            "confidence_basis": "Two domains share one canonical pattern.",
            "falsifier": "Each domain has an independent owner and failure mode.",
            "actor": "milestone-d-matrix",
        },
    )
    apply_hypothesis_plan(board, project, proposal["plan_token"])

    before_digest = hashlib.sha256(
        b"".join(path.read_bytes() for path in sorted(board.rglob("*.md")))
    ).hexdigest()
    first = build_context(
        board,
        project,
        task="Fix the boundary-ownership failures at the shared root.",
        files=["api/router.py"],
        entry_ids=["B001"],
        cwd=str(repo),
        limit=10,
    )
    second = build_context(
        board,
        project,
        task="Fix the boundary-ownership failures at the shared root.",
        files=["api/router.py"],
        entry_ids=["B001"],
        cwd=str(repo),
        limit=10,
    )
    after_digest = hashlib.sha256(
        b"".join(path.read_bytes() for path in sorted(board.rglob("*.md")))
    ).hexdigest()
    assert first == second
    relative_root = build_context(
        board,
        project,
        task="Fix the boundary-ownership failures at the shared root.",
        files=["api/router.py"],
        entry_ids=["B001"],
        cwd=".",
        limit=10,
    )
    assert relative_root == first
    assert before_digest == after_digest
    assert first["context_fingerprint"].startswith("ctx-")
    assert first["ranking_rule_version"] == "1"
    assert first["context_contract_version"] == "2"
    token_payload = _decode_context_token(first["context_token"])
    assert token_payload["context_contract_version"] == "2"
    hypothesis_memory = next(
        item for item in first["results"] if item["id"] == "H001"
    )
    assert hypothesis_memory["kind"] == "hypothesis"
    assert hypothesis_memory["status"] == "proposed"
    assert hypothesis_memory["title"] == "The shared boundary has no owner"
    assert hypothesis_memory["summary_kind"] == "proposed_root_cause"
    assert hypothesis_memory["summary"] == (
        "The API and UI rely on an implicit ownership boundary."
    )
    cluster_memory = next(
        item for item in first["results"] if item["kind"] == "cluster"
    )
    assert cluster_memory["title"] == "boundary-ownership"
    assert cluster_memory["summary_kind"] == "cluster_scope"
    assert "Pattern IDs: P001" in cluster_memory["summary"]
    assert "Normalized patterns: boundary-ownership" in cluster_memory["summary"]
    assert "Members: B001, B002" in cluster_memory["summary"]
    assert "Affected domains: api, ui" in cluster_memory["summary"]
    assert any(item["id"] == "H001" for item in first["results"])
    assert all(
        item["components"]["canonical_pattern"]
        + item["components"]["affected_path"]
        + item["components"]["graph_proximity"]
        > 0
        for item in first["results"]
    )
    checks += 1
    checks += 1

    lexical_decoy = build_context(
        board,
        project,
        task="Discuss an implicit owner without a canonical pattern or path.",
        limit=10,
    )
    assert lexical_decoy["results"] == []
    assert lexical_decoy["warnings"] == [
        "No memory was eligible from task text alone. Add files, entry_ids, "
        "or cwd to provide a structural signal."
    ]
    explicit_pattern = build_context(
        board,
        project,
        task="Investigate P001 before selecting a fix.",
        limit=10,
    )
    assert explicit_pattern["results"]
    assert explicit_pattern["warnings"] == []
    checks += 1

    mcp_context = tool_board_context(
        {
            "root": str(repo),
            "project": project,
            "task": "Fix the boundary-ownership failures at the shared root.",
            "files": ["api/router.py"],
            "entry_ids": ["B001"],
            "cwd": str(repo),
            "limit": 10,
        }
    )
    assert mcp_context == first
    mcp_relative_context = tool_board_context(
        {
            "root": str(repo),
            "project": project,
            "task": "Fix the boundary-ownership failures at the shared root.",
            "files": ["api/router.py"],
            "entry_ids": ["B001"],
            "cwd": ".",
            "limit": 10,
        }
    )
    assert mcp_relative_context == first
    cli = subprocess.run(
        [
            sys.executable,
            str(root / "hooks" / "scripts" / "board-context.py"),
            "--board-dir",
            str(board),
            "--project",
            project,
            "--task",
            "Fix the boundary-ownership failures at the shared root.",
            "--file",
            "api/router.py",
            "--entry",
            "B001",
            "--cwd",
            str(repo),
            "--limit",
            "10",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    assert json.loads(cli.stdout) == first
    checks += 1

    for invalid in (
        {"task": "", "files": [], "entry_ids": [], "cwd": ""},
        {"task": "x", "files": ["."], "entry_ids": [], "cwd": ""},
        {"task": "x", "files": ["/tmp/escape"], "entry_ids": [], "cwd": ""},
        {"task": "x", "files": ["../escape"], "entry_ids": [], "cwd": ""},
        {"task": "x", "files": [], "entry_ids": [], "cwd": str(repo.parent)},
        {"task": "x" * 4001, "files": [], "entry_ids": [], "cwd": ""},
    ):
        try:
            build_context(board, project, **invalid)
            raise AssertionError("invalid context was accepted")
        except GraphError:
            pass
    checks += 1

    tool_board_update_entry(
        {
            "root": str(repo),
            "project": project,
            "entry_id": "B001",
            "status": "resolved",
        }
    )
    outcome_payload = {
        "entry_id": "B001",
        "hypothesis_id": "H001",
        "fix_result": "held",
        "hypothesis_disposition": "confirmed",
        "fix_summary": "The shared owner held through the verification window.",
        "evidence_ids": ["B001"],
        "observed_until": "2026-07-28",
        "actor": "milestone-d-matrix",
        "context_token": first["context_token"],
        "context_used": True,
    }
    before_hypothesis = next((board / "hypotheses").glob("H*.md")).read_bytes()
    preview = plan_outcome(board, project, outcome_payload)
    assert preview["writes_canonical"] is False
    assert next((board / "hypotheses").glob("H*.md")).read_bytes() == before_hypothesis
    assert preview["learning_feedback"][0]["outcome_status"] == "supported"
    checks += 1

    for malformed in (
        dict(outcome_payload, hypothesis_disposition="rejected"),
        dict(outcome_payload, evidence_ids=[]),
        dict(outcome_payload, context_token=""),
    ):
        try:
            plan_outcome(board, project, malformed)
            raise AssertionError("invalid outcome was accepted")
        except GraphError:
            pass
    checks += 1

    applied = tool_board_outcomes(
        {
            "root": str(repo),
            "project": project,
            "action": "apply",
            "apply": preview["plan_token"],
        }
    )
    assert applied["applied"] is True
    assert applied["id"] == "H001"
    assert len(applied["learning_feedback"]) == 1
    hypothesis = load_hypothesis_registry(board)["by_id"]["H001"]
    assert hypothesis["status"] == "confirmed"
    assert "outcome-json" in hypothesis["sections"]["Outcome history"]
    checks += 1

    replay = apply_outcome_plan(board, project, preview["plan_token"])
    assert replay["disposition"] == "already_applied"
    learning_preview = applied["learning_feedback"][0]
    learning_receipt = apply_learning_plan(
        board, project, learning_preview["plan_token"]
    )
    assert learning_receipt["applied"] is True
    learning_text = (board / learning_receipt["changed"]).read_text()
    assert "outcome_status: supported" in learning_text
    assert "confidence: medium" in learning_text
    assert "outcome_refs: [H001]" in learning_text
    learning_context = build_context(
        board,
        project,
        task="boundary-ownership",
        entry_ids=["B002"],
        limit=10,
    )
    learning_memory = next(
        item for item in learning_context["results"] if item["kind"] == "learning"
    )
    assert learning_memory["title"] == "Recurring pattern: boundary-ownership"
    assert learning_memory["summary_kind"] == "learning_takeaway"
    assert "Review the cited resolutions before another local fix." in (
        learning_memory["summary"]
    )
    checks += 1
    checks += 1

    report = build_value_report(board, project)
    assert report["hypotheses_with_structured_outcomes"] == 1
    assert report["confirmed_systemic_fixes"] == 1
    assert report["useful_resurfacing_events"] == 1
    assert report["learning_outcomes"]["supported"] == 1
    assert "prompts" not in report and "sessions" not in report
    assert tool_board_context(
        {"root": str(repo), "project": project, "report": True}
    ) == report
    checks += 1

    current = build_context(
        board,
        project,
        task="boundary-ownership",
        entry_ids=["B002"],
        limit=10,
    )
    failed_preview = plan_outcome(
        board,
        project,
        {
            "entry_id": "B002",
            "hypothesis_id": "H001",
            "fix_result": "failed",
            "hypothesis_disposition": "weakened",
            "fix_summary": "The UI symptom returned during verification.",
            "evidence_ids": ["B002"],
            "observed_until": "2026-07-28",
            "actor": "milestone-d-matrix",
            "context_token": current["context_token"],
            "context_used": False,
        },
    )
    failed_receipt = apply_outcome_plan(
        board, project, failed_preview["plan_token"]
    )
    contested = failed_receipt["learning_feedback"][0]
    assert contested["new"]["outcome_status"] == "contested"
    apply_learning_plan(board, project, contested["plan_token"])
    assert "outcome_status: contested" in next(
        (board / "learnings").glob("L*.md")
    ).read_text()
    checks += 1

    before_rebuild = build_context(
        board,
        project,
        task="boundary-ownership",
        entry_ids=["B002"],
        limit=10,
    )
    graph, cache_path = build_graph_cached(
        board, project, "2026-07-28T00:00:00Z"
    )
    (board / "GRAPH.yml").write_text(json.dumps(graph), encoding="utf-8")
    h_digest = hashlib.sha256(
        next((board / "hypotheses").glob("H*.md")).read_bytes()
    ).hexdigest()
    l_digest = hashlib.sha256(
        next((board / "learnings").glob("L*.md")).read_bytes()
    ).hexdigest()
    (board / "GRAPH.yml").unlink()
    cache_path.unlink()
    after_rebuild = build_context(
        board,
        project,
        task="boundary-ownership",
        entry_ids=["B002"],
        limit=10,
    )
    assert before_rebuild == after_rebuild
    assert hashlib.sha256(
        next((board / "hypotheses").glob("H*.md")).read_bytes()
    ).hexdigest() == h_digest
    assert hashlib.sha256(
        next((board / "learnings").glob("L*.md")).read_bytes()
    ).hexdigest() == l_digest
    checks += 1

    learning_path = next((board / "learnings").glob("L*.md"))
    learning_source = learning_path.read_text(encoding="utf-8")
    learning_source = learning_source.replace(
        "title: Recurring pattern: boundary-ownership",
        "title: " + ("T" * 200),
        1,
    )
    takeaway_start = learning_source.index("## Takeaway\n\n") + len(
        "## Takeaway\n\n"
    )
    takeaway_end = learning_source.index("\n\n## Sources", takeaway_start)
    learning_source = (
        learning_source[:takeaway_start]
        + "first line\n"
        + ("x" * 2100)
        + learning_source[takeaway_end:]
    )
    learning_path.write_text(learning_source, encoding="utf-8")
    bounded_context = build_context(
        board,
        project,
        task="boundary-ownership",
        entry_ids=["B002"],
        limit=10,
    )
    bounded_learning = next(
        item for item in bounded_context["results"] if item["kind"] == "learning"
    )
    assert bounded_learning["title"] == "T" * 160
    assert len(bounded_learning["summary"]) == 2000
    assert "\n" not in bounded_learning["summary"]
    assert bounded_learning["summary"].startswith("first line ")
    checks += 1

    hypothesis_path = next((board / "hypotheses").glob("H*.md"))
    hypothesis_source = hypothesis_path.read_text(encoding="utf-8")
    assert "status: weakened\n" in hypothesis_source
    hypothesis_path.write_text(
        hypothesis_source.replace(
            "status: weakened\n", "status: rejected\n", 1
        ),
        encoding="utf-8",
    )
    rejected_context = build_context(
        board, project, task="boundary-ownership", entry_ids=["B002"], limit=10
    )
    negative_memory = next(
        item for item in rejected_context["results"] if item["id"] == "H001"
    )
    assert negative_memory["kind"] == "negative_memory"
    assert negative_memory["status"] == "rejected"
    assert negative_memory["summary_kind"] == "proposed_root_cause"
    assert "implicit ownership boundary" in negative_memory["summary"]
    checks += 1

print(f"Milestone D context and outcome intelligence matrix: {checks} checks passed")
PY
