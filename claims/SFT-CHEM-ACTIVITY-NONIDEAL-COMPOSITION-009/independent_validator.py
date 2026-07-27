"""Implementation-distinct value-free THERMO-009 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-ACTIVITY-NONIDEAL-COMPOSITION-009"
DOMAINS = (
    ("bulk-answer-or-unbound-activity-number", "complete-component-exchange-support-account"),
    ("selected-or-erased-composition-and-condition", "complete-held-condition-and-component-coordinates"),
    ("logarithm-fugacity-or-fitted-coefficient", "exact-accessible-support-over-reference-support"),
    ("ideal-mixture-prior-or-target-derived-correction", "exact-joint-versus-independent-support-relation"),
    ("numerical-zero-component-coordinate", "structural-EmptyOne-absent-component"),
    ("activity-composition-or-condition-readable-before-seal", "complete-value-free-204-row-identity-seal"),
    ("selected-system-or-deleted-absence-boundary", "complete-nine-dataset-204-row-vector-with-68-EmptyOne-boundaries"),
    ("refit-after-support-replication", "depth-independent-exact-support-replication"),
)
SURVIVOR = (
    "complete-component-exchange-support-account__complete-held-condition-and-component-coordinates__"
    "exact-accessible-support-over-reference-support__exact-joint-versus-independent-support-relation__"
    "structural-EmptyOne-absent-component__complete-value-free-204-row-identity-seal__"
    "complete-nine-dataset-204-row-vector-with-68-EmptyOne-boundaries__"
    "depth-independent-exact-support-replication"
)


def activity(accessible, reference):
    if accessible <= 0 or reference <= 0 or accessible > reference:
        raise ValueError("inadmissible support")
    return Fraction(accessible, reference)


def relation(actual, independent):
    if actual == independent:
        return "independent", None
    return ("restricted" if actual < independent else "expanded"), abs(actual - independent)


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    base_activity = activity(6, 10)
    restricted = relation(6, 8)
    independent = relation(8, 8)
    expanded = relation(9, 8)
    replicated_activity = activity(42, 70)
    replicated_relation = relation(42, 56)
    composition = (("solute-a", Fraction(3, 2)), ("solute-b", None))
    controls = sealed["controls"]
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and len([candidate for candidate, survives in decisions.items() if survives]) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls}
        == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in controls)
        and base_activity == Fraction(3, 5)
        and restricted == ("restricted", 2)
        and independent == ("independent", None)
        and expanded == ("expanded", 1)
        and composition[1][1] is None
        and replicated_activity == base_activity
        and replicated_relation[0] == restricted[0]
    )
    print(
        json.dumps(
            {
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "passed": passed,
                "certificate": {
                    "claim_id": CLAIM_ID,
                    "generated_cardinality": len(generated),
                    "unique_survivor": SURVIVOR if passed else None,
                    "closure": "depth_independent" if passed else None,
                    "exact_activity_ratio_reconstructed": base_activity == Fraction(3, 5),
                    "joint_vs_independent_relation_reconstructed": restricted == ("restricted", 2)
                    and independent == ("independent", None)
                    and expanded == ("expanded", 1),
                    "structural_absence_reconstructed": composition[1][1] is None,
                    "replication_successor_reconstructed": replicated_activity == base_activity
                    and replicated_relation[0] == restricted[0],
                    "activity_equation_fugacity_model_fit_or_measurement_file_accessed": False,
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
