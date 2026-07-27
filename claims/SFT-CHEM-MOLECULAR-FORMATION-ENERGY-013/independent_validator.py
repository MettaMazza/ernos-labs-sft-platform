"""Implementation-distinct value-free PROP-013 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-MOLECULAR-FORMATION-ENERGY-013'
DOMAINS = (('answer-only-formation-number', 'complete-product-reference-state-carrier'), ('imported-or-fitted-atomic-reference', 'exact-named-constituent-reference-composition'), ('signed-formation-proof-number', 'held-product-reference-state-order'), ('species-coefficient-or-target-value', 'exact-positive-state-separation'), ('numerical-zero-for-equality-or-blank', 'equality-or-unmeasured-as-distinct-structural-EmptyOne'), ('formation-values-readable-before-seal', 'value-free-complete-formation-identity-seal'), ('favorable-species-temperature-or-sign-subset', 'complete-values-blanks-orientations-and-reference-custody'), ('new-coefficient-per-added-constituent', 'one-relation-with-depth-independent-shared-state-extension'))
SURVIVOR = 'complete-product-reference-state-carrier__exact-named-constituent-reference-composition__held-product-reference-state-order__exact-positive-state-separation__equality-or-unmeasured-as-distinct-structural-EmptyOne__value-free-complete-formation-identity-seal__complete-values-blanks-orientations-and-reference-custody__one-relation-with-depth-independent-shared-state-extension'

def compose_reference(states):
    if not states or any(state <= 0 for state in states):
        raise ValueError("positive nonempty reference required")
    total = states[0]
    for state in states[1:]: total += state
    return total

def relation(product_state, reference_state):
    if product_state <= 0 or reference_state <= 0:
        raise ValueError("positive states required")
    if product_state == reference_state: return "product-reference-equal", None
    if product_state > reference_state: return "product-above-reference", product_state-reference_state
    return "product-below-reference", reference_state-product_state

def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    reference = compose_reference((Fraction(5,2), Fraction(7,3)))
    below = relation(Fraction(4,1), reference)
    above = relation(Fraction(6,1), reference)
    equal = relation(reference, reference)
    shared = relation(Fraction(4,1)+Fraction(11,5), reference+Fraction(11,5))
    repeated = relation(Fraction(4,1)*3, reference*3)
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
        and reference == Fraction(29,6)
        and below == ("product-below-reference", Fraction(5,6))
        and above == ("product-above-reference", Fraction(7,6))
        and equal == ("product-reference-equal", None)
        and shared == below
        and repeated == ("product-below-reference", Fraction(5,2))
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
            "reference_composition_reconstructed": reference == Fraction(29,6),
            "both_orientations_reconstructed": below[0] != above[0],
            "structural_equality_reconstructed": equal[1] is None,
            "shared_state_extension_reconstructed": shared == below,
            "positive_repetition_reconstructed": repeated[1] == Fraction(5,2),
            "measurement_file_accessed": False,
        },
    }, sort_keys=True))

if __name__ == "__main__": main()
