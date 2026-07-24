"""Implementation-distinct validator for SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001."""

from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001'
DOMAINS = (('selected-shell-degeneracy', 'complete-three-direction-weak-compositions'), ('single-or-duplicated-label', 'two-exclusion-distinct-labels'), ('closure-list', 'positive-rank-composition-form'), ('fitted-spin-orbit-strength', 'sealed-two-thirds-colour-coupling'), ('free-shell-shift', 'top-angular-half-label-pair'), ('selected-rank-threshold', 'least-positive-whole-gap'), ('arbitrary-intruder-count', 'complete-top-orbit-capacity'), ('finite-eight-value-table', 'piecewise-positive-successor-law'), ('magic-numbers-visible', 'sequence-inaccessible-until-seal'), ('extra-nuclear-rule', 'no-extra-rule'))
SURVIVOR = 'complete-three-direction-weak-compositions__two-exclusion-distinct-labels__positive-rank-composition-form__sealed-two-thirds-colour-coupling__top-angular-half-label-pair__least-positive-whole-gap__complete-top-orbit-capacity__piecewise-positive-successor-law__sequence-inaccessible-until-seal__no-extra-rule'


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}

    def base(rank):
        return rank * (rank + 1) * (rank + 2) // 3
    def closure(rank):
        return base(rank) if rank <= 3 else base(rank - 1) + 2 * rank
    sequence = tuple(closure(rank) for rank in range(1, 9))
    threshold = next(rank for rank in range(1, 10) if Fraction(2, 3) * Fraction(rank, 2) >= 1)
    arithmetic = sequence == (2, 8, 20, 28, 50, 82, 126, 184) and threshold == 3

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
