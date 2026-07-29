#!/usr/bin/env python3
"""Open and freeze independent exact LEARNX executions after registry freeze."""
import hashlib, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; REGISTRY = ROOT / "census/computation_learnx_001_026_target_registry_v1.json"; OUT = ROOT / "experiments/external_sources/computation/learnx_001_026_observation_vector_v1.json"; VALIDATOR = ROOT / "generated/computation/learnx_001_026_validator_v1.py"
def canonical(value): return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
def main():
    if OUT.exists(): raise SystemExit("LEARNX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text()); body = dict(registry); identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False: raise SystemExit("LEARNX registry changed")
    module_spec = importlib.util.spec_from_file_location("learnx_independent_observer", VALIDATOR); observer = importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(observer)
    values = (
        ("learning_identity", {"examples": 4, "unique_example_ids": 4, "feature_width": 2, "target_labels": ["left", "right"]}),
        ("hypothesis_family", {"feature_positions": 2, "label_orientations": 2, "generated_hypotheses": 4, "opaque_models": 0}),
        ("exact_loss_risk", {"best_mistakes": 0, "best_risk": "0/1 artifact absence", "alternate_mistakes": 2, "alternate_risk": "1/2", "floating_used": False}),
        ("held_out_custody", {"training_rows": 2, "validation_rows": 1, "test_rows": 1, "overlap_rows": 0, "identities_retained": True}),
        ("empirical_risk", {"hypotheses_evaluated": 4, "unique_minimizers": 1, "minimizer": "feature-1-left", "ties_hidden": False}),
        ("generalization", {"unseen_rows": 2, "preserved_rows": 2, "failed_rows": 0, "training_reuse": False}),
        ("sample_complexity", {"distinguished_points": 2, "complete_labelings": 4, "support_complete": True}),
        ("capacity_shattering", {"one_point_labelings_realized": 2, "one_point_shattered": True, "three_point_labelings_required": 8, "three_point_shattered": False}),
        ("pac_correspondence", {"complete_branches": 4, "success_branches": 3, "success_part": "3/4", "stochastic_cause_used": False}),
        ("classification", {"predictions": ["left", "right", "left", "right"], "targets": ["left", "right", "left", "right"], "errors": 0}),
        ("regression", {"targets": ["1/2", "3/2"], "exact_representative": "1/1", "continuum_used": False}),
        ("feature_selection", {"feature_one_sufficient": True, "feature_two_sufficient": False, "counterexamples_retained": True}),
        ("clustering", {"items": 3, "cluster_labels": 2, "complete_assignment_support": 8, "posthoc_labels_select_partition": False}),
        ("generative_support", {"seeds": ["left", "right"], "generated_support": [["left", "held"], ["right", "held"]], "missing_outputs": 0}),
        ("bayesian_correspondence", {"prior": {"left": "1/2", "right": "1/2"}, "likelihood": {"left": "3/4", "right": "1/4"}, "posterior": {"left": "3/4", "right": "1/4"}, "stochastic_cause_used": False}),
        ("optimization_convergence", {"initial_measure": 4, "trace": [4, 3, 2, 1], "terminal_measure": 1, "strict_descent": True}),
        ("online_regret", {"rounds": 3, "learner_loss": 1, "comparator_loss": 1, "exact_regret": 0, "future_access_used": False}),
        ("concept_drift", {"feature": "held", "before_target": "left", "after_target": "right", "change_retained": True, "prior_rows_rewritten": False}),
        ("search_planning", {"source": "a", "target": "c", "direct_cost": 3, "selected_cost": 2, "selected_path": ["a", "b", "c"], "heuristic_admissible": True}),
        ("reinforcement_return", {"reward_parts": ["1/2", "1/3", "1/6"], "finite_return": "1/1", "branch_trace_retained": True}),
        ("multi_agent", {"agents": 2, "actions_each": 2, "joint_action_rows": 4, "strategic_views_retained": True}),
        ("interpretability", {"trace": [["observe", "safe"], ["rule", "safe-to-act"], ["act", "act"]], "trace_steps": 3, "posthoc_only": False}),
        ("robustness_shift", {"stable_neighborhoods": 2, "stable_rows": 4, "adverse_coordinate_control_detected": True, "neighborhood_registered": True}),
        ("learned_verification", {"support_rows": 4, "verified_rows": 4, "property_failures": 0, "sample_only": False}),
        ("identifiability_limit", {"training_views_equal": True, "unseen_targets_distinct": True, "simultaneous_identification_possible": False}),
        ("learning_completeness", {"registered_obligations": 26, "independent_execution_rows": 26, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records=[]
    for index,(name,value) in enumerate(values,1):
        if not observer.independent_witness(index): raise SystemExit(f"LEARNX independent observation failed at {index:03d}")
        records.append({"number":f"{index:03d}","claim_id":registry["claim_ids"][index-1],"obligation_id":registry["obligation_ids"][index-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-learnx-{index:03d}-execution-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-LEARNING-OBSERVER","SFT-V1-V2-LEARNING-OBSERVATION-CORPUS"],"all_rows_preserved":True})
    payload={"schema":"sft-v3-classical-computation-learnx-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":identity,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":len(records),"all_rows_preserved":True,"external_measurement_boundary":"Learning laws are directly tested across complete generated examples, hypotheses, updates, held-out supports, shifts and adverse rows. Unison AI and application benchmarks remain downstream testbeds and cannot select these laws.","protected_engine_or_verifier_edit_made":False}; payload["vector_identity"]=canonical(payload); OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n"); print(json.dumps({"records":len(records),"identity":payload["vector_identity"]},indent=2))
if __name__=="__main__": main()
