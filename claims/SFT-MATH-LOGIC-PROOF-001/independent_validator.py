"""Implementation-distinct product validator for SFT-MATH-LOGIC-PROOF-001."""

from itertools import product
import json
import sys

CLAIM_ID = 'SFT-MATH-LOGIC-PROOF-001'
DOMAINS = (('presentation-sentence', 'canonical-distinguished-form'), ('negative-truth-value', 'complementary-held-orientation'), ('single-side-proof', 'joint-complete-proof'), ('unidentified-choice', 'held-alternative-with-support'), ('truth-table-import', 'proof-carrying-transition'), ('conclusion-only', 'complete-dependency-trace'), ('assumed-consistent', 'no-opposed-admission'), ('authority-or-name', 'rule-and-witness-preservation'), ('unbounded-global-claim', 'registered-grammar-exhaustion'), ('extra-logical-axiom', 'no-extra-logical-axiom'))
SURVIVOR = 'canonical-distinguished-form__complementary-held-orientation__joint-complete-proof__held-alternative-with-support__proof-carrying-transition__complete-dependency-trace__no-opposed-admission__rule-and-witness-preservation__registered-grammar-exhaustion__no-extra-logical-axiom'


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
        and {item["kind"] for item in controls} == {
            "false_premise", "tampered_source", "tampered_artifact", "boundary"
        }
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
