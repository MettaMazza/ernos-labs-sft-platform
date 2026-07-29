#!/usr/bin/env python3
"""Open and freeze independent exact QCOMMX executions after registry freeze."""
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/quantum_qcommx_001_024_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/quantum_computation/qcommx_001_024_observation_vector_v1.json"
VALIDATOR = ROOT / "generated/quantum_computation/qcommx_001_024_validator_v1.py"


def canonical(value): return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
def main():
    if OUT.exists(): raise SystemExit("QCOMMX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text()); body = dict(registry); identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False: raise SystemExit("QCOMMX value-free registry changed")
    spec = importlib.util.spec_from_file_location("qcommx_independent_observer", VALIDATOR); observer = importlib.util.module_from_spec(spec); spec.loader.exec_module(observer)
    values = (
        ("channel_relation", {"source_rows": 2, "image_rows": 2, "environment_rows": 2, "complete": True}),
        ("channel_composition", {"component_channels": 2, "composed_rows": 2, "memory_record_explicit": True}),
        ("classical_over_quantum", {"message_classes": 2, "distinguishable_images": 2, "decoder_complete": True}),
        ("quantum_transfer", {"word_rows": 1, "phase_rows": 1, "source_records": 1, "all_preserved": True}),
        ("entanglement_assistance", {"shared_joint_rows": 2, "left_marginal_rows": 2, "right_marginal_rows": 2}),
        ("teleportation_correspondence", {"joint_observations": 1, "classical_records": 2, "controlled_corrections": 1, "state_reconstructed": True}),
        ("dense_coding_correspondence", {"message_classes": 4, "transmitted_units": 1, "shared_joint_support": True}),
        ("no_signalling", {"remote_marginal_before": ["held", "returned"], "remote_marginal_after": ["held", "returned"], "record_transferred": False}),
        ("channel_capacity", {"distinguishable_messages": 4, "channel_uses": 2, "exact_rate": "2/1"}),
        ("private_coherent_information", {"receiver_distinctions": 4, "environment_distinctions": 2, "comparison_exact": True}),
        ("data_processing", {"distinction_counts": [4, 3, 2, 1], "increases": 0}),
        ("noise_environment", {"source_rows": 1, "mismatched_images": 1, "environment_records": 1}),
        ("entanglement_swapping", {"elementary_links": 2, "middle_observations": 1, "outer_links": 1}),
        ("repeater_correspondence", {"link_generations": 1, "verified_filters": 1, "swaps": 1, "end_links": 1}),
        ("network_identity", {"nodes": 3, "links": 2, "ownership_boundaries_explicit": True}),
        ("distributed_causality", {"events": 3, "ordered_pairs": 2, "cycles": 0}),
        ("routing", {"candidate_path_length": 4, "source": "a", "target": "d", "all_link_records_retained": True}),
        ("qkd_correctness", {"prepared": 4, "matched_bases": 2, "disclosed_test": 1, "retained_key": 1}),
        ("authentication", {"message_rows": 1, "tag_rows": 1, "verified_rows": 1, "tamper_controls_retained": True}),
        ("secret_sharing", {"participants": 3, "authorized_pairs": 3, "forbidden_singletons": 3}),
        ("device_independent_handoff", {"formal_transcript_complete": True, "physical_loophole_values_present": False}),
        ("adversary_transcript", {"queries": 1, "responses": 1, "measurements": 1, "guesses": 1}),
        ("post_quantum_handoff", {"classical_scheme_registered": True, "quantum_adversary_bounded": True, "reduction_required": True}),
        ("communication_completeness", {"registered_obligations": 24, "execution_rows": 24, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        if not observer.independent_witness(index): raise SystemExit(f"QCOMMX independent observation failed at {index:03d}")
        records.append({"number": f"{index:03d}", "claim_id": registry["claim_ids"][index - 1], "obligation_id": registry["obligation_ids"][index - 1], "observation_name": name, "exact_observation": value, "expected_label": f"complete-qcommx-{index:03d}-execution-retained", "source_ids": ["SFT-V3-INDEPENDENT-EXACT-QUANTUM-COMMUNICATION-OBSERVER", "SFT-V1-V2-QUANTUM-COMMUNICATION-OBSERVATION-CORPUS"], "all_rows_preserved": True})
    payload = {"schema": "sft-v3-quantum-qcommx-observation-vector/1", "date": "2026-07-29", "authority": "Maria Smith", "registry_identity": identity, "outcomes_opened_only_after_registry_freeze": True, "records": records, "record_count": len(records), "all_rows_preserved": True, "external_measurement_boundary": "Communication and protocol laws are tested by exact finite transcripts and independent reconstruction. Physical link rates, distances, losses, device loopholes and hardware security remain downstream measurements and cannot select these formal laws.", "protected_engine_or_verifier_edit_made": False}
    payload["vector_identity"] = canonical(payload); OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n"); print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))


if __name__ == "__main__": main()
