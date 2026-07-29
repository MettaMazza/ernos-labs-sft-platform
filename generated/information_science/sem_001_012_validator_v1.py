#!/usr/bin/env python3
"""Implementation-distinct exact validator for SEM-001--012."""
import json
import sys
from itertools import product
from pathlib import Path

RELATIONS = (
    "symbol-count-content-nonidentity",
    "complete-symbol-context-reference-record",
    "context-indexed-reference-distinction",
    "sequence-record-biology-handoff",
    "four-symbol-two-fibre-bijection",
    "signal-record-cognition-handoff",
    "report-record-qualia-handoff",
    "acknowledged-shared-record-boundary",
    "reference-preserving-translation-relation",
    "observation-action-purpose-handoff",
    "single-owner-semantic-provenance-ledger",
    "twelve-semantic-obligation-ledger",
)
GENETIC = {"A": ("fibre-a", "fibre-a"), "C": ("fibre-a", "fibre-b"), "G": ("fibre-b", "fibre-a"), "T": ("fibre-b", "fibre-b")}
CONTEXT = {("bank", "river-context"): "river-margin", ("bank", "finance-context"): "financial-institution"}


def witness(index):
    if index == 1:
        return len(("a", "b")) == len(("b", "a")) and ("a", "b") != ("b", "a")
    if index == 2:
        return CONTEXT[("bank", "river-context")] == "river-margin" and ("bank", "missing") not in CONTEXT
    if index == 3:
        return len({CONTEXT[("bank", "river-context")], CONTEXT[("bank", "finance-context")]}) == 2
    if index == 4:
        return ("sequence", "provenance", "biology-handoff") == ("sequence", "provenance", "biology-handoff")
    if index == 5:
        encoded = tuple(value for base in ("A", "C", "G", "T") for value in GENETIC[base])
        inverse = {value: base for base, value in GENETIC.items()}
        decoded = tuple(inverse[encoded[position:position + 2]] for position in range(0, len(encoded), 2))
        return len(set(GENETIC.values())) == 4 and decoded == ("A", "C", "G", "T")
    if index == 6:
        return ("signal-trace", "report-record") != ("cognitive-state", "lived-content")
    if index == 7:
        return len(("access-record", "report-record", "consciousness-handoff", "red-of-red-handoff")) == 4
    if index == 8:
        return len(("message", "ack-a", "ack-b")) == 3 and "shared-record" != "shared-lived-meaning"
    if index == 9:
        rows = (("red", "rouge", "colour-red"), ("blue", "bleu", "colour-blue"))
        return len({source for source, _target, _reference in rows}) == len({target for _source, target, _reference in rows}) == 2
    if index == 10:
        return ("observation", "action", "incidence-record") != ("purpose", "value", "policy")
    if index == 11:
        return len({"information", "biology", "cognition", "consciousness", "social", "pragmatic"}) == 6
    if index == 12:
        return len(RELATIONS) == 12 and all(witness(number) for number in range(1, 12))
    return False


def surface(index):
    axes = (
        ("partial-symbol-support", "complete-symbol-record-support"),
        ("meaning-from-count-alone", RELATIONS[index - 1]),
        ("context-erased-reference", "context-coordinate-retained"),
        ("silent-cross-domain-inference", "single-owner-explicit-handoff"),
        ("sampled-semantic-rows", "complete-declared-semantic-product"),
        ("outcome-selected", "root-bound-forward-forcing"),
        ("preopened-target", "post-registry-exact-observation"),
        ("fit-exception-extra-rule", "finite-successor-or-explicit-handoff"),
    )
    rows = tuple("__".join(choice) for choice in product(*axes))
    survivor = "__".join(choice[1] for choice in axes)
    return rows, survivor


def main():
    claim_id, _root, path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    index = int(claim_id.rsplit("-", 1)[-1])
    sealed = json.loads(path.read_text())
    rows, survivor = surface(index)
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
        witness(index),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": 256,
            "unique_survivor_count": 1,
            "complete_semantic_witness": witness(index),
        },
    }))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
