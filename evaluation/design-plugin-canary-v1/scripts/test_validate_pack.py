#!/usr/bin/env python3
import json, shutil, tempfile, unittest
from pathlib import Path
from validate_pack import validate_pack

SOURCE=Path(__file__).resolve().parents[1]
class ValidatorAdversarialTests(unittest.TestCase):
    def copy_pack(self):
        temp=tempfile.TemporaryDirectory();root=Path(temp.name)/"pack";shutil.copytree(SOURCE,root,ignore=shutil.ignore_patterns("__pycache__","SHA256SUMS","node_modules","dist"));self.addCleanup(temp.cleanup);return root
    def mutate(self,root,rel,fn):
        path=root/rel;data=json.loads(path.read_text());fn(data);path.write_text(json.dumps(data))
    def rejected(self,root,phrase):
        errors=validate_pack(root,False);self.assertTrue(any(phrase in e for e in errors),errors)
    def test_clean(self):self.assertEqual(validate_pack(SOURCE,False),[])
    def test_paid_synonyms(self):
        for term in ["premium connector","usage credits","subscription tool","commercial service","metered billing","zero-cost add-on","payment-backed tool"]:
            with self.subTest(term=term):
                root=self.copy_pack();self.mutate(root,"arms/arm-a17/manifest.json",lambda d:d["allowed_capabilities"].append(term));self.rejected(root,"paid/prohibited")
    def test_nested_credentials(self):
        for payload in [{"env":{"OPENAI_API_KEY":"secret"}},{"command":"OPENAI_API_KEY=x"}]:
            root=self.copy_pack();self.mutate(root,"arms/arm-a17/manifest.json",lambda d,p=payload:d.update(runtime=p));self.rejected(root,"nested credential")
    def test_exact_allowlist_rejects_even_free_extra_capability(self):
        root=self.copy_pack();self.mutate(root,"arms/arm-a17/manifest.json",lambda d:d["allowed_capabilities"].append("free local canvas"));self.rejected(root,"capability allowlist")
    def test_sites_variants(self):
        for term in ["OpenAI Sites","site_publish","site deployment"]:
            with self.subTest(term=term):
                root=self.copy_pack();self.mutate(root,"arms/arm-b42/manifest.json",lambda d:d["allowed_capabilities"].append(term));self.rejected(root,"paid/prohibited")
    def test_threshold_and_protocol_drift(self):
        root=self.copy_pack();self.mutate(root,"scoring.json",lambda d:d.update(normalized_lane_minimum=74));self.rejected(root,"thresholds")
        root=self.copy_pack();path=root/"protocol.md";path.write_text(path.read_text().replace("at least 5 normalized points","at least 4 normalized points"));self.rejected(root,"protocol")
        root=self.copy_pack();path=root/"protocol.md";path.write_text(path.read_text().replace("at least 75/100","at least 74/100"));self.rejected(root,"protocol")
    def test_c6_source_component_and_token_bindings(self):
        root=self.copy_pack();self.mutate(root,"fixtures/c6-penpot-roundtrip/expected-changes.json",lambda d:d["bounded_paths"].append("src/pricing/Missing.tsx"));self.rejected(root,"referenced source path")
        root=self.copy_pack();self.mutate(root,"fixtures/c6-penpot-roundtrip/roundtrip-spec.json",lambda d:d["source"]["components"].append("MissingCard/base"));self.rejected(root,"named component")
        root=self.copy_pack();self.mutate(root,"fixtures/c6-penpot-roundtrip/roundtrip-spec.json",lambda d:d["source"]["tokens"].append("--missing-token"));self.rejected(root,"semantic token")
    def test_manifest_base_and_replicates(self):
        root=self.copy_pack();self.mutate(root,"manifest.json",lambda d:d.update(base_commit="0"*40));self.rejected(root,"base commit")
        root=self.copy_pack();self.mutate(root,"manifest.json",lambda d:d.update(replicates=["r1","r2"]));self.rejected(root,"exactly r1")
    def test_missing_asset_and_output(self):
        root=self.copy_pack();(root/"fixtures/c2-brand-adherence/tokens.json").unlink();self.rejected(root,"missing fixture asset")
        root=self.copy_pack();self.mutate(root,"fixtures/c4-screenshot-to-code/fixture.json",lambda d:d["required_outputs"].remove("playwright-results.json"));self.rejected(root,"required outputs")
    def test_mutable_and_wrong_community_pins(self):
        root=self.copy_pack();self.mutate(root,"arms/arm-g73/manifest.json",lambda d:d.update(candidate_source_pin={"kind":"branch","value":"main"}));self.rejected(root,"mutable source pin")
        root=self.copy_pack();self.mutate(root,"arms/arm-c08/manifest.json",lambda d:d.update(candidate_source_pin={"kind":"commit","value":"1"*40}));self.rejected(root,"community arm exact pin")
    def test_evidence_metadata(self):
        root=self.copy_pack();self.mutate(root,"schemas/evidence.schema.json",lambda d:d["required"].remove("event_log_path"));self.rejected(root,"schema required metadata")
        root=self.copy_pack();self.mutate(root,"templates/evidence.template.json",lambda d:d["artifacts"][0].pop("retention_owner"));self.rejected(root,"artifact metadata")
    def test_each_sealed_fixture_key_is_substantive(self):
        cases={"c1-visual-generation":"seeded_traps","c2-brand-adherence":"source_precedence","c3-ux-audit":"issues","c4-screenshot-to-code":"required_interactions","c5-accessibility-repair":"defect_ids","c6-penpot-roundtrip":"approved_change_ids"}
        for directory,field in cases.items():
            with self.subTest(task=directory):
                root=self.copy_pack();self.mutate(root,f"fixtures/{directory}/sealed/answer-key.json",lambda d,f=field:d.update({f:[]}));self.rejected(root,"sealed substantive key")
    def test_sealed_arm_key(self):
        root=self.copy_pack();self.mutate(root,"sealed/arm-map.json",lambda d:d["entries"].pop());self.rejected(root,"sealed arm key")
    def test_native_imagegen_cannot_be_disabled(self):
        root=self.copy_pack();self.mutate(root,"arms/arm-c08/manifest.json",lambda d:d.update(native_imagegen="disabled"));self.rejected(root,"native ImageGen disabled")
    def test_penpot_listener_and_version(self):
        root=self.copy_pack();self.mutate(root,"templates/editable-canvas-receipt.template.json",lambda d:d["listener"].update(host="0.0.0.0"));self.rejected(root,"Penpot listener")
        root=self.copy_pack();self.mutate(root,"templates/editable-canvas-receipt.template.json",lambda d:d.update(version="2.14.9"));self.rejected(root,"Penpot version")

if __name__=="__main__":unittest.main()
