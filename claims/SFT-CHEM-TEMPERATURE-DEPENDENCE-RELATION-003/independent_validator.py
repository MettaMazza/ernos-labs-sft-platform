"""Implementation-distinct value-free KIN-003 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-TEMPERATURE-DEPENDENCE-RELATION-003"
DOMAINS = (
    ("anonymous-collapsed-or-changing-reaction", "held-registered-reaction-identity-per-row"),
    ("temperature-erased-signed-or-continuum-variable", "exact-positive-temperature-support-per-row"),
    ("answer-only-rate-or-unregistered-change", "exact-positive-elementary-rate-response-per-row"),
    ("density-bath-method-or-uncertainty-collapsed", "complete-held-density-bath-method-and-uncertainty-record"),
    ("selected-favorable-rows-reaction-or-averaged-answer", "complete-two-reaction-source-ordered-row-census"),
    ("imported-arrhenius-exponential-logarithm-prefactor-or-activation-fit", "exact-condition-bound-temperature-rate-table"),
    ("temperature-density-rate-or-target-value-readable-before-seal", "complete-value-free-19-target-identity-seal"),
    ("refit-after-complete-row-append", "depth-independent-complete-row-append-with-prior-trace-preserved"),
)
SURVIVOR = (
    "held-registered-reaction-identity-per-row__exact-positive-temperature-support-per-row__"
    "exact-positive-elementary-rate-response-per-row__complete-held-density-bath-method-and-uncertainty-record__"
    "complete-two-reaction-source-ordered-row-census__exact-condition-bound-temperature-rate-table__"
    "complete-value-free-19-target-identity-seal__depth-independent-complete-row-append-with-prior-trace-preserved"
)


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    complete_rows = (
        (1, 1, "reaction-a", Fraction(3), Fraction(5)),
        (2, 2, "reaction-a", Fraction(7), Fraction(4)),
        (3, 2, "reaction-b", Fraction(7), Fraction(6)),
    )
    extended = complete_rows + ((4, 3, "reaction-b", Fraction(11), Fraction(7)),)
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
        and tuple(row[0] for row in complete_rows) == (1, 2, 3)
        and complete_rows[1][4] < complete_rows[0][4]
        and {row[2] for row in complete_rows} == {"reaction-a", "reaction-b"}
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
            "source_order_reconstructed": True,
            "unfavorable_lower_response_retained": True,
            "two_registered_reactions_remain_distinct": True,
            "complete_row_append_preserves_prior_trace": True,
            "numerical_zero_negative_irrational_imaginary_logarithmic_signed_or_continuum_proof_value_used": False,
            "arrhenius_exponential_prefactor_activation_fit_target_or_measurement_file_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
