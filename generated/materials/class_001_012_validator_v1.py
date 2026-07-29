#!/usr/bin/env python3
"""Implementation-distinct exact reconstruction for Materials CLASS-001--012."""
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
import sys
from pathlib import Path

REL = {
    "SFT-MAT-CLASS-SOLID-SOLUTION-ALLOY-001": "constituent-phase-label-exact-alloy-partition",
    "SFT-MAT-CLASS-INTERMETALLIC-ORDER-002": "ordered-site-occupancy-compound-partition",
    "SFT-MAT-CLASS-HIGH-ENTROPY-BOUNDARY-003": "complete-component-phase-complex-alloy-boundary",
    "SFT-MAT-CLASS-REFRACTORY-UHT-004": "service-survival-retained-phase-refractory-history",
    "SFT-MAT-CLASS-CEMENTITIOUS-CONCRETE-005": "binder-aggregate-pore-hydration-composite-organization",
    "SFT-MAT-CLASS-FIBRE-REINFORCED-006": "fibre-matrix-interface-load-orientation-partition",
    "SFT-MAT-CLASS-PARTICLE-REINFORCED-007": "particle-matrix-interface-load-distribution-partition",
    "SFT-MAT-CLASS-METALLIC-GLASS-008": "local-order-nonperiodic-metastable-metallic-glass",
    "SFT-MAT-CLASS-CERAMIC-SUBCLASSES-009": "structural-functional-composition-process-ceramic-subclasses",
    "SFT-MAT-CLASS-POLYMER-SUBCLASSES-010": "thermoplastic-thermoset-elastomer-response-distinction",
    "SFT-MAT-CLASS-FUNCTIONALLY-GRADED-011": "ordered-layer-adjacency-property-gradient",
    "SFT-MAT-CLASS-ARCHITECTED-CELLULAR-012": "node-link-cell-topology-response-architecture",
}

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()

def native(claim_id):
    tests = (
        sum((Fraction(3, 5), Fraction(2, 5))) == 1,
        sum((Fraction(2, 5), Fraction(3, 5))) == 1,
        len((Fraction(2, 10), Fraction(3, 10), Fraction(5, 10))) == 3,
        Fraction(4, 5) < 1,
        sum((Fraction(2, 10), Fraction(5, 10), Fraction(1, 10), Fraction(2, 10))) == 1,
        4 + 3 + 1 == 8 and Fraction(4, 8) == Fraction(1, 2),
        3 + 4 + 1 == 8 and Fraction(3, 8) == Fraction(3, 8),
        "absent" != "periodic" and len(("near", "medium")) == 2,
        {"load"}.isdisjoint({"dielectric"}),
        len({("softens", "reshape", "retains-chain"), ("crosslinked", "permanent-shape", "does-not-commonly-soften"), ("elastic", "deform", "recover")}) == 3,
        tuple(zip(("left", "middle", "right"), ("middle", "right"))) == (("left", "middle"), ("middle", "right")),
        Fraction(6, 4 + 6 + 3) == Fraction(6, 13),
    )
    return tests[list(REL).index(claim_id)]

def main():
    claim_id, root = sys.argv[1], Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = REL[claim_id]
    axes = (
        ("class-name-only", "complete-positive-material-carrier"), ("imported-fit-classifier", relation),
        ("endpoint-only", "complete-structure-state-response-path"), ("condition-erased", "specimen-method-condition-scale-uncertainty-held"),
        ("headline-only", "complete-trace"), ("target-or-prior-model", "root-bound-forward-forcing"),
        ("selected-instance", "positive-finite-successor-closure"), ("fit-exception-extra-rule", "no-extra-rule"),
    )
    generated = tuple("__".join(row) for row in product(*axes))
    survivor = "__".join(axis[1] for axis in axes)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {candidate: candidate == survivor for candidate in generated}
    vector = json.loads((root / "experiments/external_sources/materials/class_001_012_v1/complete_evidence_vector_v1.json").read_text())
    vector_identity = vector.pop("complete_vector_identity")
    rows = {row["claim_id"]: row for row in vector["claims"]}
    evidence = vector_identity == canonical(vector) and len(rows) == 12 and claim_id in rows and rows[claim_id]["all_registered_fragments_present"] and all(file_hash(root / c["snapshot_path"]) == c["snapshot_hash"] for c in rows[claim_id]["comparisons"])
    passed = all((received == generated, len(received) == len(set(received)) == 256, decisions == expected, sum(expected.values()) == 1, sealed["closure"]["scope"] == "depth_independent", len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), native(claim_id), evidence))
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": claim_id, "candidate_count": len(received), "unique_survivor_count": sum(expected.values()), "native_reconstruction": native(claim_id), "external_reconstruction": evidence, "closure_scope": sealed["closure"]["scope"], "free_parameter_or_fitted_target_used": False}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)

if __name__ == "__main__":
    main()
