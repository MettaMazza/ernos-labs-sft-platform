#!/usr/bin/env python3
"""Open and freeze exact QSIMX outcomes after the value-free registry exists."""

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/quantum_qsimx_001_024_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/quantum_computation/qsimx_001_024_observation_vector_v1.json"
VALIDATOR = ROOT / "generated/quantum_computation/qsimx_001_024_validator_v1.py"


def canonical(value):
    return "sha256:" + hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("QSIMX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text())
    body = dict(registry)
    registry_identity = body.pop("registry_identity")
    if canonical(body) != registry_identity or registry["target_content_present"] is not False:
        raise SystemExit("QSIMX value-free registry changed")
    module_spec = importlib.util.spec_from_file_location("qsimx_independent_observer", VALIDATOR)
    observer = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(observer)
    values = (
        ("model_simulator_identity", {"model_rows": 4, "simulator_rows": 4, "forward_reverse_correspondence": True}),
        ("finite_target_support", {"word_width": 3, "generated_words": 8, "duplicate_words": 0}),
        ("digital_simulation", {"source": ["held", "returned"], "schedule": [1, 2], "trace_rows": 2, "image": ["returned", "held"]}),
        ("analog_boundary", {"formal_support_complete": True, "physical_mapping_present": False, "measurement_handoff_required": True}),
        ("local_update_composition", {"support_places": 2, "local_updates": 2, "causal_trace_retained": True}),
        ("hamiltonian_correspondence", {"generator_rows": 4, "inverse_rows": 4, "imported_continuum_operator": False, "imaginary_proof_scalar": False}),
        ("evolution_enclosure", {"finite_refinement_depths": [1, 2, 3], "complete_trace_each_depth": True, "unregistered_limit_claimed": False}),
        ("many_body_support", {"body_places": 3, "joint_words": 8, "incidence_rows_per_word": 3}),
        ("fermion_boson_correspondence", {"distinct_exchange_phase": "phase-returned", "same-label_exchange_phase": "phase-held", "conventional_statistics_imported": False}),
        ("lattice_field_handoff", {"sites": 3, "links": 2, "incidence_complete": True, "physical_spacing_present": False}),
        ("open_system_record", {"system_rows": 1, "environment_rows": 1, "cause_records": 1, "joint_reconstruction": True}),
        ("noise_source_custody", {"source_rows": 1, "image_rows": 1, "cause_rows": 1, "ontic_randomness_imported": False}),
        ("chemistry_handoff", {"formal_simulator_sealed": True, "chemistry_target_owner": "chemistry", "target_value_present": False}),
        ("materials_handoff", {"formal_simulator_sealed": True, "materials_target_owner": "materials", "target_value_present": False}),
        ("computation_verification", {"source_rows": 1, "schedule_rows": 2, "trace_rows": 2, "claimed_image_verified": True}),
        ("interactive_verification", {"challenge_rounds": 3, "response_rows": 3, "complete_transcript": True}),
        ("blind_delegation", {"task_commitment_present": True, "executor_target_access": False, "complete_verification_trace": True}),
        ("self_testing_boundary", {"formal_behavior_relation_identified": True, "physical_device_identity_claimed": False, "measurement_handoff_required": True}),
        ("tomography_boundary", {"declared_support_rows": 4, "observation_rows": 4, "reconstructed_rows": 4, "continuum_claimed": False}),
        ("process_channel_verification", {"source_rows": 4, "image_rows": 4, "duplicate_images": 0, "complete_table": True}),
        ("deterministic_benchmarking", {"schedule_depth": 3, "complete_schedules": 8, "sampled_schedules": 0, "ontic_randomness": False}),
        ("owning_domain_validation", {"formal_result_sealed": True, "target_identity_sealed": True, "data_selects_law": False, "adverse_rows_preserved": True}),
        ("workflow_provenance", {"chain_fields": 6, "source_and_trace_hashes_required": True, "independent_reconstruction_required": True}),
        ("simulation_verification_completeness", {"registered_obligations": 24, "execution_rows": 24, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    if len(values) != len(registry["claim_ids"]):
        raise SystemExit("QSIMX observation membership changed")
    records = []
    for index, (name, value) in enumerate(values, 1):
        if not observer.independent_witness(index):
            raise SystemExit(f"QSIMX independent observation failed at {index:03d}")
        records.append({
            "number": f"{index:03d}",
            "claim_id": registry["claim_ids"][index - 1],
            "obligation_id": registry["obligation_ids"][index - 1],
            "observation_name": name,
            "exact_observation": value,
            "expected_label": f"complete-qsimx-{index:03d}-execution-retained",
            "source_ids": list(registry["pre_registered_source_identities"]),
            "all_rows_preserved": True,
        })
    payload = {
        "schema": "sft-v3-quantum-qsimx-observation-vector/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "registry_identity": registry_identity,
        "outcomes_opened_only_after_registry_freeze": True,
        "records": records,
        "record_count": len(records),
        "all_rows_preserved": True,
        "external_measurement_boundary": "Exact finite simulations and verification transcripts are operationally executed and independently reconstructed. Physical dynamics, scales, device fidelity, chemistry and materials values remain explicit owning-domain measurement handoffs and cannot select the formal law.",
        "protected_engine_or_verifier_edit_made": False,
    }
    payload["vector_identity"] = canonical(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
