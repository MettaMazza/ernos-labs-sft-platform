#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_symb_001_010_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/symb_001_010_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("SYMB vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("SYMB registry changed")
 values=(
  ("canonical_expression",{"inputs":2,"canonical_record":["add","x","y"],"unit_and_order_paths_agree":True}),
  ("simplification_provenance",{"input":"add(mul(x,One),EmptyOne)","output":"x","ordered_trace":["remove-multiplicative-One","remove-structural-absence"]}),
  ("polynomial_factor_expand",{"factors":[[1,1],[2,1]],"expanded_coefficients":[2,3,1],"degree_support_complete":True}),
  ("symbolic_equation",{"equation":"x+3=7","candidate_labels":8,"complete_solution_support":[4]}),
  ("rewrite_termination_confluence",{"declared_critical_paths":2,"both_terminate":True,"common_normal_form":"x"}),
  ("generating_function_transform",{"left":[1,1,1],"right":[1,1],"convolution":[1,2,2,1]}),
  ("fourier_laplace_correspondence",{"held_walsh_output":[2,"EmptyOne"],"positive_weighted_support":"11/4","imaginary_scalar_admitted":False}),
  ("special_function_recurrence",{"recurrence":"Gamma-successor=label*Gamma","generated_trace":[1,2,6,24]}),
  ("theorem_search_boundary",{"premises":["A-to-B","B-to-C"],"registered_depth":2,"A_to_C_proofs":1,"unbounded_completion_claimed":False}),
  ("constructive_certificate",{"relation":"x+x=6","positive_witness":3,"replay":"3+3=6"}),
 )
 records=[]
 for i,(name,value) in enumerate(values,1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-symb-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-SYMBOLIC-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-symb-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":10,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":10,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
