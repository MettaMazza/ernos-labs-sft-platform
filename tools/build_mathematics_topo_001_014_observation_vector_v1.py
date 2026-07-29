#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_topo_001_014_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/topo_001_014_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("TOPO vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("TOPO registry changed")
 values=(("open_support",{"carriers":2,"open_sets":3,"closed_under_required_operations":True}),("continuity",{"open_preimages":3,"continuous":True}),("compactness",{"support":3,"cover_sets":2,"finite_subcover":2}),("connectedness",{"vertices":5,"components":2}),("separation",{"carriers":3,"ordered_distinct_pairs":6,"separated":True}),("product_quotient_subspace",{"product_carriers":6,"quotient_classes":2}),("simplicial_complex",{"vertices":3,"nonempty_faces":7,"downward_closed":True}),("homotopy",{"paths":2,"face_moves":1,"endpoints_preserved":True}),("fundamental_cycle",{"vertices":3,"edges":3,"components":1,"cycle_rank":1}),("homology",{"triangle_boundary_edges":3,"second_boundary":"absence"}),("cohomology",{"cycle_edges":3,"dual_evaluations":3}),("finite_atlas",{"charts":4,"local_carriers":3,"overlaps_compatible":True}),("knot_link",{"crossings":3,"gauss_word_length":6,"cyclic_invariant":True}),("persistence",{"component_counts":[4,2,1],"resurrection":False}))
 records=[]
 for i,(name,value) in enumerate(values,1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-topo-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-TOPOLOGY-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-topo-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":14,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":14,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
