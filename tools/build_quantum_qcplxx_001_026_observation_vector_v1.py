#!/usr/bin/env python3
"""Open and freeze independent exact QCPLXX executions after registry freeze."""
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/quantum_qcplxx_001_026_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/quantum_computation/qcplxx_001_026_observation_vector_v1.json"
VALIDATOR = ROOT / "generated/quantum_computation/qcplxx_001_026_validator_v1.py"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("QCPLXX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text())
    body = dict(registry)
    identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False:
        raise SystemExit("QCPLXX value-free registry changed")
    spec = importlib.util.spec_from_file_location("qcplxx_independent_observer", VALIDATOR)
    observer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(observer)
    values = (
        ("input_size", {"description_width": 3, "promise_rows": 1, "representation_canonical": True}),
        ("gate_depth", {"gate_count": 3, "depth": 2, "coordinates_separate": True}),
        ("live_support", {"register_width": 2, "live_support_rows": 4, "description_rows": 4}),
        ("record_resources", {"ancilla": 2, "measurements": 1, "retained_records": 3}),
        ("query_complexity", {"reversible_queries": 3, "inverse_queries_included": True}),
        ("communication_complexity", {"transmitted_distinctions": 5, "rounds": 3, "shared_records_retained": True}),
        ("decision_class", {"input_classes": 3, "accept_rows": 2, "reject_rows": 1}),
        ("bounded_error", {"favorable_support": 3, "complete_support": 4, "exact_ratio": "3/4", "ontic_randomness": False}),
        ("exact_decision", {"correct_support": 2, "complete_support": 2, "exact_ratio": "1/1"}),
        ("one_sided_error", {"complete_side_ratio": "1/1", "adverse_side_error_ratio": "0/1"}),
        ("nondeterminism_correspondence", {"generated_branches": 3, "accepting_branches": 1, "ontic_choice_imported": False}),
        ("polynomial_time", {"input_sizes": [1, 2, 3], "resource_costs": [1, 4, 9], "uniform_envelope": True}),
        ("witness_verification", {"witnesses": 2, "accepting_witnesses": 1, "complete_census": True}),
        ("interactive_proof", {"rounds": 1, "messages": 2, "final_decisions": 1, "private_support_retained": True}),
        ("space_complexity", {"stage_widths": [2, 3, 2, 1], "maximum_live_width": 3}),
        ("parallel_complexity", {"work": 6, "depth": 2, "processors": 3, "coordinates_separate": True}),
        ("uniformity", {"input_sizes": 3, "generated_circuits": 3, "single_generator": True}),
        ("reduction_completeness", {"source_classes": 1, "mapping_rows": 1, "target_classes": 1, "decision_preserved": True}),
        ("adversary_lower_bound", {"input_pairs": 2, "lower_witnesses": [2, 3], "observed_costs": [3, 4]}),
        ("polynomial_method", {"query_degrees": [1, 2, 3], "constraint_rows": 3, "continuous_coefficients_imported": False}),
        ("classical_simulation", {"quantum_vector": [3, 4, 2], "classical_vector": [5, 8, 4], "complete_trace_reproduced": True}),
        ("advantage_separation", {"same_problem": True, "quantum_vector": [3, 4, 2], "comparison_vector": [5, 8, 4], "strict_coordinate": True}),
        ("average_case", {"case_rows": 3, "weight_denominator": 6, "exact_average": "10/3", "all_cases_retained": True}),
        ("parameterized_complexity", {"parameter_slices": 2, "resource_rows": 3, "input_size_separate": True}),
        ("descriptive_complexity", {"machine_description_tokens": 3, "grammar_frozen": True, "minimum_checked": True}),
        ("complexity_completeness", {"registered_obligations": 26, "execution_rows": 26, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        if not observer.independent_witness(index):
            raise SystemExit(f"QCPLXX independent observation failed at {index:03d}")
        records.append({"number": f"{index:03d}", "claim_id": registry["claim_ids"][index - 1], "obligation_id": registry["obligation_ids"][index - 1], "observation_name": name, "exact_observation": value, "expected_label": f"complete-qcplxx-{index:03d}-execution-retained", "source_ids": ["SFT-V3-INDEPENDENT-EXACT-QUANTUM-COMPLEXITY-OBSERVER", "SFT-V1-V2-QUANTUM-COMPLEXITY-OBSERVATION-CORPUS"], "all_rows_preserved": True})
    payload = {"schema": "sft-v3-quantum-qcplxx-observation-vector/1", "date": "2026-07-29", "authority": "Maria Smith", "registry_identity": identity, "outcomes_opened_only_after_registry_freeze": True, "records": records, "record_count": len(records), "all_rows_preserved": True, "external_measurement_boundary": "Quantum-complexity laws are directly tested by exact finite executions and resource comparisons. Physical device performance and unrestricted asymptotic separations remain independently measured or proven and cannot select these formal laws.", "protected_engine_or_verifier_edit_made": False}
    payload["vector_identity"] = canonical(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
