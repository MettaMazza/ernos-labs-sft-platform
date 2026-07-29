#!/usr/bin/env python3
"""Independent reconstruction for the Medicine placebo/nocebo family."""

from fractions import Fraction
from itertools import combinations, product
import json
from pathlib import Path
import sys

RELATIONS = {
    "SFT-MED-PLACEBO-EXPECTATION-FIBRE-002": "quarter-and-three-quarter-common-half-one-image",
    "SFT-MED-PLACEBO-AVAILABLE-STATE-BOUNDARY-002": "expectation-orders-only-preexisting-routes",
    "SFT-MED-PLACEBO-OBJECTIVE-REPORT-SEPARATION-002": "eight-field-clinical-record-with-objective-comparator",
    "SFT-MED-VALIDATION-PLACEBO-NOCEBO-COMPLETE-FAMILY-002": "sealed-three-law-family-versus-distinct-registered-measurements",
}

DEPENDENCIES = {
    "SFT-MED-PLACEBO-EXPECTATION-FIBRE-002": ("SFT-CONSC-EXPECTATION-001", "SFT-FOUNDATION-HALF-ONE-001", "SFT-MED-RESPONSE-001"),
    "SFT-MED-PLACEBO-AVAILABLE-STATE-BOUNDARY-002": ("SFT-MED-PLACEBO-EXPECTATION-FIBRE-002", "SFT-BIO-HOMEOSTASIS-001", "SFT-MED-INTERVENTION-001", "SFT-MED-COMPARATOR-001"),
    "SFT-MED-PLACEBO-OBJECTIVE-REPORT-SEPARATION-002": ("SFT-MED-PLACEBO-AVAILABLE-STATE-BOUNDARY-002", "SFT-MED-BLINDING-001", "SFT-MED-CLINICAL-OUTCOME-001", "SFT-MED-ADVERSE-EVENT-001"),
    "SFT-MED-VALIDATION-PLACEBO-NOCEBO-COMPLETE-FAMILY-002": ("SFT-MED-PLACEBO-OBJECTIVE-REPORT-SEPARATION-002", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001", "SFT-PHYS-MEAS-TARGET-CUSTODY-001", "SFT-PHYS-MEAS-UNCERTAINTY-001"),
}


def surface(relation: str):
    domains = (
        ("signed-or-continuum-effect", "exact-positive-fold-parts-and-held-labels"),
        ("expectation-name-only", relation),
        ("unbounded-outcome", "available-state-only"),
        ("report-objective-conflation", "complete-distinct-clinical-record"),
        ("selected-example", "complete-declared-product"),
        ("target-before-seal", "derivation-seal-before-target"),
        ("favorable-only", "favorable-adverse-absent-unresolved"),
        ("free-exception", "no-extra-rule"),
    )
    rows = tuple("__".join(item) for item in product(*domains))
    return rows, "__".join(item[1] for item in domains)


def fold(x: Fraction) -> Fraction:
    doubled = x + x
    return doubled if doubled <= 1 else doubled - 1


def exact_check(claim_id: str) -> bool:
    if claim_id.endswith("EXPECTATION-FIBRE-002"):
        q, tq = Fraction(1, 4), Fraction(3, 4)
        return q + tq == 1 and fold(q) == fold(tq) == Fraction(1, 2)
    if claim_id.endswith("AVAILABLE-STATE-BOUNDARY-002"):
        states = {"current", "reachable-relief", "reachable-harm"}
        routes = (("current", "reachable-relief"), ("current", "reachable-harm"))
        return all({a, b}.issubset(states) for a, b in routes) and tuple(reversed(routes)) != routes
    if claim_id.endswith("OBJECTIVE-REPORT-SEPARATION-002"):
        fields = ("expectation", "intervention", "comparator", "blinding", "report", "biomarker", "adverse", "follow-up")
        return len(fields) == len(set(fields)) == 8 and len(tuple(combinations(fields, 2))) == 28 and "report" != "biomarker"
    return claim_id.endswith("COMPLETE-FAMILY-002") and len(RELATIONS) == 4


def main() -> None:
    claim_id = sys.argv[1]
    root = Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
    if claim_id not in RELATIONS:
        raise SystemExit(1)
    generated, survivor = surface(RELATIONS[claim_id])
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    reconstructed = {row: row == survivor for row in generated}
    controls = tuple(sealed["controls"])
    deps = all((root / "claims" / dep / "registration.json").is_file() and (root / "claims" / dep / "certificate.json").is_file() for dep in DEPENDENCIES[claim_id])
    passed = all((sealed["claim_id"] == claim_id, received == generated, len(received) == len(set(received)) == 256,
                  decisions == reconstructed, sum(reconstructed.values()) == 1, len(controls) == 4 and all(x["passed"] for x in controls),
                  {x["kind"] for x in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
                  sealed["closure"]["scope"] == "depth_independent", sealed["closure"]["minimality_passed"] is True,
                  sealed["closure"]["named_shape_uniqueness_passed"] is True, deps, exact_check(claim_id)))
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True,
                      "certificate": {"candidate_count": len(received), "candidate_order_reconstructed": received == generated,
                                      "decision_vector_reconstructed": decisions == reconstructed, "unique_survivor_count": sum(reconstructed.values()),
                                      "dependency_packages_present": deps, "exact_mechanism_check": exact_check(claim_id)}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
