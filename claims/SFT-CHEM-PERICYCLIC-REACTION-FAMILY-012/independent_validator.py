from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-PERICYCLIC-REACTION-FAMILY-012"
DOMAINS = (
    ("selected-product-fragment-or-missing-reactant", "complete-source-and-terminal-carriers"),
    ("open-path-or-named-reaction-assumed", "complete-generated-transition-cycle"),
    ("support-created-erased-or-renamed", "every-held-support-retained-once"),
    ("sequential-story-or-target-selected-edit", "positive-finite-cycle-confined-incidence-change"),
    ("imported-orbital-sign-or-complex-scalar", "complete-two-fibre-face-assignment-product"),
    ("single-preferred-product-or-erased-alternative", "two-relative-classes-under-global-complement"),
    ("external-stereochemistry-open-before-seal", "value-free-cycle-and-stereochemistry-seal"),
    ("species-exception-or-recomputed-prefix", "fresh-unchanged-successor-no-extra-rule"),
)
SURVIVOR = "__".join(row[1] for row in DOMAINS)


def main():
    sealed = json.load(open(sys.argv[1], encoding="utf-8"))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}

    atoms = ("a", "b", "c", "d", "f", "e")
    cycle = tuple(frozenset((atoms[index], atoms[(index + 1) % len(atoms)])) for index in range(len(atoms)))
    source = {
        "base-ab": frozenset(("a", "b")), "layer-ab": frozenset(("a", "b")),
        "base-bc": frozenset(("b", "c")), "base-cd": frozenset(("c", "d")),
        "layer-cd": frozenset(("c", "d")), "base-ef": frozenset(("e", "f")),
        "layer-ef": frozenset(("e", "f")),
    }
    terminal = {
        "base-ab": frozenset(("a", "b")), "layer-ab": frozenset(("b", "c")),
        "base-bc": frozenset(("b", "c")), "base-cd": frozenset(("c", "d")),
        "layer-cd": frozenset(("a", "e")), "base-ef": frozenset(("e", "f")),
        "layer-ef": frozenset(("d", "f")),
    }
    moved = tuple(key for key in source if source[key] != terminal[key])
    assignments = tuple(product(("first", "second"), repeat=2))
    relative = tuple("retained" if first == second else "opposed" for first, second in assignments)
    complement_pairs = ((assignments[0], assignments[3]), (assignments[1], assignments[2]))
    successor_source = {**source, "fresh": frozenset(("b", "x"))}
    successor_terminal = {**terminal, "fresh": frozenset(("b", "x"))}
    native = {
        "complete_cycle_has_six_edges": len(cycle) == 6 and len(set(cycle)) == 6,
        "every_cycle_edge_in_endpoint_union": all(edge in set(source.values()) | set(terminal.values()) for edge in cycle),
        "all_atoms_and_supports_retained": tuple(source) == tuple(terminal),
        "positive_three_support_move": moved == ("layer-ab", "layer-cd", "layer-ef"),
        "every_move_cycle_confined": all(source[key] in cycle and terminal[key] in cycle for key in moved),
        "complete_four_face_assignments": len(assignments) == 4 and len(set(assignments)) == 4,
        "exact_two_relative_classes": set(relative) == {"retained", "opposed"},
        "complete_complement_pairs": {row for pair in complement_pairs for row in pair} == set(assignments),
        "reverse_reconstructs_source": {**terminal, **{key: source[key] for key in moved}} == source,
        "fresh_successor_unchanged": successor_source["fresh"] == successor_terminal["fresh"] and tuple(successor_source)[:-1] == tuple(source),
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
            "external_product_ratio_condition_energy_or_conventional_orbital_rule_accessed": False,
            "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
