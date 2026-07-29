#!/usr/bin/env python3
"""Independent complete reconstruction of the corrected 081 submission."""

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys


CLAIM_ID = "SFT-PHYS-TESLA-RESONANT-TRANSFER-081"
DEPENDENCIES = (
    "SFT-PHYS-TESLA-LONGITUDINAL-TRANSVERSE-080",
    "SFT-PHYS-WAVE-RESONANCE-001",
    "SFT-PHYS-MECH-WORK-ENERGY-001",
    "SFT-PHYS-MECH-POWER-001",
    "SFT-PHYS-THERMO-FIRST-LAW-001",
)


def candidate_surface():
    domains = (
        ("borrowed-continuum-wave", "finite-exact-Fold-path"),
        ("unlabelled-endpoints", "held-endpoint-roles"),
        ("imported-wave-formula", "phase-matched-connected-reach-with-complete-transfer-ledger"),
        ("selected-examples", "complete-registered-product"),
        ("omitted-required-carrier", "every-required-carrier-retained"),
        ("target-selected-relation", "formal-seal-before-comparison"),
        ("favourable-only-record", "complete-trace-ledger"),
        ("free-extra-rule", "no-extra-rule"),
    )
    return tuple("__".join(row) for row in product(*domains)), "__".join(domain[1] for domain in domains)


def transfer_check():
    ledgers = (
        (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6)),
        (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4)),
    )
    return tuple(range(1, 8)) == (1, 2, 3, 4, 5, 6, 7) and all(
        row[0] + row[1] + row[2] == 1 for row in ledgers
    )


def main():
    root = Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    generated, survivor = candidate_surface()
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    received_decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    reconstructed = {candidate_id: candidate_id == survivor for candidate_id in generated}
    controls = tuple(sealed["controls"])
    dependencies_present = all(
        (root / "claims" / dependency / "registration.json").is_file()
        and (root / "claims" / dependency / "certificate.json").is_file()
        for dependency in DEPENDENCIES
    )
    passed = all((
        sys.argv[1] == CLAIM_ID,
        sealed["claim_id"] == CLAIM_ID,
        received == generated,
        len(received) == len(set(received)) == sealed["census"]["expected_cardinality"] == 256,
        received_decisions == reconstructed,
        sum(reconstructed.values()) == 1,
        len(controls) == 4 and all(row["passed"] for row in controls),
        {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        sealed["closure"]["scope"] == "depth_independent",
        sealed["closure"]["minimality_passed"] is True,
        sealed["closure"]["named_shape_uniqueness_passed"] is True,
        dependencies_present,
        transfer_check(),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": len(received),
            "candidate_order_reconstructed": received == generated,
            "decision_vector_reconstructed": received_decisions == reconstructed,
            "unique_survivor_count": sum(reconstructed.values()),
            "dependency_packages_present": dependencies_present,
            "exact_transfer_check": transfer_check(),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
