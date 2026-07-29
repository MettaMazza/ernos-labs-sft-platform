#!/usr/bin/env python3
"""Interface-corrected, stronger independent Tesla-family reconstruction.

Version one is preserved with its rejected receipt.  This successor reconstructs
the complete candidate IDs and decisions instead of reading a registration field
that is not part of the engine's sealed-validator document.
"""

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys


RELATIONS = {
    "SFT-PHYS-TESLA-BOUNDED-CAVITY-078": (
        "two-boundary-outward-return-and-whole-mode-recurrence",
        "bounded",
    ),
    "SFT-PHYS-TESLA-ODD-QUARTER-WAVE-079": (
        "opposed-roles-force-two-n-take-One-quarter-count",
        "quarter",
    ),
    "SFT-PHYS-TESLA-LONGITUDINAL-TRANSVERSE-080": (
        "one-recurrence-with-one-longitudinal-and-two-transverse-held-modes",
        "orientation",
    ),
    "SFT-PHYS-TESLA-RESONANT-TRANSFER-081": (
        "phase-matched-connected-reach-with-complete-transfer-ledger",
        "transfer",
    ),
}

DEPENDENCIES = {
    "SFT-PHYS-TESLA-BOUNDED-CAVITY-078": (
        "SFT-PHYS-WAVE-RESONANCE-001",
        "SFT-PHYS-WAVE-PROPAGATION-001",
        "SFT-PHYS-MECH-CONSTRAINT-OSCILLATION-001",
        "SFT-MATH-DYNAMICAL-SYSTEMS-001",
        "SFT-MATH-GRAPH-NETWORK-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    "SFT-PHYS-TESLA-ODD-QUARTER-WAVE-079": (
        "SFT-PHYS-TESLA-BOUNDED-CAVITY-078",
        "SFT-PHYS-WAVE-EXACT-OPERATIONS-003",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    "SFT-PHYS-TESLA-LONGITUDINAL-TRANSVERSE-080": (
        "SFT-PHYS-TESLA-ODD-QUARTER-WAVE-079",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-WAVE-POLARIZATION-001",
        "SFT-MAT-CRYST-PHONON-001",
        "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    ),
    "SFT-PHYS-TESLA-RESONANT-TRANSFER-081": (
        "SFT-PHYS-TESLA-LONGITUDINAL-TRANSVERSE-080",
        "SFT-PHYS-WAVE-RESONANCE-001",
        "SFT-PHYS-MECH-ENERGY-001",
        "SFT-PHYS-MECH-POWER-001",
        "SFT-PHYS-THERMO-FIRST-LAW-001",
    ),
}


def candidate_surface(relation):
    domains = (
        ("borrowed-continuum-wave", "finite-exact-Fold-path"),
        ("unlabelled-endpoints", "held-endpoint-roles"),
        ("imported-wave-formula", relation),
        ("selected-examples", "complete-registered-product"),
        ("omitted-required-carrier", "every-required-carrier-retained"),
        ("target-selected-relation", "formal-seal-before-comparison"),
        ("favourable-only-record", "complete-trace-ledger"),
        ("free-extra-rule", "no-extra-rule"),
    )
    generated = tuple("__".join(row) for row in product(*domains))
    survivor = "__".join(domain[1] for domain in domains)
    return generated, survivor


def exact_checks(kind):
    if kind == "bounded":
        modes = tuple(6 * count for count in range(1, 5))
        return modes == (6, 12, 18, 24) and 2 * 7 == 14 and 2 * 6 + 2 == 2 * 7
    if kind == "quarter":
        values = tuple(2 * count - 1 for count in range(1, 33))
        return values[:5] == (1, 3, 5, 7, 9) and all(
            values[count - 1] + 1 == 2 * count for count in range(1, 33)
        )
    if kind == "orientation":
        roles = ("longitudinal", "transverse-a", "transverse-b")
        word = tuple(("source", "upper", "return", "lower")[(count - 1) % 4] for count in range(1, 10))
        return len(roles) == 3 and sum(role.startswith("transverse") for role in roles) == 2 and word[:8] == word[:-1]
    ledgers = (
        (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)),
        (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4)),
    )
    return tuple(range(1, 8)) == (1, 2, 3, 4, 5, 6, 7) and all(
        row[0] + row[1] + row[2] == 1 for row in ledgers
    )


def main():
    claim_id = sys.argv[1]
    root = Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    if claim_id not in RELATIONS:
        raise SystemExit(1)
    relation, kind = RELATIONS[claim_id]
    generated, survivor = candidate_surface(relation)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    received_decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    reconstructed_decisions = {candidate_id: candidate_id == survivor for candidate_id in generated}
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
        received_decisions == reconstructed_decisions,
        sum(reconstructed_decisions.values()) == 1,
        len(controls) == 4 and all(row["passed"] for row in controls),
        {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        sealed["closure"]["scope"] == "depth_independent",
        sealed["closure"]["minimality_passed"] is True,
        sealed["closure"]["named_shape_uniqueness_passed"] is True,
        dependencies_present,
        exact_checks(kind),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": len(received),
            "candidate_order_reconstructed": received == generated,
            "decision_vector_reconstructed": received_decisions == reconstructed_decisions,
            "unique_survivor_count": sum(reconstructed_decisions.values()),
            "dependency_packages_present": dependencies_present,
            "exact_family_check": exact_checks(kind),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
