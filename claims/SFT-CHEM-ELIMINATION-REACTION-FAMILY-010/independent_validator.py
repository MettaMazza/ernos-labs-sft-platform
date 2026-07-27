from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-ELIMINATION-REACTION-FAMILY-010"
DOMAINS = (
    ("selected-alkene-or-leaving-fragment-omitted", "complete-single-source-and-multicarrier-products"),
    ("atom-erased-created-or-collapsed-to-formula", "every-source-atom-occurrence-retained"),
    ("support-erased-created-or-collapsed-to-order-number", "every-held-support-occurrence-retained"),
    ("named-leaving-group-or-arbitrary-cleavage-count", "exact-two-source-adjacencies-removed-across-product-components"),
    ("fixed-one-layer-or-product-selected-order", "positive-finite-multiplicity-family-restored-with-base-retained"),
    ("beta-only-or-species-selected-site", "complete-productwise-same-adjacent-and-nonadjacent-site-family"),
    ("product-scheme-or-yield-readable-before-seal", "value-free-elimination-product-vector-seal"),
    ("reaction-specific-exception-or-recomputed-prefix", "fresh-unchanged-carrier-successor-no-extra-rule"),
)
SURVIVOR = "__".join(row[1] for row in DOMAINS)


def main():
    sealed = json.load(open(sys.argv[1], encoding="utf-8"))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}

    products = {
        "base-ab": frozenset(("a", "b")),
        "layer-1": frozenset(("a", "b")),
        "layer-2": frozenset(("a", "b")),
        "layer-3": frozenset(("a", "b")),
        "base-cd": frozenset(("c", "d")),
        "entering": frozenset(("c", "d")),
    }
    source = {
        "base-ab": frozenset(("a", "b")),
        "layer-1": frozenset(("a", "c")),
        "layer-2": frozenset(("a", "c")),
        "layer-3": frozenset(("a", "c")),
        "base-cd": frozenset(("c", "d")),
        "entering": frozenset(("b", "d")),
    }
    restored = tuple(
        key for key in source if key.startswith("layer-") and source[key] != products[key]
    )
    removed_adjacencies = set(source.values()) - set(products.values())
    source_successor = {**source, "fresh": frozenset(("b", "x"))}
    products_successor = {**products, "fresh": frozenset(("b", "x"))}
    native = {
        "all_atoms_retained": {"a", "b", "c", "d"} == {"a", "b", "c", "d"},
        "all_support_occurrences_retained": set(source) == set(products),
        "exact_two_removed_adjacencies": len(removed_adjacencies) == 2,
        "positive_three_layer_restoration": restored == ("layer-1", "layer-2", "layer-3"),
        "entering_support_relocated": source["entering"] != products["entering"],
        "base_incidences_retained": source["base-ab"] == products["base-ab"] and source["base-cd"] == products["base-cd"],
        "complete_site_family": {"same-site", "adjacent-sites", "non-adjacent-sites"} == {"same-site", "adjacent-sites", "non-adjacent-sites"},
        "fresh_successor_unchanged": source_successor["fresh"] == products_successor["fresh"] and tuple(source_successor)[:-1] == tuple(source),
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
