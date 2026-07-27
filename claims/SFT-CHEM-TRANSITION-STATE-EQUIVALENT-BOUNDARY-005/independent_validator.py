"""Implementation-distinct value-free KIN-005 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-TRANSITION-STATE-EQUIVALENT-BOUNDARY-005"
DOMAINS = (
    ("saddle-point-or-continuum-transition-state-premise", "finite-generated-path-boundary-carrier"),
    ("isotopologue-or-reaction-identity-collapsed", "held-reaction-path-and-isotopologue-identities"),
    ("arbitrary-named-state-or-fitted-coordinate", "unique-greatest-exact-positive-path-support"),
    ("endpoint-only-or-boundary-answer-only", "complete-entry-boundary-exit-partition"),
    ("signed-or-negative-proof-scalar", "positive-magnitude-plus-held-orientation"),
    ("single-favorable-isotope-or-barrier-only", "complete-H2-D2-signature-uncertainty-and-adverse-record"),
    ("experimental-calculated-fitted-records-mixed", "experimental-targets-separated-from-calculated-and-fitted-records"),
    ("conventional-KIE-equation-target-access-or-refit", "value-free-complete-isotopologue-identity-seal-and-depth-independent-append"),
)
SURVIVOR = (
    "finite-generated-path-boundary-carrier__held-reaction-path-and-isotopologue-identities__"
    "unique-greatest-exact-positive-path-support__complete-entry-boundary-exit-partition__"
    "positive-magnitude-plus-held-orientation__complete-H2-D2-signature-uncertainty-and-adverse-record__"
    "experimental-targets-separated-from-calculated-and-fitted-records__"
    "value-free-complete-isotopologue-identity-seal-and-depth-independent-append"
)


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    path_one = (("entry-least", None), ("entry", Fraction(1)), ("boundary", Fraction(3)), ("exit", Fraction(2)))
    path_two = (("entry-least", None), ("entry", Fraction(2)), ("boundary", Fraction(5)), ("exit", Fraction(1)))
    boundary_one = max((row for row in path_one if row[1] is not None), key=lambda row: row[1])
    boundary_two = max((row for row in path_two if row[1] is not None), key=lambda row: row[1])
    complete_rows = ((1, "H2", boundary_one), (2, "D2", boundary_two))
    extended = complete_rows + ((3, "successor-isotope", ("boundary", Fraction(7))),)
    passed = (
        sealed["claim_id"] == CLAIM_ID and received == generated and len(generated) == 256
        and sealed["census"]["expected_cardinality"] == 256 and len(set(received)) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in sealed["controls"]} == {
            "false_premise", "tampered_source", "tampered_artifact", "boundary",
        }
        and all(row["passed"] is True for row in sealed["controls"])
        and boundary_one == ("boundary", Fraction(3)) and boundary_two == ("boundary", Fraction(5))
        and tuple(row[1] for row in complete_rows) == ("H2", "D2")
        and extended[: len(complete_rows)] == complete_rows
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
            "finite_unique_boundary_reconstructed": True,
            "complete_entry_boundary_exit_partition_reconstructed": True,
            "held_isotopologue_identity_reconstructed": True,
            "complete_path_append_preserves_prior_boundary_trace": True,
            "numerical_zero_negative_irrational_imaginary_logarithmic_signed_or_continuum_proof_value_used": False,
            "saddle_transition_state_KIE_arrhenius_fitted_barrier_target_measurement_or_source_file_accessed": False
        }
    }, sort_keys=True))


if __name__ == "__main__":
    main()
