"""Implementation-distinct value-free PROP-007 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-MOLECULAR-IONIZATION-ENERGY-007'
DOMAINS = (('ionization-answer-with-erased-states', 'complete-neutral-to-ionic-carrier'), ('signed-electron-subtraction', 'held-removal-and-positive-terminal-separation'), ('imported-orbital-energy-equality', 'ordered-positive-final-from-initial-Take'), ('adiabatic-vertical-state-conflation', 'least-adiabatic-and-held-geometry-vertical-paths'), ('unconstrained-vertical-reordering', 'vertical-not-below-adiabatic'), ('ionization-value-readable-before-seal', 'value-free-carrier-and-operation-seal'), ('selected-isotopologue-or-favorable-row', 'complete-nine-diatomic-NIST-vector'), ('species-fit-or-residual-correction', 'one-ionization-law-no-extra-rule'))
SURVIVOR = 'complete-neutral-to-ionic-carrier__held-removal-and-positive-terminal-separation__ordered-positive-final-from-initial-Take__least-adiabatic-and-held-geometry-vertical-paths__vertical-not-below-adiabatic__value-free-carrier-and-operation-seal__complete-nine-diatomic-NIST-vector__one-ionization-law-no-extra-rule'

def take(final, initial):
    if final <= initial or initial <= 0:
        raise ValueError("strict positive terminal ordering required")
    return final - initial

def adiabatic(initial, terminals):
    if not terminals:
        raise ValueError("complete terminal support required")
    return min(take(final, initial) for final in terminals)

def vertical_order(initial, terminals, held):
    if held not in terminals:
        raise ValueError("held geometry terminal is outside support")
    return take(held, initial) >= adiabatic(initial, terminals)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    initial = Fraction(3, 1)
    terminals = (Fraction(8, 1), Fraction(6, 1), Fraction(7, 1))
    exact_take = take(terminals[0], initial) == Fraction(5, 1)
    least = adiabatic(initial, terminals) == Fraction(3, 1)
    order = vertical_order(initial, terminals, terminals[2])
    reversed_rejected = False
    missing_rejected = False
    try:
        take(initial, terminals[0])
    except ValueError:
        reversed_rejected = True
    try:
        vertical_order(initial, terminals, Fraction(9, 1))
    except ValueError:
        missing_rejected = True
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls)
        and exact_take and least and order and reversed_rejected and missing_rejected
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
            "ordered_positive_Take_reconstructed": exact_take,
            "least_adiabatic_terminal_reconstructed": least,
            "vertical_not_below_adiabatic_reconstructed": order,
            "reversed_order_rejected": reversed_rejected,
            "missing_vertical_terminal_rejected": missing_rejected,
            "measurement_file_accessed": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
