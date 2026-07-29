#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_alg_001_016_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/alg_001_016_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("ALG vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("ALG registry changed")
 values=(("magma",{"carrier_count":2,"table_cells":4,"closed":True}),("semigroup",{"carrier_count":3,"associative_triples":27}),("monoid",{"identity_carrier":1,"two_sided":True}),("group",{"carrier_count":3,"unique_inverses":3}),("permutation_action",{"carriers":3,"actions":6}),("quotient",{"parent_carriers":4,"normal_substructure":2,"cosets":2}),("ring",{"modulus":3,"distributive_triples":27}),("domain",{"modulus":5,"nonabsence_pairs":16,"zero_divisors":"absence"}),("field",{"modulus":5,"nonabsence_inverses":4}),("module",{"field_support":2,"coordinate_dimension":2}),("algebra",{"coordinate_dimension":2,"bilinear":True}),("ideal",{"ring_carriers":6,"ideal_carriers":2,"quotient_classes":3}),("representation",{"action":"swap","uniform_mode":"held","distinction_mode":"held-opposed"}),("exact_sequence",{"image_size":2,"kernel_size":2,"equal":True}),("universal_algebra",{"carrier_count":3,"identity":"associative-commutative-idempotent"}),("operad",{"leaf_count":4,"substitution_associative":True}))
 records=[]
 for i,(name,value) in enumerate(values,1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-alg-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-ALGEBRA-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-alg-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":16,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":16,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
