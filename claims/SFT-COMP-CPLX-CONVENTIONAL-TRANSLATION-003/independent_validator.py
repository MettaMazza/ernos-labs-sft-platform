"""Implementation-distinct product validator for SFT-COMP-CPLX-CONVENTIONAL-TRANSLATION-003."""

from itertools import product
import json
import sys


CLAIM_ID = "SFT-COMP-CPLX-CONVENTIONAL-TRANSLATION-003"
DOMAINS = (
    ("sampled-external-instances", "complete-registered-external-family"),
    ("partial-or-colliding-encoding", "total-bijective-source-bound-encoding"),
    ("asserted-verdict-correspondence", "exact-bidirectional-verdict-preservation"),
    ("terminal-result-only", "complete-stepwise-trace-translation"),
    ("one-way-or-unsound-certificate-map", "sound-complete-bidirectional-certificate-map"),
    ("unmatched-size-and-cost-carriers", "explicit-common-size-polynomial-overhead"),
    ("fixed-depth-examples", "prepend-label-translation-successor"),
    ("arbitrary-conventional-p-equals-np", "conditional-family-transport-only"),
)
SURVIVOR = "complete-registered-external-family__total-bijective-source-bound-encoding__exact-bidirectional-verdict-preservation__complete-stepwise-trace-translation__sound-complete-bidirectional-certificate-map__explicit-common-size-polynomial-overhead__prepend-label-translation-successor__conditional-family-transport-only"


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
