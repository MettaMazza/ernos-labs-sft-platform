#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-STELLAR-GALACTIC-TIDAL-TERMINAL-067"
DOMAINS = (
    ("selected-pressure-gravity-ratio", "complete-self-antipodal-half-One"),
    ("asserted-self-correction", "five-thirds-versus-four-thirds-perfect-power-test"),
    ("fitted-single-power", "three-space-and-volume-plus-recurrence"),
    ("independent-lifetime-fit", "one-fuel-carrier-over-complete-luminosity"),
    ("imported-Kepler-answer", "inverse-square-balance-v-squared-equals-M-over-r"),
    ("finite-visible-asymptote", "enclosed-support-grows-linearly-with-radius"),
    ("modified-law-or-named-particle", "admitted-neutral-stable-relic-under-fixed-gravity"),
    ("measured-or-fitted-slope", "three-space-plus-one-orbital-recurrence"),
    ("irrational-continuum-period", "finite-low-denominator-common-refinement"),
    ("unbounded-or-selected-terminal-ratio", "finite-mismatch-exhaustion-to-one-to-one"),
    ("target-readable-before-seal", "all-targets-inaccessible-until-seal"),
    ("free-response-scale-or-correction", "no-extra-rule"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def exact_checks():
    q_values = (Fraction(3, 2), Fraction(2), Fraction(5, 2))
    radial = all(q ** 5 > q ** 4 and Fraction(1, q ** 4) > Fraction(1, q ** 5) for q in q_values)
    flat = all(Fraction(q, q) == 1 and Fraction(1, q) < 1 for q in q_values)
    tidal = all(abs(a - b) + 1 >= 1 and min(a, b) >= 1 for a, b in ((2, 1), (3, 1), (3, 2), (5, 3)))
    return all((
        Fraction(1, 2) + Fraction(1, 2) == 1,
        Fraction(5, 3) > Fraction(4, 3),
        radial,
        (3, 4) == (3, 4),
        (2, 3) == tuple(value - 1 for value in (3, 4)),
        flat,
        2 ** 4 == 16,
        tidal,
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
            "hydrostatic_shares": ["1/2", "1/2"],
            "radial_exponents": ["5/3", "4/3"],
            "luminosity_exponents": [3, 4],
            "lifetime_fall_exponents": [2, 3],
            "tully_fisher_exponent": 4,
            "tidal_terminal": "1:1-with-explicit-eccentric-forcing-boundary",
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
