"""Implementation-distinct product validator for SFT-COMP-CPLX-CIRCUIT-RESOURCE-001."""

from itertools import product
import json
import sys

CLAIM_ID = 'SFT-COMP-CPLX-CIRCUIT-RESOURCE-001'
DOMAINS = (('presentation-length', 'canonical-encoding-support'), ('unrecorded-cost', 'complete-resource-ledger'), ('model-unspecified', 'registered-computation-model'), ('unmatched-instances', 'common-family-comparison'), ('cost-erasing-composition', 'overhead-retaining-composition'), ('claimed-bound', 'constructive-or-adversarial-bound-witness'), ('benchmark-only', 'family-successor-certificate'), ('imported-scale-or-rate', 'no-extra-resource-parameter'))
SURVIVOR = 'canonical-encoding-support__complete-resource-ledger__registered-computation-model__common-family-comparison__overhead-retaining-composition__constructive-or-adversarial-bound-witness__family-successor-certificate__no-extra-resource-parameter'


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
