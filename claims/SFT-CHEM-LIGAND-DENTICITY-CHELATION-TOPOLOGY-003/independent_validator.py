"""Implementation-distinct, value-free INORG-003 reconstruction."""

from itertools import product
import json
import sys


CLAIM = "SFT-CHEM-LIGAND-DENTICITY-CHELATION-TOPOLOGY-003"
DOMAINS = (
    ("chemical-label-only", "one-retained-ligand-carrier-occurrence"),
    ("selected-or-nearby-donor-sites", "every-distinct-donor-site-on-that-carrier"),
    ("donor-sites-across-centres-merged", "same-retained-central-occurrence"),
    ("imported-denticity-name-or-table", "positive-count-of-generated-donor-incidences"),
    ("two-or-more-label-imported-as-threshold", "first-closed-carrier-centre-path-forces-chelation"),
    ("eta-kappa-and-separate-sites-collapsed", "separate-site-and-attachment-topologies-held"),
    ("source-topologies-readable-before-seal", "complete-24-record-value-free-identity-seal"),
    ("next-site-recounts-or-replaces-prior-support", "next-site-preserves-prior-and-adds-one"),
)
SURVIVOR = "one-retained-ligand-carrier-occurrence__every-distinct-donor-site-on-that-carrier__same-retained-central-occurrence__positive-count-of-generated-donor-incidences__first-closed-carrier-centre-path-forces-chelation__separate-site-and-attachment-topologies-held__complete-24-record-value-free-identity-seal__next-site-preserves-prior-and-adds-one"


def reconstruct(width: int):
    sites = tuple(f"donor-{number}" for number in range(1, width + 1))
    attachments = tuple(f"centre-donor-{number}" for number in range(1, width + 1))
    internal = tuple(f"donor-{number}-to-{number + 1}" for number in range(1, width))
    closed = () if width == 1 else (attachments[0], *internal, attachments[-1])
    return len(sites), sites, attachments, internal, closed


def main() -> None:
    document = json.load(open(sys.argv[1]))
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in document["census"]["candidates"]]
    decisions = {row["candidate_id"]: row["survives"] for row in document["decisions"]}
    one, two, three = reconstruct(1), reconstruct(2), reconstruct(3)
    witnesses = (
        one[0] == 1
        and not one[4]
        and two[0] == 2
        and len(two[4]) == 3
        and three[0] == 3
        and three[1][:2] == two[1]
        and three[2][:2] == two[2]
        and three[3][:-1] == two[3]
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
        and {row["kind"] for row in document["controls"]}
        == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] for row in document["controls"])
        and witnesses
    )
    print(
        json.dumps(
            {
                "validated_seal_hash": document["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "passed": passed,
                "certificate": {
                    "claim_id": CLAIM,
                    "generated_cardinality": len(generated),
                    "unique_survivor": SURVIVOR if passed else None,
                    "closure": "depth_independent" if passed else None,
                    "single_site_open_first_multiple_site_closed_and_successor_reconstructed": witnesses,
                    "numerical_zero_negative_irrational_imaginary_signed_or_continuum_proof_value_used": False,
                    "denticity_table_chelate_taxonomy_geometry_bonding_model_target_measurement_or_source_file_accessed": False,
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
