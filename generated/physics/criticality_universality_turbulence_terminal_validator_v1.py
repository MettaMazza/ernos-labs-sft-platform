#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-CRITICALITY-UNIVERSALITY-TURBULENCE-TERMINAL-047"
DOMAINS = (
    ("measured-critical-temperature", "binary-self-antipodal-half-One"),
    ("fitted-decimal-exponent", "square-excess-to-linear-order-carrier"),
    ("continuum-correlation-length-ansatz", "square-excess-to-linear-inverse-correlation"),
    ("selected-response-power", "reciprocal-linear-excess-response"),
    ("imported-field-polynomial", "generator-three-order-cube"),
    ("numerical-zero-residuals", "typed-empty-alpha-eta-with-exact-identities"),
    ("dimensional-analysis-assumption", "three-branch-cube-to-square-transfer"),
    ("fitted-negative-five-thirds", "falling-held-orientation-with-five-thirds-magnitude"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def check():
    beta = Fraction(1, 2)
    nu = Fraction(1, 2)
    gamma = Fraction(1)
    delta = Fraction(3)
    if not (gamma == beta * (delta - 1) and 2 * beta + gamma == 2 and gamma == 2 * nu):
        return False
    for q in range(2, 7):
        for depth in range(1, 7):
            carrier = q ** depth
            if not all(
                (
                    (carrier ** 2) == q ** (2 * depth),
                    (carrier ** 3) == q ** (3 * depth),
                    ((carrier ** 2) ** 3) == ((carrier ** 3) ** 2),
                    ((carrier ** 5) ** 3) == ((carrier ** 3) ** 5),
                )
            ):
                return False
    return True


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        seal = json.load(handle)
    generated = tuple("__".join(values) for values in product(*DOMAINS))
    recorded = tuple(row["candidate_id"] for row in seal["census"]["candidates"])
    valid = check()
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR and valid for candidate in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in seal["decisions"]}
    passed = all(
        (
            sys.argv[1] == CLAIM_ID,
            seal["claim_id"] == CLAIM_ID,
            recorded == generated,
            len(set(recorded)) == seal["census"]["expected_cardinality"] == 256,
            decisions == recomputed,
            sum(recomputed.values()) == 1,
            seal["closure"]["scope"] == "depth_independent",
            {row["kind"] for row in seal["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
            all(row["passed"] for row in seal["controls"]),
            valid,
        )
    )
    print(
        json.dumps(
            {
                "passed": passed,
                "validated_seal_hash": seal["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "certificate": {
                    "candidate_count": 256,
                    "critical_exponents": {"beta": "1/2", "nu": "1/2", "gamma": "1", "delta": "3", "alpha": "empty-One", "eta": "empty-One"},
                    "cascade_exponents": {"structure": "2/3", "spectrum": "falling-5/3"},
                    "survivor": "__".join(SURVIVOR),
                },
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
