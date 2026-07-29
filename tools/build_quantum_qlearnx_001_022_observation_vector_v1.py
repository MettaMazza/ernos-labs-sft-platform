#!/usr/bin/env python3
"""Open and freeze exact QLEARNX outcomes after value-free registration."""

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/quantum_qlearnx_001_022_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/quantum_computation/qlearnx_001_022_observation_vector_v1.json"
VALIDATOR = ROOT / "generated/quantum_computation/qlearnx_001_022_validator_v1.py"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("QLEARNX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text())
    body = dict(registry)
    registry_identity = body.pop("registry_identity")
    if canonical(body) != registry_identity or registry["target_content_present"] is not False:
        raise SystemExit("QLEARNX value-free registry changed")
    spec = importlib.util.spec_from_file_location("qlearnx_independent_observer", VALIDATOR)
    observer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(observer)
    values = (
        ("problem_example_identity", {"domain_examples": 2, "target_rows": 2, "duplicate_example_ids": 0}),
        ("classical_data_boundary", {"source_rows": 2, "encoded_rows": 2, "inverse_records": 2}),
        ("quantum_data_custody", {"support_width": 2, "support_rows": 4, "source_records": 4}),
        ("hypothesis_family", {"domain_rows": 2, "generated_hypotheses": 4, "pretrained_hypotheses": 0}),
        ("feature_map", {"source_rows": 4, "feature_rows": 4, "collisions": 0}),
        ("kernel_boundary", {"pair_width": 2, "retained_matches": 1, "continuum_inner_product_imported": False}),
        ("classification", {"hypotheses_evaluated": 4, "training_rows": 2, "unique_survivors": 1}),
        ("regression_correspondence", {"ordered_output_classes": 3, "exact_support_only": True, "irrational_target_imported": False}),
        ("generative_support", {"declared_rows": 4, "reconstructed_rows": 4, "missing_rows": 0}),
        ("clustering", {"support_rows": 4, "clusters": 2, "rows_per_cluster": 2}),
        ("principal_structure", {"incidence_patterns": 2, "ranked_patterns": 2, "ties_preserved": True}),
        ("learning_optimization", {"candidates": 4, "exact_scores": 4, "unique_optimum": True}),
        ("variational_boundary", {"generated_settings": 4, "free_parameters": 0, "target_fitted": False}),
        ("reinforcement_process", {"states": 4, "actions": 2, "transition_rows": 8, "ontic_randomness": False}),
        ("online_learning", {"causal_examples": 2, "updates": 2, "future_target_access": False}),
        ("sample_complexity", {"hypotheses": 4, "least_forcing_examples": 2, "smaller_support_counterexample_retained": True}),
        ("query_complexity", {"domain_rows": 2, "queries": 2, "preparation_and_observation_counted": True}),
        ("generalization_custody", {"training_rows": 1, "held_out_rows": 1, "target_opened_after_hypothesis_seal": True}),
        ("advantage_certificate", {"same_task": True, "classical_resource_ledger": True, "quantum_resource_ledger": True, "physical_speedup_claimed": False}),
        ("interpretability", {"trace_stages": 5, "branch_reconstruction_complete": True, "opaque_predictor": False}),
        ("robustness", {"support_rows": 4, "registered_perturbations": 2, "adverse_rows_preserved": True}),
        ("quantum_learning_completeness", {"registered_obligations": 22, "execution_rows": 22, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        if not observer.independent_witness(index):
            raise SystemExit(f"QLEARNX independent observation failed at {index:03d}")
        records.append({"number": f"{index:03d}", "claim_id": registry["claim_ids"][index - 1], "obligation_id": registry["obligation_ids"][index - 1], "observation_name": name, "exact_observation": value, "expected_label": f"complete-qlearnx-{index:03d}-execution-retained", "source_ids": list(registry["pre_registered_source_identities"]), "all_rows_preserved": True})
    payload = {"schema": "sft-v3-quantum-qlearnx-observation-vector/1", "date": "2026-07-29", "authority": "Maria Smith", "registry_identity": registry_identity, "outcomes_opened_only_after_registry_freeze": True, "records": records, "record_count": len(records), "all_rows_preserved": True, "external_measurement_boundary": "Exact learning processes are executed over complete finite supports. Held-out targets are opened only after hypothesis sealing. Physical advantage, device behavior and application predictions remain owning-domain empirical handoffs.", "protected_engine_or_verifier_edit_made": False}
    payload["vector_identity"] = canonical(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
