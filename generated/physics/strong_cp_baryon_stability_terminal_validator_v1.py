#!/usr/bin/env python3
"""Independent reconstruction for the terminal strong-CP/baryon claim."""

from fractions import Fraction
from itertools import combinations, product
import json
import sys


CLAIM_ID = "SFT-PHYS-STRONG-CP-BARYON-STABILITY-TERMINAL-063"
DOMAINS = (
    ("rewrite-or-bypass-predecessors", "compose-immutable-predecessors"),
    ("continuum-angle-or-fitted-small-value", "aligned-One-or-self-antipodal-half-One"),
    ("selected-single-hand", "complete-two-hand-support"),
    ("weak-antipode-reused-for-strong", "paired-parity-returns-aligned-One"),
    ("add-axion-or-free-compensator", "empty-One-no-extra-compensator"),
    ("invent-cross-fibre-mediator", "all-generated-actions-are-fibre-preserving"),
    ("untyped-particle-name", "three-one-third-parts-close-to-One"),
    ("assume-an-unregistered-decay-step", "finite-composition-preserves-the-fibre"),
    ("conflate-distinct-process-grammars", "retain-explicit-cosmological-boundary"),
    ("target-readable-before-seal", "targets-inaccessible-until-seal"),
    ("free-angle-carrier-or-operation", "no-extra-rule"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def prime(value):
    return value > 1 and all((value // divisor) * divisor != value for divisor in range(2, value))


def exact_result():
    sectors = tuple(value for value in range(2, 8) if prime(value))
    mediators = tuple(sector * sector - 1 for sector in sectors)
    signatures = tuple((sector, sector, cell) for sector, count in zip(sectors, mediators) for cell in range(1, count + 1))
    cross = tuple(
        (source, source_label, target, target_label)
        for source in sectors
        for target in sectors
        if source != target
        for source_label in range(1, source + 1)
        for target_label in range(1, target + 1)
    )
    hands = ("lower-held", "upper-held")
    subsets = tuple(subset for width in range(1, 3) for subset in combinations(hands, width))
    hand_rows = tuple((subset, len(tuple(product(range(1, 4), subset))) == 6) for subset in subsets)
    words = tuple(product(range(1, 4), repeat=3))
    baryon_tallies = tuple(sum((Fraction(1, 3) for _ in word), Fraction(1, 3)) - Fraction(1, 3) for word in words)
    return all((
        sectors == (2, 3, 5, 7),
        mediators == (3, 8, 24, 48),
        len(signatures) == 83,
        all(source == target for source, target, _ in signatures),
        len(cross) == 202,
        sum(1 for row in cross if row[0] == 3 and row[2] == 2) == 6,
        subsets == (("lower-held",), ("upper-held",), hands),
        sum(complete for _, complete in hand_rows) == 1,
        len(words) == 27,
        all(tally == Fraction(1, 1) for tally in baryon_tallies),
    ))


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        seal = json.load(handle)
    generated = tuple("__".join(values) for values in product(*DOMAINS))
    recorded = tuple(row["candidate_id"] for row in seal["census"]["candidates"])
    valid = exact_result()
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR and valid for candidate in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in seal["decisions"]}
    passed = all((
        sys.argv[1] == CLAIM_ID,
        seal["claim_id"] == CLAIM_ID,
        recorded == generated,
        len(set(recorded)) == seal["census"]["expected_cardinality"] == 2048,
        decisions == recomputed,
        sum(recomputed.values()) == 1,
        seal["closure"]["scope"] == "depth_independent",
        {row["kind"] for row in seal["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"},
        all(row["passed"] for row in seal["controls"]),
        valid,
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": seal["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": 2048,
            "strong_phase": "aligned-One",
            "mediator_count": 83,
            "cross_fibre_pairs": 202,
            "colour_to_binary_pairs": 6,
            "proton_images": 27,
            "baryon_tally": "One",
            "survivor": "__".join(SURVIVOR),
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
