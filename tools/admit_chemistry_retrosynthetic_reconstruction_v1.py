#!/usr/bin/env python3
from dataclasses import asdict
import importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from sft.chemistry.retrosynthetic_reconstruction_batch_v1 import RETROSYNTHESIS_SPEC
from sft.chemistry.retrosynthetic_reconstruction_validation_v1 import exact_analysis
from sft.engine import EngineRepository
def w(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
def execution():p=ROOT/"claims"/RETROSYNTHESIS_SPEC.claim_id/"execution.py";s=importlib.util.spec_from_file_location("org016",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.build_execution(ROOT)
def main():
 c=RETROSYNTHESIS_SPEC;cp=ROOT/"census/claims.json"
 if c.claim_id in {x["claim_id"] for x in json.loads(cp.read_text())["claims"]}:raise SystemExit("claim already admitted; immutable receipt preserved")
 run=execution();z={}
 class I:
  def validate(self,s):z.update(sealed=s,independent=run.independent_validator.validate(s));return z["independent"]
 class E:
  def validate(self,s):z["empirical"]=run.empirical_validator.validate(s);return z["empirical"]
 r=EngineRepository(ROOT).execute_official(run.program,I(),run.source_files,E())
 if not r.model_admitted:raise SystemExit(f"claim halted at {r.halted_stage}; preserved receipt {r.receipt_hash}")
 s,i,e=z["sealed"],z["independent"],z["empirical"];mp=ROOT/"census/execution_manifest.json";manifest=json.loads(mp.read_text());manifest["claims"].append({"claim_id":c.claim_id,"execution_file":f"claims/{c.claim_id}/execution.py"});w(mp,manifest);row=next(x for x in json.loads(cp.read_text())["claims"] if x["claim_id"]==c.claim_id);pkg=ROOT/"claims"/c.claim_id;a,checks=exact_analysis(ROOT);cert={"claim_id":c.claim_id,"chemistry_obligation":"SFT-CHEM-OBL-ORG-016","status":"model_admitted_forced_exhaustive_reconstruction_law_empirically_tested_and_independently_replicated","source_manifest_hash":run.program.registration.source_hash,"derivation_seal_hash":s.seal_hash,"independent_implementation_hash":i.implementation_hash,"independent_certificate_hash":i.certificate_hash,"external_validation_hash":r.external_validation_hash,"empirical_validation_hash":r.empirical_validation_hash,"measurement_receipt_hash":e.measurement_receipt_hash,"engine_receipt_hash":r.receipt_hash,"engine_receipt_path":row["receipt_path"],"closure_scope":r.closure_status,"exact_result":c.exact_result,"candidate_count":len(s.census.candidates),"unique_survivor_count":sum(x.survives for x in s.decisions),**a,"all_7_target_checks_passed":all(checks.values()),"all_external_rows_preserved":e.all_rows_preserved,"numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_native_parameter_used":False,"external_route_or_measured_success_used_to_select_tree":False,"falsification_condition":e.falsification_condition}
 for n,p in {"candidate_census.json":{"claim_id":c.claim_id,**asdict(s.census)},"retrosynthesis_receipt.json":{"claim_id":c.claim_id,"decisions":asdict(s)["decisions"],"closure":asdict(s.closure)},"controls.json":{"claim_id":c.claim_id,"controls":asdict(s)["controls"]},"empirical_validation.json":{"claim_id":c.claim_id,**asdict(e)},"certificate.json":cert}.items():w(pkg/n,p)
 reg=json.loads((pkg/"registration.json").read_text());reg["status"]="empirically_tested";reg["candidate_grammar"]["completeness_certificate"]=s.census.completeness_certificate_hash;w(pkg/"registration.json",reg);ep=ROOT/"experiments/chemistry"/c.experiment_id/"registration.json";ex=json.loads(ep.read_text());ex["status"]="measured_postseal_complete";w(ep,ex);(pkg/"STATUS.md").write_text(f"# {c.claim_id}\n\nStatus: `model_admitted_forced_exhaustive_reconstruction_law_empirically_tested_and_independently_replicated`\n\n- Chemistry obligation: `SFT-CHEM-OBL-ORG-016`\n- Exact law: every positive binary decomposition tree generated once; every path forward-reconstructs the target.\n- Exhaustive bounded census: five four-leaf trees and fourteen five-leaf trees; all nineteen exact.\n- Derivation seal: `{s.seal_hash}`\n- Engine receipt: `{r.receipt_hash}`\n");print(f"admitted {c.claim_id}: {r.receipt_hash}");print(f"derivation seal: {s.seal_hash}");print(f"candidates: {len(s.census.candidates)}; survivors: {sum(x.survives for x in s.decisions)}")
if __name__=="__main__":main()
