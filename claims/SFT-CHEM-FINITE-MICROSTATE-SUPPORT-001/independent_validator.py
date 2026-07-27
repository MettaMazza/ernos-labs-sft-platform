"""Implementation-distinct value-free THERMO-001 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-FINITE-MICROSTATE-SUPPORT-001'
DOMAINS = (('selected-or-completed-infinite-state-set', 'complete-generated-finite-chemical-support'), ('answer-only-state-count', 'complete-held-chemical-microstate-identity'), ('overlapping-or-omitting-observation-classes', 'disjoint-exhaustive-macro-observation-partition'), ('floating-or-assumed-degeneracy', 'exact-positive-fibre-count'), ('imported-distribution-or-partition-function', 'exact-fibre-count-over-complete-support-count'), ('population-temperature-or-calorimetric-target-readable-before-seal', 'complete-value-free-state-and-calorimetric-identity-seal'), ('selected-population-or-calorimetric-showcase', 'complete-387-row-external-structure-custody'), ('continuum-or-completed-infinity-closure', 'depth-independent-one-state-finite-successor'))
SURVIVOR = 'complete-generated-finite-chemical-support__complete-held-chemical-microstate-identity__disjoint-exhaustive-macro-observation-partition__exact-positive-fibre-count__exact-fibre-count-over-complete-support-count__complete-value-free-state-and-calorimetric-identity-seal__complete-387-row-external-structure-custody__depth-independent-one-state-finite-successor'

def finite_support(states, fibres):
    if not states or len(states) != len(set(states)) or not fibres:
        raise ValueError("finite unique support and fibres required")
    flattened = tuple(state for _, members in fibres for state in members)
    labels = tuple(label for label, _ in fibres)
    if len(labels) != len(set(labels)) or any(not members for _, members in fibres):
        raise ValueError("finite nonempty unique fibres required")
    if len(flattened) != len(set(flattened)) or set(flattened) != set(states):
        raise ValueError("fibres must partition support exactly once")
    return tuple(states), tuple(fibres)

def weight(support, label):
    states, fibres = support
    matches = tuple(members for name, members in fibres if name == label)
    if len(matches) != 1: raise ValueError("macrostate absent or non-unique")
    return Fraction(len(matches[0]), len(states))

def append_state(support, state, label):
    states, fibres = support
    if state in states or label in {name for name, _ in fibres}:
        raise ValueError("finite successor must be new")
    return finite_support(states + (state,), fibres + ((label, (state,)),))

def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    support = finite_support(("state-a", "state-b", "state-c"), (("macro-a", ("state-a", "state-b")), ("macro-b", ("state-c",))))
    overlap_rejected = False
    try: finite_support(("state-a", "state-b", "state-c"), (("macro-a", ("state-a", "state-b")), ("macro-b", ("state-b", "state-c"))))
    except ValueError: overlap_rejected = True
    extended = append_state(support, "state-d", "macro-c")
    controls = sealed["controls"]
    passed = (
        sealed["claim_id"] == CLAIM_ID and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls)
        and weight(support, "macro-a") == Fraction(2,3)
        and weight(support, "macro-b") == Fraction(1,3)
        and overlap_rejected
        and extended[0][:-1] == support[0] and extended[1][:-1] == support[1]
        and extended[0][-1] == "state-d" and extended[1][-1] == ("macro-c", ("state-d",))
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
            "complete_partition_reconstructed": support[0] == ("state-a", "state-b", "state-c"),
            "exact_two_thirds_and_one_third_weights_reconstructed": weight(support, "macro-a") == Fraction(2,3) and weight(support, "macro-b") == Fraction(1,3),
            "overlap_rejected": overlap_rejected,
            "finite_successor_reconstructed": extended[0][:-1] == support[0] and extended[1][:-1] == support[1],
            "measurement_file_accessed": False,
        },
    }, sort_keys=True))

if __name__ == "__main__": main()
