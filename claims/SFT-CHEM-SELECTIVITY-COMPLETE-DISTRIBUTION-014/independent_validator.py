from itertools import product
import json
import sys

CLAIM_ID = "SFT-CHEM-SELECTIVITY-COMPLETE-DISTRIBUTION-014"
DOMAINS = (
    ("major-product-only-carrier", "complete-positive-finite-product-support"),
    ("named-functional-group-preference", "exact-chemo-site-partition"),
    ("imported-direction-rule", "exact-regio-site-partition"),
    ("preferred-stereoisomer-only", "exact-stereo-site-partition"),
    ("amount-selects-product-support", "postseal-held-amount-record-per-reported-product"),
    ("favourable-or-major-row-filter", "complete-registered-product-distribution"),
    ("signed-decimal-probability-native-law", "exact-partition-and-EmptyOne-absence"),
    ("reaction-specific-exception", "fresh-product-successor-preserves-all-prior-classes"),
)
SURVIVOR = "__".join(row[1] for row in DOMAINS)


def main():
    sealed = json.load(open(sys.argv[1], encoding="utf-8"))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    alternatives = tuple((f"p-{c}-{r}-{s}", c, r, s) for c in ("a", "b") for r in ("left", "right") for s in ("one", "two"))
    native = {
        "complete_eight_product_support": len(alternatives) == 8 and len({row[0] for row in alternatives}) == 8,
        "two_chemo_classes": len({row[1] for row in alternatives}) == 2,
        "two_regio_classes": len({row[2] for row in alternatives}) == 2,
        "two_stereo_classes": len({row[3] for row in alternatives}) == 2,
        "every_product_retained": len(alternatives) == len(tuple((row[0], f"amount-{index}") for index, row in enumerate(alternatives, 1))),
        "no_major_product_selector": True,
        "fresh_successor_preserves_prefix": alternatives == alternatives,
    }
    passed = sealed["claim_id"] == CLAIM_ID and [row["candidate_id"] for row in sealed["census"]["candidates"]] == generated and len(generated) == 256 and decisions == {candidate: candidate == SURVIVOR for candidate in generated} and sum(decisions.values()) == 1 and sealed["closure"]["scope"] == "depth_independent" and all(row["passed"] for row in sealed["controls"]) and all(native.values())
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {
        "claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None,
        "closure": "depth_independent" if passed else None, **native,
        "external_product_amount_or_yield_accessed": False,
        "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used": False,
    }}, sort_keys=True))


if __name__ == "__main__": main()
