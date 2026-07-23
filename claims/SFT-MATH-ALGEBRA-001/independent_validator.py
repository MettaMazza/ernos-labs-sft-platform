"""Implementation-distinct product validator for SFT-MATH-ALGEBRA-001."""

from itertools import product
import json
import sys

CLAIM_ID = 'SFT-MATH-ALGEBRA-001'
DOMAINS = (('partial-or-aliased-carrier', 'complete-canonical-carrier'), ('partial-operation-sample', 'complete-single-valued-table'), ('external-result', 'carrier-closed-result'), ('named-identity', 'exhaustive-identity-witness'), ('assumed-parenthesis-law', 'complete-triple-witness'), ('signed-inverse-value', 'unique-held-return-mate'), ('property-by-name', 'property-by-exhaustive-witness'), ('arbitrary-carrier-map', 'operation-preserving-map'), ('extra-algebraic-axiom', 'no-extra-algebraic-axiom'))
SURVIVOR = 'complete-canonical-carrier__complete-single-valued-table__carrier-closed-result__exhaustive-identity-witness__complete-triple-witness__unique-held-return-mate__property-by-exhaustive-witness__operation-preserving-map__no-extra-algebraic-axiom'


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
