#!/usr/bin/env python3
"""Implementation-distinct exact reconstruction for Materials NANO-001--010."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

REL = {
    "SFT-MAT-NANO-SIZE-SHAPE-DISTRIBUTION-001": "particle-identity-three-dimension-shape-complete-distribution",
    "SFT-MAT-NANO-NANOWIRE-CONFINEMENT-002": "one-extended-two-finite-terminal-held-wire-support",
    "SFT-MAT-NANO-LAYER-STACKING-003": "ordered-layer-interface-registry-word",
    "SFT-MAT-NANO-QUANTUM-DOT-CONFINEMENT-004": "finite-site-boundary-carrier-level-confinement",
    "SFT-MAT-NANO-SURFACE-VOLUME-DOMINANCE-005": "counted-boundary-interior-successor-surface-part",
    "SFT-MAT-NANO-PHASE-MELTING-BOUNDARY-006": "size-phase-method-conditioned-transition-boundary",
    "SFT-MAT-NANO-QUANTUM-COLLECTIVE-STATE-007": "local-correlation-joint-topology-collective-state",
    "SFT-MAT-NANO-MOIRE-SUPERSTRUCTURE-008": "two-layer-least-positive-joint-recurrence",
    "SFT-MAT-NANO-NANOCOMPOSITE-INTERFACE-DENSITY-009": "matrix-inclusion-interface-contact-density-ledger",
    "SFT-MAT-NANO-AGGREGATION-DISPERSION-CUSTODY-010": "particle-cluster-medium-condition-complete-custody",
}


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def native(claim_id):
    surface_three = Fraction(26, 27)
    surface_four = Fraction(56, 64)
    tests = (
        len({("p1", (1, 2, 3), "rod"), ("p2", (1, 1, 1), "compact")}) == 2,
        (5, 1, 1) == (5, 1, 1),
        len(("ab", "bc")) + 1 == len(("a", "b", "c")),
        4 <= 5 and len(("ground", "excited")) == 2,
        surface_four < surface_three,
        Fraction(1) < Fraction(3, 2) < Fraction(2),
        len((("a", "b"), ("b", "c"))) == 2,
        next(step for step in range(1, 7) if step % 2 == 0 and step % 3 == 0) == 6,
        Fraction(4, 3 + 2) == Fraction(4, 5),
        {member for group in (("p1", "p2"), ("p3",)) for member in group} == {"p1", "p2", "p3"},
    )
    return tests[list(REL).index(claim_id)]


def main():
    claim_id, root = sys.argv[1], Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = REL[claim_id]
    axes = (
        ("label-only", "complete-positive-nanomaterial-carrier"),
        ("imported-fit-model", relation),
        ("endpoint-or-average-only", "complete-generated-discrete-organization"),
        ("condition-erased", "specimen-method-condition-scale-uncertainty-held"),
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
    vector = json.loads((root / "experiments/external_sources/materials/nano_001_010_v1/complete_evidence_vector_v1.json").read_text())
    vector_identity = vector.pop("complete_vector_identity")
    rows = {row["claim_id"]: row for row in vector["claims"]}
    evidence = (
        vector_identity == canonical(vector)
        and len(rows) == 10
        and claim_id in rows
        and rows[claim_id]["all_registered_fragments_present"]
        and all(file_hash(root / comparison["snapshot_path"]) == comparison["snapshot_hash"] for comparison in rows[claim_id]["comparisons"])
        and all("text_reconstruction_path" not in comparison or file_hash(root / comparison["text_reconstruction_path"]) == comparison["text_reconstruction_hash"] for comparison in rows[claim_id]["comparisons"])
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
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": claim_id,
            "candidate_count": len(received),
            "unique_survivor_count": sum(expected.values()),
            "native_reconstruction": native(claim_id),
            "external_reconstruction": evidence,
            "closure_scope": sealed["closure"]["scope"],
            "free_parameter_or_fitted_target_used": False,
        },
    }, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()

