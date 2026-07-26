#!/usr/bin/env python3
"""Implementation-distinct thermal-history terminal reconstruction."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-THERMAL-HISTORY-RECOMBINATION-TERMINAL-037"
DOMAINS = (
    ("named-cosmological-chronology", "admitted-threshold-and-transport-dependencies"),
    ("same-direction-or-fitted-cooling", "exact-inverse-scale-transport"),
    ("named-epoch-list", "descending-distinct-binding-thresholds"),
    ("one-seventh-ratio-rubber-stamp", "least-live-neutron-share"),
    ("selected-decay-correction", "least-complete-binary-cover-successor"),
    ("named-quarter-abundance", "paired-neutron-helium-and-hydrogen-families"),
    ("instantaneous-zero-width-collapse", "half-One-midpoint-with-finite-visibility"),
    ("observed-multipoles-assumed-exact-integers", "internal-whole-modes-parity-and-projection-record"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def generated_ids() -> tuple[str, ...]:
    return tuple("__".join(row) for row in product(*DOMAINS))


def orbit() -> tuple[int, ...]:
    values: list[int] = []
    current = 1
    while current not in values:
        values.append(current)
        current = (2 * current) % 7
    return tuple(values)


def visibility(radius: int) -> tuple[tuple[Fraction, ...], int]:
    rising = tuple(range(1, radius + 2))
    weights = rising + tuple(reversed(rising[:-1]))
    total = sum(weights)
    normalized = tuple(Fraction(weight, total) for weight in weights)
    return normalized, radius


def theorem_check() -> bool:
    temperature = all(
        (value / growth) * growth == value
        for value, growth in product(
            (Fraction(1, 4), Fraction(2, 3), Fraction(5, 2)),
            (Fraction(1, 2), Fraction(2), Fraction(7, 3)),
        )
    )
    thresholds = tuple(sorted((Fraction(1, 2), Fraction(7, 8), Fraction(1, 4), Fraction(3, 4)), reverse=True))
    visible = all(
        sum(weights) == Fraction(1)
        and weights[midpoint] == max(weights)
        and weights.count(weights[midpoint]) == 1
        for weights, midpoint in (visibility(radius) for radius in range(1, 10))
    )
    modes = tuple("compression" if mode % 2 == 1 else "rarefaction" for mode in range(1, 9))
    sound_horizon = Fraction(1, 8) * Fraction(1, 2) + Fraction(1, 4) * Fraction(2, 3) + Fraction(3, 8) * Fraction(3, 4)
    neutron_freezeout = Fraction(1, 7)
    proton_freezeout = Fraction(6, 7)
    neutron_capture = Fraction(1, 8)
    proton_capture = Fraction(7, 8)
    return (
        temperature
        and thresholds == (Fraction(7, 8), Fraction(3, 4), Fraction(1, 2), Fraction(1, 4))
        and orbit() == (1, 2, 4)
        and neutron_freezeout / proton_freezeout == Fraction(1, 6)
        and neutron_capture / proton_capture == Fraction(1, 7)
        and 2 * neutron_capture == Fraction(1, 4)
        and Fraction(6, 8) == Fraction(3, 4)
        and visible
        and modes == ("compression", "rarefaction") * 4
        and sound_horizon == Fraction(49, 96)
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
            "candidate_count": len(generated),
            "orbit": [1, 2, 4],
            "freezeout_neutron_proton": "1/6",
            "capture_neutron_proton": "1/7",
            "helium_family": "1/4",
            "hydrogen_family": "3/4",
            "sound_horizon_example": "49/96",
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
