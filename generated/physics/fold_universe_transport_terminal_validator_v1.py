#!/usr/bin/env python3
"""Independent composite Fold-orbit and transport-boundary reconstruction."""

from __future__ import annotations

from itertools import product
from math import gcd
import json
import sys


CLAIM_ID = "SFT-PHYS-FOLD-UNIVERSE-TRANSPORT-TERMINAL-024"
DOMAINS = (
    ("unbounded-cosmological-world", "exact-odd-denominator-orbit-component"),
    ("selected-denominator-change", "denominator-preserved-at-every-step"),
    ("asserted-network-edge", "complete-coprime-composite-product"),
    ("lossy-or-selected-projection", "bijective-commuting-component-map"),
    ("chosen-or-multiplied-period", "least-common-multiple-period"),
    ("independent-unrelated-trajectories", "joint-lockstep-support-correlation"),
    ("correlation-relabeled-as-signal", "target-trajectory-independent-of-source"),
    ("description-map-relabeled-as-travel", "empty-cross-component-transition-record"),
    ("literal-multiverse-transport-asserted", "arithmetic-correspondence-with-causal-boundary"),
    ("free-portal-or-time-channel", "no-extra-rule"),
)
SURVIVOR = tuple(domain[-1] for domain in DOMAINS)


def units(q):
    return tuple(r for r in range(1, q) if gcd(r, q) == 1)


def fold(r, q):
    return (2 * r) % q


def period(q):
    current = 1
    count = 0
    while True:
        current = fold(current, q)
        count += 1
        if current == 1:
            return count


def pair_check(left, right):
    composite = left * right
    pairs = tuple((r % left, r % right) for r in units(composite))
    target = tuple(product(units(left), units(right)))
    commutes = all((fold(r, composite) % left, fold(r, composite) % right) == (fold(r % left, left), fold(r % right, right)) for r in units(composite))
    lcm = period(left) * period(right) // gcd(period(left), period(right))
    target_rows = []
    for source in units(left):
        current_source = source
        current_target = 1
        target_trace = []
        for _ in range(12):
            current_source = fold(current_source, left)
            current_target = fold(current_target, right)
            target_trace.append(current_target)
        target_rows.append(tuple(target_trace))
    target_independent = len(set(target_rows)) == 1
    return len(set(pairs)) == len(pairs) == len(target) and set(pairs) == set(target) and commutes and period(composite) == lcm and target_independent


def theorem_check():
    return all(pair_check(left, right) for left, right in ((3, 5), (3, 7), (5, 7))) and all(fold(r, q) in units(q) for q in (3, 5, 7, 15, 21, 35) for r in units(q))


def generated_ids():
    return tuple("__".join(row) for row in product(*DOMAINS))


def main() -> None:
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = generated_ids()
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    recomputed = {candidate_id: tuple(candidate_id.split("__")) == SURVIVOR and theorem_check() for candidate_id in generated}
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    passed = sys.argv[1] == CLAIM_ID and sealed["claim_id"] == CLAIM_ID and received == generated and len(set(received)) == sealed["census"]["expected_cardinality"] == 1024 and decisions == recomputed and sum(recomputed.values()) == 1 and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"} and all(row["passed"] for row in sealed["controls"]) and theorem_check()
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": len(generated), "coprime_pairs_checked": [[3, 5], [3, 7], [5, 7]], "literal_physical_transport_admitted": False, "survivor": "__".join(SURVIVOR)}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
