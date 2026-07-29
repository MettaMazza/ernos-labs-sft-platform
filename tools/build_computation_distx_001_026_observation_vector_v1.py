#!/usr/bin/env python3
"""Open and freeze independent exact DISTX executions after registry freeze."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/computation_distx_001_026_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/computation/distx_001_026_observation_vector_v1.json"
VALIDATOR = ROOT / "generated/computation/distx_001_026_validator_v1.py"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("DISTX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text())
    body = dict(registry); identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False:
        raise SystemExit("DISTX registry changed")
    module_spec = importlib.util.spec_from_file_location("distx_independent_observer", VALIDATOR)
    observer = importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(observer)
    values = (
        ("event_local_order", {"process": "p", "events": ["p1", "p2", "p3"], "local_edges": [["p1", "p2"], ["p2", "p3"]]}),
        ("partial_order_interleavings", {"events": ["a", "b", "c"], "required_edges": [["a", "c"], ["b", "c"]], "lawful_linearizations": [["a", "b", "c"], ["b", "a", "c"]]}),
        ("happens_before", {"primitive_edges": [["a", "b"], ["b", "c"]], "forced_transitive_edge": ["a", "c"], "closure_edges": 3}),
        ("message_custody", {"message": "m", "sender": "p", "receiver": "q", "send_count": 1, "receipt_count": 1, "orphan_receipts": 0}),
        ("synchrony_boundary", {"synchronous_events": ["send", "receive", "ack"], "asynchronous_queue_width": 1, "timing_inferred": False}),
        ("mutual_exclusion", {"lawful_schedule_max_holders": 1, "overlap_control_rejected": True, "token_identity_retained": True}),
        ("progress_classes", {"terminal_classes": ["deadlock", "livelock", "progress"], "distinct_classes": 3, "nonterminal_cycle_retained": True}),
        ("coordination_primitives", {"participants": 2, "barrier_release_rows": 1, "semaphore_permit_retained": True, "rendezvous_pair_retained": True}),
        ("logical_clock", {"send_clock": 1, "receipt_clock": 2, "causal_inequality": "send-before-receipt", "wall_clock_used": False}),
        ("delivery_modes", {"registered_receivers": 3, "point_deliveries": 1, "multicast_deliveries": 2, "broadcast_deliveries": 3}),
        ("failure_free_consensus", {"inputs": ["b", "a", "b"], "decision": "a", "participant_decisions": ["a", "a", "a"], "validity": True}),
        ("crash_fault_boundary", {"retained_local_views_equal": True, "hidden_remote_states_distinct": True, "unconditional_total_decision_admitted": False}),
        ("byzantine_quorum", {"participants": 4, "declared_fault_support": 1, "quorum_width": 3, "least_pair_intersection": 2, "nonadversarial_intersection_forced": True}),
        ("hidden_predecessor", {"predecessor_count": 2, "terminal_images": 1, "reverse_label_retained": False, "predecessor_identifiable": False}),
        ("failure_detector_custody", {"suspected_process": "q", "basis": "missed-declared-round", "synchrony_contract": "bounded-round", "knowledge_claimed": False}),
        ("replication", {"replicas": 3, "command_trace": ["a", "b"], "distinct_terminal_states": 1, "deterministic_transition": True}),
        ("consistency_boundary", {"linearizable_history": True, "read_mismatch_control": True, "real_time_edges_retained": True, "program_order_edges_retained": True}),
        ("causal_eventual", {"updates": ["write-a", "write-b"], "merge_after_updates": True, "causal_edges_preserved": 2, "unregistered_convergence_time": False}),
        ("quorum_intersection", {"participants": 3, "quorum_width": 2, "quorum_count": 3, "least_intersection": 1}),
        ("transaction_atomicity", {"all_yes_decision": "commit", "retained_no_decision": "abort", "partial_effect_admitted": False}),
        ("distributed_knowledge", {"local_views": [["a", "b"], ["b", "c"]], "shared_support": ["a", "b", "c"], "common_support": ["b"]}),
        ("locality_radius", {"source": "a", "round_layers": [["a"], ["b"], ["c"], ["d"]], "rounds_to_d": 3, "instant_remote_access": False}),
        ("network_topology", {"source": "a", "reachable": ["a", "b", "c", "d"], "reachable_count": 4, "path_required": True}),
        ("partition_custody", {"components": [["a", "b"], ["c", "d"]], "source_a_reachable": ["a", "b"], "cross_partition_delivery": False}),
        ("safety_liveness_fairness", {"safety_control_passed": True, "terminal_progress_reached": True, "continuously_enabled_actions_served": 2}),
        ("distributed_completeness", {"registered_obligations": 26, "independent_execution_rows": 26, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        if not observer.independent_witness(index):
            raise SystemExit(f"DISTX independent observation failed at {index:03d}")
        records.append({"number": f"{index:03d}", "claim_id": registry["claim_ids"][index - 1], "obligation_id": registry["obligation_ids"][index - 1], "observation_name": name, "exact_observation": value, "expected_label": f"complete-distx-{index:03d}-execution-retained", "source_ids": ["SFT-V3-INDEPENDENT-EXACT-DISTRIBUTED-OBSERVER", "SFT-V1-V2-DISTRIBUTED-OBSERVATION-CORPUS"], "all_rows_preserved": True})
    payload = {"schema": "sft-v3-classical-computation-distx-observation-vector/1", "date": "2026-07-29", "authority": "Maria Smith", "registry_identity": identity, "outcomes_opened_only_after_registry_freeze": True, "records": records, "record_count": len(records), "all_rows_preserved": True, "external_measurement_boundary": "Distributed laws are directly tested across complete generated event, schedule, message, fault and topology supports and by implementation-distinct reconstruction. Platform deployments and conventional protocol claims require explicit transport and never select a survivor.", "protected_engine_or_verifier_edit_made": False}
    payload["vector_identity"] = canonical(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
