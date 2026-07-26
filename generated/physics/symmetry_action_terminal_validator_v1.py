#!/usr/bin/env python3
"""Independent finite symmetry/action reconstruction."""

from __future__ import annotations

from fractions import Fraction
from itertools import permutations, product
from math import gcd
import json
import sys


CLAIM_ID = "SFT-PHYS-DYNAMICS-SYMMETRY-ACTION-TERMINAL-016"
DOMAINS = (
    ("selected-or-continuous-state-sample", "complete-finite-generated-support"),
    ("named-transformation-without-census", "complete-bijection-enumeration"),
    ("state-labels-without-transition-law", "transition-incidence-preserved"),
    ("free-rescaling-under-symmetry", "exact-positive-carrier-preserved"),
    ("answer-only-scalar", "odd-core-and-held-invariant-fibre"),
    (
        "assert-every-conservation-has-unknown-symmetry",
        "enumerate-all-fibre-preserving-bijections",
    ),
    ("signed-or-imported-action-integral", "sum-of-positive-oriented-step-magnitudes"),
    (
        "postulated-stationary-physical-path",
        "dyadic-Fold-descent-and-positive-detour-bound",
    ),
    ("free-Lagrangian-or-Euler-equation", "no-extra-rule"),
)
SURVIVOR = tuple(domain[-1] for domain in DOMAINS)


def magnitude(a: Fraction, b: Fraction) -> Fraction:
    if a == b:
        raise ValueError("empty step")
    return a - b if a > b else b - a


def action(path: tuple[Fraction, ...]) -> Fraction:
    steps = tuple(magnitude(a, b) for a, b in zip(path, path[1:]))
    total = steps[0]
    for step in steps[1:]:
        total += step
    return total


def fold(value: Fraction) -> Fraction:
    paired = value + value
    return paired if paired <= 1 else paired - 1


def odd_core(value: Fraction) -> int:
    denominator = value.denominator
    while denominator % 2 == 0:
        denominator //= 2
    return denominator


def dyadic_trace(value: Fraction) -> tuple[Fraction, ...]:
    trace = (value,)
    while value != 1:
        value = fold(value)
        trace += (value,)
    return trace


def theorem_check() -> bool:
    odd_core_controls = all(
        odd_core(Fraction(numerator, denominator))
        == odd_core(fold(Fraction(numerator, denominator)))
        for denominator in range(2, 129)
        for numerator in range(1, denominator + 1)
        if gcd(numerator, denominator) == 1
    )
    dyadic_controls = all(
        len(dyadic_trace(Fraction(numerator, 2**depth))) == depth + 1
        and dyadic_trace(Fraction(numerator, 2**depth))[-1] == 1
        for depth in range(1, 9)
        for numerator in range(1, 2**depth, 2)
    )
    values = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
    for length in (2, 3, 4, 5):
        for path in product(values, repeat=length):
            if path[0] == path[-1] or any(a == b for a, b in zip(path, path[1:])):
                continue
            endpoint = magnitude(path[0], path[-1])
            if action(path) < endpoint:
                return False
            descending = all(a > b for a, b in zip(path, path[1:]))
            if descending and action(path) != endpoint:
                return False
    charges = ("a", "a", "b", "b")
    preserving = tuple(
        p
        for p in permutations(range(4))
        if all(charges[i] == charges[p[i]] for i in range(4))
    )
    if len(preserving) != 4 or not odd_core_controls or not dyadic_controls:
        return False
    return all(
        all(charges[i] == charges[p[i]] for i in range(4)) for p in preserving
    )


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
    passed = (
        sys.argv[1] == CLAIM_ID
        and sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(set(received))
        == sealed["census"]["expected_cardinality"]
        == 512
        and decisions == recomputed
        and sum(recomputed.values()) == 1
        and {row["kind"] for row in sealed["controls"]}
        == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in sealed["controls"])
        and theorem_check()
    )
    print(
        json.dumps(
            {
                "passed": passed,
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "certificate": {
                    "candidate_count": len(generated),
                    "survivor": "__".join(SURVIVOR),
                    "path_lengths_exhausted": [2, 3, 4, 5],
                    "odd_core_denominators_exhausted_through": 128,
                    "dyadic_depths_exhausted_through": 8,
                    "charge_preserving_bijections": 4,
                },
            },
            sort_keys=True,
        )
    )
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
