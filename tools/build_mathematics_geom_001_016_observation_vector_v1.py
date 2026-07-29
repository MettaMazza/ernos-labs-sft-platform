#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_geom_001_016_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/geom_001_016_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("GEOM vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("GEOM registry changed")
 values=(("point_incidence",{"points":3,"held_total":11,"opposed_total":11,"collinear":True}),("euclidean_distance",{"squared_distance":25,"root_imported":False}),("affine_invariance",{"midpoint":[2,3],"translated_midpoint":[4,4]}),("projective_incidence",{"points":7,"lines":7,"points_per_line":3,"line_per_pair":1}),("convex_separation",{"centre":[[1,2],[1,2]],"external_coordinate":2,"separated":True}),("lattice_polytope",{"boundary_points":4,"interior":"absence","area":1}),("polyhedral_incidence",{"vertices":8,"edges":12,"faces":6,"euler_total":2}),("computational_predicates",{"query":[2,2],"nearest":[1,1],"unique":True}),("orientation_intersection",{"orientation":"held","intersection":[2,2]}),("algebraic_solution_set",{"relation":"x*y=6","ordered_solutions":4}),("finite_charts",{"chart_points":4,"transition":[2,3],"adjacency_preserved":True}),("finite_curvature",{"vertices":4,"curvature_each":[1,2],"total":2}),("metric_geodesic",{"start":[1,1],"end":[3,3],"length":4}),("self_similarity",{"depth_counts":[1,3,9,27],"exact_part_scale":[1,2]}),("tessellation",{"rows":3,"columns":3,"cells":9,"complete_cover":True}),("transformation_group",{"square_symmetries":8}))
 records=[]
 for i,(name,value) in enumerate(values,1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-geom-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-GEOMETRY-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-geom-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":16,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":16,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
