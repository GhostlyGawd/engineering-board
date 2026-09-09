#!/usr/bin/env python3
"""Validate retained reviewer records, reconcile them, and decide advancement."""
from __future__ import annotations
import argparse, json, statistics
from datetime import datetime
from pathlib import Path

TASK_POINTS={"C1":15,"C2":20,"C3":15,"C4":25,"C5":15,"C6":25}
TASK_DIRS={"C1":"c1-visual-generation","C2":"c2-brand-adherence","C3":"c3-ux-audit","C4":"c4-screenshot-to-code","C5":"c5-accessibility-repair","C6":"c6-penpot-roundtrip"}
LANES={"workflow-code-native":(["C1","C2","C3","C4","C5"],90,{"C4":70}),"editable-canvas":(["C1","C2","C4","C6"],85,{"C4":70,"C6":70}),"free-brand-assets":(["C1","C2"],35,{"C2":80}),"qa-augmentation":(["C4","C5"],40,{})}
SCORE_KEYS={"schema_version","reviewer_id","reviewer_role","arm_id","task_id","replicate_id","rubric_version","item_scores","raw_score","maximum_score","pairwise_baseline_preference","hard_gates","locked_at_utc","adjudication_required"}
ITEM_KEYS={"item_id","score","maximum","evidence_ids","note"}; GATES={"security","accessibility","cost","evidence"}
OPS_KEYS={"schema_version","reviewer_id","reviewer_role","arm_id","task_id","replicate_id","hard_gates","evidence_ids","locked_at_utc"}
class ScoreError(ValueError):pass

def utc(value):
    try:return bool(value.endswith("Z") and datetime.fromisoformat(value[:-1]+"+00:00").utcoffset().total_seconds()==0)
    except (AttributeError,ValueError):return False
def rubric_for(pack_root,task):
    data=json.loads((pack_root/"fixtures"/TASK_DIRS[task]/"sealed/rubric.json").read_text())
    return {item["id"]:item["points"] for item in data["items"]}
def validate_score(score,task,replicate,arm,rubric=None):
    if set(score)!=SCORE_KEYS:raise ScoreError("score fields are missing or unknown")
    if score["schema_version"]!="1.0.0" or score["rubric_version"]!="1.0.0":raise ScoreError("score schema/rubric version mismatch")
    if score["task_id"]!=task or score["replicate_id"]!=replicate or score["arm_id"]!=arm:raise ScoreError("score identity mismatch")
    if score["reviewer_role"] not in {"blinded_human","blinded_adjudicator"} or not score["reviewer_id"]:raise ScoreError("invalid human reviewer")
    if not utc(score["locked_at_utc"]):raise ScoreError("score timestamp must be ISO UTC")
    if score["maximum_score"]!=TASK_POINTS[task] or not score["item_scores"]:raise ScoreError("maximum or items invalid")
    seen=set();total=0.0
    for item in score["item_scores"]:
        if set(item)!=ITEM_KEYS or not item["item_id"] or item["item_id"] in seen:raise ScoreError("item fields/id invalid")
        seen.add(item["item_id"])
        if not isinstance(item["evidence_ids"],list) or not item["evidence_ids"] or any(not isinstance(x,str) or not x for x in item["evidence_ids"]):raise ScoreError("item evidence IDs must be nonempty")
        if not isinstance(item["score"],(int,float)) or not isinstance(item["maximum"],(int,float)) or not 0<=item["score"]<=item["maximum"]:raise ScoreError("item score out of range")
        total+=item["score"]
    if rubric is not None and ({item["item_id"]:item["maximum"] for item in score["item_scores"]}!=rubric):raise ScoreError("item IDs/maxima do not match sealed rubric")
    if abs(total-score["raw_score"])>1e-9:raise ScoreError("raw score does not equal item sum")
    if not 0<=score["raw_score"]<=score["maximum_score"]:raise ScoreError("raw score out of range")
    if set(score["hard_gates"])!=GATES or any(v not in {"pass","fail"} for v in score["hard_gates"].values()):raise ScoreError("human hard gates invalid")
def validate_ops(record,task,replicate,arm,human_ids):
    if set(record)!=OPS_KEYS or record.get("schema_version")!="1.0.0" or record.get("reviewer_role")!="operations_security":raise ScoreError("operations review fields/role invalid")
    if record.get("task_id")!=task or record.get("replicate_id")!=replicate or record.get("arm_id")!=arm:raise ScoreError("operations review identity mismatch")
    if not record.get("reviewer_id") or record["reviewer_id"] in human_ids:raise ScoreError("operations reviewer must be distinct")
    if set(record.get("hard_gates",{}))!=GATES or any(v not in {"pass","fail"} for v in record["hard_gates"].values()):raise ScoreError("operations hard gates invalid")
    if not record.get("evidence_ids") or any(not isinstance(x,str) or not x for x in record["evidence_ids"]):raise ScoreError("operations evidence required")
    if not utc(record.get("locked_at_utc")):raise ScoreError("operations timestamp must be ISO UTC")
def reconcile(scores,task,replicate,arm,rubric,baseline=False):
    for item in scores:validate_score(item,task,replicate,arm,rubric)
    primary=[s for s in scores if s["reviewer_role"]=="blinded_human"];adj=[s for s in scores if s["reviewer_role"]=="blinded_adjudicator"]
    if len(primary)!=2 or primary[0]["reviewer_id"]==primary[1]["reviewer_id"]:raise ScoreError("two distinct blinded human reviewers required")
    one={x["item_id"]:x for x in primary[0]["item_scores"]};two={x["item_id"]:x for x in primary[1]["item_scores"]}
    trigger=any(abs(one[k]["score"]/one[k]["maximum"]*10-two[k]["score"]/two[k]["maximum"]*10)>2 for k in one)
    if not baseline and task in {"C1","C2","C4"}:trigger|=primary[0]["pairwise_baseline_preference"]!=primary[1]["pairwise_baseline_preference"]
    if trigger:
        if len(adj)!=1 or adj[0]["reviewer_id"] in {x["reviewer_id"] for x in primary}:raise ScoreError("distinct third adjudicator required")
        result=adj[0]["raw_score"]
    else:
        if adj:raise ScoreError("adjudicator supplied without trigger")
        result=statistics.mean([x["raw_score"] for x in primary])
    failures={g for s in scores for g,v in s["hard_gates"].items() if v=="fail"}
    return result,trigger,failures,{x["reviewer_id"] for x in scores}
def validate_runs(runs,tasks,arm,pack_root,baseline=False):
    expected={(t,f"r{i}") for t in tasks for i in range(1,4)};observed={(r.get("task_id"),r.get("replicate_id")) for r in runs}
    if len(runs)!=len(expected) or observed!=expected:raise ScoreError("exactly three retained replicates per task required")
    by_task={t:[] for t in tasks};failures=[];gates=set();times=[];reconciled=[]
    for run in runs:
        if set(run)!={"task_id","replicate_id","completion_state","elapsed_seconds","scores","operations_review"}:raise ScoreError("replicate fields missing or unknown")
        task,rep=run["task_id"],run["replicate_id"]
        if run["completion_state"] not in {"complete","failed"} or not isinstance(run["elapsed_seconds"],(int,float)) or run["elapsed_seconds"]<0:raise ScoreError("replicate state/time invalid")
        times.append(run["elapsed_seconds"])
        if run["completion_state"]=="failed":
            if baseline:raise ScoreError("baseline contains failed replicate")
            value,trigger,human_gates,human_ids=0.0,False,set(),set()
            failures.append(f"{task}-{rep}")
        else:value,trigger,human_gates,human_ids=reconcile(run["scores"],task,rep,arm,rubric_for(pack_root,task),baseline)
        validate_ops(run["operations_review"],task,rep,arm,human_ids)
        gates|=human_gates|{g for g,v in run["operations_review"]["hard_gates"].items() if v=="fail"}
        by_task[task].append(value)
        if trigger:reconciled.append(f"{task}-{rep}")
    return {t:statistics.median(v) for t,v in by_task.items()},failures,gates,statistics.median(times),reconciled
def aggregate(campaign,pack_root=None):
    pack_root=pack_root or Path(__file__).resolve().parents[1]
    keys={"schema_version","lane","arm_id","baseline_arm_id","replicates","baseline_replicates"}
    if set(campaign)!=keys or campaign.get("schema_version")!="1.0.0":raise ScoreError("campaign fields/version invalid; caller baseline numbers prohibited")
    lane=campaign["lane"]
    if lane not in LANES or campaign["arm_id"]==campaign["baseline_arm_id"]:raise ScoreError("lane/arm comparison invalid")
    tasks,denominator,floors=LANES[lane]
    base_medians,_,base_gates,base_time,_=validate_runs(campaign["baseline_replicates"],tasks,campaign["baseline_arm_id"],pack_root,True)
    if base_gates:raise ScoreError("baseline hard gate failed")
    medians,failed,gates,elapsed,reconciled=validate_runs(campaign["replicates"],tasks,campaign["arm_id"],pack_root)
    normalized=sum(medians.values())/denominator*100;base=sum(base_medians.values())/denominator*100;improvement=normalized-base
    time_reg=(elapsed/base_time-1)*100 if base_time>0 else float("inf");floor_fail=[t for t,f in floors.items() if medians[t]/TASK_POINTS[t]*100<f]
    reasons=[]
    if failed:reasons.append("failed_replicate")
    if gates:reasons.append("hard_gate")
    if floor_fail:reasons.append("task_floor")
    if normalized<75:reasons.append("lane_score")
    if improvement<5:reasons.append("baseline_improvement")
    if time_reg>20:reasons.append("time_regression")
    return {"schema_version":"1.0.0","lane":lane,"arm_id":campaign["arm_id"],"baseline_arm_id":campaign["baseline_arm_id"],"task_medians":medians,"baseline_task_medians":base_medians,"normalized_lane_score":normalized,"baseline_normalized_lane_score":base,"baseline_improvement":improvement,"median_elapsed_seconds":elapsed,"baseline_median_elapsed_seconds":base_time,"median_time_regression_percent":time_reg,"failed_replicates":failed,"failed_hard_gates":sorted(gates),"failed_task_floors":floor_fail,"reconciled_replicates":reconciled,"advances":not reasons,"stop_reasons":reasons}
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--output",type=Path);p.add_argument("--pack-root",type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    try:result=aggregate(json.loads(a.input.read_text()),a.pack_root)
    except (OSError,json.JSONDecodeError,ScoreError) as exc:print(f"ERROR: {exc}");return 1
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.output:a.output.write_text(text)
    else:print(text,end="")
    return 0
if __name__=="__main__":raise SystemExit(main())
