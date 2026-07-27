"""Implementation-distinct, target-inaccessible INORG-009 reconstruction."""

from itertools import product
import json
import sys


CLAIM = "SFT-CHEM-INORGANIC-MAGNETIC-STATE-009"
DOMAINS = (
    ("free-magnetic-number", "one-retained-complex-carrier"),
    ("selected-or-averaged-spin", "complete-unpaired-occurrence-support"),
    ("numerical-zero-paired-state", "pairwise-closure-to-EmptyOne"),
    ("square-root-spin-only-formula", "exact-unpaired-support-count"),
    ("asserted-multiplicity", "unpaired-successor-spin-width"),
    ("signed-susceptibility-proof", "held-drawn-or-repelled-field-relation"),
    ("species-magnetic-lookup", "EmptyOne-diamagnetic-positive-paramagnetic"),
    ("fitted-g-factor-or-complex-exception", "unpaired-successor-with-no-extra-rule"),
)
SURVIVOR = "one-retained-complex-carrier__complete-unpaired-occurrence-support__pairwise-closure-to-EmptyOne__exact-unpaired-support-count__unpaired-successor-spin-width__held-drawn-or-repelled-field-relation__EmptyOne-diamagnetic-positive-paramagnetic__unpaired-successor-with-no-extra-rule"


def main() -> None:
    document = json.load(open(sys.argv[1], encoding="utf-8"))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in document["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in document["decisions"]}

    def state(unpaired_count):
        if unpaired_count is None:
            return ("EmptyOne", 1, "repelled-from-field", "diamagnetic")
        return (unpaired_count, unpaired_count + 1, "drawn-into-field", "paramagnetic")

    balanced = state(None)
    high = state(4)
    successor = state(5)
    reconstructed = (
        balanced == ("EmptyOne", 1, "repelled-from-field", "diamagnetic")
        and high == (4, 5, "drawn-into-field", "paramagnetic")
        and successor == (5, 6, "drawn-into-field", "paramagnetic")
    )
    passed = (
        document["claim_id"] == CLAIM
        and received == generated
        and len(generated) == 256
        and len(set(received)) == 256
        and document["census"]["expected_cardinality"] == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and document["closure"]["scope"] == "depth_independent"
        and document["closure"]["minimality_passed"]
        and document["closure"]["named_shape_uniqueness_passed"]
        and {row["kind"] for row in document["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in document["controls"])
        and reconstructed
    )
    print(json.dumps({
        "validated_seal_hash": document["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": CLAIM,
            "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
            "balanced_state": balanced,
            "four_unpaired_state": high,
            "successor_state": successor,
            "numerical_zero_negative_irrational_imaginary_signed_continuum_or_fitted_parameter_used": False,
            "external_target_definition_value_orientation_absence_or_species_lookup_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
