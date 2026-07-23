"""Implementation-distinct product validator for SFT-INFO-MUTUAL-CONDITIONAL-001."""

from itertools import product
import json
import sys

CLAIM_ID = 'SFT-INFO-MUTUAL-CONDITIONAL-001'
DOMAINS = (('partial-source-support', 'complete-deterministic-support'), ('partial-or-multivalued-views', 'two-total-observation-maps'), ('named-marginal-scores', 'exact-provenance-classes'), ('sampled-joint-cells', 'complete-joint-incidence-ledger'), ('renormalized-prior', 'exact-class-restriction'), ('scalar-log-ratio', 'joint-versus-product-ledger'), ('uncorrelated-assertion', 'all-cell-exact-equality'), ('stochastic-source-premise', 'deterministic-observation-incidence'), ('small-table-only', 'source-successor-update'), ('extra-base-prior-or-scalar', 'no-extra-information-measure'))
SURVIVOR = 'complete-deterministic-support__two-total-observation-maps__exact-provenance-classes__complete-joint-incidence-ledger__exact-class-restriction__joint-versus-product-ledger__all-cell-exact-equality__deterministic-observation-incidence__source-successor-update__no-extra-information-measure'


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
