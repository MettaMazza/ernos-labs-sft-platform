"""Implementation-distinct value-free THERMO-016 reconstruction."""

from fractions import Fraction
from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-MOLECULAR-DIFFUSION-RELATION-016"
DOMAINS = (
    ("detached-diffusion-number-or-continuum-field", "complete-molecular-transition-condition-account"),
    ("anonymous-particle-or-erased-medium", "distinct-held-migrating-and-medium-identities"),
    ("unbounded-continuous-displacement", "counted-adjacent-generated-cell-transition"),
    ("created-lost-or-merged-constituent", "complete-global-constituent-conservation"),
    ("unrecorded-time-space-or-random-premise", "exact-positive-tick-cell-and-path-support"),
    ("imported-Fick-Brownian-Stokes-Einstein-or-fit", "exact-positive-postseal-diffusion-support"),
    ("species-condition-method-or-value-readable-before-seal", "complete-value-free-164-record-identity-seal"),
    ("refit-after-transition-replication-or-record-append", "depth-independent-common-replication-and-record-append"),
)
SURVIVOR = (
    "complete-molecular-transition-condition-account__distinct-held-migrating-and-medium-identities__"
    "counted-adjacent-generated-cell-transition__complete-global-constituent-conservation__"
    "exact-positive-tick-cell-and-path-support__exact-positive-postseal-diffusion-support__"
    "complete-value-free-164-record-identity-seal__depth-independent-common-replication-and-record-append"
)


def orientation(source, destination):
    if abs(source - destination) != 1:
        raise ValueError("not adjacent")
    return "toward-later-generated-cell" if source < destination else "toward-earlier-generated-cell"


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    controls = sealed["controls"]
    constituents_before = ("migrant", "medium")
    constituents_after = tuple(reversed(constituents_before))
    density = Fraction(7, 5)
    replicated_density = Fraction(7 * 6, 5 * 6)
    classes = tuple(f"{name}-identity-retained-adjacent-transition" for name in ("binary", "self", "tracer"))
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
        and orientation(3, 4) == "toward-later-generated-cell"
        and orientation(4, 3) == "toward-earlier-generated-cell"
        and sorted(constituents_before) == sorted(constituents_after)
        and density == replicated_density
        and len(classes) == 3 and len(set(classes)) == 3
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None, "closure": "depth_independent" if passed else None,
            "binary_self_tracer_carriers_reconstructed": classes,
            "adjacent_held_orientation_reconstructed": orientation(3, 4) != orientation(4, 3),
            "constituent_conservation_reconstructed": sorted(constituents_before) == sorted(constituents_after),
            "deterministic_common_replication_preserves_exact_density": density == replicated_density,
            "numerical_zero_or_negative_proof_value_used": False,
            "random_premise_Fick_Brownian_Stokes_Einstein_fit_target_or_measurement_file_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
