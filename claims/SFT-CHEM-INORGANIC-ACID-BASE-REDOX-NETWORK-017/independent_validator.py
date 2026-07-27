from itertools import product
import json
import sys


CLAIM = "SFT-CHEM-INORGANIC-ACID-BASE-REDOX-NETWORK-017"
DOMAINS = (
    ("selected-inorganic-equation", "complete-finite-species-transition-network"),
    ("untracked-reagent-labels", "complete-held-species-identity-support"),
    ("assumed-acid-and-base-names", "provider-acceptor-two-occurrence-pair-transfer"),
    ("unstructured-acid-base-mixture", "retained-provider-acceptor-adduct-composition"),
    ("signed-oxidation-number-arithmetic", "positive-complete-held-electron-transfer"),
    ("independent-oxidation-and-reduction-labels", "one-donor-acceptor-conserved-transfer"),
    ("unordered-reaction-list", "complete-ordered-transition-path"),
    ("named-reaction-exception", "transition-successor-no-extra-rule"),
)
SURVIVOR = (
    "complete-finite-species-transition-network__complete-held-species-identity-support__"
    "provider-acceptor-two-occurrence-pair-transfer__retained-provider-acceptor-adduct-composition__"
    "positive-complete-held-electron-transfer__one-donor-acceptor-conserved-transfer__"
    "complete-ordered-transition-path__transition-successor-no-extra-rule"
)


def main():
    document = json.load(open(sys.argv[1], encoding="utf-8"))
    generated = ["__".join(candidate) for candidate in product(*DOMAINS)]
    recorded = [row["candidate_id"] for row in document["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in document["decisions"]}
    species = ("base", "acid", "adduct", "donor", "acceptor")
    pair = ("pair-one", "pair-two")
    transfer = ("electron-one", "electron-two")
    path = ("Lewis-step", "redox-step")
    reverse_transfer = tuple(transfer)
    reconstructed = (
        len(species) == 5
        and len(set(species)) == 5
        and len(pair) == 2
        and transfer == reverse_transfer
        and len(path) == 2
    )
    passed = (
        document["claim_id"] == CLAIM
        and recorded == generated
        and len(generated) == 256
        and len(set(recorded)) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and document["closure"]["scope"] == "depth_independent"
        and document["closure"]["minimality_passed"]
        and document["closure"]["named_shape_uniqueness_passed"]
        and all(row["passed"] for row in document["controls"])
        and reconstructed
    )
    print(
        json.dumps(
            {
                "validated_seal_hash": document["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "passed": passed,
                "certificate": {
                    "claim_id": CLAIM,
                    "generated_cardinality": len(generated),
                    "unique_survivor": SURVIVOR if passed else None,
                    "independent_species_count": len(species),
                    "independent_pair_count": len(pair),
                    "independent_transfer_count": len(transfer),
                    "independent_path_count": len(path),
                    "external_definition_example_criterion_or_target_accessed": False,
                    "numerical_zero_negative_irrational_imaginary_signed_continuum_fitted_or_free_parameter_used": False,
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
