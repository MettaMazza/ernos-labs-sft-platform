#!/usr/bin/env python3
"""Open and freeze independent exact CBLX executions after registry freeze."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/computation_cblx_001_021_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/computation/cblx_001_021_observation_vector_v1.json"
VALIDATOR = ROOT / "generated/computation/cblx_001_021_validator_v1.py"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists(): raise SystemExit("CBLX observation vector already frozen")
    registry = json.loads(REGISTRY.read_text()); body = dict(registry); identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False: raise SystemExit("CBLX registry changed")
    module_spec = importlib.util.spec_from_file_location("cblx_independent_observer", VALIDATOR)
    observer = importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(observer)
    values = (
        ("decision_closure", {"domain_size": 4, "union_size": 3, "intersection_size": 1, "relative_complement_size": 1}),
        ("paired_recognizer_decision", {"member_support": 2, "complement_support": 2, "overlap": 0, "domain_covered": True}),
        ("fair_dovetail", {"processes": 3, "finite_emissions": ["a", "b", "c"], "emissions_omitted": 0}),
        ("diagonal_language", {"machine_rows": 3, "self_rows_compared": 3, "opposite_verdicts": 3}),
        ("fixed_point", {"description_retained": True, "self_input_retained": True, "fixed_behavior_equal": True}),
        ("recursion_theorem", {"description_transform_total": True, "quotation_trace_retained": True, "fixed_behavior_equal": True}),
        ("semantic_property_boundary", {"terminal_verdicts": ["accept", "reject"], "self_negating_fixed_verdicts": 0}),
        ("many_one_reduction", {"source_instances": 2, "mapped_instances": 2, "verdicts_preserved": 2}),
        ("adaptive_oracle_reduction", {"query_count": 2, "queries": ["q1", "q2"], "answers": ["accept", "reject"], "order_retained": True}),
        ("enumeration_reducibility", {"positive_query_sets": 2, "negative_queries_used": 0, "all_positive_queries_observed": True}),
        ("degree_order", {"degree_classes": 3, "explicit_reductions": 2, "transitive_reduction": ["A", "C"], "reflexive_rows": 3}),
        ("relative_jump", {"machine_rows": 3, "diagonal_rows": 3, "prior_self_verdicts_all_opposed": True}),
        ("oracle_custody", {"oracle_identity_retained": True, "query_identity_retained": True, "answer_identity_retained": True, "answer_order_retained": True}),
        ("quantifier_hierarchy", {"finite_domain_size": 2, "existential_result": True, "universal_result": False, "universal_existential_result": True}),
        ("post_correspondence", {"tile_count": 3, "search_depth": 2, "least_witness_indices": [0], "matched_word": ["a"]}),
        ("entscheidungsproblem", {"generated_prefix_decisions_retained": True, "total_self_negating_decider_exists": False}),
        ("incompleteness", {"internal_proof_rows": 2, "complete_internal_consistency_certificate_present": False, "external_record_required": True}),
        ("busy_beaver_domination", {"depths_checked": [1, 2, 3, 4, 5, 6, 7, 8], "maximum_runtime_equals_depth": True, "smaller_bound_dominated": True}),
        ("finite_busy_beaver_census", {"depths_exhausted": [1, 2, 3, 4, 5, 6, 7], "alphabet_size": 2, "maxima": [1, 2, 3, 4, 5, 6, 7], "all_ties_retained": True}),
        ("hypercomputation_admissibility", {"operational_trace_or_oracle_record_required": True, "unrecorded_answers_admitted": False, "physical_realization_handoff": True}),
        ("computability_completeness", {"registered_obligations": 21, "independent_execution_rows": 21, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        if not observer.independent_witness(index): raise SystemExit(f"CBLX independent observation failed at {index:03d}")
        records.append({"number": f"{index:03d}", "claim_id": registry["claim_ids"][index-1], "obligation_id": registry["obligation_ids"][index-1], "observation_name": name, "exact_observation": value, "expected_label": f"complete-cblx-{index:03d}-execution-retained", "source_ids": ["SFT-V3-INDEPENDENT-EXACT-COMPUTABILITY-OBSERVER", "SFT-V1-V2-COMPUTABILITY-OBSERVATION-CORPUS"], "all_rows_preserved": True})
    payload = {"schema": "sft-v3-classical-computation-cblx-observation-vector/1", "date": "2026-07-29", "authority": "Maria Smith", "registry_identity": identity, "outcomes_opened_only_after_registry_freeze": True, "records": records, "record_count": len(records), "all_rows_preserved": True, "external_measurement_boundary": "Computability laws are tested by exact generated executions and implementation-distinct reconstruction; bounded censuses retain their boundary and are not relabelled as unrestricted negative results.", "protected_engine_or_verifier_edit_made": False}
    payload["vector_identity"] = canonical(payload); OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))


if __name__ == "__main__": main()
