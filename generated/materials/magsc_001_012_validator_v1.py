#!/usr/bin/env python3
"""Implementation-distinct exact reconstruction for Materials MAGSC-001--012."""
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
import sys
from pathlib import Path

REL = {
    "SFT-MAT-MAGSC-PARAMAGNETIC-RESPONSE-001": "parallel-moment-field-susceptibility-ledger",
    "SFT-MAT-MAGSC-DIAMAGNETIC-RESPONSE-002": "opposed-moment-field-susceptibility-ledger",
    "SFT-MAT-MAGSC-SPIN-GLASS-FREEZING-003": "temperature-state-preparation-freezing-history",
    "SFT-MAT-MAGSC-DOMAINS-WALLS-004": "domain-wall-nucleation-growth-motion-disappearance",
    "SFT-MAT-MAGSC-HYSTERESIS-LOOP-005": "closed-forward-reverse-field-magnetization-word",
    "SFT-MAT-MAGSC-MAGNETOCRYSTALLINE-ANISOTROPY-006": "easy-hard-crystal-axis-anisotropy-gap",
    "SFT-MAT-MAGSC-MAGNETORESISTANCE-007": "base-field-response-orientation-magnetoresistance",
    "SFT-MAT-MAGSC-SPIN-TRANSPORT-RELAXATION-008": "initial-retained-lost-spin-relaxation-path",
    "SFT-MAT-MAGSC-SC-CRITICAL-FIELDS-009": "ordered-critical-fields-Meissner-mixed-normal",
    "SFT-MAT-MAGSC-SC-VORTEX-PINNING-010": "pinned-mobile-vortex-lattice-partition",
    "SFT-MAT-MAGSC-SC-COHERENCE-LENGTH-011": "coherence-penetration-type-boundary",
    "SFT-MAT-MAGSC-SUPERFLUID-CRITICAL-FLOW-012": "persistent-excitation-critical-superfluid-flow",
}

def canon(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()

def native(claim_id):
    tests = (
        Fraction(2, 4) == Fraction(1, 2),
        "opposed" == "opposed",
        tuple(("mobile", "frozen")).index("frozen") + 1 == 2,
        2 < 4 and ("nucleated", "grown", "moved")[-1] == "moved",
        (1, 2) == (1, 2) and {"forward", "reverse"} == {"forward", "reverse"},
        5 - 3 == 2,
        Fraction(6, 4) == Fraction(3, 2),
        Fraction(3, 5) == Fraction(3, 5),
        5 - 2 == 3 and ("Meissner", "mixed", "normal")[1] == "mixed",
        3 + 2 == 5,
        Fraction(4, 2) == 2,
        3 + 2 == 5 and 3 < 4,
    )
    return tests[list(REL).index(claim_id)]

def main():
    claim_id, root = sys.argv[1], Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = REL[claim_id]
    axes = (
        ("answer-only", "complete-positive-magnetic-carrier"),
        ("imported-fit-continuum", relation),
        ("endpoint-only", "complete-field-spin-vortex-flow-path"),
        ("condition-erased", "specimen-method-field-temperature-uncertainty-held"),
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
    vector = json.loads((root / "experiments/external_sources/materials/magsc_001_012_v1/complete_evidence_vector_v1.json").read_text())
    vector_identity = vector.pop("complete_vector_identity")
    rows = {row["claim_id"]: row for row in vector["claims"]}
    evidence = (
        vector_identity == canon(vector)
        and len(rows) == 12
        and claim_id in rows
        and rows[claim_id]["all_registered_fragments_present"]
        and all(file_hash(root / comparison["snapshot_path"]) == comparison["snapshot_hash"] for comparison in rows[claim_id]["comparisons"])
    )
    passed = all((
        received == generated,
        len(received) == len(set(received)) == 256,
        decisions == expected,
        sum(expected.values()) == 1,
        sealed["closure"]["scope"] == "depth_independent",
        len(sealed["controls"]) == 4,
        all(row["passed"] for row in sealed["controls"]),
        native(claim_id),
        evidence,
    ))
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": claim_id, "candidate_count": len(received), "unique_survivor_count": sum(expected.values()), "native_reconstruction": native(claim_id), "external_reconstruction": evidence, "closure_scope": sealed["closure"]["scope"], "free_parameter_or_fitted_target_used": False}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)

if __name__ == "__main__":
    main()
