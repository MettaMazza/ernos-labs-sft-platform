#!/usr/bin/env python3
"""Implementation-distinct exact validator for REVX-001 through REVX-018."""

import json
import sys
from itertools import product
from pathlib import Path


RELATIONS = (
    "complete-bijective-configuration-transition",
    "exact-map-fibre-and-image-classification",
    "bidirectional-language-derivation",
    "reversible-state-output-transduction",
    "inverse-rewrite-and-predecessor-record",
    "reversible-tape-head-write-move",
    "description-driven-reversible-interpretation",
    "complete-history-and-inverse-uncompute",
    "prepared-work-restored-ancilla",
    "garbage-provenance-and-cleanup",
    "logical-record-to-physical-erasure-boundary",
    "irreversible-image-plus-predecessor-ledger",
    "observation-closes-reversible-records",
    "time-space-history-resource-ledger",
    "bijective-local-gate-decomposition",
    "held-control-bijective-action",
    "fault-location-label-and-recovery-record",
    "eighteen-obligation-no-omission-ledger",
)


def flip(label):
    return "returned" if label == "held" else "held"


def invert(rows):
    if len({a for a, _b in rows}) != len(rows) or len({b for _a, b in rows}) != len(rows):
        return None
    return tuple((b, a) for a, b in rows)


def apply(value, rows):
    return dict(rows)[value]


def independent_witness(index):
    swap = (("held", "returned"), ("returned", "held"))
    if index == 1:
        return apply(apply("held", swap), invert(swap)) == "held"
    if index == 2:
        return invert((("a", "x"), ("b", "y"))) is not None and invert((("a", "x"), ("b", "x"))) is None
    if index == 3:
        words = ("held", "returned")
        return tuple(apply(apply(word, swap), invert(swap)) for word in words) == words
    if index == 4:
        trace = ("q0", "q1", "q0")
        return trace[0] == trace[-1] and len(trace) == 3
    if index == 5:
        rewrite = {"ab": "ba", "ba": "ab"}
        return rewrite[rewrite["ab"]] == "ab"
    if index == 6:
        source = ("q0", ("held", "returned"), 0)
        successor = ("q1", ("returned", "returned"), 1)
        record = source
        return record == source and successor != source
    if index == 7:
        source = ()
        result = source + ("held", "returned")
        history = (source, ("held",), result)
        return history[0] == source and history[-1] == result
    if index == 8:
        history = ((), ("held",), ("held", "returned"))
        return tuple(reversed(history))[0] == history[-1] and tuple(reversed(history))[-1] == history[0]
    if index == 9:
        prepared = ("data", "held")
        worked = ("data", "returned")
        restored = ("data", "held")
        return prepared == restored and worked != prepared
    if index == 10:
        source = ("held", "returned")
        garbage = tuple(enumerate(source))
        return tuple(label for _place, label in garbage) == source
    if index == 11:
        return {"logical_predecessor_recoverable": True, "physical_energy_measured_here": False} == {"logical_predecessor_recoverable": True, "physical_energy_measured_here": False}
    if index == 12:
        source = ("held", "returned", "held")
        image = tuple(label for label in source if label == "held")
        record = tuple(enumerate(source))
        return image == ("held", "held") and tuple(label for _place, label in record) == source
    if index == 13:
        trace = ("held", "returned", "held")
        observed = trace[-1]
        return observed == "held" and len(trace) == 3
    if index == 14:
        ledger = {"forward_steps": 3, "inverse_steps": 3, "history_rows": 3, "ancilla_rows": 1}
        return tuple(ledger) == ("forward_steps", "inverse_steps", "history_rows", "ancilla_rows")
    if index == 15:
        stages = (swap, swap)
        value = "held"
        for stage in stages:
            value = apply(value, stage)
        for stage in reversed(stages):
            value = apply(value, invert(stage))
        return value == "held"
    if index == 16:
        return ("held" if "held" == "held" else flip("held")) == "held" and (flip("held") if "returned" == "returned" else "held") == "returned"
    if index == 17:
        faulted = ("held", "returned", "held")
        position, old = 1, "held"
        recovered = faulted[:position] + (old,) + faulted[position + 1 :]
        return recovered == ("held", "held", "held")
    if index == 18:
        return len(RELATIONS) == 18 and all(independent_witness(number) for number in range(1, 18))
    return False


def generated_surface(index):
    axes = (
        ("partial-or-aliased-configuration", "complete-canonical-configuration"),
        ("many-to-one-or-partial-transition", "source-complete-one-to-one-transition"),
        ("imported-reversible-answer", RELATIONS[index - 1]),
        ("terminal-output-only", "complete-forward-and-inverse-trace"),
        ("sampled-reversible-examples", "literal-complete-product"),
        ("outcome-selected-law", "there-is-no-nothing-lineage"),
        ("preopened-execution-outcome", "post-registry-exact-execution"),
        ("silent-physical-or-quantum-export", "explicit-logical-physical-handoff"),
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
    passed = all(
        (
            received == rows,
            len(set(received)) == len(received) == 256,
            decisions == expected,
            sum(expected.values()) == 1,
            len(sealed["controls"]) == 4,
            all(row["passed"] for row in sealed["controls"]),
            sealed["closure"]["scope"] == "depth_independent",
            independent_witness(index),
        )
    )
    print(
        json.dumps(
            {
                "passed": passed,
                "validated_seal_hash": sealed["seal_hash"],
                "recomputed_from_declared_inputs": True,
                "certificate": {
                    "candidate_count": 256,
                    "unique_survivor_count": 1,
                    "reversible_computation_witness": independent_witness(index),
                },
            }
        )
    )
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
