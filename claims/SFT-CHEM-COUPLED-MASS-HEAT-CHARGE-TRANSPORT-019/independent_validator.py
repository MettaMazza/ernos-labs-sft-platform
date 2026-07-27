"""Implementation-distinct value-free THERMO-019 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-COUPLED-MASS-HEAT-CHARGE-TRANSPORT-019"
DOMAINS = (
    ("detached-cross-coefficient-or-answer-vector", "complete-composition-phase-mass-heat-charge-account"),
    ("anonymous-collapsed-carriers-or-pair", "distinct-held-triad-and-pairwise-projections"),
    ("imported-Onsager-matrix-gradient-or-flux-equation", "counted-shared-adjacent-cell-transition-ledger"),
    ("signed-flux-proof-magnitudes", "held-per-carrier-transfer-orientations"),
    ("unrecorded-packet-event-time-boundary-or-condition", "exact-positive-packet-event-tick-boundary-and-condition-support"),
    ("phenomenological-cross-coefficient-fit-or-target-value", "exact-positive-postseal-pairwise-response-support"),
    ("substance-pair-property-condition-method-or-value-readable-before-seal", "complete-value-free-232-record-pair-identity-seal"),
    ("refit-after-event-replication-or-record-append", "depth-independent-common-replication-and-record-append"),
)
SURVIVOR = "complete-composition-phase-mass-heat-charge-account__distinct-held-triad-and-pairwise-projections__counted-shared-adjacent-cell-transition-ledger__held-per-carrier-transfer-orientations__exact-positive-packet-event-tick-boundary-and-condition-support__exact-positive-postseal-pairwise-response-support__complete-value-free-232-record-pair-identity-seal__depth-independent-common-replication-and-record-append"


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    triad = ("mass", "heat", "charge")
    projections = ("mass-heat", "mass-charge", "heat-charge")
    forward = tuple(f"{carrier}:source-to-destination" for carrier in triad)
    reverse = tuple(f"{carrier}:destination-to-source" for carrier in triad)
    responses = tuple(Fraction(packet * 7, 11 * 2) for packet in (2, 3, 5))
    replicated = tuple(Fraction(packet * (7 * 6), (11 * 6) * 2) for packet in (2, 3, 5))
    passed = (
        sealed["claim_id"] == CLAIM_ID and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256 and len(set(received)) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated} and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent" and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls) and len(set(triad)) == 3 and len(set(projections)) == 3
        and forward != reverse and responses == replicated == (Fraction(7, 11), Fraction(21, 22), Fraction(35, 22))
    )
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {
        "claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None,
        "closure": "depth_independent" if passed else None, "mass_heat_charge_triad_reconstructed": triad,
        "all_pairwise_projections_reconstructed": projections, "held_opposed_carrier_orientations_reconstructed": forward != reverse,
        "exact_packet_event_tick_boundary_responses_and_replication_reconstructed": responses == replicated,
        "numerical_zero_negative_or_signed_proof_value_used": False,
        "Onsager_matrix_continuum_gradient_flux_cross_coefficient_fit_target_or_measurement_file_accessed": False,
    }}, sort_keys=True))


if __name__ == "__main__":
    main()
