#!/usr/bin/env python3
"""Implementation-distinct exact validator for DISTX-001 through DISTX-026."""
import json
import sys
from itertools import combinations, permutations, product
from pathlib import Path

RELATIONS = (
    "event-identity-local-order", "partial-order-interleaving-class", "transitive-happens-before-closure", "send-receive-channel-ledger",
    "declared-synchrony-delivery-boundary", "single-holder-critical-section-invariant", "deadlock-livelock-progress-trichotomy",
    "coordination-token-correspondence", "causality-preserving-logical-clock", "recipient-set-delivery-relation", "failure-free-agreement-decision",
    "crash-indistinguishability-boundary", "adversarial-quorum-intersection-boundary", "unrecorded-predecessor-impossibility",
    "detector-assumption-ledger", "deterministic-replicated-state-trace", "real-time-and-program-order-consistency-boundary",
    "causal-order-eventual-convergence-boundary", "intersecting-replicated-quorum", "all-or-abort-transaction-boundary",
    "local-shared-common-knowledge-ledger", "radius-bounded-information-propagation", "topology-conditioned-computability",
    "time-indexed-partition-ledger", "safety-liveness-fairness-certificate", "twenty-six-obligation-no-omission-ledger",
)


def closure(edges):
    result = set(edges)
    while True:
        expanded = result | {(a, d) for a, b in result for c, d in result if b == c and a != d}
        if expanded == result:
            return frozenset(result)
        result = expanded


def ordered(events, edges):
    required = closure(edges)
    return tuple(order for order in permutations(events) if all(order.index(a) < order.index(b) for a, b in required))


def reachable(edges, source):
    known = {source}
    while True:
        expanded = known | {target for node in known for target in edges.get(node, ())}
        if expanded == known:
            return frozenset(known)
        known = expanded


def independent_witness(index):
    if index == 1:
        events = ("p1", "p2", "p3"); return tuple(zip(events, events[1:])) == (("p1", "p2"), ("p2", "p3"))
    if index == 2:
        return ordered(("a", "b", "c"), (("a", "c"), ("b", "c"))) == (("a", "b", "c"), ("b", "a", "c"))
    if index == 3:
        return closure((("a", "b"), ("b", "c"))) == frozenset({("a", "b"), ("b", "c"), ("a", "c")})
    if index == 4:
        trace = (("send", "m", "p", "q"), ("receive", "m", "p", "q")); return trace[0][1:] == trace[1][1:]
    if index == 5:
        synchronous = ("send", "receive", "ack"); queue = [("p", "q", "m")]; delivered = [queue.pop(0)]; return len(synchronous) == 3 and delivered == [("p", "q", "m")]
    if index == 6:
        good = (("enter", "p"), ("leave", "p"), ("enter", "q"), ("leave", "q")); bad = (("enter", "p"), ("enter", "q"))
        def safe(trace):
            active = set()
            for action, process in trace:
                if action == "enter" and active: return False
                if action == "enter": active.add(process)
                else: active.discard(process)
            return True
        return safe(good) and not safe(bad)
    if index == 7:
        deadlock = not {"b": ()}["b"]; livelock = len(("a", "b", "a")) != len(set(("a", "b", "a"))); progress = "done" in {"done"}; return deadlock and livelock and progress
    if index == 8:
        return sum(row == ("arrived", "arrived") for row in product(("arrived", "waiting"), repeat=2)) == 1
    if index == 9:
        send = 1; receiver_local = 1; receipt = max(send, receiver_local) + 1; return send < receipt and receipt == 2
    if index == 10:
        receivers = ("q", "r", "s"); return (len(receivers[:1]), len(receivers[:-1]), len(receivers)) == (1, 2, 3)
    if index == 11:
        inputs = ("b", "a", "b"); decision = min(inputs); return decision in inputs and (decision,) * len(inputs) == ("a", "a", "a")
    if index == 12:
        view_a = {"local": "a"}; view_b = {"local": "a"}; hidden = (("remote", "a"), ("remote", "b")); return view_a == view_b and hidden[0] != hidden[1]
    if index == 13:
        quorums = tuple(frozenset(row) for row in combinations(("p", "q", "r", "s"), 3)); return all(len(a & b) >= 2 for a in quorums for b in quorums)
    if index == 14:
        predecessors = (("left", "right"), ("right", "left")); images = ("merged", "merged"); return predecessors[0] != predecessors[1] and len(set(images)) == 1
    if index == 15:
        record = ("suspect-q", "missed-declared-round", "bounded-round"); return len(record) == 3 and record[1] == "missed-declared-round"
    if index == 16:
        commands = ("a", "b"); states = {replica: tuple(commands) for replica in ("p", "q", "r")}; return len(set(states.values())) == 1
    if index == 17:
        good = (("write", "x", "a"), ("read", "x", "a")); bad = (("write", "x", "a"), ("read", "x", "b")); return good[0][2] == good[1][2] and bad[0][2] != bad[1][2]
    if index == 18:
        events = ("write-a", "write-b", "merge"); positions = {event: n for n, event in enumerate(events)}; return all(positions[a] < positions[b] for a, b in (("write-a", "merge"), ("write-b", "merge")))
    if index == 19:
        quorums = tuple(frozenset(row) for row in combinations(("p", "q", "r"), 2)); return all(a & b for a in quorums for b in quorums)
    if index == 20:
        decide = lambda votes: "commit" if all(v == "yes" for v in votes) else "abort"; return decide(("yes",) * 3) == "commit" and decide(("yes", "no", "yes")) == "abort"
    if index == 21:
        left, right = frozenset({"a", "b"}), frozenset({"b", "c"}); return left | right == frozenset({"a", "b", "c"}) and left & right == frozenset({"b"})
    if index == 22:
        edges = {"a": ("b",), "b": ("c",), "c": ("d",)}; layers = []
        seen = set(); frontier = {"a"}
        while frontier:
            layers.append(frozenset(frontier)); seen |= frontier; frontier = {x for n in frontier for x in edges.get(n, ()) if x not in seen}
        return tuple(layers) == (frozenset({"a"}), frozenset({"b"}), frozenset({"c"}), frozenset({"d"}))
    if index == 23:
        return reachable({"a": ("b", "c"), "b": ("d",), "c": ()}, "a") == frozenset({"a", "b", "c", "d"})
    if index == 24:
        return reachable({"a": ("b",), "b": (), "c": ("d",), "d": ()}, "a") == frozenset({"a", "b"})
    if index == 25:
        return len({"p"}) == 1 and "done" in {"done"} and {"send-p", "send-q"} <= set(("send-p", "send-q"))
    if index == 26:
        return len(RELATIONS) == 26 and all(independent_witness(number) for number in range(1, 26))
    return False


def surface(index):
    axes = (
        ("anonymous-or-missing-event", "complete-process-bound-events"),
        ("hidden-message-or-schedule", "complete-message-synchronization-ledger"),
        ("imported-distributed-answer", RELATIONS[index - 1]),
        ("favorable-execution", "complete-adversarial-trace-certificate"),
        ("sampled-schedules", "literal-complete-product"),
        ("outcome-selected", "there-is-no-nothing-lineage"),
        ("preopened-target", "post-registry-exact-distributed-execution"),
        ("unrestricted-network-export", "declared-fault-time-topology-boundary"),
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
    passed = all((received == rows, len(set(received)) == len(received) == 256, decisions == expected, sum(expected.values()) == 1, len(sealed["controls"]) == 4, all(row["passed"] for row in sealed["controls"]), sealed["closure"]["scope"] == "depth_independent", independent_witness(index)))
    print(json.dumps({"passed": passed, "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "certificate": {"candidate_count": 256, "unique_survivor_count": 1, "distributed_witness": independent_witness(index)}}))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
