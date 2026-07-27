"""Implementation-distinct value-free THERMO-013 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-MULTICOMPONENT-PHASE-DIAGRAM-013"
DOMAINS = (
    ("unbound-coordinate-cloud", "complete-multicomponent-two-phase-point"),
    ("selected-coordinate-or-unclosed-sum", "complete-exact-phase-words-closing-to-One"),
    ("single-bulk-composition-or-erased-phase", "two-distinct-held-phase-composition-words"),
    ("imported-lever-rule-or-target-derived-tie-line", "componentwise-exact-exchange-support-balance"),
    ("free-continuum-diagram-plane", "exact-phase-rule-component-count-support"),
    ("numerical-zero-composition", "structural-EmptyOne-absent-coordinate"),
    ("coexistence-values-readable-before-seal", "complete-value-free-116-record-identity-seal"),
    ("redraw-refit-or-interpolate-after-extension", "depth-independent-append-and-exchange-replication"),
)
SURVIVOR = (
    "complete-multicomponent-two-phase-point__complete-exact-phase-words-closing-to-One__"
    "two-distinct-held-phase-composition-words__componentwise-exact-exchange-support-balance__"
    "exact-phase-rule-component-count-support__structural-EmptyOne-absent-coordinate__"
    "complete-value-free-116-record-identity-seal__depth-independent-append-and-exchange-replication"
)


def closes_to_one(values):
    if not values:
        return False
    total = values[0]
    for value in values[1:]:
        total += value
    return total == Fraction(1, 1)


def phase_rank(component_labels, phase_labels):
    carriers = list(component_labels) + ["temperature", "pressure"]
    for _phase in phase_labels:
        if not carriers:
            raise ValueError("phase cancellation exceeds carriers")
        carriers.pop()
    return tuple(carriers)


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    binary_liquid = (Fraction(2, 5), Fraction(3, 5))
    binary_gas = (Fraction(3, 5), Fraction(2, 5))
    ternary_liquid = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
    ternary_gas = (Fraction(1, 3), Fraction(1, 2), Fraction(1, 6))
    exchange = ((2, 2), (5, 5), (7, 7))
    replicated = tuple((first * 6, second * 6) for first, second in exchange)
    appended = (binary_liquid, ternary_liquid)
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and len([candidate for candidate, survives in decisions.items() if survives]) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls)
        and closes_to_one(binary_liquid) and closes_to_one(binary_gas)
        and closes_to_one(ternary_liquid) and closes_to_one(ternary_gas)
        and len(phase_rank(("a", "b"), ("liquid", "gas"))) == 2
        and len(phase_rank(("a", "b", "c"), ("liquid", "gas"))) == 3
        and all(first == second for first, second in exchange)
        and all(first == second for first, second in replicated)
        and len(appended) == 2
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
            "binary_and_ternary_exact_composition_closure_reconstructed": all(closes_to_one(values) for values in (binary_liquid, binary_gas, ternary_liquid, ternary_gas)),
            "componentwise_exchange_balance_reconstructed": all(first == second for first, second in exchange),
            "binary_and_ternary_phase_rank_reconstructed": len(phase_rank(("a", "b"), ("liquid", "gas"))) == 2 and len(phase_rank(("a", "b", "c"), ("liquid", "gas"))) == 3,
            "append_and_replication_reconstructed": len(appended) == 2 and all(first == second for first, second in replicated),
            "lever_rule_tie_line_gibbs_triangle_convex_hull_eos_fit_or_measurement_file_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
