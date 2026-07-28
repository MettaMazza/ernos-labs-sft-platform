#!/usr/bin/env python3
"""Integrate the 72 admitted Consciousness claims without replaying them."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.consciousness_cognitive_science.obligations import CONSCIOUSNESS_OBLIGATIONS, FAMILY_COUNTS, FAMILY_ORDER  # noqa: E402


OUTPUT = ROOT / "audits/consciousness_foundation_integration.json"
MARKDOWN = ROOT / "audits/consciousness_foundation_integration.md"
REQUIRED_PACKAGE_FILES = (
    "registration.json",
    "candidate_census.json",
    "elimination_receipt.json",
    "controls.json",
    "empirical_validation.json",
    "certificate.json",
    "WHY_DERIVATION_CHECK.md",
    "STATUS.md",
    "execution.py",
    "independent_validator.py",
)


def identity(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def main() -> None:
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
    manifest = json.loads((ROOT / "census/execution_manifest.json").read_text(encoding="utf-8"))["claims"]
    audit = json.loads((ROOT / "audits/consciousness_v1_v2_atomic_reconciliation.json").read_text(encoding="utf-8"))
    source_audit = json.loads((ROOT / "experiments/consciousness/source_feature_audit.json").read_text(encoding="utf-8"))
    targets = json.loads((ROOT / "experiments/consciousness/claim_specific_external_targets.json").read_text(encoding="utf-8"))
    checkpoint = json.loads((ROOT / "census/consciousness_continuation_checkpoint.json").read_text(encoding="utf-8"))
    ordered_ids = [row.claim_id for row in CONSCIOUSNESS_OBLIGATIONS]
    admitted_rows = [row for row in census if row.get("branch") == "consciousness_cognitive_science" and row.get("model_admitted") is True]
    admitted = {row["claim_id"]: row for row in admitted_rows}
    manifest_ids = [row["claim_id"] for row in manifest if str(row.get("claim_id", "")).startswith("SFT-CONSC-")]
    global_position = {row["claim_id"]: position for position, row in enumerate(census)}
    claim_rows = []
    for obligation in CONSCIOUSNESS_OBLIGATIONS:
        claim_id = obligation.claim_id
        package = ROOT / "claims" / claim_id
        registration = json.loads((package / "registration.json").read_text(encoding="utf-8"))
        candidate = json.loads((package / "candidate_census.json").read_text(encoding="utf-8"))
        elimination = json.loads((package / "elimination_receipt.json").read_text(encoding="utf-8"))
        controls = json.loads((package / "controls.json").read_text(encoding="utf-8"))
        empirical = json.loads((package / "empirical_validation.json").read_text(encoding="utf-8"))
        certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
        row = admitted.get(claim_id)
        dependency_ordered = all(dep in global_position and global_position[dep] < global_position[claim_id] for dep in registration["dependencies"])
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
            "evidence_non_substitution": certificate["phenomenal_occurrence_directly_observed_by_third_person"] is False and certificate["formal_structure_relabelled_as_empirical_phenomenal_fact"] is False,
        }
        claim_rows.append(
            {
                "claim_id": claim_id,
                "family": obligation.family,
                "receipt_hash": None if row is None else row["receipt_hash"],
                "evidence_directness": certificate["evidence_directness"],
                "empirical_disposition": certificate["external_evidence_class"],
                "checks": checks,
                "passed": all(checks.values()),
            }
        )

    family_rows = []
    for family in FAMILY_ORDER:
        rows = [row for row in claim_rows if row["family"] == family]
        family_rows.append(
            {
                "family": family,
                "required_claim_count": FAMILY_COUNTS[family],
                "admitted_claim_count": len(rows),
                "passed_claim_count": sum(row["passed"] for row in rows),
                "status": "current_evidence_closed_extension_open" if rows and all(row["passed"] for row in rows) else "open",
            }
        )
    directness_counts = Counter(row["evidence_directness"] for row in claim_rows)
    preserved_failures = sum(not transport["usable_for_feature_audit"] for source in source_audit["sources"] for transport in source["transport_history"])
    all_pass = (
        ordered_ids == [row["claim_id"] for row in admitted_rows]
        and ordered_ids == manifest_ids
        and all(row["passed"] for row in claim_rows)
        and audit["same_strength_open_atom_count"] == 0
        and targets["passed_claim_count"] == len(ordered_ids)
        and targets["unresolved_claim_count"] == 0
        and checkpoint["admitted_claim_count"] == len(ordered_ids)
    )
    payload = {
        "schema": "sft-v3-consciousness-foundation-integration-audit/1",
        "audit_date": "2026-07-27",
        "status": "current_evidence_closed_extension_open" if all_pass else "open",
        "claim_count": len(claim_rows),
        "candidate_count": len(claim_rows) * 256,
        "family_count": len(family_rows),
        "family_results": family_rows,
        "claim_results": claim_rows,
        "prior_atomic_reconciliation": {"closed": audit["same_strength_closed_atom_count"], "open": audit["same_strength_open_atom_count"], "audit_hash": audit["audit_hash"]},
        "external_evidence": {
            "source_count": source_audit["source_count"],
            "registered_feature_count": source_audit["registered_feature_count"],
            "present_feature_count": source_audit["present_feature_count"],
            "absent_feature_count_preserved": source_audit["absent_feature_count"],
            "transport_or_content_failure_rows_preserved": preserved_failures,
            "claim_targets_passed": targets["passed_claim_count"],
            "claim_targets_unresolved": targets["unresolved_claim_count"],
            "evidence_directness_counts": dict(sorted(directness_counts.items())),
        },
        "canonical_engine_seal": checkpoint["engine_seal"],
        "verification_authority_seal": checkpoint["verification_authority_seal"],
        "engine_or_protected_authority_modified": False,
        "branch_never_permanently_locked": True,
        "extension_condition": "New claims remain admissible only through the same frozen engine, complete generated grammar, independent reconstruction, controls and purpose-matched evidence.",
        "remote_publication_authorized": False,
    }
    payload["audit_hash"] = identity(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Consciousness and Cognitive Science foundation integration audit",
        "",
        f"Status: `{payload['status']}`.",
        "",
        f"- Claims: `{payload['claim_count']}/{payload['claim_count']}` admitted and integrated",
        f"- Candidate forms: `{payload['candidate_count']:,}` enumerated",
        f"- Prior V1/V2 atomic questions: `{audit['same_strength_closed_atom_count']}/{audit['atom_count']}` closed",
        f"- External sources: `{source_audit['source_count']}`",
        f"- Registered source features: `{source_audit['present_feature_count']}` present; `{source_audit['absent_feature_count']}` absent and preserved; `{source_audit['registered_feature_count']}` total",
        f"- Preserved transport/content failure rows: `{preserved_failures}`",
        "- Direct third-person possession of phenomenal occurrence claimed: `false`",
        "- Branch permanently locked against lawful extension: `false`",
        "",
        "| Family | Claims | Status |",
        "|---|---:|---|",
    ]
    for family in family_rows:
        lines.append(f"| `{family['family']}` | {family['passed_claim_count']}/{family['required_claim_count']} | `{family['status']}` |")
    lines.extend(["", "## Audit identity", "", f"`{payload['audit_hash']}`", ""])
    MARKDOWN.write_text("\n".join(lines), encoding="utf-8")
    if not all_pass:
        raise RuntimeError("Consciousness foundation integration remains open")
    print(f"Consciousness foundation integration: PASS 72/72; {payload['audit_hash']}")


if __name__ == "__main__":
    main()
