#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"

python3 - "$ROOT" <<'PY'
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess
import sys
import tempfile

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "mcp-server"))

from engineering_board_core import (
    GraphError,
    apply_hypothesis_plan,
    apply_pattern_operation,
    build_insights,
    list_hypotheses,
    plan_hypothesis_operation,
    plan_pattern_operation,
)
from engineering_board_mcp import (
    tool_board_create_entry,
    tool_board_graph,
    tool_board_hypotheses,
    tool_board_init,
    tool_board_insights,
)

checks = 0
with tempfile.TemporaryDirectory(prefix="eb-milestone-c-") as tmp:
    repo = Path(tmp)
    project = "atlas"
    tool_board_init({"root": str(repo), "project": project})
    board = repo / "engineering-board" / project
    assert (board / "hypotheses" / ".gitkeep").is_file()
    checks += 1

    for label in ("Boundary Ownership", "State Duplication", "Retry Storm"):
        preview = plan_pattern_operation(board, "create", {"label": label})
        apply_pattern_operation(
            board,
            project,
            "create",
            {"label": label},
            preview["plan_id"],
        )

    entries = []
    for title, priority, affects, pattern, discovered in (
        ("API loses tenant boundary", "P1", "api/router.py", "boundary-ownership", "2026-07-27"),
        ("UI loses tenant boundary", "P1", "ui/state.ts", "boundary-ownership", "2026-07-28"),
        ("Worker duplicates state", "P1", "worker/job.py", "state-duplication", "2026-07-27"),
        ("Storage duplicates state", "P1", "storage/model.py", "state-duplication", "2026-07-28"),
        ("Queue retries without a limit", "P3", "queue/worker.py", "retry-storm", "2026-01-01"),
        ("Queue repeats failed delivery", "P3", "queue/delivery.py", "retry-storm", "2026-01-02"),
    ):
        entries.append(
            tool_board_create_entry(
                {
                    "root": str(repo),
                    "project": project,
                    "type": "bug",
                    "title": title,
                    "priority": priority,
                    "affects": affects,
                    "pattern": [pattern],
                    "discovered": discovered,
                    "done_when": ["The shared root cause is removed."],
                }
            )
        )

    direct = build_insights(board, project)
    mcp = tool_board_insights({"root": str(repo), "project": project})
    assert direct == mcp
    assert direct["ranking_rule_version"] == "1"
    assert len(direct["ranked_clusters"]) == 3
    assert direct["ranked_clusters"] == sorted(
        direct["ranked_clusters"],
        key=lambda item: (-item["score"], item["cluster_fingerprint"]),
    )
    assert direct["ranked_clusters"][0]["score"] == direct["ranked_clusters"][1]["score"]
    assert direct["ranked_clusters"][1]["score"] > direct["ranked_clusters"][2]["score"]
    checks += 1

    cli = root / "hooks" / "scripts" / "board-insights.py"
    cli_rank = subprocess.run(
        [
            sys.executable,
            str(cli),
            "--board-dir",
            str(board),
            "--project",
            project,
            "rank",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    assert json.loads(cli_rank.stdout) == direct
    checks += 1

    first = direct["ranked_clusters"][0]
    payload = {
        "cluster_fingerprint": first["cluster_fingerprint"],
        "claim_key": "shared-boundary-is-implicit",
        "title": "Shared boundary ownership is implicit",
        "root_cause": "A shared <script>alert(1)</script> boundary has no owner.",
        "supporting_evidence": [
            {"id": entry_id, "reason": f"{entry_id} crosses the same boundary."}
            for entry_id in first["members"]
        ],
        "alternatives": ["Two independent defects created the same symptom."],
        "counter_evidence": ["No failure appears in the isolated parser."],
        "confidence": "medium",
        "confidence_basis": "Two domains share one canonical pattern.",
        "falsifier": "A controlled test shows independent owners and failure modes.",
        "actor": "milestone-c-matrix",
    }

    before_files = sorted((board / "hypotheses").glob("*.md"))
    proposal = plan_hypothesis_operation(board, project, "propose", payload)
    assert proposal["writes_canonical"] is False and proposal["plan_token"]
    assert sorted((board / "hypotheses").glob("*.md")) == before_files
    checks += 1

    for malformed in (
        dict(payload, alternatives=[]),
        dict(payload, supporting_evidence=payload["supporting_evidence"][:-1]),
        dict(payload, falsifier=""),
        dict(payload, actor=None),
    ):
        try:
            plan_hypothesis_operation(board, project, "propose", malformed)
            raise AssertionError("malformed proposal was accepted")
        except GraphError:
            pass
    assert sorted((board / "hypotheses").glob("*.md")) == before_files
    checks += 1

    tool_board_create_entry(
        {
            "root": str(repo),
            "project": project,
            "type": "observation",
            "title": "Unrelated source change",
            "body": "This changes canonical source state.",
            "discovered": "2026-07-28",
        }
    )
    try:
        apply_hypothesis_plan(board, project, proposal["plan_token"])
        raise AssertionError("stale proposal plan was accepted")
    except GraphError as exc:
        assert "plan_stale" in str(exc)
    assert not list((board / "hypotheses").glob("H*.md"))
    checks += 1

    current = build_insights(
        board, project, cluster_fingerprint=first["cluster_fingerprint"]
    )["ranked_clusters"][0]
    payload["supporting_evidence"] = [
        {"id": entry_id, "reason": f"{entry_id} crosses the same boundary."}
        for entry_id in current["members"]
    ]
    proposal = tool_board_hypotheses(
        {"root": str(repo), "project": project, "action": "propose", **payload}
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(
                apply_hypothesis_plan,
                board,
                project,
                proposal["plan_token"],
            )
            for _ in range(2)
        ]
        outcomes = []
        for future in futures:
            try:
                outcomes.append(future.result())
            except GraphError as exc:
                outcomes.append(str(exc))
    applied_results = [
        result for result in outcomes if isinstance(result, dict)
    ]
    stale_results = [
        result
        for result in outcomes
        if isinstance(result, str) and "plan_stale" in result
    ]
    assert len(applied_results) == 1 and len(stale_results) == 1
    applied = applied_results[0]
    assert applied["applied"] is True and applied["id"] == "H001"
    assert len(list((board / "hypotheses").glob("H*.md"))) == 1
    assert list_hypotheses(board, project)["hypotheses"][0]["status"] == "proposed"
    checks += 1

    for status, reason in (
        ("confirmed", "Confirmation requires cited evaluation evidence."),
        ("rejected", "The controlled test falsified shared ownership."),
    ):
        try:
            plan_hypothesis_operation(
                board,
                project,
                "evaluate",
                {
                    "hypothesis_id": "H001",
                    "status": status,
                    "reason": reason,
                    "evidence_ids": [],
                    "actor": "milestone-c-matrix",
                },
            )
            raise AssertionError("evaluation without evidence was accepted")
        except GraphError:
            pass
        if status == "rejected":
            evaluation = plan_hypothesis_operation(
                board,
                project,
                "evaluate",
                {
                    "hypothesis_id": "H001",
                    "status": status,
                    "reason": reason,
                    "evidence_ids": current["members"],
                    "actor": "milestone-c-matrix",
                },
            )
            apply_hypothesis_plan(board, project, evaluation["plan_token"])
    checks += 1

    blocked = plan_hypothesis_operation(board, project, "propose", payload)
    assert blocked["disposition"] == "blocked_by_negative_memory"
    assert blocked["hypothesis_id"] == "H001"
    assert blocked["rejecting_outcome"] == "rejected"
    assert blocked["plan_token"] is None and blocked["writes_canonical"] is False
    checks += 1

    try:
        plan_hypothesis_operation(
            board,
            project,
            "reopen",
            {
                "hypothesis_id": "H001",
                "cluster_fingerprint": current["cluster_fingerprint"],
                "new_evidence_reason": "Recheck without new evidence.",
                "evidence_ids": current["members"],
                "actor": "milestone-c-matrix",
            },
        )
        raise AssertionError("reopen without new evidence was accepted")
    except GraphError as exc:
        assert "new evidence" in str(exc)

    first_pattern = current["patterns"][0]
    added = tool_board_create_entry(
        {
            "root": str(repo),
            "project": project,
            "type": "bug",
            "title": "CLI crosses the same boundary",
            "priority": "P2",
            "affects": "cli/main.py",
            "pattern": [first_pattern],
            "discovered": "2026-07-28",
            "done_when": ["Boundary ownership is explicit."],
        }
    )
    reopened_cluster = next(
        item
        for item in build_insights(board, project)["ranked_clusters"]
        if added["id"] in item["members"]
    )
    reopen = plan_hypothesis_operation(
        board,
        project,
        "reopen",
        {
            "hypothesis_id": "H001",
            "cluster_fingerprint": reopened_cluster["cluster_fingerprint"],
            "new_evidence_reason": "A third domain supplies new canonical evidence.",
            "evidence_ids": reopened_cluster["members"],
            "actor": "milestone-c-matrix",
        },
    )
    apply_hypothesis_plan(board, project, reopen["plan_token"])
    assert list_hypotheses(board, project)["hypotheses"][0]["status"] == "proposed"
    checks += 1

    split = plan_hypothesis_operation(
        board,
        project,
        "split",
        {
            "hypothesis_id": "H001",
            "claim_keys": ["api-boundary-owner", "ui-boundary-owner"],
            "reason": "Evidence supports two falsifiable ownership claims.",
            "evidence_ids": reopened_cluster["members"],
            "actor": "milestone-c-matrix",
        },
    )
    apply_hypothesis_plan(board, project, split["plan_token"])
    listed = list_hypotheses(board, project)
    assert listed["hypotheses"][0]["status"] == "split"
    assert len(listed["hypotheses"]) == 1
    checks += 1

    second = next(
        item
        for item in build_insights(board, project)["ranked_clusters"]
        if item["cluster_fingerprint"] != reopened_cluster["cluster_fingerprint"]
    )
    proposal_ids = []
    for claim_key in ("duplicate-cache-owner", "duplicate-store-owner"):
        second_payload = dict(payload)
        second_payload.update(
            {
                "cluster_fingerprint": second["cluster_fingerprint"],
                "claim_key": claim_key,
                "title": claim_key.replace("-", " ").title(),
                "root_cause": (
                    "Two mutable <script>alert(1)</script> state owners "
                    "implement one contract."
                ),
                "supporting_evidence": [
                    {"id": entry_id, "reason": "The state contract is duplicated."}
                    for entry_id in second["members"]
                ],
            }
        )
        preview = plan_hypothesis_operation(
            board, project, "propose", second_payload
        )
        result = apply_hypothesis_plan(board, project, preview["plan_token"])
        proposal_ids.append(result["id"])

    confirmation = plan_hypothesis_operation(
        board,
        project,
        "evaluate",
        {
            "hypothesis_id": proposal_ids[0],
            "status": "confirmed",
            "reason": "A controlled fix removed both cited symptoms.",
            "evidence_ids": second["members"],
            "actor": "milestone-c-matrix",
        },
    )
    apply_hypothesis_plan(board, project, confirmation["plan_token"])
    weakening = plan_hypothesis_operation(
        board,
        project,
        "evaluate",
        {
            "hypothesis_id": proposal_ids[0],
            "status": "weakened",
            "reason": "A later controlled run exposed an independent path.",
            "evidence_ids": second["members"],
            "actor": "milestone-c-matrix",
        },
    )
    apply_hypothesis_plan(board, project, weakening["plan_token"])

    try:
        plan_hypothesis_operation(
            board,
            project,
            "merge",
            {
                "hypothesis_id": proposal_ids[1],
                "into": proposal_ids[1],
                "reason": "Self merge must fail.",
                "evidence_ids": second["members"],
                "actor": "milestone-c-matrix",
            },
        )
        raise AssertionError("self merge was accepted")
    except GraphError:
        pass
    merge = plan_hypothesis_operation(
        board,
        project,
        "merge",
        {
            "hypothesis_id": proposal_ids[1],
            "into": proposal_ids[0],
            "reason": "The evidence supports one state-ownership claim.",
            "evidence_ids": second["members"],
            "actor": "milestone-c-matrix",
        },
    )
    apply_hypothesis_plan(board, project, merge["plan_token"])
    statuses = {
        item["id"]: item for item in list_hypotheses(board, project)["hypotheses"]
    }
    assert statuses[proposal_ids[1]]["status"] == "merged"
    assert statuses[proposal_ids[0]]["merged_from"] == [proposal_ids[1]]
    checks += 1

    cached_before = tool_board_graph(
        {"root": str(repo), "project": project}
    )["graph"]
    ranking_before = build_insights(board, project)
    cache_root = repo / ".engineering-board" / "cache"
    for cache_file in cache_root.rglob("state.json"):
        cache_file.unlink()
    ranking_after = build_insights(board, project)
    assert ranking_before == ranking_after
    assert cached_before["schema_version"] == "3"
    checks += 1

    offline = subprocess.run(
        [
            sys.executable,
            str(cli),
            "--board-dir",
            str(board),
            "--project",
            project,
            "rank",
        ],
        check=True,
        text=True,
        capture_output=True,
        env=dict(
            os.environ,
            HTTP_PROXY="http://127.0.0.1:9",
            HTTPS_PROXY="http://127.0.0.1:9",
            NO_PROXY="",
        ),
    )
    assert json.loads(offline.stdout) == ranking_after
    checks += 1

    tool_board_create_entry(
        {
            "root": str(repo),
            "project": project,
            "type": "observation",
            "title": "Post-evaluation source change",
            "body": "This makes existing graph bindings visibly stale.",
            "discovered": "2026-07-28",
        }
    )
    rendered = subprocess.run(
        ["bash", "hooks/scripts/board-view.sh", project, "--stdout"],
        check=True,
        text=True,
        capture_output=True,
        cwd=root,
        env=dict(os.environ, CLAUDE_PROJECT_DIR=repo.as_posix()),
    ).stdout
    assert "Ranked systemic investigations" in rendered
    assert "score is not confidence" in rendered
    assert "H001" in rendered and "split" in rendered
    assert "stale binding" in rendered
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in rendered, [
        rendered[max(0, index - 80):index + 120]
        for index in [rendered.find("alert(1)")]
    ]
    assert "<script>alert(1)</script>" not in rendered
    assert "plan_token" not in rendered and "Apply hypothesis" not in rendered
    checks += 1

print(f"Milestone C root-cause intelligence matrix: {checks} checks passed")
PY
