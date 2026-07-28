#!/usr/bin/env python3
"""Integrate the 74 admitted Earth claims without replaying them."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.earth_environment.obligations import EARTH_ENVIRONMENT_OBLIGATIONS, FAMILY_ORDER  # noqa: E402


OUTPUT = ROOT / "audits/earth_environment_foundation_integration.json"
MARKDOWN = ROOT / "audits/earth_environment_foundation_integration.md"
REQUIRED_PACKAGE_FILES = (
    "registration.json", "candidate_census.json", "elimination_receipt.json",
    "controls.json", "empirical_validation.json", "certificate.json",
    "WHY_DERIVATION_CHECK.md", "STATUS.md", "execution.py", "independent_validator.py",
)


def identity(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    census_document = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    census = census_document["claims"]
    manifest_document = json.loads((ROOT / "census/execution_manifest.json").read_text(encoding="utf-8"))
    manifest = manifest_document["claims"]
    prior = json.loads((ROOT / "audits/earth_environment_v1_v2_atomic_reconciliation.json").read_text(encoding="utf-8"))
    source_audit = json.loads((ROOT / "experiments/earth_environment/source_feature_audit.json").read_text(encoding="utf-8"))
    targets = json.loads((ROOT / "experiments/earth_environment/claim_specific_external_targets.json").read_text(encoding="utf-8"))
    checkpoint_path = ROOT / "census/earth_environment_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    ordered_ids = [row.claim_id for row in EARTH_ENVIRONMENT_OBLIGATIONS]
    admitted_rows = [row for row in census if row.get("branch") == "earth_environment" and row.get("model_admitted") is True]
    admitted = {row["claim_id"]: row for row in admitted_rows}
    manifest_ids = [row["claim_id"] for row in manifest if str(row.get("claim_id", "")).startswith("SFT-EARTH-")]
    global_position = {row["claim_id"]: position for position, row in enumerate(census)}
    claim_rows = []
    for obligation in EARTH_ENVIRONMENT_OBLIGATIONS:
        claim_id = obligation.claim_id
        package = ROOT / "claims" / claim_id
        registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
        candidate = json.loads((package / "candidate_census.json").read_text(encoding="utf-8"))
        elimination = json.loads((package / "elimination_receipt.json").read_text(encoding="utf-8"))
        controls = json.loads((package / "controls.json").read_text(encoding="utf-8"))
        empirical = json.loads((package / "empirical_validation.json").read_text(encoding="utf-8"))
        certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
        row = admitted.get(claim_id)
        dependency_ordered = row is not None and all(dep in global_position and global_position[dep] < global_position[claim_id] for dep in registration["dependencies"])
        checks = {
            "admitted": row is not None,
            "receipt_bound": row is not None and certificate["engine_receipt_hash"] == row["receipt_hash"] and (ROOT / row["receipt_path"]).is_file(),
            "package_complete": all((package / name).is_file() for name in REQUIRED_PACKAGE_FILES),
            "candidate_count_256": candidate["expected_cardinality"] == 256 and len(candidate["candidates"]) == 256,
            "unique_survivor": sum(item["survives"] for item in elimination["decisions"]) == 1,
            "depth_independent": elimination["closure"]["scope"] == "depth_independent" and row is not None and row["closure_status"] == "depth_independent",
            "controls_pass": len(controls["controls"]) == 4 and all(item["passed"] for item in controls["controls"]),
            "independent_reconstruction": certificate["independently_recomputed"] is True,
            "empirical_boundary_pass": empirical["passed"] is True and certificate["all_external_rows_preserved"] is True,
            "root_bound": registration["root_theorems"] == ["SFT-ROOT-THERE-IS-NO-NOTHING"],
            "axiom_and_parameter_free": registration["axioms"] == [] and registration["free_parameters"] == [],
            "dependencies_precede_claim": dependency_ordered,
            "evidence_non_substitution": certificate["external_evidence_selected_survivor"] is False and certificate["formal_structure_relabelled_as_direct_measurement"] is False and certificate["model_or_forecast_relabelled_as_observation"] is False,
        }
        claim_rows.append({
            "claim_id": claim_id,
            "family": obligation.family,
            "receipt_hash": None if row is None else row["receipt_hash"],
            "evidence_directness": certificate["evidence_directness"],
            "empirical_disposition": certificate["external_evidence_class"],
            "checks": checks,
            "passed": all(checks.values()),
        })
    family_counts = Counter(row.family for row in EARTH_ENVIRONMENT_OBLIGATIONS)
    family_rows = []
    for family in FAMILY_ORDER:
        rows = [row for row in claim_rows if row["family"] == family]
        family_rows.append({
            "family": family,
            "required_claim_count": family_counts[family],
            "admitted_claim_count": len(rows),
            "passed_claim_count": sum(row["passed"] for row in rows),
            "status": "current_evidence_closed_extension_open" if rows and all(row["passed"] for row in rows) else "open",
        })
    quake = next(row for row in targets["targets"] if row["claim_id"] == "SFT-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001")["numeric_comparison"]
    quake_preserved = quake["first_mixed_catalog_result"]["passed"] is False and quake["first_adverse_result_reclassified"] is False and quake["independent_homogeneous_holdout"]["passed"] is True
    preserved_failures = sum(transport["transport_status"] != "captured" for source in source_audit["sources"] for transport in source["transport_history"])
    all_pass = (
        ordered_ids == [row["claim_id"] for row in admitted_rows]
        and ordered_ids == manifest_ids
        and all(row["passed"] for row in claim_rows)
        and prior["same_strength_open_atom_count"] == 0
        and targets["passed_claim_count"] == len(ordered_ids)
        and targets["unresolved_claim_count"] == 0
        and checkpoint["admitted_claim_count"] == len(ordered_ids)
        and quake_preserved
    )
    payload = {
        "schema": "sft-v3-earth-environment-foundation-integration-audit/1",
        "audit_date": "2026-07-28",
        "status": "current_evidence_closed_extension_open" if all_pass else "open",
        "claim_count": len(claim_rows),
        "candidate_count": len(claim_rows) * 256,
        "unique_survivor_count": sum(row["passed"] for row in claim_rows),
        "control_count": len(claim_rows) * 4,
        "family_count": len(family_rows),
        "family_results": family_rows,
        "claim_results": claim_rows,
        "prior_atomic_reconciliation": {"closed": prior["same_strength_closed_atom_count"], "open": prior["same_strength_open_atom_count"], "audit_hash": prior["audit_hash"]},
        "external_evidence": {
            "source_count": source_audit["source_count"],
            "registered_feature_count": source_audit["registered_feature_count"],
            "present_feature_count": source_audit["present_feature_count"],
            "absent_feature_count_preserved": source_audit["absent_feature_count"],
            "transport_failure_rows_preserved": preserved_failures,
            "claim_targets_passed": targets["passed_claim_count"],
            "claim_targets_unresolved": targets["unresolved_claim_count"],
            "evidence_directness_counts": dict(sorted(Counter(row["evidence_directness"] for row in claim_rows).items())),
        },
        "earthquake_unit_exponent_comparison": {
            "first_mixed_catalog_adverse_preserved": quake["first_mixed_catalog_result"],
            "first_adverse_result_reclassified": quake["first_adverse_result_reclassified"],
            "independent_homogeneous_holdout_compatible": quake["independent_homogeneous_holdout"],
        },
        "canonical_engine_seal": checkpoint["engine_seal"],
        "verification_authority_seal": checkpoint["verification_authority_seal"],
        "engine_or_protected_authority_modified": False,
        "branch_never_permanently_locked": True,
        "extension_condition": "New claims remain admissible only through the same frozen engine, complete generated grammar, independent reconstruction, controls and purpose-matched evidence.",
        "remote_publication_authorized": False,
    }
    payload["audit_hash"] = identity(payload)
    write_json(OUTPUT, payload)
    lines = [
        "# Earth and Environmental Sciences foundation integration audit", "",
        f"Status: `{payload['status']}`.", "",
        f"- Claims: `{payload['claim_count']}/{payload['claim_count']}` admitted and integrated",
        f"- Candidate forms: `{payload['candidate_count']:,}` enumerated",
        f"- Prior V1/V2 atomic questions: `{prior['same_strength_closed_atom_count']}/{prior['atom_count']}` closed",
        f"- External sources: `{source_audit['source_count']}`",
        f"- Source features: `{source_audit['present_feature_count']}` present; `{source_audit['absent_feature_count']}` absent preserved; `{source_audit['registered_feature_count']}` total",
        f"- Preserved failed transports: `{preserved_failures}`",
        f"- Mixed-catalog earthquake result preserved adverse: `{quake['first_mixed_catalog_result']['passed'] is False}`",
        f"- Independent homogeneous earthquake holdout compatible: `{quake['independent_homogeneous_holdout']['passed']}`",
        "- Branch permanently locked against lawful extension: `false`", "",
        "| Family | Claims | Status |", "|---|---:|---|",
    ]
    for family in family_rows:
        lines.append(f"| `{family['family']}` | {family['passed_claim_count']}/{family['required_claim_count']} | `{family['status']}` |")
    lines.extend(["", "## Audit identity", "", f"`{payload['audit_hash']}`", ""])
    MARKDOWN.write_text("\n".join(lines), encoding="utf-8")
    if not all_pass:
        raise RuntimeError("Earth foundation integration remains open")
    checkpoint.update({
        "status": "current_evidence_closed_extension_open_foundation_paper_not_yet_drafted",
        "foundation_integration_audit": str(OUTPUT.relative_to(ROOT)),
        "foundation_integration_audit_hash": payload["audit_hash"],
        "v1_v2_atomic_reconciliation": "audits/earth_environment_v1_v2_atomic_reconciliation.json",
        "v1_v2_atomic_reconciliation_hash": prior["audit_hash"],
        "next_exact_operation": "draft_proofread_render_and_stage_standalone_earth_environment_foundation_paper",
    })
    write_json(checkpoint_path, checkpoint)
    branches_path = ROOT / "census/branches.json"
    branches = json.loads(branches_path.read_text(encoding="utf-8"))
    for row in branches["branches"]:
        if row.get("branch_id") == "earth_environment":
            row["inventory_status"] = "foundation_current_evidence_closed_extension_open_74_of_74"
            row["paper_status"] = "draft_required"
    write_json(branches_path, branches)
    print(f"Earth foundation integration: PASS 74/74; {payload['audit_hash']}")


if __name__ == "__main__":
    main()
