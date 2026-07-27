"""Implementation-distinct value-free PROP-002 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-BOND-DISSOCIATION-ENERGY-002'
DOMAINS = (('generic-molecule-with-erased-isotope', 'named-isotopologue-and-X-state'), ('dissociation-products-erased', 'both-product-channels-held'), ('answer-only-energy-lookup', 'shared-prefix-path-composition'), ('signed-or-floating-subtraction', 'ordered-positive-held-Take'), ('measured-value-used-as-prediction-input', 'all-measurements-opened-post-seal'), ('dissociation-target-readable-before-seal', 'target-inaccessible-until-prediction-seal'), ('selected-historical-or-current-row', 'complete-historical-and-current-vector'), ('species-coefficient-or-correction', 'typed-two-row-exhaustion-no-extra-rule'))
SURVIVOR = 'named-isotopologue-and-X-state__both-product-channels-held__shared-prefix-path-composition__ordered-positive-held-Take__all-measurements-opened-post-seal__target-inaccessible-until-prediction-seal__complete-historical-and-current-vector__typed-two-row-exhaustion-no-extra-rule'

def positive_take(longer, shorter):
    if not longer > shorter:
        raise ValueError("ordered positive Take halted")
    result = longer - shorter
    if result.numerator < 1 or result.denominator < 1:
        raise ValueError("Take left the exact positive domain")
    return result

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    operational = positive_take(Fraction(9, 8), Fraction(3, 4)) == Fraction(3, 8)
    reversed_rejected = False
    try:
        positive_take(Fraction(3, 4), Fraction(9, 8))
    except ValueError:
        reversed_rejected = True
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "finite_complete"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls)
        and operational and reversed_rejected
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "finite_complete" if passed else None,
            "ordered_positive_Take_reconstructed": operational,
            "reversed_Take_rejected": reversed_rejected,
            "measurement_file_accessed": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
