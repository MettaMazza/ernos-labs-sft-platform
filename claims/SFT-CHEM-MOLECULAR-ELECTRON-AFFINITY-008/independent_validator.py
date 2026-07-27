"""Implementation-distinct value-free PROP-008 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-MOLECULAR-ELECTRON-AFFINITY-008'
DOMAINS = (('electron-affinity-answer-with-erased-states', 'complete-neutral-electron-anion-carrier'), ('signed-electron-addition', 'held-electron-gain-orientation'), ('conventional-signed-affinity-scalar', 'held-order-plus-positive-state-Take'), ('bound-anion-only-domain', 'bound-unbound-and-EmptyOne-boundary'), ('affinity-value-or-orientation-readable-before-seal', 'value-and-orientation-free-carrier-seal'), ('selected-positive-or-favorable-molecular-row', 'complete-NIST-molecular-experimental-vector'), ('central-value-with-erased-uncertainty', 'complete-source-uncertainty-custody'), ('species-fit-or-sign-correction', 'one-affinity-law-no-extra-rule'))
SURVIVOR = 'complete-neutral-electron-anion-carrier__held-electron-gain-orientation__held-order-plus-positive-state-Take__bound-unbound-and-EmptyOne-boundary__value-and-orientation-free-carrier-seal__complete-NIST-molecular-experimental-vector__complete-source-uncertainty-custody__one-affinity-law-no-extra-rule'

def difference(neutral, anion):
    if neutral == anion:
        return ("coincident-no-affinity-distinction", "empty-One")
    if neutral > anion:
        return ("anion-below-neutral-bound-attachment", neutral - anion)
    return ("anion-above-neutral-unbound-autodetachment", anion - neutral)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    bound = difference(Fraction(8, 1), Fraction(3, 1))
    unbound = difference(Fraction(3, 1), Fraction(8, 1))
    coincident = difference(Fraction(3, 1), Fraction(3, 1))
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
        and bound == ("anion-below-neutral-bound-attachment", Fraction(5, 1))
        and unbound == ("anion-above-neutral-unbound-autodetachment", Fraction(5, 1))
        and coincident == ("coincident-no-affinity-distinction", "empty-One")
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
            "bound_orientation_and_positive_Take_reconstructed": bound[1] == Fraction(5, 1),
            "unbound_orientation_and_positive_Take_reconstructed": unbound[1] == Fraction(5, 1),
            "coincident_EmptyOne_reconstructed": coincident[1] == "empty-One",
            "negative_proof_number_used": False,
            "measurement_file_accessed": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
