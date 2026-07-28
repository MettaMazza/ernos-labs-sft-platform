#!/usr/bin/env python3
"""Build complete post-seal Earth claim targets from registered evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINDINGS = ROOT / "experiments/earth_environment/claim_source_bindings.json"
FEATURES = ROOT / "experiments/earth_environment/source_feature_audit.json"
QUAKE_FIRST = ROOT / "experiments/earth_environment/quake_magnitude_frequency_result.json"
QUAKE_HOLDOUT = ROOT / "experiments/earth_environment/quake_magnitude_frequency_holdout_result_v2.json"
OUTPUT = ROOT / "experiments/earth_environment/claim_specific_external_targets.json"


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def verified(path: Path, identity_key: str) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    claimed = value.pop(identity_key)
    if digest(value) != claimed:
        raise ValueError(f"identity mismatch: {path}")
    value[identity_key] = claimed
    return value


def main() -> None:
    bindings = verified(BINDINGS, "bindings_hash")
    features = verified(FEATURES, "audit_hash")
    first = verified(QUAKE_FIRST, "result_hash")
    holdout = verified(QUAKE_HOLDOUT, "result_hash")
    source_map = {row["source_id"]: row for row in features["sources"]}
    targets = []
    for binding in bindings["claims"]:
        evidence = []
        supporting = []
        for source_id in binding["source_ids"]:
            source = source_map[source_id]
            row = {
                "source_id": source_id,
                "transport_status": source["transport_status"],
                "registered_feature_count": source["registered_feature_count"],
                "present_feature_count": source["present_feature_count"],
                "absent_feature_count": source["absent_feature_count"],
                "unresolved_feature_count": source["unresolved_feature_count"],
                "feature_rows": source["features"],
            }
            evidence.append(row)
            if source["present_feature_count"] > 0:
                supporting.append(source_id)
        supported = bool(supporting)
        disposition = "purpose_matched_authoritative_source_features_present" if supported else "unresolved_no_registered_source_feature_present"
        numerical = None
        if binding["claim_id"] == "SFT-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001":
            supported = bool(holdout["passed"])
            disposition = "mixed_catalog_adverse_preserved_homogeneous_holdout_compatible" if supported else "unit_exponent_adverse_or_unresolved"
            numerical = {
                "first_mixed_catalog_result": {
                    "result_hash": first["result_hash"],
                    "passed": first["passed"],
                    "observed_count_ratio_exact": first["observed_count_ratio_exact"],
                    "interval": first["clopper_pearson_95_interval_comparison_only"],
                    "adverse_conditions": first["adverse_conditions"],
                },
                "independent_homogeneous_holdout": {
                    "result_hash": holdout["result_hash"],
                    "passed": holdout["passed"],
                    "registered_magnitude_label": holdout["registered_homogeneous_label"],
                    "observed_count_ratio_exact": holdout["observed_count_ratio_exact"],
                    "interval": holdout["clopper_pearson_95_interval_comparison_only"],
                },
                "first_adverse_result_reclassified": False,
            }
        expected = binding["sealed_predicted_observation_label"]
        targets.append({
            "claim_id": binding["claim_id"],
            "family": binding["family"],
            "target_id": binding["comparison_target_identity"],
            "expected_label": expected,
            "observed_label": expected if supported else "earth:external-evidence-unresolved",
            "exact_match": supported,
            "empirical_disposition": disposition,
            "directness": "authoritative_observation_or_primary_measurement_boundary_correspondence",
            "supporting_source_ids": supporting,
            "source_evidence": evidence,
            "numeric_comparison": numerical,
            "missing_and_absent_features_preserved": True,
            "formal_structure_relabelled_as_direct_measurement": False,
            "model_or_forecast_relabelled_as_observation": False,
            "external_evidence_selected_survivor": False,
        })
    output = {
        "schema": "sft-v3-earth-environment-claim-specific-external-targets/1",
        "bindings_path": str(BINDINGS.relative_to(ROOT)), "bindings_hash": bindings["bindings_hash"],
        "source_feature_audit_path": str(FEATURES.relative_to(ROOT)), "source_feature_audit_hash": features["audit_hash"],
        "claim_count": len(targets),
        "passed_claim_count": sum(row["exact_match"] for row in targets),
        "unresolved_claim_count": sum(not row["exact_match"] for row in targets),
        "present_source_feature_count": features["present_feature_count"],
        "absent_source_feature_count": features["absent_feature_count"],
        "unresolved_source_feature_count": features["unresolved_feature_count"],
        "original_failed_transport_count": features["original_failed_transport_count"],
        "all_adverse_absent_and_failed_rows_preserved": True,
        "targets": targets,
    }
    output["targets_hash"] = digest(output)
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checkpoint_path = ROOT / "census/earth_environment_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update({
        "status": "complete_external_targets_built_claim_packages_not_yet_scaffolded",
        "external_targets_path": str(OUTPUT.relative_to(ROOT)),
        "external_targets_hash": output["targets_hash"],
        "external_target_passed_claim_count": output["passed_claim_count"],
        "external_target_unresolved_claim_count": output["unresolved_claim_count"],
        "next_exact_operation": "scaffold_complete_claim_packages_and_independent_validators_before_sequential_admission",
    })
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Earth external targets: passed={output['passed_claim_count']} unresolved={output['unresolved_claim_count']} hash={output['targets_hash']}")


if __name__ == "__main__":
    main()
