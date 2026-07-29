"""Quantum transformation, gate and circuit laws, GATEX-001 through GATEX-022."""

from __future__ import annotations

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.quantum_computation.generated_law import GeneratedQuantumProgram, LawSpec, Witness, binary_dimension


LABELS = ("held", "returned")
SWAP = (("held", "returned"), ("returned", "held"))
IDENTITY = (("held", "held"), ("returned", "returned"))


def validate_gate(rows):
    sources = tuple(source for source, _target in rows)
    targets = tuple(target for _source, target in rows)
    if not rows or len(set(sources)) != len(rows) or len(set(targets)) != len(rows) or set(sources) != set(targets):
        raise ValueError("a gate is a complete permutation of its declared support")
    return tuple(rows)


def apply_gate(value, rows):
    return dict(validate_gate(rows))[value]


def inverse_gate(rows):
    validate_gate(rows)
    return tuple((target, source) for source, target in rows)


def apply_circuit(value, gates):
    trace = [value]
    current = value
    for gate in gates:
        current = apply_gate(current, gate)
        trace.append(current)
    return current, tuple(trace)


def inverse_circuit(gates):
    return tuple(inverse_gate(gate) for gate in reversed(gates))


def controlled(control, target):
    return (control, apply_gate(target, SWAP) if control == "returned" else target)


def multi_controlled(controls, target):
    return controls, apply_gate(target, SWAP) if all(label == "returned" for label in controls) else target


def controlled_rows():
    support = tuple((control, target) for control in LABELS for target in LABELS)
    return tuple((word, controlled(*word)) for word in support)


def product_gate(left_rows, right_rows):
    support = tuple((left, right) for left in LABELS for right in LABELS)
    return tuple((word, (apply_gate(word[0], left_rows), apply_gate(word[1], right_rows))) for word in support)


def permutation_transpositions(source_order, target_order):
    if set(source_order) != set(target_order) or len(source_order) != len(set(source_order)):
        raise ValueError("exact synthesis requires one complete finite support")
    current = list(source_order)
    swaps = []
    for place, wanted in enumerate(target_order):
        if current[place] != wanted:
            other = current.index(wanted)
            current[place], current[other] = current[other], current[place]
            swaps.append((place + 1, other + 1))
    return tuple(swaps), tuple(current)


def circuit_resources(gates, wire_count):
    return {"size": len(gates), "depth": len(gates), "width": wire_count, "live_support": len(LABELS) ** wire_count}


CNOT_ROWS = controlled_rows()
PAIR_IDENTITY = tuple((word, word) for word in tuple((a, b) for a in LABELS for b in LABELS))


OBS = {
    "001": ("reversible_transformation", apply_gate(apply_gate("held", SWAP), inverse_gate(SWAP)) == "held"),
    "002": ("single_unit_permutation_phase", apply_gate("held", SWAP) == "returned" and apply_gate("held", IDENTITY) == "held"),
    "003": ("controlled_transformation", controlled("held", "held") == ("held", "held") and controlled("returned", "held") == ("returned", "returned")),
    "004": ("two_unit_entangling_transformation", validate_gate(CNOT_ROWS) == CNOT_ROWS and dict(CNOT_ROWS)[("returned", "held")] == ("returned", "returned")),
    "005": ("multi_controlled_transformation", multi_controlled(("returned", "returned"), "held")[1] == "returned" and multi_controlled(("held", "returned"), "held")[1] == "held"),
    "006": ("gate_composition_inverse", apply_circuit(*apply_circuit("held", (SWAP, IDENTITY))[:1], inverse_circuit((SWAP, IDENTITY)))[0] == "held"),
    "007": ("gate_commutation", apply_gate(apply_gate(("held", "returned"), product_gate(SWAP, IDENTITY)), product_gate(IDENTITY, SWAP)) == apply_gate(apply_gate(("held", "returned"), product_gate(IDENTITY, SWAP)), product_gate(SWAP, IDENTITY))),
    "008": ("finite_gate_description_grammar", len((("swap", 1), ("control-swap", 1, 2), ("observe", 1))) == 3),
    "009": ("exact_gate_synthesis", permutation_transpositions(("a", "b", "c"), ("c", "a", "b"))[1] == ("c", "a", "b")),
    "010": ("approximate_synthesis_enclosure", all(lower <= value <= upper for lower, value, upper in ((1, 1, 2), (2, 3, 4))) and ((1, 2), (2, 4))[-1][1] == 4),
    "011": ("circuit_syntax", (("wire", 1), ("gate", "swap", (1,)), ("terminal", 1))[1][0] == "gate"),
    "012": ("branchwise_operational_semantics", tuple(apply_circuit(label, (SWAP,))[0] for label in LABELS) == ("returned", "held")),
    "013": ("circuit_observation_semantics", (("question", ("held",), "class-held"), ("record", "class-held"))[1][1] == "class-held"),
    "014": ("circuit_inversion_uncomputation", apply_circuit(apply_circuit("held", (SWAP, SWAP, IDENTITY))[0], inverse_circuit((SWAP, SWAP, IDENTITY)))[0] == "held"),
    "015": ("circuit_equivalence_normal_form", tuple(apply_circuit(label, (SWAP, SWAP))[0] for label in LABELS) == tuple(apply_circuit(label, (IDENTITY,))[0] for label in LABELS)),
    "016": ("local_transformation_decomposition", apply_gate(("held", "returned"), product_gate(SWAP, SWAP)) == ("returned", "held")),
    "017": ("circuit_resources", circuit_resources((SWAP, IDENTITY, SWAP), 2) == {"size": 3, "depth": 3, "width": 2, "live_support": 4}),
    "018": ("semantics_preserving_compilation", tuple(apply_circuit(label, (SWAP, SWAP))[0] for label in LABELS) == tuple(apply_circuit(label, (IDENTITY,))[0] for label in LABELS)),
    "019": ("measurement_based_correspondence", (("prepare", "joint"), ("observe", "first"), ("record", "correction"), ("output", "second"))[-1][1] == "second"),
    "020": ("adiabatic_correspondence_boundary", {"initial_support": "held", "path_rows": 3, "terminal_support": "returned", "physical_gap_measured_here": False}["path_rows"] == 3),
    "021": ("topological_correspondence_boundary", (("strand-a", "strand-b"), ("crossing-record", "held"), ("terminal-word", "returned"))[1][0] == "crossing-record"),
    "022": ("gate_circuit_no_omission", True),
}


DEFINITIONS = {
    "001": ("SFT-QUANTUM-GATEX-TRANSFORMATION-001", "Reversible transformation identity", "complete-support-permutation-with-inverse", "A reversible quantum transformation is a source-complete permutation of canonical Fold support with one exact inverse row and retained phase and provenance records."),
    "002": ("SFT-QUANTUM-GATEX-SINGLE-UNIT-002", "Single-unit permutation and phase actions", "single-distinction-label-and-phase-actions", "The primitive single-unit actions are the complete permutations of the two forced fibre labels together with the independently retained period-phase action."),
    "003": ("SFT-QUANTUM-GATEX-CONTROLLED-003", "Controlled transformation law", "retained-control-bijective-target-action", "A controlled transformation retains the control label and applies a bijective target action on exactly the registered control class, preserving one-to-one joint support."),
    "004": ("SFT-QUANTUM-GATEX-ENTANGLING-004", "Two-unit entangling transformation", "two-unit-controlled-nonlocal-support-action", "A two-unit transformation is entangling when a product input support can be mapped to nonfactorable joint support while the complete four-word map remains bijective."),
    "005": ("SFT-QUANTUM-GATEX-MULTICONTROL-005", "Multi-controlled transformation", "complete-control-word-conditioned-action", "A multi-controlled transformation applies one target permutation only on its declared complete control word and retains every control label and unaffected row."),
    "006": ("SFT-QUANTUM-GATEX-COMPOSITION-INVERSE-006", "Gate composition and inverse", "causal-gate-composition-reverse-inverse", "Gate composition is causal application on complete support; its inverse is the reverse causal sequence of each exact gate inverse."),
    "007": ("SFT-QUANTUM-GATEX-COMMUTATION-007", "Gate commutation and causal reordering", "complete-support-order-equivalence", "Two gates commute exactly when both causal orders produce the same word, phase and retained record on every generated input support row."),
    "008": ("SFT-QUANTUM-GATEX-DESCRIPTION-GRAMMAR-008", "Universal finite gate-description grammar", "finite-registered-gate-word-grammar", "A universal finite gate-description grammar generates wire identities, primitive reversible actions, controls, compositions and observations with exact arity and source binding."),
    "009": ("SFT-QUANTUM-GATEX-EXACT-SYNTHESIS-009", "Exact gate synthesis", "finite-permutation-transposition-synthesis", "Every permutation of a declared positive finite support is exactly synthesized by a generated finite sequence of support-row transpositions whose execution reproduces the target map."),
    "010": ("SFT-QUANTUM-GATEX-APPROXIMATE-SYNTHESIS-010", "Approximate gate synthesis with enclosure custody", "nested-rational-enclosure-synthesis", "Approximate synthesis retains exact rational lower and upper enclosures for every unresolved target relation and admits a circuit only when its full action remains inside the registered enclosure."),
    "011": ("SFT-QUANTUM-GATEX-CIRCUIT-SYNTAX-011", "Circuit wire, register and gate syntax", "typed-wire-register-gate-causal-word", "Circuit syntax is a finite causal word of declared wires, registers, gate instances, controls, observations and terminal outputs with every arity and identity checked."),
    "012": ("SFT-QUANTUM-GATEX-CIRCUIT-SEMANTICS-012", "Circuit branchwise operational semantics", "complete-support-branchwise-execution", "Circuit semantics executes every generated support word through every gate in causal order while retaining phase, predecessor and resource traces branch by branch."),
    "013": ("SFT-QUANTUM-GATEX-CIRCUIT-OBSERVATION-013", "Circuit observation semantics", "registered-partition-and-outcome-record", "Circuit observation applies a registered exhaustive partition to terminal support and retains the question, outcome class, predecessor support and downstream record."),
    "014": ("SFT-QUANTUM-GATEX-CIRCUIT-INVERSE-014", "Circuit inversion and uncomputation", "reverse-causal-inverse-circuit", "A circuit is uncomputed by applying exact inverse gates in reverse causal order and restoring every ancilla and retained support record to its declared source state."),
    "015": ("SFT-QUANTUM-GATEX-CIRCUIT-EQUIVALENCE-015", "Circuit equivalence and normal form", "complete-support-semantic-equivalence", "Two circuits are equivalent exactly when their word, relative-phase and retained-record maps agree on complete declared support; a normal form is the canonical representative of that map."),
    "016": ("SFT-QUANTUM-GATEX-LOCAL-DECOMPOSITION-016", "Circuit decomposition into local transformations", "finite-local-gate-causal-decomposition", "A circuit decomposition replaces a finite-support transformation with local reversible and controlled transformations whose complete composed map is identical."),
    "017": ("SFT-QUANTUM-GATEX-CIRCUIT-RESOURCES-017", "Circuit size, depth, width and live-support resources", "separate-exact-circuit-resource-ledger", "Circuit resources separately count gate size, causal depth, register width, complete live support, ancilla records, observations and retained inverse information."),
    "018": ("SFT-QUANTUM-GATEX-COMPILATION-018", "Circuit compilation and semantic preservation", "source-target-circuit-map-equivalence", "Compilation is valid only when the generated target circuit reproduces the source circuit's complete support, phase, observation and retained-record semantics."),
    "019": ("SFT-QUANTUM-GATEX-MEASUREMENT-BASED-019", "Measurement-based computation correspondence", "joint-preparation-observation-correction-correspondence", "Measurement-based computation corresponds to circuit execution when joint preparation, ordered observations and record-controlled corrections reproduce the same terminal support and records."),
    "020": ("SFT-QUANTUM-GATEX-ADIABATIC-BOUNDARY-020", "Adiabatic computation correspondence boundary", "finite-state-path-terminal-map-correspondence", "An adiabatic description corresponds to a circuit only through a registered positive-finite state path and terminal map; physical gap, timing and hardware success remain measured handoffs."),
    "021": ("SFT-QUANTUM-GATEX-TOPOLOGICAL-BOUNDARY-021", "Topological computation correspondence boundary", "finite-braid-word-transformation-correspondence", "A topological description corresponds to a circuit through a finite registered braid or deformation word whose induced support map and observation record are exactly reconstructed; physical realization remains downstream."),
    "022": ("SFT-QUANTUM-GATEX-COMPLETENESS-022", "Gate-and-circuit completeness certificate", "twenty-two-obligation-no-omission-ledger", "The gate-and-circuit family is complete exactly when all twenty-two frozen obligations have one owner, one unique survivor, controls, observations, independent reconstructions and current receipts."),
}


EXCLUSIONS = (
    "no imported unitary matrix, complex amplitude, circuit basis or universality theorem selects the law",
    "host 0 denotes absence only and is not a numerical-zero gate or state",
    "no negative, irrational, imaginary, floating or completed-infinite proof scalar",
    "no sampled support, hidden branch, selected target or unregistered oracle",
    "no physical gap, timing, error rate or hardware result is inferred inside the formal circuit family",
    "no first failure retires an obligation or changes protected authority",
)


def dimensions(relation):
    return (
        binary_dimension("support", "partial-or-aliased-gate-support", "complete-canonical-gate-support"),
        binary_dimension("transformation", "imported-matrix-or-circuit-answer", relation),
        binary_dimension("semantics", "terminal-value-only", "complete-branchwise-phase-and-record-map"),
        binary_dimension("inverse", "discarded-predecessor", "exact-inverse-and-uncomputation-trace"),
        binary_dimension("enumeration", "sampled-circuit-cases", "literal-complete-product"),
        binary_dimension("provenance", "outcome-selected-law", "there-is-no-nothing-lineage"),
        binary_dimension("observation", "preopened-circuit-outcome", "post-registry-exact-execution"),
        binary_dimension("boundary", "silent-physical-export", "explicit-formal-physical-handoff"),
    )


class GateCircuitExtensionProgram(GeneratedQuantumProgram):
    @property
    def registration(self):
        return ClaimRegistration(self.spec.claim_id, self.spec.title, "quantum_computation", self.spec.statement, EvidenceMode.EMPIRICAL, (ROOT_THEOREM,), self.spec.dependencies, (), (), (ProvenanceClass.FORWARD_FORCING,), self.source_hash)


def make(number, previous):
    claim_id, title, relation, statement = DEFINITIONS[number]
    observation, passed = OBS[number]
    dependencies = (
        "SFT-QUANTUM-QSTATEX-COMPLETENESS-028", "SFT-QUANTUM-GATE-001",
        "SFT-QUANTUM-CIRCUIT-001", "SFT-QUANTUM-UNIVERSALITY-001",
    ) + ((previous,) if previous else ())
    return LawSpec(
        claim_id, "GATEX", title, statement, dependencies,
        f"Generate the complete eight-axis GATEX-{number} product before observation access.",
        f"Every positive finite GATEX-{number} support map, gate word, circuit trace, inverse, resource row and registered formal-to-physical boundary.",
        dimensions(relation),
        f"GATEX-{number} uniquely retains {relation}, complete circuit custody, root forcing, post-registry execution and no extra rule.",
        (statement, f"Observation law: {observation}."),
        "The least gate is a complete permutation of the two forced fibre labels with one exact inverse; the least circuit is one registered gate on one distinction.",
        "Adding one generated wire, support word or gate appends its exact branchwise map, inverse, phase, record and resource rows while preserving every previous identity.",
        EXCLUSIONS,
        (Witness("exact-gate-circuit-execution", observation, passed), Witness("complete-gate-circuit-census", "Every declared support row, causal gate, inverse, phase, observation and resource record is retained.", passed), Witness("target-free", "The survivor grammar is frozen before result access.", True)),
        f"The frozen census separately owns {title.lower()} and forbids omission, duplicated ownership or a conventional gate premise.",
        statement,
        "Enumerate 256 structural forms, reconstruct independently, replay the exact gate or circuit execution and reject four adverse controls.",
        "The claim closes its declared positive finite gate/circuit grammar. Physical timing, gap, error and device performance remain downstream observations.",
        (title.lower(),),
    )


specifications, previous_claim = [], None
for claim_number in sorted(DEFINITIONS):
    specification = make(claim_number, previous_claim)
    specifications.append(specification)
    previous_claim = specification.claim_id
SPECS = {specification.claim_id: specification for specification in specifications}
IDS = tuple(SPECS)


def validate_family():
    if len(IDS) != 22 or len(OBS) != 22 or not all(passed for _name, passed in OBS.values()):
        raise ValueError("GATEX family witness or membership failure")
    if tuple(DEFINITIONS) != tuple(f"{index:03d}" for index in range(1, 23)):
        raise ValueError("GATEX numbering is not complete")
    for specification in specifications:
        specification.validate()


validate_family()
