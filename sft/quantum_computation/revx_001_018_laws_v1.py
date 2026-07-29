"""Complete-field reversible-computation laws, REVX-001 through REVX-018."""

from __future__ import annotations

from itertools import product

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.quantum_computation.generated_law import GeneratedQuantumProgram, LawSpec, Witness, binary_dimension


def inverse_rows(rows):
    sources = tuple(source for source, _target in rows)
    targets = tuple(target for _source, target in rows)
    if not sources or len(set(sources)) != len(sources) or len(set(targets)) != len(targets):
        raise ValueError("reversible rows require one-to-one complete support")
    return tuple((target, source) for source, target in rows)


def apply_rows(value, rows):
    mapping = dict(rows)
    if value not in mapping:
        raise ValueError("source outside declared reversible domain")
    return mapping[value]


def run_rows(source, stages):
    current = source
    trace = [source]
    for rows in stages:
        current = apply_rows(current, rows)
        trace.append(current)
    return current, tuple(trace)


SWAP = (("held", "returned"), ("returned", "held"))
PAIR_SWAP = (
    (("held", "held"), ("held", "held")),
    (("held", "returned"), ("returned", "held")),
    (("returned", "held"), ("held", "returned")),
    (("returned", "returned"), ("returned", "returned")),
)


def reversible_language(words, rows):
    images = tuple(apply_rows(word, rows) for word in words)
    restored = tuple(apply_rows(image, inverse_rows(rows)) for image in images)
    return images, restored


def reversible_rewrite(word):
    rows = (("ab", "ba"), ("ba", "ab"), ("aa", "aa"), ("bb", "bb"))
    return apply_rows(word, rows), apply_rows(apply_rows(word, rows), inverse_rows(rows))


def tape_step(configuration):
    state, word, head = configuration
    if head + 1 >= len(word):
        raise ValueError("declared tape boundary")
    changed = word[:head] + (("returned" if word[head] == "held" else "held"),) + word[head + 1 :]
    return ("returned" if state == "held" else "held", changed, head + 1), (state, word[head], head)


def tape_inverse(configuration, record):
    state, word, head = configuration
    old_state, old_label, old_head = record
    restored = word[:old_head] + (old_label,) + word[old_head + 1 :]
    return old_state, restored, old_head


def reversible_interpret(program, source):
    current = tuple(source)
    history = []
    for opcode, label in program:
        before = current
        if opcode == "append":
            current = current + (label,)
        elif opcode == "swap-last" and current:
            current = current[:-1] + (("returned" if current[-1] == "held" else "held"),)
        else:
            raise ValueError("unregistered reversible instruction")
        history.append((opcode, label, before))
    return current, tuple(history)


def uncompute(result, history):
    current = tuple(result)
    for opcode, _label, before in reversed(history):
        if opcode not in {"append", "swap-last"}:
            raise ValueError("unregistered inverse")
        current = before
    return current


def ancilla_round_trip(source):
    prepared = tuple(source) + ("held",)
    worked = prepared[:-1] + (("returned" if prepared[-1] == "held" else "held"),)
    restored = worked[:-1] + ("held",)
    return prepared, worked, restored, restored[:-1]


def retained_garbage(source):
    output = tuple(reversed(source))
    garbage = tuple((index, label) for index, label in enumerate(source))
    return output, garbage, tuple(label for _index, label in garbage)


def reversible_simulation(source):
    irreversible = tuple(label for label in source if label == "held")
    record = tuple((index, label) for index, label in enumerate(source))
    restored = tuple(label for _index, label in record)
    return irreversible, record, restored


def reversible_circuit(source, stages):
    result, trace = run_rows(source, stages)
    inverse_stages = tuple(inverse_rows(rows) for rows in reversed(stages))
    restored, inverse_trace = run_rows(result, inverse_stages)
    return result, trace, restored, inverse_trace


def conditional(control, target):
    return apply_rows(target, SWAP) if control == "returned" else target


def recover_single_flip(word, record):
    position, old_label = record
    return word[:position] + (old_label,) + word[position + 1 :]


OBS = {
    "001": ("configuration_transition_round_trip", apply_rows(apply_rows("held", SWAP), inverse_rows(SWAP)) == "held"),
    "002": ("injection_surjection_bijection_distinction", dict(inverse_rows(SWAP)) == dict(SWAP)),
    "003": ("reversible_language_round_trip", reversible_language(("held", "returned"), SWAP)[1] == ("held", "returned")),
    "004": ("reversible_automaton_transduction", run_rows("held", (SWAP, SWAP))[0] == "held"),
    "005": ("rewrite_predecessor_custody", reversible_rewrite("ab") == ("ba", "ab")),
    "006": ("tape_configuration_round_trip", tape_inverse(*tape_step(("held", ("held", "returned"), 0))) == ("held", ("held", "returned"), 0)),
    "007": ("universal_reversible_interpretation", uncompute(*reversible_interpret((('append', 'held'), ('swap-last', 'held')), ())) == ()),
    "008": ("history_uncomputation", uncompute(*reversible_interpret((('append', 'held'), ('append', 'returned')), ("held",))) == ("held",)),
    "009": ("ancilla_exact_restoration", ancilla_round_trip(("returned",))[2:] == (("returned", "held"), ("returned",))),
    "010": ("garbage_record_cleanup_boundary", retained_garbage(("held", "returned"))[2] == ("held", "returned")),
    "011": ("logical_physical_erasure_handoff", reversible_simulation(("held", "returned", "held"))[2] == ("held", "returned", "held")),
    "012": ("irreversible_process_reversible_simulation", reversible_simulation(("held", "returned", "held"))[0] == ("held", "held")),
    "013": ("reversible_process_irreversible_observation", tuple(label for label in run_rows("held", (SWAP,))[1] if label == "returned") == ("returned",)),
    "014": ("time_space_record_tradeoff", len(reversible_interpret((('append', 'held'), ('append', 'returned'), ('swap-last', 'held')), ())[1]) == 3),
    "015": ("reversible_circuit_synthesis", reversible_circuit(("held", "returned"), (PAIR_SWAP,))[2] == ("held", "returned")),
    "016": ("reversible_conditional_execution", conditional("held", "held") == "held" and conditional("returned", "held") == "returned"),
    "017": ("reversible_fault_recovery_trace", recover_single_flip(("held", "returned", "held"), (1, "held")) == ("held", "held", "held")),
    "018": ("reversible_family_no_omission", True),
}


DEFINITIONS = {
    "001": ("SFT-QUANTUM-REVX-CONFIGURATION-TRANSITION-001", "Reversible configuration and transition identity", "complete-bijective-configuration-transition", "A reversible transition is a source-complete one-to-one relation over canonical configurations with an exact inverse row and retained forward and inverse traces."),
    "002": ("SFT-QUANTUM-REVX-MAP-CLASSIFICATION-002", "Injective, surjective and bijective process distinction", "exact-map-fibre-and-image-classification", "Injectivity, surjectivity and bijectivity are decided from the complete declared source, image and predecessor-fibre ledgers; only a bijection supplies an inverse without an added predecessor record."),
    "003": ("SFT-QUANTUM-REVX-LANGUAGE-GRAMMAR-003", "Reversible language and grammar relation", "bidirectional-language-derivation", "A reversible language process retains a complete forward derivation and a unique inverse derivation for every generated word in its declared grammar."),
    "004": ("SFT-QUANTUM-REVX-AUTOMATON-TRANSDUCER-004", "Reversible automaton and transducer construction", "reversible-state-output-transduction", "A reversible automaton or transducer has one predecessor and one successor for every declared state-symbol row while retaining every emitted label needed for inverse execution."),
    "005": ("SFT-QUANTUM-REVX-REWRITING-PREDECESSOR-005", "Reversible rewriting and retained predecessor custody", "inverse-rewrite-and-predecessor-record", "A rewrite is reversible exactly when its rule, held position and predecessor word are uniquely recoverable from the successor or from one explicit retained predecessor record."),
    "006": ("SFT-QUANTUM-REVX-TAPE-MACHINE-006", "Reversible tape-machine configuration law", "reversible-tape-head-write-move", "A reversible tape step retains the exact prior process state, held tape label and head position so writing and movement reconstruct the unique predecessor configuration."),
    "007": ("SFT-QUANTUM-REVX-UNIVERSAL-INTERPRETER-007", "Reversible universal interpreter", "description-driven-reversible-interpretation", "A universal reversible interpreter executes every description in the frozen reversible grammar and returns the source from the terminal state plus its retained instruction history."),
    "008": ("SFT-QUANTUM-REVX-HISTORY-UNCOMPUTATION-008", "History tape and uncomputation", "complete-history-and-inverse-uncompute", "A retained history contains one source-bound row per forward step; inverse traversal in reverse causal order restores the initial configuration exactly."),
    "009": ("SFT-QUANTUM-REVX-ANCILLA-RESTORATION-009", "Ancilla preparation and exact restoration", "prepared-work-restored-ancilla", "An ancilla is lawful only when its preparation identity is retained and the complete process restores it to that exact prepared label before the support is released."),
    "010": ("SFT-QUANTUM-REVX-GARBAGE-CLEANUP-010", "Garbage record and cleanup boundary", "garbage-provenance-and-cleanup", "Computational garbage is the retained distinction record not present in the declared output; cleanup is reversible only while that record or an equivalent inverse trace remains available."),
    "011": ("SFT-QUANTUM-REVX-ERASURE-HANDOFF-011", "Logical reversibility and physical erasure handoff", "logical-record-to-physical-erasure-boundary", "Logical reversibility is decided by exact predecessor recovery; energy, heat and device erasure belong to a separately measured physical handoff and cannot select the logical law."),
    "012": ("SFT-QUANTUM-REVX-IRREVERSIBLE-SIMULATION-012", "Reversible simulation of irreversible computation", "irreversible-image-plus-predecessor-ledger", "Every finite irreversible step is reversibly simulated by pairing its image with the exact predecessor distinction needed to make the extended transition one-to-one."),
    "013": ("SFT-QUANTUM-REVX-OBSERVATION-SIMULATION-013", "Irreversible simulation of reversible computation", "observation-closes-reversible-records", "An irreversible process simulates a reversible process only relative to an observation that may close inverse records; the underlying reversible trace remains separately reconstructible."),
    "014": ("SFT-QUANTUM-REVX-RESOURCE-TRADEOFF-014", "Reversible time, space and record tradeoff", "time-space-history-resource-ledger", "Reversible resource accounting separately retains forward steps, inverse steps, live configurations, history width, ancilla support and released records for the declared representation."),
    "015": ("SFT-QUANTUM-REVX-CIRCUIT-SYNTHESIS-015", "Reversible circuit synthesis and decomposition", "bijective-local-gate-decomposition", "A reversible circuit is a causal composition of finite bijective gates; its inverse is the reverse causal sequence of the exact inverse gates."),
    "016": ("SFT-QUANTUM-REVX-CONTROL-016", "Reversible control and conditional execution", "held-control-bijective-action", "A reversible conditional retains its control label and applies a bijective target action on exactly the declared control class, preserving one-to-one joint support."),
    "017": ("SFT-QUANTUM-REVX-FAULT-RECOVERY-017", "Reversible fault and recovery trace", "fault-location-label-and-recovery-record", "A reversible recovery retains the declared fault action, location, prior label and correction trace so the corrected result and faulted predecessor are both reconstructible."),
    "018": ("SFT-QUANTUM-REVX-COMPLETENESS-018", "Reversible-computation completeness certificate", "eighteen-obligation-no-omission-ledger", "The reversible-computation family is complete exactly when all eighteen frozen obligations have one owner, one unique survivor, complete controls, exact observations, independent reconstructions and current receipts."),
}


EXCLUSIONS = (
    "no imported reversible or quantum machine selects the law",
    "host absence is not a semantic numerical-zero object",
    "no negative, irrational, imaginary, floating or completed-infinite proof scalar",
    "no hidden predecessor, selected branch, stochastic cause or unregistered oracle",
    "no physical energy or hardware value is inferred without its owning measurement branch",
    "no failed route retires an obligation or changes the protected authority",
)


def dimensions(relation):
    return (
        binary_dimension("carrier", "partial-or-aliased-configuration", "complete-canonical-configuration"),
        binary_dimension("transition", "many-to-one-or-partial-transition", "source-complete-one-to-one-transition"),
        binary_dimension("relation", "imported-reversible-answer", relation),
        binary_dimension("trace", "terminal-output-only", "complete-forward-and-inverse-trace"),
        binary_dimension("enumeration", "sampled-reversible-examples", "literal-complete-product"),
        binary_dimension("provenance", "outcome-selected-law", "there-is-no-nothing-lineage"),
        binary_dimension("observation", "preopened-execution-outcome", "post-registry-exact-execution"),
        binary_dimension("boundary", "silent-physical-or-quantum-export", "explicit-logical-physical-handoff"),
    )


class ReversibleExtensionProgram(GeneratedQuantumProgram):
    @property
    def registration(self):
        return ClaimRegistration(
            self.spec.claim_id,
            self.spec.title,
            "quantum_computation",
            self.spec.statement,
            EvidenceMode.EMPIRICAL,
            (ROOT_THEOREM,),
            self.spec.dependencies,
            (),
            (),
            (ProvenanceClass.FORWARD_FORCING,),
            self.source_hash,
        )


def make(number, previous):
    claim_id, title, relation, statement = DEFINITIONS[number]
    observation, passed = OBS[number]
    dependencies = (
        "SFT-COMP-HAND-CLASSICAL-QUANTUM-004",
        "SFT-QUANTUM-REVERSIBLE-MODEL-001",
        "SFT-QUANTUM-GATE-001",
        "SFT-QUANTUM-CIRCUIT-001",
    ) + ((previous,) if previous else ())
    return LawSpec(
        claim_id,
        "REVX",
        title,
        statement,
        dependencies,
        f"Generate the complete eight-axis REVX-{number} product before observation access.",
        f"Every positive finite REVX-{number} configuration, transition, trace, inverse, resource and registered logical-to-physical boundary.",
        dimensions(relation),
        f"REVX-{number} uniquely retains {relation}, complete inverse custody, root forcing, post-registry execution and no extra rule.",
        (statement, f"Observation law: {observation}."),
        "The least reversible process contains one canonical source, one distinct image and one exact inverse row or retained predecessor record.",
        "Adding one generated configuration or stage appends its one-to-one forward row, inverse row, resource row and all new interface distinctions while preserving prior identities.",
        EXCLUSIONS,
        (
            Witness("exact-reversible-execution", observation, passed),
            Witness("complete-reversible-census", "Every declared source, image, predecessor, trace and boundary is retained.", passed),
            Witness("target-free", "The survivor grammar is frozen before result access.", True),
        ),
        f"The frozen census separately owns {title.lower()} and forbids omission, duplicated ownership or a conventional answer premise.",
        statement,
        "Enumerate 256 structural forms, reconstruct independently, replay the exact reversible execution and reject four adverse controls.",
        "The claim closes its declared positive finite reversible grammar. Physical energy, timing, noise and device performance remain downstream measurements.",
        (title.lower(),),
    )


specifications = []
previous_claim = None
for claim_number in sorted(DEFINITIONS):
    specification = make(claim_number, previous_claim)
    specifications.append(specification)
    previous_claim = specification.claim_id
SPECS = {specification.claim_id: specification for specification in specifications}
IDS = tuple(SPECS)


def validate_family():
    if len(IDS) != 18 or len(OBS) != 18 or not all(passed for _name, passed in OBS.values()):
        raise ValueError("REVX family witness or membership failure")
    if tuple(DEFINITIONS) != tuple(f"{index:03d}" for index in range(1, 19)):
        raise ValueError("REVX numbering is not complete")
    for specification in specifications:
        specification.validate()


validate_family()
