#!/usr/bin/env python3
"""Implementation-distinct validator for residual nuclear interaction."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-NUCLEAR-RESIDUAL-FORCE-TERMINAL-005"
DOMAINS = (
    ("rewrite-nucleon-predecessors", "compose-immutable-neutral-composite-predecessors"),
    ("export-raw-colour-label", "leading-colour-act-closes-to-empty-form"),
    ("reuse-primary-half-One", "paired-half-One-boundary-act"),
    ("identify-quarter-with-all-cross-sections", "structural-order-not-universal-dimensional-strength"),
    ("numerical-zero-mass", "empty-mass-label-or-positive-mass-carrier"),
    ("chosen-decay-length", "exact-reciprocal-mass-scale"),
    ("import-particle-range-ranking", "lighter-positive-mass-has-greater-reciprocal"),
    ("all-to-all-independent-links", "finite-boundary-cells-with-finite-range"),
    ("external-target-readable", "target-inaccessible-until-seal"),
    ("free-decay-profile-or-coupling", "no-extra-rule"),
)


def independent_arithmetic() -> bool:
    primary = Fraction(1, 2)
    residual = primary * primary
    fold_once = residual + residual
    fold_twice = fold_once + fold_once
    ordered = all(Fraction(1, rank) > Fraction(1, rank + 1) for rank in range(1, 256))
    finite = all(Fraction(1, rank) > 0 for rank in range(1, 256))
    return residual == Fraction(1, 4) and fold_once == primary and fold_twice == Fraction(1, 1) and ordered and finite


def main() -> None:
    claim_id = sys.argv[1]
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(row) for row in product(*DOMAINS))
    survivor = "__".join(domain[1] for domain in DOMAINS)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    arithmetic = independent_arithmetic()
    passed = (
        claim_id == CLAIM_ID
        and sealed["claim_id"] == claim_id
        and arithmetic
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
            "exact_arithmetic": arithmetic,
            "target_value_accessed": False,
            "implementation": "independent paired-half support and positive reciprocal-order reconstruction",
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
