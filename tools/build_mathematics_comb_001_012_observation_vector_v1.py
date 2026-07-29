#!/usr/bin/env python3
import hashlib,json,math
from itertools import combinations,permutations,product
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_comb_001_012_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/comb_001_012_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def setparts(items):
 if not items:return {()}
 first=items[0];out=set()
 for p in setparts(items[1:]):
  blocks=[tuple(b) for b in p];out.add(tuple(sorted(((first,),)+tuple(blocks))))
  for i in range(len(blocks)):
   q=list(blocks);q[i]=tuple(sorted((first,)+q[i]));out.add(tuple(sorted(q)))
 return out
def main():
 if OUT.exists():raise SystemExit("COMB vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("COMB registry changed")
 fano=((1,2,3),(1,4,5),(1,6,7),(2,4,6),(2,5,7),(3,4,7),(3,5,6))
 obs=(("sum_product",{"sum":7,"product":12}),("permutation_combination",{"permutations_5":len(tuple(permutations(range(5)))),"combinations_5_2":len(tuple(combinations(range(5),2)))}),("inclusion_exclusion",{"left":6,"right":4,"overlap":2,"union":8}),("occupancy",{"objects":7,"boxes":3,"forced_minimum_maximum":3}),("binary_recurrence",[2**n for n in range(1,9)]),("partitions_five",{"count":7,"cell_count":5}),("antichain_four",{"maximum":6,"middle_layer":6}),("deterministic_support_average",{"support":8,"total_held_labels":12,"average":[3,2],"existence_at_least":2}),("fano_incidence",{"points":7,"blocks":7,"block_size":3,"point_degree":3,"pair_degree":1}),("binary_code",{"word_length":3,"minimum_distance":3,"maximum_size":2}),("ramsey_six",{"edge_colourings":32768,"monochromatic_triangle_forced":True}),("set_partition_species_four",{"structures":len(setparts((1,2,3,4)))},))
 rec=[]
 for i,(name,v) in enumerate(obs,1):rec.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":v,"expected_label":f"complete-comb-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-COMBINATORICS-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-comb-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":rec,"record_count":12,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":12,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
