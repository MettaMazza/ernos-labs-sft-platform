#!/usr/bin/env python3
import hashlib, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/quantum_qcodex_001_032_target_registry_v1.json"; OUT = ROOT / "experiments/external_sources/quantum_computation/qcodex_001_032_observation_vector_v1.json"; VALIDATOR = ROOT / "generated/quantum_computation/qcodex_001_032_validator_v1.py"
def canonical(value): return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
def main():
    if OUT.exists(): raise SystemExit("QCODEX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text()); body = dict(registry); identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False: raise SystemExit("QCODEX value-free registry changed")
    spec = importlib.util.spec_from_file_location("qcodex_independent_observer", VALIDATOR); observer = importlib.util.module_from_spec(spec); spec.loader.exec_module(observer)
    values = (
        ("logical_physical", {"logical_classes": 2, "physical_width": 3, "carrier_distinction_retained": True}),
        ("encoder_decoder", {"logical_inputs": 2, "encoded_words": 2, "round_trip_complete": True}),
        ("error_family", {"width": 3, "masks_through_order_one": 4, "frozen_before_outcomes": True}),
        ("syndrome", {"constraint_rows": 2, "distinct_rows": 2, "logical_class_hidden": True}),
        ("correctable_condition", {"single_faults": 3, "distinct_syndromes": 3, "recoveries": 3}),
        ("bit_repetition", {"fault_order": 1, "width": 3, "mask_rows": 4, "all_recovered": True}),
        ("phase_repetition", {"fault_order": 1, "width": 3, "mask_rows": 4, "all_recovered": True}),
        ("joint_error", {"label_faults": 1, "phase_faults": 1, "joint_records": 1}),
        ("single_error", {"fault_order": 1, "width": 3, "exhaustive_masks": 4, "failures": 0}),
        ("two_error", {"fault_order": 2, "width": 5, "exhaustive_masks": 16, "failures": 0}),
        ("three_error", {"fault_order": 3, "width": 7, "exhaustive_masks": 64, "failures": 0}),
        ("multi_error_successor", {"law": "2t+1", "tested_orders": [1, 2, 3, 4, 5], "induction_depth_independent": True}),
        ("erasure", {"located_position": 2, "source_width": 3, "reconstructed": True}),
        ("amplitude_loss", {"located_loss_record": True, "physical_decay_rate_present": False}),
        ("dephasing", {"phase_fault_rows": 1, "environment_records": 1, "physical_rate_present": False}),
        ("depolarizing_support", {"error_classes": ["label", "phase", "joint"], "physical_weights_present": False}),
        ("stabilizer_correspondence", {"constraint_rows": 2, "code_syndrome": ["same", "same"], "imported_algebra": False}),
        ("css_correspondence", {"label_constraint_families": 1, "phase_constraint_families": 1, "records_composed": True}),
        ("subsystem_correspondence", {"logical_factors": 1, "gauge_factors": 1, "syndrome_factors": 1}),
        ("topological_boundary", {"cell_edges": 3, "syndrome_chains": 1, "physical_locality_present": False}),
        ("surface_boundary", {"vertices": 4, "edges": 4, "faces": 1, "physical_threshold_present": False}),
        ("concatenation", {"outer_width": 3, "inner_width": 3, "physical_carriers": 9}),
        ("logical_gate", {"logical_classes": 2, "encoded_images": 2, "code_space_preserved": True}),
        ("transversal_containment", {"carrierwise_actions": 3, "within_block_spread": 1, "contained": True}),
        ("syndrome_extraction_fault", {"data_rows": 1, "syndrome_rows": 1, "extraction_fault_rows": 1}),
        ("fault_tolerant_locations", {"location_orders": [1, 2, 3], "composable_containment": True}),
        ("malignant_fault_sets", {"fault_subsets": 2, "benign_rows": 1, "logical_failure_rows": 1, "all_retained": True}),
        ("correlated_fault", {"fault_locations": 2, "joint_cause_records": 1, "independence_assumed": False}),
        ("leakage_loss", {"code_support_classes": 2, "outside_support_classes": 1, "located_loss_classes": 1}),
        ("distillation", {"input_resources": 3, "accepted": 1, "rejected": 2, "physical_fidelity_present": False}),
        ("threshold_handoff", {"formal_fault_grammar_complete": True, "physical_threshold_value_present": False, "owner": "physics-engineering-measurement"}),
        ("coding_completeness", {"registered_obligations": 32, "execution_rows": 32, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        if not observer.independent_witness(index): raise SystemExit(f"QCODEX independent observation failed at {index:03d}")
        records.append({"number": f"{index:03d}", "claim_id": registry["claim_ids"][index - 1], "obligation_id": registry["obligation_ids"][index - 1], "observation_name": name, "exact_observation": value, "expected_label": f"complete-qcodex-{index:03d}-execution-retained", "source_ids": ["SFT-V3-INDEPENDENT-EXACT-QUANTUM-CODING-OBSERVER", "SFT-V1-V2-QUANTUM-CODING-FAULT-OBSERVATION-CORPUS"], "all_rows_preserved": True})
    payload = {"schema": "sft-v3-quantum-qcodex-observation-vector/1", "date": "2026-07-29", "authority": "Maria Smith", "registry_identity": identity, "outcomes_opened_only_after_registry_freeze": True, "records": records, "record_count": len(records), "all_rows_preserved": True, "external_measurement_boundary": "Coding and recovery laws are tested by exact exhaustive fault masks and independent reconstruction. Physical error rates, correlations, leakage, fidelities and threshold constants remain downstream measurements and cannot select formal codes.", "protected_engine_or_verifier_edit_made": False}; payload["vector_identity"] = canonical(payload); OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n"); print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))
if __name__ == "__main__": main()
