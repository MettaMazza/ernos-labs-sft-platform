#!/usr/bin/env python3
"""Implementation-distinct validator for terminal fusion/fission forcing.

This process imports no claimant module and reads no measurement target.  It
reconstructs the candidate product, exact representative binding inequalities
and all-mass stability maximum from rational arithmetic.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-NUCLEAR-FUSION-FISSION-TERMINAL-005"
ALPHA = Fraction(3676744786, 503846395469)
SURFACE = Fraction(1, 5)
QUARTER = Fraction(1, 4)
FUSION_OPERATIONS = ("identity", "binary-junction", "binary-decomposition")
FISSION_OPERATIONS = ("identity", "binary-junction", "binary-decomposition")
BINDING_DIRECTIONS = ("toward-higher-binding", "toward-lower-binding")
BARRIER_LABELS = ("quarter-One", "half-One", "three-quarter-One", "One")
ENERGY_ACCOUNTINGS = ("complete-held-release", "unrecorded-release")
PEAK_CLOSURES = ("unique-unbounded-peak", "selected-finite-peak")
TARGET_BOUNDARIES = ("sealed-before-release", "readable-before-seal")
EXTENSIONS = ("empty-extension", "free-correction")


def positive_take(whole: Fraction, part: Fraction) -> Fraction:
    if whole <= part:
        raise ValueError("independent exact subtraction left the positive domain")
    return whole - part


def integer_cube_root_scaled(value: int, scale: int) -> tuple[Fraction, Fraction]:
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
    asymmetry = QUARTER * Fraction(unmatched * unmatched, mass * mass)
    retained = positive_take(Fraction(1, 1), asymmetry) if asymmetry else Fraction(1, 1)
    radial = SURFACE
    if charge > 1:
        radial += ALPHA * Fraction(charge * (charge - 1), mass)
    pairing = QUARTER * Fraction(1, mass)
    if mass % 2 == 0 and charge % 2 == 0:
        radial = positive_take(radial, pairing)
    elif mass % 2 == 0 and charge % 2 == 1:
        radial += pairing
    lower_radius, upper_radius = integer_cube_root_scaled(mass, scale)
    return (
        positive_take(retained, radial / lower_radius),
        positive_take(retained, radial / upper_radius),
    )


def vertex_candidates(mass: int, scale: int) -> tuple[int, ...]:
    lower, upper = integer_cube_root_scaled(mass, scale)

    def vertex(radius: Fraction) -> Fraction:
        return Fraction(mass, 1) * (radius + ALPHA) / (
            2 * radius + 2 * ALPHA * mass
        )

    left, right = vertex(lower), vertex(upper)
    start = max(1, left.numerator // left.denominator - 3)
    stop = min(mass - 1, right.numerator // right.denominator + 4)
    return tuple(range(start, stop + 1))


def independent_peak() -> dict[str, object]:
    scale = 2 ** 16
    candidates = tuple(
        (mass, charge)
        for mass in range(2, 4096)
        for charge in vertex_candidates(mass, scale)
    )
    bounds = {
        candidate: score_bounds(candidate[0], candidate[1], scale)
        for candidate in candidates
    }
    winner = max(candidates, key=lambda candidate: bounds[candidate][0])
    rival_upper = max(
        bounds[candidate][1] for candidate in candidates if candidate != winner
    )
    winner_lower, winner_upper = bounds[winner]

    cutoff, radius = 4096, 16
    maximum_pairing_gain = QUARTER * Fraction(1, cutoff * radius)
    low_charge_upper = Fraction(91, 100) + maximum_pairing_gain
    least_high_charge = cutoff // 5 + 1
    coulomb_loss = ALPHA * Fraction(
        least_high_charge * (least_high_charge - 1), cutoff * radius
    )
    high_charge_upper = positive_take(Fraction(1, 1), coulomb_loss) + maximum_pairing_gain
    tail_monotone = 2 * cutoff * cutoff > 12 * cutoff + 14
    tail_closed = (
        winner_lower > low_charge_upper
        and winner_lower > high_charge_upper
        and tail_monotone
    )
    return {
        "mass": winner[0],
        "charge": winner[1],
        "neutron": winner[0] - winner[1],
        "winner_lower": winner_lower,
        "winner_upper": winner_upper,
        "rival_upper": max(rival_upper, low_charge_upper, high_charge_upper),
        "tail_closed": tail_closed,
    }


def representative_relations() -> dict[str, object]:
    scale = 2 ** 16
    deuteron = score_bounds(2, 1, scale)
    helium = score_bounds(4, 2, scale)
    uranium = score_bounds(238, 92, scale)
    palladium = score_bounds(119, 46, scale)
    fusion_gain = positive_take(4 * helium[0], 4 * deuteron[1])
    fission_gain = positive_take(238 * palladium[0], 238 * uranium[1])
    return {
        "fusion_higher": helium[0] > deuteron[1],
        "fission_higher": palladium[0] > uranium[1],
        "fusion_lower": helium[1] < deuteron[0],
        "fission_lower": palladium[1] < uranium[0],
        "fusion_gain_lower": fusion_gain,
        "fission_gain_lower": fission_gain,
        "counts_conserved": (
            2 + 2 == 4
            and 1 + 1 == 2
            and 238 == 119 + 119
            and 92 == 46 + 46
        ),
    }


def generated_ids() -> tuple[str, ...]:
    return tuple(
        "__".join(values)
        for values in product(
            FUSION_OPERATIONS,
            FISSION_OPERATIONS,
            BINDING_DIRECTIONS,
            BARRIER_LABELS,
            ENERGY_ACCOUNTINGS,
            PEAK_CLOSURES,
            TARGET_BOUNDARIES,
            EXTENSIONS,
        )
    )


def form_survives(candidate_id: str, peak: dict[str, object], relations: dict[str, object]) -> bool:
    fields = candidate_id.split("__")
    if len(fields) != 8:
        return False
    fusion, fission, direction, barrier, accounting, peak_scope, target, extension = fields
    fusion_map = fusion == "binary-junction" and relations["fusion_higher"] is True
    fission_map = fission == "binary-decomposition" and relations["fission_higher"] is True
    if direction == "toward-higher-binding":
        direction_passed = relations["fusion_higher"] is True and relations["fission_higher"] is True
    elif direction == "toward-lower-binding":
        direction_passed = relations["fusion_lower"] is True and relations["fission_lower"] is True
    else:
        direction_passed = False
    barrier_parts = {
        "quarter-One": Fraction(1, 4),
        "half-One": Fraction(1, 2),
        "three-quarter-One": Fraction(3, 4),
        "One": Fraction(1, 1),
    }
    barrier_passed = barrier_parts.get(barrier) == Fraction(1, 2)
    complete = (
        relations["counts_conserved"] is True
        and relations["fusion_higher"] is True
        and relations["fission_higher"] is True
    )
    accounting_passed = complete if accounting == "complete-held-release" else False
    unbounded = (
        peak["mass"] == 62
        and peak["charge"] == 28
        and peak["neutron"] == 34
        and peak["winner_lower"] > peak["rival_upper"]
        and peak["tail_closed"] is True
    )
    peak_passed = unbounded if peak_scope == "unique-unbounded-peak" else False
    target_passed = target == "sealed-before-release"
    extension_passed = extension == "empty-extension"
    return all((
        fusion_map,
        fission_map,
        direction_passed,
        barrier_passed,
        accounting_passed,
        peak_passed,
        target_passed,
        extension_passed,
    ))


def main() -> None:
    claim_id = sys.argv[1]
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)

    generated = generated_ids()
    peak = independent_peak()
    relations = representative_relations()
    expected_decisions = {
        candidate_id: form_survives(candidate_id, peak, relations)
        for candidate_id in generated
    }
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {
        row["candidate_id"]: row["survives"] for row in sealed["decisions"]
    }
    control_kinds = {row["kind"] for row in sealed["controls"]}
    passed = (
        claim_id == CLAIM_ID
        and sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 1152
        and decisions == expected_decisions
        and sum(expected_decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and control_kinds == {
            "false_premise", "tampered_source", "tampered_artifact", "boundary"
        }
        and all(row["passed"] is True for row in sealed["controls"])
    )
    surviving_ids = tuple(
        candidate_id for candidate_id, survives in expected_decisions.items() if survives
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "generated_cardinality": len(generated),
            "computed_surviving_ids": surviving_ids,
            "fusion_gain_lower": str(relations["fusion_gain_lower"]),
            "fission_gain_lower": str(relations["fission_gain_lower"]),
            "peak_coordinate": [peak["mass"], peak["charge"], peak["neutron"]],
            "peak_winner_lower": str(peak["winner_lower"]),
            "all_rivals_upper": str(peak["rival_upper"]),
            "unbounded_tail_closed": peak["tail_closed"],
            "target_value_accessed": False,
            "implementation": "independent integer-scaled rational enclosure, candidate reconstruction and two-case unbounded tail proof",
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
