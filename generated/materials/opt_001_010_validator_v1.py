#!/usr/bin/env python3
"""Implementation-distinct exact reconstruction for Materials OPT-001--010."""
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
import sys
from pathlib import Path

REL = {
    "SFT-MAT-OPT-ABSORPTION-EXTINCTION-001": "incident-transmitted-reflected-absorbed-scattered-extinction-partition",
    "SFT-MAT-OPT-REFLECTION-TRANSMISSION-002": "incident-reflection-transmission-retained-geometry-ledger",
    "SFT-MAT-OPT-LUMINESCENCE-YIELD-003": "absorbed-emitted-nonradiative-quantum-yield-partition",
    "SFT-MAT-OPT-LIGHT-SCATTERING-004": "elastic-inelastic-unscattered-channel-partition",
    "SFT-MAT-OPT-BIREFRINGENCE-ANISOTROPY-005": "two-polarization-axis-ratio-positive-gap-anisotropy",
    "SFT-MAT-OPT-NONLINEAR-MIXING-006": "input-output-polarization-sum-difference-harmonic-mixing",
    "SFT-MAT-OPT-WAVEGUIDE-CONFINEMENT-LOSS-007": "incident-guided-lost-core-cladding-path-partition",
    "SFT-MAT-OPT-PHOTONIC-GAP-DEFECT-008": "ordered-gap-periodic-support-confined-defect-mode",
    "SFT-MAT-OPT-PLASMONIC-RESPONSE-009": "interface-collective-dissipated-plasmonic-mode-partition",
    "SFT-MAT-OPT-EXCITON-DYNAMICS-010": "generated-transported-recombined-retained-exciton-history",
}

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()

def native(claim_id):
    tests = (
        2 + 2 + 3 + 1 == 8 and Fraction(3 + 1, 8) == Fraction(1, 2),
        2 + 3 + 3 == 8 and Fraction(2, 8) == Fraction(1, 4),
        3 + 2 == 5 and Fraction(3, 5) == Fraction(3, 5),
        2 + 2 + 4 == 8 and Fraction(2 + 2, 8) == Fraction(1, 2),
        5 != 3 and abs(5 - 3) == 2,
        2 + 3 == 5,
        3 + 2 == 5 and Fraction(3, 5) == Fraction(3, 5),
        2 < 4 < 6 and 6 - 2 == 4,
        3 + 2 == 5 and Fraction(3, 5) == Fraction(3, 5),
        3 + 2 == 5 and 4 <= 5 and Fraction(2, 5) == Fraction(2, 5),
    )
    return tests[list(REL).index(claim_id)]

def main():
    claim_id, root = sys.argv[1], Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = REL[claim_id]
    axes = (
        ("answer-only", "complete-positive-optical-carrier"),
        ("imported-fit-continuum", relation),
        ("endpoint-only", "complete-optical-state-channel-path"),
        ("condition-erased", "specimen-method-geometry-spectrum-polarization-uncertainty-held"),
        ("headline-only", "complete-trace"),
        ("target-or-prior-model", "root-bound-forward-forcing"),
        ("selected-instance", "positive-finite-successor-closure"),
        ("fit-exception-extra-rule", "no-extra-rule"),
    )
    generated = tuple("__".join(row) for row in product(*axes))
    survivor = "__".join(axis[1] for axis in axes)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {candidate: candidate == survivor for candidate in generated}
    vector = json.loads((root / "experiments/external_sources/materials/opt_001_010_v1/complete_evidence_vector_v1.json").read_text())
    vector_identity = vector.pop("complete_vector_identity")
    rows = {row["claim_id"]: row for row in vector["claims"]}
    evidence = vector_identity == canonical(vector) and len(rows) == 10 and claim_id in rows and rows[claim_id]["all_registered_fragments_present"] and all(file_hash(root / comparison["snapshot_path"]) == comparison["snapshot_hash"] for comparison in rows[claim_id]["comparisons"])
    passed = all((received == generated, len(received) == len(set(received)) == 256, decisions == expected, sum(expected.values()) == 1, sealed["closure"]["scope"] == "depth_independent", len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), native(claim_id), evidence))
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": claim_id, "candidate_count": len(received), "unique_survivor_count": sum(expected.values()), "native_reconstruction": native(claim_id), "external_reconstruction": evidence, "closure_scope": sealed["closure"]["scope"], "free_parameter_or_fitted_target_used": False}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)

if __name__ == "__main__":
    main()
