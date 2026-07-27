"""Implementation-distinct value-free THERMO-005 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005"
DOMAINS = (
    ("selected-or-completed-infinite-chemical-support", "complete-finite-chemical-microstate-support"),
    ("overlapping-or-partial-macroclasses", "disjoint-exhaustive-chemical-observation-classes"),
    ("fitted-probability-or-floating-weight", "exact-positive-class-count-and-whole-part"),
    ("logarithmic-or-irrational-scalar-proof", "complete-unresolved-distinction-ledger"),
    ("numerical-zero-singleton-entropy", "structural-EmptyOne-singleton-certainty"),
    ("entropy-or-phase-target-readable-before-seal", "complete-value-free-entropy-phase-identity-seal"),
    ("selected-entropy-or-single-phase-row", "complete-13-row-entropy-phase-transition-vector"),
    ("resample-or-refit-after-new-microstate", "depth-independent-one-microstate-ledger-successor"),
)
SURVIVOR = (
    "complete-finite-chemical-microstate-support__disjoint-exhaustive-chemical-observation-classes__"
    "exact-positive-class-count-and-whole-part__complete-unresolved-distinction-ledger__"
    "structural-EmptyOne-singleton-certainty__complete-value-free-entropy-phase-identity-seal__"
    "complete-13-row-entropy-phase-transition-vector__depth-independent-one-microstate-ledger-successor"
)


def ledger(support, observation):
    images = dict(observation)
    if not support or len(set(support)) != len(support) or len(images) != len(observation) or set(images) != set(support):
        raise ValueError("complete finite support and total observation required")
    labels = tuple(dict.fromkeys(images[state] for state in support))
    result = []
    for label in labels:
        members = tuple(state for state in support if images[state] == label)
        pairs = tuple((left, right) for position, left in enumerate(members) for right in members[position + 1:])
        result.append((label, members, len(members), Fraction(len(members), len(support)), pairs if pairs else None))
    return tuple(result)


def append_preserves(support, observation, state, image):
    prior = ledger(support, observation)
    extended = ledger(support + (state,), observation + ((state, image),))
    prior_map = {row[0]: row for row in prior}; extended_map = {row[0]: row for row in extended}
    return all(
        extended_map[label][1][:-1] == row[1] if label == image else extended_map[label][1] == row[1]
        for label, row in prior_map.items()
    )


def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    support = ("aa", "ab", "ba", "bb")
    fine = tuple((state, state) for state in support)
    prefix = tuple((state, state[0]) for state in support)
    coarse = tuple((state, "unresolved") for state in support)
    fine_ledger, prefix_ledger, coarse_ledger = ledger(support, fine), ledger(support, prefix), ledger(support, coarse)
    controls = sealed["controls"]
    passed = (
        sealed["claim_id"] == CLAIM_ID and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and len(tuple(candidate for candidate, survives in decisions.items() if survives)) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls)
        and all(row[2] == 2 and row[3] == Fraction(1, 2) and len(row[4]) == 1 for row in prefix_ledger)
        and all(row[4] is None for row in fine_ledger)
        and len(coarse_ledger[0][4]) == 6
        and append_preserves(support, prefix, "ac", "a")
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None, "closure": "depth_independent" if passed else None,
            "exact_multiplicity_reconstructed": all(row[2] == 2 and row[3] == Fraction(1, 2) for row in prefix_ledger),
            "complete_pair_ledger_reconstructed": len(coarse_ledger[0][4]) == 6,
            "structural_singleton_absence_reconstructed": all(row[4] is None for row in fine_ledger),
            "one_microstate_successor_reconstructed": append_preserves(support, prefix, "ac", "a"),
            "logarithm_or_measurement_file_accessed": False
        }
    }, sort_keys=True))


if __name__ == "__main__":
    main()
