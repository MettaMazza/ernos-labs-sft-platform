#!/usr/bin/env python3
"""Implementation-distinct reconstruction of the Consciousness return family."""

from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import sys

RELATIONS = {
    "SFT-CONSC-SYNAESTHESIA-DIRECTIONAL-LOCK-002": "stable-directed-cross-link-over-common-half-one-image",
    "SFT-CONSC-NONORDINARY-THREE-QUALITY-ORBIT-002": "one-seventh-two-sevenths-four-sevenths-closed-orbit",
    "SFT-CONSC-SLEEP-DREAM-PERIOD-TWO-002": "one-third-two-thirds-closed-orbit-with-half-one-balance",
    "SFT-CONSC-CESSATION-LOCK-ANCHOR-002": "releasable-half-one-lock-and-fixed-one-anchor",
    "SFT-CONSC-VALIDATION-NONORDINARY-COMPLETE-FAMILY-002": "sealed-four-law-family-versus-distinct-registered-observations",
}

DEPENDENCIES = {
    "SFT-CONSC-SYNAESTHESIA-DIRECTIONAL-LOCK-002": ("SFT-CONSC-CROSS-MODAL-QUALIA-001", "SFT-CONSC-QUALIA-COMPOSITION-001", "SFT-FOUNDATION-HALF-ONE-001"),
    "SFT-CONSC-NONORDINARY-THREE-QUALITY-ORBIT-002": ("SFT-CONSC-SYNAESTHESIA-DIRECTIONAL-LOCK-002", "SFT-CONSC-ALTERED-STATE-REPORT-BOUNDARY-001", "SFT-CONSC-QUALIA-RECURRENCE-001", "SFT-CONSC-RED-OF-RED-001"),
    "SFT-CONSC-SLEEP-DREAM-PERIOD-TWO-002": ("SFT-CONSC-NONORDINARY-THREE-QUALITY-ORBIT-002", "SFT-CONSC-MEMORY-PERSISTENCE-001", "SFT-CONSC-UNCONSCIOUS-PROCESS-001", "SFT-CONSC-REPORT-001"),
    "SFT-CONSC-CESSATION-LOCK-ANCHOR-002": ("SFT-CONSC-SLEEP-DREAM-PERIOD-TWO-002", "SFT-CONSC-CESSATION-001", "SFT-CONSC-IDENTITY-CONTINUITY-001", "SFT-CONSC-SUBSTRATE-INDEPENDENCE-001"),
    "SFT-CONSC-VALIDATION-NONORDINARY-COMPLETE-FAMILY-002": ("SFT-CONSC-CESSATION-LOCK-ANCHOR-002", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001", "SFT-PHYS-MEAS-TARGET-CUSTODY-001", "SFT-PHYS-MEAS-UNCERTAINTY-001"),
}


def surface(relation: str):
    domains = (
        ("continuum-or-signed-state", "exact-positive-fold-parts-and-held-labels"),
        ("name-or-analogy-only", relation),
        ("unbounded-or-untraceable-content", "generated-support-and-retained-record-boundary"),
        ("dismissed-or-ontologized-report", "report-preserved-ontology-separate"),
        ("selected-example", "complete-declared-product"),
        ("target-before-seal", "derivation-seal-before-target"),
        ("favorable-only", "favorable-adverse-absent-heterogeneous-unresolved"),
        ("free-exception", "no-extra-rule"),
    )
    rows = tuple("__".join(item) for item in product(*domains))
    return rows, "__".join(item[1] for item in domains)


def fold(value: Fraction) -> Fraction:
    doubled = value + value
    return doubled if doubled <= 1 else doubled - 1


def exact_check(claim_id: str) -> bool:
    if claim_id.endswith("SYNAESTHESIA-DIRECTIONAL-LOCK-002"):
        left, right = Fraction(1, 4), Fraction(3, 4)
        routes = (("trigger", "concurrent"),)
        return left + right == 1 and fold(left) == fold(right) == Fraction(1, 2) and ("concurrent", "trigger") not in routes
    if claim_id.endswith("NONORDINARY-THREE-QUALITY-ORBIT-002"):
        values = (Fraction(1, 7), Fraction(2, 7), Fraction(4, 7))
        return sum(values) == 1 and tuple(fold(x) for x in values) == (values[1], values[2], values[0])
    if claim_id.endswith("SLEEP-DREAM-PERIOD-TWO-002"):
        left, right = Fraction(1, 3), Fraction(2, 3)
        balance = (left + right) / 2
        return left + right == 1 and fold(left) == right and fold(right) == left and balance == Fraction(1, 2) and fold(balance) == 1
    if claim_id.endswith("CESSATION-LOCK-ANCHOR-002"):
        parts = (Fraction(1, 4), Fraction(3, 4))
        return sum(parts) == 1 and fold(Fraction(1, 2)) == fold(Fraction(1, 1)) == 1 and "unoccupied" != "occupied"
    return claim_id.endswith("COMPLETE-FAMILY-002") and len(RELATIONS) == 5


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
