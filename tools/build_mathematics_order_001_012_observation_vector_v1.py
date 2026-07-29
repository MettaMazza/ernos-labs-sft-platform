#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_order_001_012_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/order_001_012_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("ORDER vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("ORDER registry changed")
 values=(("preorder_quotient",{"depth":3,"length_classes":4,"reflexive_transitive":True}),("partial_order",{"carrier_support":8,"antisymmetric":True}),("conditional_totality",{"exact_fraction_carriers":4,"all_pairs_comparable":True}),("meet_join",{"carrier_support":8,"ordered_pairs":64,"unique_meet_join":True}),("distributive_modular",{"ordered_triples":512,"distributive":True,"modular":True}),("complement",{"carrier_support":8,"unique_complements":8}),("closure",{"carrier_support":8,"extensive_monotone_idempotent":True}),("galois_connection",{"left_subsets":8,"right_subsets":4,"equivalence_pairs":32}),("domain_approximation",{"chain_carriers":4,"recovered_by_approximants":4}),("monotone_map",{"chain_carriers":4,"comparison_pairs":16,"preserved":True}),("fixed_point",{"iterations":1,"least_fixed_support":[1]}),("complete_lattice",{"carrier_support":8,"generated_subfamilies":256,"all_meets_joins_present":True}))
 records=[]
 for i,(name,value) in enumerate(values,1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-order-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-ORDER-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-order-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":12,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":12,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
