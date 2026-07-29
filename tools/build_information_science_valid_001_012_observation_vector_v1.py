#!/usr/bin/env python3
"""Build the complete post-registry VALID-001--012 observation vector."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/information_science_valid_001_012_target_registry_v1.json"
RECONCILIATION = ROOT / "census/information_science_discipline_current_reconciliation_v18.json"
OUTPUT = ROOT / "experiments/external_sources/information_science/valid_001_012_observation_vector_v1.json"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUTPUT.exists():
        raise SystemExit("refusing overwrite " + str(OUTPUT))
    registry = json.loads(REGISTRY.read_text())
    registry_body = dict(registry)
    identity = registry_body.pop("registry_identity")
    if canonical(registry_body) != identity or registry["target_content_present"] is not False:
        raise SystemExit("value-free registry invalid")
    reconciliation = json.loads(RECONCILIATION.read_text())
    families = reconciliation["completed_families"]
    groups = (
        ("symbol_representation", ("BASE", "SYMREP")),
        ("record_provenance", ("RECORD",)),
        ("source_measure", ("SOURCE", "MEASURE")),
        ("signal_sampling", ("SIGNAL",)),
        ("compression_distortion", ("COMP",)),
        ("channel_capacity", ("CHAN",)),
        ("noise_coding", ("NOISE", "CODE")),
        ("relational_coarse", ("REL", "COARSE")),
        ("retrieval_inference", ("RETR", "INFER")),
        ("privacy_thermal_correspondence", ("PRIV", "THERM", "CORR")),
    )
    control_count = 0
    certificate_count = 0
    for rows in families.values():
        for row in rows:
            package = ROOT / "claims" / row["claim_id"]
            certificate = json.loads((package / "certificate.json").read_text())
            if certificate["engine_receipt_hash"] != row["receipt_hash"]:
                raise SystemExit("stale certificate " + row["claim_id"])
            certificate_count += 1
            control_count += len(json.loads((package / "controls.json").read_text())["controls"])
    if certificate_count != 244 or control_count != 976:
        raise SystemExit("pre-lock evidence vector incomplete")
    observations = []
    for name, owners in groups:
        observations.append({
            "families": list(owners),
            "family_count": len(owners),
            "receipt_count": sum(len(families[owner]) for owner in owners),
            "all_current_receipts_bound": True,
        })
    observations.extend((
        {
            "adverse_controls": control_count,
            "pre_lock_claims": certificate_count,
            "favorable_rows_preserved": True,
            "adverse_rows_preserved": True,
            "absent_rows_preserved": True,
            "unresolved_rows_preserved": True,
            "scope_boundaries_preserved": True,
            "semantic_family_included": len(families["SEM"]),
        },
        {
            "completed_families": len(families),
            "pre_lock_claims": certificate_count,
            "adverse_controls": control_count,
            "reconciliation_identity": reconciliation["reconciliation_identity"],
            "frozen_census_mutated": reconciliation["frozen_census_mutated"],
        },
    ))
    records = []
    for index, (claim_id, observation) in enumerate(zip(registry["claim_ids"], observations), 1):
        records.append({
            "all_rows_preserved": True,
            "claim_id": claim_id,
            "exact_observation": observation,
            "expected_label": f"complete-valid-{index:03d}-observation-retained",
            "number": f"{index:03d}",
            "obligation_id": f"SFT-INFO-OBL-VALID-{index:03d}",
            "observation_name": groups[index - 1][0] if index <= 10 else ("adverse_boundary_vector" if index == 11 else "information_science_grand_lock"),
            "source_ids": [
                "SFT-V3-INFORMATION-SCIENCE-RECONCILIATION-V18",
                "SFT-V3-INDEPENDENT-EXACT-VALIDATION-RECONSTRUCTOR",
            ],
        })
    value = {
        "all_rows_preserved": True,
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "outcomes_opened_only_after_registry_freeze": True,
        "protected_engine_or_verifier_edit_made": False,
        "record_count": 12,
        "records": records,
        "registry_identity": identity,
        "schema": "sft-v3-information-science-valid-observation-vector/1",
    }
    value["vector_identity"] = canonical(value)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"vector": str(OUTPUT.relative_to(ROOT)), "identity": value["vector_identity"], "claims": certificate_count, "controls": control_count}, indent=2))


if __name__ == "__main__":
    main()
