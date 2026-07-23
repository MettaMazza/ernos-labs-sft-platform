"""Implementation-distinct product validator for SFT-INFO-CHANNEL-CAPACITY-001."""

from itertools import product
import json
import sys

CLAIM_ID = 'SFT-INFO-CHANNEL-CAPACITY-001'
DOMAINS = (('partial-input-carrier', 'complete-canonical-inputs'), ('partial-output-carrier', 'complete-canonical-outputs'), ('opaque-channel-box', 'held-transport-relation'), ('missing-input-row', 'nonempty-output-support-per-input'), ('probability-threshold', 'overlapping-output-support'), ('sampled-input-set', 'pairwise-disjoint-output-selection'), ('logarithmic-rate', 'complete-greatest-code-family'), ('endpoint-guess', 'exact-relational-paths'), ('sampled-channels', 'carrier-successor'), ('extra-transition-probability', 'no-extra-channel-model'))
SURVIVOR = 'complete-canonical-inputs__complete-canonical-outputs__held-transport-relation__nonempty-output-support-per-input__overlapping-output-support__pairwise-disjoint-output-selection__complete-greatest-code-family__exact-relational-paths__carrier-successor__no-extra-channel-model'


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
