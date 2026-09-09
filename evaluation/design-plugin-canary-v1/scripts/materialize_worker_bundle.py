#!/usr/bin/env python3
"""Create an isolated public worker bundle for one canary task."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

TASKS = {
    "C1": "c1-visual-generation",
    "C2": "c2-brand-adherence",
    "C3": "c3-ux-audit",
    "C4": "c4-screenshot-to-code",
    "C5": "c5-accessibility-repair",
    "C6": "c6-penpot-roundtrip",
}


def materialize(pack_root: Path, task_id: str, output: Path) -> Path:
    if task_id not in TASKS:
        raise ValueError(f"unknown task {task_id}")
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    source = pack_root / "fixtures" / TASKS[task_id]
    fixture = json.loads((source / "fixture.json").read_text(encoding="utf-8"))
    output.mkdir(parents=True)
    fixture_out = output / "fixture"
    fixture_out.mkdir()

    public_inputs: list[str] = []
    for rel in [fixture["prompt"], *fixture["inputs"]]:
        if rel.startswith("../../fixture-workspace/"):
            public_inputs.append("../workspace/" + rel.removeprefix("../../fixture-workspace/"))
            continue
        src = source / rel
        dst = fixture_out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        public_inputs.append(rel)

    allowed_src = (source / fixture["allowed_packages"]).resolve()
    shutil.copy2(allowed_src, fixture_out / "allowed-packages.json")
    shutil.copytree(pack_root / "fixture-workspace", output / "workspace", ignore=shutil.ignore_patterns("node_modules", "dist", "storybook-static", "__pycache__"))

    public_fixture = {key: value for key, value in fixture.items() if key not in {"sealed_answer_key", "rubric"}}
    public_fixture["inputs"] = public_inputs[1:]
    public_fixture["prompt"] = public_inputs[0]
    public_fixture["allowed_packages"] = "allowed-packages.json"
    public_fixture["workspace"] = "../workspace"
    (fixture_out / "fixture.json").write_text(json.dumps(public_fixture, indent=2) + "\n", encoding="utf-8")
    bundle = {"schema_version": "1.0.0", "task_id": task_id, "fixture": "fixture/fixture.json", "workspace": "workspace", "workspace_route": fixture.get("workspace_route")}
    (output / "bundle.json").write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--task", choices=sorted(TASKS), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    materialize(args.pack_root.resolve(), args.task, args.output.resolve())
    print(f"Materialized {args.task} worker bundle at {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
