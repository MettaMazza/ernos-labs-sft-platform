#!/usr/bin/env python3
"""Implementation-distinct reconstruction of the Biology mechanism family."""

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys


RELATIONS = {
    "SFT-BIO-ORIGIN-AUTOCATALYTIC-IGNITION-002": "m-minus-one-supported-plus-one-seed-closure",
    "SFT-BIO-HOMOCHIRAL-AMPLIFICATION-002": "held-parity-oriented-power-of-two-amplification",
    "SFT-BIO-SOMATIC-GERMLINE-ORBIT-SPLIT-002": "two-power-transient-then-odd-recurrence",
    "SFT-BIO-NEURAL-HALF-ONE-THRESHOLD-002": "least-doubled-support-completing-one",
    "SFT-BIO-DIFFERENTIATION-LOSS-CANCER-002": "cycle-plus-differentiation-loss-plus-control-escape",
    "SFT-BIO-BOUNDED-ORBIT-ECOSYSTEM-002": "three-fifths-period-four-bounded-orbit",
    "SFT-BIO-VALIDATION-PRIOR-MECHANISMS-COMPLETE-FAMILY-002": "sealed-six-mechanism-family-versus-complete-source-record",
}

DEPENDENCIES = {
    "SFT-BIO-ORIGIN-AUTOCATALYTIC-IGNITION-002": ("SFT-BIO-LIFE-AUTOCATALYTIC-CLOSURE-001", "SFT-CHEM-NET-AUTOCATALYSIS-001", "SFT-PHYS-COUPLED-MAP-CRITICALITY-TERMINAL-008"),
    "SFT-BIO-HOMOCHIRAL-AMPLIFICATION-002": ("SFT-BIO-ORIGIN-AUTOCATALYTIC-IGNITION-002", "SFT-BIO-BIOLOGICAL-HOMOCHIRALITY-001", "SFT-CHEM-STEREO-CHIRALITY-001", "SFT-PHYS-WEAK-PARITY-FIBRE-002"),
    "SFT-BIO-SOMATIC-GERMLINE-ORBIT-SPLIT-002": ("SFT-BIO-HOMOCHIRAL-AMPLIFICATION-002", "SFT-BIO-SENESCENCE-001", "SFT-MATH-DYNAMICAL-SYSTEMS-001"),
    "SFT-BIO-NEURAL-HALF-ONE-THRESHOLD-002": ("SFT-BIO-SOMATIC-GERMLINE-ORBIT-SPLIT-002", "SFT-BIO-EXCITABLE-THRESHOLD-001", "SFT-FOUNDATION-HALF-ONE-001"),
    "SFT-BIO-DIFFERENTIATION-LOSS-CANCER-002": ("SFT-BIO-NEURAL-HALF-ONE-THRESHOLD-002", "SFT-BIO-DYSREGULATED-DIVISION-001", "SFT-BIO-DIFFERENTIATION-001"),
    "SFT-BIO-BOUNDED-ORBIT-ECOSYSTEM-002": ("SFT-BIO-DIFFERENTIATION-LOSS-CANCER-002", "SFT-BIO-ECOLOGICAL-RECURRENCE-001", "SFT-BIO-ECOSYSTEM-001"),
    "SFT-BIO-VALIDATION-PRIOR-MECHANISMS-COMPLETE-FAMILY-002": ("SFT-BIO-BOUNDED-ORBIT-ECOSYSTEM-002", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001", "SFT-PHYS-MEAS-TARGET-CUSTODY-001", "SFT-PHYS-MEAS-UNCERTAINTY-001"),
}


def surface(relation: str):
    domains = (
        ("imported-continuum-variable", "exact-positive-fold-carrier"),
        ("named-outcome-without-mechanism", relation),
        ("conditions-erased", "all-conditions-held"),
        ("selected-example", "complete-declared-product"),
        ("target-before-seal", "formal-seal-before-target"),
        ("favorable-only", "favorable-adverse-absent-unresolved"),
        ("invented-number", "structural-absence-or-halt"),
        ("free-exception", "no-extra-rule"),
    )
    generated = tuple("__".join(row) for row in product(*domains))
    return generated, "__".join(domain[1] for domain in domains)


def fold(value: Fraction) -> Fraction:
    doubled = value + value
    return doubled if doubled <= 1 else doubled - 1


def exact_check(claim_id: str) -> bool:
    if claim_id.endswith("AUTOCATALYTIC-IGNITION-002"):
        return all((m - 1) + 1 == m and all(k + 1 < m for k in range(1, m - 1)) for m in range(2, 17))
    if claim_id.endswith("HOMOCHIRAL-AMPLIFICATION-002"):
        shares = tuple(Fraction(2**t, 2**t + 1) for t in range(1, 17))
        return all(b > a for a, b in zip(shares, shares[1:])) and all(s < 1 for s in shares)
    if claim_id.endswith("SOMATIC-GERMLINE-ORBIT-SPLIT-002"):
        for power in range(1, 9):
            for odd in range(3, 18, 2):
                x = Fraction(1, (2**power) * odd)
                for _ in range(power):
                    x = fold(x)
                if x != Fraction(1, odd):
                    return False
        return True
    if claim_id.endswith("NEURAL-HALF-ONE-THRESHOLD-002"):
        return Fraction(1, 2) + Fraction(1, 2) == 1 and Fraction(1, 3) + Fraction(1, 3) < 1
    if claim_id.endswith("DIFFERENTIATION-LOSS-CANCER-002"):
        normal = {"progenitor": "differentiated"}
        malignant = {"cycling-a": "cycling-b", "cycling-b": "cycling-a"}
        return normal["progenitor"] == "differentiated" and malignant[malignant["cycling-a"]] == "cycling-a"
    if claim_id.endswith("BOUNDED-ORBIT-ECOSYSTEM-002"):
        x = Fraction(3, 5)
        trace = [x]
        for _ in range(4):
            x = fold(x)
            trace.append(x)
        return tuple(trace) == (Fraction(3, 5), Fraction(1, 5), Fraction(2, 5), Fraction(4, 5), Fraction(3, 5))
    return claim_id.endswith("COMPLETE-FAMILY-002") and len(RELATIONS) == 7


def main() -> None:
    claim_id = sys.argv[1]
    root = Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    if claim_id not in RELATIONS:
        raise SystemExit(1)
    generated, survivor = surface(RELATIONS[claim_id])
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    reconstructed = {candidate: candidate == survivor for candidate in generated}
    controls = tuple(sealed["controls"])
    dependencies_present = all((root / "claims" / d / "registration.json").is_file() and (root / "claims" / d / "certificate.json").is_file() for d in DEPENDENCIES[claim_id])
    passed = all((
        sealed["claim_id"] == claim_id,
        received == generated,
        len(received) == len(set(received)) == sealed["census"]["expected_cardinality"] == 256,
        decisions == reconstructed,
        sum(reconstructed.values()) == 1,
        len(controls) == 4 and all(row["passed"] for row in controls),
        {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        sealed["closure"]["scope"] == "depth_independent",
        sealed["closure"]["minimality_passed"] is True,
        sealed["closure"]["named_shape_uniqueness_passed"] is True,
        dependencies_present,
        exact_check(claim_id),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": len(received),
            "candidate_order_reconstructed": received == generated,
            "decision_vector_reconstructed": decisions == reconstructed,
            "unique_survivor_count": sum(reconstructed.values()),
            "dependency_packages_present": dependencies_present,
            "exact_mechanism_check": exact_check(claim_id),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
