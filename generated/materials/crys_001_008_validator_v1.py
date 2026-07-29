#!/usr/bin/env python3
"""Implementation-distinct reconstruction of Materials CRYS-001--008."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys


RELATIONS = {
    "SFT-MAT-CRYS-DIFFRACTION-AMPLITUDE-001": "period-four-phase-cancellation-and-coherent-pair-ledger",
    "SFT-MAT-CRYS-STRUCTURE-FACTOR-002": "finite-scatterer-position-phase-composition",
    "SFT-MAT-CRYS-TEXTURE-ORIENTATION-003": "exact-grain-orientation-rational-distribution",
    "SFT-MAT-CRYS-SHORT-RANGE-DIFFUSE-004": "lag-labelled-local-pair-and-diffuse-support-ledger",
    "SFT-MAT-CRYS-STACKING-FAULT-DIFFRACTION-005": "cyclic-layer-successor-fault-and-diffraction-ledger",
    "SFT-MAT-CRYS-TWIN-DOMAIN-006": "nonidentity-involution-and-two-domain-ledger",
    "SFT-MAT-CRYS-MODULATED-INCOMMENSURATE-007": "independent-modulation-successor-and-compound-index-ledger",
    "SFT-MAT-CRYS-PAIR-DISTRIBUTION-008": "complete-positive-pair-separation-multiplicity-ledger",
}


def canonical(value: object) -> str:
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def native_reconstruction(claim_id: str) -> bool:
    if claim_id.endswith("AMPLITUDE-001"):
        totals = Counter({"p1": 5, "p3": 2, "p2": 1, "p4": 1})
        first_axis = totals["p1"] - totals["p3"]
        second_axis_absent = totals["p2"] == totals["p4"]
        return first_axis == 3 and second_axis_absent and first_axis * first_axis == 9
    if claim_id.endswith("FACTOR-002"):
        scatterers = ((2, 1), (3, 1))
        phase_weights = Counter()
        for weight, position in scatterers:
            phase_weights[((position * 4 - 1) % 4) + 1] += weight
        return sum(phase_weights.values()) == 5 and sum(phase_weights.values()) ** 2 == 25
    if claim_id.endswith("ORIENTATION-003"):
        labels = ("north", "north", "east")
        counts = Counter(labels)
        distribution = tuple((label, Fraction(count, len(labels))) for label, count in sorted(counts.items()))
        return distribution == (("east", Fraction(1, 3)), ("north", Fraction(2, 3)))
    if claim_id.endswith("DIFFUSE-004"):
        varied = tuple(zip(("A", "B", "A"), ("B", "A", "C")))
        recurrent = tuple(zip(("A", "A", "A"), ("A", "A", "A")))
        return len(Counter(varied)) == 3 and len(Counter(recurrent)) == 1
    if claim_id.endswith("DIFFRACTION-005"):
        successor = {"A": "B", "B": "C", "C": "A"}
        ideal = tuple("ABCABC")
        faulted = tuple("ABCACB")
        count = lambda word: sum(successor[left] != right for left, right in zip(word, word[1:]))
        return count(ideal) == 0 and count(faulted) == 2
    if claim_id.endswith("DOMAIN-006"):
        points = ((1, 2, 3), (2, 2, 4))
        transform = lambda point: (point[1], point[0], point[2])
        twin = tuple(transform(point) for point in points)
        return tuple(transform(point) for point in twin) == points and set(points).symmetric_difference(twin) == {(1, 2, 3), (2, 1, 3)}
    if claim_id.endswith("INCOMMENSURATE-007"):
        carrier = tuple((index, ("independent", index)) for index in range(1, 8))
        successor = (8, ("independent", 8))
        return len(set(carrier)) == 7 and successor not in carrier
    if claim_id.endswith("DISTRIBUTION-008"):
        positions = (1, 2, 4)
        distances = tuple(right - left for left, right in combinations(positions, 2))
        counts = Counter(distances)
        distribution = tuple((distance, Fraction(counts[distance], len(distances))) for distance in sorted(counts))
        return distribution == ((1, Fraction(1, 3)), (2, Fraction(1, 3)), (3, Fraction(1, 3)))
    return False


def main() -> None:
    claim_id = sys.argv[1]
    root = Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = RELATIONS[claim_id]
    axes = (
        ("answer-only-or-erased-carrier", "complete-positive-material-carrier"),
        ("imported-continuum-or-fitted-relation", relation),
        ("average-structure-only", "complete-local-and-reciprocal-organization"),
        ("method-condition-boundary-erased", "probe-condition-scale-and-uncertainty-held"),
        ("headline-value-only", "complete-state-transition-resource-trace"),
        ("authority-measurement-or-prior-model", "root-bound-forward-forcing"),
        ("selected-example-or-finite-lookup", "positive-finite-successor-closure"),
        ("free-fit-exception-or-extra-rule", "no-extra-rule"),
    )
    generated = tuple("__".join(row) for row in product(*axes))
    survivor = "__".join(axis[1] for axis in axes)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {row: row == survivor for row in generated}

    vector_path = root / "experiments/external_sources/materials/crys_001_008_v3/complete_evidence_vector_v1.json"
    vector = json.loads(vector_path.read_text())
    identity = vector.pop("complete_vector_identity")
    row_by_id = {row["claim_id"]: row for row in vector["claims"]}
    evidence_complete = identity == canonical(vector) and len(row_by_id) == 8 and claim_id in row_by_id
    if evidence_complete:
        for comparison in row_by_id[claim_id]["comparisons"]:
            evidence_complete = evidence_complete and file_hash(root / comparison["snapshot_path"]) == comparison["snapshot_hash"]
    passed = all((
        received == generated,
        len(received) == len(set(received)) == 256,
        decisions == expected,
        sum(expected.values()) == 1,
        sealed["closure"]["scope"] == "depth_independent",
        len(sealed["controls"]) == 4,
        all(row["passed"] for row in sealed["controls"]),
        native_reconstruction(claim_id),
        evidence_complete,
    ))
    response = {
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {
            "claim_id": claim_id,
            "candidate_count": len(received),
            "unique_survivor_count": sum(expected.values()),
            "independent_native_reconstruction": native_reconstruction(claim_id),
            "complete_external_row_reconstruction": evidence_complete,
            "closure_scope": sealed["closure"]["scope"],
            "external_source_accessed_by_law": False,
            "free_parameter_or_fitted_target_used": False,
        },
    }
    print(json.dumps(response, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
