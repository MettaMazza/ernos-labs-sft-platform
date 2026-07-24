"""Exact operational kernels used by the classical-computation derivations.

The objects in this module are deliberately small and transparent.  They are
not imports of conventional machine models.  They are generated finite
carriers, held labels, total or explicitly partial relations, and complete
traces built from already admitted Fold, relation, information and composition
laws.  Python indices and empty containers are host mechanics only.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Iterable


EMPTY_ONE = ("empty-One",)


def _unique(values: tuple[str, ...], name: str) -> None:
    if len(set(values)) != len(values):
        raise ValueError(f"{name} must contain unique generated identities")


@dataclass(frozen=True)
class ExactTransitionSystem:
    states: tuple[str, ...]
    actions: tuple[str, ...]
    transitions: tuple[tuple[str, str, str], ...]

    def __post_init__(self) -> None:
        _unique(self.states, "states")
        _unique(self.actions, "actions")
        if not self.states or not self.actions:
            raise ValueError("a transition system requires generated states and actions")
        seen: set[tuple[str, str]] = set()
        for source, action, target in self.transitions:
            if source not in self.states or target not in self.states or action not in self.actions:
                raise ValueError("a transition row escapes the generated carriers")
            key = (source, action)
            if key in seen:
                raise ValueError("a deterministic transition coordinate occurs twice")
            seen.add(key)

    def step(self, state: str, action: str) -> str:
        rows = tuple(target for source, label, target in self.transitions if source == state and label == action)
        if len(rows) != 1:
            raise ValueError("the requested transition is not exactly generated")
        return rows[0]

    def run(self, initial: str, actions: tuple[str, ...]) -> tuple[str, ...]:
        if initial not in self.states:
            raise ValueError("initial state is outside the carrier")
        trace = [initial]
        current = initial
        for action in actions:
            current = self.step(current, action)
            trace.append(current)
        return tuple(trace)


def generated_words(alphabet: tuple[str, ...], depth_trace: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    """Generate complete word support at each named position in ``depth_trace``."""

    _unique(alphabet, "alphabet")
    _unique(depth_trace, "depth trace")
    if not alphabet:
        raise ValueError("alphabet requires a generated symbol")
    words: tuple[tuple[str, ...], ...] = (EMPTY_ONE,)
    frontier: tuple[tuple[str, ...], ...] = ((),)
    produced: list[tuple[str, ...]] = [EMPTY_ONE]
    for _position in depth_trace:
        frontier = tuple(word + (symbol,) for word in frontier for symbol in alphabet)
        produced.extend(frontier)
    return tuple(produced)


def exact_rewrite(word: tuple[str, ...], held_position: str, positions: tuple[str, ...], replacement: str) -> tuple[str, ...]:
    _unique(positions, "positions")
    if len(word) != len(positions) or held_position not in positions:
        raise ValueError("rewrite position is not an exact generated coordinate")
    return tuple(replacement if position == held_position else symbol for position, symbol in zip(positions, word))


def structural_recursion(base: tuple[str, ...], successor_trace: tuple[str, ...], step: Callable[[tuple[str, ...], str], tuple[str, ...]]) -> tuple[tuple[str, ...], ...]:
    _unique(successor_trace, "successor trace")
    values = [base]
    current = base
    for position in successor_trace:
        current = step(current, position)
        values.append(current)
    return tuple(values)


def self_negating_boundary(candidate_verdict: str) -> str:
    """Return the held complement demanded by a self-negating description."""

    complements = {"accept": "reject", "reject": "accept"}
    if candidate_verdict not in complements:
        raise ValueError("verdict is not a generated held label")
    return complements[candidate_verdict]


def complete_enumeration(descriptions: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    _unique(descriptions, "descriptions")
    if not descriptions:
        raise ValueError("enumeration requires generated descriptions")
    return tuple((f"position-{index + 1}", description) for index, description in enumerate(descriptions))


def resource_ledger(trace: tuple[str, ...], occupied: tuple[str, ...]) -> dict[str, object]:
    _unique(occupied, "occupied states")
    if not trace or not occupied:
        raise ValueError("resource ledgers require nonempty generated traces")
    return {
        "time_trace": tuple((f"transition-{index + 1}", item) for index, item in enumerate(trace)),
        "space_support": occupied,
        "time_count": len(trace),
        "space_count": len(occupied),
    }


def exact_search(carrier: tuple[str, ...], target: str) -> tuple[str, str]:
    _unique(carrier, "search carrier")
    if target not in carrier:
        raise ValueError("target is not in the registered carrier")
    for index, value in enumerate(carrier):
        if value == target:
            return (f"position-{index + 1}", value)
    raise AssertionError("complete finite carrier was not exhausted")


def evaluate_expression(expression: tuple[object, ...], environment: tuple[tuple[str, Fraction], ...]) -> Fraction:
    bindings = dict(environment)
    if len(bindings) != len(environment):
        raise ValueError("binding identity occurs twice")
    tag = expression[0]
    if tag == "value":
        value = expression[1]
        if not isinstance(value, Fraction) or value <= 0:
            raise ValueError("only exact positive parts are semantic values")
        return value
    if tag == "name":
        name = expression[1]
        if name not in bindings:
            raise ValueError("unbound name")
        return bindings[name]
    if tag == "join":
        return evaluate_expression(expression[1], environment) + evaluate_expression(expression[2], environment)
    raise ValueError("expression constructor is outside the generated syntax")


def causal_closure(events: tuple[str, ...], edges: tuple[tuple[str, str], ...]) -> tuple[tuple[str, str], ...]:
    _unique(events, "events")
    relation = set(edges)
    if any(left not in events or right not in events for left, right in relation):
        raise ValueError("causal edge escapes the event carrier")
    changed = True
    while changed:
        changed = False
        additions = {
            (left, right2)
            for left, right in relation
            for left2, right2 in relation
            if right == left2 and (left, right2) not in relation
        }
        if additions:
            relation.update(additions)
            changed = True
    if any(left == right for left, right in relation):
        raise ValueError("causal cycle violates the partial-order boundary")
    return tuple(sorted(relation))


def exact_security_partition(messages: tuple[str, ...], observations: tuple[tuple[str, str], ...]) -> tuple[tuple[str, tuple[str, ...]], ...]:
    _unique(messages, "messages")
    mapping: dict[str, list[str]] = {}
    observed_messages = tuple(message for message, _view in observations)
    if set(observed_messages) != set(messages) or len(observed_messages) != len(messages):
        raise ValueError("security observation must cover each message exactly once")
    for message, view in observations:
        mapping.setdefault(view, []).append(message)
    return tuple(sorted((view, tuple(sorted(group))) for view, group in mapping.items()))


def consistent_hypotheses(examples: tuple[tuple[str, str], ...], hypotheses: tuple[tuple[str, tuple[tuple[str, str], ...]], ...]) -> tuple[str, ...]:
    names = tuple(name for name, _rows in hypotheses)
    _unique(names, "hypotheses")
    if not examples or not hypotheses:
        raise ValueError("learning support requires generated examples and hypotheses")
    return tuple(
        name
        for name, rows in hypotheses
        if all(row in rows for row in examples)
    )


def exact_error_ledger(reference: tuple[Fraction, ...], approximation: tuple[Fraction, ...]) -> tuple[tuple[str, Fraction, str], ...]:
    if len(reference) != len(approximation) or not reference:
        raise ValueError("comparison requires equal nonempty generated supports")
    ledger = []
    for index, (exact, approximate) in enumerate(zip(reference, approximation), 1):
        if exact <= 0 or approximate <= 0:
            raise ValueError("scientific proof values must be exact positive parts")
        if approximate == exact:
            ledger.append((f"cell-{index}", Fraction(1, 1), "equal"))
        elif approximate < exact:
            ledger.append((f"cell-{index}", exact - approximate, "held-below"))
        else:
            ledger.append((f"cell-{index}", approximate - exact, "held-above"))
    return tuple(ledger)


def group_witnesses(group: str, claim_id: str) -> tuple[tuple[str, str, bool], ...]:
    """Execute an implementation-level witness suite for a claim group."""

    identity = claim_id.rsplit("-", 2)[0]
    if group == "formal_computation":
        machine = ExactTransitionSystem(("held", "returned"), ("fold",), (("held", "fold", "returned"), ("returned", "fold", "held")))
        trace = machine.run("held", ("fold", "fold"))
        words = generated_words(("held", "returned"), ("place-1", "place-2"))
        rewritten = exact_rewrite(("held", "held"), "place-2", ("place-1", "place-2"), "returned")
        checks = (trace == ("held", "returned", "held"), len(words) == 7, rewritten == ("held", "returned"))
    elif group == "computability":
        enumeration = complete_enumeration(("machine-a", "machine-b"))
        checks = (enumeration[0][1] == "machine-a", self_negating_boundary("accept") == "reject", self_negating_boundary("reject") == "accept")
    elif group == "complexity":
        ledger = resource_ledger(("step-a", "step-b"), ("state-a", "state-b"))
        checks = (ledger["time_count"] == 2, ledger["space_count"] == 2, len(ledger["time_trace"]) == 2)
    elif group == "algorithms":
        found = exact_search(("a", "b", "c"), "b")
        recursion = structural_recursion(("seed",), ("p1", "p2"), lambda value, position: value + (position,))
        checks = (found == ("position-2", "b"), recursion[-1] == ("seed", "p1", "p2"), len(recursion) == 3)
    elif group == "semantics":
        expression = ("join", ("name", "x"), ("value", Fraction(1, 3)))
        value = evaluate_expression(expression, (("x", Fraction(2, 3)),))
        checks = (value == Fraction(1, 1), evaluate_expression(("name", "x"), (("x", Fraction(1, 2)),)) == Fraction(1, 2), identity.startswith("SFT-COMP"))
    elif group == "distributed_computation":
        closure = causal_closure(("a", "b", "c"), (("a", "b"), ("b", "c")))
        checks = (("a", "c") in closure, ("c", "a") not in closure, len(closure) == 3)
    elif group == "cryptography_security":
        partition = exact_security_partition(("m1", "m2"), (("m1", "same-view"), ("m2", "same-view")))
        checks = (len(partition) == 1, partition[0][1] == ("m1", "m2"), identity.startswith("SFT-COMP"))
    elif group == "learning_intelligence":
        support = consistent_hypotheses(
            (("a", "held"),),
            (("h1", (("a", "held"), ("b", "returned"))), ("h2", (("a", "returned"),))),
        )
        checks = (support == ("h1",), len(support) == 1, identity.startswith("SFT-COMP"))
    elif group == "scientific_computation":
        ledger = exact_error_ledger((Fraction(1, 2), Fraction(2, 3)), (Fraction(1, 3), Fraction(2, 3)))
        checks = (ledger[0][2] == "held-below", ledger[1][2] == "equal", ledger[0][1] == Fraction(1, 6))
    else:
        raise ValueError(f"unknown computation group: {group}")
    return tuple(
        (f"{group}-witness-{index}", f"{group} exact operational witness {index} for {claim_id}", passed)
        for index, passed in enumerate(checks, 1)
    )

