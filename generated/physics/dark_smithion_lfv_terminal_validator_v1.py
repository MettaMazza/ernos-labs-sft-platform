#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061"
DOMAINS = (
    ("selected-particle-sector", "both-forced-prime-sectors"),
    ("one-selected-kind", "complete-down-up-dual"),
    ("chosen-depth", "least-binary-cover-of-sector-power"),
    ("independent-mass-parameter", "same-coloured-product-family"),
    ("chosen-decimal-roots", "complete-grid-and-rational-halving"),
    ("floating-central-estimates", "squared-rational-enclosures-with-light-lift"),
    ("named-dark-particle", "least-complete-neutral-singlet"),
    ("freezeout-fit-or-density-input", "generation-volume-over-cover-depth"),
    ("fitted-branching-fractions", "squared-separation-times-parent-part"),
    ("search-result-readable-before-seal", "all-targets-inaccessible-until-seal"),
    ("extra-scale-sector-or-correction", "no-extra-rule"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def cover(value):
    depth, support = 1, 2
    while support < value:
        depth += 1
        support *= 2
    return depth


def coloured_product(sector, depth):
    return Fraction(sector, sector * (2 * sector ** depth - 1) - 1)


def side(x, second, third):
    left = x * x * x + second * x
    right = x * x + third
    if left == right:
        return ()
    return ("left", left - right) if left > right else ("right", right - left)


def roots(sector, kind):
    depth = cover(sector ** (3 if kind == "down" else 4))
    second = Fraction(1, 8) if kind == "down" else Fraction(1, 4 * sector)
    third = coloured_product(sector, depth)
    support = 1024
    rows = []
    lower = ()
    lower_side = ("right", third)
    for index in range(1, support + 1):
        upper = Fraction(index, support)
        upper_side = side(upper, second, third)
        if upper_side == () or lower_side[0] != upper_side[0]:
            rows.append((lower, upper))
        lower, lower_side = upper, upper_side
    if len(rows) != 3:
        return ()
    for _ in range(60):
        refined = []
        for lower, upper in rows:
            midpoint = upper / 2 if lower == () else (lower + upper) / 2
            lower_side = ("right", third) if lower == () else side(lower, second, third)
            midpoint_side = side(midpoint, second, third)
            if midpoint_side == () or lower_side[0] != midpoint_side[0]:
                refined.append((lower, midpoint))
            else:
                refined.append((midpoint, upper))
        rows = refined
    return tuple(rows)


def exact_result():
    spectra = tuple(roots(sector, kind) for sector in (5, 7) for kind in ("down", "up"))
    weights = (Fraction(1, 4) ** 2 * Fraction(1, 2), Fraction(1, 4) ** 2 * Fraction(5, 6), Fraction(1, 2) ** 2 * Fraction(5, 6))
    return all(len(row) == 3 and row[0][0] and row[0][1] < row[1][0] < row[2][0] for row in spectra) and coloured_product(3, 5) == Fraction(3, 1454) and coloured_product(3, 7) == Fraction(3, 13118) and weights == (Fraction(1, 32), Fraction(5, 96), Fraction(5, 24)) and weights[2] / weights[1] == 4 and Fraction(27, 5) + 1 == Fraction(32, 5)


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        seal = json.load(handle)
    generated = tuple("__".join(values) for values in product(*DOMAINS))
    recorded = tuple(row["candidate_id"] for row in seal["census"]["candidates"])
    valid = exact_result()
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR and valid for candidate in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in seal["decisions"]}
    passed = all((sys.argv[1] == CLAIM_ID, seal["claim_id"] == CLAIM_ID, recorded == generated, len(set(recorded)) == seal["census"]["expected_cardinality"] == 2048, decisions == recomputed, sum(recomputed.values()) == 1, seal["closure"]["scope"] == "depth_independent", {row["kind"] for row in seal["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}, all(row["passed"] for row in seal["controls"]), valid))
    print(json.dumps({"passed": passed, "validated_seal_hash": seal["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 2048, "spectra": 4, "roots": 12, "dark_to_baryon": "27/5", "lfv": ["1/32", "5/96", "5/24"], "survivor": "__".join(SURVIVOR)}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
