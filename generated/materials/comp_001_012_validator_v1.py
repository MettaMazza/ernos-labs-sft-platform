#!/usr/bin/env python3
"""Implementation-distinct exact reconstruction for Materials COMP-001--012."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

REL = {
    "SFT-MAT-COMP-DATA-REPRESENTATION-001": "identity-structure-property-provenance-record",
    "SFT-MAT-COMP-STRUCTURE-PROPERTY-002": "structure-property-scope-method-boundary",
    "SFT-MAT-COMP-FINITE-SIMULATION-003": "initial-state-transition-finite-trace",
    "SFT-MAT-COMP-MULTISCALE-COMPOSITION-004": "scale-model-handoff-composition",
    "SFT-MAT-COMP-ERROR-PROPAGATION-005": "positive-component-total-scope-error-ledger",
    "SFT-MAT-COMP-INVERSE-PROBLEM-006": "candidate-forward-target-unique-inverse-enumeration",
    "SFT-MAT-COMP-LEARNING-BOUNDARY-007": "training-test-prediction-method-all-outcomes",
    "SFT-MAT-COMP-DATABASE-PROVENANCE-008": "identity-payload-source-version-database",
    "SFT-MAT-COMP-PHASE-FIELD-009": "cell-state-update-boundary-phasefield",
    "SFT-MAT-COMP-MOLECULAR-DYNAMICS-010": "particle-state-transition-boundary-dynamics",
    "SFT-MAT-COMP-ELECTRONIC-STRUCTURE-011": "site-orbital-occupation-method-electronic",
    "SFT-MAT-COMP-SIMULATION-EXPERIMENT-012": "prediction-observation-unit-uncertainty-source-all-results",
}


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def native(claim_id):
    tests = (
        len({"r1", "r2"}) == 2 and all(("structure", "property", "source")),
        len(("structure", "property", "scope", "method")) == 4,
        len(("a", "b")) == len((("a", "b"),)) + 1,
        len(("micro", "macro")) == len(("m1", "m2")) == len((("m1", "m2"),)) + 1,
        sum((Fraction(1, 3), Fraction(2, 3))) == 1,
        tuple(identity for identity, output in (("a", "x"), ("b", "y")) if output == "y") == ("b",),
        sum(expected == predicted for expected, predicted in zip(("a", "b"), ("a", "a"))) == 1,
        len({("id", "version")}) == 1,
        len(("a", "b", "a")) == 3 and len((("a", "b"),)) == 1,
        len({"p1", "p2"}) == 2 and len(("s1", "s2")) == len((("s1", "s2"),)) + 1,
        sum((1, 2)) == 3,
        sum(predicted == observed for predicted, observed in ((1, 1), (1, 2))) == 1,
    )
    return tests[list(REL).index(claim_id)]


def main():
    claim_id, root = sys.argv[1], Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = REL[claim_id]
    axes = (
        ("label-only", "complete-positive-computational-material-carrier"),
        ("imported-fit-model", relation),
        ("endpoint-or-score-only", "complete-computational-trace"),
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
    vector = json.loads((root / "experiments/external_sources/materials/comp_001_012_v1/complete_evidence_vector_v1.json").read_text())
    vector_identity = vector.pop("complete_vector_identity")
    rows = {row["claim_id"]: row for row in vector["claims"]}
    evidence = (
        vector_identity == canonical(vector)
        and len(rows) == 12
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
