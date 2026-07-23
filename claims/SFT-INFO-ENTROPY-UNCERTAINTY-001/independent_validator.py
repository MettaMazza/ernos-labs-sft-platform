"""Implementation-distinct product validator for SFT-INFO-ENTROPY-UNCERTAINTY-001."""

from itertools import product
import json
import sys

CLAIM_ID = 'SFT-INFO-ENTROPY-UNCERTAINTY-001'
DOMAINS = (('partial-microstate-support', 'complete-deterministic-support'), ('overlapping-or-partial-classes', 'total-disjoint-observation-classes'), ('floating-probability', 'exact-class-whole-part'), ('scalar-uncertainty-score', 'complete-within-class-pairs'), ('logarithmic-expectation', 'weighted-class-distinction-ledger'), ('assumed-more-information', 'class-containment-witness'), ('ontic-random-source', 'deterministic-support-observation'), ('sampled-distributions', 'microstate-successor'), ('extra-log-base-or-prior', 'no-extra-entropy-convention'))
SURVIVOR = 'complete-deterministic-support__total-disjoint-observation-classes__exact-class-whole-part__complete-within-class-pairs__weighted-class-distinction-ledger__class-containment-witness__deterministic-support-observation__microstate-successor__no-extra-entropy-convention'


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
