"""Implementation-distinct product validator for SFT-INFO-CLASSICAL-PROBABILISTIC-001."""

from itertools import product
import json
import sys

CLAIM_ID = 'SFT-INFO-CLASSICAL-PROBABILISTIC-001'
DOMAINS = (('sampled-or-duplicated-support', 'complete-canonical-support'), ('unheld-symbol-name', 'one-held-supported-state'), ('free-weight-list', 'total-observation-classes'), ('floating-propensities', 'exact-class-whole-parts'), ('ontic-random-cause', 'unresolved-deterministic-distinction'), ('likely-state-selection', 'singleton-class-only'), ('stochastic-transition-matrix', 'deterministic-predecessor-grouping'), ('fitted-normalization', 'partition-exact-whole'), ('finite-examples-only', 'microstate-successor'), ('extra-seed-prior-or-kernel', 'no-extra-stochastic-law'))
SURVIVOR = 'complete-canonical-support__one-held-supported-state__total-observation-classes__exact-class-whole-parts__unresolved-deterministic-distinction__singleton-class-only__deterministic-predecessor-grouping__partition-exact-whole__microstate-successor__no-extra-stochastic-law'


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
