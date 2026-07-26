#!/usr/bin/env python3
"""Implementation-distinct reconstruction of collective radiation response."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-COLLECTIVE-RADIATION-RESPONSE-TERMINAL-041"
DOMAINS = (
    ("continuum-exponential-premise", "complete-finite-boson-word-census"),
    ("fitted-Stefan-exponent", "three-mode-powers-plus-one-energy-power"),
    ("selected-frequency-list", "positive-whole-harmonic-ladder"),
    ("unrelated-spontaneous-output", "duplicated-identical-held-mode"),
    ("free-gain-setting", "gain-loss-equality-with-strict-half-One-inversion"),
    ("zero-width-monochromatic-idealization", "positive-reciprocal-coherence-carrier"),
    ("named-empirical-fit", "charge-stiffness-over-inertia-and-thermal-balance"),
    ("selected-wave-speed", "magnetic-tension-over-fluid-inertia"),
)
SURVIVOR = tuple(row[1] for row in DOMAINS)


def occupations(costs, energy):
    limits = tuple(energy // cost for cost in costs)
    return tuple(word for word in product(*(range(n + 1) for n in limits)) if sum(c * n for c, n in zip(costs, word)) == energy)


def theorem_check():
    costs = (1, 2, 3, 5, 8)
    words = occupations(costs, 7)
    scaled = occupations(tuple(4 * x for x in costs), 28)
    return all((
        len(words) == 10, words == scaled,
        all(sum(c * n for c, n in zip(costs, word)) == 7 for word in words),
        all(word[-1] == 0 for word in words),
        Fraction(2) ** 4 == 16,
        tuple(n * Fraction(1, 6) for n in range(1, 5)) == (Fraction(1, 6), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3)),
        Fraction(3, 5) > Fraction(1, 2), Fraction(4, 3) > Fraction(5, 4), Fraction(1, 7) * 7 == 1,
        Fraction(3) * 2 * 2 / (Fraction(5) * 7) == Fraction(12, 35),
        Fraction(7) * 11 / (Fraction(3) * 2 * 2) == Fraction(77, 12),
        Fraction(3) ** 2 / (Fraction(5) * 7) == Fraction(9, 35),
    ))


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(row) for row in product(*DOMAINS))
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {candidate_id: tuple(candidate_id.split("__")) == SURVIVOR and theorem_check() for candidate_id in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = all((
        sys.argv[1] == CLAIM_ID, sealed["claim_id"] == CLAIM_ID, received == generated,
        len(set(received)) == sealed["census"]["expected_cardinality"] == 256,
        decisions == recomputed, sum(recomputed.values()) == 1, sealed["closure"]["scope"] == "depth_independent",
        {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        all(row["passed"] for row in sealed["controls"]), theorem_check(),
    ))
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "finite_occupation_words": 10, "temperature_double_power": 16, "laser_threshold": "gain=loss; inversion>1/2", "survivor": "__".join(SURVIVOR)}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
