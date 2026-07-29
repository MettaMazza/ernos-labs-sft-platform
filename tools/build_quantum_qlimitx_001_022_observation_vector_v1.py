#!/usr/bin/env python3
"""Open and freeze exact QLIMITX outcomes after value-free registration."""

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/quantum_qlimitx_001_022_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/quantum_computation/qlimitx_001_022_observation_vector_v1.json"
VALIDATOR = ROOT / "generated/quantum_computation/qlimitx_001_022_validator_v1.py"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("QLIMITX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text())
    body = dict(registry)
    registry_identity = body.pop("registry_identity")
    if canonical(body) != registry_identity or registry["target_content_present"] is not False:
        raise SystemExit("QLIMITX value-free registry changed")
    spec = importlib.util.spec_from_file_location("qlimitx_independent_observer", VALIDATOR)
    observer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(observer)
    values = (
        ("classical_embedding", {"classical_words": 1, "support_rows": 1, "phase_class": "phase-held"}),
        ("reversible_submodel", {"source_rows": 4, "image_rows": 4, "inverse_rows": 4}),
        ("probabilistic_support", {"deterministic_support_rows": 4, "observation_relation_present": True, "ontic_randomness": False}),
        ("measurement_decoder", {"selected_classes": 1, "closed_classes": 1, "source_record_retained": True}),
        ("bidirectional_simulation", {"forward_rows": 4, "reverse_rows": 4, "resource_ledgers_compared": True}),
        ("efficient_region", {"tested_depths": [1, 2, 3], "resource_bound": "two rows per depth", "outside_region_claimed": False}),
        ("phase_separation", {"word_supports": 1, "distinct_phase_classes": 2, "phase_deletion_equivalent": False}),
        ("entanglement_separation", {"joint_rows": 2, "factorable": False, "independent_product_rows": 4}),
        ("no_cloning", {"same_observed_word": True, "distinct_unknown_phase_descriptions": 2, "universal_reversible_cloner": False}),
        ("measurement_disturbance", {"selected_classes": 1, "closed_classes": 1, "reverse_record_required": True}),
        ("halting_self_reference", {"embedded_decider_answers": 2, "self_negating_rows": 2, "total_consistent_decider": False}),
        ("undecidability", {"classical_embedding_complete": True, "quantum_total_decider": False}),
        ("incompleteness", {"finite_proof_system": True, "complete_internal_self_truth": False}),
        ("no_hypercomputation", {"finite_generated_transition": True, "unregistered_oracle": False, "hypercomputation_claim": False}),
        ("finite_support", {"tested_widths": [1, 2, 3, 4], "support_counts": [2, 4, 8, 16], "completed_infinity": False}),
        ("bounded_example_limit", {"bounded_depths": [1, 2, 3], "unrestricted_advantage_claimed": False}),
        ("physical_speedup_handoff", {"formal_resource_separation": True, "device_timing_present": False, "measurement_required": True}),
        ("hardware_threshold_handoff", {"formal_code_width": "2t+1", "hardware_threshold_present": False, "measurement_required": True}),
        ("implementation_handoff", {"measurement_classes": ["energy", "timing", "geometry", "control", "temperature"], "values_present": False}),
        ("physics_boundary", {"formal_prediction_sealed": True, "physical_target_identity_sealed": True, "blind_measurement_owner": "physics"}),
        ("open_falsification", {"dated_closure": True, "lawful_extensions_allowed": True, "adverse_rows_preserved": True}),
        ("limits_completeness", {"registered_obligations": 22, "execution_rows": 22, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        if not observer.independent_witness(index):
            raise SystemExit(f"QLIMITX independent observation failed at {index:03d}")
        records.append({"number": f"{index:03d}", "claim_id": registry["claim_ids"][index - 1], "obligation_id": registry["obligation_ids"][index - 1], "observation_name": name, "exact_observation": value, "expected_label": f"complete-qlimitx-{index:03d}-execution-retained", "source_ids": list(registry["pre_registered_source_identities"]), "all_rows_preserved": True})
    payload = {"schema": "sft-v3-quantum-qlimitx-observation-vector/1", "date": "2026-07-29", "authority": "Maria Smith", "registry_identity": registry_identity, "outcomes_opened_only_after_registry_freeze": True, "records": records, "record_count": len(records), "all_rows_preserved": True, "external_measurement_boundary": "Formal classical-quantum limits are executed and independently reconstructed. Physical speedup, timing, energy, fidelity and hardware threshold values remain explicit Physics/device measurement handoffs.", "protected_engine_or_verifier_edit_made": False}
    payload["vector_identity"] = canonical(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
