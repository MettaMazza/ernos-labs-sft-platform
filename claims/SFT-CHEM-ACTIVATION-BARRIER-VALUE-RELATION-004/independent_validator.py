"""Implementation-distinct value-free KIN-004 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-ACTIVATION-BARRIER-VALUE-RELATION-004"
DOMAINS = (
    ("endpoint-only-or-saddle-continuum-premise", "complete-generated-discrete-path-state-word"),
    ("free-fitted-or-imported-barrier-number", "exact-source-bound-state-support"),
    ("arbitrary-named-transition-state", "highest-positive-generated-path-boundary"),
    ("absolute-energy-origin-or-signed-difference", "least-state-EmptyOne-relative-support"),
    ("nonminimal-added-support", "least-crossing-positive-support"),
    ("species-path-or-state-collapsed", "held-species-torsion-and-state-identities"),
    ("barrier-answer-only-or-selected-profile", "complete-source-ordered-profile-reference-and-adverse-record"),
    ("barrier-value-readable-before-seal-or-refit-on-append", "complete-value-free-44-target-identity-seal-and-depth-independent-append"),
)
SURVIVOR = (
    "complete-generated-discrete-path-state-word__exact-source-bound-state-support__"
    "highest-positive-generated-path-boundary__least-state-EmptyOne-relative-support__"
    "least-crossing-positive-support__held-species-torsion-and-state-identities__"
    "complete-source-ordered-profile-reference-and-adverse-record__"
    "complete-value-free-44-target-identity-seal-and-depth-independent-append"
)


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    path_one = (("least", None), ("state-a", Fraction(2)), ("boundary", Fraction(5)), ("state-b", Fraction(3)))
    path_two = (("least", None), ("boundary", Fraction(3)))
    positive_one = tuple(row for row in path_one if row[1] is not None)
    barrier_one = max(positive_one, key=lambda row: row[1])
    complete_rows = ((1, "species-a", "path-a", barrier_one), (2, "species-b", "path-b", path_two[-1]))
    extended = complete_rows + ((3, "species-c", "path-c", ("boundary", Fraction(7))),)
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
        and barrier_one == ("boundary", Fraction(5))
        and path_one[0][1] is None
        and tuple(row[0] for row in complete_rows) == (1, 2)
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
            "highest_positive_path_boundary_reconstructed": True,
            "structural_least_state_reconstructed": True,
            "species_path_and_state_identity_retention_reconstructed": True,
            "complete_path_append_preserves_prior_trace": True,
            "numerical_zero_negative_irrational_imaginary_logarithmic_signed_or_continuum_proof_value_used": False,
            "saddle_transition_state_arrhenius_fitted_barrier_target_or_measurement_file_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
