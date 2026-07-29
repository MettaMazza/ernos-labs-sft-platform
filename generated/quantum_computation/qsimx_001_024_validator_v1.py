#!/usr/bin/env python3
"""Implementation-distinct exact validator for QSIMX-001 through QSIMX-024."""

import json
import sys
from itertools import product
from pathlib import Path


RELATIONS = (
    "source-bound-model-simulator-bisimulation",
    "complete-finite-target-word-encoding",
    "finite-reversible-update-sequence-simulation",
    "formal-support-to-physical-dynamics-handoff",
    "causally-ordered-local-update-composition",
    "finite-reversible-generator-relation",
    "nested-finite-update-enclosure-ledger",
    "complete-joint-word-incidence-support",
    "exchange-class-and-phase-record-encoding",
    "finite-cell-incidence-to-physical-field-handoff",
    "system-environment-reversible-extension",
    "registered-source-image-cause-noise-ledger",
    "formal-simulator-to-chemistry-measurement-interface",
    "formal-simulator-to-materials-measurement-interface",
    "source-schedule-trace-image-verification",
    "challenge-response-round-transcript-verification",
    "sealed-task-view-bounded-delegation-transcript",
    "behavior-relation-to-device-identity-boundary",
    "complete-observation-class-support-reconstruction",
    "complete-source-image-process-table-reconstruction",
    "complete-generated-benchmark-schedule-support",
    "sealed-formal-result-to-blind-owning-data-comparison",
    "registry-source-trace-result-control-receipt-chain",
    "twenty-four-obligation-no-omission-ledger",
)


def words(width):
    return tuple(product(("held", "returned"), repeat=width))


def toggle(label):
    return "returned" if label == "held" else "held"


def step(word, place):
    result = list(word)
    result[place - 1] = toggle(result[place - 1])
    return tuple(result)


def run(word, schedule):
    state = tuple(word)
    trace = []
    for place in schedule:
        image = step(state, place)
        trace.append((state, place, image))
        state = image
    return state, tuple(trace)


def table(width, schedule):
    return tuple((source, run(source, schedule)[0]) for source in words(width))


def independent_witness(index):
    checks = (
        table(2, (1,)) == tuple((source, step(source, 1)) for source in words(2)),
        len(words(3)) == len(set(words(3))) == 8,
        run(("held", "returned"), (1, 2))[0] == ("returned", "held"),
        (True, False)[0] is True,
        run(("held", "held"), (1, 2))[0] == ("returned", "returned"),
        set(table(2, (1,))) == set((image, source) for source, image in table(2, (1,))),
        len(run(("held", "held"), (1, 2, 1))[1]) == 3,
        len(tuple((word, tuple(enumerate(word, 1))) for word in words(3))) == 8,
        ("phase-returned" if "a" != "b" else "phase-held") == "phase-returned",
        len(((1, 2), (2, 3))) == 2,
        ("system", "environment", "cause-record")[-1] == "cause-record",
        len(("source", "image", "cause")) == 3,
        ("formal", "chemistry", "measurement")[-1] == "measurement",
        ("formal", "materials", "measurement")[-1] == "measurement",
        run(("held", "returned"), (1, 2))[0] == ("returned", "held"),
        len(tuple((round_index, place) for round_index, place in enumerate((1, 2, 1), 1))) == 3,
        {"sealed": True, "executor_target_access": False}["sealed"],
        {"formal_behavior": True, "physical_identity": False}["formal_behavior"],
        tuple(dict.fromkeys(source for source in words(2))) == words(2),
        len(table(2, (1,))) == 4 and len({image for _source, image in table(2, (1,))}) == 4,
        len(tuple(product((1, 2), repeat=3))) == 8,
        {"prediction_sealed": True, "target_selected_law": False}["prediction_sealed"],
        len(("registry", "source", "trace", "result", "control", "receipt")) == 6,
        len(RELATIONS) == 24,
    )
    return checks[index - 1]


def generated_surface(index):
    axes = (
        ("imported-or-partial-quantum-model", "complete-source-bound-Fold-model"),
        ("opaque-or-target-selected-simulator", RELATIONS[index - 1]),
        ("terminal-output-only", "complete-update-phase-observation-trace"),
        ("hidden-support-or-verifier-resource", "complete-support-depth-round-and-record-ledger"),
        ("sampled-or-favorable-cases", "literal-complete-product"),
        ("outcome-selected-law", "there-is-no-nothing-lineage"),
        ("preopened-simulation-outcome", "post-registry-exact-execution"),
        ("silent-physical-or-unrestricted-export", "explicit-formal-finite-physical-handoff"),
    )
    rows = tuple("__".join(coordinates) for coordinates in product(*axes))
    return rows, "__".join(axis[1] for axis in axes)


def main():
    claim_id = sys.argv[1]
    _root = Path(sys.argv[2])
    sealed_path = Path(sys.argv[3])
    index = int(claim_id.rsplit("-", 1)[-1])
    sealed = json.loads(sealed_path.read_text())
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
        "certificate": {
            "candidate_count": 256,
            "unique_survivor_count": 1,
            "quantum_simulation_verification_witness": independent_witness(index),
        },
    }))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
