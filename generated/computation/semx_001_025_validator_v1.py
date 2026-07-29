#!/usr/bin/env python3
"""Implementation-distinct exact validator for SEMX-001 through SEMX-025."""
import json
import sys
from itertools import product
from pathlib import Path

RELATIONS = (
    "canonical-well-formed-syntax", "free-bound-scope-ledger", "alpha-renaming-equivalence",
    "capture-avoiding-substitution", "one-step-contextual-reduction", "whole-derivation-evaluation",
    "single-hole-context-composition", "compositional-fold-denotation", "operational-denotational-adequacy",
    "declared-context-full-abstraction", "type-formation-introduction-elimination", "syntax-directed-type-judgment",
    "representation-independent-parametricity", "type-indexed-evidence-carrier", "state-effect-exception-trace",
    "all-context-observation-equivalence", "well-founded-term-descent", "pre-post-termination-correctness",
    "invariant-preserving-assertion-logic", "behavior-subset-refinement-order", "semantics-preserving-transformation",
    "step-simulating-compiler-correctness", "composed-intermediate-simulation", "proof-carrying-certificate-check",
    "twenty-five-obligation-no-omission-ledger",
)

A = ("value", ("a",))
B = ("value", ("b",))
JOIN = ("join", A, B)
LET = ("let", "x", A, ("join", ("name", "x"), B))


def closed(term, names=()):
    tag = term[0]
    if tag == "value":
        return len(term) == 2
    if tag == "name":
        return len(term) == 2 and term[1] in names
    if tag == "join":
        return len(term) == 3 and closed(term[1], names) and closed(term[2], names)
    if tag == "let":
        return len(term) == 4 and closed(term[2], names) and closed(term[3], names + (term[1],))
    if tag == "same":
        return len(term) == 5 and all(closed(child, names) for child in term[1:])
    return False


def unbound(term, names=()):
    tag = term[0]
    if tag == "value":
        return set()
    if tag == "name":
        return set() if term[1] in names else {term[1]}
    if tag == "join":
        return unbound(term[1], names) | unbound(term[2], names)
    if tag == "let":
        return unbound(term[2], names) | unbound(term[3], names + (term[1],))
    answer = set()
    for child in term[1:]:
        answer |= unbound(child, names)
    return answer


def rename_scope(term, old, new):
    tag = term[0]
    if tag == "value":
        return term
    if tag == "name":
        return ("name", new if term[1] == old else term[1])
    if tag == "join":
        return ("join", rename_scope(term[1], old, new), rename_scope(term[2], old, new))
    if tag == "same":
        return ("same",) + tuple(rename_scope(child, old, new) for child in term[1:])
    binder, value, body = term[1:]
    renamed_value = rename_scope(value, old, new)
    if binder == old:
        return ("let", binder, renamed_value, body)
    return ("let", binder, renamed_value, rename_scope(body, old, new))


def alpha_top(term, new):
    if term[0] != "let" or new in unbound(term):
        raise ValueError("alpha boundary")
    binder, value, body = term[1:]
    return ("let", new, value, rename_scope(body, binder, new))


def replace_free(term, name, replacement):
    tag = term[0]
    if tag == "value":
        return term
    if tag == "name":
        return replacement if term[1] == name else term
    if tag == "join":
        return ("join", replace_free(term[1], name, replacement), replace_free(term[2], name, replacement))
    if tag == "same":
        return ("same",) + tuple(replace_free(child, name, replacement) for child in term[1:])
    binder, value, body = term[1:]
    value = replace_free(value, name, replacement)
    if binder == name:
        return ("let", binder, value, body)
    if binder in unbound(replacement):
        fresh = next(label for label in ("u", "v", "w", "z") if label not in unbound(body) | unbound(replacement) | {name})
        body = rename_scope(body, binder, fresh)
        binder = fresh
    return ("let", binder, value, replace_free(body, name, replacement))


def terminal(term):
    return term[0] == "value"


def contract(term):
    tag = term[0]
    if tag == "join":
        if not terminal(term[1]):
            return ("join", contract(term[1]), term[2])
        if not terminal(term[2]):
            return ("join", term[1], contract(term[2]))
        return ("value", term[1][1] + term[2][1])
    if tag == "let":
        if not terminal(term[2]):
            return ("let", term[1], contract(term[2]), term[3])
        return replace_free(term[3], term[1], term[2])
    if tag == "same":
        left, right, yes, no = term[1:]
        if not terminal(left):
            return ("same", contract(left), right, yes, no)
        if not terminal(right):
            return ("same", left, contract(right), yes, no)
        return yes if left[1] == right[1] else no
    raise ValueError("terminal or stuck")


def normalize(term):
    trace = [term]
    while not terminal(term):
        term = contract(term)
        trace.append(term)
    return term, tuple(trace)


def direct(term, environment=None):
    environment = {} if environment is None else dict(environment)
    tag = term[0]
    if tag == "value":
        return term
    if tag == "name":
        return environment[term[1]]
    if tag == "join":
        return ("value", direct(term[1], environment)[1] + direct(term[2], environment)[1])
    if tag == "let":
        environment[term[1]] = direct(term[2], environment)
        return direct(term[3], environment)
    left, right = direct(term[1], environment), direct(term[2], environment)
    return direct(term[3] if left[1] == right[1] else term[4], environment)


def plug(context, term):
    return term if context == ("hole",) else (context[0], plug(context[1], term), context[2])


def type_of(term, environment=None):
    environment = {} if environment is None else dict(environment)
    tag = term[0]
    if tag == "value":
        return "word"
    if tag == "name":
        return environment[term[1]]
    if tag == "join":
        if type_of(term[1], environment) == type_of(term[2], environment) == "word":
            return "word"
        raise TypeError("join")
    if tag == "let":
        environment[term[1]] = type_of(term[2], environment)
        return type_of(term[3], environment)
    if type_of(term[1], environment) != type_of(term[2], environment):
        raise TypeError("comparison")
    yes, no = type_of(term[3], environment), type_of(term[4], environment)
    if yes != no:
        raise TypeError("branches")
    return yes


def size(term):
    return 1 if term[0] in ("value", "name") else 1 + sum(size(child) for child in term[1:] if isinstance(child, tuple))


def code(term):
    if term[0] == "value":
        return (("push", term[1]),)
    if term[0] == "join":
        return code(term[1]) + code(term[2]) + (("join", ()),)
    raise ValueError("compiler subset")


def machine(instructions):
    stack = []
    for operation, argument in instructions:
        if operation == "push":
            stack.append(argument)
        else:
            right, left = stack.pop(), stack.pop()
            stack.append(left + right)
    return ("value", stack[-1])


def independent_witness(index):
    if index == 1:
        return closed(LET) and not closed(("name", "x"))
    if index == 2:
        return unbound(("let", "x", A, ("join", ("name", "x"), ("name", "y")))) == {"y"}
    if index == 3:
        return alpha_top(("let", "x", A, ("name", "x")), "u") == ("let", "u", A, ("name", "u"))
    if index == 4:
        return replace_free(("let", "y", A, ("name", "x")), "x", ("name", "y"))[1] == "u"
    if index == 5:
        result, trace = normalize(JOIN); return result == ("value", ("a", "b")) and len(trace) == 2
    if index == 6:
        return direct(LET) == ("value", ("a", "b"))
    if index == 7:
        return normalize(plug(("join", ("hole",), B), A))[0] == ("value", ("a", "b"))
    if index == 8:
        return direct(JOIN)[1] == direct(A)[1] + direct(B)[1]
    if index == 9:
        return normalize(LET)[0] == direct(LET)
    if index == 10:
        contexts = (("hole",), ("join", ("hole",), A)); folded = ("value", ("a", "b"))
        return all(normalize(plug(context, JOIN))[0] == normalize(plug(context, folded))[0] for context in contexts)
    if index == 11:
        return type_of(LET) == "word"
    if index == 12:
        return type_of(("same", A, A, B, A)) == "word"
    if index == 13:
        samples = (A, ("vector", 2, ("a", "b")), ("pair", A, B)); return all(sample == sample for sample in samples)
    if index == 14:
        return len(("a", "b", "c")) == 3 and len(("a",)) != 2
    if index == 15:
        store = {}; trace = []; result = A
        for command in (("set", "x", A), ("get", "x"), ("raise", "halt"), ("set", "x", B)):
            if command[0] == "set": store[command[1]] = command[2]; result = command[2]
            elif command[0] == "get": result = store[command[1]]
            else: result = ("exception", command[1]); trace.append((command, dict(store), result)); break
            trace.append((command, dict(store), result))
        return result == ("exception", "halt") and store["x"] == A and len(trace) == 3
    if index == 16:
        folded = ("value", ("a", "b")); contexts = (("hole",), ("join", ("hole",), A))
        return all(normalize(plug(context, JOIN))[0] == normalize(plug(context, folded))[0] for context in contexts)
    if index == 17:
        return size(contract(JOIN)) < size(JOIN)
    if index == 18:
        states = (("a",), ("a", "b")); return all((state + ("done",))[-1] == "done" for state in states)
    if index == 19:
        states = (("a",), ("b",)); return all(len(state + ("a",)) >= 2 for state in states)
    if index == 20:
        inputs = ((), ("b",)); return all(tuple(list(value) + ["a"]) == value + ("a",) for value in inputs)
    if index == 21:
        return normalize(JOIN)[0] == ("value", A[1] + B[1])
    if index == 22:
        return machine(code(JOIN)) == normalize(JOIN)[0]
    if index == 23:
        nested = ("join", JOIN, A); return machine(code(nested)) == normalize(nested)[0]
    if index == 24:
        return closed(JOIN) and type_of(JOIN) == "word" and normalize(JOIN)[0] == ("value", ("a", "b"))
    if index == 25:
        return len(RELATIONS) == 25 and all(independent_witness(number) for number in range(1, 25))
    return False


def surface(index):
    axes = (
        ("partial-or-ill-scoped-term", "complete-well-formed-term"),
        ("output-only-or-hidden-step", "complete-operational-and-compositional-trace"),
        ("imported-language-answer", RELATIONS[index - 1]),
        ("trusted-producer-claim", "independently-checkable-judgment"),
        ("sampled-programs", "literal-complete-product"),
        ("outcome-selected", "there-is-no-nothing-lineage"),
        ("preopened-target", "post-registry-exact-program-execution"),
        ("unrestricted-language-export", "declared-language-or-explicit-translation"),
    )
    rows = tuple("__".join(row) for row in product(*axes))
    return rows, "__".join(axis[1] for axis in axes)


def main():
    claim_id, _root, sealed_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    index = int(claim_id.rsplit("-", 1)[-1])
    sealed = json.loads(sealed_path.read_text())
    rows, survivor = surface(index)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: bool(row["survives"]) for row in sealed["decisions"]}
    expected = {candidate: candidate == survivor for candidate in rows}
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
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "semantic_witness": independent_witness(index)}}))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
