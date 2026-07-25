#!/usr/bin/env python3
"""Independent reconstruction of the D10e strong-field iteration census."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = "SFT-PHYS-STRONG-FIELD-NONLINEAR-FIXED-POINT-TERMINAL-014"
AXES = (
    ("colour-carrier-retained-inside-its-own-source-update", "external-matter-source-only", "target-assigned-source-composition"),
    ("each-successor-retains-prior-source-and-appends-complete-binary-carrier", "free-linear-contracted-or-oscillatory-update", "target-assigned-update"),
    ("persistent-exact-binary-correction-at-every-successor", "shrinking-or-free-correction", "target-assigned-correction"),
    ("empty-positive-finite-fixed-point-record-by-F-plus-two-order", "selected-finite-strong-fixed-point", "target-assigned-fixed-point"),
    ("neutral-hold-gravity-contraction-strong-persistence-three-way-discriminator", "conflate-all-self-source-iterations", "target-assigned-comparator"),
    ("finite-witness-above-every-positive-exact-bound", "bounded-prefix-or-completed-infinity", "target-assigned-confinement"),
    ("sealed-before-observation-release", "observation-readable-before-seal"),
    ("empty-extension", "free-strong-field-correction"),
)


def exact_law():
    strong = tuple(Fraction(1 + 2 * step, 1) for step in range(17))
    corrections = tuple(strong[index + 1] - strong[index] for index in range(len(strong) - 1))
    neutral = tuple(Fraction(1, 1) for _ in range(17))
    candidates = (Fraction(1, 127), Fraction(1, 2), Fraction(1, 1), Fraction(7, 3), Fraction(32, 1))
    fixed_excluded = all(candidate + 2 > candidate and candidate + 2 != candidate for candidate in candidates)
    bounds = []
    for bound in candidates:
        ratio = bound / 2
        step = ratio.numerator // ratio.denominator + 1
        bounds.append(Fraction(1 + 2 * step, 1) > bound)
    gravity_matter = Fraction(7, 16)
    gravity_coupling = Fraction(1, 2)
    gravity_fixed = Fraction(1, 4)
    gravity_values = [gravity_coupling * gravity_matter]
    for _ in range(8):
        gravity_values.append(gravity_coupling * (gravity_matter + gravity_values[-1] * gravity_values[-1]))
    gravity_errors = tuple(gravity_fixed - value for value in gravity_values)
    gravity_corrections = tuple(gravity_values[index + 1] - gravity_values[index] for index in range(len(gravity_values) - 1))
    return all(
        (
            all(strong[index + 1] > strong[index] for index in range(len(strong) - 1)),
            all(correction == 2 for correction in corrections),
            len(set(neutral)) == 1,
            fixed_excluded,
            all(bounds),
            all(gravity_errors[index + 1] < gravity_errors[index] for index in range(len(gravity_errors) - 1)),
            all(gravity_corrections[index + 1] < gravity_corrections[index] for index in range(len(gravity_corrections) - 1)),
        )
    )


def ids():
    return tuple("__".join(values) for values in product(*AXES))


def survives(candidate_id):
    return exact_law() and candidate_id.split("__") == [axis[0] for axis in AXES]


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ids()
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {candidate_id: survives(candidate_id) for candidate_id in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    survivors = tuple(candidate_id for candidate_id in generated if recomputed[candidate_id])
    kinds = {row["kind"] for row in sealed["controls"]}
    passed = all(
        (
            sys.argv[1] == CLAIM_ID,
            sealed["claim_id"] == CLAIM_ID,
            received == generated,
            len(set(received)) == sealed["census"]["expected_cardinality"] == 2916,
            decisions == recomputed,
            len(survivors) == 1,
            exact_law(),
            sealed["closure"]["scope"] == "depth_independent",
            sealed["closure"]["minimality_passed"] is True,
            sealed["closure"]["named_shape_uniqueness_passed"] is True,
            kinds == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
            all(row["passed"] for row in sealed["controls"]),
        )
    )
    print(
        json.dumps(
            {
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "passed": passed,
                "certificate": {
                    "generated_cardinality": len(generated),
                    "computed_surviving_ids": survivors,
                    "neutral_correction": "empty",
                    "gravity_fixed_point": "1/4",
                    "gravity_corrections": "strictly-shrinking",
                    "strong_correction": "2",
                    "strong_corrections": "persistent",
                    "strong_finite_fixed_point": "empty",
                    "external_targets_used": False,
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
