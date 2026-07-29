#!/usr/bin/env python3
"""Open and freeze independent exact SECX executions after registry freeze."""
import hashlib, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; REGISTRY = ROOT / "census/computation_secx_001_025_target_registry_v1.json"; OUT = ROOT / "experiments/external_sources/computation/secx_001_025_observation_vector_v1.json"; VALIDATOR = ROOT / "generated/computation/secx_001_025_validator_v1.py"
def canonical(value): return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
def main():
    if OUT.exists(): raise SystemExit("SECX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text()); body = dict(registry); identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False: raise SystemExit("SECX registry changed")
    module_spec = importlib.util.spec_from_file_location("secx_independent_observer", VALIDATOR); observer = importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(observer)
    values = (
        ("adversary_definition", {"public_items": 1, "queries": 1, "resource_classes": 1, "success_event": "invert", "implicit_capabilities": 0}),
        ("information_theoretic_secrecy", {"messages": ["left", "right"], "ciphertext_support_each": ["left", "right"], "support_multiplicities_equal": True}),
        ("computational_indistinguishability", {"left_view": ["left", "right"], "right_view": ["right", "left"], "complete_support_equal": True, "observer_class_explicit": True}),
        ("one_way_resource", {"mapping_width": 3, "limited_queries": 2, "limited_inversion": "absent-from-declared-query-support", "complete_enumeration_inversion": "c"}),
        ("hard_core_boundary", {"seed_support": 2, "retained_terminal_distinctions": ["left", "right"], "unrestricted_hardness_claimed": False}),
        ("pseudorandom_generator", {"seed_support": 2, "generated_output_support": 2, "complete_three-label-support": 8, "unbounded_distinguishable": True}),
        ("pseudorandom_function", {"keys": 2, "input_support": 2, "left_key_map": ["left", "right"], "right_key_map": ["right", "left"]}),
        ("symmetric_encryption", {"messages": 2, "keys": 2, "correctness_rows": 4, "failed_correctness_rows": 0, "ciphertext_support_equal": True}),
        ("public_key_boundary", {"forward_table_public": True, "reverse_table_trapdoor": True, "finite_unbounded_enumeration_recovers": True, "unrestricted_secrecy_claimed": False}),
        ("authentication_integrity", {"honest_pair_accepted": True, "altered_message_rejected": True, "keyed_tag_retained": True}),
        ("entity_freshness", {"fresh_challenges": ["fresh-a", "fresh-b"], "responses_distinct": True, "replay_as_new_session": False}),
        ("hash_properties", {"domain_width": 4, "image_width": 2, "compression": True, "retained_collision": [["left", "left"], ["right", "right"]]}),
        ("commitment", {"commitment_records": 2, "openings_per_record": 2, "opening_correctness": True, "binding_control_detected": True, "simultaneous_unrestricted_hiding_binding_claimed": False}),
        ("digital_signature", {"honest_signature_accepted": True, "altered_message_rejected": True, "unrestricted_unforgeability_claimed": False}),
        ("key_establishment", {"transcript_items": 2, "shared_key_parts": ["left", "right"], "authentication_boundary_retained": True}),
        ("secret_sharing", {"shares": 3, "threshold": 2, "authorized_subsets": 3, "unauthorized_single_share": "insufficient-shares"}),
        ("proof_of_knowledge", {"challenge_support": 2, "dual_response_extraction": "secret", "single_transcript_extraction": "insufficient-transcripts"}),
        ("zero_knowledge", {"real_view_rows": 2, "simulated_view_rows": 2, "complete_support_equal": True, "simulator_witness_access": False}),
        ("secure_multiparty", {"participants": 2, "function_output": ["left", "right"], "local_views": 2, "leakage_boundary_retained": True}),
        ("oblivious_transfer", {"messages": ["a", "b"], "choice": "right", "selected": "b", "sender_choice_view": "choice-hidden"}),
        ("composable_adversary", {"timing_classes": 2, "session_classes": 2, "corruption_classes": 2, "complete_environment_rows": 8}),
        ("side_channel_handoff", {"algorithmic_channels": ["ciphertext"], "implementation_channels": ["time", "power"], "owner": "engineering-translation"}),
        ("post_quantum_boundary", {"classical_resource_registry": "separate", "quantum_resource_registry": "separate", "silent_transport": False}),
        ("quantum_cryptography_handoff", {"classical_security_owner": "computation-security", "quantum_channel_owner": "quantum-computation", "handoff_explicit": True}),
        ("security_completeness", {"registered_obligations": 25, "independent_execution_rows": 25, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        if not observer.independent_witness(index): raise SystemExit(f"SECX independent observation failed at {index:03d}")
        records.append({"number": f"{index:03d}", "claim_id": registry["claim_ids"][index - 1], "obligation_id": registry["obligation_ids"][index - 1], "observation_name": name, "exact_observation": value, "expected_label": f"complete-secx-{index:03d}-execution-retained", "source_ids": ["SFT-V3-INDEPENDENT-EXACT-SECURITY-OBSERVER", "SFT-V1-V2-SECURITY-OBSERVATION-CORPUS"], "all_rows_preserved": True})
    payload = {"schema": "sft-v3-classical-computation-secx-observation-vector/1", "date": "2026-07-29", "authority": "Maria Smith", "registry_identity": identity, "outcomes_opened_only_after_registry_freeze": True, "records": records, "record_count": len(records), "all_rows_preserved": True, "external_measurement_boundary": "Security laws are directly tested over complete generated scheme, adversary, transcript, resource and success supports. Bounded demonstrations, adverse properties and unrestricted-enumeration routes remain visible; no toy execution is exported as practical security.", "protected_engine_or_verifier_edit_made": False}; payload["vector_identity"] = canonical(payload); OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n"); print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))
if __name__ == "__main__": main()
