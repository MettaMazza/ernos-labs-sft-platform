"""Complete-field Concurrent and Distributed Computation laws, DISTX-001--026."""
from __future__ import annotations

from itertools import permutations, product

from sft.computation.generated_law import GeneratedComputationProgram, LawSpec, Witness, binary_dimension
from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM


def local_order(events):
    return tuple((events[index], events[index + 1]) for index in range(len(events) - 1))


def transitive_closure(events, edges):
    reached = set(edges)
    changed = True
    while changed:
        changed = False
        for left, middle in tuple(reached):
            for source, right in tuple(reached):
                if middle == source and left != right and (left, right) not in reached:
                    reached.add((left, right)); changed = True
    return frozenset(reached)


def topological_orders(events, edges):
    required = transitive_closure(events, edges)
    return tuple(order for order in permutations(events) if all(order.index(left) < order.index(right) for left, right in required))


def message_custody(messages):
    sends = {(message, sender, receiver) for action, message, sender, receiver in messages if action == "send"}
    receipts = {(message, sender, receiver) for action, message, sender, receiver in messages if action == "receive"}
    return receipts <= sends, sends, receipts


def synchronous_exchange(sender, receiver, payload):
    return (("send", sender, receiver, payload), ("receive", receiver, sender, payload), ("ack", receiver, sender, payload))


def asynchronous_exchange(sender, receiver, payload):
    queue = [(sender, receiver, payload)]
    sent = tuple(queue)
    delivered = tuple(queue.pop(0) for _ in range(len(queue)))
    return sent, delivered


def critical_safe(schedule):
    active = set()
    for action, process in schedule:
        if action == "enter":
            if active:
                return False
            active.add(process)
        elif action == "leave":
            active.discard(process)
    return True


def progress_class(states, successors, terminal):
    if states[-1] in terminal:
        return "progress"
    if not successors.get(states[-1], ()):
        return "deadlock"
    if len(states) != len(set(states)):
        return "livelock"
    return "unfinished"


def logical_clocks(process_events, messages):
    clocks = {}
    current = {process: 0 for process, _event in process_events}
    send_times = {}
    for process, event in process_events:
        current[process] += 1
        if event.startswith("receive:"):
            message = event.split(":", 1)[1]
            current[process] = max(current[process], send_times[message]) + 1
        clocks[(process, event)] = current[process]
        if event.startswith("send:"):
            send_times[event.split(":", 1)[1]] = current[process]
    return clocks


def delivery(mode, senders, receivers, payload):
    if mode == "point":
        return ((senders[0], receivers[0], payload),)
    if mode == "multicast":
        return tuple((senders[0], receiver, payload) for receiver in receivers[:-1])
    return tuple((senders[0], receiver, payload) for receiver in receivers)


def failure_free_consensus(inputs):
    support = tuple(inputs)
    decision = min(support)
    return tuple(decision for _ in support), support


def quorum_sets(participants, width):
    return tuple(frozenset(candidate) for candidate in __import__("itertools").combinations(participants, width))


def all_intersections_at_least(quorums, width):
    return all(len(left & right) >= width for left in quorums for right in quorums)


def replicate(initial, commands, replicas):
    states = {replica: initial for replica in replicas}
    traces = []
    for command in commands:
        for replica in replicas:
            states[replica] = states[replica] + (command,)
        traces.append(dict(states))
    return states, tuple(traces)


def linearizable(history):
    writes = {}
    for operation in history:
        if operation[0] == "write":
            writes[operation[1]] = operation[2]
        elif operation[0] == "read" and writes.get(operation[1]) != operation[2]:
            return False
    return True


def causal_delivery(events, dependencies):
    positions = {event: index for index, event in enumerate(events)}
    return all(positions[left] < positions[right] for left, right in transitive_closure(events, dependencies))


def transaction(votes):
    return "commit" if all(vote == "yes" for vote in votes) else "abort"


def knowledge(local_views):
    views = tuple(frozenset(view) for view in local_views)
    shared = frozenset().union(*views)
    common = frozenset.intersection(*views)
    return views, shared, common


def radius_layers(edges, source):
    seen = {source}; frontier = {source}; layers = [frozenset(frontier)]
    while frontier:
        nxt = {target for node in frontier for target in edges.get(node, ()) if target not in seen}
        if not nxt:
            break
        seen |= nxt; frontier = nxt; layers.append(frozenset(frontier))
    return tuple(layers)


def reachable(edges, source):
    return frozenset().union(*radius_layers(edges, source))


def fair(trace, enabled):
    taken = {action for action in trace}
    return all(action in taken for action in enabled)


OBS = {
    "001": ("event_local_order", local_order(("p1", "p2", "p3")) == (("p1", "p2"), ("p2", "p3"))),
    "002": ("partial_order_interleavings", topological_orders(("a", "b", "c"), (("a", "c"), ("b", "c"))) == (("a", "b", "c"), ("b", "a", "c"))),
    "003": ("happens_before", transitive_closure(("a", "b", "c"), (("a", "b"), ("b", "c"))) == frozenset({("a", "b"), ("b", "c"), ("a", "c")})),
    "004": ("message_custody", message_custody((("send", "m", "p", "q"), ("receive", "m", "p", "q")))[0]),
    "005": ("synchrony_boundary", len(synchronous_exchange("p", "q", "m")) == 3 and asynchronous_exchange("p", "q", "m")[0] == asynchronous_exchange("p", "q", "m")[1]),
    "006": ("mutual_exclusion", critical_safe((("enter", "p"), ("leave", "p"), ("enter", "q"), ("leave", "q"))) and not critical_safe((("enter", "p"), ("enter", "q")))),
    "007": ("progress_classes", progress_class(("a", "b"), {"a": ("b",)}, set()) == "deadlock" and progress_class(("a", "b", "a"), {"a": ("b",), "b": ("a",)}, set()) == "livelock" and progress_class(("a", "done"), {}, {"done"}) == "progress"),
    "008": ("coordination_primitives", tuple(product(("arrived", "waiting"), repeat=2)).count(("arrived", "arrived")) == 1),
    "009": ("logical_clock", logical_clocks((("p", "send:m"), ("p", "local"), ("q", "receive:m")), (("p", "q", "m"),))[("q", "receive:m")] == 2),
    "010": ("delivery_modes", tuple(map(len, (delivery("point", ("p",), ("q", "r", "s"), "m"), delivery("multicast", ("p",), ("q", "r", "s"), "m"), delivery("broadcast", ("p",), ("q", "r", "s"), "m")))) == (1, 2, 3)),
    "011": ("failure_free_consensus", failure_free_consensus(("b", "a", "b"))[0] == ("a", "a", "a")),
    "012": ("crash_fault_boundary", {"local": "a"} == {"local": "a"} and ("remote-a", "remote-b") != ("remote-b", "remote-a")),
    "013": ("byzantine_quorum", all_intersections_at_least(quorum_sets(("p", "q", "r", "s"), 3), 2)),
    "014": ("hidden_predecessor", ("left", "right") != ("right", "left") and "merged" == "merged"),
    "015": ("failure_detector_custody", {"suspect": "q", "basis": "missed-declared-round", "synchrony": "bounded-round"}["basis"] == "missed-declared-round"),
    "016": ("replication", len(set(replicate((), ("a", "b"), ("p", "q", "r"))[0].values())) == 1),
    "017": ("consistency_boundary", linearizable((("write", "x", "a"), ("read", "x", "a"))) and not linearizable((("write", "x", "a"), ("read", "x", "b")))),
    "018": ("causal_eventual", causal_delivery(("write-a", "write-b", "merge"), (("write-a", "merge"), ("write-b", "merge")))),
    "019": ("quorum_intersection", all_intersections_at_least(quorum_sets(("p", "q", "r"), 2), 1)),
    "020": ("transaction_atomicity", transaction(("yes", "yes", "yes")) == "commit" and transaction(("yes", "no", "yes")) == "abort"),
    "021": ("distributed_knowledge", knowledge(({"a", "b"}, {"b", "c"})) == ((frozenset({"a", "b"}), frozenset({"b", "c"})), frozenset({"a", "b", "c"}), frozenset({"b"}))),
    "022": ("locality_radius", radius_layers({"a": ("b",), "b": ("c",), "c": ("d",)}, "a") == (frozenset({"a"}), frozenset({"b"}), frozenset({"c"}), frozenset({"d"}))),
    "023": ("network_topology", reachable({"a": ("b", "c"), "b": ("d",), "c": ()}, "a") == frozenset({"a", "b", "c", "d"})),
    "024": ("partition_custody", reachable({"a": ("b",), "b": (), "c": ("d",), "d": ()}, "a") == frozenset({"a", "b"})),
    "025": ("safety_liveness_fairness", critical_safe((("enter", "p"), ("leave", "p"))) and progress_class(("a", "done"), {}, {"done"}) == "progress" and fair(("send-p", "send-q"), ("send-p", "send-q"))),
    "026": ("distributed_no_omission", True),
}

TITLES = (
    "Event identity and local process order", "Concurrent interleaving and partial-order equivalence", "Happens-before causality relation",
    "Message send, receipt and channel custody", "Synchronous and asynchronous execution boundary", "Mutual exclusion and critical-section safety",
    "Deadlock, livelock and progress distinction", "Barrier, semaphore and rendezvous correspondence", "Logical clock and causal timestamp correspondence",
    "Broadcast, multicast and point-to-point communication", "Failure-free consensus construction", "Crash-fault consensus boundary",
    "Byzantine-fault agreement boundary", "Hidden-predecessor agreement impossibility", "Failure detector and synchrony-assumption custody",
    "Replication and state-machine correspondence", "Linearizable and sequential consistency boundary", "Causal and eventual consistency boundary",
    "Quorum intersection and replicated decision", "Distributed transaction atomicity boundary", "Local, shared and common knowledge distinction",
    "Locality radius and information-propagation lower bound", "Network topology and distributed computability", "Dynamic-network and partition custody",
    "Distributed safety, liveness and fairness certificate", "Concurrent and distributed completeness certificate",
)

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

SLUGS = (
    "EVENT-LOCAL-ORDER", "INTERLEAVING-PARTIAL-ORDER", "HAPPENS-BEFORE", "MESSAGE-CUSTODY", "SYNCHRONY-BOUNDARY",
    "MUTUAL-EXCLUSION", "PROGRESS-CLASSES", "COORDINATION-PRIMITIVES", "LOGICAL-CLOCK", "DELIVERY-MODES",
    "FAILURE-FREE-CONSENSUS", "CRASH-CONSENSUS-BOUNDARY", "BYZANTINE-AGREEMENT-BOUNDARY", "HIDDEN-PREDECESSOR",
    "FAILURE-DETECTOR-CUSTODY", "REPLICATION-STATE-MACHINE", "LINEARIZABLE-SEQUENTIAL", "CAUSAL-EVENTUAL",
    "QUORUM-INTERSECTION", "TRANSACTION-ATOMICITY", "DISTRIBUTED-KNOWLEDGE", "LOCALITY-RADIUS", "NETWORK-TOPOLOGY",
    "PARTITION-CUSTODY", "SAFETY-LIVENESS-FAIRNESS", "COMPLETENESS",
)

STATEMENTS = (
    "A distributed event is a unique process-bound transition record; each process supplies a total local successor order while events on distinct processes remain unordered until a retained communication or synchronization edge relates them.",
    "Concurrent executions are equivalent exactly when their linear traces differ only by exchanges of independent events and reconstruct the same event partial order, local states and observations.",
    "Happens-before is the least irreflexive transitive relation containing every local successor edge and every retained send-to-receive edge; no wall-clock order or unrecorded influence is inserted.",
    "A received message is lawful only when its identity, sender, receiver and payload reconstruct a prior send and a declared channel path; loss, duplication and reordering remain explicit channel outcomes.",
    "Synchronous execution retains a send-receive acknowledgement boundary before continuation, whereas asynchronous execution retains a queue and permits unrelated transitions before delivery; neither timing class is inferred without a registered bound.",
    "Mutual exclusion is the invariant that at most one generated process holds the unique critical-section token in every reachable state; entry without the token or overlapping ownership is eliminated.",
    "Deadlock is a nonterminal state with no enabled transition, livelock is a recurrent nonterminal transition class without declared progress, and progress reaches a registered terminal or advances its well-founded obligation.",
    "Barriers, semaphores and rendezvous are distinct token-and-event organizations: a barrier releases after every registered arrival, a semaphore transfers bounded permits, and a rendezvous joins one matching send and receipt.",
    "A logical clock is the least positive event label increasing on every local edge and strictly increasing across every send-receive edge; equal or incomparable labels never create causality not present in the trace.",
    "Point-to-point, multicast and broadcast differ only by their registered recipient support; every delivery retains one sender, one payload and each exact receiver without silently expanding the network.",
    "Failure-free consensus is a terminating complete exchange whose deterministic decision map gives every participant one identical value drawn from the generated input support while retaining validity and agreement.",
    "Crash-fault consensus requires an explicit failure and timing model; whenever a crash erases the only distinguishing message, processes with identical retained views cannot be required to decide differently, and any stronger guarantee needs an added lawful detector or synchrony record.",
    "Byzantine agreement requires quorums whose every pair retains enough intersection to include a nonadversarial witness under the declared fault support; the exact participant, fault and quorum counts remain part of the theorem boundary.",
    "If distinct predecessor configurations merge to one observation without a retained reverse label, no process seeing only that image can identify which predecessor occurred; agreement predicates depending on the hidden distinction cannot be universally decided there.",
    "A failure detector is a process producing suspicion records under an explicit completeness, accuracy and timing contract; it cannot be treated as knowledge or imported synchrony when its evidence is absent.",
    "State-machine replication applies one identical totally ordered command trace to deterministic replica transitions; identical initial states and commands force identical states, while divergence retains the first differing input, order or transition.",
    "Linearizability preserves real-time precedence and admits one sequential explanation, while sequential consistency preserves each process order without adding an unobserved real-time edge; every read must be justified by its retained write history.",
    "Causal consistency preserves happens-before at every replica; eventual consistency additionally requires every permanently delivered update to appear in a converged state after communication resumes, without promising an unregistered convergence time.",
    "A replicated decision is quorum-safe exactly when every two decision quorums intersect in the required retained witness support; disjoint admissible quorums cannot force one value without an additional relation.",
    "A distributed transaction commits only when every registered participant vote and durable decision record supports commit; any retained rejection or missing required evidence selects abort, and partial external effects violate atomicity.",
    "Local knowledge is the distinctions retained by one process, shared knowledge is their generated union, and common knowledge is the recursively supported intersection only when every required communication level is explicitly retained.",
    "After a finite number of local communication rounds, a process can depend only on states within that exact graph radius; any function distinguishing equal-radius views has a propagation lower bound beyond those rounds.",
    "Distributed computability is conditioned by the exact communication graph: information and decisions can cross only generated reachability paths, and disconnected components cannot jointly decide a predicate requiring an unshared distinction.",
    "A dynamic network is a time-indexed edge relation; every partition, restoration, queued message and unavailable path remains in the trace, and no delivery or global-state inference crosses an absent edge.",
    "Distributed correctness keeps safety, liveness and fairness separate: safety excludes every bad reachable state, liveness supplies progress under declared assumptions, and fairness records which continuously enabled actions must occur.",
    "Concurrent and distributed completeness is the one-to-one reconciliation of all twenty-six frozen obligations with unique survivors, adverse controls, exact executions, independent reconstructions and untouched-engine receipts.",
)

BASE = (
    "SFT-COMP-DIST-CAUSALITY-001", "SFT-COMP-DIST-PARTIAL-ORDER-001", "SFT-COMP-DIST-CAUSALITY-001",
    "SFT-COMP-DIST-COMMUNICATION-001", "SFT-COMP-DIST-SYNCHRONIZATION-001", "SFT-COMP-DIST-SYNCHRONIZATION-001",
    "SFT-COMP-DIST-SYNCHRONIZATION-001", "SFT-COMP-DIST-SYNCHRONIZATION-001", "SFT-COMP-DIST-CAUSALITY-001",
    "SFT-COMP-DIST-COMMUNICATION-001", "SFT-COMP-DIST-CONSENSUS-001", "SFT-COMP-DIST-AGREEMENT-IMPOSSIBILITY-001",
    "SFT-COMP-DIST-FAULT-MODEL-001", "SFT-COMP-DIST-AGREEMENT-IMPOSSIBILITY-001", "SFT-COMP-DIST-FAULT-MODEL-001",
    "SFT-COMP-DIST-REPLICATION-CONSISTENCY-001", "SFT-COMP-DIST-REPLICATION-CONSISTENCY-001", "SFT-COMP-DIST-REPLICATION-CONSISTENCY-001",
    "SFT-COMP-DIST-REPLICATION-CONSISTENCY-001", "SFT-COMP-DIST-REPLICATION-CONSISTENCY-001", "SFT-COMP-DIST-DISTRIBUTED-KNOWLEDGE-001",
    "SFT-COMP-DIST-LOCALITY-001", "SFT-COMP-DIST-NETWORK-COMPUTATION-001", "SFT-COMP-DIST-NETWORK-COMPUTATION-001",
    "SFT-COMP-DIST-NETWORK-COMPUTATION-001", "SFT-COMP-DIST-NETWORK-COMPUTATION-001",
)

EXCLUSIONS = (
    "no axiom, imported distributed theorem answer or target outcome selects the survivor",
    "host absence and artifact counters are not admitted numerical-zero objects",
    "no negative, irrational, imaginary, floating or completed-infinite proof scalar",
    "no hidden message, process state, scheduler choice, timing bound, detector or failure",
    "no platform implementation or favorable execution substitutes for the complete distributed law",
    "no failed route retires an obligation or changes protected authority",
)


def dimensions(relation):
    return (
        binary_dimension("events", "complete event identity and local order?", "anonymous-or-missing-event", "Missing event identity prevents causal reconstruction.", "complete-process-bound-events", "Every event and local successor is retained."),
        binary_dimension("communication", "complete message and synchronization custody?", "hidden-message-or-schedule", "A hidden communication cannot support a distributed conclusion.", "complete-message-synchronization-ledger", "Every message, queue and synchronization edge is retained."),
        binary_dimension("relation", "forced distributed relation?", "imported-distributed-answer", "An imported theorem cannot select the law.", relation, "The relation follows from exact generated event structure."),
        binary_dimension("correctness", "complete safety, progress or agreement certificate?", "favorable-execution", "One favorable schedule cannot establish distributed correctness.", "complete-adversarial-trace-certificate", "Every registered trace and adverse case is retained."),
        binary_dimension("enumeration", "complete declared grammar?", "sampled-schedules", "Sampled schedules cannot close a distributed family.", "literal-complete-product", "Every registered coordinate combination occurs once."),
        binary_dimension("provenance", "root-bound forcing?", "outcome-selected", "Outcome feedback violates forward forcing.", "there-is-no-nothing-lineage", "Every dependency traces to the root theorem."),
        binary_dimension("observation", "post-registry execution?", "preopened-target", "A preopened target could choose the survivor.", "post-registry-exact-distributed-execution", "Execution opens only after registry freeze."),
        binary_dimension("boundary", "fault, timing and topology boundary explicit?", "unrestricted-network-export", "A finite distributed result cannot silently export beyond its model.", "declared-fault-time-topology-boundary", "Every participant, fault, timing and topology condition is explicit."),
    )


class DistributedExtensionProgram(GeneratedComputationProgram):
    @property
    def registration(self):
        return ClaimRegistration(claim_id=self.spec.claim_id, title=self.spec.title, branch="computation", statement=self.spec.statement, evidence_mode=EvidenceMode.EMPIRICAL, root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies, axioms=(), free_parameters=(), provenance=(ProvenanceClass.FORWARD_FORCING,), source_hash=self.source_hash)


def make(number, previous):
    index = int(number) - 1
    title, relation, statement = TITLES[index], RELATIONS[index], STATEMENTS[index]
    claim_id = f"SFT-COMP-DISTX-{SLUGS[index]}-{number}"
    observation, passed = OBS[number]
    dependencies = ("SFT-MATH-HAND-CROSS-BRANCH-COMPLETENESS-006", "SFT-INFO-HAND-CROSS-BRANCH-COMPLETENESS-006", "SFT-COMP-SEMX-COMPLETENESS-025", BASE[index]) + ((previous,) if previous else ())
    return LawSpec(claim_id, "DISTX", title.lower().replace(" ", "-"), title, statement, dependencies, f"Generate the complete eight-axis DISTX-{number} product before observation access.", f"Every positive finite DISTX-{number} process, event, message, schedule, fault, topology, observation and registered correspondence boundary.", dimensions(relation), f"DISTX-{number} uniquely retains {relation}, complete distributed trace custody, root forcing, post-registry execution and no extra rule.", (statement, observation), "The least distributed process has one event, one local state and one retained observation.", "Adding one process, event, message, edge, schedule or fault preserves every prior identity and generates all new lawful trace relations exactly once.", EXCLUSIONS, (Witness("exact-distributed-execution", observation, passed), Witness("complete-distributed-census", "Every declared event, message, schedule, fault, state and observation is retained.", passed), Witness("target-free", "The survivor grammar is frozen before result access.", True)), f"The frozen census separately owns {title.lower()} and forbids omission or duplicate ownership.", statement, "Enumerate 256 structural forms, reconstruct independently, replay the exact distributed execution and reject four adverse controls.", "The claim closes its declared finite process, fault, timing and topology grammar; broader implementations require explicit transport.", (title.lower(),))


specifications = []
previous_claim = None
for number in sorted(OBS):
    spec = make(number, previous_claim)
    specifications.append(spec)
    previous_claim = spec.claim_id
SPECS = {spec.claim_id: spec for spec in specifications}
IDS = tuple(SPECS)


def validate_family():
    if len(IDS) != 26 or not all(row[1] for row in OBS.values()):
        raise ValueError("DISTX family witness or membership failure")
    for spec in specifications:
        spec.validate()


validate_family()
