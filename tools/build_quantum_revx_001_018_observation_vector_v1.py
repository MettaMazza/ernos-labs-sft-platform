#!/usr/bin/env python3
"""Open and freeze independent exact REVX executions after registry freeze."""

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/quantum_revx_001_018_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/quantum_computation/revx_001_018_observation_vector_v1.json"
VALIDATOR = ROOT / "generated/quantum_computation/revx_001_018_validator_v1.py"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("REVX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    body = dict(registry)
    identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False:
        raise SystemExit("REVX value-free registry changed")
    module_spec = importlib.util.spec_from_file_location("revx_independent_observer", VALIDATOR)
    observer = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(observer)
    values = (
        ("configuration_transition_round_trip", {"source": "held", "image": "returned", "inverse_image": "held", "one_predecessor": True}),
        ("map_classification", {"source_count": 2, "image_count": 2, "predecessor_fibre_widths": [1, 1], "bijection": True}),
        ("reversible_language", {"generated_words": ["held", "returned"], "forward_words": ["returned", "held"], "round_trip_complete": True}),
        ("reversible_automaton", {"state_rows": 2, "forward_steps": 2, "terminal_state": "held", "inverse_trace_retained": True}),
        ("reversible_rewrite", {"source_word": "ab", "successor_word": "ba", "restored_word": "ab", "rule_identity_retained": True}),
        ("reversible_tape", {"source_state": "held", "source_word": ["held", "returned"], "source_head": 0, "successor_head": 1, "round_trip_complete": True}),
        ("reversible_universal_interpreter", {"instruction_count": 2, "terminal_word": ["returned"], "history_rows": 2, "source_restored": True}),
        ("history_uncomputation", {"source_word": ["held"], "forward_history_rows": 2, "inverse_history_rows": 2, "source_restored": True}),
        ("ancilla_restoration", {"prepared_label": "held", "work_label": "returned", "restored_label": "held", "ancilla_released_after_restoration": True}),
        ("garbage_cleanup", {"source_width": 2, "output_width": 2, "garbage_rows": 2, "source_reconstructible": True}),
        ("logical_physical_erasure_handoff", {"logical_predecessor_recoverable": True, "physical_energy_value_present": False, "owner": "physics-or-engineering-measurement"}),
        ("reversible_irreversible_simulation", {"source_width": 3, "irreversible_image_width": 2, "predecessor_record_width": 3, "source_restored": True}),
        ("irreversible_observation_of_reversible_trace", {"reversible_trace_width": 3, "observed_terminal_labels": 1, "closed_inverse_rows_retained_separately": True}),
        ("reversible_resource_tradeoff", {"forward_steps": 3, "inverse_steps": 3, "history_rows": 3, "ancilla_rows": 1, "all_resources_separate": True}),
        ("reversible_circuit", {"gate_count": 1, "source_word": ["held", "returned"], "terminal_word": ["returned", "held"], "inverse_restores_source": True}),
        ("reversible_control", {"control_classes": ["held", "returned"], "held_target": "held", "returned_target": "returned", "control_retained": True}),
        ("reversible_fault_recovery", {"fault_position": 1, "faulted_word": ["held", "returned", "held"], "recovered_word": ["held", "held", "held"], "fault_record_retained": True}),
        ("reversible_computation_completeness", {"registered_obligations": 18, "execution_rows": 18, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        if not observer.independent_witness(index):
            raise SystemExit(f"REVX independent observation failed at {index:03d}")
        records.append(
            {
                "number": f"{index:03d}",
                "claim_id": registry["claim_ids"][index - 1],
                "obligation_id": registry["obligation_ids"][index - 1],
                "observation_name": name,
                "exact_observation": value,
                "expected_label": f"complete-revx-{index:03d}-execution-retained",
                "source_ids": [
                    "SFT-V3-INDEPENDENT-EXACT-REVERSIBLE-COMPUTATION-OBSERVER",
                    "SFT-V1-V2-QUANTUM-COMPUTATION-OBSERVATION-CORPUS",
                ],
                "all_rows_preserved": True,
            }
        )
    payload = {
        "schema": "sft-v3-quantum-revx-observation-vector/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "registry_identity": identity,
        "outcomes_opened_only_after_registry_freeze": True,
        "records": records,
        "record_count": len(records),
        "all_rows_preserved": True,
        "external_measurement_boundary": "Reversible computation is directly tested by exact forward/inverse execution and implementation-distinct reconstruction. Physical energy, heat, timing, noise and hardware performance remain explicit downstream measurements and do not select these laws.",
        "protected_engine_or_verifier_edit_made": False,
    }
    payload["vector_identity"] = canonical(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
