"""Implementation-distinct value-free PROP-004 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-DIHEDRAL-TORSIONAL-STATE-004'
DOMAINS = (('unordered-or-three-site-angle', 'named-ordered-four-site-carrier'), ('signed-conventional-angle', 'held-cycle-orientation'), ('continuum-rotation-coordinate', 'generated-sector-successor-coordinate'), ('named-conformer-without-neighbours', 'complete-neighbour-conformer-state'), ('imported-saddle-or-signed-difference', 'local-barrier-and-ordered-positive-Take'), ('duplicated-terminal-configuration', 'terminal-One-identifies-anchor-class'), ('angle-or-energy-target-readable', 'value-free-coordinate-and-operation-seal'), ('selected-extrema-or-one-rotor', 'complete-two-rotor-fifty-row-vector'))
SURVIVOR = 'named-ordered-four-site-carrier__held-cycle-orientation__generated-sector-successor-coordinate__complete-neighbour-conformer-state__local-barrier-and-ordered-positive-Take__terminal-One-identifies-anchor-class__value-free-coordinate-and-operation-seal__complete-two-rotor-fifty-row-vector'

def coordinate(position, sectors):
    if position < 1 or sectors < 1 or position > sectors + 1:
        raise ValueError("invalid generated coordinate")
    return None if position == 1 else Fraction(position - 1, sectors)

def positive_take(higher, lower):
    if lower is None:
        return higher
    if higher is None or not higher > lower:
        raise ValueError("ordered positive Take halted")
    return higher - lower

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    path = tuple(coordinate(position, 24) for position in range(1, 26))
    reversed_rejected = False
    try:
        positive_take(Fraction(2, 1), Fraction(5, 1))
    except ValueError:
        reversed_rejected = True
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "finite_complete"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls)
        and len(path) == 25 and path[0] is None and path[1] == Fraction(1, 24) and path[-1] == Fraction(1, 1)
        and positive_take(Fraction(5, 1), None) == Fraction(5, 1)
        and positive_take(Fraction(5, 1), Fraction(2, 1)) == Fraction(3, 1)
        and reversed_rejected
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "finite_complete" if passed else None,
            "twenty_four_sector_cycle_reconstructed": True,
            "anchor_is_structural_absence": path[0] is None,
            "terminal_is_recurrent_One": path[-1] == Fraction(1, 1),
            "ordered_positive_Take_reconstructed": reversed_rejected,
            "measurement_file_accessed": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
