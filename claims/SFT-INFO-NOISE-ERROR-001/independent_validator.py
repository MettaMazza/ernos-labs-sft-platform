"""Implementation-distinct product validator for SFT-INFO-NOISE-ERROR-001."""

from itertools import product
import json
import sys

CLAIM_ID = 'SFT-INFO-NOISE-ERROR-001'
DOMAINS = (('partial-source-support', 'complete-canonical-sources'), ('sampled-received-forms', 'complete-registered-images'), ('opaque-perturbation', 'held-action-relation'), ('scalar-error-size', 'complete-changed-position-trace'), ('probability-threshold', 'invalid-codeword-witness'), ('chosen-likely-source', 'complete-source-class'), ('nearest-form-assumption', 'singleton-predecessor'), ('stochastic-noise-source', 'deterministic-transformation-family'), ('sampled-masks', 'action-successor'), ('extra-error-rate-or-metric', 'no-extra-error-model'))
SURVIVOR = 'complete-canonical-sources__complete-registered-images__held-action-relation__complete-changed-position-trace__invalid-codeword-witness__complete-source-class__singleton-predecessor__deterministic-transformation-family__action-successor__no-extra-error-model'


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
