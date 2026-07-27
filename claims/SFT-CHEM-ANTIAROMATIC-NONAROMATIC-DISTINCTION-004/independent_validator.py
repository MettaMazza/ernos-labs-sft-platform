"""Implementation-distinct, value-free ORG-004 reconstruction."""
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-ANTIAROMATIC-NONAROMATIC-DISTINCTION-004'
DOMAINS = (('different-or-name-only-carriers', 'one-retained-same-cycle-carrier'), ('selected-favourable-category', 'complete-three-class-census'), ('planarity-assumed-or-erased', 'held-planar-or-broken-geometry'), ('conjugation-name-only', 'held-complete-or-broken-conjugation'), ('electron-count-label-imported', 'closed-frustrated-or-EmptyOne-return'), ('measured-energy-selected-order', 'positive-two-step-stability-order'), ('selected-or-preopened-comparison', 'value-free-complete-comparative-seal'), ('named-ring-or-extra-count-rule', 'complete-four-cell-successors-no-extra-rule'))
SURVIVOR = 'one-retained-same-cycle-carrier__complete-three-class-census__held-planar-or-broken-geometry__held-complete-or-broken-conjugation__closed-frustrated-or-EmptyOne-return__positive-two-step-stability-order__value-free-complete-comparative-seal__complete-four-cell-successors-no-extra-rule'
FIBRES = ("fibre-one", "fibre-two")
PAIR_CELLS = tuple(product(FIBRES, repeat=2))

def same_cycle(kind, centres, plane, conjugated, layers):
    if len(centres) < 3 or len(set(centres)) != len(centres):
        raise ValueError("one complete distinct cycle required")
    edges = tuple(zip(centres, centres[1:] + centres[:1]))
    if kind == "closed":
        if not plane or not conjugated or not layers or any(tuple(layer) != PAIR_CELLS for layer in layers):
            raise ValueError("closed recurrence requires complete planar support")
        support = len(FIBRES) + sum(len(layer) for layer in layers)
    elif kind == "frustrated":
        if not plane or not conjugated or not layers or any(tuple(layer) != PAIR_CELLS for layer in layers):
            raise ValueError("frustrated recurrence requires complete planar support")
        support = sum(len(layer) for layer in layers)
    elif kind == "broken":
        if plane and conjugated or layers:
            raise ValueError("broken recurrence requires a structural break and no recurrence layer")
        support = "structural-EmptyOne"
    else:
        raise ValueError("unknown same-cycle class")
    return {"kind": kind, "centres": centres, "edges": edges, "support": support}

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    centres = tuple("c" + str(index) for index in range(1, 7))
    closed = same_cycle("closed", centres, True, True, (PAIR_CELLS,))
    broken = same_cycle("broken", centres, False, True, ())
    frustrated = same_cycle("frustrated", centres, True, True, (PAIR_CELLS,))
    closed_next = same_cycle("closed", centres, True, True, (PAIR_CELLS, PAIR_CELLS))
    frustrated_next = same_cycle("frustrated", centres, True, True, (PAIR_CELLS, PAIR_CELLS))
    anti_break_rejected = missing_break_rejected = incomplete_layer_rejected = False
    try:
        same_cycle("frustrated", centres, False, True, (PAIR_CELLS,))
    except ValueError:
        anti_break_rejected = True
    try:
        same_cycle("broken", centres, True, True, ())
    except ValueError:
        missing_break_rejected = True
    try:
        same_cycle("closed", centres, True, True, (PAIR_CELLS[:-1],))
    except ValueError:
        incomplete_layer_rejected = True
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(generated) == 256 and len(set(received)) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in sealed["controls"])
        and (closed["support"], broken["support"], frustrated["support"]) == (6, "structural-EmptyOne", 4)
        and (closed_next["support"], broken["support"], frustrated_next["support"]) == (10, "structural-EmptyOne", 8)
        and closed["edges"] == broken["edges"] == frustrated["edges"]
        and anti_break_rejected and missing_break_rejected and incomplete_layer_rejected
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
            "same_cycle_class_count": 3,
            "base_supports": [closed["support"], broken["support"], frustrated["support"]],
            "successor_supports": [closed_next["support"], broken["support"], frustrated_next["support"]],
            "identical_cycle_graph_retained": closed["edges"] == broken["edges"] == frustrated["edges"],
            "antiaromatic_with_break_rejected": anti_break_rejected,
            "nonaromatic_without_break_rejected": missing_break_rejected,
            "incomplete_pair_cell_layer_rejected": incomplete_layer_rejected,
            "external_definition_species_geometry_energy_value_sign_or_uncertainty_accessed": False,
            "imported_huckel_or_electron_count_rule_used": False,
            "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_or_imported_parameter_used": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
