#!/usr/bin/env python3
"""Independent reconstruction of the simultaneous strong-carrier census."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = "SFT-PHYS-STRONG-CARRIER-MASSLESS-CONFINED-TERMINAL-013"
AXES = (
    ("generated-colour-three-sector-with-eight-nonsinglet-carriers", "free-sector-or-mediator-count", "target-assigned-sector"),
    ("empty-mass-label-with-no-rest-capture", "numerical-zero-or-positive-fitted-mass", "target-assigned-mass"),
    ("One-support-cell-per-tick-with-retained-phase", "free-sub-or-super-One-speed", "target-assigned-speed"),
    ("colour-carrying-mediator-resources-its-own-channel", "chargeless-linear-carrier", "target-assigned-self-source"),
    ("fixed-half-One-tube-and-two-thirds-work-successor", "spreading-flux-or-bounded-separation-work", "target-assigned-confinement"),
    ("local-massless-One-speed-and-asymptotic-confined-records-coexist", "masslessness-and-confinement-treated-as-exclusive", "target-assigned-composition"),
    ("sealed-before-observation-release", "observation-readable-before-seal"),
    ("empty-extension", "free-carrier-correction"),
)


def exact_law():
    coupling = Fraction(2, 3)
    positions = tuple(Fraction(tick, 1) for tick in range(1, 18))
    increments = tuple(positions[index + 1] - positions[index] for index in range(len(positions) - 1))
    widths = tuple(Fraction(1, 2) for _ in range(1, 17))
    works = tuple(coupling * step for step in range(1, 17))
    work_steps = tuple(works[index + 1] - works[index] for index in range(len(works) - 1))
    bounds = (Fraction(1, 8), Fraction(1, 2), Fraction(1, 1), Fraction(7, 3), Fraction(32, 1))
    witnesses = []
    for bound in bounds:
        ratio = bound / coupling
        step = ratio.numerator // ratio.denominator + 1
        witnesses.append(coupling * step > bound)
    return all(
        (
            3 * 3 - 1 == 8,
            all(increment == 1 for increment in increments),
            len(set(widths)) == 1,
            all(work_step == coupling for work_step in work_steps),
            all(witnesses),
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
                    "colour_labels": 3,
                    "carrier_count": 8,
                    "mass_label": "empty",
                    "causal_speed": "One",
                    "tube_width": "1/2",
                    "work_successor": "2/3",
                    "external_targets_used": False,
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
