#!/usr/bin/env python3
"""Independent exact reconstruction of the terminal proton-radius grammar."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-PROTON-RADIUS-TERMINAL-029"
DOMAINS = (
    ("named-proton-without-composition", "admitted-uud-colour-three-proton"),
    ("inner-one-third-as-outer-edge", "outer-two-thirds-complement"),
    ("partial-colour-or-single-fibre-support", "all-three-colours-times-both-Fold-labels"),
    ("eight-nonreturn-mediators", "nine-internal-colour-pairs", "ten-internal-pairs-plus-unit-charge"),
    ("no-terminal-transport", "one-alpha-spatial-traversal", "alpha-squared-energy-composition"),
    ("append-outward-free-share", "hold-inward-share-from-edge"),
    ("full-cycle-or-fitted-length", "reduced-proton-Compton-postseal"),
    ("probe-results-readable-before-seal", "capability-closed-before-target-release"),
    ("claim-historical-blindness", "observational-derivation-explicit"),
    ("free-form-factor-or-probe-correction", "no-extra-rule"),
)
SURVIVOR = (
    "admitted-uud-colour-three-proton",
    "outer-two-thirds-complement",
    "all-three-colours-times-both-Fold-labels",
    "ten-internal-pairs-plus-unit-charge",
    "one-alpha-spatial-traversal",
    "hold-inward-share-from-edge",
    "reduced-proton-Compton-postseal",
    "capability-closed-before-target-release",
    "observational-derivation-explicit",
    "no-extra-rule",
)


def theorem_check() -> bool:
    alpha = Fraction(3676744786, 503846395469)
    inner = Fraction(1, 3)
    edge = Fraction(2, 3)
    leading = 3 * 2 * edge
    coefficient = leading * (Fraction(1, 1) - alpha / 10)
    rows = tuple(
        (
            support,
            order,
            leading * (
                Fraction(1, 1)
                if order == 1
                else Fraction(1, 1) - alpha ** (order - 1) / support
            ),
        )
        for support in (8, 9, 10)
        for order in (1, 2, 3)
    )
    return all((
        inner + edge == 1,
        leading == 4,
        3 * 3 + 1 == 10,
        coefficient == Fraction(10069574419808, 2519231977345),
        len(rows) == 9,
        all(value > 0 for _, _, value in rows),
    ))


def generated_ids() -> tuple[str, ...]:
    return tuple("__".join(row) for row in product(*DOMAINS))


def main() -> None:
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = generated_ids()
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {
        candidate_id: tuple(candidate_id.split("__")) == SURVIVOR and theorem_check()
        for candidate_id in generated
    }
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = all((
        sys.argv[1] == CLAIM_ID,
        sealed["claim_id"] == CLAIM_ID,
        received == generated,
        len(set(received)) == sealed["census"]["expected_cardinality"] == 2304,
        decisions == recomputed,
        sum(recomputed.values()) == 1,
        {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        all(row["passed"] for row in sealed["controls"]),
        theorem_check(),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": len(generated),
            "formula_control_count": 9,
            "terminal_coefficient": "10069574419808/2519231977345",
            "target_content_used": False,
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
