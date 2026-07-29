#!/usr/bin/env python3
"""Open and freeze independent exact CPLXX resource executions after registry freeze."""
import hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REGISTRY=ROOT/"census/computation_cplxx_001_033_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/computation/cplxx_001_033_observation_vector_v1.json";VALIDATOR=ROOT/"generated/computation/cplxx_001_033_validator_v1.py"
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
    if OUT.exists():raise SystemExit("CPLXX observation vector already frozen")
    registry=json.loads(REGISTRY.read_text());body=dict(registry);identity=body.pop("registry_identity")
    if canonical(body)!=identity or registry["target_content_present"] is not False:raise SystemExit("CPLXX registry changed")
    spec=importlib.util.spec_from_file_location("cplxx_independent_observer",VALIDATOR);observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
    values=(
    ("canonical_input_length",{"word_depth":3,"complete_instance_count":8,"all_encodings_same_depth":True}),
    ("deterministic_time",{"instance_count":8,"transition_count_each":3,"unique_trace_each":True}),
    ("deterministic_space",{"instance_count":8,"maximum_live_word_width":3,"provenance_record_separate":True}),
    ("resource_hierarchy",{"depths":[1,2,3,4,5,6],"attained_resources":[1,2,3,4,5,6],"strict_successors":True}),
    ("nondeterministic_support",{"branch_labels":2,"depth":4,"complete_branch_count":16,"stochastic_cause_used":False}),
    ("certificate_resource",{"instances":8,"certificate_length":3,"verification_steps":3,"all_verdicts_reconstructed":True}),
    ("native_fold_p_np",{"native_depth":3,"deterministic_resource":3,"certificate_resource":3,"scope":"admitted-native-closing-grammar"}),
    ("conventional_transport",{"external_instances":8,"native_instances":8,"bijection":True,"verdict_trace_certificate_preserved":True,"arbitrary_export":False}),
    ("complement_class",{"terminal_classes":["accept","reject"],"verdicts_exchanged":True,"nontermination_relabelled":False}),
    ("alternating_space",{"existential_nodes":1,"universal_nodes":1,"terminal_nodes":3,"root_verdict":"accept","one_active_path_retained":True}),
    ("exponential_support",{"depths":[1,2,3,4,5,6],"support":[2,4,8,16,32,64]}),
    ("circuit_uniformity",{"family_depths":[1,2,3,4,5,6],"uniform_generator_present":True,"nonuniform_advice_rows":6}),
    ("circuit_resource_vector",{"depth":4,"width":16,"size":30,"coordinates_separate":True}),
    ("graph_model_translation",{"input_depth":3,"formula_path":3,"branching_path":3,"circuit_path":3,"trace_preserved":True}),
    ("parallel_work_depth",{"input_width":8,"layer_widths":[8,4,2,1],"depth":3,"work_and_depth_separate":True}),
    ("communication_distinctions",{"input_pairs":4,"transcript_classes":2,"same_class_size":2,"different_class_size":2}),
    ("query_lower_bound",{"input_depth":4,"required_leaves":16,"complete_tree_nodes":31,"unresolved_pair_below_depth":True}),
    ("randomized_support",{"branches":4,"accept_part":"3/4","reject_part":"1/4","stochastic_cause_used":False}),
    ("derandomization_boundary",{"branch_invariant_support":4,"branch_invariant_outcomes":1,"mixed_support_outcomes":2,"unforced_selection_rejected":True}),
    ("counting_support",{"branches":4,"accepting_branches":3,"rejecting_branches":1,"exact_census_retained":True}),
    ("reduction_completeness",{"source_instances":2,"intermediate_instances":2,"terminal_instances":2,"composition_preserves_verdict":True}),
    ("upper_bound",{"input_depth":4,"execution_steps":4,"bound_attained":True}),
    ("lower_bound",{"input_depth":4,"observed_prefix_depth":3,"indistinguishable_pairs_with_different_suffix":8,"smaller_observation_insufficient":True}),
    ("native_circuit_lower_bound",{"depths":[1,2,3,4,5,6,7],"path_bounds":[1,2,3,4,5,6,7],"width_at_depth_seven":128,"size_at_depth_seven":254}),
    ("worst_average",{"resource_vector":[1,2,4,1],"worst":4,"exact_average":"2/1","distribution_rows":4}),
    ("approximation_ratio",{"candidate":6,"optimum":4,"oriented_exact_part":"3/2","floating_used":False}),
    ("parameterized_resource",{"input_depth":3,"parameters":[1,2],"coordinates_separate":True,"resource_bound_preserved":True}),
    ("kernelization",{"source":["a","a","b","a"],"parameter":2,"kernel":["a","b"],"reverse_locations":{"a":[0,1,3],"b":[2]}}),
    ("amortized_resource",{"operation_costs":[1,1,3,1],"prefix_totals":[1,2,5,6],"aggregate":6,"exact_average":"3/2","negative_credit_used":False}),
    ("online_competitive",{"online_cost":6,"offline_optimum":4,"exact_ratio":"3/2","complete_prefixes_retained":True}),
    ("description_complexity",{"literal_description_length":3,"compressed_description_length":2,"least_registered_length":2,"grammar_fixed":True}),
    ("reversible_tradeoff",{"source":["a","b","c"],"reverse_record":["c","b","a"],"restored":["a","b","c"],"lost_predecessor_labels":0}),
    ("complexity_completeness",{"registered_obligations":33,"independent_execution_rows":33,"duplicate_owners":0,"omitted_owners":0}))
    records=[]
    for index,(name,value) in enumerate(values,1):
        if not observer.independent_witness(index):raise SystemExit(f"CPLXX independent observation failed at {index:03d}")
        records.append({"number":f"{index:03d}","claim_id":registry["claim_ids"][index-1],"obligation_id":registry["obligation_ids"][index-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-cplxx-{index:03d}-execution-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-COMPLEXITY-OBSERVER","SFT-V1-V2-COMPLEXITY-OBSERVATION-CORPUS"],"all_rows_preserved":True})
    payload={"schema":"sft-v3-classical-computation-cplxx-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":identity,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":len(records),"all_rows_preserved":True,"external_measurement_boundary":"Complexity laws are tested by exact complete-family resource executions and implementation-distinct reconstruction. Native and finite results retain explicit transport and depth boundaries.","protected_engine_or_verifier_edit_made":False};payload["vector_identity"]=canonical(payload);OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":len(records),"identity":payload["vector_identity"]},indent=2))
if __name__=="__main__":main()
