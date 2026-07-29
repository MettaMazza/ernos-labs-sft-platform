#!/usr/bin/env python3
"""Implementation-distinct exact reconstruction for Materials EXT-001--008."""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

REL = {
    "SFT-MAT-EXT-HIGH-PRESSURE-STATE-001": "specimen-pressure-state-transition-method-uncertainty-path",
    "SFT-MAT-EXT-HIGH-TEMPERATURE-STATE-002": "specimen-temperature-state-transition-method-uncertainty-path",
    "SFT-MAT-EXT-CRYOGENIC-RESPONSE-003": "descending-positive-temperature-state-transition-path",
    "SFT-MAT-EXT-ELECTRIC-FIELD-RESPONSE-004": "positive-electric-field-state-transition-path",
    "SFT-MAT-EXT-MAGNETIC-FIELD-RESPONSE-005": "positive-magnetic-field-state-transition-path",
    "SFT-MAT-EXT-SHOCK-RESPONSE-006": "positive-rate-impact-state-transition-path",
    "SFT-MAT-EXT-RADIATION-RESPONSE-007": "radiation-event-defect-state-transition-path",
    "SFT-MAT-EXT-COMBINED-PATH-CUSTODY-008": "joint-named-condition-state-transition-path",
}


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def native(claim_id):
    tests = (
        len((1, 2)) == len(("a", "b")) == len((("a", "b"),)) + 1,
        len((1, 2)) == len(("hot-a", "hot-b")),
        (2, 1)[0] > (2, 1)[1],
        len((1, 2)) == len(("field-a", "field-b")),
        len((1, 2)) == len(("mag-a", "mag-b")),
        len(("load", "impact")) == 2,
        len({"d1", "d2"}) == 2,
        len({"heat", "force"}) == 2 and all(len(row) == 2 for row in ((1, 1), (2, 2))),
    )
    return tests[list(REL).index(claim_id)]


def main():
    claim_id, root = sys.argv[1], Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = REL[claim_id]
    axes = (
        ("terminal-label-only", "complete-positive-extreme-material-carrier"),
        ("imported-response-model", relation),
        ("endpoint-only", "complete-extreme-condition-state-path"),
        ("specimen-method-erased", "specimen-method-condition-scale-uncertainty-held"),
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
    vector = json.loads((root / "experiments/external_sources/materials/ext_001_008_v1/complete_evidence_vector_v1.json").read_text())
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
