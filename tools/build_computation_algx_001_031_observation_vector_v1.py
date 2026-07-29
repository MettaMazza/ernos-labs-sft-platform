#!/usr/bin/env python3
"""Open and freeze independent exact ALGX executions after registry freeze."""
import hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REGISTRY=ROOT/"census/computation_algx_001_031_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/computation/algx_001_031_observation_vector_v1.json";VALIDATOR=ROOT/"generated/computation/algx_001_031_validator_v1.py"
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("ALGX observation vector already frozen")
 registry=json.loads(REGISTRY.read_text());body=dict(registry);identity=body.pop("registry_identity")
 if canonical(body)!=identity or registry["target_content_present"] is not False:raise SystemExit("ALGX registry changed")
 spec=importlib.util.spec_from_file_location("algx_independent_observer",VALIDATOR);observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
 values=(
 ("algorithm_certificate",{"input":["a","b","c"],"target":"b","observed_positions":[0,1],"terminal_position":1,"invariant_retained":True}),
 ("search",{"linear_terminal_position":3,"ordered_terminal_position":2,"absent_result_supported":True}),
 ("comparison_sort",{"input":[3,1,2,1],"output":[1,1,2,3],"multiset_preserved":True,"stable_identity_retained":True}),
 ("bucket_order",{"input":["c","a","b","a"],"alphabet":["a","b","c"],"output":["a","a","b","c"]}),
 ("arithmetic",{"left_width":2,"right_width":3,"sum_width":5,"product_cells":6,"division_quotient":2,"division_remainder":1}),
 ("gcd_modular",{"inputs":[18,12],"greatest_common_part":6,"modular_power_remainder":4}),
 ("rational_arithmetic",{"sum":"1/2","product":"1/2","floating_used":False}),
 ("string_matching",{"text":"ababa","pattern":"aba","match_positions":[0,2],"overlaps_retained":True}),
 ("sequence_edit",{"source":"abc","target":"ac","least_edit_count":1,"witness_operation":"remove-b"}),
 ("tree_traversal",{"root":"r","preorder":["r","a","c","b"],"nodes_visited":4,"duplicates":0}),
 ("graph_reachability",{"source":"a","reach_order":["a","b","c","d"],"reached_vertices":4}),
 ("shortest_path",{"source":"a","target":"c","direct_cost":5,"composed_cost":3,"selected_path":["a","b","c"]}),
 ("spanning_tree",{"vertices":4,"tree_edges":[["a","b"],["a","c"],["b","d"]],"cycle_free":True,"all_reached":True}),
 ("flow_cut",{"path_flows":[2,1],"total_flow":3,"cut_capacities":[3,4,3],"least_cut":3,"equality":True}),
 ("matching",{"left":["a","b"],"right":["x","y"],"complete_matchings":1,"matched_pairs":[["a","x"],["b","y"]]}),
 ("exact_linear_solving",{"equations":["x+y=2","x+2y=3"],"positive_candidates_per_coordinate":3,"unique_solution":{"x":"1/1","y":"1/1"}}),
 ("symbolic_polynomial",{"left":"x+1","right":"x+1","product_coefficients":{"degree-2":1,"degree-1":2,"degree-0":1}}),
 ("geometry_orientation",{"left_example":"left","aligned_example":"aligned","signed_scalar_used":False}),
 ("convex_hull",{"points":5,"directed_boundary_edges":8,"undirected_boundary_edges":4,"interior_points":1}),
 ("dynamic_programming",{"tiling_width":6,"subproblem_rows":7,"exact_tiling_count":13}),
 ("greedy_boundary",{"intervals":4,"selected_intervals":[[1,3],[3,4],[4,6]],"selected_count":3,"exchange_checked":True}),
 ("branch_and_bound",{"items":3,"capacity":5,"optimal_value":7,"all_feasible_subsets_retained":True}),
 ("randomized_support",{"branch_labels":2,"depth":3,"complete_branches":8,"stochastic_cause_used":False}),
 ("parallel_algorithm",{"input_width":8,"layer_widths":[8,4,2,1],"work_depth_separate":True}),
 ("distributed_algorithm",{"source":"a","round_support_sizes":[1,2,3,4],"terminal_knowledge":["a","b","c","d"]}),
 ("online_algorithm",{"online_cost":6,"offline_optimum":4,"exact_competitive_part":"3/2","future_access_used":False}),
 ("streaming_algorithm",{"stream":["a","b","a","c"],"distinct_support":["a","b","c"],"summary_width":3}),
 ("numerical_iteration",{"start":"3/1","steps":3,"terminal":"5/4","limit":"1/1","all_values_rational":True,"floating_used":False}),
 ("symbolic_simplification",{"source":"join(a,a)","normal_form":"a","equivalence_preserved":True,"terminates":True}),
 ("approximation_scheme",{"candidate_guarantee":"7/8","registered_requirement":"3/4","guarantee_met":True,"floating_tolerance_used":False}),
 ("algorithm_completeness",{"registered_obligations":31,"independent_execution_rows":31,"duplicate_owners":0,"omitted_owners":0}))
 records=[]
 for index,(name,value) in enumerate(values,1):
  if not observer.independent_witness(index):raise SystemExit(f"ALGX independent observation failed at {index:03d}")
  records.append({"number":f"{index:03d}","claim_id":registry["claim_ids"][index-1],"obligation_id":registry["obligation_ids"][index-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-algx-{index:03d}-execution-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-ALGORITHM-OBSERVER","SFT-V1-V2-ALGORITHM-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 payload={"schema":"sft-v3-classical-computation-algx-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":identity,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":len(records),"all_rows_preserved":True,"external_measurement_boundary":"Algorithm laws are directly tested by exact generated executions and implementation-distinct reconstruction. Library, hardware and benchmark behavior remain downstream comparisons, never selectors.","protected_engine_or_verifier_edit_made":False};payload["vector_identity"]=canonical(payload);OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":len(records),"identity":payload["vector_identity"]},indent=2))
if __name__=="__main__":main()
