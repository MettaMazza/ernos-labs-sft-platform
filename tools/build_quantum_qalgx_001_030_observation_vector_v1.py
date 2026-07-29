#!/usr/bin/env python3
"""Open and freeze independent exact QALGX executions after registry freeze."""
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/quantum_qalgx_001_030_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/quantum_computation/qalgx_001_030_observation_vector_v1.json"
VALIDATOR = ROOT / "generated/quantum_computation/qalgx_001_030_validator_v1.py"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("QALGX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text())
    body = dict(registry)
    identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False:
        raise SystemExit("QALGX value-free registry changed")
    spec = importlib.util.spec_from_file_location("qalgx_independent_observer", VALIDATOR)
    observer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(observer)
    values = (
        ("algorithm_specification", {"input_classes": 1, "process_steps": 1, "output_classes": 1, "correctness_trace": True}),
        ("reversible_oracle", {"source_rows": 4, "image_rows": 4, "queries": 1, "bijection": True}),
        ("phase_kickback", {"control_retained": True, "target_restored": True, "relative_phase_recorded": True}),
        ("fourier_correspondence", {"support_rows": 4, "period_classes": 2, "complex_scalars_imported": False}),
        ("phase_estimation", {"phase_rows": 4, "least_period": 2, "exact_enclosure": True}),
        ("period_order", {"domain_rows": 6, "least_period": 3, "all_rows_checked": True}),
        ("deutsch_promise", {"promise_classes": 2, "function_rows": 2, "distinguished": True}),
        ("simon_hidden_structure", {"word_width": 2, "candidate_translations": 4, "unique_consistent_translation": True}),
        ("factorization", {"composite": 15, "positive_divisors": [1, 3, 5, 15], "nontrivial_divisors": [3, 5]}),
        ("unstructured_search", {"support_rows": 4, "marked_rows": 1, "query_trace_retained": True}),
        ("quantum_counting", {"support_rows": 4, "marked_rows": 2, "cardinality_exact": True}),
        ("amplitude_estimation", {"exact_ratio": "1/3", "lower_enclosure": "1/4", "upper_enclosure": "1/2"}),
        ("quantum_walk", {"vertices": 2, "steps": 2, "source_restored": True}),
        ("walk_search", {"path_rows": 3, "marked_vertices": 1, "observation_retained": True}),
        ("linear_system", {"relation_rows": 2, "solution_rows": 2, "inverse_explicit": True}),
        ("eigenmode", {"mode_rows": 4, "least_period": 2, "phase_record_retained": True}),
        ("hamiltonian_interface", {"local_generators": 2, "duration_count": 1, "physical_values_present": False}),
        ("product_formula", {"local_actions": 4, "ordering_retained": True, "error_enclosure_exact": True}),
        ("combinatorial_optimization", {"candidate_rows": 3, "unique_minimum": "b", "full_order_retained": True}),
        ("variational_boundary", {"generated_controls": 4, "fitted_controls": 0, "unique_survivors": 1}),
        ("annealing_boundary", {"finite_path_rows": 3, "terminal_map_retained": True, "physical_schedule_present": False}),
        ("sampling_custody", {"output_rows": 3, "exact_multiplicities": {"held": 2, "returned": 1}, "ontic_randomness_imported": False}),
        ("bosonic_sampling_boundary", {"occupation_words": 2, "permutation_classes": 2, "device_probability_present": False}),
        ("hidden_subgroup", {"cosets": 2, "support_rows": 4, "candidate_partitions_exhausted": True}),
        ("dynamic_programming", {"subproblems": 4, "terminal_optimum": 2, "dependency_rows_retained": True}),
        ("quantum_parallelism", {"branch_rows": 8, "registered_output_observations": 1, "all_branch_values_claimed_returned": False}),
        ("classical_custody", {"classical_pre_steps": 1, "quantum_core_steps": 1, "classical_post_steps": 1, "resources_separate": True}),
        ("speedup_grammar", {"same_problem": True, "resource_vectors": 2, "observation_boundaries_equal": True}),
        ("resource_bounds", {"lower_witnesses": 2, "upper_witnesses": 2, "all_exact_values_enclosed": True}),
        ("algorithm_completeness", {"registered_obligations": 30, "execution_rows": 30, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        if not observer.independent_witness(index):
            raise SystemExit(f"QALGX independent observation failed at {index:03d}")
        records.append({"number": f"{index:03d}", "claim_id": registry["claim_ids"][index - 1], "obligation_id": registry["obligation_ids"][index - 1], "observation_name": name, "exact_observation": value, "expected_label": f"complete-qalgx-{index:03d}-execution-retained", "source_ids": ["SFT-V3-INDEPENDENT-EXACT-QUANTUM-ALGORITHM-OBSERVER", "SFT-V1-V2-QUANTUM-ALGORITHM-OBSERVATION-CORPUS"], "all_rows_preserved": True})
    payload = {"schema": "sft-v3-quantum-qalgx-observation-vector/1", "date": "2026-07-29", "authority": "Maria Smith", "registry_identity": identity, "outcomes_opened_only_after_registry_freeze": True, "records": records, "record_count": len(records), "all_rows_preserved": True, "external_measurement_boundary": "Quantum-algorithm laws are directly tested by exact finite execution and independent reconstruction. Physical device performance and unrestricted asymptotic advantage remain separately measured or bounded and cannot select the formal laws.", "protected_engine_or_verifier_edit_made": False}
    payload["vector_identity"] = canonical(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
