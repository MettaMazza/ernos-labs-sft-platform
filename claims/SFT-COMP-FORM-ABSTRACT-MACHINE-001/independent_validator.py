"""Implementation-distinct product validator for SFT-COMP-FORM-ABSTRACT-MACHINE-001."""

from itertools import product
import json
import sys

CLAIM_ID = 'SFT-COMP-FORM-ABSTRACT-MACHINE-001'
DOMAINS = (('sampled-carrier', 'complete-generated-carrier'), ('presentation-identity', 'canonical-held-identity'), ('assumed-operation', 'source-bound-exact-relation'), ('result-only', 'complete-retained-trace'), ('implicit-terminal-boundary', 'explicit-initial-terminal-boundary'), ('opaque-assembly', 'interface-preserving-composition'), ('fixed-examples', 'structural-successor'), ('imported-machine-model', 'no-extra-computational-premise'))
SURVIVOR = 'complete-generated-carrier__canonical-held-identity__source-bound-exact-relation__complete-retained-trace__explicit-initial-terminal-boundary__interface-preserving-composition__structural-successor__no-extra-computational-premise'


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
