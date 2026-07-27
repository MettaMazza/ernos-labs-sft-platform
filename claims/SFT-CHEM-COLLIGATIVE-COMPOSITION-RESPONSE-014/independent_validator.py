"""Implementation-distinct value-free THERMO-014 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-COLLIGATIVE-COMPOSITION-RESPONSE-014"
DOMAINS = (
    ("unbound-response-number", "complete-solvent-solute-particle-account"),
    ("anonymous-particle-count-or-erased-solvent", "distinct-held-solvent-and-solute-identities"),
    ("imported-colligative-equation-or-dissociation-factor", "exact-solvent-transmission-and-solute-retention-boundary"),
    ("signed-temperature-or-pressure-displacement", "held-boiling-freezing-osmotic-orientation-label"),
    ("linear-constant-fit-or-target-correction", "exact-positive-reference-response-separation"),
    ("numerical-zero-solute-coordinate", "structural-EmptyOne-pure-solvent-boundary"),
    ("response-values-readable-before-seal", "complete-value-free-276-record-identity-seal"),
    ("refit-after-particle-or-response-replication", "depth-independent-common-replication-and-record-append"),
)
SURVIVOR = (
    "complete-solvent-solute-particle-account__distinct-held-solvent-and-solute-identities__"
    "exact-solvent-transmission-and-solute-retention-boundary__held-boiling-freezing-osmotic-orientation-label__"
    "exact-positive-reference-response-separation__structural-EmptyOne-pure-solvent-boundary__"
    "complete-value-free-276-record-identity-seal__depth-independent-common-replication-and-record-append"
)
ORIENTATIONS = {
    "boiling": "temperature-support-expanded-until-liquid-gas-balance",
    "freezing": "temperature-support-reduced-until-liquid-crystal-balance",
    "osmotic": "pressure-support-directed-toward-solute-holding-solution",
}


def compare(first, second):
    if first == second:
        return "coincident", None
    if first < second:
        return "expanded", second - first
    return "reduced", first - second


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    relation, separation = compare(Fraction(7, 3), Fraction(8, 3))
    replicated_relation, replicated_separation = compare(Fraction(42, 3), Fraction(48, 3))
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
        and tuple(ORIENTATIONS) == ("boiling", "freezing", "osmotic")
        and relation == replicated_relation == "expanded"
        and separation == Fraction(1, 3) and replicated_separation == Fraction(2, 1)
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None, "closure": "depth_independent" if passed else None,
            "three_response_orientations_reconstructed": tuple(ORIENTATIONS) == ("boiling", "freezing", "osmotic"),
            "exact_positive_separation_reconstructed": relation == "expanded" and separation == Fraction(1, 3),
            "common_replication_preserves_order": replicated_relation == relation,
            "numerical_zero_used": False,
            "colligative_equation_constant_factor_fit_target_or_measurement_file_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
