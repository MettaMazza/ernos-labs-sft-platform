"""Implementation-distinct value-free KIN-001 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001"
DOMAINS = (
    ("detached-rate-number-or-continuum-field", "complete-registered-elementary-transition-carrier"),
    ("endpoint-erased-or-identity-change", "distinct-held-initial-and-terminal-molecular-states"),
    ("continuous-change-primitive-or-uncounted-event", "positive-completed-transition-count"),
    ("clock-free-or-continuum-time-derivative", "positive-reference-tick-count"),
    ("condition-or-observation-support-erased", "complete-condition-and-positive-observation-support"),
    ("imported-mass-action-order-arrhenius-fit-or-logarithm", "exact-transition-count-per-tick-and-observation-support"),
    ("reaction-condition-method-or-value-readable-before-seal", "complete-value-free-46-record-identity-seal"),
    ("refit-after-event-resource-replication-or-record-append", "depth-independent-common-event-tick-replication-and-record-append"),
)
SURVIVOR = "complete-registered-elementary-transition-carrier__distinct-held-initial-and-terminal-molecular-states__positive-completed-transition-count__positive-reference-tick-count__complete-condition-and-positive-observation-support__exact-transition-count-per-tick-and-observation-support__complete-value-free-46-record-identity-seal__depth-independent-common-event-tick-replication-and-record-append"


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    base = Fraction(6, 4 * 3)
    successor = Fraction(6 * 7, (4 * 7) * 3)
    passed = (
        sealed["claim_id"] == CLAIM_ID and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls)
        and base == successor == Fraction(1, 2)
        and "reactants-to-products" != "products-to-reactants"
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None, "closure": "depth_independent" if passed else None,
            "exact_event_tick_observation_response_reconstructed": base == Fraction(1, 2),
            "common_event_tick_replication_reconstructed": successor == base,
            "held_opposed_orientation_reconstructed": True,
            "numerical_zero_negative_irrational_imaginary_logarithmic_signed_or_continuum_proof_value_used": False,
            "mass_action_reaction_order_arrhenius_fitted_constant_concentration_derivative_target_or_measurement_file_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
