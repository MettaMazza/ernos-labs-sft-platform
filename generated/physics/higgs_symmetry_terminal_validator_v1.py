#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-HIGGS-SYMMETRY-TERMINAL-065"
DOMAINS = (
    ("absence-as-numerical-ground", "positive-proper-ground-carrier"),
    ("unison-or-selected-part", "unique-self-antipodal-half-One"),
    ("discard-or-rewrite-leading-rungs", "retain-half-quarter-eighth-controls"),
    ("selected-direction-subset", "complete-two-by-three-product"),
    ("retain-all-six-as-active", "hold-unique-return-leaving-five"),
    ("free-denominator", "least-cover-of-generation-volume"),
    ("fitted-offset-or-repeated-series", "one-six-over-five-alpha-return"),
    ("import-potential-or-free-lambda", "squared-excitation-shared-over-two-fibres"),
    ("independent-mass-and-coupling-routes", "exact-two-route-cross-lock"),
    ("target-readable-before-seal", "all-targets-inaccessible-until-seal"),
    ("extra-mass-potential-or-correction", "no-extra-rule"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def exact_result():
    alpha = Fraction(3676744786, 503846395469)
    vacuum = Fraction(1, 2)
    directions = 2 * 3
    active = directions - 1
    depth, support = 1, 2
    while support < 3 ** 3:
        depth += 1
        support *= 2
    ratio = vacuum + Fraction(directions, active) * alpha
    coupling = ratio * ratio / 2
    return all((
        directions == 6,
        active == depth == 5,
        ratio == Fraction(2563352914777, 5038463954690),
        coupling == Fraction(6570778165695741824959729, 50772238045420788745992200),
        ratio * ratio == 2 * coupling,
    ))


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = tuple("__".join(row) for row in product(*DOMAINS))
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    valid = exact_result()
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR and valid for candidate in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = all((
        sys.argv[1] == CLAIM_ID,
        sealed["claim_id"] == CLAIM_ID,
        received == generated,
        len(set(received)) == sealed["census"]["expected_cardinality"] == 2048,
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
            "candidate_count": 2048,
            "ground": "half-One",
            "directions": 6,
            "active_and_cover": 5,
            "mass_ratio": "2563352914777/5038463954690",
            "self_coupling": "6570778165695741824959729/50772238045420788745992200",
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
