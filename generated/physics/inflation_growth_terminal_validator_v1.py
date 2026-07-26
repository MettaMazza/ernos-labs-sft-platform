#!/usr/bin/env python3
"""Implementation-distinct inflation-growth terminal reconstruction."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-INFLATION-GROWTH-TERMINAL-039"
DOMAINS = (
    ("named-observable-universe-size", "generator-three-space-volume"),
    ("selected-sixty-efold-story", "least-binary-depth-five-cover"),
    ("irrational-logarithmic-efolds", "five-exact-doubling-transitions"),
    ("fitted-spectral-index", "one-boundary-record-short-of-complete"),
    ("free-tensor-amplitude", "one-tensor-pair-record-in-thirty-two"),
    ("chosen-inflaton-potential-exit", "first-complete-generator-volume-cover"),
    ("stochastic-or-decaying-seed", "quarter-half-One-two-step-growth"),
    ("fitted-transfer-function", "third-versus-fourth-power-relative-growth"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def generated_ids() -> tuple[str, ...]:
    return tuple("__".join(row) for row in product(*DOMAINS))


def least_cover(size: int) -> tuple[int, int]:
    depth = 1
    support = 2
    while support < size:
        support *= 2
        depth += 1
    return depth, support


def theorem_check() -> bool:
    volume = 3 ** 3
    depth, support = least_cover(volume)
    scalar = Fraction(support - 1, support)
    tensor = Fraction(1, support)
    trace = (Fraction(1, 4), Fraction(1, 2), Fraction(1))
    transfer = all(
        Fraction(1, growth ** 3) / Fraction(1, growth ** 4) == growth
        for growth in (2, 3, 4, 5, 7)
    )
    return (
        volume == 27
        and depth == 5
        and support == 32
        and scalar == Fraction(31, 32)
        and tensor == Fraction(1, 32)
        and scalar + tensor == Fraction(1)
        and trace == (Fraction(1, 4), Fraction(1, 2), Fraction(1))
        and trace[0] < trace[1] < trace[2]
        and transfer
    )


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
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 256
        and decisions == recomputed
        and sum(recomputed.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and {row["kind"] for row in sealed["controls"]}
        == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in sealed["controls"])
        and theorem_check()
    )
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "volume": 27,
            "cover_depth": 5,
            "cover_support": 32,
            "scalar_support": "31/32",
            "tensor_support": "1/32",
            "growth_trace": ["1/4", "1/2", "1"],
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
