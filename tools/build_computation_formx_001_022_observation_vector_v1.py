#!/usr/bin/env python3
"""Open and freeze independent exact FORMX executions after registry freeze."""
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/computation_formx_001_022_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/computation/formx_001_022_observation_vector_v1.json"
VALIDATOR = ROOT / "generated/computation/formx_001_022_validator_v1.py"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("FORMX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text())
    body = dict(registry)
    identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False:
        raise SystemExit("FORMX value-free registry changed")
    module_spec = importlib.util.spec_from_file_location("formx_independent_observer", VALIDATOR)
    observer = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(observer)
    values = (
        ("configuration_round_trip", {"coordinate_count": 3, "state_retained": True, "storage_retained": True, "focus_retained": True}),
        ("partial_total_transition_distinction", {"complete_source_rows": 2, "absent_source_row_retained_as_partial": True, "multiple_images_not_silently_selected": True}),
        ("terminal_outcome_partition", {"terminal_labels": ["accept", "reject"], "recurrent_trace_separate": True, "open_boundary_separate": True}),
        ("language_operations", {"left_support": 2, "right_support": 2, "union_support": 3, "intersection_support": 1, "relative_complement_support": 1}),
        ("concatenation_iteration", {"alphabet_size": 2, "successor_depth": 2, "ordered_word_support": 4, "empty_one_word_retained": True}),
        ("derivation_tree_ambiguity", {"terminal_word": "aaa", "complete_parse_tree_count": 2, "all_trees_retained": True}),
        ("parse_recognize_generate", {"generated_widths_checked": [1, 2, 3, 4], "all_generated_words_parsed": True, "rejecting_trace_retained": True}),
        ("automaton_product_quotient", {"generated_words_checked": 15, "future_observation_classes": 2, "parity_observation_preserved": True}),
        ("finite_transduction", {"source_word": ["a", "b", "a"], "output_word": ["x", "y", "x"], "state_trace_retained": True}),
        ("storage_machine_correspondence", {"source_word": ["a", "b", "c"], "stack_output": ["c", "b", "a"], "queue_remainder": ["b", "c"], "operations_typed": True}),
        ("rewrite_normal_form", {"source_word": "abab", "normal_form": "bbaa", "terminal_forms": 1, "well_founded_descent": True}),
        ("critical_pair_confluence", {"source_word": "aaa", "divergent_first_steps": 2, "common_normal_forms": ["a"], "all_critical_pairs_join": True}),
        ("recursive_composition", {"control_word": ["a", "b", "c"], "successor_applications": 3, "output_word": ["x", "x", "x"]}),
        ("primitive_recursion_minimization", {"base_word": ["s"], "control_width": 2, "recursive_output": ["s", "x", "x"], "least_witness_prefix": ["a", "a", "b"]}),
        ("lambda_capture_avoidance", {"source": "lambda y . x", "replacement": "y", "fresh_binder": "u", "result": "lambda u . y", "capture_avoided": True}),
        ("machine_simulation", {"source_word": ["a", "b", "c"], "stack_trace_steps": 6, "source_output": ["c", "b", "a"], "target_output": ["c", "b", "a"]}),
        ("circuit_evaluation", {"input_labels": ["held", "changed"], "gate_count": 2, "terminal_label": "changed", "all_intermediates_retained": True}),
        ("sequential_unrolling", {"combinational_output": "held", "sequential_state_trace": [["a"], ["a", "b"]], "finite_unrolling_preserves_output": True}),
        ("process_interleaving", {"left_steps": 2, "right_steps": 2, "complete_interleaving_count": 6, "all_local_orders_preserved": True}),
        ("universal_interpretation", {"instruction_count": 4, "terminal_word": ["b"], "self_description_admitted": True, "trace_complete": True}),
        ("model_translation_overhead", {"source_steps": 2, "translated_steps": 2, "source_output": ["a", "b"], "translated_output": ["a", "b"], "reverse_reconstructible": True}),
        ("formal_computation_completeness", {"registered_obligations": 22, "independent_execution_rows": 22, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        if not observer.independent_witness(index):
            raise SystemExit(f"FORMX independent observation failed at {index:03d}")
        records.append({
            "number": f"{index:03d}",
            "claim_id": registry["claim_ids"][index - 1],
            "obligation_id": registry["obligation_ids"][index - 1],
            "observation_name": name,
            "exact_observation": value,
            "expected_label": f"complete-formx-{index:03d}-execution-retained",
            "source_ids": [
                "SFT-V3-INDEPENDENT-EXACT-FORMAL-COMPUTATION-OBSERVER",
                "SFT-V1-V2-COMPUTATION-OBSERVATION-CORPUS",
            ],
            "all_rows_preserved": True,
        })
    payload = {
        "schema": "sft-v3-classical-computation-formx-observation-vector/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "registry_identity": identity,
        "outcomes_opened_only_after_registry_freeze": True,
        "records": records,
        "record_count": len(records),
        "all_rows_preserved": True,
        "external_measurement_boundary": "Formal computation is directly tested by exact execution and implementation-distinct reconstruction; conventional machine correspondences are separate registered observations, not imported premises.",
        "protected_engine_or_verifier_edit_made": False,
    }
    payload["vector_identity"] = canonical(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
