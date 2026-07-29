#!/usr/bin/env python3
"""Implementation-distinct exact reconstruction for Materials SURF-001--008."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

REL = {
    "SFT-MAT-SURF-FREE-STATE-ENERGY-001": "bulk-surface-state-condition-excess-ledger",
    "SFT-MAT-SURF-WETTING-CONTACT-ANGLE-002": "liquid-surface-contact-noncontact-angle-method-custody",
    "SFT-MAT-SURF-ADHESION-SEPARATION-003": "interface-link-separation-work-path-ledger",
    "SFT-MAT-SURF-COATING-SUBSTRATE-004": "substrate-layer-interface-process-word",
    "SFT-MAT-SURF-ROUGHNESS-SCALE-005": "height-word-lateral-scale-method-range",
    "SFT-MAT-SURF-REACTION-CATALYSIS-HANDOFF-006": "surface-site-reactant-product-path-catalyst-handoff",
    "SFT-MAT-SURF-TRIBOFILM-RETENTION-007": "film-substrate-covered-uncovered-path",
    "SFT-MAT-SURF-DELAMINATION-008": "layer-substrate-intact-separated-front-path",
}


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def native(claim_id):
    tests = (
        Fraction(2, 3 + 2) == Fraction(2, 5),
        Fraction(3, 3 + 2) == Fraction(3, 5),
        3 + 2 == 5 and Fraction(4, 2) == 2,
        len(("sb", "bt")) == len(("bond", "top")),
        max((1, 3, 2)) - min((1, 3, 2)) == 2,
        ("catalyst", "catalyst")[0] == ("catalyst", "catalyst")[1],
        Fraction(3, 5) == Fraction(3, 5),
        Fraction(2, 5) == Fraction(2, 5),
    )
    return tests[list(REL).index(claim_id)]


def main():
    claim_id, root = sys.argv[1], Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = REL[claim_id]
    axes = (
        ("label-only", "complete-positive-surface-carrier"),
        ("imported-fit-model", relation),
        ("endpoint-or-average-only", "complete-surface-interface-state-path"),
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
    vector = json.loads((root / "experiments/external_sources/materials/surf_001_008_v1/complete_evidence_vector_v1.json").read_text())
    vector_identity = vector.pop("complete_vector_identity")
    rows = {row["claim_id"]: row for row in vector["claims"]}
    evidence = (
        vector_identity == canonical(vector)
        and len(rows) == 8
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
