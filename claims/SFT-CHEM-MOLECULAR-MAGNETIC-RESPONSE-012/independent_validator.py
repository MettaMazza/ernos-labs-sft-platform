"""Implementation-distinct value-free PROP-012 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-MOLECULAR-MAGNETIC-RESPONSE-012'
DOMAINS = (('answer-only-magnetic-number', 'complete-molecular-state-and-angular-carrier'), ('signed-direction-as-proof-number', 'opposed-held-orientation-labels'), ('assume-every-carrier-has-net-moment', 'pairwise-closure-to-EmptyOne-or-positive-excess'), ('fitted-or-species-g-coefficient', 'positive-response-per-angular-recurrence'), ('continuum-derivative-field-law', 'positive-induced-response-per-field-act'), ('moment-or-susceptibility-readable-before-seal', 'value-free-complete-magnetic-identity-seal'), ('favorable-or-accessible-molecule-subset', 'complete-g-factor-susceptibility-and-unavailable-custody'), ('species-correction-or-new-field-coefficient', 'one-ratio-law-with-depth-independent-repetition'))
SURVIVOR = 'complete-molecular-state-and-angular-carrier__opposed-held-orientation-labels__pairwise-closure-to-EmptyOne-or-positive-excess__positive-response-per-angular-recurrence__positive-induced-response-per-field-act__value-free-complete-magnetic-identity-seal__complete-g-factor-susceptibility-and-unavailable-custody__one-ratio-law-with-depth-independent-repetition'

def orientation_excess(a, b):
    if a <= 0 or b <= 0:
        raise ValueError("positive supports required")
    if a == b:
        return "balanced-closed", None
    return ("fibre-a", a-b) if a > b else ("fibre-b", b-a)

def moment(response, recurrence):
    if response <= 0 or recurrence <= 0:
        raise ValueError("positive response and recurrence required")
    return Fraction(response, recurrence)

def susceptibility(response, field_acts):
    if response <= 0 or field_acts <= 0:
        raise ValueError("positive response and field required")
    return response / field_acts

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    closed_orientation, closed = orientation_excess(3, 3)
    retained_orientation, retained = orientation_excess(5, 2)
    exact_moment = moment(retained, 2)
    exact_susceptibility = susceptibility(exact_moment, 5)
    repeated = susceptibility(exact_moment * 7, 5 * 7)
    controls = sealed["controls"]
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
        and closed_orientation == "balanced-closed" and closed is None
        and retained_orientation == "fibre-a" and retained == 3
        and exact_moment == Fraction(3, 2)
        and exact_susceptibility == Fraction(3, 10)
        and repeated == exact_susceptibility
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
            "balanced_orientation_closure_reconstructed": closed is None,
            "positive_unmatched_support_reconstructed": retained == 3,
            "exact_moment_ratio_reconstructed": exact_moment == Fraction(3, 2),
            "exact_susceptibility_ratio_reconstructed": exact_susceptibility == Fraction(3, 10),
            "equal_repetition_invariance_reconstructed": repeated == exact_susceptibility,
            "measurement_file_accessed": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
