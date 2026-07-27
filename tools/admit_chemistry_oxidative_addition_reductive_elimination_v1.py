#!/usr/bin/env python3
from dataclasses import asdict
import importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sft.chemistry.oxidative_addition_reductive_elimination_batch_v1 import OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC,PRIMARY_PATH  # noqa:E402
from sft.chemistry.oxidative_addition_reductive_elimination_validation_v1 import _source_rows,exact_analysis  # noqa:E402
from sft.engine import EngineRepository  # noqa:E402
def write_json(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
def load_execution():
 p=ROOT/"claims"/OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC.claim_id/"execution.py";s=importlib.util.spec_from_file_location("i12",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.build_execution(ROOT)
def main():
 spec=OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC;cpath=ROOT/"census/claims.json"
 if spec.claim_id in {x["claim_id"] for x in json.loads(cpath.read_text())["claims"]}:raise SystemExit("claim already admitted; immutable receipt preserved")
 e=load_execution();cap={}
 class I:
  def validate(self,s):cap["s"]=s;cap["i"]=e.independent_validator.validate(s);return cap["i"]
 class E:
  def validate(self,s):cap["e"]=e.empirical_validator.validate(s);return cap["e"]
 r=EngineRepository(ROOT).execute_official(e.program,I(),e.source_files,E())
 if not r.model_admitted:raise SystemExit(f"claim halted at {r.halted_stage}; preserved receipt {r.receipt_hash}")
 s,i,ev=cap["s"],cap["i"],cap["e"];mp=ROOT/"census/execution_manifest.json";m=json.loads(mp.read_text());m["claims"].append({"claim_id":spec.claim_id,"execution_file":f"claims/{spec.claim_id}/execution.py"});write_json(mp,m);crow=next(x for x in json.loads(cpath.read_text())["claims"] if x["claim_id"]==spec.claim_id);pkg=ROOT/"claims"/spec.claim_id;a=exact_analysis(_source_rows(ROOT),json.loads((ROOT/PRIMARY_PATH).read_text()))
 payloads={"candidate_census.json":{"claim_id":spec.claim_id,**asdict(s.census)},"elimination_receipt.json":{"claim_id":spec.claim_id,"decisions":asdict(s)["decisions"],"closure":asdict(s.closure)},"controls.json":{"claim_id":spec.claim_id,"controls":asdict(s)["controls"]},"empirical_validation.json":{"claim_id":spec.claim_id,**asdict(ev)},"certificate.json":{"claim_id":spec.claim_id,"chemistry_obligation":"SFT-CHEM-OBL-INORG-012","status":"model_admitted_forward_forced_empirically_tested_and_independently_replicated","source_manifest_hash":e.program.registration.source_hash,"derivation_seal_hash":s.seal_hash,"independent_implementation_hash":i.implementation_hash,"independent_certificate_hash":i.certificate_hash,"external_validation_hash":r.external_validation_hash,"empirical_validation_hash":r.empirical_validation_hash,"measurement_receipt_hash":ev.measurement_receipt_hash,"engine_receipt_hash":r.receipt_hash,"engine_receipt_path":crow["receipt_path"],"closure_scope":r.closure_status,"exact_result":spec.exact_result,"candidate_count":len(s.census.candidates),"unique_survivor_count":sum(x.survives for x in s.decisions),"single_metal_transfer_distribution":a["single_distribution"],"two_metal_transfer_distribution":a["split_distribution"],"conserved_carrier_count":a["carrier_count"],"product_incidence_count":a["product_incidence_count"],"reductive_elimination_exactly_restores_source":a["reverse_restores_source"],"complete_registered_external_surface_count":a["complete_target_count"],"complete_source_count":a["complete_source_count"],"scope_distinction_count":a["scope_distinction_count"],"complete_target_vector_hash":a["complete_target_vector_hash"],"source_recapture_count":a["source_recapture_count"],"all_external_rows_preserved":ev.all_rows_preserved,"numerical_zero_negative_irrational_imaginary_signed_continuum_fitted_free_or_imported_parameter_used":False,"signed_oxidation_formal_charge_observed_mechanism_or_fit_used_to_select_survivor":False,"falsification_condition":ev.falsification_condition}}
 for n,x in payloads.items():write_json(pkg/n,x)
 reg=json.loads((pkg/"registration.json").read_text());reg["status"]="empirically_tested";reg["candidate_grammar"]["completeness_certificate"]=s.census.completeness_certificate_hash;write_json(pkg/"registration.json",reg);ep=ROOT/"experiments/chemistry"/spec.experiment_id/"registration.json";ex=json.loads(ep.read_text());ex["status"]="measured";write_json(ep,ex)
 (pkg/"STATUS.md").write_text(f"# {spec.claim_id}\n\nStatus: `model_admitted_forward_forced_empirically_tested_and_independently_replicated`\n\n- Chemistry obligation: `SFT-CHEM-OBL-INORG-012`\n- Transfer partitions: `(2)` and `(1,1)`; reductive elimination is the exact inverse.\n- External vector: five rows from two complete IUPAC records.\n- Derivation seal: `{s.seal_hash}`\n- Engine receipt: `{r.receipt_hash}`\n",encoding="utf-8");print(f"admitted {spec.claim_id}: {r.receipt_hash}");print(f"derivation seal: {s.seal_hash}");print(f"candidates: {len(s.census.candidates)}; survivors: {sum(x.survives for x in s.decisions)}")
if __name__=="__main__":main()
