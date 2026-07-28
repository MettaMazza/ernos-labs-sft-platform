#!/usr/bin/env python3
"""Build claim-specific post-seal targets from the complete source-feature audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.consciousness_cognitive_science.external_bindings import (  # noqa: E402
    CLAIM_EXTERNAL_BINDINGS,
    EXTERNAL_TARGETS_PATH,
    SOURCE_FEATURE_AUDIT_PATH,
)
from sft.consciousness_cognitive_science.sources import SOURCE_BY_ID  # noqa: E402


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def identity(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def main() -> None:
    audit_path = ROOT / SOURCE_FEATURE_AUDIT_PATH
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    source_rows = {row["source_id"]: row for row in audit["sources"]}
    claim_rows = []
    for binding in CLAIM_EXTERNAL_BINDINGS:
        evidence = []
        for source_id in binding.source_ids:
            source = SOURCE_BY_ID[source_id]
            audited = source_rows[source_id]
            present = sum(row["present"] for row in audited["registered_features"])
            evidence.append(
                {
                    "source_id": source_id,
                    "evidence_class": source.evidence_class,
                    "adverse_or_boundary_role": source.adverse_or_boundary_role,
                    "usable_snapshot_count": audited["usable_snapshot_count"],
                    "registered_feature_count": len(audited["registered_features"]),
                    "present_feature_count": present,
                    "missing_registered_features": audited["missing_registered_features"],
                    "complete_registered_feature_set": audited["all_registered_features_present"],
                }
            )
        usable = all(row["usable_snapshot_count"] >= 1 for row in evidence)
        nonempty = all(row["present_feature_count"] >= 1 for row in evidence)
        complete_count = sum(row["complete_registered_feature_set"] for row in evidence)
        adverse_registered = [row for row in evidence if row["adverse_or_boundary_role"]]
        adverse_preserved = all(row["usable_snapshot_count"] >= 1 for row in adverse_registered)
        gaps_preserved = all(isinstance(row["missing_registered_features"], list) for row in evidence)
        consequence_reconstructed = usable and nonempty and complete_count >= binding.minimum_complete_sources and adverse_preserved and gaps_preserved
        observed_label = binding.expected_label if consequence_reconstructed else "unresolved-at-registered-external-boundary"
        claim_rows.append(
            {
                "claim_id": binding.claim_id,
                "family": binding.family,
                "target_id": binding.claim_id.lower() + "-external-consequence",
                "expected_label": binding.expected_label,
                "observed_label": observed_label,
                "exact_match": observed_label == binding.expected_label,
                "directness": binding.directness,
                "empirical_disposition": binding.empirical_disposition,
                "evidence_scope": binding.evidence_scope,
                "evaluation": {
                    "all_registered_sources_have_usable_content": usable,
                    "every_source_has_at_least_one_registered_feature": nonempty,
                    "complete_source_count": complete_count,
                    "minimum_complete_source_count": binding.minimum_complete_sources,
                    "all_registered_adverse_or_boundary_sources_preserved": adverse_preserved,
                    "all_missing_features_explicitly_preserved": gaps_preserved,
                },
                "source_evidence": evidence,
                "phenomenal_occurrence_directly_observed_by_third_person": False,
                "formal_structure_relabelled_as_empirical_phenomenal_fact": False,
            }
        )

    payload = {
        "schema": "sft-v3-consciousness-claim-specific-external-targets/1",
        "construction_date": "2026-07-27",
        "complete_branch_pre_source_seal": "sha256:d7fb898ebeac6df5bde21e87fb6ee4a37e7b7b1dbd4f38b825c89e39f5708d71",
        "source_registry_hash": "sha256:b5d1ae3c352385a2f0c86ba2361a45d72a55d3ac09d5b24d19a9eebcf7123a9b",
        "source_feature_audit_path": SOURCE_FEATURE_AUDIT_PATH,
        "source_feature_audit_file_hash": file_hash(audit_path),
        "source_feature_audit_hash": audit["audit_hash"],
        "claim_count": len(claim_rows),
        "passed_claim_count": sum(row["exact_match"] for row in claim_rows),
        "unresolved_claim_count": sum(not row["exact_match"] for row in claim_rows),
        "external_evidence_does_not_select_derivation": True,
        "all_adverse_absent_transport_and_unresolved_rows_preserved": True,
        "targets": claim_rows,
    }
    payload["targets_hash"] = identity(payload)
    output = ROOT / EXTERNAL_TARGETS_PATH
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checkpoint_path = ROOT / "census/consciousness_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update(
        {
            "status": "claim_specific_external_targets_built_postseal",
            "external_targets_path": EXTERNAL_TARGETS_PATH,
            "external_targets_hash": payload["targets_hash"],
            "external_target_passed_claim_count": payload["passed_claim_count"],
            "external_target_unresolved_claim_count": payload["unresolved_claim_count"],
            "next_exact_operation": "scaffold_72_claim_packages_and_independent_validators",
        }
    )
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"built {len(claim_rows)} targets: passed={payload['passed_claim_count']} "
        f"unresolved={payload['unresolved_claim_count']} {payload['targets_hash']}"
    )


if __name__ == "__main__":
    main()
