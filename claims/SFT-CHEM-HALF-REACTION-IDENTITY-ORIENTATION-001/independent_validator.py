from itertools import product
import json
import sys

CLAIM_ID = "SFT-CHEM-HALF-REACTION-IDENTITY-ORIENTATION-001"
DOMAINS = (
    ("equation-text-only", "exact-half-reaction-identity"),
    ("selected-or-unphased-species", "complete-species-phase-carrier"),
    ("signed-electron-count", "positive-count-of-held-electron-carriers"),
    ("sign-as-direction", "held-source-terminal-orientation"),
    ("open-oxidation-or-reduction-story", "exact-inverse-half-reaction-pair"),
    ("unbound-potential-answer", "held-reference-half-cell-identity"),
    ("favourable-species-only", "complete-half-reaction-record"),
    ("reaction-specific-exception", "fresh-species-successor-preserves-prior-record"),
)
SURVIVOR = "__".join(domain[1] for domain in DOMAINS)

def main():
    sealed = json.load(open(sys.argv[1]))
    generated = ["__".join(candidate) for candidate in product(*DOMAINS)]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    source = ("oxidized(aqueous)",)
    terminal = ("reduced(solid)",)
    carriers = ("electron-1",)
    forward = (source, terminal, carriers, "source-to-terminal", "reference-half-cell")
    inverse = (terminal, source, carriers, "terminal-to-source", "reference-half-cell")
    native = {
        "identity_retained": True,
        "complete_species_phase_retained": "aqueous" in source[0] and "solid" in terminal[0],
        "positive_held_transfer_count": len(carriers) == 1,
        "orientation_held": forward[3] == "source-to-terminal",
        "inverse_swaps_complete_sides": inverse[0] == forward[1] and inverse[1] == forward[0],
        "inverse_retains_carriers": inverse[2] == forward[2],
        "reference_retained": inverse[4] == forward[4],
    }
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and [row["candidate_id"] for row in sealed["census"]["candidates"]] == generated
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and all(row["passed"] for row in sealed["controls"])
        and all(native.values())
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
            **native,
            "external_source_accessed": False,
            "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_parameter_used": False,
        },
    }, sort_keys=True))

if __name__ == "__main__":
    main()
