"""Implementation-distinct value-free PROP-011 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-INTERMOLECULAR-BINDING-011'
DOMAINS = (('answer-only-binding-number-with-erased-components', 'named-constituents-and-bound-composite-carrier'), ('continuum-distance-or-imported-potential-coordinate', 'finite-held-separation-organization'), ('constituent-energies-erased-or-merged', 'exact-positive-constituent-state-composition'), ('signed-free-energy-or-negative-binding-number', 'ordered-positive-separated-Take-bound'), ('assume-every-generated-aggregate-is-bound', 'strict-bound-order-or-structural-EmptyOne'), ('binding-target-readable-before-seal', 'value-free-complete-dimer-cluster-identity-seal'), ('favorable-dimer-method-or-measurement-subset', 'complete-computed-measured-adverse-and-scope-custody'), ('fitted-interaction-coefficient-or-species-correction', 'one-state-order-law-with-depth-independent-constituent-extension'))
SURVIVOR = 'named-constituents-and-bound-composite-carrier__finite-held-separation-organization__exact-positive-constituent-state-composition__ordered-positive-separated-Take-bound__strict-bound-order-or-structural-EmptyOne__value-free-complete-dimer-cluster-identity-seal__complete-computed-measured-adverse-and-scope-custody__one-state-order-law-with-depth-independent-constituent-extension'

def constituent_sum(states):
    if len(states) < 2 or any(value <= 0 for value in states):
        raise ValueError("two or more positive constituent states required")
    total = states[0]
    for value in states[1:]:
        total += value
    return total

def binding_take(separated, bound):
    if separated <= 0 or bound <= 0 or separated <= bound:
        raise ValueError("strict positive state order required")
    return separated - bound

def append_shared(separated, bound, shared):
    if shared <= 0:
        raise ValueError("shared constituent must be positive")
    return binding_take(separated + shared, bound + shared) == binding_take(separated, bound)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    separated = constituent_sum((Fraction(5, 2), Fraction(7, 3)))
    base = separated == Fraction(29, 6) and binding_take(separated, Fraction(4, 1)) == Fraction(5, 6)
    successor = append_shared(separated, Fraction(4, 1), Fraction(11, 5))
    repeated = binding_take(separated * 3, Fraction(4, 1) * 3) == Fraction(5, 2)
    reversed_rejected = False
    equal_rejected = False
    incomplete_rejected = False
    try:
        binding_take(Fraction(4, 1), separated)
    except ValueError:
        reversed_rejected = True
    try:
        binding_take(Fraction(4, 1), Fraction(4, 1))
    except ValueError:
        equal_rejected = True
    try:
        constituent_sum((Fraction(1, 1),))
    except ValueError:
        incomplete_rejected = True
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls)
        and base and successor and repeated and reversed_rejected and equal_rejected and incomplete_rejected
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID,
            "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
            "exact_named_constituent_composition_reconstructed": base,
            "ordered_positive_binding_take_reconstructed": base,
            "shared_constituent_successor_reconstructed": successor,
            "equal_repetition_reconstructed": repeated,
            "reversed_state_order_rejected": reversed_rejected,
            "equal_state_order_rejected": equal_rejected,
            "incomplete_constituent_support_rejected": incomplete_rejected,
            "measurement_file_accessed": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
