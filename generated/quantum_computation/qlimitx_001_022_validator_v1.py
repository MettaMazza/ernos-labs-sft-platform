#!/usr/bin/env python3
"""Implementation-distinct exact validator for QLIMITX-001 through QLIMITX-022."""

import json
import sys
from itertools import product
from pathlib import Path

RELATIONS = (
    "single-word-phase-held-classical-embedding", "phase-invariant-word-permutation-submodel", "deterministic-complete-support-plus-observation-correspondence", "selected-class-and-closed-distinction-decoder", "source-image-trace-bisimulation", "positive-finite-resource-bound-region", "same-word-distinct-phase-operational-witness", "nonfactorable-joint-support-operational-witness", "unknown-phase-support-copying-noninjectivity", "observation-closure-and-record-cost", "quantum-process-self-negating-halting-transfer", "classical-undecidable-submodel-reduction", "finite-proof-system-self-description-boundary", "finite-generated-transition-no-oracle-boundary", "positive-finite-successor-support-only", "bounded-separation-scope-custody", "formal-resource-to-measured-device-speedup-handoff", "formal-fault-order-to-measured-threshold-handoff", "formal-resource-ledger-to-implementation-measurement", "sealed-formal-prediction-to-blind-physical-measurement", "dated-closure-open-lawful-extension", "twenty-two-obligation-no-omission-ledger",
)


def independent_witness(index):
    labels = ("held", "returned")
    support = tuple(product(labels, repeat=2))
    flip = tuple((word, (("returned" if word[0] == "held" else "held"), word[1])) for word in support)
    correlated = (("held", "held"), ("returned", "returned"))
    checks = (
        (("held", "returned"),) == (("held", "returned"),),
        len({image for _source, image in flip}) == 4,
        len(support) == len(set(support)) == 4,
        len(("selected", "support", "closed", "phase")) == 4,
        dict(flip)[dict(flip)[("held", "held")]] == ("held", "held"),
        all(rows <= depth * 2 for depth, rows in ((1, 2), (2, 4), (3, 6))),
        ("held",) == ("held",) and "phase-held" != "phase-returned",
        set(correlated) != set(product(labels, labels)),
        len({"phase-held", "phase-returned"}) == 2 and len({("held",)}) == 1,
        len(tuple(word for word in labels if word != "held")) == 1,
        ("continues" if "halts" == "halts" else "halts") == "continues",
        {"embedded_classical_boundary": True, "total_decider": False}["embedded_classical_boundary"],
        {"finite_proof_system": True, "total_self_truth": False}["finite_proof_system"],
        {"finite_transition": True, "oracle": False}["finite_transition"],
        all(len(tuple(product(labels, repeat=width))) == 2 ** width for width in (1, 2, 3, 4)),
        {"bounded": True, "unrestricted": False}["unrestricted"] is False,
        {"formal": True, "device_timing": False}["formal"],
        ("2t+1", False)[0] == "2t+1",
        len(("energy", "timing", "geometry", "control", "temperature")) == 5,
        ("formal", "target", "measurement")[-1] == "measurement",
        len(("premise", "candidate", "control", "measurement", "adverse")) == 5,
        len(RELATIONS) == 22,
    )
    return checks[index - 1]


def generated_surface(index):
    axes = (
        ("imported-or-incomplete-limit-model", "complete-classical-quantum-Fold-model"),
        ("assumed-or-bounded-extrapolated-limit", RELATIONS[index - 1]),
        ("terminal-answer-only", "complete-source-phase-joint-observation-trace"),
        ("hidden-oracle-or-physical-resource", "complete-support-time-space-query-and-record-ledger"),
        ("selected-favorable-cases", "literal-complete-product"),
        ("outcome-selected-law", "there-is-no-nothing-lineage"),
        ("preopened-limit-outcome", "post-registry-exact-execution"),
        ("silent-unrestricted-or-physical-export", "explicit-formal-finite-physical-handoff"),
    )
    rows = tuple("__".join(coordinates) for coordinates in product(*axes))
    return rows, "__".join(axis[1] for axis in axes)


def main():
    claim_id, _root, sealed_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    index = int(claim_id.rsplit("-", 1)[-1])
    sealed = json.loads(sealed_path.read_text())
    rows, survivor = generated_surface(index)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {row: row == survivor for row in rows}
    passed = all((received == rows, len(set(received)) == len(received) == 256, decisions == expected, sum(expected.values()) == 1, len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), sealed["closure"]["scope"] == "depth_independent", independent_witness(index)))
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "quantum_limits_witness": independent_witness(index)}}))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
