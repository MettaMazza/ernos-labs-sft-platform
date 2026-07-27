#!/usr/bin/env python3
from dataclasses import asdict
import importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sft.chemistry.insertion_elimination_pathway_batch_v1 import INSERTION_ELIMINATION_PATHWAY_SPEC,PRIMARY_PATH  # noqa:E402
from sft.chemistry.insertion_elimination_pathway_validation_v1 import _source_rows,exact_analysis  # noqa:E402
from sft.engine import EngineRepository  # noqa:E402
def w(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
def load():
 p=ROOT/"claims"/INSERTION_ELIMINATION_PATHWAY_SPEC.claim_id/"execution.py";s=importlib.util.spec_from_file_location("i13",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.build_execution(ROOT)
def main():
 spec=INSERTION_ELIMINATION_PATHWAY_SPEC;cp=ROOT/"census/claims.json"
 if spec.claim_id in {x["claim_id"] for x in json.loads(cp.read_text())["claims"]}:raise SystemExit("claim already admitted; immutable receipt preserved")
 e=load();cap={}
 class I:
  def validate(self,s):cap["s"]=s;cap["i"]=e.independent_validator.validate(s);return cap["i"]
 class E:
  def validate(self,s):cap["e"]=e.empirical_validator.validate(s);return cap["e"]
 r=EngineRepository(ROOT).execute_official(e.program,I(),e.source_files,E())
 if not r.model_admitted:raise SystemExit(f"claim halted at {r.halted_stage}; preserved receipt {r.receipt_hash}")
 s,i,ev=cap["s"],cap["i"],cap["e"];mp=ROOT/"census/execution_manifest.json";m=json.loads(mp.read_text());m["claims"].append({"claim_id":spec.claim_id,"execution_file":f"claims/{spec.claim_id}/execution.py"});w(mp,m);row=next(x for x in json.loads(cp.read_text())["claims"] if x["claim_id"]==spec.claim_id);pkg=ROOT/"claims"/spec.claim_id;a=exact_analysis(_source_rows(ROOT),json.loads((ROOT/PRIMARY_PATH).read_text()))
 payloads={"candidate_census.json":{"claim_id":spec.claim_id,**asdict(s.census)},"elimination_receipt.json":{"claim_id":spec.claim_id,"decisions":asdict(s)["decisions"],"closure":asdict(s.closure)},"controls.json":{"claim_id":spec.claim_id,"controls":asdict(s)["controls"]},"empirical_validation.json":{"claim_id":spec.claim_id,**asdict(ev)},"certificate.json":{"claim_id":spec.claim_id,"chemistry_obligation":"SFT-CHEM-OBL-INORG-013","status":"model_admitted_forward_forced_empirically_tested_and_independently_replicated","source_manifest_hash":e.program.registration.source_hash,"derivation_seal_hash":s.seal_hash,"independent_implementation_hash":i.implementation_hash,"independent_certificate_hash":i.certificate_hash,"external_validation_hash":r.external_validation_hash,"empirical_validation_hash":r.empirical_validation_hash,"measurement_receipt_hash":ev.measurement_receipt_hash,"engine_receipt_hash":r.receipt_hash,"engine_receipt_path":row["receipt_path"],"closure_scope":r.closure_status,"exact_result":spec.exact_result,"candidate_count":len(s.census.candidates),"unique_survivor_count":sum(x.survives for x in s.decisions),"insertion_adjacency_count_vector":[a["insertion_before_count"],a["insertion_after_count"],a["insertion_removed_count"],a["insertion_added_count"]],"extrusion_exactly_restores_source":a["extrusion_restores_source"],"migratory_composition":a["migratory_composition"],"distinct_eliminand_removed_count":a["distinct_eliminand_removed_count"],"single_centre_carrier_count":a["single_centre_carrier_count"],"complete_registered_external_surface_count":a["complete_target_count"],"complete_source_count":a["complete_source_count"],"scope_distinction_count":a["scope_distinction_count"],"rendered_structure_absence_count":a["rendered_structure_absence_count"],"complete_target_vector_hash":a["complete_target_vector_hash"],"source_recapture_count":a["source_recapture_count"],"all_external_rows_preserved":ev.all_rows_preserved,"numerical_zero_negative_irrational_imaginary_signed_continuum_fitted_free_or_imported_parameter_used":False,"observed_product_named_mechanism_or_fit_used_to_select_survivor":False,"falsification_condition":ev.falsification_condition}}
 for n,x in payloads.items():w(pkg/n,x)
 reg=json.loads((pkg/"registration.json").read_text());reg["status"]="empirically_tested";reg["candidate_grammar"]["completeness_certificate"]=s.census.completeness_certificate_hash;w(pkg/"registration.json",reg);ep=ROOT/"experiments/chemistry"/spec.experiment_id/"registration.json";ex=json.loads(ep.read_text());ex["status"]="measured";w(ep,ex);(pkg/"STATUS.md").write_text(f"# {spec.claim_id}\n\nStatus: `model_admitted_forward_forced_empirically_tested_and_independently_replicated`\n\n- Chemistry obligation: `SFT-CHEM-OBL-INORG-013`\n- Insertion counts: `(1,2,1,2)`; extrusion exact inverse; migration plus insertion retained.\n- External vector: ten rows from three IUPAC records, including scope and absence rows.\n- Derivation seal: `{s.seal_hash}`\n- Engine receipt: `{r.receipt_hash}`\n",encoding="utf-8");print(f"admitted {spec.claim_id}: {r.receipt_hash}");print(f"derivation seal: {s.seal_hash}");print(f"candidates: {len(s.census.candidates)}; survivors: {sum(x.survives for x in s.decisions)}")
if __name__=="__main__":main()
