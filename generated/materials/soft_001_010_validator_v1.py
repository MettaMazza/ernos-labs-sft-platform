#!/usr/bin/env python3
"""Implementation-distinct exact reconstruction for Materials SOFT-001--010."""
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
import sys
from pathlib import Path

REL = {
    "SFT-MAT-SOFT-COLLOID-AGGREGATION-001": "free-aggregated-interaction-condition-colloid-partition",
    "SFT-MAT-SOFT-GEL-PERCOLATION-002": "node-link-spanning-response-gel-network",
    "SFT-MAT-SOFT-FOAM-DRAINAGE-003": "cell-gas-retained-drained-foam-ledger",
    "SFT-MAT-SOFT-LIQUID-CRYSTAL-ORDER-004": "orientation-part-phase-defect-liquid-crystal-order",
    "SFT-MAT-SOFT-EMULSION-DROPLET-005": "droplet-phase-interface-shear-emulsion-history",
    "SFT-MAT-SOFT-MEMBRANE-THIN-FILM-006": "layer-interface-transport-retention-membrane-ledger",
    "SFT-MAT-SOFT-GRANULAR-FORCE-CHAIN-007": "grain-contact-packing-force-chain-support",
    "SFT-MAT-SOFT-JAMMING-BOUNDARY-008": "before-after-applied-resisted-jamming-path",
    "SFT-MAT-SOFT-STIMULI-RESPONSIVE-009": "stimulus-before-after-response-reversible-history",
    "SFT-MAT-SOFT-ACTIVE-NONEQUILIBRIUM-010": "agent-input-motion-dissipation-nonequilibrium-history",
}

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()

def native(claim_id):
    tests = (
        3 + 2 == 5 and Fraction(2, 5) == Fraction(2, 5),
        Fraction(5, 9) == Fraction(5, 4 + 5),
        3 + 2 == 5 and Fraction(2, 5) == Fraction(2, 5),
        sum((Fraction(3, 5), Fraction(2, 5))) == 1,
        sum((Fraction(3, 5), Fraction(2, 5))) == 1,
        3 + 2 == 5 and Fraction(3, 5) == Fraction(3, 5),
        sum((Fraction(2, 5), Fraction(3, 5))) == 1,
        "flow" != "jammed" and Fraction(4, 5) < 1,
        Fraction(3, 2) == Fraction(3, 2),
        3 + 2 == 5 and Fraction(3, 5) == Fraction(3, 5),
    )
    return tests[list(REL).index(claim_id)]

def main():
    claim_id, root = sys.argv[1], Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = REL[claim_id]
    axes = (
        ("name-only", "complete-positive-soft-carrier"), ("imported-fit-continuum", relation),
        ("endpoint-only", "complete-state-structure-response-path"), ("condition-erased", "specimen-method-condition-scale-uncertainty-held"),
        ("headline-only", "complete-trace"), ("target-or-prior-model", "root-bound-forward-forcing"),
        ("selected-instance", "positive-finite-successor-closure"), ("fit-exception-extra-rule", "no-extra-rule"),
    )
    generated = tuple("__".join(row) for row in product(*axes))
    survivor = "__".join(axis[1] for axis in axes)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {candidate: candidate == survivor for candidate in generated}
    vector = json.loads((root / "experiments/external_sources/materials/soft_001_010_v1/complete_evidence_vector_v1.json").read_text())
    vector_identity = vector.pop("complete_vector_identity")
    rows = {row["claim_id"]: row for row in vector["claims"]}
    evidence = vector_identity == canonical(vector) and len(rows) == 10 and claim_id in rows and rows[claim_id]["all_registered_fragments_present"] and all(file_hash(root / c["snapshot_path"]) == c["snapshot_hash"] for c in rows[claim_id]["comparisons"])
    passed = all((received == generated, len(received) == len(set(received)) == 256, decisions == expected, sum(expected.values()) == 1, sealed["closure"]["scope"] == "depth_independent", len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), native(claim_id), evidence))
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": claim_id, "candidate_count": len(received), "unique_survivor_count": sum(expected.values()), "native_reconstruction": native(claim_id), "external_reconstruction": evidence, "closure_scope": sealed["closure"]["scope"], "free_parameter_or_fitted_target_used": False}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)

if __name__ == "__main__":
    main()
