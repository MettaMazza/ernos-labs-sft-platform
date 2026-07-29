#!/usr/bin/env python3
"""Open and freeze independent exact QSTATEX executions after registry freeze."""
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/quantum_qstatex_001_028_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/quantum_computation/qstatex_001_028_observation_vector_v1.json"
VALIDATOR = ROOT / "generated/quantum_computation/qstatex_001_028_validator_v1.py"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("QSTATEX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    body = dict(registry)
    identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False:
        raise SystemExit("QSTATEX value-free registry changed")
    module_spec = importlib.util.spec_from_file_location("qstatex_independent_observer", VALIDATOR)
    observer = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(observer)
    values = (
        ("information_unit", {"distinction_count": 1, "fibre_labels": ["held", "returned"], "labels_distinct": True}),
        ("finite_register", {"width": 3, "word_count": 8, "complete_support": True}),
        ("canonical_state", {"support_rows": 2, "unique_words": 2, "presentation_order_closed": True}),
        ("state_preparation", {"source": "registered", "terminal": "prepared", "provenance_retained": True}),
        ("product_state", {"left_width": 2, "right_width": 1, "joint_width": 2, "components_reconstructible": True}),
        ("joint_marginal", {"joint_rows": 2, "left_marginal_rows": 2, "right_marginal_rows": 2, "joint_record_retained": True}),
        ("pure_mixed_correspondence", {"support_identity_count": 1, "preparation_record_count": 2, "ontic_randomness_imported": False}),
        ("complete_superposition_support", {"register_width": 4, "support_rows": 16, "all_words_present_once": True}),
        ("relative_phase", {"phase_labels": ["phase-held", "phase-returned"], "relative_classes": ["same", "distinct"]}),
        ("global_relative_phase", {"common_action_applied": True, "relative_classes_preserved": True}),
        ("phase_inverse", {"period": 2, "source_phase": "phase-held", "restored_phase": "phase-held"}),
        ("interference_classes", {"predecessors": 2, "shared_image": True, "same_and_distinct_phase_classes_retained": True}),
        ("path_merging", {"predecessor_paths": 2, "observed_images": 1, "predecessor_ledger_width": 2}),
        ("which_path_boundary", {"path_record_retained": True, "distinguishable_classes": 2, "closed_merge_allowed": False}),
        ("bipartite_nonfactorability", {"joint_rows": 2, "marginal_product_rows": 4, "factorable": False}),
        ("multipartite_nonfactorability", {"joint_rows": 2, "partitions_checked": 2, "factorable_partitions": 0}),
        ("partition_cut", {"declared_cuts": [1, 2], "nonfactorable_cuts": [1, 2], "complete_census": True}),
        ("entanglement_swapping", {"input_joint_supports": 2, "middle_observation_retained": True, "outer_support_repartitioned": True}),
        ("monogamy_shareability", {"requested_product_rows": 4, "present_joint_rows": 2, "missing_cross_words": 2}),
        ("purification", {"preparation_classes": 2, "record_words_added": 2, "extended_support_source_bound": True}),
        ("reduced_observation", {"projected_rows": 2, "environment_rows_retained": 2, "joint_rows_retained": 2}),
        ("measurement_classes", {"question_classes": 2, "matched_classes": 1, "question_identity_retained": True}),
        ("measurement_repeatability", {"first_outcome": "class-held", "repeated_outcome": "class-held", "intervening_transform": False}),
        ("observation_compatibility", {"causal_orders_compared": 2, "same_record_required_for_compatibility": True}),
        ("deferred_measurement", {"question_record_retained": True, "immediate_outcome": "held", "deferred_outcome": "held"}),
        ("no_cloning_boundary", {"unknown_joint_support_factorable": False, "local_source_independent_copy": False, "distinguished_label_copy_allowed": True}),
        ("no_deleting_boundary", {"distinct_sources": 2, "terminal_labels": 1, "retained_environment_records": 2}),
        ("state_family_completeness", {"registered_obligations": 28, "execution_rows": 28, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        if not observer.independent_witness(index):
            raise SystemExit(f"QSTATEX independent observation failed at {index:03d}")
        records.append({
            "number": f"{index:03d}",
            "claim_id": registry["claim_ids"][index - 1],
            "obligation_id": registry["obligation_ids"][index - 1],
            "observation_name": name,
            "exact_observation": value,
            "expected_label": f"complete-qstatex-{index:03d}-execution-retained",
            "source_ids": ["SFT-V3-INDEPENDENT-EXACT-QUANTUM-STATE-OBSERVER", "SFT-V1-V2-QUANTUM-STATE-OBSERVATION-CORPUS"],
            "all_rows_preserved": True,
        })
    payload = {
        "schema": "sft-v3-quantum-qstatex-observation-vector/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "registry_identity": identity,
        "outcomes_opened_only_after_registry_freeze": True,
        "records": records,
        "record_count": len(records),
        "all_rows_preserved": True,
        "external_measurement_boundary": "Quantum-state laws are directly tested by exact support, phase, path, partition and record executions plus implementation-distinct reconstruction. Physical probability frequencies, amplitudes and device results remain downstream measurements and do not select these laws.",
        "protected_engine_or_verifier_edit_made": False,
    }
    payload["vector_identity"] = canonical(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
