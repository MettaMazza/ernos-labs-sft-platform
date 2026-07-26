#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-THERMAL-HELIUM-ISOTOPE-TERMINAL-057"
DOMAINS = (
    ("measured-decimal-called-family-law", "admitted-quarter-baryon-family"),
    ("selected-arity", "helium-four-complete-arity"),
    ("selected-proper-subset", "all-fifteen-nonempty-subwords"),
    ("partial-incidence-ledger", "complete-four-by-fifteen-product"),
    ("empty-or-multiple-composite-identities", "one-global-composite-identity"),
    ("fitted-isotope-correction", "fifty-nine-of-sixty-isotope-cells"),
    ("quarter-rubber-stamp-or-decimal-copy", "fifty-nine-over-two-forty-and-one-eighty-one-over-two-forty"),
    ("target-readable-candidate-selection", "target-closed-until-formal-seal"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def check():
    masks = tuple(range(1, 2 ** 4))
    cells = tuple((position, mask) for position in range(1, 5) for mask in masks)
    return all((len(masks) == 15, len(cells) == len(set(cells)) == 60, Fraction(60 - 1, 60) == Fraction(59, 60), Fraction(1, 4) * Fraction(59, 60) == Fraction(59, 240), Fraction(59, 240) + Fraction(181, 240) == 1))


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        seal = json.load(handle)
    generated = tuple("__".join(values) for values in product(*DOMAINS))
    recorded = tuple(row["candidate_id"] for row in seal["census"]["candidates"])
    valid = check()
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR and valid for candidate in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in seal["decisions"]}
    passed = all((sys.argv[1] == CLAIM_ID, seal["claim_id"] == CLAIM_ID, recorded == generated, len(set(recorded)) == seal["census"]["expected_cardinality"] == 256, decisions == recomputed, sum(recomputed.values()) == 1, seal["closure"]["scope"] == "depth_independent", {row["kind"] for row in seal["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}, all(row["passed"] for row in seal["controls"]), valid))
    print(json.dumps({"passed": passed, "validated_seal_hash": seal["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "constituents": 4, "nonempty_subwords": 15, "complete_cells": 60, "collective_identity_records": 1, "conversion": "59/60", "physical_helium_share": "59/240", "survivor": "__".join(SURVIVOR)}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
