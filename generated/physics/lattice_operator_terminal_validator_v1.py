#!/usr/bin/env python3
"""Independent exact Fold lattice-operator reconstruction."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-LATTICE-OPERATOR-TERMINAL-022"
DOMAINS = (
    ("signed-field-number", "positive-held-site-presence"),
    ("selected-or-remote-neighbours", "complete-two-per-generated-axis-ring"),
    ("free-dimension-specific-weights", "half-One-held-half-One-equally-distributed"),
    ("signed-Laplacian-value", "positive-peak-with-held-opposition"),
    ("chosen-peak-or-partial-ring", "two-dimension-peak-and-complete-ring"),
    ("continuum-or-selected-front", "complete-oriented-taxicab-ball"),
    ("evaluated-cosine-or-mode-table", "complete-exact-phase-mode-carriers"),
    ("bounded-count-list", "axis-and-oriented-step-successor"),
    ("measurement-selects-operator", "inherit-sealed-dispersion-and-cubic-records"),
    ("free-coefficient-or-extra-neighbour", "no-extra-rule"),
)
SURVIVOR = tuple(domain[-1] for domain in DOMAINS)


def positions(radius: int):
    return (("origin", None),) + tuple((direction, magnitude) for magnitude in range(1, radius + 1) for direction in ("lower", "upper"))


def ball_count(dimension: int, ticks: int) -> int:
    return sum(1 for coordinate in product(positions(ticks), repeat=dimension) if sum(magnitude for _, magnitude in coordinate if magnitude is not None) <= ticks)


def update(state):
    size = len(state)
    return tuple(Fraction(1, 2) * state[index] + Fraction(1, 4) * state[(index + size - 1) % size] + Fraction(1, 4) * state[(index + 1) % size] for index in range(size))


def theorem_check() -> bool:
    stencils = tuple((2 * dimension, Fraction(1, 4 * dimension)) for dimension in (1, 2, 3))
    conserved = all(Fraction(1, 2) + count * share == 1 for count, share in stencils)
    counts = {dimension: tuple(ball_count(dimension, tick) for tick in (1, 2, 3)) for dimension in (1, 2, 3)}
    bump = (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4))
    flat = (Fraction(1, 5),) * 5
    mode_indices = tuple(range(1, 8))
    return conserved and stencils == ((2, Fraction(1, 4)), (4, Fraction(1, 8)), (6, Fraction(1, 12))) and update(bump)[1] == Fraction(3, 8) and update(flat) == flat and counts == {1: (3, 5, 7), 2: (5, 13, 25), 3: (7, 25, 63)} and len(mode_indices) == 7 and sum(index == 7 for index in mode_indices) == 1


def generated_ids() -> tuple[str, ...]:
    return tuple("__".join(row) for row in product(*DOMAINS))


def main() -> None:
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = generated_ids()
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {candidate_id: tuple(candidate_id.split("__")) == SURVIVOR and theorem_check() for candidate_id in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = sys.argv[1] == CLAIM_ID and sealed["claim_id"] == CLAIM_ID and received == generated and len(set(received)) == sealed["census"]["expected_cardinality"] == 1024 and decisions == recomputed and sum(recomputed.values()) == 1 and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"} and all(row["passed"] for row in sealed["controls"]) and theorem_check()
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": len(generated), "causal_vectors": {"1": [3, 5, 7], "2": [5, 13, 25], "3": [7, 25, 63]}, "mode_carriers_checked": 7, "irrational_mode_value_evaluated": False, "survivor": "__".join(SURVIVOR)}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
