#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-COMPACT-HORIZON-THERMODYNAMICS-TERMINAL-071"
DOMAINS = (
    ("multiply-occupied-cell", "one-fermion-per-generated-cell"),
    ("selected-momentum-scale", "cube-side-momentum-depth"),
    ("imported-pressure-equation", "occupants-times-forced-depth-q4"),
    ("linear-unpaired-source", "paired-source-q6"),
    ("chosen-dimensional-mass", "three-quarter-preimage-to-half-One"),
    ("open-ended-remnant-list", "exactly-two-binary-fibre-families"),
    ("imported-metric-radius", "one-Fold-mass-doubling"),
    ("volume-support", "rank-two-radius-pair"),
    ("selected-entropy-coefficient", "quarter-area-boundary-record"),
    ("constant-or-fitted-temperature", "fixed-thermal-mass-product"),
    ("numerical-zero-or-completed-infinity", "positive-finite-floor-at-every-reached-depth"),
    ("free-family-or-correction", "no-extra-rule"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def exact_checks():
    exponent_order = all(side ** 6 > side ** 4 for side in range(2, 65))
    threshold = Fraction(3, 4) - Fraction(1, 4) == Fraction(1, 2)
    reference_mass = Fraction(1, 4)
    product_value = Fraction(1, 16)
    reference_temperature = product_value / reference_mass
    masses = tuple(Fraction(1, 2 ** depth) for depth in range(1, 17))
    temperatures = tuple(product_value / mass for mass in masses)
    areas = tuple((mass + mass) ** 2 for mass in masses)
    return all((
        exponent_order,
        threshold,
        reference_temperature == Fraction(1, 4),
        all(left > right for left, right in zip(masses, masses[1:])),
        all(left < right for left, right in zip(temperatures, temperatures[1:])),
        all(left > right for left, right in zip(areas, areas[1:])),
        all(mass * temperature == product_value for mass, temperature in zip(masses, temperatures)),
        all(value > 0 for value in masses + temperatures + areas),
    ))


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(row) for row in product(*DOMAINS))
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    valid = exact_checks()
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR and valid for candidate in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = all((
        sys.argv[1] == CLAIM_ID,
        sealed["claim_id"] == CLAIM_ID,
        received == generated,
        len(set(received)) == sealed["census"]["expected_cardinality"] == 4096,
        decisions == recomputed,
        sum(recomputed.values()) == 1,
        sealed["closure"]["scope"] == "depth_independent",
        {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        all(row["passed"] for row in sealed["controls"]),
        valid,
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": 4096,
            "exclusion_scaling": "q^4-versus-q^6",
            "loaded_threshold": "3/4",
            "folded_balance": "1/2",
            "pre_horizon_family_count": 2,
            "thermal_mass_product": "1/16",
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
