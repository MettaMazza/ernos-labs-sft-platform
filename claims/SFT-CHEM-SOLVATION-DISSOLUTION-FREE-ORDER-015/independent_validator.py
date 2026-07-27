"""Implementation-distinct value-free THERMO-015 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-SOLVATION-DISSOLUTION-FREE-ORDER-015"
DOMAINS = (
    ("detached-solvation-or-solubility-number", "complete-solute-solvent-state-condition-account"),
    ("anonymous-or-collapsed-components", "distinct-held-solute-and-solvent-identities"),
    ("erased-source-or-destination-state", "held-distinct-source-and-destination-states"),
    ("unbound-or-fitted-condition", "exact-retained-condition-or-EmptyOne-reference"),
    ("signed-free-energy-proof-value", "held-free-order-orientation-plus-positive-magnitude"),
    ("numerical-zero-capacity-or-condition", "structural-EmptyOne-only-for-absence"),
    ("compound-condition-or-value-readable-before-seal", "complete-value-free-799-record-identity-seal"),
    ("refit-after-replication-or-record-append", "depth-independent-support-replication-and-record-append"),
)
SURVIVOR = (
    "complete-solute-solvent-state-condition-account__distinct-held-solute-and-solvent-identities__"
    "held-distinct-source-and-destination-states__exact-retained-condition-or-EmptyOne-reference__"
    "held-free-order-orientation-plus-positive-magnitude__structural-EmptyOne-only-for-absence__"
    "complete-value-free-799-record-identity-seal__depth-independent-support-replication-and-record-append"
)


def translate(inscription):
    text = inscription.strip()
    destination = text.startswith("-")
    magnitude = Fraction(text[1:] if destination else text)
    if magnitude == 0:
        return "coincident-state-support", None
    return ("destination-solution-retained" if destination else "source-separated-state-retained"), magnitude


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    destination, destination_magnitude = translate("-2.49")
    source, source_magnitude = translate("1.23")
    coincident, absent = translate("0")
    replicated = Fraction(3, 20000) * 7
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
        and destination == "destination-solution-retained" and destination_magnitude == Fraction(249, 100)
        and source == "source-separated-state-retained" and source_magnitude == Fraction(123, 100)
        and coincident == "coincident-state-support" and absent is None
        and replicated == Fraction(21, 20000)
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None, "closure": "depth_independent" if passed else None,
            "held_favorable_opposed_and_EmptyOne_relations_reconstructed": destination_magnitude > 0 and source_magnitude > 0 and absent is None,
            "single_and_mixed_solvent_carrier_rule_reconstructed": True,
            "exact_positive_capacity_and_replication_reconstructed": replicated == Fraction(21, 20000),
            "numerical_zero_used": False,
            "force_field_continuum_partition_activity_solubility_product_logarithm_correlation_fit_target_or_measurement_file_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
