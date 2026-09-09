#!/usr/bin/env python3
"""Adversarial validation for the frozen preparation-only canary pack."""
from __future__ import annotations
import argparse, hashlib, json, re, struct, sys
from pathlib import Path
from aggregate_scores import ScoreError, validate_ops, validate_score

BASE_COMMIT="b423a159e2107ee4c06e4a899e9fbf1bd01a70dd"
ARMS={"arm-a17","arm-b42","arm-c08","arm-d31","arm-e59","arm-f24","arm-g73","arm-h66","arm-j11","arm-k90"}
COMMUNITY_PINS={"arm-c08":"ccbc15639c97057cbfcf32ecebc38ef716e4bb37","arm-d31":"4aad0584d92131626b16d4ff4d77f0455385013c","arm-e59":"ff94e5b4e1c98d259f3cde9f806406c4528deed4"}
ARM_CORE={
"arm-a17":("planned","control",["workflow-code-native","free-brand-assets"],["C1","C2","C3","C4","C5"],False),
"arm-b42":("planned","included-workflow-control",["workflow-code-native","free-brand-assets"],["C1","C2","C3","C4","C5"],True),
"arm-c08":("planned_requires_retained_package","community-instruction-challenger",["workflow-code-native"],["C1","C2","C3","C4","C5"],True),
"arm-d31":("planned_requires_retained_package","community-instruction-challenger",["workflow-code-native"],["C1","C2","C3","C4","C5"],True),
"arm-e59":("conditional_requires_retained_package_approval","optional-community-instruction-reserve",["workflow-code-native"],["C1","C2","C3","C4","C5"],True),
"arm-f24":("planned_requires_receipt","editable-canvas",["editable-canvas"],["C1","C2","C4","C6"],True),
"arm-g73":("conditional_unpinned","optional-editable-canvas-exploratory",["editable-canvas"],["C1","C2","C4","C6"],True),
"arm-h66":("conditional_read_only_unscored","optional-read-only-context",[],["C1","C2","C4"],True),
"arm-j11":("conditional_requires_receipt","optional-brand-production-workflow",["free-brand-assets"],["C1","C2"],True),
"arm-k90":("planned_overlay","local-qa-augmentation",["qa-augmentation"],["C4","C5"],True)}
ARM_ALLOWED={
"arm-a17":{"local repository","included local browser","native Codex ImageGen"},
"arm-b42":{"local repository","included local browser","native Codex ImageGen","sealed workflow instructions"},
"arm-c08":{"local repository","included local browser","native Codex ImageGen","retained instruction files"},
"arm-d31":{"local repository","included local browser","native Codex ImageGen","retained instruction and data files"},
"arm-e59":{"local repository","included local browser","native Codex ImageGen","retained instruction files"},
"arm-f24":{"local repository","included local browser","native Codex ImageGen","isolated editable canvas"},
"arm-g73":{"local repository","included local browser","native Codex ImageGen","free eligible canvas path"},
"arm-h66":{"read-only design context"},
"arm-j11":{"local repository","native Codex ImageGen","included sealed workflow path"},
"arm-k90":{"local Storybook","retained shadcn-compatible components","local Playwright","local axe-core","local Pa11y"}}
ARM_OPTIONAL_KEYS={"arm-c08":{"retained_package_sha256"},"arm-d31":{"retained_package_sha256"},"arm-e59":{"retained_package_sha256","activation_requirements"},"arm-f24":{"security_requirements"},"arm-g73":{"retained_package_sha256","activation_requirements"},"arm-h66":{"retained_package_sha256","activation_requirements"},"arm-j11":{"retained_package_sha256","activation_requirements"}}
ARM_BASE_KEYS={"schema_version","arm_id","activation","arm_class","lanes","tasks","instruction_layer","candidate_source_pin","zero_cost_receipt_required","native_imagegen","allowed_capabilities","blocked_capabilities"}
ARM_PINS={"arm-a17":{"kind":"builtin","value":"pinned Codex snapshot from run manifest"},"arm-b42":{"kind":"catalog-version","value":"0.1.54"},"arm-c08":{"kind":"commit","value":"ccbc15639c97057cbfcf32ecebc38ef716e4bb37"},"arm-d31":{"kind":"commit","value":"4aad0584d92131626b16d4ff4d77f0455385013c"},"arm-e59":{"kind":"commit","value":"ff94e5b4e1c98d259f3cde9f806406c4528deed4"},"arm-f24":{"kind":"exact-version","value":"2.15.0"},"arm-g73":None,"arm-h66":{"kind":"catalog-version","value":"2.0.21"},"arm-j11":{"kind":"catalog-version","value":"0.1.25"},"arm-k90":{"kind":"allowlisted-package-lock","value":"fixtures/shared/allowed-packages.json"}}
SCORING={"replicate_count":3,"normalized_lane_minimum":75,"matched_baseline_improvement_minimum":5,"maximum_median_time_regression_percent":20,"failed_replicate_prevents_advancement":True,"hard_gates":["security","accessibility","cost","evidence"],"cross_lane_leaderboard_prohibited":True,"lane_denominators":{"workflow-code-native":90,"editable-canvas":85,"free-brand-assets":35,"qa-augmentation":40},"task_floors_percent":{"workflow-code-native:C4":70,"editable-canvas:C4":70,"editable-canvas:C6":70,"free-brand-assets:C2":80},"task_points":{"C1":15,"C2":20,"C3":15,"C4":25,"C5":15,"C6":25}}
OUTPUTS={
"C1":{"direction-1","direction-2","direction-3","selection-rationale.md","refined-source","desktop-1440x1000.png","campaign-1080x1080.png","evidence.json"},
"C2":{"pricing-page-source","pricing-1440x1000.png","email-header-1200x480.png","social-1080x1080.png","social-1080x1350.png","social-1080x1920.png","token-component-map.json","evidence.json"},
"C3":{"step-1.png","step-2.png","step-3.png","step-4.png","step-5.png","findings.json","evidence.json"},
"C4":{"repository-code","desktop-1440x1000.png","mobile-390x844.png","playwright-results.json","loading.png","empty.png","error.png","evidence.json"},
"C5":{"code.diff","playwright-results.json","axe-results.json","pa11y-results.json","keyboard-trace.json","reduced-motion.json","zoom-200.json","320.png","768.png","1440.png","1920.png","evidence.json"},
"C6":{"editable-canvas-receipt.json","canvas-before.png","canvas-after.png","source.diff","unrelated-snapshot-after.txt","desktop-final.png","mobile-final.png","audit-trail.json","evidence.json"}}
SCHEMA_REQUIRED={
"evidence.schema.json":{"schema_version","run_id","artifacts","event_log_path","stdout_path","stderr_path","code_diff_path","dependency_diff_path","accessibility_report_paths","tool_receipt_paths"},
"score.schema.json":{"schema_version","reviewer_id","reviewer_role","arm_id","task_id","replicate_id","rubric_version","item_scores","raw_score","maximum_score","pairwise_baseline_preference","hard_gates","locked_at_utc","adjudication_required"},
"operations-review.schema.json":{"schema_version","reviewer_id","reviewer_role","arm_id","task_id","replicate_id","hard_gates","evidence_ids","locked_at_utc"},
"zero-cost-receipt.schema.json":{"schema_version","arm_id","product","capability","account_plan","price_displayed","trial_state","renewal_or_conversion","remaining_quota","payment_method_required","paid_seat_required","subscription_required","addon_required","paid_hosting_required","commercial_license_trigger","upgrade_required","checked_evidence_locator","checked_at_utc","checker","evidence_sha256","eligible"},
"editable-canvas-receipt.schema.json":{"schema_version","arm_id","platform","version","listener","public_listener_detected","zero_cost_receipt_sha256","canvas_locator","canvas_sha256","checked_at_utc","checker"}}
SCHEMAS={"run-manifest.schema.json","evidence.schema.json","score.schema.json","operations-review.schema.json","zero-cost-receipt.schema.json","native-imagegen-availability.schema.json","editable-canvas-receipt.schema.json"}
PROTOCOL_TEXT=["normalized lane score is at least 75/100","it improves by at least 5 normalized points over its matched baseline.","One failed replicate prevents advancement","Any security, accessibility, cost, or evidence hard-gate failure prevents advancement.","evaluated agents receive only worker bundles","listener host must be exactly `127.0.0.1` or `::1`","pack revision is the containing Git commit recorded by the F006 lead"]
PAID=re.compile(r"\b(paid|premium|bill(?:ed|ing)?|subscription|credits?|purchase|upgrade|commercial|metered|full seat|pro plan|stripe|checkout|cost|payment|fee|chargeable|enterprise)\b",re.I)
SITES=re.compile(r"\bsites?\b|site[_ -]?(?:publish|deploy|host)",re.I)
SHA=re.compile(r"^[0-9a-f]{64}$")

def load(path, errors):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: errors.append(f"invalid JSON {path}: {exc}"); return {}
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def png(path):
    data=path.read_bytes()[:33]
    if len(data)<33 or data[:8]!=b"\x89PNG\r\n\x1a\n" or data[12:16]!=b"IHDR": raise ValueError("invalid PNG IHDR")
    return struct.unpack(">IIBB",data[16:26])
def version_at_least_215(value):
    match=re.fullmatch(r"(\d+)\.(\d+)(?:\.(\d+))?",str(value))
    return bool(match and tuple(map(int,match.groups(default="0"))) >= (2,15,0))
def nested_credential(value, path=""):
    if isinstance(value,dict):
        for key,item in value.items():
            here=f"{path}.{key}"; norm=re.sub(r"[^a-z0-9]","",key.lower())
            if key!="blocked_capabilities" and (norm in {"openaiapikey","apikey","credentials","secrettoken"} or "openaiapikey" in norm): return here
            if key!="blocked_capabilities":
                found=nested_credential(item,here)
                if found:return found
    elif isinstance(value,list):
        for index,item in enumerate(value):
            found=nested_credential(item,f"{path}[{index}]")
            if found:return found
    elif isinstance(value,str) and (value.upper()=="OPENAI_API_KEY" or re.search(r"OPENAI_API_KEY\s*=",value,re.I)): return path
    return None

def evidence_template_errors(data):
    errors=[]; required=SCHEMA_REQUIRED["evidence.schema.json"]
    if set(data)!=required: return ["evidence template fields are missing or unknown"]
    if not all(isinstance(data[k],str) and data[k] for k in ("run_id","event_log_path","stdout_path","stderr_path")): errors.append("evidence template path metadata invalid")
    if not isinstance(data["artifacts"],list) or not data["artifacts"]: errors.append("evidence template artifacts empty"); return errors
    fields={"artifact_id","kind","path_or_uri","sha256","size_bytes","created_at_utc","retention_owner","retention_expires_at","viewport","source_event_id"}
    for item in data["artifacts"]:
        if set(item)!=fields or not all(item.get(k) for k in ("artifact_id","kind","path_or_uri","created_at_utc","retention_owner","retention_expires_at","source_event_id")) or not SHA.fullmatch(str(item.get("sha256",""))) or not isinstance(item.get("size_bytes"),int) or item["size_bytes"]<1: errors.append("evidence artifact metadata invalid")
    return errors

def canvas_receipt_errors(data):
    errors=[]; required=SCHEMA_REQUIRED["editable-canvas-receipt.schema.json"]
    if set(data)!=required:return ["editable canvas receipt fields are missing or unknown"]
    listener=data.get("listener",{})
    if set(listener)!={"host","port","inspection_command","inspection_output","inspection_output_sha256"}: errors.append("Penpot listener evidence incomplete")
    elif listener["host"] not in {"127.0.0.1","::1"} or not listener["inspection_command"] or not listener["inspection_output"] or not SHA.fullmatch(listener["inspection_output_sha256"]) or hashlib.sha256(listener["inspection_output"].encode()).hexdigest()!=listener["inspection_output_sha256"]: errors.append("Penpot listener must be exact loopback with command/output/hash")
    if not version_at_least_215(data.get("version")) or data.get("public_listener_detected") is not False: errors.append("Penpot version/listener security gate failed")
    return errors

def validate_pack(root:Path,verify_checksums=True):
    errors=[]
    for name in ["README.md","protocol.md","manifest.json","scoring.json","native-imagegen-availability.json","report.md"]:
        if not (root/name).is_file():errors.append(f"missing required file: {name}")
    manifest=load(root/"manifest.json",errors); scoring=load(root/"scoring.json",errors); protocol=(root/"protocol.md").read_text(encoding="utf-8")
    if manifest.get("base_commit")!=BASE_COMMIT:errors.append("manifest base commit drift")
    if manifest.get("pack_revision")!="containing_git_commit":errors.append("pack revision must be the containing Git commit")
    if manifest.get("replicates")!=["r1","r2","r3"]:errors.append("manifest must plan exactly r1, r2, r3")
    if set(manifest.get("opaque_arm_ids",[]))!=ARMS:errors.append("manifest opaque arm set changed")
    if {k:scoring.get(k) for k in SCORING}!=SCORING:errors.append("frozen scoring thresholds, gates, weights, or denominators changed")
    lower=protocol.lower()
    if any(text.lower() not in lower for text in PROTOCOL_TEXT) or "capability win" in lower or "cannot perform" in lower:errors.append("protocol frozen threshold/isolation text drift")
    for name in SCHEMAS:
        path=root/"schemas"/name
        if not path.is_file():errors.append(f"missing schema: {name}");continue
        schema=load(path,errors)
        if schema.get("additionalProperties") is not False or not schema.get("required"):errors.append(f"schema is not strict at root: {name}")
        if name in SCHEMA_REQUIRED and set(schema.get("required",[]))!=SCHEMA_REQUIRED[name]:errors.append(f"schema required metadata changed: {name}")
    errors.extend(evidence_template_errors(load(root/"templates/evidence.template.json",errors)))
    errors.extend(canvas_receipt_errors(load(root/"templates/editable-canvas-receipt.template.json",errors)))
    try:
        rubric={item["id"]:item["points"] for item in load(root/"fixtures/c1-visual-generation/sealed/rubric.json",errors)["items"]}
        validate_score(load(root/"templates/reviewer-score.template.json",errors),"C1","r1","arm-a17",rubric)
        validate_ops(load(root/"templates/operations-review.template.json",errors),"C1","r1","arm-a17",{"blind-reviewer-01"})
    except ScoreError as exc:errors.append(f"score template invalid: {exc}")
    receipt=load(root/"templates/zero-cost-receipt.template.json",errors)
    if set(receipt)!=SCHEMA_REQUIRED["zero-cost-receipt.schema.json"] or receipt.get("eligible") is not True or any(receipt.get(k) is not False for k in ("payment_method_required","paid_seat_required","subscription_required","addon_required","paid_hosting_required","commercial_license_trigger","upgrade_required")):errors.append("zero-cost receipt template invalid")
    native=load(root/"native-imagegen-availability.json",errors)
    if native.get("model")!="gpt-image-2" or any(native.get(k) is not True for k in ("openai_api_key_prohibited","paid_api_fallback_prohibited","capacity_purchase_prohibited")):errors.append("native ImageGen record invalid")
    arm_ids=set()
    for path in sorted((root/"arms").glob("arm-*/manifest.json")):
        arm=load(path,errors); aid=arm.get("arm_id");arm_ids.add(aid)
        if aid!=path.parent.name:errors.append(f"arm id/path mismatch: {path}")
        if aid in ARM_CORE:
            activation,kind,lanes,tasks,receipt=ARM_CORE[aid]
            if set(arm)!=(ARM_BASE_KEYS|ARM_OPTIONAL_KEYS.get(aid,set())) or arm.get("schema_version")!="1.0.0" or arm.get("activation")!=activation or arm.get("arm_class")!=kind or arm.get("lanes")!=lanes or arm.get("tasks")!=tasks or arm.get("zero_cost_receipt_required") is not receipt:errors.append(f"arm structural profile changed: {aid}")
            if set(arm.get("allowed_capabilities",[]))!=ARM_ALLOWED[aid] or len(arm.get("allowed_capabilities",[]))!=len(ARM_ALLOWED[aid]):errors.append(f"arm capability allowlist changed: {aid}")
            if arm.get("candidate_source_pin")!=ARM_PINS[aid] or not isinstance(arm.get("blocked_capabilities"),list) or not arm["blocked_capabilities"]:errors.append(f"arm source/block profile changed: {aid}")
        allowed=" ".join(arm.get("allowed_capabilities",[]))
        if PAID.search(allowed) or SITES.search(allowed):errors.append(f"unapproved paid/prohibited capability in {aid}")
        if nested_credential(arm):errors.append(f"nested credential/API-key surface prohibited in {aid}")
        pin=arm.get("candidate_source_pin")
        if isinstance(pin,dict) and (pin.get("kind") in {"branch","mutable-branch"} or str(pin.get("value","")).lower() in {"latest","main","master","head","develop"}):errors.append(f"mutable source pin prohibited: {aid}")
        if aid in COMMUNITY_PINS:
            if pin!={"kind":"commit","value":COMMUNITY_PINS[aid]} or "retained_package_sha256" not in arm:errors.append(f"community arm exact pin/retained hash contract changed: {aid}")
        if "retained_package_sha256" in arm and arm["retained_package_sha256"] is not None and not SHA.fullmatch(str(arm["retained_package_sha256"])):errors.append(f"retained package hash invalid: {aid}")
        if set(arm.get("tasks",[])) & {"C1","C2"} and arm.get("native_imagegen")!="fixed_when_task_requires_images":errors.append(f"native ImageGen disabled or unequal in applicable arm: {aid}")
    if arm_ids!=ARMS:errors.append("arm definitions incomplete")
    penpot=load(root/"arms/arm-f24/manifest.json",errors)
    requirements=" ".join(penpot.get("security_requirements",[]))
    if penpot.get("candidate_source_pin")!={"kind":"exact-version","value":"2.15.0"} or "127.0.0.1 or ::1" not in requirements or "command/output/hash" not in requirements:errors.append("Penpot arm security contract changed")
    amap=load(root/"sealed/arm-map.json",errors); entries=amap.get("entries",[])
    if amap.get("sealed") is not True or {e.get("arm_id") for e in entries}!=ARMS or len(entries)!=len(ARMS) or any(set(e)!={"arm_id","identity","version","role"} or not all(e.values()) for e in entries):errors.append("sealed arm key incomplete")
    fixtures={}
    for directory in sorted((root/"fixtures").glob("c[1-6]-*")):
        fixture=load(directory/"fixture.json",errors);task=fixture.get("task_id");fixtures[task]=(directory,fixture)
        required={"schema_version","task_id","title","prompt","inputs","sealed_answer_key","rubric","allowed_packages","viewports","required_outputs"}
        if not required.issubset(fixture) or not fixture.get("viewports"):errors.append(f"fixture metadata incomplete: {task}")
        if set(fixture.get("required_outputs",[]))!=OUTPUTS.get(task,set()):errors.append(f"required outputs incomplete or changed: {task}")
        if task in {"C3","C4","C5","C6"} and (fixture.get("workspace")!="../../fixture-workspace" or not fixture.get("workspace_route")):errors.append(f"runnable workspace path missing: {task}")
        for rel in [fixture.get("prompt"),fixture.get("sealed_answer_key"),fixture.get("rubric"),fixture.get("allowed_packages"),*fixture.get("inputs",[])]:
            if not isinstance(rel,str) or not (directory/rel).is_file():errors.append(f"missing fixture asset {directory.name}/{rel}")
        key=load(directory/str(fixture.get("sealed_answer_key","missing")),errors);rubric=load(directory/str(fixture.get("rubric","missing")),errors)
        if key.get("task_id")!=task:errors.append(f"sealed answer key incomplete for {task}")
        if rubric.get("task_id")!=task or not rubric.get("items") or sum(i.get("points",0) for i in rubric.get("items",[]))!=rubric.get("maximum_points") or rubric.get("maximum_points")!=SCORING["task_points"].get(task):errors.append(f"rubric incomplete for {task}")
    if set(fixtures)!={"C1","C2","C3","C4","C5","C6"}:errors.append("fixture set must be C1-C6")
    keys={task:load(directory/fixture["sealed_answer_key"],errors) for task,(directory,fixture) in fixtures.items()}
    substantive={"C1":len(keys.get("C1",{}).get("seeded_traps",[]))==3 and len(keys["C1"].get("evidence_minimum",[]))>=6,"C2":len(keys.get("C2",{}).get("seeded_traps",[]))==4 and len(keys["C2"].get("source_precedence",[]))==5,"C3":len(keys.get("C3",{}).get("issues",[]))==12 and len(keys["C3"].get("intentional_nonissues",[]))==3,"C4":len(keys.get("C4",{}).get("seeded_traps",[]))==4 and len(keys["C4"].get("required_interactions",[]))==3,"C5":len(keys.get("C5",{}).get("defect_ids",[]))==10 and len(keys["C5"].get("check_ids",[]))==10,"C6":len(keys.get("C6",{}).get("seeded_traps",[]))==4 and len(keys["C6"].get("approved_change_ids",[]))==3}
    for task,ok in substantive.items():
        if not ok:errors.append(f"sealed substantive key incomplete for {task}")
    c3public=(root/"fixtures/c3-ux-audit/flow-spec.json").read_text().lower()
    if '"behavior"' in c3public or any(term in c3public for term in ["discoverability","dead-end","screen-reader","overflow","contrast"]):errors.append("C3 public flow leaks answer annotations")
    for ref,align in [("desktop-1440.svg","xMaxYMin slice"),("mobile-390.svg","xMinYMax slice")]:
        text=(root/"fixtures/c4-screenshot-to-code/references"/ref).read_text()
        if 'href="aurora.jpg.svg"' not in text or align not in text:errors.append(f"C4 executable crop missing: {ref}")
    starter=(root/"fixture-workspace/src/routes/Analytics.tsx").read_text()
    if any(marker in starter for marker in ['<svg role="img"','intent="primary"','/aurora.svg','className="analytics"']):errors.append("C4 starter contains solved scored behavior")
    if "selected-direction.md" not in fixtures["C2"][1].get("inputs",[]):errors.append("C2 frozen selected direction missing")
    c6_changes=load(root/"fixtures/c6-penpot-roundtrip/expected-changes.json",errors);c6_spec=load(root/"fixtures/c6-penpot-roundtrip/roundtrip-spec.json",errors)
    for rel in [*c6_changes.get("bounded_paths",[]),*c6_changes.get("must_not_change",[])]:
        if isinstance(rel,str) and rel.startswith("src/") and not (root/"fixture-workspace"/rel).is_file():errors.append(f"C6 referenced source path missing: {rel}")
    grid=(root/"fixture-workspace/src/pricing/PricingGrid.tsx").read_text();tokens=(root/"fixture-workspace/src/tokens.css").read_text()
    for named in c6_spec.get("source",{}).get("components",[]):
        component=str(named).split("/",1)[0];source=root/"fixture-workspace/src/pricing"/f"{component}.tsx"
        if component=="PricingGrid":source=root/"fixture-workspace/src/pricing/PricingGrid.tsx"
        if not source.is_file() or f"export function {component}" not in source.read_text() or (component!="PricingGrid" and f"<{component}" not in grid):errors.append(f"C6 named component is not exported and used: {named}")
    for token in c6_spec.get("source",{}).get("tokens",[]):
        if not re.search(rf"{re.escape(str(token))}\s*:",tokens):errors.append(f"C6 semantic token missing: {token}")
    specs=load(root/"fixtures/c1-visual-generation/image-specs.json",errors)
    for item in specs.get("images",[]):
        path=root/"fixtures/c1-visual-generation"/item["path"]
        if not path.is_file():errors.append(f"missing fixture asset C1/{item['path']}");continue
        try:w,h,depth,color=png(path); assert depth>=8
        except Exception as exc:errors.append(f"invalid C1 PNG {item['path']}: {exc}");continue
        if w<item["minimum_width"] or h<item["minimum_height"]:errors.append(f"C1 image too small: {item['path']}")
        if item.get("requires_transparency") and color not in {4,6}:errors.append(f"C1 image lacks alpha: {item['path']}")
    c5=load(root/"fixtures/c5-accessibility-repair/flawed-checkout-spec.json",errors);checks=load(root/"fixtures/c5-accessibility-repair/expected-checks.json",errors)
    if len(c5.get("seeded_defects",[]))!=10 or {x.get("covers") for x in checks.get("checks",[])}!={f"D{i:02d}" for i in range(1,11)}:errors.append("C5 defect/check ledger incomplete")
    workspace=root/"fixture-workspace"; required_workspace=["package.json","package-lock.json","tsconfig.json","vite.config.ts","index.html","src/App.tsx","src/data.ts","src/tokens.css","src/ui/Button.tsx","src/ui/Tabs.tsx","src/ui/Drawer.tsx","src/routes/AccountRecovery.tsx","src/routes/Analytics.tsx","src/routes/Checkout.tsx","src/pricing/PricingGrid.tsx","src/pricing/PlanCard.tsx","src/pricing/FeatureList.tsx","src/pricing/BillingToggle.tsx","src/pricing/UnrelatedTrustSection.tsx",".storybook/main.ts","src/ui/Button.stories.tsx","tests/fixtures.test.mjs","public/aurora.svg"]
    for rel in required_workspace:
        if not (workspace/rel).is_file():errors.append(f"runnable workspace file missing: {rel}")
    package=load(workspace/"package.json",errors);lock=load(workspace/"package-lock.json",errors)
    allowed=load(root/"fixtures/shared/allowed-packages.json",errors);allowed_versions={item.get("name"):item.get("version") for item in allowed.get("packages",[])}
    for group in ("dependencies","devDependencies"):
        for name,version in package.get(group,{}).items():
            if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?",version):errors.append(f"workspace dependency not exact: {name}")
            if lock.get("packages",{}).get("",{}).get(group,{}).get(name)!=version:errors.append(f"lockfile mismatch: {name}")
            if allowed_versions.get(name)!=version:errors.append(f"allowed package inventory mismatch: {name}")
    if verify_checksums:
        sums=root/"SHA256SUMS"
        if not sums.is_file():errors.append("missing SHA256SUMS")
        else:
            listed=set()
            for line in sums.read_text().splitlines():
                try:expected,rel=line.split(None,1);rel=rel.lstrip("*");path=root.parent.parent/rel;listed.add(str(path.relative_to(root)))
                except Exception:errors.append("malformed SHA256SUMS line");continue
                if not path.is_file() or digest(path)!=expected:errors.append(f"checksum mismatch: {rel}")
            actual={str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and p.name!="SHA256SUMS" and "__pycache__" not in p.parts and "node_modules" not in p.parts and "dist" not in p.parts}
            if listed!=actual:errors.append("SHA256SUMS inventory incomplete or extra")
    return errors

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument("--skip-checksums",action="store_true");args=parser.parse_args();errors=validate_pack(args.root.resolve(),not args.skip_checksums)
    if errors:
        for error in errors:print(f"ERROR: {error}",file=sys.stderr)
        print(f"FAIL: {len(errors)} validation error(s)",file=sys.stderr);return 1
    print("PASS: design-plugin-canary-v1 is internally consistent");return 0
if __name__=="__main__":raise SystemExit(main())
