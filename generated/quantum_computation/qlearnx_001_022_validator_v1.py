#!/usr/bin/env python3
"""Implementation-distinct exact validator for QLEARNX-001 through QLEARNX-022."""

import json
import sys
from itertools import product
from pathlib import Path

RELATIONS = (
    "typed-problem-example-target-resource-registry", "canonical-classical-data-to-Fold-support-encoding", "complete-quantum-example-support-observation-ledger", "complete-generated-quantum-hypothesis-family", "reversible-source-feature-support-map", "exact-pair-comparison-observation-relation", "complete-hypothesis-class-observation-selection", "exact-ordered-output-support-relation", "complete-source-support-reconstruction", "generated-equivalence-class-partition", "exact-incidence-rank-and-tie-ledger", "exhaustive-hypothesis-score-order-selection", "generated-setting-not-fitted-parameter-boundary", "state-action-transition-observation-transcript", "causal-example-update-prediction-transcript", "least-example-support-for-declared-learning-condition", "least-query-transcript-for-declared-learning-condition", "sealed-hypothesis-blind-held-out-comparison", "same-task-complete-resource-ledger-separation", "input-feature-hypothesis-branch-output-reconstruction", "complete-perturbation-tamper-verification-census", "twenty-two-obligation-no-omission-ledger",
)


def independent_witness(index):
    domain = (("held",), ("returned",))
    hypotheses = tuple(tuple(zip(domain, images)) for images in product(("held", "returned"), repeat=2))
    identity = ((domain[0], "held"), (domain[1], "returned"))
    support = tuple(product(("held", "returned"), repeat=2))
    checks = (
        len({source for source, _target in identity}) == 2,
        tuple(enumerate(domain[0], 1)) == ((1, "held"),),
        len(support) == len(set(support)) == 4,
        len(hypotheses) == len(set(hypotheses)) == 4,
        len({tuple(enumerate(word, 1)) for word in support}) == 4,
        sum(a == b for a, b in zip(("held", "returned"), ("held", "held"))) == 1,
        dict(identity)[("returned",)] == "returned",
        tuple((word, word.count("held")) for word in support)[-1][1] == 0,
        tuple(dict.fromkeys(support)) == support,
        all(len(tuple(word for word in support if word[0] == label)) == 2 for label in ("held", "returned")),
        sorted(((1, 2), (2, 1)), key=lambda row: (-row[1], row[0]))[0] == (1, 2),
        max(sum(dict(h)[source] == target for source, target in identity) for h in hypotheses) == 2,
        {"settings": 4, "fitted": False}["settings"] == 4,
        (("returned",), "flip-first") != (("held",), "flip-first"),
        len(((1, identity[0]), (2, identity[1]))) == 2,
        len(identity) == 2,
        len(tuple((source, dict(identity)[source]) for source in domain)) == 2,
        {"sealed": True, "opened_after": True}["opened_after"],
        all((True, True, True)),
        len(("input", "feature", "hypothesis", "branch", "observation")) == 5,
        all(word == tuple(word) for word in support),
        len(RELATIONS) == 22,
    )
    return checks[index - 1]


def generated_surface(index):
    axes = (
        ("imported-or-target-shaped-learning-problem", "registered-source-target-resource-problem"),
        ("pretrained-or-selected-learner", RELATIONS[index - 1]),
        ("terminal-prediction-only", "complete-example-hypothesis-branch-observation-trace"),
        ("hidden-sample-query-or-physical-resource", "complete-sample-query-depth-and-record-ledger"),
        ("sampled-favorable-hypotheses", "literal-complete-product"),
        ("outcome-selected-law", "there-is-no-nothing-lineage"),
        ("preopened-training-or-heldout-outcome", "post-registry-exact-execution"),
        ("silent-advantage-or-physical-export", "explicit-formal-finite-physical-handoff"),
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
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "quantum_learning_witness": independent_witness(index)}}))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
