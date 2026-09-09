#!/usr/bin/env python3
"""Descriptive post-run summary; does not introduce a pass threshold."""
import argparse
import hashlib
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    campaign = args.campaign.resolve()
    # Trace packet creation requires recorded judgments for all opaque arms.
    trace_review = campaign / "trace-packet/committed-patch-review.json"
    if not trace_review.is_file():
        raise RuntimeError("Patch-first review must be recorded before summary/unblinding")
    plan = read(campaign / "plan.json")
    rows = []
    for arm in plan["arms"]:
        result = campaign / "results" / arm["id"]
        receipt = read(result / "end.json")
        grade = read(result / "grader.stdout")
        # Started/completed events repeat the same id. Count distinct tool ids,
        # not the runner's raw tool-event count; keep the latest observed event.
        tool_items = {}
        for line in (result / "stdout.jsonl").read_text().splitlines():
            event = json.loads(line)
            item = event.get("item", {})
            if item.get("type") in ("command_execution", "mcp_tool_call", "web_search", "collab_tool_call"):
                if not item.get("id"):
                    raise RuntimeError("Tool event without identity; cannot deduplicate")
                tool_items[item["id"]] = item
        mcp = [{key: item.get(key) for key in ("id", "server", "tool", "arguments", "status", "error")}
               for item in tool_items.values() if item["type"] == "mcp_tool_call"]
        rows.append({
            "arm_id": arm["id"], "case_id": arm["case_id"], "condition": arm["condition"],
            "wall_seconds": receipt["wall_seconds"], "usage": receipt["trace"].get("usage"),
            "client_failure": receipt["failure"], "trace_violations": receipt["trace"].get("trace_violations"),
            "hidden_checks": {"passed": grade["passed"], "total": grade["total"],
                              "failed": [name for name, check in grade["checks"].items() if not check["passed"]]},
            "distinct_tool_calls": len(tool_items), "mcp_calls": mcp,
            "end_receipt_sha256": hashlib.sha256((result / "end.json").read_bytes()).hexdigest(),
            "grader_output_sha256": hashlib.sha256((result / "grader.stdout").read_bytes()).hexdigest()
        })
    summary = {
        "provenance": "Four authored synthetic cases, one run per case-condition; descriptive only",
        "source_commit": plan["source_commit"],
        "prepared_manifest_sha256": hashlib.sha256((campaign / "prepared-manifest.json").read_bytes()).hexdigest(),
        "patch_review_sha256": hashlib.sha256(trace_review.read_bytes()).hexdigest(),
        "run": read(campaign / "RUN-END.json"),
        "rows": sorted(rows, key=lambda row: (row["case_id"], row["condition"])),
        "limits": "No causal or population efficacy estimate. End-to-end wall time includes host/tool startup; cost and preparation/review effort are not measured. Memory action attribution requires separate trace review."
    }
    with args.output.open("x") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"arms": len(rows), "output": str(args.output)}))


if __name__ == "__main__":
    main()
