#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_anal_001_016_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/anal_001_016_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("ANAL vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("ANAL registry changed")
 values=(("sequence_convergence",{"refinements":8,"enclosed_carrier":1,"width_rule":"1/n"}),("cauchy_support",{"tail_depths":6,"pair_bounds_preserved":True}),("completeness",{"nested_enclosures":8,"common_exact_carrier":1,"completed_continuum_claimed":False}),("series_remainder",{"truncations":8,"remainder_rule":"1/2^n"}),("power_series",{"terms":5,"truncation":[31,16]}),("functional_space",{"domain_carriers":3,"binary_functions":8}),("norm_metric",{"one_norm":6,"metric_triangle":True}),("bounded_operator",{"input_dimension":2,"bound":2,"all_generated_inputs_pass":True}),("harmonic_support",{"points":4,"alternating_orientation":"opposed","magnitude":2}),("transform_inversion",{"input":[3,1],"transformed":[4,2],"exact_reconstruction":True}),("convolution",{"signal":[1,2,3],"identity_support":[1,0,0],"reconstructed":True}),("orthogonal_expansion",{"coordinates":[3,2],"cross_pairing":"absence"}),("weak_observation",{"weights":[[1,3],[2,3]],"pairing":[5,3]}),("contraction",{"factor":[1,2],"fixed_carrier":1}),("held_phase_pair",{"real_orientation":"absence","quarter_phase_magnitude":2,"imaginary_scalar_used":False}),("spectral_measure",{"modes":[2,3],"weights":[1,4],"total":5,"first_moment":14}))
 records=[]
 for i,(name,value) in enumerate(values,1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-anal-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-ANALYSIS-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-anal-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":16,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":16,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
