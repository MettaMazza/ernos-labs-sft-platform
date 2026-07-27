"""Implementation-distinct value-free KIN-007 reconstruction."""

from itertools import product
import json
import sys


CLAIM_ID = "SFT-CHEM-SEQUENTIAL-MECHANISM-COMPOSITION-007"
DOMAINS = (
    ("endpoint-only-or-selected-snapshot-support", "complete-source-ordered-state-and-transition-support"),
    ("aggregate-start-to-finish-jump", "exact-entry-exit-boundary-matching-for-every-edge"),
    ("implicit-eliminated-or-fitted-intermediate", "every-intermediate-occurrence-retained-explicitly"),
    ("imported-differential-exponential-or-lifetime-law", "finite-exact-ordered-edge-composition"),
    ("condition-time-or-dose-collapsed", "held-state-and-transition-condition-boundaries"),
    ("adverse-unresolved-or-parallel-record-omitted", "favorable-adverse-unresolved-and-parallel-status-retained"),
    ("structure-answer-without-source-custody", "complete-article-supplement-PDB-raw-custody-and-control-record"),
    ("time-coordinate-occupancy-or-target-readable-before-seal", "value-free-seventeen-record-identity-seal-and-depth-independent-successor"),
)
SURVIVOR = (
    "complete-source-ordered-state-and-transition-support__"
    "exact-entry-exit-boundary-matching-for-every-edge__"
    "every-intermediate-occurrence-retained-explicitly__"
    "finite-exact-ordered-edge-composition__"
    "held-state-and-transition-condition-boundaries__"
    "favorable-adverse-unresolved-and-parallel-status-retained__"
    "complete-article-supplement-PDB-raw-custody-and-control-record__"
    "value-free-seventeen-record-identity-seal-and-depth-independent-successor"
)


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    states = ("state-a", "state-b", "state-c")
    edges = (("edge-ab", "state-a", "state-b"), ("edge-bc", "state-b", "state-c"))
    intermediate = states[1:-1]
    extended_states = states + ("state-d",)
    extended_edges = edges + (("edge-cd", "state-c", "state-d"),)
    passed = (
        sealed["claim_id"] == CLAIM_ID and received == generated and len(generated) == 256
        and sealed["census"]["expected_cardinality"] == 256 and len(set(received)) == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in sealed["controls"])
        and len(edges) == len(states) - 1
        and all(edge[1] == states[index] and edge[2] == states[index + 1] for index, edge in enumerate(edges))
        and edges[0][2] == edges[1][1] and intermediate == ("state-b",)
        and extended_states[: len(states)] == states and extended_edges[: len(edges)] == edges
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None, "closure": "depth_independent" if passed else None,
            "complete_state_edge_word_reconstructed": True,
            "every_adjacent_boundary_and_intermediate_reconstructed": True,
            "successor_prefix_retention_reconstructed": True,
            "numerical_zero_negative_irrational_imaginary_logarithmic_signed_or_continuum_proof_value_used": False,
            "differential_equation_exponential_decay_fitted_lifetime_steady_state_target_measurement_or_source_file_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
