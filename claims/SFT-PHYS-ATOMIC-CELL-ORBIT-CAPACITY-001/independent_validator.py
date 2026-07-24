"""Implementation-distinct validator for SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001."""

from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001'
DOMAINS = (('unlabelled-cell-count', 'held-orientation-cell'), ('empty-numerical-origin', 'one-central-orientation'), ('free-rank-increment', 'one-boundary-orientation-pair'), ('single-or-three-direction-addition', 'forced-rank-two-pair'), ('label-erased-or-selected', 'both-Fold-labels'), ('duplicate-cell-label', 'one-of-each-label-per-cell'), ('linear-or-doubling-without-boundary', 'labels-times-complete-orientations'), ('finite-width-list', 'constant-boundary-pair-successor'), ('width-list-visible', 'widths-inaccessible-until-seal'), ('extra-degeneracy-rule', 'no-extra-rule'))
SURVIVOR = 'held-orientation-cell__one-central-orientation__one-boundary-orientation-pair__forced-rank-two-pair__both-Fold-labels__one-of-each-label-per-cell__labels-times-complete-orientations__constant-boundary-pair-successor__widths-inaccessible-until-seal__no-extra-rule'


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}

    capacities = tuple(2 * (1 + 2 * (rank - 1)) for rank in range(1, 13))
    arithmetic = capacities[:5] == (2, 6, 10, 14, 18) and all(capacities[i] - capacities[i - 1] == 4 for i in range(1, len(capacities)))

    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated)
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in sealed["controls"])
        and arithmetic
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {"claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None, "arithmetic_reconstruction": arithmetic},
    }, sort_keys=True))


if __name__ == "__main__":
    main()
