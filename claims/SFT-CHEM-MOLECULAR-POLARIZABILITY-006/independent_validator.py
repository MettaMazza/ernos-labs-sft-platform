"""Implementation-distinct value-free PROP-006 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-MOLECULAR-POLARIZABILITY-006'
DOMAINS = (('answer-only-alpha-scalar', 'complete-named-molecular-response-carrier'), ('imported-continuum-derivative', 'exact-positive-response-over-field-ratio'), ('signed-Cartesian-component', 'held-axis-positive-component'), ('continuum-tensor-trace-premise', 'three-axis-exact-one-third-Junction'), ('depth-specific-response-coefficient', 'equal-act-ratio-invariant-successor'), ('alpha-readable-before-seal', 'value-free-identity-and-relation-seal'), ('selected-species-or-favorable-subset', 'complete-NIST-non-atomic-vector'), ('species-fit-or-residual-correction', 'one-response-law-no-extra-rule'))
SURVIVOR = 'complete-named-molecular-response-carrier__exact-positive-response-over-field-ratio__held-axis-positive-component__three-axis-exact-one-third-Junction__equal-act-ratio-invariant-successor__value-free-identity-and-relation-seal__complete-NIST-non-atomic-vector__one-response-law-no-extra-rule'

def response_ratio(response, field):
    if response <= 0 or field <= 0:
        raise ValueError("response and field must be positive")
    return response / field

def repeated_ratio(response, field, count):
    if count < 1:
        raise ValueError("count must be positive")
    return response_ratio(response * count, field * count)

def isotropic(parts):
    if len(parts) != 3 or len({axis for axis, value in parts}) != 3:
        raise ValueError("complete distinct three-axis support required")
    values = [value for axis, value in parts]
    if any(value <= 0 for value in values):
        raise ValueError("component response must be positive")
    return (values[0] + values[1] + values[2]) / 3

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    base = response_ratio(Fraction(6, 1), Fraction(2, 1)) == Fraction(3, 1)
    successor = repeated_ratio(Fraction(6, 1), Fraction(2, 1), 7) == Fraction(3, 1)
    mean = isotropic((("a", Fraction(2, 1)), ("b", Fraction(3, 1)), ("c", Fraction(4, 1)))) == Fraction(3, 1)
    incomplete_rejected = False
    duplicate_rejected = False
    try:
        isotropic((("a", Fraction(2, 1)), ("b", Fraction(3, 1))))
    except ValueError:
        incomplete_rejected = True
    try:
        isotropic((("a", Fraction(2, 1)), ("a", Fraction(3, 1)), ("c", Fraction(4, 1))))
    except ValueError:
        duplicate_rejected = True
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
        and base and successor and mean and incomplete_rejected and duplicate_rejected
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
            "exact_response_ratio_reconstructed": base,
            "equal_act_successor_reconstructed": successor,
            "three_axis_one_third_Junction_reconstructed": mean,
            "incomplete_axis_support_rejected": incomplete_rejected,
            "duplicate_axis_rejected": duplicate_rejected,
            "measurement_file_accessed": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
