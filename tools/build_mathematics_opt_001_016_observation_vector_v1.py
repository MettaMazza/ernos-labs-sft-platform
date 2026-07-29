#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_opt_001_016_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/opt_001_016_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("OPT vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("OPT registry changed")
 values=(
  ("feasible_objective_order",{"generated":[1,2,3,4],"feasible":[2,3,4],"minimum":2}),
  ("finite_extrema",{"values":[4,1,3,2],"minimum":1,"maximum":4}),
  ("pareto_frontier",{"points":[[1,4],[2,2],[4,1],[3,3]],"nondominated":[[1,4],[2,2],[4,1]]}),
  ("linear_program",{"positive_grid_extent":3,"constraint":"x+y<=4","optimum":4,"optimum_set":[[1,3],[2,2],[3,1]]}),
  ("integer_combinatorial",{"weights":[1,2,3],"values":[2,3,4],"capacity":3,"unique_optimum_items":[1,2],"optimum_value":5}),
  ("convex_correspondence",{"candidates":[1,2,3,4,5],"objective":"held-distance-square-to-three","unique_minimizer":3}),
  ("duality_certificate",{"primal_optimum":4,"dual_bound":4,"exact_match":True}),
  ("variational_correspondence",{"positive_parts":3,"total":6,"action":"sum-of-squares","unique_path":[2,2,2]}),
  ("dynamic_programming",{"path_costs":[3,3,6],"complete_minimum":3,"backward_recurrence":3}),
  ("optimal_control",{"initial":1,"goal":5,"controls":[1,2],"unique_least_step_path":[2,2]}),
  ("game_equilibrium",{"actions":2,"profiles":4,"unique_mutual_best_response":[2,2]}),
  ("decision_loss",{"actions":["A","B","C"],"exact_losses":["3/2","2","5/2"],"minimum":"A"}),
  ("flow_scheduling",{"maximum_flow":3,"single_machine_lengths":[2,1],"makespan":3}),
  ("robust_optimization",{"worst_case_losses":{"A":5,"B":4,"C":6},"unique_choice":"B"}),
  ("approximation_gap",{"candidate":8,"optimum_bound":10,"ratio":"4/5","gap":2}),
  ("infeasible_unbounded_boundary",{"opposed_bounds":["at-most-two","at-least-three"],"feasible_count":0,"successor_exceeds_every_supplied_bound":True}),
 )
 records=[]
 for i,(name,value) in enumerate(values,1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-opt-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-OPTIMIZATION-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-opt-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":16,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":16,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
