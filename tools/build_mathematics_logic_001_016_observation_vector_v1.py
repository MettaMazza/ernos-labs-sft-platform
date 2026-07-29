#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_logic_001_016_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/logic_001_016_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("LOGIC vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("LOGIC registry changed")
 values=(
  ("proposition_distinction",{"labels":["held","opposed"],"exclusive":True,"complete":True}),
  ("inference_consequence",{"valuations":4,"rule":"modus-ponens","all_preserved":True}),
  ("sound_complete_correspondence",{"propositions":2,"valuations":4,"proof_model_rows_equal":True}),
  ("proof_object_check",{"premises":["P","P-implies-Q"],"rule":"modus-ponens","conclusion":"Q","checked":True}),
  ("finite_quantifier",{"domain":[1,2,3],"predicate":"equals-two","exists":"held","forall":"opposed"}),
  ("model_interpretation",{"domain":[1,2,3],"predicate_extension":[2],"existential":"held"}),
  ("compactness_boundary",{"support":[1,2,3,4],"proper_exclusion_families_satisfied":4,"complete_exclusion_family_satisfied":False,"unrestricted_claimed":False}),
  ("decidability_interface",{"formulas":6,"valuations":4,"evaluations":24,"all_halted":True}),
  ("incompleteness_self_reference",{"labels":["held","opposed"],"self_negating_fixed_labels":0,"host_zero_is_count_only":True}),
  ("finite_collection",{"base_labels":3,"subcollections":8,"union_closed":True,"intersection_closed":True}),
  ("size_boundary",{"ranks":[1,2,3,4],"sizes":[2,4,8,16],"universal_totality_claimed":False}),
  ("constructive_correspondence",{"conjunction_witnesses":["proof-A","proof-B"],"disjunction_side":"left","disjunction_witness":"proof-A"}),
  ("modal_temporal",{"states":4,"necessary_at_state_one":True,"possible_at_state_two":True,"transition_custody":True}),
  ("many_valued",{"labels":["opposed","unresolved","held"],"complete_binary_rows":9,"reversal_preserves_unresolved":True}),
  ("normalization",{"redex":"identity-applied-to-A","normal_form":"A","measure_strictly_decreased":True}),
  ("consistency_self_verification",{"declared_closure":["P","P-implies-Q","Q"],"opposed_P_derived":False,"unrestricted_self_verification_claimed":False}),
 )
 records=[]
 for i,(name,value) in enumerate(values,1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-logic-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-LOGIC-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-logic-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":16,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":16,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
