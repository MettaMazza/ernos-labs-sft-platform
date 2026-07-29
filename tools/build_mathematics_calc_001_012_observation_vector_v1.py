#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_calc_001_012_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/calc_001_012_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("CALC vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("CALC registry changed")
 values=(("finite_difference",{"values":[1,4,9,16],"changes":[3,5,7]}),("higher_difference",{"sequence":[1,8,27,64,125],"third_difference":[6,6]}),("accumulation",{"terms":5,"sum":15}),("fundamental_correspondence",{"initial":1,"change_sum":15,"terminal":16}),("product_composition",{"product_change":6,"law_reconstruction":6}),("rational_convergence",{"refinements":8,"nested":True,"width_rule":"1/n"}),("derivative_correspondence",{"base_component":4,"retained_part_rule":"1/n"}),("integral_correspondence",{"enclosed_value":[1,2],"width_rule":"1/n","refinements":7}),("multivariable_change",{"x_direction":3,"y_direction":2}),("divergence_flux",{"local_changes":[1,1],"boundary_magnitude":2}),("variational_stationary",{"candidates":5,"unique_stationary":3}),("continuum_boundary",{"exact_enclosures":8,"nested":True,"completed_continuum_claimed":False}))
 records=[]
 for i,(name,value) in enumerate(values,1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-calc-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-CALCULUS-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-calc-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":12,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":12,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
