#!/usr/bin/env python3
import copy,json,unittest
from pathlib import Path
from aggregate_scores import ScoreError,aggregate
ROOT=Path(__file__).resolve().parents[1];DIRS={"C1":"c1-visual-generation","C2":"c2-brand-adherence"}
def rubric(task):return json.loads((ROOT/"fixtures"/DIRS[task]/"sealed/rubric.json").read_text())
def score(task,rep,arm,reviewer,total,role="blinded_human",preference="candidate"):
    spec=rubric(task);ratio=total/spec["maximum_points"];items=[{"item_id":x["id"],"score":x["points"]*ratio,"maximum":x["points"],"evidence_ids":[f"{task}-{rep}-render"],"note":""} for x in spec["items"]]
    return {"schema_version":"1.0.0","reviewer_id":reviewer,"reviewer_role":role,"arm_id":arm,"task_id":task,"replicate_id":rep,"rubric_version":"1.0.0","item_scores":items,"raw_score":sum(x["score"] for x in items),"maximum_score":spec["maximum_points"],"pairwise_baseline_preference":preference,"hard_gates":{"security":"pass","accessibility":"pass","cost":"pass","evidence":"pass"},"locked_at_utc":"2026-09-09T00:00:00Z","adjudication_required":role=="blinded_adjudicator"}
def ops(task,rep,arm,reviewer="ops-1"):return {"schema_version":"1.0.0","reviewer_id":reviewer,"reviewer_role":"operations_security","arm_id":arm,"task_id":task,"replicate_id":rep,"hard_gates":{"security":"pass","accessibility":"pass","cost":"pass","evidence":"pass"},"evidence_ids":[f"{task}-{rep}-ops"],"locked_at_utc":"2026-09-09T00:00:01Z"}
def runs(arm,values,baseline=False):
    out=[]
    for task,total in values.items():
        for index in range(1,4):
            rep=f"r{index}";pref="not_applicable" if baseline else "candidate"
            out.append({"task_id":task,"replicate_id":rep,"completion_state":"complete","elapsed_seconds":100,"scores":[score(task,rep,arm,"human-a",total,preference=pref),score(task,rep,arm,"human-b",total,preference=pref)],"operations_review":ops(task,rep,arm)})
    return out
def campaign():return {"schema_version":"1.0.0","lane":"free-brand-assets","arm_id":"arm-b42","baseline_arm_id":"arm-a17","replicates":runs("arm-b42",{"C1":13,"C2":18}),"baseline_replicates":runs("arm-a17",{"C1":12,"C2":16},True)}
class Tests(unittest.TestCase):
    def test_valid_records_advance_and_compute_baseline(self):
        result=aggregate(campaign(),ROOT);self.assertTrue(result["advances"]);self.assertAlmostEqual(result["baseline_normalized_lane_score"],80)
    def test_caller_baseline_number_is_rejected(self):
        data=campaign();data["baseline_normalized_score"]=0
        with self.assertRaisesRegex(ScoreError,"caller baseline"):aggregate(data,ROOT)
    def test_rubric_item_id_and_maximum_are_bound(self):
        for field,value in [("item_id","invented"),("maximum",99)]:
            with self.subTest(field=field):
                data=campaign();data["replicates"][0]["scores"][0]["item_scores"][0][field]=value
                with self.assertRaisesRegex(ScoreError,"sealed rubric"):aggregate(data,ROOT)
    def test_score_range_sum_timestamp_and_evidence(self):
        mutations=[lambda s:s["item_scores"][0].update(score=99),lambda s:s.update(raw_score=0),lambda s:s.update(locked_at_utc="yesterday"),lambda s:s["item_scores"][0].update(evidence_ids=[])]
        for mutate in mutations:
            data=campaign();mutate(data["replicates"][0]["scores"][0])
            with self.assertRaises(ScoreError):aggregate(data,ROOT)
    def test_distinct_humans_and_operations_reviewer_required(self):
        data=campaign();data["replicates"][0]["scores"][1]["reviewer_id"]="human-a"
        with self.assertRaisesRegex(ScoreError,"distinct blinded"):aggregate(data,ROOT)
        data=campaign();data["replicates"][0]["operations_review"]["reviewer_id"]="human-a"
        with self.assertRaisesRegex(ScoreError,"operations reviewer"):aggregate(data,ROOT)
        data=campaign();data["replicates"][0].pop("operations_review")
        with self.assertRaisesRegex(ScoreError,"replicate fields"):aggregate(data,ROOT)
    def test_operations_evidence_gate_and_timestamp(self):
        for mutate in [lambda o:o.update(evidence_ids=[]),lambda o:o["hard_gates"].update(cost="fail"),lambda o:o.update(locked_at_utc="2026-09-09")]:
            data=campaign();mutate(data["replicates"][0]["operations_review"])
            if data["replicates"][0]["operations_review"]["hard_gates"]["cost"]=="fail":self.assertIn("hard_gate",aggregate(data,ROOT)["stop_reasons"])
            else:
                with self.assertRaises(ScoreError):aggregate(data,ROOT)
    def test_mean_within_threshold_and_adjudicator_replacement(self):
        data=campaign();run=data["replicates"][0];run["scores"][1]=score("C1","r1","arm-b42","human-b",8,preference="baseline");run["scores"].append(score("C1","r1","arm-b42","human-c",14,"blinded_adjudicator"))
        result=aggregate(data,ROOT);self.assertIn("C1-r1",result["reconciled_replicates"]);self.assertEqual(result["task_medians"]["C1"],13)
        data=campaign();data["replicates"][0]["scores"][1]=score("C1","r1","arm-b42","human-b",8,preference="baseline")
        with self.assertRaisesRegex(ScoreError,"adjudicator"):aggregate(data,ROOT)
    def test_three_replicates_failure_floors_thresholds_and_time(self):
        data=campaign();data["replicates"].pop()
        with self.assertRaisesRegex(ScoreError,"three retained"):aggregate(data,ROOT)
        data=campaign();data["replicates"][0]["completion_state"]="failed";data["replicates"][0]["scores"]=[];self.assertIn("failed_replicate",aggregate(data,ROOT)["stop_reasons"])
        data=campaign();[run.update(elapsed_seconds=121) for run in data["replicates"]];self.assertIn("time_regression",aggregate(data,ROOT)["stop_reasons"])
        data=campaign();data["baseline_replicates"]=runs("arm-a17",{"C1":13,"C2":18},True);self.assertIn("baseline_improvement",aggregate(data,ROOT)["stop_reasons"])
        data=campaign();data["replicates"]=runs("arm-b42",{"C1":15,"C2":15});self.assertIn("task_floor",aggregate(data,ROOT)["stop_reasons"])
if __name__=="__main__":unittest.main()
