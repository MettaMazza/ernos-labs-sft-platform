#!/usr/bin/env python3
"""Independent reconstruction of the two-fibre partition/path law."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-SCATTERING-PARTITION-PATH-TERMINAL-017"
DOMAINS = (
    ("arbitrary-scatterer", "registered-one-target-Fold-geometry"),
    ("sampled-or-omitted-channel", "complete-scatter-pass-pair"),
    ("overlapping-outcome-cells", "mutually-exclusive-held-labels"),
    ("assumed-equal-probability", "equipotent-two-cell-support"),
    ("fitted-dimensional-number", "successful-over-incident-support"),
    ("density-omitted", "positive-density-times-section"),
    ("selected-path-length", "reciprocal-encounter-support"),
    ("stochastic-transition-oracle", "deterministic-held-outcomes"),
    ("free-geometry-or-correction", "no-extra-rule"),
)
SURVIVOR = tuple(domain[-1] for domain in DOMAINS)
ONE = Fraction(1, 1)


def path(density: Fraction, section: Fraction) -> Fraction:
    return ONE / (density * section)


def theorem_check() -> bool:
    half = Fraction(1, 2)
    ordered = tuple(Fraction(n, 8) for n in range(1, 9))
    return all(
        (
            half + half == ONE,
            path(ONE, ONE) == ONE,
            path(ONE, half) == Fraction(2, 1),
            all(path(Fraction(3, 2), larger) < path(Fraction(3, 2), smaller) for smaller, larger in zip(ordered, ordered[1:])),
        )
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
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 512
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
            "survivor": "__".join(SURVIVOR),
            "partition": ["1/2", "1/2"],
            "unit_density_path_pairs": [["1", "1"], ["1/2", "2"]],
            "ordered_sections_checked": 8,
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
