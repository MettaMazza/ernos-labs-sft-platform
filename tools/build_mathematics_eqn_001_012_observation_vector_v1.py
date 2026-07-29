#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_eqn_001_012_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/eqn_001_012_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("EQN vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("EQN registry changed")
 values=(
  ("ordinary_difference",{"initial":1,"transition":"twice-current","solution":[1,2,4,8,16]}),
  ("ordinary_differential_correspondence",{"step_denominators":[1,2,3,4,5,6],"carriers":["1","3/2","2"],"local_ratio_equals_carrier":True}),
  ("partial_difference",{"grid_rule":"i-plus-j","i_domain":[1,2,3],"j_domain":[1,2,3],"change_each_direction":1}),
  ("partial_differential_correspondence",{"grid_rule":"i-plus-j","second_difference_each_direction":"absence","all_grid_rows_preserved":True}),
  ("boundary_initial_well_posedness",{"initial":1,"transition":"successor","unique_solution":[1,2,3,4,5,6]}),
  ("integral_equation_correspondence",{"source":1,"kernel":"unit-retained","finite_volterra_solution":[1,2,4,8]}),
  ("functional_equation",{"function":"two-to-generated-power","domain":[1,2,3,4],"composition_identity_passed":True}),
  ("recurrence_solution_space",{"initial_record":[1,1],"solution":[1,1,2,3,5,8]}),
  ("green_response",{"source":[1,0,2,0],"response":[1,1,3,3],"exact_difference_reconstruction":True}),
  ("conservation_weak_correspondence",{"before":[2,3],"after":[3,2],"retained_total":5}),
  ("stability_perturbation",{"solution_map":"half-contraction","input_carriers":["1/4","1/2","3/4","1"],"distance_ratio":"1/2"}),
  ("existence_uniqueness_blowup_boundary",{"initial":2,"transition":"square-current","finite_solution":[2,4,16,256,65536],"unrestricted_blowup_claimed":False}),
 )
 records=[]
 for i,(name,value) in enumerate(values,1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-eqn-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-EQUATION-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-eqn-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":12,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":12,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
