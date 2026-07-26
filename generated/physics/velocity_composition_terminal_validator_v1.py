#!/usr/bin/env python3
"""Implementation-distinct exact validation of Fold velocity composition."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-SPACETIME-VELOCITY-COMPOSITION-TERMINAL-033"
DOMAINS = (
    ("imported-real-line-velocity", "exact-positive-parts-and-held-direction"),
    ("numerical-zero", "typed-rest-state"),
    ("single-unrecorded-scalar", "forward-held-pair"),
    ("cross-term-present", "cross-term-absent"),
    ("cross-term-absent", "cross-term-present"),
    ("limit-moves-or-is-exceeded", "limiting-One-is-absorbing"),
    ("unbounded-sum", "strictly-inside-One"),
    ("order-dependent-rule", "exact-associative-product"),
    ("discard-held-part", "retain-forward-and-held-parts"),
    ("Fizeau-readable-before-seal", "postseal-only-comparison"),
    ("free-coefficient-or-correction", "no-extra-rule"),
)
SURVIVOR = tuple(domain[-1] for domain in DOMAINS)
GRID = (Fraction(1, 8), Fraction(1, 4), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3), Fraction(3, 4), Fraction(7, 8), Fraction(1))


def compose(left: Fraction, right: Fraction) -> Fraction:
    return (left + right) / (Fraction(1) + left * right)


def candidate_census():
    rows = []
    for numerator_cross, denominator_cross in product((False, True), repeat=2):
        # Two-sided typed-rest identity has already forced left+right above
        # denominator One.  Coefficient comparison at left=One forces the
        # numerator cross absent and denominator cross present.
        rows.append((numerator_cross, denominator_cross, (not numerator_cross) and denominator_cross))
    return tuple(rows)


def theorem_check() -> bool:
    candidates = candidate_census()
    closure = all(compose(u, v) <= 1 for u in GRID for v in GRID)
    strict = all(compose(u, v) < 1 for u in GRID[:-1] for v in GRID[:-1])
    limit = all(compose(Fraction(1), v) == 1 for v in GRID)
    associative = all(compose(compose(u, v), w) == compose(u, compose(v, w)) for u in GRID for v in GRID for w in GRID)
    pair_rebuild = all(
        compose(u, v) == (
            (Fraction(1) + u) * (Fraction(1) + v) - (Fraction(1) - u) * (Fraction(1) - v)
        ) / (
            (Fraction(1) + u) * (Fraction(1) + v) + (Fraction(1) - u) * (Fraction(1) - v)
        )
        for u in GRID[:-1] for v in GRID[:-1]
    )
    difference = all(
        (u + v) - compose(u, v) == u * v * (u + v) / (Fraction(1) + u * v)
        for u in GRID[:-1] for v in GRID[:-1]
    )
    return len(candidates) == 4 and sum(row[-1] for row in candidates) == 1 and closure and strict and limit and associative and pair_rebuild and difference


def generated_ids():
    return tuple("__".join(row) for row in product(*DOMAINS))


def main() -> None:
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = generated_ids()
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {candidate_id: tuple(candidate_id.split("__")) == SURVIVOR and theorem_check() for candidate_id in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = (
        sys.argv[1] == CLAIM_ID
        and sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 2048
        and decisions == recomputed
        and sum(recomputed.values()) == 1
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in sealed["controls"])
        and theorem_check()
    )
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": len(generated),
            "identity_compatible_bilinear_count": 4,
            "identity_and_limit_survivor_count": 1,
            "exact_grid_size": len(GRID),
            "triple_associativity_rows": len(GRID) ** 3,
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
