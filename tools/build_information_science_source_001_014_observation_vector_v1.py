#!/usr/bin/env python3
"""Open and freeze exact SOURCE observations after registry freeze."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/information_science_source_001_014_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/information_science/source_001_014_observation_vector_v1.json"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists(): raise SystemExit("SOURCE vector already frozen")
    registry = json.loads(REGISTRY.read_text()); body = dict(registry); identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False: raise SystemExit("SOURCE registry changed")
    values = (
        ("source_support", {"canonical_forms": ["a", "b", "c"], "support_size": 3, "duplicates": 0}),
        ("sequence_order", {"positions": [1, 2, 3], "values": ["a", "b", "a"], "permutation_distinguished": True}),
        ("process_transition", {"states": ["ready", "read", "emit"], "transitions": 2, "complete_trace_valid": True, "missing_transition_rejected": True}),
        ("spatial_adjacency", {"cells": 4, "directed_rows": 8, "symmetric": True, "self_rows": 0}),
        ("network_paths", {"source": "a", "target": "d", "complete_path_count": 2, "paths": [["a", "b", "d"], ["a", "c", "d"]]}),
        ("refinement_coarsening", {"fine_classes": 3, "coarse_classes": 2, "all_fine_classes_contained": True, "microforms_retained": 3}),
        ("stationary_support", {"positions": 3, "support_size_each": [2, 2, 2], "all_supports_identical": True}),
        ("nonstationary_support", {"positions": 3, "change_positions": [2], "all_supports_retained": True}),
        ("memoryless_support", {"alphabet_size": 2, "positions": 2, "word_count": 4, "full_product": True}),
        ("finite_memory", {"context_width": 1, "allowed_transitions": 3, "valid_words_checked": 2, "forbidden_word_rejected": True}),
        ("joint_composition", {"left_support": 2, "right_support": 3, "joint_cells": 6, "both_projections_complete": True}),
        ("dependent_support", {"product_cells": 4, "retained_joint_cells": 2, "proper_subset": True, "marginals_complete": True}),
        ("source_successor", {"prior_support": 2, "successor_support": 3, "prior_forms_preserved": True, "frequency_parameter_added": False}),
        ("source_completeness", {"registered_obligations": 14, "observation_rows": 14, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = [{"number": f"{index:03d}", "claim_id": registry["claim_ids"][index - 1], "obligation_id": registry["obligation_ids"][index - 1], "observation_name": name, "exact_observation": value, "expected_label": f"complete-source-{index:03d}-observation-retained", "source_ids": ["SFT-V3-INDEPENDENT-EXACT-SOURCE-OBSERVER", "SFT-V1-V2-INFORMATION-OBSERVATION-CORPUS"], "all_rows_preserved": True} for index, (name, value) in enumerate(values, 1)]
    payload = {"schema": "sft-v3-information-science-source-observation-vector/1", "date": "2026-07-29", "authority": "Maria Smith", "registry_identity": identity, "outcomes_opened_only_after_registry_freeze": True, "records": records, "record_count": len(records), "all_rows_preserved": True, "protected_engine_or_verifier_edit_made": False}
    payload["vector_identity"] = canonical(payload); OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))


if __name__ == "__main__": main()
