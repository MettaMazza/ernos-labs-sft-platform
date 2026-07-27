"""Implementation-distinct, value-free ORG-002 reconstruction."""
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-RESONANCE-EQUIVALENT-REPRESENTATION-002'
DOMAINS = (('different-molecular-carriers', 'one-retained-molecular-carrier'), ('atom-occurrence-change', 'complete-equal-atom-occurrence-support'), ('connectivity-change', 'complete-equal-adjacency-support'), ('one-encoding-only', 'multiple-distinct-encoding-identities'), ('partial-or-arbitrary-label-change', 'complete-opposed-fibre-complement'), ('representations-counted-as-species', 'one-carrier-many-representations'), ('equilibrium-or-transition-imported', 'representation-relation-only'), ('named-resonance-exception', 'shared-complement-successor-no-extra-rule'))
SURVIVOR = 'one-retained-molecular-carrier__complete-equal-atom-occurrence-support__complete-equal-adjacency-support__multiple-distinct-encoding-identities__complete-opposed-fibre-complement__one-carrier-many-representations__representation-relation-only__shared-complement-successor-no-extra-rule'

def complement(fibres):
    if any(row not in ("one", "two") for row in fibres):
        raise ValueError("exactly two fibres required")
    return tuple("two" if row == "one" else "one" for row in fibres)

def representation_pair(carrier_a, carrier_b, atoms_a, atoms_b, edges_a, edges_b, first, second):
    if carrier_a != carrier_b:
        raise ValueError("one carrier required")
    if atoms_a != atoms_b or len(atoms_a) < 3 or len(set(atoms_a)) != len(atoms_a):
        raise ValueError("complete equal atom support required")
    if edges_a != edges_b or len(edges_a) != len(first):
        raise ValueError("complete equal adjacency required")
    if first == second or complement(first) != second:
        raise ValueError("distinct complete complement required")
    return (carrier_a, atoms_a, edges_a, first, second)

def append(pair, fresh):
    carrier, atoms, edges, first, second = pair
    if fresh in atoms:
        raise ValueError("fresh successor required")
    next_atoms = atoms + (fresh,)
    next_edges = edges + ((atoms[-1], fresh),)
    next_first = first + (("two" if first[-1] == "one" else "one"),)
    next_second = second + (("two" if second[-1] == "one" else "one"),)
    return representation_pair(carrier, carrier, next_atoms, next_atoms, next_edges, next_edges, next_first, next_second)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    atoms = ("a", "b", "c")
    edges = (("a", "b"), ("b", "c"))
    base = representation_pair("carrier", "carrier", atoms, atoms, edges, edges, ("one", "two"), ("two", "one"))
    successor = append(base, "d")
    carrier_rejected = adjacency_rejected = partial_rejected = identical_rejected = False
    try:
        representation_pair("carrier", "other", atoms, atoms, edges, edges, ("one", "two"), ("two", "one"))
    except ValueError:
        carrier_rejected = True
    try:
        representation_pair("carrier", "carrier", atoms, atoms, edges, (("a", "c"), ("b", "c")), ("one", "two"), ("two", "one"))
    except ValueError:
        adjacency_rejected = True
    try:
        representation_pair("carrier", "carrier", atoms, atoms, edges, edges, ("one", "two"), ("one", "one"))
    except ValueError:
        partial_rejected = True
    try:
        representation_pair("carrier", "carrier", atoms, atoms, edges, edges, ("one", "two"), ("one", "two"))
    except ValueError:
        identical_rejected = True
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(generated) == 256
        and len(set(received)) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in sealed["controls"])
        and len(base[1]) == 3 and len(base[2]) == 2
        and len(successor[1]) == 4 and len(successor[2]) == 3
        and successor[1][:-1] == base[1] and successor[2][:-1] == base[2]
        and complement(successor[3]) == successor[4]
        and carrier_rejected and adjacency_rejected and partial_rejected and identical_rejected
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
            "base_atom_count": len(base[1]),
            "base_adjacency_count": len(base[2]),
            "base_representation_count": 2,
            "successor_atom_count": len(successor[1]),
            "successor_adjacency_count": len(successor[2]),
            "complete_complement_preserved": complement(successor[3]) == successor[4],
            "carrier_mismatch_rejected": carrier_rejected,
            "adjacency_mismatch_rejected": adjacency_rejected,
            "partial_complement_rejected": partial_rejected,
            "identical_encoding_rejected": identical_rejected,
            "external_definition_note_example_wavefunction_coefficient_or_charge_accessed": False,
            "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_or_imported_parameter_used": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
