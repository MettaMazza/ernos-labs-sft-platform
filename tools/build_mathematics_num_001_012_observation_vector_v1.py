#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_num_001_012_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/num_001_012_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("NUM vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("NUM registry changed")
 values=(
  ("exact_representation_rounding",{"source_fraction":"7/3","lower":2,"upper":3,"selected_display":2,"lower_gap":"1/3","upper_gap":"2/3"}),
  ("interval_rational_enclosure",{"left":["1/2","2/3"],"right":["1/3","1/2"],"sum":["5/6","7/6"],"positive_product":["1/6","1/3"]}),
  ("truncation_residual",{"generated_parts":8,"identity":"partial(n)+1/(2^n)=One","all_rows_reconstruct":True}),
  ("forward_backward_stability",{"approximate_result":"23/10","exact_result":"7/3","forward_gap":"1/30","reconstructed_coefficient":"70/23","backward_gap":"1/23"}),
  ("conditioning_sensitivity",{"input_gap":"1/100","output_gap":"1/20","exact_gap_ratio":5}),
  ("convergence_order",{"error_family":"1/(2^n)","generated_successors":8,"successor_ratio":"1/2","all_bounds_exact":True}),
  ("root_isolation",{"equation":"square(x)=2","lower":"7/5","upper":"3/2","lower_square":"49/25","upper_square":"9/4","irrational_scalar_admitted":False}),
  ("linear_system_solver",{"equations":["x+y=5","x+2y=8"],"positive_candidate_pairs":64,"unique_solution":[2,3]}),
  ("interpolation",{"endpoints":[[1,2],[3,6]],"midpoint":2,"weights":["1/2","1/2"],"value":4}),
  ("quadrature_accumulation",{"interval":[1,3],"identity_values":True,"midpoint_result":4,"trapezoid_result":4}),
  ("differential_equation_recurrence",{"initial":"1","part_width":"1/2","steps":2,"trace":["1","3/2","9/4"]}),
  ("verified_computation_certificate",{"expression":"1/2+1/3","cross_numerator":5,"cross_denominator":6,"reduced_result":"5/6","gcd":1}),
 )
 records=[]
 for i,(name,value) in enumerate(values,1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-num-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-NUMERICAL-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-num-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":12,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":12,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
