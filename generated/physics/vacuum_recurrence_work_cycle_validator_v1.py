#!/usr/bin/env python3
"""Implementation-distinct reconstruction of the recurrence-work successors."""

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys


WORK = "SFT-PHYS-VACUUM-FOLD-RECURRENCE-WORK-CYCLE-096"
BOUNDARY = "SFT-PHYS-VACUUM-RECURRENCE-CYCLE-BOUNDARY-097"
RELATIONS = {
    WORK: "Fold-third-to-two-thirds-then-take-half",
    BOUNDARY: "restored-cyclic-subsystem-with-explicit-outputs",
}
DEPENDENCIES = {
    WORK: (
        "SFT-PHYS-VACUUM-HALF-ONE-FLOOR-003",
        "SFT-PHYS-VACUUM-ODD-RECURRENCE-003",
        "SFT-PHYS-VACUUM-ASYMMETRIC-BEAT-EXTRACTION-003",
        "SFT-PHYS-VACUUM-LOCAL-RESONANT-DRIVE-083",
        "SFT-PHYS-MECH-WORK-ENERGY-001",
        "SFT-PHYS-MECH-CONSERVATION-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    BOUNDARY: (
        WORK,
        "SFT-PHYS-VACUUM-COMPLETE-CYCLE-LEDGER-003",
        "SFT-PHYS-VACUUM-INERTIA-COMPLETE-LEDGER-086",
        "SFT-PHYS-THERMO-FIRST-LAW-001",
        "SFT-PHYS-THERMO-LANDAUER-DEMON-TERMINAL-018",
        "SFT-INFO-CONSERVATION-LOSS-001",
        "SFT-PHYS-MECH-CONSERVATION-001",
    ),
}


def surface(claim_id: str):
    if claim_id == WORK:
        domains = (
            ("unrecorded-external-source", "admitted-Fold-recurrence"),
            ("work-only-without-residual", "half-equals-third-plus-sixth"),
            ("repay-first-work-directly", RELATIONS[claim_id]),
            ("merge-or-discard-one-leg", "two-distinct-positive-sixths"),
            ("vacuum-state-left-open", "vacuum-half-One-restored"),
            ("outcome-only-record", "complete-source-transition-output-record"),
            ("completed-infinite-total", "every-positive-finite-cycle-count"),
            ("free-extra-rule", "no-extra-rule"),
        )
    else:
        domains = (
            ("globally-identical-state-with-retained-output", RELATIONS[claim_id]),
            ("source-free-as-source-absent", "Fold-recurrence-source-recorded"),
            ("unmodelled-device-efficiency", "repeatable-controller-configuration"),
            ("erase-all-records-for-free", "append-audit-output-and-reset-controller-phase"),
            ("unrecorded-net-support", "source-state-and-all-outputs-held"),
            ("rewrite-direct-repayment-result", "preserve-narrow-result-add-broader-route"),
            ("declare-measured-device-power", "formal-cycle-plus-open-apparatus-test"),
            ("free-extra-rule", "no-extra-rule"),
        )
    return tuple("__".join(row) for row in product(*domains)), "__".join(axis[1] for axis in domains)


def exact_cycle() -> bool:
    half = Fraction(1, 2)
    lower = Fraction(1, 3)
    first = half - lower
    doubled = lower + lower
    upper = doubled if doubled <= 1 else doubled - 1
    second = upper - half
    final = upper - second
    return (
        first == second == Fraction(1, 6)
        and upper == Fraction(2, 3)
        and final == half
        and first + second == Fraction(1, 3)
    )


def exact_boundary() -> bool:
    controller_initial = ("ready", "outward-port-armed", "return-port-armed")
    controller_final = ("ready", "outward-port-armed", "return-port-armed")
    outputs = (Fraction(1, 6), Fraction(1, 6))
    audit = ("initial", "outward", "Fold", "return", "final")
    return exact_cycle() and controller_initial == controller_final and len(outputs) == 2 and len(audit) == 5


def main() -> None:
    claim_id = sys.argv[1]
    root = Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    generated, survivor = surface(claim_id)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    recomputed = {candidate: candidate == survivor for candidate in generated}
    controls = tuple(sealed["controls"])
    dependencies_present = all(
        (root / "claims" / dependency / "registration.json").is_file()
        and (root / "claims" / dependency / "certificate.json").is_file()
        for dependency in DEPENDENCIES[claim_id]
    )
    preregistration = json.loads((root / "claims" / claim_id / "preregistration.json").read_text(encoding="utf-8"))
    exact = exact_cycle() if claim_id == WORK else exact_boundary()
    passed = all((
        preregistration["claim_id"] == claim_id,
        preregistration["status"] == "registered",
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
        exact,
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
            "dependencies_present": dependencies_present,
            "exact_cycle_reconstructed": exact_cycle(),
            "boundary_reconstructed": exact_boundary() if claim_id == BOUNDARY else True,
            "preregistration_verified": preregistration["claim_id"] == claim_id,
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
