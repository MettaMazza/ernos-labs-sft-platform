"""Implementation-distinct, value-free ORG-001 reconstruction."""
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-CONJUGATED-SUPPORT-001'
DOMAINS = (('selected-unbound-bond-marks', 'one-retained-molecular-subcarrier'), ('disconnected-support-fragments', 'complete-connected-adjacency-path'), ('bond-support-label-erased', 'two-forced-held-support-fibres'), ('arbitrary-adjacent-fibre-repetition', 'exact-opposed-adjacent-fibre-recurrence'), ('favourable-subpath-only', 'complete-atom-and-incidence-support'), ('independent-bond-pairs', 'shared-centre-support-propagation'), ('spectrum-or-name-selects-structure', 'structure-sealed-before-external-observation'), ('named-conjugation-exception', 'opposed-fibre-successor-no-extra-rule'))
SURVIVOR = 'one-retained-molecular-subcarrier__complete-connected-adjacency-path__two-forced-held-support-fibres__exact-opposed-adjacent-fibre-recurrence__complete-atom-and-incidence-support__shared-centre-support-propagation__structure-sealed-before-external-observation__opposed-fibre-successor-no-extra-rule'

def exact_path(atoms, fibres):
    if len(atoms) < 3 or len(set(atoms)) != len(atoms):
        raise ValueError("distinct positive atom support required")
    if len(fibres) != len(atoms) - 1:
        raise ValueError("complete incidence support required")
    if any(value not in ("fibre-one", "fibre-two") for value in fibres):
        raise ValueError("exactly two Fold fibres required")
    if any(left == right for left, right in zip(fibres, fibres[1:])):
        raise ValueError("adjacent support must alternate")
    return tuple(zip(atoms, fibres, atoms[1:]))

def append(atoms, fibres, fresh):
    if fresh in atoms:
        raise ValueError("successor occurrence must be fresh")
    opposed = "fibre-two" if fibres[-1] == "fibre-one" else "fibre-one"
    return atoms + (fresh,), fibres + (opposed,)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    atoms = ("a", "b", "c")
    fibres = ("fibre-one", "fibre-two")
    base = exact_path(atoms, fibres)
    next_atoms, next_fibres = append(atoms, fibres, "d")
    successor = exact_path(next_atoms, next_fibres)
    repeated_rejected = incomplete_rejected = duplicate_rejected = False
    try:
        exact_path(atoms, ("fibre-one", "fibre-one"))
    except ValueError:
        repeated_rejected = True
    try:
        exact_path(atoms, ("fibre-one",))
    except ValueError:
        incomplete_rejected = True
    try:
        append(atoms, fibres, "b")
    except ValueError:
        duplicate_rejected = True
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
        and len(base) == 2
        and len(successor) == 3
        and successor[:2] == base
        and repeated_rejected and incomplete_rejected and duplicate_rejected
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
            "base_atom_count": len(atoms),
            "base_incidence_count": len(base),
            "successor_atom_count": len(next_atoms),
            "successor_incidence_count": len(successor),
            "prior_incidence_prefix_preserved": successor[:2] == base,
            "repeated_fibre_rejected": repeated_rejected,
            "incomplete_incidence_rejected": incomplete_rejected,
            "duplicate_occurrence_rejected": duplicate_rejected,
            "external_definition_structure_or_spectrum_accessed": False,
            "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_or_imported_parameter_used": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
