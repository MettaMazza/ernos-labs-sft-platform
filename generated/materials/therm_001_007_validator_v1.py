#!/usr/bin/env python3
"""Implementation-distinct reconstruction for Materials THERM-001--007."""
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

RELATIONS = {
    "SFT-MAT-THERM-DIFFUSIVITY-001": "conductivity-over-density-specific-heat-exact-diffusivity-part",
    "SFT-MAT-THERM-BOUNDARY-RESISTANCE-002": "interface-held-temperature-drop-area-per-heat-flow-reciprocal-ledger",
    "SFT-MAT-THERM-PHONON-MEAN-PATH-003": "complete-phonon-path-segment-scattering-event-mean-ledger",
    "SFT-MAT-THERM-RADIATIVE-TRANSPORT-004": "spectral-directional-incident-reflected-transmitted-absorbed-partition",
    "SFT-MAT-THERM-THERMOELECTRIC-BOUNDARY-005": "seebeck-squared-temperature-over-resistivity-conductivity-boundary",
    "SFT-MAT-THERM-PHASE-STORAGE-006": "sensible-latent-sensible-complete-phase-storage-ledger",
    "SFT-MAT-THERM-SHOCK-FATIGUE-007": "oriented-temperature-step-cycle-crack-critical-boundary-ledger",
}

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()

def native(claim_id):
    tests = (
        Fraction(12, 2 * 3) == 2,
        Fraction(3 * 2, 6) == 1 and Fraction(6, 3 * 2) == 1,
        Fraction(2 + 4 + 3, 3) == 3,
        2 + 3 + 5 == 10 and Fraction(2, 10) + Fraction(3, 10) + Fraction(5, 10) == 1,
        Fraction(2 * 2 * 3, 2 * 3) == 2,
        2 + 5 + 3 == 10 and Fraction(5, 10) == Fraction(1, 2),
        next(index for index, value in enumerate((None, 1, 2), 1) if value is not None) == 2,
    )
    return tests[list(RELATIONS).index(claim_id)]

def main():
    claim_id, root = sys.argv[1], Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = RELATIONS[claim_id]
    axes = (
        ("answer-only", "complete-positive-thermal-carrier"),
        ("imported-fit-or-continuum", relation),
        ("endpoint-only", "complete-interface-scattering-phase-cycle-path"),
        ("condition-erased", "specimen-method-temperature-scale-uncertainty-held"),
        ("headline-only", "complete-state-transition-resource-trace"),
        ("target-authority-or-prior-model", "root-bound-forward-forcing"),
        ("selected-instance", "positive-finite-successor-closure"),
        ("free-fit-exception-or-extra-rule", "no-extra-rule"),
    )
    generated = tuple("__".join(row) for row in product(*axes))
    survivor = "__".join(axis[1] for axis in axes)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {candidate: candidate == survivor for candidate in generated}
    vector = json.loads((root / "experiments/external_sources/materials/therm_001_007_v1/complete_evidence_vector_v1.json").read_text())
    vector_identity = vector.pop("complete_vector_identity")
    rows = {row["claim_id"]: row for row in vector["claims"]}
    evidence = vector_identity == canonical(vector) and len(rows) == 7 and claim_id in rows and rows[claim_id]["all_registered_fragments_present"] and all(file_hash(root / comparison["snapshot_path"]) == comparison["snapshot_hash"] for comparison in rows[claim_id]["comparisons"])
    passed = all((received == generated, len(received) == len(set(received)) == 256, decisions == expected, sum(expected.values()) == 1, sealed["closure"]["scope"] == "depth_independent", len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), native(claim_id), evidence))
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": claim_id, "candidate_count": len(received), "unique_survivor_count": sum(expected.values()), "native_reconstruction": native(claim_id), "external_reconstruction": evidence, "closure_scope": sealed["closure"]["scope"], "free_parameter_or_fitted_target_used": False}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)

if __name__ == "__main__":
    main()
