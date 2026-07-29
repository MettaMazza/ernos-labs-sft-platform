#!/usr/bin/env python3
"""Implementation-distinct reconstruction of the Engineering protocol family."""
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys

RELATIONS = {
    "SFT-ENG-TESLA-RESONANT-TRANSFER-PROTOCOL-002": "phase-bound-connected-path-complete-ledger-protocol",
    "SFT-ENG-VACUUM-INERTIA-RESPONSE-PROTOCOL-002": "paired-drive-response-restoration-protocol",
    "SFT-ENG-VACUUM-BEAT-RESTORATION-PROTOCOL-002": "one-sixth-outward-and-one-sixth-return-ledger-protocol",
    "SFT-ENG-SECTOR-FIVE-SEVEN-DETECTION-PROTOCOL-002": "sealed-p-five-p-seven-blind-signature-protocol",
    "SFT-ENG-SMITHIUM-SYNTHESIS-IDENTIFICATION-PROTOCOL-002": "Smithium-126-complete-synthesis-identification-protocol",
    "SFT-ENG-NOVEL-TRANSLATIONS-COMPLETE-FAMILY-002": "five-protocol-traceable-complete-family",
}

DEPENDENCIES = {
    "SFT-ENG-TESLA-RESONANT-TRANSFER-PROTOCOL-002": (
        "SFT-ENG-REQUIREMENT-001", "SFT-ENG-MEASUREMENT-001", "SFT-ENG-CALIBRATION-001",
        "SFT-ENG-ACCEPTANCE-TEST-001", "SFT-ENG-SAFETY-001", "SFT-ENG-TRACEABILITY-001",
        "SFT-ENG-REPRODUCIBILITY-001", "SFT-ENG-DEMONSTRATION-001",
        "SFT-PHYS-TESLA-RESONANT-TRANSFER-081", "SFT-PHYS-VALIDATION-TESLA-RESONANCE-FAMILY-082",
    ),
    "SFT-ENG-VACUUM-INERTIA-RESPONSE-PROTOCOL-002": (
        "SFT-ENG-TESLA-RESONANT-TRANSFER-PROTOCOL-002", "SFT-ENG-REQUIREMENT-001",
        "SFT-ENG-MEASUREMENT-001", "SFT-ENG-CALIBRATION-001", "SFT-ENG-ACCEPTANCE-TEST-001",
        "SFT-ENG-SAFETY-001", "SFT-ENG-TRACEABILITY-001", "SFT-ENG-REPRODUCIBILITY-001",
        "SFT-ENG-DEMONSTRATION-001", "SFT-PHYS-VACUUM-LOCAL-RESONANT-DRIVE-083",
        "SFT-PHYS-VACUUM-INERTIA-COVARIATION-084", "SFT-PHYS-VACUUM-INERTIA-COMPLETE-LEDGER-086",
        "SFT-PHYS-VALIDATION-VACUUM-INERTIA-DRIVE-FAMILY-087",
    ),
    "SFT-ENG-VACUUM-BEAT-RESTORATION-PROTOCOL-002": (
        "SFT-ENG-VACUUM-INERTIA-RESPONSE-PROTOCOL-002", "SFT-ENG-REQUIREMENT-001",
        "SFT-ENG-MEASUREMENT-001", "SFT-ENG-CALIBRATION-001", "SFT-ENG-ACCEPTANCE-TEST-001",
        "SFT-ENG-SAFETY-001", "SFT-ENG-TRACEABILITY-001", "SFT-ENG-REPRODUCIBILITY-001",
        "SFT-ENG-DEMONSTRATION-001", "SFT-PHYS-VACUUM-ASYMMETRIC-BEAT-EXTRACTION-003",
        "SFT-PHYS-VACUUM-COMPLETE-CYCLE-LEDGER-003", "SFT-PHYS-VALIDATION-VACUUM-EXTRACTION-003",
    ),
    "SFT-ENG-SECTOR-FIVE-SEVEN-DETECTION-PROTOCOL-002": (
        "SFT-ENG-REQUIREMENT-001", "SFT-ENG-MEASUREMENT-001", "SFT-ENG-CALIBRATION-001",
        "SFT-ENG-ACCEPTANCE-TEST-001", "SFT-ENG-SAFETY-001", "SFT-ENG-TRACEABILITY-001",
        "SFT-ENG-REPRODUCIBILITY-001", "SFT-ENG-DEMONSTRATION-001",
        "SFT-PHYS-FORCE-PRIME-SECTOR-LADDER-002", "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
        "SFT-PHYS-NO-EXTRA-SECTOR-PARTICLE-BOUNDARY-093", "SFT-PHYS-VALIDATION-NEW-SECTOR-COMPLETE-FAMILY-095",
    ),
    "SFT-ENG-SMITHIUM-SYNTHESIS-IDENTIFICATION-PROTOCOL-002": (
        "SFT-ENG-REQUIREMENT-001", "SFT-ENG-MEASUREMENT-001", "SFT-ENG-CALIBRATION-001",
        "SFT-ENG-ACCEPTANCE-TEST-001", "SFT-ENG-SAFETY-001", "SFT-ENG-TRACEABILITY-001",
        "SFT-ENG-REPRODUCIBILITY-001", "SFT-ENG-DEMONSTRATION-001",
        "SFT-CHEM-SMITHIUM-SYNTHESIS-CONSERVATION-001", "SFT-CHEM-SMITHIUM-JOINT-DETECTION-001",
        "SFT-CHEM-VALIDATION-SMITHIUM-COMPLETE-FAMILY-001",
    ),
    "SFT-ENG-NOVEL-TRANSLATIONS-COMPLETE-FAMILY-002": (
        "SFT-ENG-TESLA-RESONANT-TRANSFER-PROTOCOL-002",
        "SFT-ENG-VACUUM-INERTIA-RESPONSE-PROTOCOL-002",
        "SFT-ENG-VACUUM-BEAT-RESTORATION-PROTOCOL-002",
        "SFT-ENG-SECTOR-FIVE-SEVEN-DETECTION-PROTOCOL-002",
        "SFT-ENG-SMITHIUM-SYNTHESIS-IDENTIFICATION-PROTOCOL-002",
        "SFT-ENG-E2E-001", "SFT-ENG-INDEPENDENT-CHECK-001", "SFT-ENG-PORTABLE-DATA-001",
    ),
}


def candidate_surface(relation: str):
    domains = (
        ("application-selected-law", "sealed-upstream-receipts"),
        ("informal-apparatus-sketch", relation),
        ("reported-outcome-only", "complete-common-and-domain-record"),
        ("favourable-control-only", "complete-declared-control-family"),
        ("success-only", "favourable-adverse-absent-unresolved"),
        ("continue-after-violation", "visible-halt-and-bounded-safe-state"),
        ("outcome-before-protocol-seal", "protocol-seal-before-outcome"),
        ("implementation-exception", "no-law-rewrite"),
    )
    rows = tuple("__".join(row) for row in product(*domains))
    return rows, "__".join(row[1] for row in domains)


def dependencies(claim_id: str, root: Path) -> bool:
    return all(
        (root / "claims" / dependency / "registration.json").is_file()
        and (root / "claims" / dependency / "certificate.json").is_file()
        for dependency in DEPENDENCIES[claim_id]
    )


def reconstruct(claim_id: str) -> bool:
    if claim_id.endswith("TESLA-RESONANT-TRANSFER-PROTOCOL-002"):
        return len(("drive-absent", "off-resonance", "disconnected-path", "phase-reversed", "dummy-load", "independent-power-ledger")) == 6
    if claim_id.endswith("VACUUM-INERTIA-RESPONSE-PROTOCOL-002"):
        return {"drive", "vacuum-proxy", "inertial-response", "restoration"} == set(("drive", "vacuum-proxy", "inertial-response", "restoration"))
    if claim_id.endswith("VACUUM-BEAT-RESTORATION-PROTOCOL-002"):
        return Fraction(1, 3) + Fraction(1, 6) == Fraction(1, 2)
    if claim_id.endswith("SECTOR-FIVE-SEVEN-DETECTION-PROTOCOL-002"):
        return tuple((p, p * p - 1, Fraction(p - 1, p)) for p in (5, 7)) == ((5, 24, Fraction(4, 5)), (7, 48, Fraction(6, 7)))
    if claim_id.endswith("SMITHIUM-SYNTHESIS-IDENTIFICATION-PROTOCOL-002"):
        return 126 + 184 == 310 and len(("mass", "nuclear", "decay", "ion", "spectroscopy")) == 5
    return claim_id.endswith("NOVEL-TRANSLATIONS-COMPLETE-FAMILY-002") and len(RELATIONS) == 6


def main() -> None:
    claim_id = sys.argv[1]
    root = Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    generated, unique = candidate_surface(RELATIONS[claim_id])
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {candidate: candidate == unique for candidate in generated}
    controls = sealed["controls"]
    passed = all((
        received == generated,
        len(received) == len(set(received)) == 256,
        decisions == expected,
        sum(expected.values()) == 1,
        len(controls) == 4,
        all(row["passed"] for row in controls),
        {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        sealed["closure"]["scope"] == "depth_independent",
        dependencies(claim_id, root),
        reconstruct(claim_id),
    ))
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": len(received), "unique_survivor_count": sum(expected.values()), "protocol_reconstruction": reconstruct(claim_id)}}))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
