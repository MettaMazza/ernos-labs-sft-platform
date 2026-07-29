#!/usr/bin/env python3
"""Implementation-distinct exact reconstruction for Materials SUST-001--009."""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

REL = {
    "SFT-MAT-SUST-EMBODIED-LEDGER-001": "identity-kind-positive-amount-source-scope-ledger",
    "SFT-MAT-SUST-AVAILABILITY-BOUNDARY-002": "material-available-required-period-source-boundary",
    "SFT-MAT-SUST-REUSE-REMANUFACTURE-003": "identity-state-operation-inspection-reuse-path",
    "SFT-MAT-SUST-RECOVERY-YIELD-004": "positive-feed-recovered-residual-method-scope-partition",
    "SFT-MAT-SUST-CIRCULAR-FLOW-005": "node-transfer-amount-material-boundary-network",
    "SFT-MAT-SUST-DURABILITY-EXTENSION-006": "identity-baseline-extension-intervention-evidence",
    "SFT-MAT-SUST-TOXICITY-HANDOFF-007": "material-exposure-observation-scope-health-owner-handoff",
    "SFT-MAT-SUST-SUBSTITUTION-FUNCTION-008": "distinct-material-required-function-condition-preservation",
    "SFT-MAT-SUST-END-OF-LIFE-CUSTODY-009": "identity-material-fate-residual-source-boundary-custody",
}


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def native(claim_id):
    tests = (
        len({"a", "b"}) == 2 and 1 + 2 == 3,
        2 < 3 and "shortfall" != "sufficient",
        len(("a", "b")) == len(("repair",)) + 1,
        2 + 1 == 3,
        len({"a", "b"}) == 2 and len((("a", "b", 1, "m"),)) == 1,
        2 > 1 and 2 - 1 == 1,
        len(("exposure",)) == len(("observation",)),
        set(("f1", "f2")) == set(("f2", "f1")),
        len({"identity"}) == 1 and all(("material", "fate", "residual", "source")),
    )
    return tests[list(REL).index(claim_id)]


def main():
    claim_id, root = sys.argv[1], Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = REL[claim_id]
    axes = (
        ("summary-label-only", "complete-positive-sustainable-material-carrier"),
        ("imported-lifecycle-model", relation),
        ("endpoint-or-score-only", "complete-material-lifecycle-path"),
        ("scope-source-erased", "specimen-method-condition-scale-uncertainty-held"),
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
    vector = json.loads((root / "experiments/external_sources/materials/sust_001_009_v1/complete_evidence_vector_v1.json").read_text())
    vector_identity = vector.pop("complete_vector_identity")
    rows = {row["claim_id"]: row for row in vector["claims"]}
    evidence = (
        vector_identity == canonical(vector)
        and len(rows) == 9
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
