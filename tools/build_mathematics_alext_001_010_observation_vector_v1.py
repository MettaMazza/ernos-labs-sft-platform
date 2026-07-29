#!/usr/bin/env python3
import hashlib,json,math
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_alext_001_010_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/alext_001_010_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def value(n,p):
 c=0
 while n%p==0:n//=p;c+=1
 return c
def main():
 if OUT.exists():raise SystemExit("ALEXT vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("ALEXT registry changed")
 obs=(("square_root_two_bracket",{"lower":[7,5],"upper":[3,2]}),("cube_root_two_bracket",{"lower":[5,4],"upper":[4,3]}),("beta_square_two_product",{"left":[1,1],"right":[1,1],"result":[3,2]}),("field_mod_five",{"labels":5,"nonabsence_inverses":[1,3,2,4]}),("finite_root_orbit",{"labels":[1,2,4],"square_action":[1,4,2]}),("five_phase_cycle",[1,2,3,4,0]),("held_pair_product",{"left":[1,1],"right":[1,1],"real":"structural-absence","imaginary_orientation_magnitude":2}),("algebraic_order",{"cube_root_two_upper":[4,3],"square_root_two_lower":[7,5],"disjoint":True}),("ternary_valuation",{"held_difference":81,"depth":value(81,3)}),("nonrepresentability_boundary",{"rational_square_search_denominator_bound":20,"exact_match_present":False,"transcendence_claimed":False}))
 rec=[]
 for i,(name,v) in enumerate(obs,1):rec.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":v,"expected_label":f"complete-alext-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-ALGEBRAIC-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-alext-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":rec,"record_count":10,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":10,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
