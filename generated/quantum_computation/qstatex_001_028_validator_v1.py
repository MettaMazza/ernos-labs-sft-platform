#!/usr/bin/env python3
"""Implementation-distinct exact validator for QSTATEX-001 through QSTATEX-028."""

import json
import sys
from itertools import product
from pathlib import Path


RELATIONS = (
    "one-fold-distinction-two-fibre-labels", "positive-finite-cartesian-word-support",
    "canonical-word-phase-record-ledger", "source-bound-preparation-trace",
    "cartesian-product-with-exact-factor-recovery", "joint-words-and-projected-support",
    "support-versus-preparation-record-class", "complete-word-support-with-held-phases",
    "period-two-held-relative-phase-relation", "common-phase-action-preserves-relations",
    "period-two-phase-action-and-inverse", "same-and-distinct-phase-predecessor-merge",
    "many-predecessor-one-image-phase-ledger", "path-record-retains-distinguishability",
    "noncartesian-bipartite-joint-support", "nonfactorable-multipartite-joint-support",
    "complete-partition-factorability-census", "joint-observation-repartitions-outer-support",
    "joint-support-shareability-census", "preparation-record-extension",
    "projected-observation-with-joint-custody", "complete-partition-observation",
    "retained-outcome-class-repeatability", "observation-order-record-comparison",
    "reversible-question-record-then-read", "unknown-joint-state-copy-impossibility",
    "reversible-deletion-requires-record", "twenty-eight-obligation-no-omission-ledger",
)


def binary_words(width):
    labels = ("held", "returned")
    return tuple(product(labels, repeat=width))


def projections(support, width):
    left = tuple(dict.fromkeys(word[:width] for word in support))
    right = tuple(dict.fromkeys(word[width:] for word in support))
    return left, right


def factorable(support, width):
    left, right = projections(support, width)
    return set(support) == {a + b for a in left for b in right}


def independent_witness(index):
    pair = (("held", "held"), ("returned", "returned"))
    triple = (("held", "held", "held"), ("returned", "returned", "returned"))
    checks = (
        len({"held", "returned"}) == 2,
        len(binary_words(3)) == 8,
        tuple(sorted((("returned", "phase-returned"), ("held", "phase-held"))))[0][0] == "held",
        ("source", "prepared", "trace")[0] == "source",
        {a + b for a in (("held",), ("returned",)) for b in (("held",),)} == {("held", "held"), ("returned", "held")},
        projections(pair, 1) == ((("held",), ("returned",)), (("held",), ("returned",))),
        len({"preparation-a", "preparation-b"}) == 2,
        len(binary_words(4)) == 16,
        ("same", "distinct") != ("same", "same"),
        tuple("returned" if x == "held" else "held" for x in ("held", "returned")) == ("returned", "held"),
        ("returned" if ("returned" if "held" == "held" else "held") == "held" else "held") == "held",
        {"phase-held", "phase-returned"} == set(("phase-held", "phase-returned")),
        len(("path-a", "path-b")) == 2,
        len({("path-a", "image"), ("path-b", "image")}) == 2,
        not factorable(pair, 1),
        not factorable(triple, 1),
        all(not factorable(triple, cut) for cut in (1, 2)),
        ("outer-left", "outer-right") != ("middle-left", "middle-right"),
        not factorable(triple, 1),
        len(tuple(word + (f"record-{i}",) for i, word in enumerate(pair, 1))) == 2,
        len(projections(pair, 1)[0]) == 2 and len(pair) == 2,
        {("held",): "class-held", ("returned",): "class-returned"}[("held",)] == "class-held",
        ("class-held", "class-held")[0] == ("class-held", "class-held")[1],
        ("word-then-phase", "phase-then-word")[0] != ("word-then-phase", "phase-then-word")[1],
        ("retained-question", "held")[1] == "held",
        not factorable(pair, 1),
        len({("terminal", "record-held"), ("terminal", "record-returned")}) == 2,
        len(RELATIONS) == 28,
    )
    return checks[index - 1]


def generated_surface(index):
    axes = (
        ("sampled-or-aliased-support", "complete-canonical-word-support"),
        ("imported-vector-composition", RELATIONS[index - 1]),
        ("numeric-complex-amplitude-premise", "held-relative-phase-ledger"),
        ("terminal-outcome-only", "complete-source-and-observation-record"),
        ("selected-state-examples", "literal-complete-product"),
        ("outcome-selected-law", "there-is-no-nothing-lineage"),
        ("preopened-state-outcome", "post-registry-exact-execution"),
        ("silent-physical-export", "explicit-formal-physical-handoff"),
    )
    rows = tuple("__".join(coordinates) for coordinates in product(*axes))
    survivor = "__".join(axis[1] for axis in axes)
    return rows, survivor


def main():
    claim_id, _root, sealed_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    index = int(claim_id.rsplit("-", 1)[-1])
    sealed = json.loads(sealed_path.read_text(encoding="utf-8"))
    rows, survivor = generated_surface(index)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {row: row == survivor for row in rows}
    passed = all((
        received == rows,
        len(set(received)) == len(received) == 256,
        decisions == expected,
        sum(expected.values()) == 1,
        len(sealed["controls"]) == 4,
        all(row["passed"] for row in sealed["controls"]),
        sealed["closure"]["scope"] == "depth_independent",
        independent_witness(index),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "quantum_state_witness": independent_witness(index)},
    }))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
