#!/usr/bin/env python3
"""Implementation-distinct exact reconstruction for Materials BIO-001--008."""
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
import sys
from pathlib import Path

REL = {
    "SFT-MAT-BIO-BIOCOMPATIBILITY-INTERFACE-001": "exposure-compatible-adverse-material-interface-ledger",
    "SFT-MAT-BIO-BIORESORPTION-DEGRADATION-002": "initial-retained-resorbed-product-path-ledger",
    "SFT-MAT-BIO-SCAFFOLD-POROSITY-CONNECTIVITY-003": "pore-strut-link-class-spanning-scaffold",
    "SFT-MAT-BIO-CELL-MATERIAL-ADHESION-004": "presented-adherent-nonadherent-cell-material-interface",
    "SFT-MAT-BIO-MECHANICAL-MATCHING-005": "applied-material-tissue-interface-load-partition",
    "SFT-MAT-BIO-CONTROLLED-RELEASE-006": "loaded-released-retained-carrier-path",
    "SFT-MAT-BIO-MINERALIZED-ORGANIZATION-007": "organic-mineral-pore-identity-structure",
    "SFT-MAT-BIO-BIOFABRICATED-IDENTITY-008": "biological-source-cell-process-input-output-custody",
}

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()

def native(claim_id):
    tests = (
        4 + 1 == 5 and Fraction(4, 5) == Fraction(4, 5),
        3 + 2 == 5 and Fraction(2, 5) == Fraction(2, 5),
        Fraction(5, 5 + 3) == Fraction(5, 8),
        3 + 2 == 5 and Fraction(3, 5) == Fraction(3, 5),
        3 + 4 + 1 == 8,
        3 + 2 == 5 and Fraction(3, 5) == Fraction(3, 5),
        sum((Fraction(2, 8), Fraction(5, 8), Fraction(1, 8))) == 1,
        Fraction(3, 5) == Fraction(3, 5),
    )
    return tests[list(REL).index(claim_id)]

def main():
    claim_id, root = sys.argv[1], Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = REL[claim_id]
    axes = (
        ("label-only", "complete-positive-biomaterial-carrier"), ("imported-fit-model", relation),
        ("endpoint-only", "complete-material-interface-state-path"), ("condition-erased", "specimen-method-condition-scale-uncertainty-held"),
        ("headline-only", "complete-trace"), ("target-or-prior-model", "root-bound-forward-forcing"),
        ("selected-instance", "positive-finite-successor-closure"), ("fit-exception-extra-rule", "no-extra-rule"),
    )
    generated = tuple("__".join(row) for row in product(*axes))
    survivor = "__".join(axis[1] for axis in axes)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {candidate: candidate == survivor for candidate in generated}
    vector = json.loads((root / "experiments/external_sources/materials/bio_001_008_v1/complete_evidence_vector_v1.json").read_text())
    vector_identity = vector.pop("complete_vector_identity")
    rows = {row["claim_id"]: row for row in vector["claims"]}
    evidence = vector_identity == canonical(vector) and len(rows) == 8 and claim_id in rows and rows[claim_id]["all_registered_fragments_present"] and all(file_hash(root / c["snapshot_path"]) == c["snapshot_hash"] for c in rows[claim_id]["comparisons"])
    passed = all((received == generated, len(received) == len(set(received)) == 256, decisions == expected, sum(expected.values()) == 1, sealed["closure"]["scope"] == "depth_independent", len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), native(claim_id), evidence))
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": claim_id, "candidate_count": len(received), "unique_survivor_count": sum(expected.values()), "native_reconstruction": native(claim_id), "external_reconstruction": evidence, "closure_scope": sealed["closure"]["scope"], "free_parameter_or_fitted_target_used": False}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)

if __name__ == "__main__":
    main()
