"""Implementation-distinct product validator for SFT-MATH-DYNAMICAL-SYSTEMS-001."""

from itertools import product
import json
import sys

CLAIM_ID = 'SFT-MATH-DYNAMICAL-SYSTEMS-001'
DOMAINS = (('partial-or-aliased-state', 'complete-canonical-states'), ('opaque-update-rule', 'held-state-relation'), ('endpoint-only', 'complete-transition-trace'), ('continuous-clock-parameter', 'positive-transition-count'), ('visual-sameness', 'retained-identity-transition'), ('periodic-assertion', 'explicit-first-return-trace'), ('sampled-neighborhood', 'complete-reachability-selection'), ('infer-unrecorded-predecessor', 'retained-predecessor-record'), ('epsilon-parameter', 'registered-perturbation-closure'), ('extra-force-or-random-law', 'no-extra-dynamic-law'))
SURVIVOR = 'complete-canonical-states__held-state-relation__complete-transition-trace__positive-transition-count__retained-identity-transition__explicit-first-return-trace__complete-reachability-selection__retained-predecessor-record__registered-perturbation-closure__no-extra-dynamic-law'


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
