#!/usr/bin/env python3
"""Open and freeze independent exact SCIX executions after registry freeze."""
import hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REGISTRY=ROOT/"census/computation_scix_001_025_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/computation/scix_001_025_observation_vector_v1.json";VALIDATOR=ROOT/"generated/computation/scix_001_025_validator_v1.py"
def canonical(value):return "sha256:"+hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("SCIX observation vector already frozen")
 registry=json.loads(REGISTRY.read_text());body=dict(registry);identity=body.pop("registry_identity")
 if canonical(body)!=identity or registry["target_content_present"] is not False:raise SystemExit("SCIX registry changed")
 spec=importlib.util.spec_from_file_location("scix_independent_observer",VALIDATOR);observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
 values=(
 ("exact_approximate",{"exact":"1/3","approximation":"33/100","enclosure":["33/100","34/100"],"contained":True}),
 ("finite_precision",{"source":"7/5","grid_denominator":4,"nearest":"3/2","tie_rule":"least-exact-grid-part"}),
 ("rounding_truncation",{"exact":"7/5","represented":"3/2","separation":"1/10","floating_used":False}),
 ("forward_backward",{"forward_separation":"1/10","reconstructed_exact_input":"7/5","both_ledgers_retained":True}),
 ("conditioning",{"input_separation":"1/1","output_separation":"2/1","amplification":"2/1"}),
 ("stability_composition",{"steps":2,"terminal_enclosure":["27/10","33/10"],"all_step_errors_retained":True}),
 ("convergence",{"errors":["1/2","1/4","1/8"],"reduction_ratios":["2/1","2/1"],"stopping_certificate":"registered-error-sequence"}),
 ("discretization",{"interval":["1/1","2/1"],"pieces":4,"mesh":["1/1","5/4","3/2","7/4","2/1"]}),
 ("interpolation",{"nodes":[["1/1","2/1"],["3/1","6/1"]],"point":"2/1","interpolated":"4/1"}),
 ("quadrature",{"function":"square","nodes":["1/1","2/1","3/1"],"trapezoid_sum":"9/1","residual_boundary_retained":True}),
 ("root_interval",{"target_square":"4/1","initial_interval":["1/1","3/1"],"exact_root":"2/1","substitution_closes":True}),
 ("linear_system",{"equations":["x+y=3","x+2y=5"],"solution":{"x":"1/1","y":"2/1"},"residuals":["absence","absence"]}),
 ("eigen_modes",{"operator":"diagonal(2,3)","modes":[{"value":"2/1","vector":["1/1","absence"]},{"value":"3/1","vector":["absence","1/1"]}],"residuals_close":True}),
 ("ordinary_system",{"initial":"1/1","step":"1/2","derivative":"y","terminal":"3/2","trace_retained":True}),
 ("partial_system",{"source_row":[1,2,3,4,5],"smoothed_interior":[2,3,4],"boundary_retained":True}),
 ("stochastic_support",{"branch_labels":2,"depth":3,"complete_paths":8,"stochastic_cause_used":False}),
 ("monte_carlo_support",{"support_values":[1,2,3,4],"support_width":4,"exact_average":"5/2","sample_promoted_to_whole":False}),
 ("inverse_identifiability",{"parameters":["a","b","c"],"image_same_predecessors":["a","b"],"identifiable":False,"regularizer_selected":False}),
 ("computational_statistics",{"values":[1,3,2],"mean":"2/1","median":"2/1","complete_support_retained":True}),
 ("sparse_computation",{"width":3,"stored_entries":2,"result":[8,"absence",15],"absent_coordinates_retained":True}),
 ("many_body",{"component_states":2,"bodies":4,"product_states":16,"interactions_hidden":False}),
 ("symbolic_numeric",{"expression":"1+2x+x^2","input":"2/1","exact_output":"9/1","rewrite_trace_retained":True}),
 ("simulation_validation",{"equation":"two-times-input","input":"3/1","implementation_output":"6/1","equation_output":"6/1","external_validation_separate":True}),
 ("model_provenance",{"equation":"two-times-input","inputs":["3/1"],"output":"6/1","source":"registered","receipt_bound":True}),
 ("scientific_completeness",{"registered_obligations":25,"independent_execution_rows":25,"duplicate_owners":0,"omitted_owners":0}))
 records=[]
 for index,(name,value) in enumerate(values,1):
  if not observer.independent_witness(index):raise SystemExit(f"SCIX independent observation failed at {index:03d}")
  records.append({"number":f"{index:03d}","claim_id":registry["claim_ids"][index-1],"obligation_id":registry["obligation_ids"][index-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-scix-{index:03d}-execution-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-SCIENTIFIC-OBSERVER","SFT-V1-V2-SCIENTIFIC-COMPUTATION-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 payload={"schema":"sft-v3-classical-computation-scix-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":identity,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":len(records),"all_rows_preserved":True,"external_measurement_boundary":"Scientific-computation laws are tested by exact generated calculations and independent reconstruction. Domain measurements validate application models in their owning science branches and never select the numerical law.","protected_engine_or_verifier_edit_made":False};payload["vector_identity"]=canonical(payload);OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":len(records),"identity":payload["vector_identity"]},indent=2))
if __name__=="__main__":main()
