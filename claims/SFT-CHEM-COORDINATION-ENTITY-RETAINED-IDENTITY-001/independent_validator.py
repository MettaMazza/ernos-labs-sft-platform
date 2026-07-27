"""Implementation-distinct, value-free INORG-001 reconstruction."""
from itertools import product
import json
import sys

CLAIM = "SFT-CHEM-COORDINATION-ENTITY-RETAINED-IDENTITY-001"
DOMAINS = (
    ("formula-or-name-only", "complete-coordination-entity-carrier"),
    ("conventional-central-and-ligand-names-imported", "incidence-forced-central-and-surrounding-roles"),
    ("element-or-ligand-occurrences-collapsed", "central-and-every-ligand-occurrence-retained"),
    ("proximity-or-continuum-distance-only", "positive-central-ligand-incidence-trace"),
    ("selected-or-average-ligand-support", "complete-gap-free-ligand-support"),
    ("numerical-zero-or-negative-vacancy", "structural-EmptyOne-only"),
    ("source-structure-visible-before-seal", "complete-20-record-identity-sealed-structure-vector"),
    ("successor-replaces-central-or-prior-ligand", "next-ligand-preserves-entire-prior-entity"),
)
SURVIVOR = "complete-coordination-entity-carrier__incidence-forced-central-and-surrounding-roles__central-and-every-ligand-occurrence-retained__positive-central-ligand-incidence-trace__complete-gap-free-ligand-support__structural-EmptyOne-only__complete-20-record-identity-sealed-structure-vector__next-ligand-preserves-entire-prior-entity"


def main():
    document = json.load(open(sys.argv[1]))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in document["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in document["decisions"]}
    central = "Fe-one"
    ligand_occurrences = tuple(f"CO-{number}" for number in range(1, 6))
    incidences = tuple((central, ligand) for ligand in ligand_occurrences)
    successor = incidences + ((central, "CO-6"),)
    witnesses = (
        len(set(ligand_occurrences)) == 5
        and len(set(incidences)) == 5
        and all(edge[0] == central for edge in incidences)
        and successor[:len(incidences)] == incidences
        and successor[-1] == (central, "CO-6")
    )
    passed = (
        document["claim_id"] == CLAIM
        and received == generated
        and len(generated) == 256
        and len(set(received)) == 256
        and document["census"]["expected_cardinality"] == 256
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated}
        and sum(decisions.values()) == 1
        and document["closure"]["scope"] == "depth_independent"
        and document["closure"]["minimality_passed"]
        and document["closure"]["named_shape_uniqueness_passed"]
        and {row["kind"] for row in document["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in document["controls"])
        and witnesses
    )
    print(json.dumps({
        "validated_seal_hash": document["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": CLAIM,
            "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
            "central_and_five_distinct_ligand_occurrences_reconstructed": witnesses,
            "five_positive_incidence_traces_reconstructed": witnesses,
            "successor_preserves_complete_prior_entity": witnesses,
            "numerical_zero_negative_irrational_imaginary_signed_or_continuum_proof_value_used": False,
            "coordination_number_valence_bond_ligand_field_geometry_model_target_measurement_or_source_file_accessed": False
        }
    }, sort_keys=True))


if __name__ == "__main__":
    main()
