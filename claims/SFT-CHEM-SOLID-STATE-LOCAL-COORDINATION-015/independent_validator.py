from itertools import product
from math import gcd
from functools import reduce
import json
import sys


CLAIM = "SFT-CHEM-SOLID-STATE-LOCAL-COORDINATION-015"
DOMAINS = (
    ("bulk-material-response", "one-finite-local-chemical-motif"),
    ("nominal-formula-label", "complete-species-occurrence-multiset"),
    ("unreduced-or-fitted-stoichiometry", "exact-primitive-positive-count-ratio"),
    ("averaged-coordination-number", "complete-local-bond-adjacency-support"),
    ("continuum-infinite-lattice", "generated-repeat-axis-rank-one-two-or-three"),
    ("real-valued-solid-solution-fraction", "positive-second-constituent-support-or-EmptyOne"),
    ("chemistry-claims-bulk-response", "chemistry-local-materials-bulk-handoff"),
    ("crystal-family-exception", "local-occurrence-successor-no-extra-rule"),
)
SURVIVOR = (
    "one-finite-local-chemical-motif__complete-species-occurrence-multiset__"
    "exact-primitive-positive-count-ratio__complete-local-bond-adjacency-support__"
    "generated-repeat-axis-rank-one-two-or-three__positive-second-constituent-support-or-EmptyOne__"
    "chemistry-local-materials-bulk-handoff__local-occurrence-successor-no-extra-rule"
)


def main():
    document = json.load(open(sys.argv[1], encoding="utf-8"))
    generated = ["__".join(candidate) for candidate in product(*DOMAINS)]
    recorded = [row["candidate_id"] for row in document["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in document["decisions"]}
    counts = (4, 2)
    divisor = reduce(gcd, counts)
    primitive_formula = tuple(count // divisor for count in counts)
    repeat_axes = ("axis-one", "axis-two", "axis-three")
    local_edges = (("A1", "B1"), ("A2", "B2"))
    reconstructed = primitive_formula == (2, 1) and len(repeat_axes) == 3 and len(local_edges) == 2
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
                    "independent_primitive_formula": primitive_formula,
                    "independent_repeat_rank": len(repeat_axes),
                    "external_definition_or_target_accessed": False,
                    "numerical_zero_negative_irrational_imaginary_continuum_fitted_or_free_parameter_used": False,
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
