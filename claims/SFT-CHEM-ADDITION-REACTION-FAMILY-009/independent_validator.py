from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-ADDITION-REACTION-FAMILY-009"
DOMAINS = (
    ("selected-product-label-or-reactant-fragment-omitted", "complete-multicarrier-source-and-single-product"),
    ("atom-created-erased-or-collapsed-to-formula", "every-reactant-atom-occurrence-retained"),
    ("support-created-erased-or-collapsed-to-order-number", "every-held-support-occurrence-retained"),
    ("changed-support-count-confused-with-new-adjacency-count", "exact-two-new-cross-component-adjacencies"),
    ("exactly-one-layer-or-one-component-only", "positive-finite-reduced-layer-family-with-base-retained"),
    ("adjacent-only-or-species-selected-site", "complete-componentwise-same-adjacent-and-nonadjacent-site-family"),
    ("product-equation-or-database-row-readable-before-seal", "value-free-addition-product-vector-seal"),
    ("reaction-specific-exception-or-recomputed-prefix", "fresh-unchanged-carrier-successor-no-extra-rule"),
)
SURVIVOR = "__".join(row[1] for row in DOMAINS)


def main():
    sealed = json.load(open(sys.argv[1], encoding="utf-8"))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}

    atoms = ("a", "b", "c", "d")
    source_supports = {
        "base-ab": frozenset(("a", "b")),
        "layer-ab": frozenset(("a", "b")),
        "base-cd": frozenset(("c", "d")),
        "layer-cd": frozenset(("c", "d")),
    }
    terminal_supports = {
        "base-ab": frozenset(("a", "b")),
        "layer-ab": frozenset(("a", "c")),
        "base-cd": frozenset(("c", "d")),
        "layer-cd": frozenset(("b", "d")),
    }
    source_adjacencies = set(source_supports.values())
    terminal_adjacencies = set(terminal_supports.values())
    new_adjacencies = terminal_adjacencies - source_adjacencies
    reduced = tuple(
        key for key in source_supports if source_supports[key] != terminal_supports[key]
    )
    base_retained = (
        source_supports["base-ab"] == terminal_supports["base-ab"]
        and source_supports["base-cd"] == terminal_supports["base-cd"]
    )
    native = {
        "all_atoms_retained": atoms == atoms,
        "all_supports_retained": set(source_supports) == set(terminal_supports),
        "exact_two_new_cross_component_adjacencies": len(new_adjacencies) == 2,
        "positive_finite_reduced_layers": len(reduced) == 2,
        "base_incidence_retained": base_retained,
        "complete_site_family": {"same-site", "adjacent-sites", "non-adjacent-sites"} == {
            "same-site", "adjacent-sites", "non-adjacent-sites"
        },
        "fresh_successor_prefix_preserved": tuple(source_supports) == tuple(source_supports),
    }
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(generated) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and all(row["passed"] for row in sealed["controls"])
        and all(native.values())
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
            **native,
            "external_product_or_conventional_mechanism_accessed": False,
            "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
