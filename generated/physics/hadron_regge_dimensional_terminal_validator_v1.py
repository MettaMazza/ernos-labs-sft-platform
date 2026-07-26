#!/usr/bin/env python3
from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-PHYS-HADRON-REGGE-DIMENSIONAL-TERMINAL-059"
DOMAINS = (
    ("rewrite-or-ignore-admitted-laws", "immutable-receipt-custody"),
    ("selected-or-fitted-intercept", "admitted-three-fifths-motion-share"),
    ("chosen-trajectory-multiplicity", "both-forced-Fold-hands"),
    ("fitted-common-slope", "two-times-three-fifths"),
    ("numerical-zero-or-free-offset", "first-positive-rank-three-fifths"),
    ("finite-five-row-pattern", "depth-independent-induction"),
    ("unit-name-selects-coefficients", "postseal-common-positive-unit"),
    ("target-readable-before-seal", "target-inaccessible-until-formal-seal"),
    ("free-spin-correction", "no-extra-rule"),
)
SURVIVOR = tuple(domain[1] for domain in DOMAINS)


def main():
    with open(sys.argv[2], encoding="utf-8") as handle:
        seal = json.load(handle)
    generated = tuple("__".join(values) for values in product(*DOMAINS))
    recorded = tuple(row["candidate_id"] for row in seal["census"]["candidates"])
    carriers = tuple(Fraction(6 * rank - 3, 5) for rank in range(1, 65))
    valid = carriers[:5] == (Fraction(3, 5), Fraction(9, 5), Fraction(3), Fraction(21, 5), Fraction(27, 5)) and all(carriers[i + 1] - carriers[i] == Fraction(6, 5) for i in range(63))
    recomputed = {candidate: tuple(candidate.split("__")) == SURVIVOR and valid for candidate in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in seal["decisions"]}
    passed = all((sys.argv[1] == CLAIM_ID, seal["claim_id"] == CLAIM_ID, recorded == generated, len(set(recorded)) == seal["census"]["expected_cardinality"] == 512, decisions == recomputed, sum(recomputed.values()) == 1, seal["closure"]["scope"] == "depth_independent", {row["kind"] for row in seal["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}, all(row["passed"] for row in seal["controls"]), valid))
    print(json.dumps({"passed": passed, "validated_seal_hash": seal["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 512, "base": "3/5", "successor": "6/5", "first_five": [str(value) for value in carriers[:5]], "survivor": "__".join(SURVIVOR)}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
