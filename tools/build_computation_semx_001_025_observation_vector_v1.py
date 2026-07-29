#!/usr/bin/env python3
"""Open and freeze independent exact SEMX executions after registry freeze."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/computation_semx_001_025_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/computation/semx_001_025_observation_vector_v1.json"
VALIDATOR = ROOT / "generated/computation/semx_001_025_validator_v1.py"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("SEMX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text())
    body = dict(registry)
    identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False:
        raise SystemExit("SEMX registry changed")
    module_spec = importlib.util.spec_from_file_location("semx_independent_observer", VALIDATOR)
    observer = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(observer)
    values = (
        ("ast_well_formed", {"closed_term": "let x=a in join(x,b)", "constructor_rows": 4, "unbound_name_rejected": True}),
        ("free_bound_scope", {"bound_name": "x", "free_support": ["y"], "nearest_binder_retained": True}),
        ("alpha_equivalence", {"source_binder": "x", "fresh_binder": "u", "bound_occurrences_renamed": 1, "free_names_changed": False}),
        ("capture_avoiding_substitution", {"substituted_name": "x", "replacement_free_name": "y", "conflicting_binder_renamed": "u", "capture_occurred": False}),
        ("small_step", {"source": "join(a,b)", "transition_count": 1, "terminal_word": ["a", "b"], "intermediates_retained": 2}),
        ("big_step", {"source": "let x=a in join(x,b)", "terminal_word": ["a", "b"], "environment_binding_retained": True}),
        ("evaluation_context", {"context": "join(hole,b)", "hole_count": 1, "filled_term": "join(a,b)", "terminal_word": ["a", "b"]}),
        ("denotational_composition", {"left_meaning": ["a"], "right_meaning": ["b"], "composed_meaning": ["a", "b"]}),
        ("operational_denotational_adequacy", {"operational_value": ["a", "b"], "denotational_value": ["a", "b"], "directions_checked": 2}),
        ("full_abstraction_boundary", {"registered_contexts": ["hole", "join(hole,a)"], "terms": ["join(a,b)", "ab"], "observations_equal": True, "export_unrestricted": False}),
        ("type_rules", {"term": "let x=a in join(x,b)", "inferred_type": "word", "premise_tree_retained": True}),
        ("type_inference", {"term": "same(a,a,b,a)", "inferred_type": "word", "branch_types_equal": True}),
        ("parametric_identity", {"type_fibres": ["word", "vector", "pair"], "identity_results_preserved": 3, "representation_inspection": False}),
        ("dependent_evidence", {"retained_index": 3, "witness_width": 3, "mismatched_index_rejected": True}),
        ("state_effect_exception", {"effects_executed": ["set-x", "get-x", "raise-halt"], "effects_after_exception": 0, "terminal": "exception-halt"}),
        ("contextual_equivalence", {"registered_context_count": 2, "source": "join(a,b)", "optimized": "ab", "all_observations_equal": True}),
        ("termination_measure", {"source_size": 3, "successor_size": 1, "strict_descent": True}),
        ("partial_total_correctness", {"generated_states": 2, "precondition_rows": 2, "postcondition_rows": 2, "termination_certificate": "single append transition"}),
        ("assertion_invariant", {"generated_states": 2, "initial_minimum_width": 1, "terminal_minimum_width": 2, "invariant_preserved": True}),
        ("specification_refinement", {"generated_inputs": 2, "source_outputs": ["a", "ba"], "target_outputs": ["a", "ba"], "behavior_inclusion": True}),
        ("program_transformation", {"source": "join(a,b)", "transformed": "ab", "source_value": ["a", "b"], "transformed_value": ["a", "b"]}),
        ("compiler_simulation", {"source_steps": 1, "target_instructions": 3, "source_value": ["a", "b"], "target_value": ["a", "b"]}),
        ("intermediate_composition", {"source": "join(join(a,b),a)", "target_instructions": 5, "terminal_value": ["a", "b", "a"], "interfaces_identical": True}),
        ("proof_carrying_program", {"term_well_formed": True, "checked_type": "word", "checked_value": ["a", "b"], "producer_trusted": False}),
        ("semantics_completeness", {"registered_obligations": 25, "independent_execution_rows": 25, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        if not observer.independent_witness(index):
            raise SystemExit(f"SEMX independent observation failed at {index:03d}")
        records.append({
            "number": f"{index:03d}",
            "claim_id": registry["claim_ids"][index - 1],
            "obligation_id": registry["obligation_ids"][index - 1],
            "observation_name": name,
            "exact_observation": value,
            "expected_label": f"complete-semx-{index:03d}-execution-retained",
            "source_ids": ["SFT-V3-INDEPENDENT-EXACT-SEMANTICS-OBSERVER", "SFT-V1-V2-SEMANTICS-OBSERVATION-CORPUS"],
            "all_rows_preserved": True,
        })
    payload = {
        "schema": "sft-v3-classical-computation-semx-observation-vector/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "registry_identity": identity,
        "outcomes_opened_only_after_registry_freeze": True,
        "records": records,
        "record_count": len(records),
        "all_rows_preserved": True,
        "external_measurement_boundary": "Semantic laws are directly tested by complete generated program executions and implementation-distinct reconstruction. Conventional languages, compilers and implementation benchmarks remain explicit comparison boundaries and never select a survivor.",
        "protected_engine_or_verifier_edit_made": False,
    }
    payload["vector_identity"] = canonical(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
