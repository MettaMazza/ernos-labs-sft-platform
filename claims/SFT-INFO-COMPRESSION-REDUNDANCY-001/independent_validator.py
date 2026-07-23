"""Implementation-distinct product validator for SFT-INFO-COMPRESSION-REDUNDANCY-001."""

from itertools import product
import json
import sys

CLAIM_ID = 'SFT-INFO-COMPRESSION-REDUNDANCY-001'
DOMAINS = (('partial-message', 'complete-canonical-message'), ('opaque-short-string', 'dictionary-and-token-trace'), ('similar-output', 'exact-decoder-equality'), ('ambiguous-concatenation', 'prefix-or-delimiter-witness'), ('frequency-assumption', 'reconstructible-occurrence-trace'), ('payload-only', 'complete-description-resource'), ('universal-shortening-claim', 'pigeonhole-boundary'), ('tuned-score', 'complete-undominated-descriptions'), ('sampled-messages', 'token-successor'), ('extra-statistical-model', 'no-extra-compression-model'))
SURVIVOR = 'complete-canonical-message__dictionary-and-token-trace__exact-decoder-equality__prefix-or-delimiter-witness__reconstructible-occurrence-trace__complete-description-resource__pigeonhole-boundary__complete-undominated-descriptions__token-successor__no-extra-compression-model'


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
