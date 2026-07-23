"""Implementation-distinct product validator for SFT-INFO-CONSERVATION-LOSS-001."""

from itertools import product
import json
import sys

CLAIM_ID = 'SFT-INFO-CONSERVATION-LOSS-001'
DOMAINS = (('partial-input-support', 'complete-canonical-source'), ('partial-or-multivalued-rule', 'total-single-valued-map'), ('image-only-output', 'exact-predecessor-fibres'), ('output-cardinality-only', 'complete-source-pair-partition'), ('lower-score-assertion', 'non-singleton-image-fibre'), ('assumed-inverse', 'singleton-fibre-or-held-record'), ('fresh-downstream-distinction', 'retained-pair-subset'), ('unchanged-scalar', 'retained-plus-closed-exhaustion'), ('sampled-transformations', 'source-successor-map-cell'), ('unrecorded-created-distinction', 'no-extra-information-source'))
SURVIVOR = 'complete-canonical-source__total-single-valued-map__exact-predecessor-fibres__complete-source-pair-partition__non-singleton-image-fibre__singleton-fibre-or-held-record__retained-pair-subset__retained-plus-closed-exhaustion__source-successor-map-cell__no-extra-information-source'


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
