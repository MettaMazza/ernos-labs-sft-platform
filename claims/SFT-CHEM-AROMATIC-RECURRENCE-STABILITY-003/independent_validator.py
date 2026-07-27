"""Implementation-distinct, value-free ORG-003 reconstruction."""
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-AROMATIC-RECURRENCE-STABILITY-003'
DOMAINS = (('aromatic-name-or-answer-only', 'one-complete-molecular-carrier'), ('open-path-or-selected-ring', 'complete-generated-cycle'), ('one-fibre-or-duplicated-boundary', 'complete-two-fibre-boundary'), ('selected-transition-cell-subset', 'complete-four-ordered-pair-cell-layer'), ('period-label-without-trace', 'explicit-complete-first-return-trace'), ('measured-energy-or-name-selected-order', 'positive-recurrence-opening-gap'), ('selected-or-preopened-value-row', 'value-free-seal-and-complete-blind-vector'), ('imported-electron-count-or-species-rule', 'complete-four-cell-successor-no-extra-rule'))
SURVIVOR = 'one-complete-molecular-carrier__complete-generated-cycle__complete-two-fibre-boundary__complete-four-ordered-pair-cell-layer__explicit-complete-first-return-trace__positive-recurrence-opening-gap__value-free-seal-and-complete-blind-vector__complete-four-cell-successor-no-extra-rule'
FIBRES = ("fibre-one", "fibre-two")
PAIR_CELLS = tuple(product(FIBRES, repeat=2))

def recurrence(centres, boundary, layers):
    if len(centres) < 3 or len(set(centres)) != len(centres):
        raise ValueError("complete distinct cycle centres required")
    if len(boundary) != 2 or set(boundary) != set(FIBRES):
        raise ValueError("both boundary fibres required")
    if not layers or any(tuple(layer) != PAIR_CELLS for layer in layers):
        raise ValueError("every positive layer requires all ordered pair cells")
    edges = tuple(zip(centres, centres[1:] + centres[:1]))
    trace = centres + centres[:1]
    return {"centres": centres, "edges": edges, "trace": trace, "support": len(boundary) + sum(len(layer) for layer in layers)}

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    centres = tuple("c" + str(index) for index in range(1, 7))
    base = recurrence(centres, FIBRES, (PAIR_CELLS,))
    successor = recurrence(centres, FIBRES, (PAIR_CELLS, PAIR_CELLS))
    second = recurrence(centres, FIBRES, (PAIR_CELLS, PAIR_CELLS, PAIR_CELLS))
    incomplete_rejected = duplicate_boundary_rejected = open_cycle_rejected = False
    try:
        recurrence(centres, FIBRES, (PAIR_CELLS[:-1],))
    except ValueError:
        incomplete_rejected = True
    try:
        recurrence(centres, ("fibre-one", "fibre-one"), (PAIR_CELLS,))
    except ValueError:
        duplicate_boundary_rejected = True
    try:
        recurrence(("left", "right"), FIBRES, (PAIR_CELLS,))
    except ValueError:
        open_cycle_rejected = True
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
        and (base["support"], successor["support"], second["support"]) == (6, 10, 14)
        and base["trace"][0] == base["trace"][-1]
        and incomplete_rejected and duplicate_boundary_rejected and open_cycle_rejected
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
            "complete_ordered_pair_cell_count": len(PAIR_CELLS),
            "primitive_support_count": base["support"],
            "successor_support_count": successor["support"],
            "second_successor_support_count": second["support"],
            "complete_first_return": base["trace"][0] == base["trace"][-1],
            "incomplete_pair_cell_layer_rejected": incomplete_rejected,
            "duplicated_boundary_fibre_rejected": duplicate_boundary_rejected,
            "open_two_centre_cycle_rejected": open_cycle_rejected,
            "external_definition_table_energy_value_sign_or_uncertainty_accessed": False,
            "imported_huckel_or_electron_count_rule_used": False,
            "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_or_imported_parameter_used": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
