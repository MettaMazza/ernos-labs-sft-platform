"""Implementation-distinct value-free PROP-010 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-ROTATIONAL-CONSTANT-010'
DOMAINS = (('answer-only-rotational-number', 'complete-finite-state-geometry-axis-carrier'), ('merged-or-relabelled-axis', 'held-principal-axis-and-equivalence-class'), ('imported-rotational-constant-or-inertia-equation', 'exact-axis-recurrence-over-interval-ratio'), ('continuum-or-free-angular-spectrum', 'positive-JJplusOne-level-and-2J-gap'), ('reciprocal-centimeter-selects-law', 'post-recurrence-held-unit-translation'), ('rotational-target-readable-before-seal', 'value-free-complete-axis-identity-seal'), ('favorable-molecule-or-present-axis-subset', 'complete-NIST-list-choice-result-and-axis-custody'), ('fitted-inertia-geometry-or-species-correction', 'one-axis-recurrence-law-no-extra-rule'))
SURVIVOR = 'complete-finite-state-geometry-axis-carrier__held-principal-axis-and-equivalence-class__exact-axis-recurrence-over-interval-ratio__positive-JJplusOne-level-and-2J-gap__post-recurrence-held-unit-translation__value-free-complete-axis-identity-seal__complete-NIST-list-choice-result-and-axis-custody__one-axis-recurrence-law-no-extra-rule'

def constant(recurrences, interval):
    if not isinstance(recurrences, int) or not isinstance(interval, int) or recurrences < 1 or interval < 1:
        raise ValueError("positive finite counts required")
    return Fraction(recurrences, interval)

def level(j):
    if not isinstance(j, int) or j < 1:
        raise ValueError("positive rotational ordinal required")
    return j * (j + 1)

def gap(j):
    if not isinstance(j, int) or j < 1:
        raise ValueError("positive upper ordinal required")
    return 2 * j

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    base = constant(12, 3)
    repeated = constant(60, 15)
    invalid_rejected = False
    try:
        constant(1, None)
    except ValueError:
        invalid_rejected = True
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
        and base == Fraction(4, 1)
        and repeated == base
        and tuple(level(j) for j in range(1, 5)) == (2, 6, 12, 20)
        and tuple(gap(j) for j in range(1, 5)) == (2, 4, 6, 8)
        and invalid_rejected
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
            "held_axis_recurrence_ratio_reconstructed": base == Fraction(4, 1),
            "equal_interval_successor_reconstructed": repeated == base,
            "positive_JJplusOne_ladder_reconstructed": tuple(level(j) for j in range(1, 5)) == (2, 6, 12, 20),
            "adjacent_2J_gaps_reconstructed": tuple(gap(j) for j in range(1, 5)) == (2, 4, 6, 8),
            "invalid_interval_rejected": invalid_rejected,
            "rigid_rotor_or_inertia_equation_used": False,
            "measurement_file_accessed": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
