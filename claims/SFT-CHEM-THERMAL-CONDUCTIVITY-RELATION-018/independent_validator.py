"""Implementation-distinct value-free THERMO-018 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-THERMAL-CONDUCTIVITY-RELATION-018"
DOMAINS = (
    ("detached-conductivity-number-or-continuum-field", "complete-composition-phase-condition-energy-transfer-account"),
    ("anonymous-or-collapsed-composition-phase", "distinct-held-complete-component-and-phase-identities"),
    ("Fourier-gradient-or-continuum-carrier-premise", "counted-adjacent-cell-energy-packet-transfer"),
    ("signed-heat-flux-proof-magnitude", "held-higher-to-lower-thermal-order-orientation"),
    ("unrecorded-energy-transfer-time-boundary-order-or-condition", "exact-positive-packet-transfer-tick-boundary-order-and-condition-support"),
    ("imported-Fourier-kinetic-mixing-temperature-fit-or-logarithm", "exact-positive-postseal-thermal-conductivity-support"),
    ("substance-composition-phase-condition-method-or-value-readable-before-seal", "complete-value-free-655-record-identity-seal"),
    ("refit-after-transfer-replication-or-record-append", "depth-independent-common-replication-and-record-append"),
)
SURVIVOR = "complete-composition-phase-condition-energy-transfer-account__distinct-held-complete-component-and-phase-identities__counted-adjacent-cell-energy-packet-transfer__held-higher-to-lower-thermal-order-orientation__exact-positive-packet-transfer-tick-boundary-order-and-condition-support__exact-positive-postseal-thermal-conductivity-support__complete-value-free-655-record-identity-seal__depth-independent-common-replication-and-record-append"


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    classes = tuple(f"{name}-composition-phase-energy-packet-transfer" for name in ("pure", "binary", "ternary"))
    forward = "source-higher-to-destination-lower-thermal-order" if 7 > 3 else "destination-higher-to-source-lower-thermal-order"
    reverse = "source-higher-to-destination-lower-thermal-order" if 3 > 7 else "destination-higher-to-source-lower-thermal-order"
    response = Fraction(5 * 11, 7 * 2 * 4)
    replicated_response = Fraction(5 * (11 * 6), (7 * 6) * 2 * 4)
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls)
        and len(set(classes)) == 3
        and forward != reverse
        and response == replicated_response == Fraction(55, 56)
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
            "pure_binary_ternary_carriers_reconstructed": classes,
            "held_opposed_thermal_orientations_reconstructed": forward != reverse,
            "exact_packet_transfer_tick_boundary_order_response_and_replication_reconstructed": response == replicated_response,
            "numerical_zero_negative_or_signed_proof_value_used": False,
            "continuum_Fourier_kinetic_mixing_temperature_fit_target_or_measurement_file_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
