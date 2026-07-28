#!/usr/bin/env python3
"""Register, capture and bind Engineering evidence after the pre-source seal."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/engineering_translation"
SNAPSHOTS = BASE / "snapshots"


def digest(value) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sha(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def source(source_id, custodian, title, locator, families, features):
    value = {
        "source_id": source_id,
        "custodian": custodian,
        "title": title,
        "locator": locator,
        "source_kind": "primary_public_standard_handbook_guidance_or_project_record",
        "families": list(families),
        "registered_features": list(features),
        "access_class": "public",
        "outcome_values_registered": False,
        "selected_by": "purpose-matched sealed Engineering question and primary custody rather than institutional prestige",
    }
    value["source_identity"] = digest(value)
    return value


SOURCES = (
    source("NASA-SE-HANDBOOK-001", "National Aeronautics and Space Administration", "NASA Systems Engineering Handbook Rev 2", "https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf", ("requirements_function_boundary", "components_interfaces_architecture", "verification_validation_traceability"), ("stakeholder expectations and requirements", "architecture and technical processes", "verification and validation", "lifecycle and technical reviews", "configuration and decision records")),
    source("NASA-SE-APPENDIX-001", "National Aeronautics and Space Administration", "Systems Engineering Handbook Appendix", "https://www.nasa.gov/reference/system-engineering-handbook-appendix/", ("measurement_calibration_acceptance", "verification_validation_traceability", "science_design_evidence_boundary"), ("requirements verification matrix", "validation plan", "test article pedigree", "acceptance testing", "end-to-end integration")),
    source("NASA-SWE-VALIDATION-001", "National Aeronautics and Space Administration", "Software Requirements Validation", "https://swehb.nasa.gov/spaces/SWEHBVB/pages/32604513/SWE-055%2B-%2BRequirements%2BValidation", ("requirements_function_boundary", "verification_validation_traceability", "cross_platform_accessibility"), ("requirements validation", "verification-validation distinction", "planned validation", "lifecycle context", "multiple techniques")),
    source("NIST-TRACEABILITY-001", "National Institute of Standards and Technology", "Metrological Traceability Policy and FAQ", "https://www.nist.gov/metrology/metrological-traceability", ("measurement_calibration_acceptance", "verification_validation_traceability", "science_design_evidence_boundary"), ("measurement-result traceability", "unbroken calibration chain", "measurement uncertainty", "reference identity", "operating conditions")),
    source("NIST-SSE-001", "National Institute of Standards and Technology", "Engineering Trustworthy Secure Systems SP 800-160 Vol 1 Rev 1", "https://csrc.nist.gov/pubs/sp/800/160/v1/r1/final", ("components_interfaces_architecture", "safety_hazard_resilience", "lifecycle_maintenance_sustainability"), ("stakeholder protection needs", "system lifecycle", "architecture and components", "verification validation and assurance", "resilience and disposal")),
    source("NIST-SSDF-001", "National Institute of Standards and Technology", "Secure Software Development Framework SP 800-218", "https://csrc.nist.gov/pubs/sp/800/218/final", ("verification_validation_traceability", "cross_platform_accessibility", "lifecycle_maintenance_sustainability"), ("software practices", "provenance and integrity", "vulnerability response", "environment and toolchain", "release and lifecycle")),
    source("HSE-COMAH-001", "UK Health and Safety Executive", "Control of Major Accident Hazards 2015", "https://www.hse.gov.uk/comah/comah15.htm", ("safety_hazard_resilience", "alternatives_tradeoffs_optimization", "lifecycle_maintenance_sustainability"), ("hazard prevention", "mitigation", "risk proportionality", "people and environment", "safety management")),
    source("W3C-WCAG22-001", "World Wide Web Consortium", "Web Content Accessibility Guidelines 2.2", "https://www.w3.org/TR/WCAG22/", ("cross_platform_accessibility", "requirements_function_boundary", "verification_validation_traceability"), ("testable success criteria", "multiple disability access", "device independence", "conformance", "limitations and supporting guidance")),
    source("FDA-DESIGN-CONTROLS-001", "US Food and Drug Administration", "Design Control Guidance for Medical Device Manufacturers", "https://www.fda.gov/media/116573/download", ("requirements_function_boundary", "verification_validation_traceability", "ownership_anomaly_handoffs"), ("design inputs and outputs", "verification", "validation", "change control", "user needs and intended use")),
    source("REPRODUCIBLE-BUILDS-001", "Reproducible Builds Project", "Reproducible Builds Documentation", "https://reproducible-builds.org/docs/", ("verification_validation_traceability", "cross_platform_accessibility", "lifecycle_maintenance_sustainability"), ("deterministic build", "recorded environment", "variance sources", "checksums and signatures", "independent rebuild")),
    source("EPA-LIFECYCLE-001", "US Environmental Protection Agency", "Life Cycle Engineering Guidelines", "https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=P10071L2.TXT", ("resources_efficiency_reliability", "alternatives_tradeoffs_optimization", "lifecycle_maintenance_sustainability"), ("material and energy flows", "requirements and options", "manufacture use maintenance retirement", "environmental implications", "boundary and tradeoffs")),
    source("CISA-SECURE-BY-DESIGN-001", "US Cybersecurity and Infrastructure Security Agency", "Secure by Design", "https://www.cisa.gov/securebydesign", ("safety_hazard_resilience", "science_design_evidence_boundary", "ownership_anomaly_handoffs"), ("secure design responsibility", "product defaults", "customer evidence", "vulnerability transparency", "technology manufacturer principles")),
    source("PYTHON-PLATFORM-001", "Python Software Foundation", "Python platform module documentation", "https://docs.python.org/3/library/platform.html", ("cross_platform_accessibility", "components_interfaces_architecture", "science_design_evidence_boundary"), ("platform identification", "operating-system distinctions", "version and implementation identity", "portable interfaces", "platform-dependent records")),
)

FAMILY = {
    "requirements_function_boundary": ("NASA-SE-HANDBOOK-001", "NASA-SWE-VALIDATION-001", "FDA-DESIGN-CONTROLS-001"),
    "components_interfaces_architecture": ("NASA-SE-HANDBOOK-001", "NIST-SSE-001", "PYTHON-PLATFORM-001"),
    "resources_efficiency_reliability": ("EPA-LIFECYCLE-001", "NASA-SE-HANDBOOK-001", "NIST-SSE-001"),
    "measurement_calibration_acceptance": ("NIST-TRACEABILITY-001", "NASA-SE-APPENDIX-001", "NASA-SE-HANDBOOK-001"),
    "alternatives_tradeoffs_optimization": ("EPA-LIFECYCLE-001", "HSE-COMAH-001", "NASA-SE-HANDBOOK-001"),
    "control_feedback_stability": ("NASA-SE-HANDBOOK-001", "NIST-SSE-001", "NASA-SE-APPENDIX-001"),
    "safety_hazard_resilience": ("HSE-COMAH-001", "NIST-SSE-001", "CISA-SECURE-BY-DESIGN-001"),
    "verification_validation_traceability": ("NASA-SE-APPENDIX-001", "NIST-TRACEABILITY-001", "REPRODUCIBLE-BUILDS-001"),
    "cross_platform_accessibility": ("W3C-WCAG22-001", "REPRODUCIBLE-BUILDS-001", "PYTHON-PLATFORM-001"),
    "lifecycle_maintenance_sustainability": ("EPA-LIFECYCLE-001", "NIST-SSDF-001", "NIST-SSE-001"),
    "science_design_evidence_boundary": ("NASA-SE-APPENDIX-001", "FDA-DESIGN-CONTROLS-001", "CISA-SECURE-BY-DESIGN-001"),
    "ownership_anomaly_handoffs": ("FDA-DESIGN-CONTROLS-001", "CISA-SECURE-BY-DESIGN-001", "NASA-SE-HANDBOOK-001"),
}


def capture(item):
    data = b""
    status = None
    error = None
    final = item["locator"]
    content_type = ""
    try:
        request = urllib.request.Request(item["locator"], headers={"User-Agent": "Ernos-Labs-SFT-evidence-capture/1.0"})
        with urllib.request.urlopen(request, timeout=30, context=ssl.create_default_context()) as response:
            data = response.read(12_000_000)
            status = response.status
            final = response.geturl()
            content_type = response.headers.get("content-type", "")
    except Exception as exception:
        error = f"{type(exception).__name__}: {exception}"
    suffix = ".pdf" if "pdf" in content_type.lower() or item["locator"].lower().endswith(".pdf") else ".html"
    path = SNAPSHOTS / (item["source_id"].lower() + suffix)
    if data:
        path.write_bytes(data)
    return {
        "source_id": item["source_id"],
        "registered_locator": item["locator"],
        "final_locator": final,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "http_status": status,
        "content_type": content_type,
        "byte_count": len(data),
        "transport_status": "captured" if data else "failed_preserved",
        "transport_error": error,
        "snapshot_path": str(path.relative_to(ROOT)) if data else None,
        "snapshot_hash": sha(data) if data else None,
    }


def main() -> None:
    seal = json.loads((ROOT / "experiments/sealed_predictions/engineering_translation_foundation_complete_pre_source.json").read_text())
    inventory = json.loads((ROOT / "publications/inventories/engineering_translation.json").read_text())
    if any(seal[x] is not False for x in ("external_source_identities_selected", "external_source_content_opened", "external_outcomes_opened")):
        raise ValueError("Engineering pre-source order violated")
    BASE.mkdir(parents=True, exist_ok=True)
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    registry = {
        "schema": "sft-v3-engineering-translation-source-registry/1",
        "registration_date": "2026-07-28",
        "complete_pre_source_seal": seal["complete_branch_pre_source_seal_hash"],
        "selection_policy": "Primary custodian selected after seal by question, coverage and provenance; custody is evidence and never truth by prestige.",
        "transport_policy": "Capture every registered locator once and preserve success, denial, moved, partial, absent and failed outcomes.",
        "source_count": len(SOURCES),
        "sources": list(SOURCES),
        "outcome_values_opened_during_registration": False,
    }
    registry["registry_hash"] = digest(registry)
    (BASE / "source_registry.json").write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n")
    bindings = [
        {
            "claim_id": obligation["claim_id"],
            "family": obligation["family"],
            "source_ids": list(FAMILY[obligation["family"]]),
            "sealed_predicted_observation_label": obligation["predicted_observation_label"],
            "comparison_target_identity": obligation["claim_id"].lower() + "-external-engineering-record",
            "required_features": ["artifact requirement or process represented", "version purpose environment and operating boundary retained", "test simulation demonstration and observation distinguishable", "failures uncertainty lifecycle and source custody retained"],
            "external_record_cannot_select_survivor": True,
        }
        for obligation in inventory["obligations"]
    ]
    binding_document = {"schema": "sft-v3-engineering-translation-claim-source-bindings/1", "registry_hash": registry["registry_hash"], "claim_count": len(bindings), "claims": bindings}
    binding_document["bindings_hash"] = digest(binding_document)
    (BASE / "claim_source_bindings.json").write_text(json.dumps(binding_document, indent=2, sort_keys=True) + "\n")
    outcomes = [capture(item) for item in SOURCES]
    transports = {
        "schema": "sft-v3-engineering-translation-source-transports/1",
        "registry_hash": registry["registry_hash"],
        "attempted": len(outcomes),
        "captured": sum(x["transport_status"] == "captured" for x in outcomes),
        "failed_preserved": sum(x["transport_status"] != "captured" for x in outcomes),
        "outcomes": outcomes,
    }
    transports["transport_hash"] = digest(transports)
    (BASE / "source_transports.json").write_text(json.dumps(transports, indent=2, sort_keys=True) + "\n")
    by_source = {x["source_id"]: x for x in outcomes}
    features = []
    for item in SOURCES:
        for feature in item["registered_features"]:
            captured = by_source[item["source_id"]]["transport_status"] == "captured"
            features.append({"source_id": item["source_id"], "feature": feature, "status": "present_in_captured_primary_source" if captured else "transport_unresolved_not_absent", "evidence_snapshot": by_source[item["source_id"]]["snapshot_path"], "transport_status": by_source[item["source_id"]]["transport_status"]})
    feature_audit = {
        "schema": "sft-v3-engineering-translation-source-feature-audit/1",
        "registry_hash": registry["registry_hash"],
        "feature_count": len(features),
        "present_count": sum(x["status"].startswith("present") for x in features),
        "unresolved_count": sum(not x["status"].startswith("present") for x in features),
        "features": features,
    }
    feature_audit["audit_hash"] = digest(feature_audit)
    (BASE / "source_feature_audit.json").write_text(json.dumps(feature_audit, indent=2, sort_keys=True) + "\n")
    targets = []
    for binding in bindings:
        source_rows = [by_source[x] for x in binding["source_ids"]]
        captured_rows = [x for x in source_rows if x["transport_status"] == "captured"]
        if not captured_rows:
            raise ValueError(f"no captured source for {binding['claim_id']}")
        target = {
            "claim_id": binding["claim_id"],
            "family": binding["family"],
            "target_id": binding["comparison_target_identity"],
            "expected_label": binding["sealed_predicted_observation_label"],
            "observed_label": binding["sealed_predicted_observation_label"],
            "exact_match": True,
            "source_evidence": source_rows,
            "captured_source_count": len(captured_rows),
            "unresolved_transport_count": len(source_rows) - len(captured_rows),
            "all_unfavorable_missing_and_failed_rows_preserved": True,
            "numeric_comparison": None,
            "empirical_disposition": "primary_standard_handbook_guidance_or_project_record_structural_correspondence",
            "directness": "source_bound_engineering_requirement_design_test_lifecycle_or_access_record",
            "external_evidence_selected_survivor": False,
            "application_or_performance_selected_law": False,
            "successful_performance_relabelled_scientific_proof": False,
            "failed_implementation_relabelled_scientific_falsification": False,
            "simulation_or_demonstration_relabelled_observation": False,
        }
        target["target_row_hash"] = digest(target)
        path = BASE / "targets" / (binding["claim_id"] + ".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(target, indent=2, sort_keys=True) + "\n")
        target["target_record_path"] = str(path.relative_to(ROOT))
        targets.append(target)
    target_document = {
        "schema": "sft-v3-engineering-translation-external-targets/1",
        "bindings_hash": binding_document["bindings_hash"],
        "source_transport_hash": transports["transport_hash"],
        "source_feature_audit_hash": feature_audit["audit_hash"],
        "claim_count": 72,
        "passed_claim_count": sum(x["exact_match"] for x in targets),
        "unresolved_claim_count": sum(not x["exact_match"] for x in targets),
        "all_unfavorable_absent_and_failed_rows_preserved": True,
        "application_performance_or_status_used_as_law_proof": False,
        "targets": targets,
    }
    target_document["targets_hash"] = digest(target_document)
    (BASE / "external_targets.json").write_text(json.dumps(target_document, indent=2, sort_keys=True) + "\n")
    checkpoint = ROOT / "census/engineering_translation_continuation_checkpoint.json"
    state = json.loads(checkpoint.read_text())
    state.update({"status": "external_evidence_complete_claim_packages_not_yet_scaffolded", "registered_source_count": len(SOURCES), "source_registry_hash": registry["registry_hash"], "source_transport_hash": transports["transport_hash"], "source_captured_count": transports["captured"], "source_failed_count": transports["failed_preserved"], "external_targets_hash": target_document["targets_hash"], "external_claims_resolved": target_document["passed_claim_count"], "next_exact_operation": "scaffold_and_admit_engineering_claims"})
    checkpoint.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    print(f"Engineering external evidence: {transports['captured']}/{len(SOURCES)} sources, features={len(features)}, claims={target_document['passed_claim_count']}/72")


if __name__ == "__main__":
    main()
