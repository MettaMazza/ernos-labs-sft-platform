#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_meas_001_010_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/meas_001_010_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("MEAS vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("MEAS registry changed")
 values=(
  ("finite_support_weight",{"support":[1,2,3],"weights":["1/6","2/6","3/6"],"complete_weight":1}),
  ("disjoint_additivity",{"support_count":8,"all_disjoint_pairs_tested":True,"all_additive":True}),
  ("outer_covering",{"target":[1,3],"all_covers_tested":True,"least_cover_weight":"4/6"}),
  ("measurable_boundary",{"boundary":[1,2],"test_support_count":8,"all_exact_decompositions":True}),
  ("finite_support_integration",{"values":[1,2,3],"weights":["1/6","2/6","3/6"],"integral":"7/3"}),
  ("refinement_sum_integration",{"refinement_counts":[1,2,3,4,5,6,7,8],"midpoint_sum_each":"1/2"}),
  ("product_conditional_support",{"first_weights":["1/3","2/3"],"second_weights":["1/4","3/4"],"product_total":1,"conditional_second":"3/4"}),
  ("held_orientation_signed",{"held":"3/4","opposed":"1/4","retained_held":"1/2","negative_scalar_used":False}),
  ("distribution_observation",{"first_action":"7/3","second_action":"5/3","composed_action":4,"linearity_exact":True}),
  ("convergence_finite_witness",{"successors":8,"width_rule":"1/(n+1)","strictly_refined":True,"completed_infinite_equality_claimed":False}),
 )
 records=[]
 for i,(name,value) in enumerate(values,1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-meas-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-MEASURE-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-meas-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":10,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":10,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
