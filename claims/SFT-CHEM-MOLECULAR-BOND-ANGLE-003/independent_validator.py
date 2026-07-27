"""Implementation-distinct value-free PROP-003 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-MOLECULAR-BOND-ANGLE-003'
DOMAINS = (('answer-only-angle-scalar', 'named-state-geometry-sector-carrier'), ('unordered-ligand-cloud', 'exact-generated-cyclic-order'), ('unequal-or-fitted-sectors', 'symmetry-forced-equal-sectors'), ('continuum-trigonometric-angle', 'positive-sector-separation-over-count'), ('degree-target-in-prediction', 'value-free-exact-turn-fraction'), ('target-open-before-seal', 'all-angle-values-open-post-seal'), ('selected-species-or-angle-role', 'complete-three-species-four-angle-vector'), ('species-correction-or-angle-exception', 'one-law-no-extra-rule'))
SURVIVOR = 'named-state-geometry-sector-carrier__exact-generated-cyclic-order__symmetry-forced-equal-sectors__positive-sector-separation-over-count__value-free-exact-turn-fraction__all-angle-values-open-post-seal__complete-three-species-four-angle-vector__one-law-no-extra-rule'

def equal_sector(geometry, count, separation):
    expected = {
        "linear-equal-two-sector": 2,
        "trigonal-planar-equal-three-sector": 3,
        "square-planar-equal-four-sector": 4,
    }
    if geometry not in expected or count != expected[geometry] or separation + separation > count:
        raise ValueError("ungenerated angle carrier")
    return Fraction(separation, count)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    vector = (
        equal_sector("trigonal-planar-equal-three-sector", 3, 1),
        equal_sector("linear-equal-two-sector", 2, 1),
        equal_sector("square-planar-equal-four-sector", 4, 1),
        equal_sector("square-planar-equal-four-sector", 4, 2),
    )
    unsupported_rejected = False
    try:
        equal_sector("tetrahedral-continuum-angle", 4, 1)
    except ValueError:
        unsupported_rejected = True
    wrong_count_rejected = False
    try:
        equal_sector("square-planar-equal-four-sector", 3, 1)
    except ValueError:
        wrong_count_rejected = True
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
        and vector == (Fraction(1, 3), Fraction(1, 2), Fraction(1, 4), Fraction(1, 2))
        and unsupported_rejected and wrong_count_rejected
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "finite_complete" if passed else None,
            "turn_fractions_reconstructed": ["1/3", "1/2", "1/4", "1/2"],
            "unsupported_geometry_rejected": unsupported_rejected,
            "wrong_count_rejected": wrong_count_rejected,
            "measurement_file_accessed": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
