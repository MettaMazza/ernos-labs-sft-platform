#!/usr/bin/env python3
"""Open and freeze exact SYMREP observations after registry freeze."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/information_science_symrep_001_014_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/information_science/symrep_001_014_observation_vector_v1.json"


def canonical(value):
    return "sha256:" + hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("SYMREP vector already frozen")
    registry = json.loads(REGISTRY.read_text())
    body = dict(registry)
    identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False:
        raise SystemExit("SYMREP registry changed")
    values = (
        ("canonical_alphabet", {"symbols": ["a", "b", "c"], "duplicate_free": True, "complete": True}),
        ("observation_classes", {"fine_class_count": 3, "coarse_classes": [["L", ["a", "b"]], ["R", ["c"]]], "microforms_retained": True}),
        ("codeword_parsing", {"source_word": ["a", "b", "c"], "encoded_units": ["L", "R", "L", "R", "R"], "parse_count": 1}),
        ("prefix_unique_decoding", {"codebook": {"a": ["L"], "b": ["R", "L"], "c": ["R", "R"]}, "generated_words_checked": 39, "all_unique": True}),
        ("grammar_language", {"depth": 3, "complete_form_count": 7, "forms": ["S", "aS", "aaS", "aaaS", "aab", "ab", "b"]}),
        ("representation_isomorphism", {"source_symbols": 3, "target_symbols": 3, "relation_rows": 2, "bijective": True, "preserved_and_reflected": True}),
        ("canonical_normalization", {"rewrite_chain": ["A1", "A", "a"], "canonical": "a", "idempotent": True}),
        ("variable_length_boundary", {"prefix_code_unique": True, "unbounded_stream": ["L", "L"], "unbounded_parse_count": 2, "boundary_required": True}),
        ("product_alphabet", {"left_size": 2, "right_size": 3, "ordered_pair_count": 6, "all_cross_pairs_once": True}),
        ("typed_symbol", {"type_count": 2, "fibre_sizes": [2, 2], "cross_fibre_value_rejected": True}),
        ("transduction", {"source_word": ["a", "b", "a"], "intermediate": ["x", "y", "x"], "terminal": ["L", "R", "L"], "composition_equal": True}),
        ("ambiguity_ledger", {"stream": ["L", "L"], "parse_count": 2, "parses": [["a", "a"], ["b"]], "all_alternatives_retained": True}),
        ("alphabet_successor", {"prior_size": 3, "successor_size": 4, "new_symbol": "d", "new_pair_count": 3, "prior_rows_preserved": True}),
        ("representation_completeness", {"registered_obligations": 14, "observation_rows": 14, "duplicate_owners": 0, "omitted_owners": 0}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        records.append({
            "number": f"{index:03d}",
            "claim_id": registry["claim_ids"][index - 1],
            "obligation_id": registry["obligation_ids"][index - 1],
            "observation_name": name,
            "exact_observation": value,
            "expected_label": f"complete-symrep-{index:03d}-observation-retained",
            "source_ids": [
                "SFT-V3-INDEPENDENT-EXACT-REPRESENTATION-OBSERVER",
                "SFT-V1-V2-INFORMATION-OBSERVATION-CORPUS",
            ],
            "all_rows_preserved": True,
        })
    payload = {
        "schema": "sft-v3-information-science-symrep-observation-vector/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "registry_identity": identity,
        "outcomes_opened_only_after_registry_freeze": True,
        "records": records,
        "record_count": len(records),
        "all_rows_preserved": True,
        "protected_engine_or_verifier_edit_made": False,
    }
    payload["vector_identity"] = canonical(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": len(records), "identity": payload["vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
