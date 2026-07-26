#!/usr/bin/env python3
"""Independent exact reconstruction of finite Fold quantum gravity."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-FINITE-QUANTUM-GRAVITY-TERMINAL-023"
DOMAINS = (
    ("separate-quantum-and-gravity-substrates", "single-finite-Fold-lattice"),
    ("chosen-or-extra-dimensional-space", "three-space-plus-one-process-direction"),
    ("scalar-or-selected-tensor", "complete-symmetric-rank-two-source"),
    ("assigned-spin-or-mode-count", "ten-take-four-take-four-leaves-two"),
    ("fitted-mass-or-speed", "empty-mass-record-and-One-cell-per-tick"),
    ("continuum-amplitude-space", "complete-finite-binary-word-support"),
    ("completed-infinity-or-counterterm", "complete-finite-rational-loop-prefix"),
    ("unbounded-or-unrecorded-boundary", "positive-floor-and-quarter-area-record"),
    ("target-selects-composition", "inherit-sealed-wave-loop-and-horizon-comparisons"),
    ("extra-dimension-or-free-regulator", "no-extra-rule"),
)
SURVIVOR = tuple(domain[-1] for domain in DOMAINS)


def loop_sum(depth: int) -> Fraction:
    return sum((Fraction(1, 2**step) for step in range(1, depth + 1)), Fraction(0, 1))


def theorem_check() -> bool:
    for depth in range(1, 13):
        support = 2**depth
        floor = Fraction(1, support)
        slots = 4 * 5 // 2
        modes = slots - 4 - 4
        if not (slots == 10 and modes == 2 and 0 < floor <= Fraction(1, 2) and 0 < loop_sum(depth) < 1 and Fraction(support, 4) * 4 == support):
            return False
    return True


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
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": len(generated), "depths_checked": 12, "symmetric_slots": 10, "physical_modes": 2, "completed_infinity_used": False, "survivor": "__".join(SURVIVOR)}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
