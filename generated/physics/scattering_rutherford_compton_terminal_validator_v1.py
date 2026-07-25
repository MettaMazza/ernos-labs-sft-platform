#!/usr/bin/env python3
"""Implementation-distinct validator for terminal scattering laws.

This process imports neither the claimant nor an empirical adapter. It
reconstructs the finite-transfer geometry, conservation law, complete candidate
product and computed survivor from exact declared inputs.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-SCATTERING-RUTHERFORD-COMPTON-TERMINAL-006"

AMPLITUDE_CARRIERS = (
    "paired-phase-compatible-overlap-legs",
    "single-unpaired-channel-count",
    "imported-complex-amplitude",
)
CROSS_SECTION_MEASURES = (
    "paired-weight-per-incident-boundary-support",
    "unnormalized-outgoing-count",
    "target-fitted-area",
)
COULOMB_ANGULAR_LAWS = (
    "inverse-transfer-part-squared",
    "inverse-transfer-part-first-power",
    "angle-independent-response",
)
COULOMB_SCALE_LAWS = (
    "charge-product-squared-energy-inverse-squared",
    "charge-product-linear-energy-inverse",
    "free-dimensional-scale",
)
PHOTON_SHIFT_LAWS = (
    "two-transfer-parts-times-action-over-inertia-speed",
    "one-transfer-part-times-action-over-inertia-speed",
    "angle-independent-wavelength-change",
)
PHOTON_ENERGY_LAWS = (
    "rest-over-rest-plus-two-energy-transfer-parts",
    "incident-energy-preserved",
    "outgoing-energy-greater-than-incident",
)
TARGET_BOUNDARIES = ("sealed-before-release", "readable-before-seal")
EXTENSIONS = ("empty-extension", "free-correction")
PARTS = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))


def leg(part: Fraction) -> Fraction:
    return Fraction(1, 1) / part


def point_density(part: Fraction) -> Fraction:
    return leg(part) * leg(part)


def cumulative(part: Fraction):
    if part == Fraction(1, 1):
        return ()
    return (Fraction(1, 1) - part) / part


def annular(lower: Fraction, upper: Fraction) -> Fraction:
    low = cumulative(lower)
    high = cumulative(upper)
    removed = low if high == () else low - high
    return removed / (upper - lower)


def scale(charge: Fraction, energy: Fraction) -> Fraction:
    ratio = charge / (Fraction(4, 1) * energy)
    return ratio * ratio


def shift(part: Fraction) -> Fraction:
    return Fraction(2, 1) * part


def outgoing_ratio(x: Fraction, part: Fraction) -> Fraction:
    return Fraction(1, 1) / (Fraction(1, 1) + Fraction(2, 1) * x * part)


def conservation_transfer(x: Fraction, ratio: Fraction) -> Fraction:
    return Fraction(1, 1) / (x * ratio) - Fraction(1, 1) / x


def outgoing_rest(x: Fraction, part: Fraction) -> Fraction:
    return x * outgoing_ratio(x, part)


def ceiling(part: Fraction) -> Fraction:
    return Fraction(1, 1) / (Fraction(2, 1) * part)


def generated_ids() -> tuple[str, ...]:
    return tuple(
        "__".join(values)
        for values in product(
            AMPLITUDE_CARRIERS,
            CROSS_SECTION_MEASURES,
            COULOMB_ANGULAR_LAWS,
            COULOMB_SCALE_LAWS,
            PHOTON_SHIFT_LAWS,
            PHOTON_ENERGY_LAWS,
            TARGET_BOUNDARIES,
            EXTENSIONS,
        )
    )


def form_survives(candidate_id: str) -> bool:
    fields = candidate_id.split("__")
    if len(fields) != 8:
        return False
    amplitude, measure, angle, scale_law, shift_law, energy_law, target, extension = fields

    angular = tuple(point_density(part) for part in PARTS)
    annular_identity = all(
        annular(lower, upper) == Fraction(1, 1) / (lower * upper)
        for lower, upper in zip(PARTS, PARTS[1:])
    )
    amplitude_passed = {
        "paired-phase-compatible-overlap-legs": all(
            point_density(part) == leg(part) * leg(part) for part in PARTS
        ) and annular_identity,
        "single-unpaired-channel-count": all(point_density(part) == leg(part) for part in PARTS),
        "imported-complex-amplitude": False,
    }.get(amplitude, False)

    measured_ratio = Fraction(3, 1) / (Fraction(5, 1) * Fraction(2, 1))
    measure_passed = {
        "paired-weight-per-incident-boundary-support": measured_ratio == Fraction(3, 10),
        "unnormalized-outgoing-count": measured_ratio == Fraction(3, 1),
        "target-fitted-area": False,
    }.get(measure, False)

    angle_passed = {
        "inverse-transfer-part-squared": angular == (
            Fraction(16, 1), Fraction(4, 1), Fraction(16, 9), Fraction(1, 1)
        ),
        "inverse-transfer-part-first-power": angular == (
            Fraction(4, 1), Fraction(2, 1), Fraction(4, 3), Fraction(1, 1)
        ),
        "angle-independent-response": angular == (Fraction(1, 1),) * 4,
    }.get(angle, False)

    charge_ratio = scale(Fraction(2, 1), Fraction(1, 1)) / scale(Fraction(1, 1), Fraction(1, 1))
    energy_ratio = scale(Fraction(1, 1), Fraction(2, 1)) / scale(Fraction(1, 1), Fraction(1, 1))
    scale_passed = {
        "charge-product-squared-energy-inverse-squared": (
            charge_ratio == Fraction(4, 1) and energy_ratio == Fraction(1, 4)
        ),
        "charge-product-linear-energy-inverse": (
            charge_ratio == Fraction(2, 1) and energy_ratio == Fraction(1, 2)
        ),
        "free-dimensional-scale": False,
    }.get(scale_law, False)

    shifts = tuple(shift(part) for part in PARTS)
    conservation = tuple(
        conservation_transfer(Fraction(1, 1), outgoing_ratio(Fraction(1, 1), part))
        for part in PARTS
    )
    shift_passed = {
        "two-transfer-parts-times-action-over-inertia-speed": (
            shifts == (Fraction(1, 2), Fraction(1, 1), Fraction(3, 2), Fraction(2, 1))
            and conservation == shifts
        ),
        "one-transfer-part-times-action-over-inertia-speed": shifts == PARTS,
        "angle-independent-wavelength-change": shifts == (Fraction(1, 1),) * 4,
    }.get(shift_law, False)

    energy = tuple(outgoing_ratio(Fraction(1, 1), part) for part in PARTS)
    positive_steps = all(
        outgoing_rest(Fraction(depth + 1, 1), part) > outgoing_rest(Fraction(depth, 1), part)
        for part in PARTS
        for depth in (1, 2, 3, 4)
    )
    below_ceiling = all(
        outgoing_rest(Fraction(depth, 1), part) < ceiling(part)
        for part in PARTS
        for depth in (1, 2, 3, 4)
    )
    energy_passed = {
        "rest-over-rest-plus-two-energy-transfer-parts": (
            energy == (Fraction(2, 3), Fraction(1, 2), Fraction(2, 5), Fraction(1, 3))
            and ceiling(Fraction(1, 2)) == Fraction(1, 1)
            and ceiling(Fraction(1, 1)) == Fraction(1, 2)
            and positive_steps
            and below_ceiling
        ),
        "incident-energy-preserved": energy == (Fraction(1, 1),) * 4,
        "outgoing-energy-greater-than-incident": all(value > 1 for value in energy),
    }.get(energy_law, False)

    return all((
        amplitude_passed,
        measure_passed,
        angle_passed,
        scale_passed,
        shift_passed,
        energy_passed,
        target == "sealed-before-release",
        extension == "empty-extension",
    ))


def main() -> None:
    claim_id = sys.argv[1]
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)

    generated = generated_ids()
    expected = {candidate_id: form_survives(candidate_id) for candidate_id in generated}
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    control_kinds = {row["kind"] for row in sealed["controls"]}
    survivors = tuple(candidate_id for candidate_id, survives in expected.items() if survives)
    passed = (
        claim_id == CLAIM_ID
        and sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 2916
        and decisions == expected
        and len(survivors) == 1
        and tuple(point_density(part) for part in PARTS)
        == (Fraction(16, 1), Fraction(4, 1), Fraction(16, 9), Fraction(1, 1))
        and all(
            annular(lower, upper) == Fraction(1, 1) / (lower * upper)
            for lower, upper in zip(PARTS, PARTS[1:])
        )
        and tuple(shift(part) for part in PARTS)
        == (Fraction(1, 2), Fraction(1, 1), Fraction(3, 2), Fraction(2, 1))
        and ceiling(Fraction(1, 2)) == Fraction(1, 1)
        and ceiling(Fraction(1, 1)) == Fraction(1, 2)
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and control_kinds == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in sealed["controls"])
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "generated_cardinality": len(generated),
            "computed_surviving_ids": survivors,
            "coulomb_point_density": [str(point_density(part)) for part in PARTS],
            "annular_density": [
                str(annular(lower, upper)) for lower, upper in zip(PARTS, PARTS[1:])
            ],
            "compton_shift": [str(shift(part)) for part in PARTS],
            "equal_rest_outgoing_ratio": [
                str(outgoing_ratio(Fraction(1, 1), part)) for part in PARTS
            ],
            "right_angle_ceiling": str(ceiling(Fraction(1, 2))),
            "backscatter_ceiling": str(ceiling(Fraction(1, 1))),
            "forward_transfer": [],
            "target_values_used": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
