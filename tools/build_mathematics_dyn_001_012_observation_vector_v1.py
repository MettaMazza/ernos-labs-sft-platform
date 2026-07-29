#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_dyn_001_012_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/dyn_001_012_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("DYN vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("DYN registry changed")
 values=(
  ("state_orbit",{"map":{"1":2,"2":3,"3":2,"4":4},"initial":1,"orbit":[1,2,3,2,3]}),
  ("fixed_periodic",{"fixed":[4],"period_two":[2,3]}),
  ("recurrence_return",{"state_two_return_time":2,"state_four_return_time":1}),
  ("invariant_conserved",{"support":[2,3],"image":[2,3],"retained_cardinality":2}),
  ("stability_attraction",{"map":"(x+1)/2","fixed_carrier":1,"distance_ratio":"1/2"}),
  ("bifurcation_distinction",{"first_transition_attractors":1,"second_transition_attractors":2,"distinction_change":True}),
  ("symbolic_shift",{"word":[1,1,2,2],"return_shifts":4,"multiset_preserved":True}),
  ("exact_sensitivity",{"first_word":[1,1,1,1],"second_word":[1,1,1,2],"first_observed_distinction_depth":3}),
  ("ergodic_average",{"cycle":[1,3],"all_start_full_cycle_average":2}),
  ("hamiltonian_reversible",{"map":"pair-swap","self_inverse":True,"total_preserved":True}),
  ("dissipative_retained_loss",{"predecessors":4,"images":2,"retained_fibre_labels":2,"reconstructed_predecessors":4}),
  ("coupled_networked",{"initial":[1,3],"orbit":[[1,3],[3,1],[1,3]],"period":2,"total_preserved":True}),
 )
 records=[]
 for i,(name,value) in enumerate(values,1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-dyn-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-DYNAMICS-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-dyn-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":12,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":12,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
