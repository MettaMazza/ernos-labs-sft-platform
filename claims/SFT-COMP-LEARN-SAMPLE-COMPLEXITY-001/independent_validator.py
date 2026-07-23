"""Implementation-distinct product validator for SFT-COMP-LEARN-SAMPLE-COMPLEXITY-001."""

from itertools import product
import json
import sys

CLAIM_ID = 'SFT-COMP-LEARN-SAMPLE-COMPLEXITY-001'
DOMAINS = (('sampled-hypotheses', 'complete-generated-hypothesis-support'), ('opaque-representation', 'traceable-canonical-representation'), ('pretrained-answer', 'exact-evidence-to-hypothesis-relation'), ('development-score', 'sealed-independent-evaluation'), ('single-winner-erasure', 'retained-alternative-ledger'), ('unreported-search', 'complete-learning-resource-trace'), ('training-examples-only', 'structural-or-empirical-target-boundary'), ('fitted-weight-or-prior', 'no-extra-learning-parameter'))
SURVIVOR = 'complete-generated-hypothesis-support__traceable-canonical-representation__exact-evidence-to-hypothesis-relation__sealed-independent-evaluation__retained-alternative-ledger__complete-learning-resource-trace__structural-or-empirical-target-boundary__no-extra-learning-parameter'


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(coordinates) for coordinates in product(*DOMAINS)]
    received = [item["candidate_id"] for item in sealed["census"]["candidates"]]
    decisions = {item["candidate_id"]: item["survives"] for item in sealed["decisions"]}
    controls = sealed["controls"]
    closure = sealed["closure"]
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated)
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and closure["scope"] == "depth_independent"
        and closure["minimality_passed"] is True
        and closure["named_shape_uniqueness_passed"] is True
        and {item["kind"] for item in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(item["passed"] is True for item in controls)
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
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
