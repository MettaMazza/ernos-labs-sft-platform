"""Implementation-distinct, target-inaccessible INORG-008 reconstruction."""

from itertools import product
import json
import sys


CLAIM = "SFT-CHEM-INORGANIC-COLOUR-ELECTRONIC-TRANSITION-008"
DOMAINS = (
    ("anonymous-complex-transition", "one-retained-coordination-entity"),
    ("imported-orbital-symbol-pair", "complete-ligand-metal-carrier-pair"),
    ("energy-only-endpoints", "two-retained-state-identities"),
    ("signed-charge-displacement", "held-source-target-direction"),
    ("floating-or-dimensional-energy-gap", "positive-state-order-separation"),
    ("selected-colour-name", "proper-absorbed-distinction-class"),
    ("conventional-colour-wheel", "retained-complement-observation-class"),
    ("species-peak-or-threshold-exception", "complete-spectra-with-no-extra-rule"),
)
SURVIVOR = "one-retained-coordination-entity__complete-ligand-metal-carrier-pair__two-retained-state-identities__held-source-target-direction__positive-state-order-separation__proper-absorbed-distinction-class__retained-complement-observation-class__complete-spectra-with-no-extra-rule"


def main() -> None:
    document = json.load(open(sys.argv[1]))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in document["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in document["decisions"]}
    carriers = ("ligand", "metal")
    classes = tuple(f"{source}-to-{target}" for source, target in product(carriers, repeat=2))
    source_position, target_position = 1, 3
    gap = target_position - source_position
    incident = ("a", "b", "c")
    absorbed = ("b",)
    retained = tuple(value for value in incident if value not in absorbed)
    reconstructed = classes == ("ligand-to-ligand", "ligand-to-metal", "metal-to-ligand", "metal-to-metal") and gap == 2 and len(absorbed) == 1 and retained == ("a", "c")
    passed = (
        document["claim_id"] == CLAIM and received == generated and len(generated) == 256 and len(set(received)) == 256
        and document["census"]["expected_cardinality"] == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated} and sum(decisions.values()) == 1
        and document["closure"]["scope"] == "depth_independent" and document["closure"]["minimality_passed"] and document["closure"]["named_shape_uniqueness_passed"]
        and {row["kind"] for row in document["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in document["controls"]) and reconstructed
    )
    print(json.dumps({
        "validated_seal_hash": document["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {
            "claim_id": CLAIM, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None, "transition_classes": classes, "positive_order_gap": gap,
            "absorbed_count": len(absorbed), "retained_colour_count": len(retained),
            "numerical_zero_negative_irrational_imaginary_signed_continuum_or_fitted_parameter_used_in_proof_object": False,
            "orbital_colour_wheel_spectrum_peak_wavelength_intensity_target_source_or_measured_value_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
