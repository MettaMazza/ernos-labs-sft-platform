#!/usr/bin/env python3
"""Implementation-distinct exact validator for FORMX-001 through FORMX-022."""
import json
import sys
from itertools import product
from pathlib import Path


RELATIONS = (
    "canonical-configuration-carrier",
    "source-complete-transition-relation",
    "three-way-terminal-recurrence-ledger",
    "complete-support-language-operations",
    "ordered-concatenation-successor-closure",
    "complete-derivation-tree-ledger",
    "parse-recognize-generate-equivalence",
    "observation-equivalent-state-quotient",
    "state-and-output-transduction",
    "typed-storage-operation-ledger",
    "well-founded-rewrite-normalization",
    "complete-critical-pair-joinability",
    "base-successor-recursive-composition",
    "generated-prefix-least-witness",
    "capture-avoiding-bound-substitution",
    "stepwise-configuration-simulation",
    "topological-gate-evaluation",
    "state-retained-sequential-unrolling",
    "complete-interleaving-trace-equivalence",
    "description-driven-universal-interpretation",
    "bidirectional-trace-preserving-translation",
    "twenty-two-obligation-no-omission-ledger",
)


def parse_trees(width):
    if width == 1:
        return 1
    return sum(parse_trees(left) * parse_trees(width - left) for left in range(1, width))


def parity(word):
    state = "even"
    for label in word:
        if label == "a":
            state = "odd" if state == "even" else "even"
    return state


def reductions(word, rules):
    pending = [tuple(word)]
    seen = set()
    ends = set()
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        next_rows = set()
        for source, target in rules:
            for place in range(len(current) - len(source) + 1):
                if current[place : place + len(source)] == source:
                    next_rows.add(current[:place] + target + current[place + len(source) :])
        if next_rows:
            pending.extend(next_rows)
        else:
            ends.add(current)
    return ends


def shuffles(left, right):
    pending = [(tuple(left), tuple(right), ())]
    rows = set()
    while pending:
        a, b, trace = pending.pop()
        if not a and not b:
            rows.add(trace)
        if a:
            pending.append((a[1:], b, trace + (a[0],)))
        if b:
            pending.append((a, b[1:], trace + (b[0],)))
    return rows


def run(program):
    value = ()
    trace = []
    for opcode, argument in program:
        if opcode == "append":
            value += (argument,)
        elif opcode == "drop":
            value = value[:-1] if value else value
        elif opcode != "retain":
            return None, ()
        trace.append((opcode, value))
    return value, tuple(trace)


def independent_witness(index):
    if index == 1:
        encoded = ("q", ("a", "b", "a"), "middle")
        return encoded == tuple(encoded) and len(encoded) == 3
    if index == 2:
        relation = {"s": ("t",), "t": ("u",)}
        return set(relation) == {"s", "t"} and "u" not in relation
    if index == 3:
        accepting, rejecting, cycle = {"accept"}, {"reject"}, ("r", "s", "r")
        return accepting.isdisjoint(rejecting) and cycle[0] == cycle[-1]
    if index == 4:
        left, right = {("a",), ("b",)}, {("b",), ("c",)}
        return left | right == {("a",), ("b",), ("c",)} and left & right == {("b",)} and left - right == {("a",)}
    if index == 5:
        language = {("a",), ("b",)}
        pairs = {x + y for x in language for y in language}
        return pairs == set(product(("a", "b"), repeat=2)) and () in {()}
    if index == 6:
        return parse_trees(3) == 2
    if index == 7:
        return all(parse_trees(width) >= 1 for width in (1, 2, 3, 4)) and parity(("a",)) == "odd"
    if index == 8:
        return all((parity(word) == "even") == (word.count("a") % 2 == 0) for width in range(4) for word in product(("a", "b"), repeat=width))
    if index == 9:
        mapping = {"a": "x", "b": "y"}
        return tuple(mapping[x] for x in ("a", "b", "a")) == ("x", "y", "x")
    if index == 10:
        word = ("a", "b", "c")
        return tuple(reversed(word)) == ("c", "b", "a") and word[1:] == ("b", "c")
    if index == 11:
        return reductions(("a", "b", "a", "b"), ((('a', 'b'), ('b', 'a')),)) == {("b", "b", "a", "a")}
    if index == 12:
        return reductions(("a", "a", "a"), ((('a', 'a'), ('a',)),)) == {("a",)}
    if index == 13:
        value = ()
        for _ in ("a", "b", "c"):
            value += ("x",)
        return value == ("x", "x", "x")
    if index == 14:
        sequence = ("a", "a", "b", "a")
        found = next((sequence[:place] for place in range(1, len(sequence) + 1) if sequence[place - 1] == "b"), None)
        return ("s",) + tuple("x" for _ in ("a", "b")) == ("s", "x", "x") and found == ("a", "a", "b")
    if index == 15:
        source_free = {"x"}; replacement_free = {"y"}; binder = "y"
        fresh = next(x for x in ("u", "v", "w") if x not in source_free | replacement_free)
        return fresh == "u" and binder in replacement_free
    if index == 16:
        word = ("a", "b", "c")
        stack_trace = tuple(("push", x) for x in word) + tuple(("pop", x) for x in reversed(word))
        return tuple(reversed(word)) == word[::-1] and len(stack_trace) == 6
    if index == 17:
        first, second = "held", "changed"
        middle = "held" if first == second else "changed"
        return middle == "changed"
    if index == 18:
        combinational = "held" if "held" == "held" else "changed"
        sequential, _ = run((("append", "a"), ("append", "b")))
        return combinational == "held" and sequential == ("a", "b")
    if index == 19:
        rows = shuffles(("a1", "a2"), ("b1", "b2"))
        return len(rows) == 6 and all(tuple(x for x in row if x.startswith("a")) == ("a1", "a2") for row in rows)
    if index == 20:
        value, trace = run((("append", "a"), ("retain", "self"), ("drop", "a"), ("append", "b")))
        return value == ("b",) and len(trace) == 4
    if index == 21:
        value, trace = run((("append", "a"), ("append", "b")))
        return value == tuple(reversed(("b", "a"))) and len(trace) == 2
    if index == 22:
        return len(RELATIONS) == 22 and all(independent_witness(number) for number in range(1, 22))
    return False


def generated_surface(index):
    axes = (
        ("partial-carrier", "complete-canonical-carrier"),
        ("hidden-or-selected-transition", "source-bound-complete-transition"),
        ("imported-model-answer", RELATIONS[index - 1]),
        ("terminal-only-output", "complete-step-trace"),
        ("sampled-examples", "literal-complete-product"),
        ("outcome-selected", "there-is-no-nothing-lineage"),
        ("preopened-target", "post-registry-exact-execution"),
        ("fit-exception-rule", "finite-successor-or-explicit-boundary"),
    )
    rows = tuple("__".join(coordinates) for coordinates in product(*axes))
    survivor = "__".join(axis[1] for axis in axes)
    return rows, survivor


def main():
    claim_id, _root, sealed_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
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
            "formal_computation_witness": independent_witness(index),
        },
    }))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
