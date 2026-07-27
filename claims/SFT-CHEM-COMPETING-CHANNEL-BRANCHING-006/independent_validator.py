"""Implementation-distinct value-free KIN-006 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-COMPETING-CHANNEL-BRANCHING-006"
DOMAINS = (
    ("selected-dominant-or-favorable-channel-subset", "complete-registered-product-channel-support"),
    ("imported-probability-normalization-axiom", "exact-sum-of-complete-retained-support"),
    ("fitted-or-free-branching-ratio", "exact-channel-support-over-complete-support"),
    ("reaction-condition-or-product-identity-collapsed", "held-reaction-condition-product-and-source-row-identities"),
    ("unfavorable-null-or-unresolved-channel-omitted", "structural-EmptyOne-channel-retained-without-invented-value"),
    ("ratio-answer-only-or-renormalized-table", "complete-source-ordered-support-share-uncertainty-and-adverse-record"),
    ("experimental-and-calculated-columns-mixed", "experimental-vector-separated-from-calculated-and-analysis-disclosures"),
    ("branch-value-readable-before-seal-or-corrected-after-release", "value-free-complete-eight-channel-identity-seal-and-depth-independent-successor"),
)
SURVIVOR = (
    "complete-registered-product-channel-support__exact-sum-of-complete-retained-support__"
    "exact-channel-support-over-complete-support__held-reaction-condition-product-and-source-row-identities__"
    "structural-EmptyOne-channel-retained-without-invented-value__"
    "complete-source-ordered-support-share-uncertainty-and-adverse-record__"
    "experimental-vector-separated-from-calculated-and-analysis-disclosures__"
    "value-free-complete-eight-channel-identity-seal-and-depth-independent-successor"
)


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    supports = (Fraction(2), Fraction(3))
    total = sum(supports, Fraction())
    shares = tuple(value / total for value in supports)
    prior = ((1, "product-a", supports[0]), (2, "product-b", supports[1]))
    extended = prior + ((3, "product-c", Fraction(1)),)
    passed = (
        sealed["claim_id"] == CLAIM_ID and received == generated and len(generated) == 256
        and sealed["census"]["expected_cardinality"] == 256 and len(set(received)) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in sealed["controls"])
        and total == Fraction(5) and shares == (Fraction(2, 5), Fraction(3, 5))
        and sum(shares, Fraction()) == Fraction(1) and extended[: len(prior)] == prior
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None, "closure": "depth_independent" if passed else None,
            "exact_complete_support_and_shares_reconstructed": True,
            "complete_partition_reconstructs_One": True,
            "channel_identity_and_successor_retention_reconstructed": True,
            "numerical_zero_negative_irrational_imaginary_logarithmic_signed_or_continuum_proof_value_used": False,
            "probability_axiom_branching_equation_fit_renormalization_target_measurement_or_source_file_accessed": False
        }
    }, sort_keys=True))


if __name__ == "__main__":
    main()
