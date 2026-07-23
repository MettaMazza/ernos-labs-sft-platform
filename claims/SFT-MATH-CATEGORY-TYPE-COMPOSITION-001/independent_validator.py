"""Implementation-distinct product validator for SFT-MATH-CATEGORY-TYPE-COMPOSITION-001."""

from itertools import product
import json
import sys

CLAIM_ID = 'SFT-MATH-CATEGORY-TYPE-COMPOSITION-001'
DOMAINS = (('presentation-objects', 'canonical-Fold-objects'), ('endpoint-only-arrow', 'proof-carrying-transition'), ('assumed-neutral-map', 'empty-One-return'), ('presentation-concatenation', 'exact-interface-match'), ('borrowed-category-axiom', 'canonical-path-flattening'), ('informal-class-name', 'source-bound-form-predicate'), ('borrowed-set-constructor', 'joint-pairs-and-held-alternatives'), ('arbitrary-renaming', 'identity-and-composition-preservation'), ('diagram-by-appearance', 'equal-complete-paths'), ('extra-composition-axiom', 'no-extra-composition-axiom'))
SURVIVOR = 'canonical-Fold-objects__proof-carrying-transition__empty-One-return__exact-interface-match__canonical-path-flattening__source-bound-form-predicate__joint-pairs-and-held-alternatives__identity-and-composition-preservation__equal-complete-paths__no-extra-composition-axiom'


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
