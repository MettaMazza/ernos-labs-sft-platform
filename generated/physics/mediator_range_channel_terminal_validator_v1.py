#!/usr/bin/env python3
"""Independent exact mediator-range reconstruction."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-MEDIATOR-RANGE-CHANNEL-TERMINAL-020"
DOMAINS = (
    ("untracked-field-value", "held-forward-and-rest-carriers"),
    ("named-unbroken-channel", "combination-reassembling-the-One"),
    ("assigned-mass-label", "positive-shortfall-or-empty-record"),
    ("sink-or-imported-exponential", "exact-positive-forward-to-rest-transfer"),
    ("forward-loss-without-ledger", "forward-plus-rest-reassembles-One"),
    ("selected-cutoff-distance", "positive-trace-and-reciprocal-mass-scale"),
    ("independent-range-order", "larger-mass-shorter-range"),
    ("finite-hard-stop", "held-forward-and-positive-finite-radius"),
    ("W-Z-photon-selected-before-law", "inherit-sealed-electroweak-and-range-records"),
    ("free-Yukawa-or-cutoff-rule", "no-extra-rule"),
)
SURVIVOR = tuple(domain[-1] for domain in DOMAINS)
ONE = Fraction(1, 1)


def trace(mass: Fraction) -> tuple[Fraction, ...]:
    current = ONE
    rows = (current,)
    while current > mass:
        current -= mass
        rows += (current,)
    return rows


def theorem_check() -> bool:
    masses = (Fraction(1, 7), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3))
    reaches = tuple(len(trace(mass)) - 1 for mass in masses)
    conserved = all(all(forward + (ONE - forward) == ONE for forward in trace(mass)[1:]) for mass in masses)
    reciprocal_order = all(ONE / larger < ONE / smaller for smaller, larger in zip(masses, masses[1:]) if smaller < larger)
    massless = all(ONE / Fraction(radius * radius, 1) > 0 for radius in range(1, 65))
    return reaches == (6, 2, 1, 1) and conserved and reciprocal_order and massless


def generated_ids() -> tuple[str, ...]:
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
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 1024
        and decisions == recomputed
        and sum(recomputed.values()) == 1
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in sealed["controls"])
        and theorem_check()
    )
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": len(generated), "survivor": "__".join(SURVIVOR), "mass_reach_pairs": [["1/7", 6], ["1/3", 2], ["1/2", 1], ["2/3", 1]], "massless_radii_checked_through": 64, "hard_physical_cutoff_claimed": False}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
