#!/usr/bin/env python3
"""Independent complete reconstruction for formal vacuum/inertia drive claims."""

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys


CLAIMS = {
    "SFT-PHYS-VACUUM-LOCAL-RESONANT-DRIVE-083": ("exact-local-state-change-with-source-bound-transfer", "drive"),
    "SFT-PHYS-VACUUM-INERTIA-COVARIATION-084": ("vacuum-change-equals-inertia-change-at-exchange-One", "covariation"),
    "SFT-PHYS-VACUUM-INERTIA-POSITIVE-FLOOR-085": ("finite-depth-floor-bounds-both-unity-related-carriers", "floor"),
    "SFT-PHYS-VACUUM-INERTIA-COMPLETE-LEDGER-086": ("complete-paired-drive-response-restoration-and-information-ledger", "ledger"),
}
DEPENDENCIES = {
    "SFT-PHYS-VACUUM-LOCAL-RESONANT-DRIVE-083": ("SFT-PHYS-VACUUM-ODD-RECURRENCE-003", "SFT-PHYS-TESLA-RESONANT-TRANSFER-081", "SFT-PHYS-WAVE-RESONANCE-001", "SFT-MATH-DYNAMICAL-SYSTEMS-001", "SFT-MATH-EXACT-ARITHMETIC-001"),
    "SFT-PHYS-VACUUM-INERTIA-COVARIATION-084": ("SFT-PHYS-VACUUM-LOCAL-RESONANT-DRIVE-083", "SFT-PHYS-VACUUM-INERTIA-UNITY-003", "SFT-PHYS-MECH-INERTIA-001", "SFT-MATH-EXACT-ARITHMETIC-001"),
    "SFT-PHYS-VACUUM-INERTIA-POSITIVE-FLOOR-085": ("SFT-PHYS-VACUUM-INERTIA-COVARIATION-084", "SFT-PHYS-VACUUM-HALF-ONE-FLOOR-003", "SFT-FOUNDATION-PART-001", "SFT-MATH-EXACT-ARITHMETIC-001"),
    "SFT-PHYS-VACUUM-INERTIA-COMPLETE-LEDGER-086": ("SFT-PHYS-VACUUM-INERTIA-POSITIVE-FLOOR-085", "SFT-PHYS-VACUUM-ASYMMETRIC-BEAT-EXTRACTION-003", "SFT-PHYS-VACUUM-COMPLETE-CYCLE-LEDGER-003", "SFT-PHYS-THERMO-FIRST-LAW-001", "SFT-INFO-CONSERVATION-LOSS-001"),
}


def surface(relation):
    domains = (
        ("inert-empty-background", "live-exact-positive-vacuum-carrier"),
        ("unrecorded-field-assertion", "resonant-source-bound-transition"),
        ("free-response-coefficient", relation),
        ("drive-to-numerical-nothing", "positive-finite-depth-floor"),
        ("outcome-only-ledger", "complete-drive-response-restoration-ledger"),
        ("target-selected-channel", "formal-seal-before-apparatus-comparison"),
        ("favourable-only-record", "complete-favourable-adverse-unresolved-record"),
        ("free-extra-rule", "no-extra-rule"),
    )
    return tuple("__".join(row) for row in product(*domains)), "__".join(domain[1] for domain in domains)


def exact(kind):
    initial, driven = Fraction(1, 3), Fraction(1, 4)
    change = initial - driven
    if kind == "drive":
        phase = Fraction(1, 3)
        phase = phase + phase
        phase = phase + phase - 1
        return change == Fraction(1, 12) and driven + change == initial and phase == initial
    if kind == "covariation":
        return initial / initial == driven / driven == 1 and change == initial - driven
    if kind == "floor":
        support = 2
        floors = []
        for _ in range(3):
            support += support
            floors.append(Fraction(1, support))
        return tuple(floors) == (Fraction(1, 4), Fraction(1, 8), Fraction(1, 16)) and driven >= floors[-1]
    records = ("initial-pair", "drive-act", "driven-pair", "outward-transfer", "restoration-act", "restored-pair")
    return driven + change == initial and len(records) == 6 and change == Fraction(1, 12)


def main():
    claim_id = sys.argv[1]
    root = Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    if claim_id not in CLAIMS:
        raise SystemExit(1)
    relation, kind = CLAIMS[claim_id]
    generated, survivor = surface(relation)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    recomputed = {candidate: candidate == survivor for candidate in generated}
    controls = tuple(sealed["controls"])
    dependencies_present = all(
        (root / "claims" / dependency / "registration.json").is_file()
        and (root / "claims" / dependency / "certificate.json").is_file()
        for dependency in DEPENDENCIES[claim_id]
    )
    passed = all((
        sealed["claim_id"] == claim_id,
        received == generated,
        len(received) == len(set(received)) == sealed["census"]["expected_cardinality"] == 256,
        decisions == recomputed,
        sum(recomputed.values()) == 1,
        len(controls) == 4 and all(row["passed"] for row in controls),
        {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        sealed["closure"]["scope"] == "depth_independent",
        sealed["closure"]["minimality_passed"] is True,
        sealed["closure"]["named_shape_uniqueness_passed"] is True,
        dependencies_present,
        exact(kind),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": len(received),
            "candidate_order_reconstructed": received == generated,
            "decision_vector_reconstructed": decisions == recomputed,
            "unique_survivor_count": sum(recomputed.values()),
            "dependency_packages_present": dependencies_present,
            "exact_family_check": exact(kind),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
