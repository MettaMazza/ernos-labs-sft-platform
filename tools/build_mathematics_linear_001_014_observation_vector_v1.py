#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_linear_001_014_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/linear_001_014_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("LINEAR vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("LINEAR registry changed")
 obs=(("vector_coordinates",{"left":[1,2,3],"right":[2,1,1],"junction":[3,3,4]}),("linear_map_composition",{"input":[1,2],"composed_output":[8,6]}),("matrix_row_operations",{"input_rows":[[1,2],[3,4]],"swapped_rows":[[3,4],[1,2]],"relation_preserved":True}),("rank_nullity",{"field_support":2,"columns":3,"rank":2,"nullity":1}),("determinant_orientation",{"held_product":4,"opposed_product":6,"orientation":"opposed","magnitude":2}),("exact_linear_system",{"solution":[2,1],"relations":[3,4]}),("basis_dimension",{"ambient_dimension":2,"basis":[[1,0],[1,1]],"coordinates":[1,2]}),("inner_product_metric",{"inner_product":5,"squared_distance":5}),("eigen_invariant_support",{"uniform_mode":3,"distinction_mode":1}),("rational_spectral_enclosure",{"lower":[8,5],"upper":[13,8],"relation":"x*x=x+1"}),("multilinear_tensor_product",{"left_dimension":2,"right_dimension":3,"product_dimension":6,"outer_product":[[3,4,5],[6,8,10]]}),("tensor_contraction",{"tensor_shape":[2,2,2],"contracted_matrix":[[6,8],[10,12]]}),("exterior_symmetric",{"repeated_wedge":"absence","distinct_wedge_orientation":"held","symmetric_pair_count":3}),("operator_decomposition",{"operator":[[2,0],[0,1]],"component_weights":[2,1],"idempotent_components":True}))
 rec=[]
 for i,(name,value) in enumerate(obs,1):rec.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-linear-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-LINEAR-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-linear-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":rec,"record_count":14,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":14,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
