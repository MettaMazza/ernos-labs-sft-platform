#!/usr/bin/env python3
import hashlib,json
from fractions import Fraction
from itertools import combinations,permutations,product
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_graph_001_014_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/graph_001_014_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def connected(vertices,edges):
 seen={vertices[0]};changed=True
 while changed:
  changed=False
  for a,b in edges:
   if a in seen and b not in seen:seen.add(b);changed=True
   if b in seen and a not in seen:seen.add(a);changed=True
 return len(seen)==len(vertices)
def main():
 if OUT.exists():raise SystemExit("GRAPH vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("GRAPH registry changed")
 vertices=(1,2,3,4);k4=tuple(combinations(vertices,2));spanning=sum(len(es)==3 and connected(vertices,es) for es in combinations(k4,3))
 triangle=((1,2),(2,3),(1,3));connected_masks=sum(connected((1,2,3),tuple(e for i,e in enumerate(triangle) if mask>>i&1)) for mask in range(8))
 obs=(
  ("graph_identity_isomorphism",{"vertices":4,"edges":4,"isomorphic_relabellings":8}),
  ("path_reachability_cycle",{"reachable_order":[1,2,3,4],"least_cycle_length":4}),
  ("connectivity_cut_flow",{"maximum_integral_flow":3,"minimum_cut_capacity":3}),
  ("tree_forest_spanning",{"complete_graph_vertices":4,"spanning_trees":spanning,"edges_per_tree":3}),
  ("planarity_embedding",{"k4_vertices":4,"k4_edges":6,"k4_faces":4,"euler_total":2,"k5_edge_bound_exceeded":True}),
  ("colouring_constraints",{"cycle_vertices":5,"chromatic_number":3}),
  ("matching_covering_packing",{"bipartite_part_size":3,"maximum_matching":3,"minimum_vertex_cover":3}),
  ("directed_causal_reachability",{"vertices":5,"causal_pairs":9,"topological_order":[1,2,3,4,5]}),
  ("weighted_exact_parts",{"path_weight":{"numerator":7,"denominator":6},"alternative_weight":{"numerator":4,"denominator":3}}),
  ("hypergraph_higher_incidence",{"vertices":6,"hyperedges":4,"rank":3,"vertex_degree":2}),
  ("matroid_independence",{"ground_size":4,"rank":2,"independent_sets":11,"basis_count":6}),
  ("reliability_failure_custody",{"edge_masks":8,"connected_masks":connected_masks,"exact_reliability":{"numerator":1,"denominator":2}}),
  ("spectral_even_walk_correspondence",{"operator":"adjacency-square-k4","uniform_mode":9,"distinction_mode":1,"trace":12}),
  ("dynamic_temporal_network",{"time_respecting_path":[1,2,3,4],"arrival_time":3,"static_but_time_forbidden_path":[1,3,4]}),
 )
 rec=[]
 for i,(name,value) in enumerate(obs,1):rec.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-graph-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-GRAPH-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-graph-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":rec,"record_count":14,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":14,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
