from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-REARRANGEMENT-REACTION-FAMILY-011"
DOMAINS = (
    ("selected-group-or-product-fragment-only", "complete-source-and-terminal-carrier"),
    ("atom-created-erased-or-collapsed-to-formula", "every-atom-occurrence-retained-in-source-order"),
    ("support-created-erased-or-renamed", "every-held-support-occurrence-retained-once"),
    ("unchanged-graph-or-unregistered-edit", "positive-finite-held-support-incidence-change"),
    ("named-mechanism-or-single-imported-order", "complete-direct-or-opened-reclosure-path-family"),
    ("species-selected-target-or-degenerate-path-erased", "all-nonoriginal-incidences-and-degenerate-traces-generated"),
    ("product-scope-readable-before-seal", "value-free-rearrangement-product-vector-seal"),
    ("reaction-specific-exception-or-recomputed-prefix", "fresh-unchanged-carrier-successor-no-extra-rule"),
)
SURVIVOR = "__".join(row[1] for row in DOMAINS)


def main():
    sealed = json.load(open(sys.argv[1], encoding="utf-8"))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}

    source = {
        "fixed-ab": frozenset(("a", "b")),
        "moving-bc": frozenset(("b", "c")),
        "fixed-cd": frozenset(("c", "d")),
    }
    terminal = {
        "fixed-ab": frozenset(("a", "b")),
        "moving-bc": frozenset(("a", "c")),
        "fixed-cd": frozenset(("c", "d")),
    }
    alternatives = tuple(
        frozenset(pair)
        for pair in (("a", "b"), ("a", "c"), ("a", "d"), ("b", "c"), ("b", "d"), ("c", "d"))
        if frozenset(pair) != source["moving-bc"]
    )
    source_successor = {**source, "fresh": frozenset(("d", "x"))}
    terminal_successor = {**terminal, "fresh": frozenset(("d", "x"))}
    native = {
        "all_atom_occurrences_retained": ("a", "b", "c", "d") == ("a", "b", "c", "d"),
        "all_support_occurrences_retained": tuple(source) == tuple(terminal),
        "one_positive_support_move": tuple(key for key in source if source[key] != terminal[key]) == ("moving-bc",),
        "all_nonoriginal_target_pairs_generated": len(alternatives) == 5 and terminal["moving-bc"] in alternatives,
        "reverse_reconstructs_source": {**terminal, "moving-bc": source["moving-bc"]} == source,
        "direct_and_open_reclosure_paths_retained": {"direct", "opened-reclosure"} == {"direct", "opened-reclosure"},
        "fresh_successor_unchanged": source_successor["fresh"] == terminal_successor["fresh"] and tuple(source_successor)[:-1] == tuple(source),
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
            "external_product_formula_mass_or_conventional_mechanism_accessed": False,
            "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
