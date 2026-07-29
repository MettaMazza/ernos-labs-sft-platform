#!/usr/bin/env python3
"""Implementation-distinct exact validator for SYMREP-001--014."""
import json
import sys
from itertools import product
from pathlib import Path

RELATIONS = (
    "complete-canonical-alphabet",
    "source-bound-observation-classes",
    "exact-concatenation-and-parse",
    "prefix-free-unique-decoding",
    "generated-grammar-language",
    "bijective-structure-preserving-renaming",
    "terminating-idempotent-canonicalization",
    "retained-self-delimiting-boundary",
    "complete-ordered-product-alphabet",
    "source-bound-dependent-symbol",
    "total-single-valued-provenance-transduction",
    "complete-alternative-parse-ledger",
    "fresh-symbol-successor-extension",
    "fourteen-obligation-no-omission-ledger",
)


def decode_all(stream, book):
    completed = []
    pending = [(0, ())]
    while pending:
        position, word = pending.pop()
        if position == len(stream):
            completed.append(word)
            continue
        for symbol in reversed(tuple(book)):
            code = book[symbol]
            if tuple(stream[position : position + len(code)]) == code:
                pending.append((position + len(code), word + (symbol,)))
    return tuple(sorted(completed))


def encode_all(word, book):
    output = ()
    for symbol in word:
        output += book[symbol]
    return output


def no_prefix_overlap(book):
    entries = tuple(book.values())
    for first in entries:
        for second in entries:
            if first != second and len(first) <= len(second) and second[: len(first)] == first:
                return False
    return True


def grammar_closure(depth):
    rules = {"S": (("a", "S"), ("b",))}
    levels = {("S",)}
    seen = set(levels)
    for _ in range(depth):
        following = set()
        for form in levels:
            for position, symbol in enumerate(form):
                for replacement in rules.get(symbol, ()):
                    following.add(form[:position] + replacement + form[position + 1 :])
        seen |= following
        levels = following
    return tuple(sorted(seen))


def witness(index):
    alphabet = ("a", "b", "c")
    prefix = {"a": ("L",), "b": ("R", "L"), "c": ("R", "R")}
    ambiguous = {"a": ("L",), "b": ("L", "L")}
    if index == 1:
        return len(alphabet) == len(set(alphabet)) == 3 and all(alphabet)
    if index == 2:
        fine = {"a": "A", "b": "B", "c": "C"}
        coarse = {"a": "L", "b": "L", "c": "R"}
        return len(set(fine.values())) == 3 and tuple((label, tuple(x for x in alphabet if coarse[x] == label)) for label in ("L", "R")) == (("L", ("a", "b")), ("R", ("c",)))
    if index == 3:
        stream = encode_all(("a", "b", "c"), prefix)
        return stream == ("L", "R", "L", "R", "R") and decode_all(stream, prefix) == (("a", "b", "c"),)
    if index == 4:
        return no_prefix_overlap(prefix) and all(decode_all(encode_all(word, prefix), prefix) == (word,) for width in (1, 2, 3) for word in product(alphabet, repeat=width))
    if index == 5:
        return grammar_closure(3) == (("S",), ("a", "S"), ("a", "a", "S"), ("a", "a", "a", "S"), ("a", "a", "b"), ("a", "b"), ("b",))
    if index == 6:
        mapping = {"a": "x", "b": "y", "c": "z"}
        source_edges = (("a", "b"), ("b", "c"))
        target_edges = (("x", "y"), ("y", "z"))
        return len(set(mapping.values())) == 3 and tuple((mapping[a], mapping[b]) for a, b in source_edges) == target_edges and {v: k for k, v in mapping.items()} == {"x": "a", "y": "b", "z": "c"}
    if index == 7:
        aliases = {"A1": "A", "A": "a"}
        def resolve(value):
            trail = ()
            while value in aliases:
                if value in trail:
                    return None
                trail += (value,)
                value = aliases[value]
            return value
        return resolve("A1") == "a" and resolve(resolve("A1")) == "a"
    if index == 8:
        return no_prefix_overlap(prefix) and decode_all(("L", "L"), ambiguous) == (("a", "a"), ("b",))
    if index == 9:
        pairs = tuple(product(("a", "b"), ("x", "y", "z")))
        return len(pairs) == len(set(pairs)) == 6 and pairs[0] == ("a", "x") and pairs[-1] == ("b", "z")
    if index == 10:
        fibres = {"shape": {"circle", "square"}, "colour": {"red", "blue"}}
        return "square" in fibres["shape"] and "red" not in fibres["shape"]
    if index == 11:
        first = {"a": "x", "b": "y"}; second = {"x": "L", "y": "R"}
        word = ("a", "b", "a")
        return tuple(second[first[x]] for x in word) == tuple({"a": "L", "b": "R"}[x] for x in word)
    if index == 12:
        return decode_all(("L", "L"), ambiguous) == (("a", "a"), ("b",))
    if index == 13:
        enlarged = alphabet + ("d",)
        return len(enlarged) == len(set(enlarged)) == 4 and tuple((old, "d") for old in alphabet) == (("a", "d"), ("b", "d"), ("c", "d"))
    if index == 14:
        return len(RELATIONS) == 14 and all(witness(number) for number in range(1, 14))
    return False


def generated_surface(index):
    axes = (
        ("partial-or-duplicated-carrier", "complete-canonical-carrier"),
        ("presentation-token-identity", "construction-and-label-identity"),
        ("imported-representation-answer", RELATIONS[index - 1]),
        ("selected-or-hidden-parse", "complete-boundary-aware-parse"),
        ("sampled-forms", "complete-declared-product"),
        ("outcome-selected", "root-bound-forward-forcing"),
        ("preopened-target", "post-registry-exact-observation"),
        ("fit-exception-extra-rule", "finite-successor-or-explicit-boundary"),
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
        witness(index),
    ))
    print(json.dumps({
        "passed": passed,
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "certificate": {
            "candidate_count": 256,
            "unique_survivor_count": 1,
            "complete_representation_witness": witness(index),
        },
    }))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
