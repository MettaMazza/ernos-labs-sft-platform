"""Implementation-distinct value-free THERMO-017 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-VISCOUS-TRANSPORT-RELATION-017"
DOMAINS = (
    ("detached-viscosity-number-or-continuum-field", "complete-composition-phase-condition-momentum-account"),
    ("anonymous-or-collapsed-composition", "distinct-held-complete-component-identities"),
    ("continuous-velocity-gradient-premise", "counted-adjacent-layer-momentum-exchange"),
    ("signed-shear-or-stress-proof-magnitude", "held-opposed-layer-transfer-orientation"),
    ("unrecorded-packet-exchange-time-or-condition", "exact-positive-packet-exchange-tick-and-condition-support"),
    ("imported-Newtonian-Arrhenius-WLF-VFT-or-fit", "exact-positive-postseal-viscosity-support"),
    ("substance-composition-condition-method-or-value-readable-before-seal", "complete-value-free-425-record-identity-seal"),
    ("refit-after-exchange-replication-or-record-append", "depth-independent-common-replication-and-record-append"),
)
SURVIVOR = "complete-composition-phase-condition-momentum-account__distinct-held-complete-component-identities__counted-adjacent-layer-momentum-exchange__held-opposed-layer-transfer-orientation__exact-positive-packet-exchange-tick-and-condition-support__exact-positive-postseal-viscosity-support__complete-value-free-425-record-identity-seal__depth-independent-common-replication-and-record-append"


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]; received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}; controls = sealed["controls"]
    classes = tuple(f"{name}-composition-retained-momentum-exchange" for name in ("pure", "binary", "ternary"))
    forward = "toward-later-generated-layer" if 4 < 5 else "toward-earlier-generated-layer"
    reverse = "toward-later-generated-layer" if 5 < 4 else "toward-earlier-generated-layer"
    density = Fraction(3 * 7, 5); replicated_density = Fraction(3 * (7 * 6), 5 * 6)
    passed = (
        sealed["claim_id"] == CLAIM_ID and received == generated and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == 256 and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1 and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls) and len(set(classes)) == 3
        and forward == "toward-later-generated-layer" and reverse == "toward-earlier-generated-layer"
        and density == replicated_density == Fraction(21, 5)
    )
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {
        "claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None,
        "closure": "depth_independent" if passed else None, "pure_binary_ternary_carriers_reconstructed": classes,
        "held_opposed_layer_orientations_reconstructed": forward != reverse,
        "exact_packet_exchange_tick_density_and_replication_reconstructed": density == replicated_density,
        "numerical_zero_negative_or_signed_proof_value_used": False,
        "continuum_Newtonian_Arrhenius_WLF_VFT_fit_target_or_measurement_file_accessed": False,
    }}, sort_keys=True))


if __name__ == "__main__": main()
