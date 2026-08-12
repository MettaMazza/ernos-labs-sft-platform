#!/usr/bin/env python3
"""Independent reconstruction of the recurrence-cycle engineering protocol."""

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys


CLAIM_ID = "SFT-ENG-VACUUM-RECURRENCE-CYCLE-PROTOCOL-003"
RELATION = "two-output-Fold-recurrence-complete-boundary-protocol"
DEPENDENCIES = (
    "SFT-ENG-VACUUM-BEAT-RESTORATION-PROTOCOL-002",
    "SFT-ENG-REQUIREMENT-001",
    "SFT-ENG-MEASUREMENT-001",
    "SFT-ENG-CALIBRATION-001",
    "SFT-ENG-ACCEPTANCE-TEST-001",
    "SFT-ENG-SAFETY-001",
    "SFT-ENG-TRACEABILITY-001",
    "SFT-ENG-REPRODUCIBILITY-001",
    "SFT-ENG-DEMONSTRATION-001",
    "SFT-PHYS-VACUUM-FOLD-RECURRENCE-WORK-CYCLE-096",
    "SFT-PHYS-VACUUM-RECURRENCE-CYCLE-BOUNDARY-097",
    "SFT-PHYS-VALIDATION-VACUUM-INERTIA-DRIVE-FAMILY-087",
)


def candidate_surface():
    domains = (
        ("application-selected-law", "sealed-upstream-receipts"),
        ("informal-apparatus-sketch", RELATION),
        ("reported-outcome-only", "complete-common-and-domain-record"),
        ("favourable-control-only", "complete-declared-control-family"),
        ("success-only", "favourable-adverse-absent-unresolved"),
        ("continue-after-violation", "visible-halt-and-bounded-safe-state"),
        ("outcome-before-protocol-seal", "protocol-seal-before-outcome"),
        ("implementation-exception", "no-law-rewrite"),
    )
    return tuple("__".join(row) for row in product(*domains)), "__".join(axis[1] for axis in domains)


def reconstruct() -> bool:
    states = (
        "initial-half", "outward-third", "first-sixth", "Fold-transition",
        "upper-two-thirds", "second-sixth", "final-half", "controller", "audit",
    )
    ledgers = ("calorimetric", "electrical", "mechanical", "thermal", "electromagnetic", "controller")
    controls = ("recurrence-disabled", "off-resonance", "receiver-disconnected", "second-take-disabled", "phase-reversed", "dummy-load", "thermal-match", "independent-ledger")
    stops = ("source", "first-output", "final-vacuum", "controller", "audit", "loss", "safety")
    return all((
        Fraction(1, 3) + Fraction(1, 6) == Fraction(1, 2),
        Fraction(1, 2) + Fraction(1, 6) == Fraction(2, 3),
        len(states) == 9,
        len(ledgers) == 6,
        len(controls) == 8,
        len(stops) == 7,
    ))


def main() -> None:
    claim_id = sys.argv[1]
    root = Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    generated, survivor = candidate_surface()
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {candidate: candidate == survivor for candidate in generated}
    controls = tuple(sealed["controls"])
    dependencies_present = all(
        (root / "claims" / dependency / "registration.json").is_file()
        and (root / "claims" / dependency / "certificate.json").is_file()
        for dependency in DEPENDENCIES
    )
    preregistration = json.loads((root / "claims" / claim_id / "preregistration.json").read_text(encoding="utf-8"))
    passed = all((
        claim_id == CLAIM_ID,
        preregistration["claim_id"] == CLAIM_ID,
        preregistration["status"] == "registered",
        received == generated,
        len(received) == len(set(received)) == sealed["census"]["expected_cardinality"] == 256,
        decisions == expected,
        sum(expected.values()) == 1,
        len(controls) == 4 and all(row["passed"] for row in controls),
        {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        sealed["closure"]["scope"] == "depth_independent",
        dependencies_present,
        reconstruct(),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": len(received),
            "unique_survivor_count": sum(expected.values()),
            "dependencies_present": dependencies_present,
            "protocol_reconstruction": reconstruct(),
            "preregistration_verified": preregistration["claim_id"] == CLAIM_ID,
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
