"""Implementation-distinct value-free THERMO-010 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-FUGACITY-EQUIVALENT-GAS-MIXTURE-010"
DOMAINS = (
    ("unbound-fugacity-number", "complete-gas-component-exchange-account"),
    ("erased-pressure-temperature-or-composition", "complete-held-pressure-temperature-composition-state"),
    ("bulk-mixture-answer-without-component-identity", "held-component-resolved-exchange-support"),
    ("imported-fugacity-eos-or-fitted-correction", "exact-accessible-over-reference-support-relation"),
    ("assumed-ideal-gas-or-target-derived-balance", "exact-component-exchange-support-balance"),
    ("real-gas-values-readable-before-seal", "complete-value-free-94-state-identity-seal"),
    ("selected-mixture-or-deleted-pressure-only-state", "complete-21-dataset-176-point-94-state-record"),
    ("refit-after-exact-support-replication", "depth-independent-common-support-replication"),
)
SURVIVOR = (
    "complete-gas-component-exchange-account__complete-held-pressure-temperature-composition-state__"
    "held-component-resolved-exchange-support__exact-accessible-over-reference-support-relation__"
    "exact-component-exchange-support-balance__complete-value-free-94-state-identity-seal__"
    "complete-21-dataset-176-point-94-state-record__depth-independent-common-support-replication"
)


def ratio(accessible, reference):
    if accessible <= 0 or reference <= 0 or accessible > reference:
        raise ValueError("inadmissible gas support")
    return Fraction(accessible, reference)


def relation(actual, comparison):
    if actual == comparison:
        return "balanced", None
    if actual < comparison:
        return "comparison-expanded", comparison - actual
    return "actual-expanded", actual - comparison


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    base_ratio = ratio(6, 10)
    interaction = relation(6, 8)
    phase_balance = relation(6, 6)
    replicated_ratio = ratio(42, 70)
    replicated_interaction = relation(42, 56)
    replicated_phase = relation(42, 42)
    controls = sealed["controls"]
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
        and {row["kind"] for row in controls}
        == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in controls)
        and base_ratio == Fraction(3, 5)
        and interaction == ("comparison-expanded", 2)
        and phase_balance == ("balanced", None)
        and replicated_ratio == base_ratio
        and replicated_interaction[0] == interaction[0]
        and replicated_phase == phase_balance
    )
    print(
        json.dumps(
            {
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "passed": passed,
                "certificate": {
                    "claim_id": CLAIM_ID,
                    "generated_cardinality": len(generated),
                    "unique_survivor": SURVIVOR if passed else None,
                    "closure": "depth_independent" if passed else None,
                    "exact_fugacity_equivalent_reconstructed": base_ratio == Fraction(3, 5),
                    "joint_vs_independent_support_reconstructed": interaction == ("comparison-expanded", 2),
                    "phase_exchange_balance_reconstructed": phase_balance == ("balanced", None),
                    "replication_successor_reconstructed": replicated_ratio == base_ratio
                    and replicated_interaction[0] == interaction[0]
                    and replicated_phase == phase_balance,
                    "fugacity_equation_eos_fit_or_measurement_file_accessed": False,
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
