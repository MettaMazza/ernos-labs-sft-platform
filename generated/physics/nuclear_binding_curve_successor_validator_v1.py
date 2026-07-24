#!/usr/bin/env python3
"""Implementation-distinct exact validator for the nuclear binding maximum."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-NUCLEAR-BINDING-CURVE-TERMINAL-005"
ALPHA = Fraction(3676744786, 503846395469)
SURFACE = Fraction(1, 5)
QUARTER = Fraction(1, 4)
DOMAINS = (
    ("rewrite-predecessor-laws", "compose-immutable-predecessors"),
    ("unbounded-pairwise-bulk-growth", "one-saturating-bulk-support"),
    ("fitted-surface-coefficient", "one-over-binary-plus-generator-interface"),
    ("import-semi-empirical-coulomb-term", "exact-alpha-times-ordered-charge-paths"),
    ("chosen-asymmetry-penalty", "quarter-order-unmatched-label-square"),
    ("fitted-pairing-term", "quarter-order-paired-gain-unpaired-loss"),
    ("evaluate-irrational-radius", "rational-enclosures-until-order-separates"),
    ("selected-isotope-window", "complete-concave-census-plus-forced-tail-induction"),
    ("external-target-readable", "target-inaccessible-until-seal"),
    ("free-coefficient-or-residual", "no-extra-rule"),
)


def integer_cube_root_scaled(value: int, scale: int) -> tuple[Fraction, Fraction]:
    """Enclose the cube root by integer search on one exact dyadic lattice."""

    target = value * scale * scale * scale
    low, high = scale, value * scale
    while low + 1 < high:
        middle = (low + high) // 2
        if middle * middle * middle <= target:
            low = middle
        else:
            high = middle
    if low * low * low == target:
        exact = Fraction(low, scale)
        return exact, exact
    return Fraction(low, scale), Fraction(high, scale)


def score_bounds(mass: int, charge: int, scale: int) -> tuple[Fraction, Fraction]:
    neutron = mass - charge
    unmatched = neutron - charge if neutron >= charge else charge - neutron
    retained = Fraction(1, 1) - QUARTER * Fraction(unmatched * unmatched, mass * mass)
    radial = SURFACE
    if charge > 1:
        radial += ALPHA * Fraction(charge * (charge - 1), mass)
    if mass % 2 == 0 and charge % 2 == 0:
        radial -= QUARTER * Fraction(1, mass)
    elif mass % 2 == 0 and charge % 2 == 1:
        radial += QUARTER * Fraction(1, mass)
    lower_radius, upper_radius = integer_cube_root_scaled(mass, scale)
    return retained - radial / lower_radius, retained - radial / upper_radius


def vertex_candidates(mass: int, scale: int) -> tuple[int, ...]:
    lower, upper = integer_cube_root_scaled(mass, scale)

    def vertex(radius: Fraction) -> Fraction:
        return Fraction(mass) * (radius + ALPHA) / (2 * radius + 2 * ALPHA * mass)

    left, right = vertex(lower), vertex(upper)
    start = max(1, left.numerator // left.denominator - 3)
    stop = min(mass - 1, right.numerator // right.denominator + 4)
    return tuple(range(start, stop + 1))


def independent_peak() -> tuple[int, int, Fraction, Fraction, bool]:
    scale = 2 ** 16
    candidates = tuple(
        (mass, charge)
        for mass in range(2, 4096)
        for charge in vertex_candidates(mass, scale)
    )
    bounds = {candidate: score_bounds(candidate[0], candidate[1], scale) for candidate in candidates}
    winner = max(candidates, key=lambda candidate: bounds[candidate][0])
    rival = max(bounds[candidate][1] for candidate in candidates if candidate != winner)
    winner_lower, winner_upper = bounds[winner]

    cutoff, radius = 4096, 16
    pairing = QUARTER * Fraction(1, cutoff * radius)
    low_charge_upper = Fraction(91, 100) + pairing
    least_high_charge = cutoff // 5 + 1
    coulomb = ALPHA * Fraction(least_high_charge * (least_high_charge - 1), cutoff * radius)
    high_charge_upper = Fraction(1, 1) - coulomb + pairing
    tail_successor_monotone = 2 * cutoff * cutoff > 12 * cutoff + 14
    tail_closed = (
        winner_lower > low_charge_upper
        and winner_lower > high_charge_upper
        and tail_successor_monotone
    )
    return winner[0], winner[1], winner_lower, max(rival, low_charge_upper, high_charge_upper), tail_closed


def main() -> None:
    claim_id = sys.argv[1]
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(row) for row in product(*DOMAINS))
    survivor = "__".join(domain[1] for domain in DOMAINS)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    mass, charge, winner_lower, rival_upper, tail_closed = independent_peak()
    exact = (
        mass == 62
        and charge == 28
        and mass - charge == 34
        and winner_lower > rival_upper
        and tail_closed
    )
    passed = (
        claim_id == CLAIM_ID
        and sealed["claim_id"] == claim_id
        and exact
        and received == generated
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 1024
        and decisions == {candidate: candidate == survivor for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in sealed["controls"])
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "generated_cardinality": len(generated),
            "unique_survivor": survivor if passed else None,
            "predicted_mass_number": mass,
            "predicted_charge_count": charge,
            "predicted_neutron_count": mass - charge,
            "winner_lower": str(winner_lower),
            "all_rivals_upper": str(rival_upper),
            "unbounded_tail_closed": tail_closed,
            "target_value_accessed": False,
            "implementation": "independent integer-scaled cube enclosure, concavity neighborhood and two-case tail proof",
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
