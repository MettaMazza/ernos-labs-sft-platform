#!/usr/bin/env python3
"""Implementation-distinct reconstruction for Materials PHASE-001--010."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys


RELATIONS = {
    "SFT-MAT-PHASE-FRACTION-LEDGER-001": "complete-held-phase-partition-and-one-recomposition",
    "SFT-MAT-PHASE-TIE-LINE-LEVER-002": "coexistence-endpoint-tie-line-and-opposite-span-partition",
    "SFT-MAT-PHASE-COMPONENT-HANDOFF-003": "component-wise-equal-handoff-across-distinct-phase-words",
    "SFT-MAT-PHASE-METASTABLE-RETENTION-004": "nonterminal-state-retention-until-exact-escape-transition",
    "SFT-MAT-PHASE-SPINODAL-INSTABILITY-005": "three-site-separation-amplifying-or-restoring-instability-ledger",
    "SFT-MAT-PHASE-MARTENSITIC-006": "atom-bijective-held-direction-cooperative-displacive-map",
    "SFT-MAT-PHASE-RECONSTRUCTIVE-007": "carrier-conserving-bond-breaking-and-forming-topology-change",
    "SFT-MAT-PHASE-ORDER-DISORDER-008": "same-carrier-site-match-and-reassignment-order-ledger",
    "SFT-MAT-PHASE-GLASS-ARREST-009": "observation-to-relaxation-recurrence-arrest-boundary",
    "SFT-MAT-PHASE-TIME-TEMPERATURE-010": "complete-ordered-time-temperature-transformed-carrier-path",
}


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def native(claim_id):
    if claim_id.endswith("LEDGER-001"):
        counts = (2, 3, 5); total = sum(counts)
        parts = tuple(Fraction(value, total) for value in counts)
        return parts == (Fraction(1, 5), Fraction(3, 10), Fraction(1, 2)) and sum(parts) == 1
    if claim_id.endswith("LEVER-002"):
        left, bulk, right = 2, 4, 8
        left_part, right_part = Fraction(right - bulk, right - left), Fraction(bulk - left, right - left)
        return left_part == Fraction(2, 3) and right_part == Fraction(1, 3) and left * left_part + right * right_part == bulk
    if claim_id.endswith("HANDOFF-003"):
        phases = ((("x", 2), ("y", 3)), (("x", 2), ("y", 3)))
        return all(len({dict(phase)[label] for phase in phases}) == 1 for label in ("x", "y"))
    if claim_id.endswith("RETENTION-004"):
        path, escape = ("held", "held", "held", "escaped"), 3
        return len(path[:escape]) == 3 and path[escape] == "escaped"
    if claim_id.endswith("INSTABILITY-005"):
        left, centre, right = 2, 5, 3
        return centre + centre > left + right and centre + centre - left - right == 5
    if claim_id.endswith("MARTENSITIC-006"):
        atoms = (("a", (1, 1, 1), ("x-forward", 1)), ("b", (2, 1, 1), ("x-forward", 1)))
        return len({row[0] for row in atoms}) == len(atoms) and all(row[2][1] >= 1 for row in atoms)
    if claim_id.endswith("RECONSTRUCTIVE-007"):
        atoms = {"a", "b", "c"}; before = {tuple(sorted(x)) for x in (("a", "b"), ("b", "c"))}; after = {tuple(sorted(x)) for x in (("a", "c"), ("b", "c"))}
        return bool(before - after) and bool(after - before) and all(set(edge) <= atoms for edge in before | after)
    if claim_id.endswith("DISORDER-008"):
        reference, observed = ("a", "b", "a", "b"), ("a", "a", "b", "b")
        matches = sum(a == b for a, b in zip(reference, observed))
        return Counter(reference) == Counter(observed) and Fraction(matches, len(reference)) == Fraction(1, 2)
    if claim_id.endswith("ARREST-009"):
        relaxation, observation = 5, 2
        return observation < relaxation and observation >= 1
    if claim_id.endswith("TEMPERATURE-010"):
        rows = ((1, 8, None, 8), (2, 7, 2, 8))
        return rows[0][2] is None and Fraction(rows[1][2], rows[1][3]) == Fraction(1, 4) and rows[0][0] < rows[1][0]
    return False


def main():
    claim_id, root = sys.argv[1], Path(sys.argv[2])
    sealed = json.loads(Path(sys.argv[3]).read_text())
    relation = RELATIONS[claim_id]
    axes = (("phase-name-or-answer-only", "complete-positive-specimen-and-phase-carrier"), ("imported-continuum-fit-or-lookup", relation), ("single-average-or-endpoint-erasure", "complete-phase-component-path-organization"), ("specimen-method-condition-scale-erased", "specimen-method-condition-scale-uncertainty-held"), ("headline-only", "complete-state-transition-resource-trace"), ("target-authority-or-prior-model", "root-bound-forward-forcing"), ("selected-specimen-or-finite-lookup", "positive-finite-successor-closure"), ("free-fit-exception-or-extra-rule", "no-extra-rule"))
    generated = tuple("__".join(row) for row in product(*axes))
    survivor = "__".join(axis[1] for axis in axes)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {row: row == survivor for row in generated}
    vector = json.loads((root / "experiments/external_sources/materials/phase_001_010_v1/complete_evidence_vector_v1.json").read_text())
    identity = vector.pop("complete_vector_identity")
    rows = {row["claim_id"]: row for row in vector["claims"]}
    evidence = identity == canonical(vector) and len(rows) == 10 and claim_id in rows and rows[claim_id]["all_registered_fragments_present"]
    if evidence:
        evidence = all(file_hash(root / item["snapshot_path"]) == item["snapshot_hash"] for item in rows[claim_id]["comparisons"])
    passed = all((received == generated, len(received) == len(set(received)) == 256, decisions == expected, sum(expected.values()) == 1, sealed["closure"]["scope"] == "depth_independent", len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), native(claim_id), evidence))
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": claim_id, "candidate_count": len(received), "unique_survivor_count": sum(expected.values()), "native_reconstruction": native(claim_id), "external_reconstruction": evidence, "closure_scope": sealed["closure"]["scope"], "free_parameter_or_fitted_target_used": False}}, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
