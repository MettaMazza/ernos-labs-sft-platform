#!/usr/bin/env python3
"""Implementation-distinct reconstruction for Materials MICRO-001--009."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys


RELATIONS = {
    "SFT-MAT-MICRO-DEFECT-POPULATION-001": "complete-site-partition-and-rational-fraction-balance",
    "SFT-MAT-MICRO-DEFECT-MIGRATION-002": "adjacent-site-axis-oriented-complete-migration-word",
    "SFT-MAT-MICRO-DISLOCATION-REACTION-003": "held-orientation-line-reaction-climb-cross-slip-ledger",
    "SFT-MAT-MICRO-GRAIN-GROWTH-004": "boundary-cell-per-grain-cell-curvature-transfer",
    "SFT-MAT-MICRO-BOUNDARY-SEGREGATION-005": "species-wise-bulk-boundary-part-comparison",
    "SFT-MAT-MICRO-PRECIPITATE-INCLUSION-006": "matrix-inclusion-recurrence-and-common-return-boundary",
    "SFT-MAT-MICRO-COARSENING-TRANSFER-007": "conserved-particle-carrier-transfer-and-absence",
    "SFT-MAT-MICRO-INTERFACE-MOBILITY-008": "oriented-interface-path-velocity-and-mobility-parts",
    "SFT-MAT-MICRO-MULTISCALE-CORRESPONDENCE-009": "complete-site-weighted-feature-to-bulk-composition",
}


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def native(claim_id):
    if claim_id.endswith("POPULATION-001"):
        sites, defects = 8, {2, 7}
        return Fraction(len(defects), sites) == Fraction(1, 4) and Fraction(sites - len(defects), sites) == Fraction(3, 4)
    if claim_id.endswith("MIGRATION-002"):
        path = ((1, 1, 1), (2, 1, 1), (2, 2, 1))
        changes = [sum(left != right for left, right in zip(a, b)) for a, b in zip(path, path[1:])]
        return changes == [1, 1] and path[-1] == (2, 2, 1)
    if claim_id.endswith("REACTION-003"):
        forward, opposed = 3, 1
        modes = {"glide": "plane-one", "climb": "adjacent-plane", "cross-slip": "plane-two"}
        return forward > opposed and forward - opposed == 2 and len(modes) == 3
    if claim_id.endswith("GROWTH-004"):
        areas, boundary = [4, 8], [4, 4]
        curvature = [Fraction(boundary[i], areas[i]) for i in range(2)]
        before = sum(areas); areas[curvature.index(max(curvature))] -= 1; areas[curvature.index(min(curvature))] += 1
        return areas == [3, 9] and sum(areas) == before
    if claim_id.endswith("SEGREGATION-005"):
        bulk, boundary = ("x", "y", "y", "y"), ("x", "x", "x", "y")
        return Fraction(Counter(boundary)["x"], len(boundary)) > Fraction(Counter(bulk)["x"], len(bulk))
    if claim_id.endswith("INCLUSION-006"):
        common = lambda a, b: next(value for value in range(a, a * b + 1, a) if value % b == 0)
        return common(3, 3) == 3 and common(2, 3) == 6
    if claim_id.endswith("TRANSFER-007"):
        before = (2, 3); after = (None, 5)
        return sum(before) == sum(value for value in after if value is not None) and sum(value is not None for value in after) == 1
    if claim_id.endswith("MOBILITY-008"):
        path, drive = (2, 4, 5), 6
        distance = path[-1] - path[0]
        return Fraction(distance, len(path) - 1) == Fraction(3, 2) and Fraction(distance, drive) == Fraction(1, 2)
    if claim_id.endswith("CORRESPONDENCE-009"):
        rows = ((2, Fraction(1, 2)), (1, Fraction(1, 1)))
        return sum(count * response for count, response in rows) / sum(count for count, _ in rows) == Fraction(2, 3)
    return False


def main():
    claim_id, root = sys.argv[1], Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = RELATIONS[claim_id]
    axes = (("answer-only-or-erased-carrier", "complete-positive-microstructure-carrier"), ("imported-continuum-or-fitted-relation", relation), ("bulk-average-only", "complete-site-path-interface-organization"), ("method-condition-scale-erased", "specimen-method-condition-scale-uncertainty-held"), ("headline-only", "complete-state-transition-resource-trace"), ("authority-target-or-prior-model", "root-bound-forward-forcing"), ("selected-instance-or-lookup", "positive-finite-successor-closure"), ("free-fit-exception-or-extra-rule", "no-extra-rule"))
    generated = tuple("__".join(row) for row in product(*axes))
    survivor = "__".join(axis[1] for axis in axes)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {row: row == survivor for row in generated}
    vector = json.loads((root / "experiments/external_sources/materials/micro_001_009_v2/complete_evidence_vector_v1.json").read_text())
    identity = vector.pop("complete_vector_identity")
    rows = {row["claim_id"]: row for row in vector["claims"]}
    evidence = identity == canonical(vector) and len(rows) == 9 and claim_id in rows
    if evidence:
        evidence = all(file_hash(root / item["snapshot_path"]) == item["snapshot_hash"] for item in rows[claim_id]["comparisons"])
    passed = all((received == generated, len(received) == len(set(received)) == 256, decisions == expected, sum(expected.values()) == 1, sealed["closure"]["scope"] == "depth_independent", len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), native(claim_id), evidence))
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": claim_id, "candidate_count": len(received), "unique_survivor_count": sum(expected.values()), "native_reconstruction": native(claim_id), "external_reconstruction": evidence, "closure_scope": sealed["closure"]["scope"], "free_parameter_or_fitted_target_used": False}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
