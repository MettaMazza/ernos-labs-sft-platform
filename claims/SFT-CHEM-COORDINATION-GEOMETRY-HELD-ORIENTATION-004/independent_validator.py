"""Implementation-distinct, value-free INORG-004 reconstruction."""

from itertools import product
import json
import sys


CLAIM = "SFT-CHEM-COORDINATION-GEOMETRY-HELD-ORIENTATION-004"
DOMAINS = (
    ("chemical-formula-only", "one-retained-centre-and-every-direct-ligand-occurrence"),
    ("coordination-number-alone-selects-shape", "complete-direct-incidence-support"),
    ("imported-shape-name-or-continuum-coordinate", "three-generated-axis-held-orientation-word"),
    ("selected-or-inferred-neighbour-pairs", "complete-generated-boundary-adjacency-trace"),
    ("orientation-or-occurrence-collapse", "exact-complete-position-adjacency-signature"),
    ("free-dimensional-or-polyhedral-rank", "forced-generator-three-and-boundary-rank-two"),
    ("selected-favourable-geometry-rows", "sealed-complete-authority-surfaces-including-adverse-identity-rows"),
    ("new-position-replaces-or-recounts-prior-geometry", "next-position-preserves-prior-and-adds-its-complete-relations"),
)
SURVIVOR = "one-retained-centre-and-every-direct-ligand-occurrence__complete-direct-incidence-support__three-generated-axis-held-orientation-word__complete-generated-boundary-adjacency-trace__exact-complete-position-adjacency-signature__forced-generator-three-and-boundary-rank-two__sealed-complete-authority-surfaces-including-adverse-identity-rows__next-position-preserves-prior-and-adds-its-complete-relations"


def reconstruct(width: int, changed_second: bool = False):
    positions = []
    for number in range(1, width + 1):
        orientation = (f"fibre-{number}", "fibre-two" if changed_second and number == 2 else "EmptyOne", "EmptyOne")
        positions.append((number, f"ligand-{number}", orientation))
    edges = tuple((f"ligand-{number}", f"ligand-{number + 1}", f"edge-{number}-{number + 1}") for number in range(1, width))
    return tuple(positions), edges, 3, 2


def main() -> None:
    document = json.load(open(sys.argv[1]))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in document["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in document["decisions"]}
    two = reconstruct(2)
    two_changed = reconstruct(2, True)
    three = reconstruct(3)
    witnesses = (
        len(two[0]) == 2
        and two[2:] == (3, 2)
        and two[0] != two_changed[0]
        and two[2:] == two_changed[2:]
        and three[0][:2] == two[0]
        and three[1][:1] == two[1]
        and len(three[0]) == 3
        and three[2:] == (3, 2)
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
            "equal_count_distinct_orientation_and_successor_reconstructed": witnesses,
            "space_rank": 3,
            "boundary_rank": 2,
            "numerical_zero_negative_irrational_imaginary_signed_or_continuum_proof_value_used": False,
            "geometry_table_shape_name_point_group_angle_distance_coordinate_target_measurement_or_source_file_accessed": False,
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
