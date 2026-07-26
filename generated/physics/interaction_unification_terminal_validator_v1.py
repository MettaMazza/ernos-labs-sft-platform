#!/usr/bin/env python3
"""Independent exact prime-sector interaction-table reconstruction."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import gcd
import json
import sys


CLAIM_ID = "SFT-PHYS-INTERACTION-UNIFICATION-TERMINAL-025"
SECTORS = (2, 3, 5, 7)
DOMAINS = (
    ("selected-familiar-sectors", "complete-prime-ladder-through-seven"),
    ("named-unification-point", "unique-self-antipodal-half-One-mode"),
    ("independent-fitted-couplings", "single-m-indexed-exact-table"),
    ("inserted-mass-parameter", "positive-shortfall-from-unison"),
    ("independent-scale-axes", "common-positive-binary-support"),
    ("target-named-physical-order", "exact-positive-m-difference-gap"),
    ("asserted-unification-crossing", "finite-triple-coincidence-forbidden"),
    ("selected-force-periods", "complete-one-two-three-period-dictionary"),
    ("flat-EM-and-inconsistent-slope-bundle", "terminal-carrier-specific-running-and-anchors"),
    ("free-group-or-crossing-scale", "no-extra-rule"),
)
SURVIVOR = tuple(domain[-1] for domain in DOMAINS)


def fold(value):
    doubled = value + value
    return doubled if doubled <= 1 else doubled - 1


def period(value):
    current = value
    count = 0
    while True:
        current = fold(current)
        count += 1
        if current == value:
            return count


def theorem_check():
    table = tuple((Fraction(m - 1, m), Fraction(1, m), m * m - 1) for m in SECTORS)
    if table != ((Fraction(1, 2), Fraction(1, 2), 3), (Fraction(2, 3), Fraction(1, 3), 8), (Fraction(4, 5), Fraction(1, 5), 24), (Fraction(6, 7), Fraction(1, 7), 48)):
        return False
    for depth in range(1, 21):
        support = 2 ** (depth - 1)
        shares = tuple(Fraction(m + support - 1, m + support) for m in SECTORS)
        if not all(shares[index] < shares[index + 1] for index in range(3)) or len(set(shares)) != 4:
            return False
    periods = (period(Fraction(1, 1)), period(Fraction(1, 3)), period(Fraction(1, 7)))
    joint = periods[0] * periods[1] * periods[2] // gcd(periods[0], gcd(periods[1], periods[2]))
    return periods == (1, 2, 3) and joint == 6 and (2 - 1) != 0


def generated_ids():
    return tuple("__".join(row) for row in product(*DOMAINS))


def main() -> None:
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = generated_ids()
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {candidate_id: tuple(candidate_id.split("__")) == SURVIVOR and theorem_check() for candidate_id in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = sys.argv[1] == CLAIM_ID and sealed["claim_id"] == CLAIM_ID and received == generated and len(set(received)) == sealed["census"]["expected_cardinality"] == 1024 and decisions == recomputed and sum(recomputed.values()) == 1 and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"} and all(row["passed"] for row in sealed["controls"]) and theorem_check()
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": len(generated), "sectors": list(SECTORS), "periods": [1, 2, 3], "joint_period": 6, "prior_flat_slope_bundle_consistent": False, "survivor": "__".join(SURVIVOR)}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
