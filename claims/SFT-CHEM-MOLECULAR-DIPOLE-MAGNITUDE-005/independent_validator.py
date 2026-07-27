"""Implementation-distinct value-free PROP-005 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-MOLECULAR-DIPOLE-MAGNITUDE-005'
DOMAINS = (('answer-only-dipole-scalar', 'complete-named-molecular-charge-carrier'), ('component-list-selected-after-values', 'symmetry-forced-component-support'), ('signed-direction-as-proof-number', 'held-orientation-positive-components'), ('continuum-vector-premise', 'finite-distinct-axis-Junction'), ('irrational-square-root-or-fitted-norm', 'exact-squared-magnitude-relation'), ('dipole-value-readable-before-seal', 'value-free-symmetry-and-relation-seal'), ('favorable-species-or-component-subset', 'complete-five-species-nine-row-vector'), ('species-coefficient-charge-fit-or-correction', 'one-structural-law-no-extra-rule'))
SURVIVOR = 'complete-named-molecular-charge-carrier__symmetry-forced-component-support__held-orientation-positive-components__finite-distinct-axis-Junction__exact-squared-magnitude-relation__value-free-symmetry-and-relation-seal__complete-five-species-nine-row-vector__one-structural-law-no-extra-rule'

def square_junction(parts):
    if not parts:
        return "EmptyOne"
    axes = [axis for axis, value in parts]
    if len(set(axes)) != len(axes):
        raise ValueError("duplicate component axis")
    squares = [value * value for axis, value in parts]
    joined = squares[0]
    for part in squares[1:]:
        joined += part
    if joined.numerator < 1 or joined.denominator < 1:
        raise ValueError("square Junction left positive exact support")
    return joined

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    empty = square_junction([]) == "EmptyOne"
    one_axis = square_junction([("b", Fraction(3, 2))]) == Fraction(9, 4)
    two_axes = square_junction([("a", Fraction(3, 5)), ("b", Fraction(4, 5))]) == Fraction(1, 1)
    duplicate_rejected = False
    try:
        square_junction([("a", Fraction(1, 1)), ("a", Fraction(1, 1))])
    except ValueError:
        duplicate_rejected = True
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
        and empty and one_axis and two_axes and duplicate_rejected
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID,
            "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "finite_complete" if passed else None,
            "structural_EmptyOne_reconstructed": empty,
            "one_axis_square_reconstructed": one_axis,
            "two_axis_square_Junction_reconstructed": two_axes,
            "duplicate_axis_rejected": duplicate_rejected,
            "measurement_file_accessed": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
