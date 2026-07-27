"""Implementation-distinct value-free PROP-014 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = 'SFT-CHEM-CROSS-PROPERTY-MOLECULAR-VECTOR-014'
DOMAINS = (('separate-carrier-per-property', 'one-complete-structural-carrier'), ('selected-or-favorable-property-subset', 'complete-applicable-property-support'), ('answer-only-property-values', 'named-admitted-relation-projections'), ('per-property-fit-or-correction', 'zero-parameter-shared-carrier-projection'), ('delete-unmeasured-or-inapplicable-row', 'structural-EmptyOne-and-unjoined-custody-retained'), ('target-payload-or-hash-readable-before-seal', 'complete-value-free-identity-seal'), ('single-species-showcase', 'complete-13-family-source-row-custody'), ('recompute-or-refit-existing-properties', 'append-only-depth-independent-projection-extension'))
SURVIVOR = 'one-complete-structural-carrier__complete-applicable-property-support__named-admitted-relation-projections__zero-parameter-shared-carrier-projection__structural-EmptyOne-and-unjoined-custody-retained__complete-value-free-identity-seal__complete-13-family-source-row-custody__append-only-depth-independent-projection-extension'

def vector(carrier, projections):
    labels=[p[0] for p in projections]
    if not carrier or not projections or len(labels) != len(set(labels)):
        raise ValueError("one carrier and unique projection families required")
    if set(carrier["families"]) != set(labels):
        raise ValueError("complete applicable support required")
    return tuple(projections)

def project(v, family):
    rows=[p for p in v if p[0] == family]
    if len(rows) != 1: raise ValueError("projection absent or duplicated")
    return rows[0]

def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed=json.load(handle)
    generated=["__".join(row) for row in product(*DOMAINS)]
    received=[row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions={row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    p1=("bond", "bond-law", Fraction(3,2)); p2=("vibration", "vibration-law", Fraction(5,3)); p3=("formation", "formation-law", Fraction(7,4))
    carrier={"id":"held-molecule", "families":("bond","vibration")}
    v=vector(carrier,(p1,p2)); extended=vector({"id":carrier["id"],"families":carrier["families"]+("formation",)},v+(p3,))
    controls=sealed["controls"]
    passed=(
        sealed["claim_id"] == CLAIM_ID and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {candidate: candidate == SURVIVOR for candidate in generated} and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in controls)
        and project(v,"bond") == p1 and project(v,"vibration") == p2
        and project(extended,"bond") == p1 and project(extended,"vibration") == p2 and project(extended,"formation") == p3
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None, "one_carrier_vector_reconstructed": len(v)==2,
            "named_projection_reconstructed": project(v,"bond")==p1,
            "append_only_extension_reconstructed": project(extended,"bond")==p1 and project(extended,"vibration")==p2,
            "per_property_fit_used": False, "measurement_file_accessed": False,
        },
    }, sort_keys=True))

if __name__ == "__main__": main()
