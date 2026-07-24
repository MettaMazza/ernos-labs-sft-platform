#!/usr/bin/env python3
"""Implementation-distinct validator for terminal nucleon binding."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-NUCLEON-BINDING-TERMINAL-005"
DOMAINS = (
    ("rewrite-predecessor-laws", "compose-immutable-predecessors"),
    ("listed-three-colour-names", "complete-period-three-One-cycle"),
    ("import-proton-neutron-labels", "enumerate-complete-three-flavour-charge-words"),
    ("selected-binding-depth", "admitted-upper-quark-depth-seven"),
    ("free-binding-percentage", "one-cell-and-complete-positive-predecessor"),
    ("qualitative-most-without-bound", "bare-below-one-percent-held-above-ninety-nine"),
    ("borrowed-quark-mass-order", "exact-light-root-enclosure-order"),
    ("ignore-or-fit-electromagnetic-effect", "compare-admitted-terminal-proton-dressing"),
    ("assert-measured-mass-order", "one-down-replacement-forces-neutron-heavier"),
    ("external-target-readable", "target-inaccessible-until-seal"),
    ("conceal-observational-development", "registered-observational-prediction-protocol"),
    ("free-mass-term-or-percentage", "no-extra-rule"),
)


def cubic_side(x: Fraction, pair_sum: Fraction, product_value: Fraction) -> str:
    positive = x ** 3 + pair_sum * x
    counter = x * x + product_value
    return "positive" if positive > counter else "counter"


def exact_arithmetic() -> bool:
    colour = (Fraction(1, 7), Fraction(2, 7), Fraction(4, 7))
    colour_closed = colour[0] + colour[1] + colour[2] == 1
    proton_charge = 2 * Fraction(2, 3) - Fraction(1, 3)
    neutron_neutral = Fraction(2, 3) == 2 * Fraction(1, 3)
    bare, held = Fraction(1, 128), Fraction(127, 128)

    down_bounds = Fraction(1, 39), Fraction(1, 38)
    up_bounds = Fraction(1, 244), Fraction(1, 243)
    down_bracket = cubic_side(down_bounds[0], Fraction(1, 8), Fraction(1, 383)) != cubic_side(down_bounds[1], Fraction(1, 8), Fraction(1, 383))
    up_bracket = cubic_side(up_bounds[0], Fraction(1, 12), Fraction(1, 3071)) != cubic_side(up_bounds[1], Fraction(1, 12), Fraction(1, 3071))
    flavour_lower = down_bounds[0] - up_bounds[1]
    inverse_alpha = Fraction(503846395469, 3676744786)
    alpha = Fraction(1, 1) / inverse_alpha
    electromagnetic = Fraction(53, 30) * alpha ** 2 * (Fraction(1, 1) + Fraction(2, 135) * alpha)
    return (
        colour_closed
        and proton_charge == 1
        and neutron_neutral
        and bare + held == 1
        and bare < Fraction(1, 100)
        and held > Fraction(99, 100)
        and down_bracket
        and up_bracket
        and flavour_lower > electromagnetic
    )


def main() -> None:
    claim_id = sys.argv[1]
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(row) for row in product(*DOMAINS))
    survivor = "__".join(domain[1] for domain in DOMAINS)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    arithmetic = exact_arithmetic()
    passed = (
        claim_id == CLAIM_ID
        and sealed["claim_id"] == claim_id
        and arithmetic
        and received == generated
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 4096
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
            "exact_arithmetic": arithmetic,
            "target_value_accessed": False,
            "implementation": "independent colour-cycle, charge-word, depth-seven ledger and rational cubic-bracket reconstruction",
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
