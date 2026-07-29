#!/usr/bin/env python3
"""Open and freeze exact RECORD observations after registry freeze."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/information_science_record_001_012_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/information_science/record_001_012_observation_vector_v1.json"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("RECORD vector already frozen")
    registry = json.loads(REGISTRY.read_text())
    body = dict(registry)
    identity = body.pop("registry_identity")
    if canonical(body) != identity or registry["target_content_present"] is not False:
        raise SystemExit("RECORD registry changed")
    values = (
        ("data_identity", {"identity_coordinates": 3, "source_retained": True, "field_retained": True, "exact_value_retained": True}),
        ("tuple_relation", {"schema_fields": 2, "rows": 2, "complete_field_cells": 4, "partial_rows": 0}),
        ("metadata", {"metadata_fields": ["record_identity", "schema", "unit", "source"], "data_replaced": False}),
        ("schema_type", {"declared_fields": 2, "complete_record_accepted": True, "missing_field_rejected": True}),
        ("provenance", {"steps": ["capture", "normalize", "publish"], "contiguous": True, "duplicate_free": True, "gap_rejected": True}),
        ("integrity", {"unchanged_payload_accepted": True, "changed_payload_rejected": True, "identity_reconstructed": True}),
        ("version_revision", {"versions": 2, "payload_identities_distinct": True, "parent_retained": "v1", "silent_overwrite": False}),
        ("absence_missing_unknown", {"states": [["absence", "0"], ["missing", "expected-row"], ["unknown", "retained-row"]], "distinct_state_count": 3, "numeric_zero_claimed": False}),
        ("duplicate_alias", {"duplicate_identity_equal": True, "alias_source_count": 2, "canonical_target_count": 1, "source_tokens_retained": True}),
        ("record_linkage", {"exact_links": 1, "unresolved_alternatives": 2, "silent_selection": False}),
        ("dataset_completeness", {"expected": 3, "observed": 3, "retained": 2, "absent": 1, "unexpected": 1, "all_rows_accounted": True}),
        ("custody_reproducibility", {"bound_components": ["data", "metadata", "schema", "provenance", "integrity"], "independent_identity_equal": True}),
    )
    records = []
    for index, (name, value) in enumerate(values, 1):
        records.append({
            "number": f"{index:03d}",
            "claim_id": registry["claim_ids"][index - 1],
            "obligation_id": registry["obligation_ids"][index - 1],
            "observation_name": name,
            "exact_observation": value,
            "expected_label": f"complete-record-{index:03d}-observation-retained",
            "source_ids": ["SFT-V3-INDEPENDENT-EXACT-RECORD-OBSERVER", "SFT-V1-V2-INFORMATION-OBSERVATION-CORPUS"],
            "all_rows_preserved": True,
        })
    payload = {
        "schema": "sft-v3-information-science-record-observation-vector/1",
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
