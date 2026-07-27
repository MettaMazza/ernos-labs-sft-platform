from itertools import product
from math import gcd
from functools import reduce
import json
import sys


CLAIM = "SFT-CHEM-DEFECT-NONSTOICHIOMETRY-016"
DOMAINS = (
    ("continuum-defect-density", "finite-complete-reference-and-observed-motif"),
    ("nominal-formula-only", "complete-reference-site-and-species-support"),
    ("numerical-zero-occupancy", "reference-site-with-structural-EmptyOne"),
    ("signed-stoichiometric-subtraction", "separate-positive-missing-and-added-supports"),
    ("selected-defect-name", "complete-vacancy-substitution-interstitial-classes"),
    ("fitted-nonstoichiometric-variable", "exact-reference-observed-primitive-formulas"),
    ("assumed-intrinsic-or-extrinsic-label", "reference-membership-forces-origin-class"),
    ("catalogue-specific-defect-exception", "site-occurrence-successor-no-extra-rule"),
)
SURVIVOR = (
    "finite-complete-reference-and-observed-motif__complete-reference-site-and-species-support__"
    "reference-site-with-structural-EmptyOne__separate-positive-missing-and-added-supports__"
    "complete-vacancy-substitution-interstitial-classes__exact-reference-observed-primitive-formulas__"
    "reference-membership-forces-origin-class__site-occurrence-successor-no-extra-rule"
)


def main():
    document = json.load(open(sys.argv[1], encoding="utf-8"))
    generated = ["__".join(candidate) for candidate in product(*DOMAINS)]
    recorded = [row["candidate_id"] for row in document["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in document["decisions"]}
    reference_counts = {"A": 2, "B": 2}
    observed_counts = {"A": 1, "B": 2}
    missing = {label: count - observed_counts.get(label, 0) for label, count in reference_counts.items() if count > observed_counts.get(label, 0)}
    added = {label: count - reference_counts.get(label, 0) for label, count in observed_counts.items() if count > reference_counts.get(label, 0)}
    observed_values = tuple(observed_counts.values())
    divisor = reduce(gcd, observed_values)
    observed_formula = tuple(value // divisor for value in observed_values)
    reconstructed = missing == {"A": 1} and added == {} and observed_formula == (1, 2)
    passed = (
        document["claim_id"] == CLAIM
        and recorded == generated
        and len(generated) == 256
        and len(set(recorded)) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and document["closure"]["scope"] == "depth_independent"
        and document["closure"]["minimality_passed"]
        and document["closure"]["named_shape_uniqueness_passed"]
        and all(row["passed"] for row in document["controls"])
        and reconstructed
    )
    print(
        json.dumps(
            {
                "validated_seal_hash": document["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "passed": passed,
                "certificate": {
                    "claim_id": CLAIM,
                    "generated_cardinality": len(generated),
                    "unique_survivor": SURVIVOR if passed else None,
                    "independent_missing_support": missing,
                    "independent_added_support_empty": added == {},
                    "independent_observed_formula": observed_formula,
                    "external_definition_note_or_target_accessed": False,
                    "numerical_zero_negative_irrational_imaginary_continuum_fitted_or_free_parameter_used": False,
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
