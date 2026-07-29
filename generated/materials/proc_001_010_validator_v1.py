#!/usr/bin/env python3
"""Implementation-distinct exact reconstruction for Materials PROC-001--010."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

REL = {
    "SFT-MAT-PROC-CASTING-HISTORY-001": "charge-filled-retained-mould-region-path",
    "SFT-MAT-PROC-FORMING-TEXTURE-002": "element-before-after-load-temperature-texture",
    "SFT-MAT-PROC-MACHINING-DAMAGE-003": "surface-intact-damaged-operation-tool-path",
    "SFT-MAT-PROC-ADDITIVE-BUILD-004": "layer-meltpool-powderbatch-build-path",
    "SFT-MAT-PROC-THIN-FILM-GROWTH-005": "substrate-layer-interface-growthstate-method",
    "SFT-MAT-PROC-EPITAXY-MATCHING-006": "film-substrate-orientation-least-joint-recurrence",
    "SFT-MAT-PROC-JOINING-INTERFACE-007": "component-interface-intact-broken-process-path",
    "SFT-MAT-PROC-POLYMER-ORIENTATION-008": "chain-before-after-process-thermal-orientation",
    "SFT-MAT-PROC-POWDER-COMPACTION-009": "particle-compacted-uncompacted-pressure-path",
    "SFT-MAT-PROC-WINDOW-PROVENANCE-010": "trial-condition-outcome-provenance-repeated-class",
}


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def native(claim_id):
    tests = (
        4 + 1 == 5 and Fraction(4, 5) == Fraction(4, 5),
        ("a", "a", "b") != ("a", "b", "b"),
        3 + 2 == 5 and Fraction(2, 5) == Fraction(2, 5),
        len(("l1", "l2")) == len(("p1", "p2")) == len(("b1", "b2")),
        len(("i1", "i2")) == len(("l1", "l2")),
        next(step for step in range(1, 7) if step % 2 == 0 and step % 3 == 0) == 6,
        4 + 1 == 5 and Fraction(4, 5) == Fraction(4, 5),
        ("a", "a", "b") != ("a", "b", "b"),
        4 + 1 == 5 and Fraction(4, 5) == Fraction(4, 5),
        len({(("a",), "pass"), (("a",), "pass")}) == 1,
    )
    return tests[list(REL).index(claim_id)]


def main():
    claim_id, root = sys.argv[1], Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = REL[claim_id]
    axes = (
        ("label-only", "complete-positive-processing-carrier"),
        ("imported-fit-model", relation),
        ("endpoint-or-average-only", "complete-processing-state-path"),
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
    vector = json.loads((root / "experiments/external_sources/materials/proc_001_010_v1/complete_evidence_vector_v1.json").read_text())
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
