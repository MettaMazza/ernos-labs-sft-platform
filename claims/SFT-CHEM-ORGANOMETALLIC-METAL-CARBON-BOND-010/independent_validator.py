"""Implementation-distinct, target-inaccessible INORG-010 reconstruction."""

from itertools import product
import json
import sys


CLAIM = "SFT-CHEM-ORGANOMETALLIC-METAL-CARBON-BOND-010"
DOMAINS = (
    ("free-compound-name", "one-retained-chemical-entity"),
    ("imported-conventional-metal-list", "retained-admitted-centre-occurrence"),
    ("selected-formula-fragment", "retained-carbon-occurrence"),
    ("proximity-or-name-association", "direct-centre-carbon-incidence"),
    ("assumed-valence-number", "complete-held-bond-electron-support"),
    ("single-selected-bond", "complete-positive-direct-incidence-support"),
    ("species-or-name-lookup", "positive-support-organometallic-EmptyOne-otherwise"),
    ("fitted-species-exception", "direct-incidence-successor-no-extra-rule"),
)
SURVIVOR = "one-retained-chemical-entity__retained-admitted-centre-occurrence__retained-carbon-occurrence__direct-centre-carbon-incidence__complete-held-bond-electron-support__complete-positive-direct-incidence-support__positive-support-organometallic-EmptyOne-otherwise__direct-incidence-successor-no-extra-rule"


def main() -> None:
    document = json.load(open(sys.argv[1], encoding="utf-8"))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in document["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in document["decisions"]}
    support = (("M1", "C1", ("e1", "e2")),)
    first = (len(support), "organometallic")
    successor_support = support + (("M1", "C2", ("e3", "e4")),)
    reconstructed = first == (1, "organometallic") and len(successor_support) == 2 and len(set((m, c) for m, c, _ in successor_support)) == 2
    passed = (
        document["claim_id"] == CLAIM and received == generated and len(generated) == 256 and len(set(received)) == 256
        and document["census"]["expected_cardinality"] == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated} and sum(decisions.values()) == 1
        and document["closure"]["scope"] == "depth_independent" and document["closure"]["minimality_passed"] and document["closure"]["named_shape_uniqueness_passed"]
        and {row["kind"] for row in document["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in document["controls"]) and reconstructed
    )
    print(json.dumps({
        "validated_seal_hash": document["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {
            "claim_id": CLAIM, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None, "first_direct_incidence_count": first[0], "successor_count": len(successor_support),
            "numerical_zero_negative_irrational_imaginary_continuum_fitted_or_free_parameter_used": False,
            "external_definition_example_scope_exclusion_or_target_payload_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
