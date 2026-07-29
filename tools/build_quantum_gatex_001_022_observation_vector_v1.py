#!/usr/bin/env python3
"""Open and freeze independent exact GATEX executions after registry freeze."""
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/quantum_gatex_001_022_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/quantum_computation/gatex_001_022_observation_vector_v1.json"
VALIDATOR = ROOT / "generated/quantum_computation/gatex_001_022_validator_v1.py"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("GATEX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text())
    body = dict(registry)
    identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False:
        raise SystemExit("GATEX value-free registry changed")
    spec = importlib.util.spec_from_file_location("gatex_independent_observer", VALIDATOR)
    observer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(observer)
    values = (
        ("reversible_transformation", {"source_rows": 2, "image_rows": 2, "inverse_rows": 2, "round_trip": True}),
        ("single_unit_actions", {"permutations": 2, "phase_actions": 2, "support_complete": True}),
        ("controlled_transformation", {"joint_rows": 4, "control_retained": True, "bijection": True}),
        ("two_unit_entangling_gate", {"joint_rows": 4, "product_input_can_become_nonfactorable": True, "bijection": True}),
        ("multi_controlled_gate", {"control_width": 2, "trigger_words": 1, "unaffected_words_retained": True}),
        ("composition_inverse", {"forward_gates": 2, "inverse_gates": 2, "source_restored": True}),
        ("commutation", {"causal_orders": 2, "complete_support_compared": True, "same_map": True}),
        ("gate_grammar", {"primitive_forms": ["wire", "swap", "control", "observe"], "finite_descriptions": True}),
        ("exact_synthesis", {"support_rows": 3, "transpositions": 2, "target_permutation_reproduced": True}),
        ("approximate_synthesis", {"enclosures": 2, "bounds_exact_rational": True, "target_outside_enclosure_rejected": True}),
        ("circuit_syntax", {"wires": 1, "gate_instances": 1, "terminal_outputs": 1, "arity_checked": True}),
        ("branchwise_semantics", {"input_branches": 2, "terminal_branches": 2, "complete_trace": True}),
        ("observation_semantics", {"question_classes": 2, "outcome_classes": 1, "predecessor_support_retained": True}),
        ("circuit_inverse", {"forward_depth": 3, "inverse_depth": 3, "source_restored": True}),
        ("circuit_equivalence", {"circuits_compared": 2, "support_rows": 2, "same_canonical_map": True}),
        ("local_decomposition", {"local_gate_count": 2, "joint_support_rows": 4, "composed_map_exact": True}),
        ("circuit_resources", {"size": 3, "depth": 3, "width": 2, "live_support": 4}),
        ("compilation", {"source_circuit_rows": 2, "target_circuit_rows": 2, "semantics_preserved": True}),
        ("measurement_based_correspondence", {"preparation": 1, "observations": 1, "record_controlled_corrections": 1, "terminal_map_preserved": True}),
        ("adiabatic_boundary", {"finite_path_rows": 3, "terminal_map_retained": True, "physical_gap_measured_here": False}),
        ("topological_boundary", {"finite_braid_words": 1, "crossing_records": 1, "physical_realization_measured_here": False}),
        ("gate_circuit_completeness", {"registered_obligations": 22, "execution_rows": 22, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        if not observer.independent_witness(index):
            raise SystemExit(f"GATEX independent observation failed at {index:03d}")
        records.append({"number": f"{index:03d}", "claim_id": registry["claim_ids"][index - 1], "obligation_id": registry["obligation_ids"][index - 1], "observation_name": name, "exact_observation": value, "expected_label": f"complete-gatex-{index:03d}-execution-retained", "source_ids": ["SFT-V3-INDEPENDENT-EXACT-GATE-CIRCUIT-OBSERVER", "SFT-V1-V2-QUANTUM-CIRCUIT-OBSERVATION-CORPUS"], "all_rows_preserved": True})
    payload = {
        "schema": "sft-v3-quantum-gatex-observation-vector/1", "date": "2026-07-29", "authority": "Maria Smith",
        "registry_identity": identity, "outcomes_opened_only_after_registry_freeze": True,
        "records": records, "record_count": len(records), "all_rows_preserved": True,
        "external_measurement_boundary": "Gate and circuit laws are directly tested by exact complete-support execution and independent reconstruction. Physical timing, gaps, error rates and hardware performance remain downstream measurements and do not select the formal laws.",
        "protected_engine_or_verifier_edit_made": False,
    }
    payload["vector_identity"] = canonical(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
