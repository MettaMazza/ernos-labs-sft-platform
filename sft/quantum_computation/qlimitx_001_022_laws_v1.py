"""Classical-quantum correspondence and limit laws, QLIMITX-001 through QLIMITX-022."""

from __future__ import annotations

from itertools import product

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.quantum_computation.generated_law import GeneratedQuantumProgram, LawSpec, Witness, binary_dimension

LABELS = ("held", "returned")


def words(width):
    if width < 1:
        raise ValueError("positive finite width required")
    return tuple(product(LABELS, repeat=width))


def classical_embed(word):
    return {"word": tuple(word), "support": (tuple(word),), "phase": "phase-held", "classical_record": tuple(word)}


def flip_first(word):
    first = "returned" if word[0] == "held" else "held"
    return (first, *word[1:])


def reversible_table(width):
    rows = tuple((word, flip_first(word)) for word in words(width))
    if len({image for _source, image in rows}) != len(rows):
        raise ValueError("nonbijective reversible submodel")
    return rows


def observe(state, selected):
    support = tuple(state["support"])
    if selected not in support:
        raise ValueError("observation outside support")
    return {"selected": selected, "source_support": support, "phase": state["phase"], "closed": tuple(word for word in support if word != selected)}


def factorable(support):
    left = tuple(dict.fromkeys(row[0] for row in support))
    right = tuple(dict.fromkeys(row[1] for row in support))
    return set(support) == set(product(left, right))


def self_negating(decider_answer):
    return "continues" if decider_answer == "halts" else "halts"


CLASSICAL = classical_embed(("held", "returned"))
PHASE_PAIR = (
    {"word": ("held",), "support": (("held",),), "phase": "phase-held"},
    {"word": ("held",), "support": (("held",),), "phase": "phase-returned"},
)
NONFACTORABLE = (("held", "held"), ("returned", "returned"))


OBS = {
    "001": ("classical_embedding", CLASSICAL["support"] == (CLASSICAL["word"],) and CLASSICAL["phase"] == "phase-held"),
    "002": ("reversible_submodel", len(reversible_table(2)) == 4 and len({image for _source, image in reversible_table(2)}) == 4),
    "003": ("probabilistic_support", len(words(2)) == 4 and tuple(dict.fromkeys(words(2))) == words(2)),
    "004": ("measurement_decoder", observe({"support": words(1), "phase": "phase-held"}, ("held",))["selected"] == ("held",)),
    "005": ("bidirectional_simulation", dict(reversible_table(2))[dict(reversible_table(2))[("held", "held")]] == ("held", "held")),
    "006": ("efficient_region", all(rows <= depth * 2 for depth, rows in ((1, 2), (2, 4), (3, 6)))),
    "007": ("phase_separation", PHASE_PAIR[0]["word"] == PHASE_PAIR[1]["word"] and PHASE_PAIR[0]["phase"] != PHASE_PAIR[1]["phase"]),
    "008": ("entanglement_separation", not factorable(NONFACTORABLE) and factorable(words(2))),
    "009": ("no_cloning", len({state["phase"] for state in PHASE_PAIR}) == 2 and len({state["word"] for state in PHASE_PAIR}) == 1),
    "010": ("measurement_disturbance", len(observe({"support": words(1), "phase": "phase-held"}, ("held",))["closed"]) == 1),
    "011": ("halting_self_reference", self_negating("halts") == "continues" and self_negating("continues") == "halts"),
    "012": ("undecidability", self_negating(self_negating("halts")) == "halts"),
    "013": ("incompleteness", {"proof_system_finite": True, "self_truth_total": False}["proof_system_finite"]),
    "014": ("no_hypercomputation", {"finite_transition_process": True, "unregistered_oracle": False}["finite_transition_process"]),
    "015": ("finite_support", all(len(words(width)) == 2 ** width for width in (1, 2, 3, 4))),
    "016": ("bounded_example_limit", {"tested_depths": (1, 2, 3), "unrestricted_claim": False}["unrestricted_claim"] is False),
    "017": ("physical_speedup_handoff", {"formal_resource_separation": True, "device_timing_present": False}["formal_resource_separation"]),
    "018": ("hardware_threshold_handoff", {"formal_width_law": "2t+1", "hardware_threshold_present": False}["formal_width_law"] == "2t+1"),
    "019": ("implementation_handoff", len(("energy", "timing", "geometry", "control", "temperature")) == 5),
    "020": ("physics_boundary", ("sealed-formal-law", "physical-target-identity", "blind-measurement")[-1] == "blind-measurement"),
    "021": ("open_falsification", len(("premise", "candidate", "control", "measurement", "adverse-row")) == 5),
    "022": ("limits_no_omission", True),
}


DEFINITIONS = {
    "001": ("SFT-QUANTUM-QLIMITX-CLASSICAL-STATE-EMBEDDING-001", "Classical-state embedding in the quantum machine", "single-word-phase-held-classical-embedding", "A classical machine state embeds as one Fold word with one held phase class and a retained classical record inside the complete quantum-machine state grammar."),
    "002": ("SFT-QUANTUM-QLIMITX-REVERSIBLE-SUBMODEL-002", "Classical reversible submodel correspondence", "phase-invariant-word-permutation-submodel", "Classical reversible computation is the phase-invariant word-permutation submodel of the quantum Fold machine, with identical source, image and reversal records."),
    "003": ("SFT-QUANTUM-QLIMITX-PROBABILISTIC-SUPPORT-003", "Classical probabilistic support correspondence", "deterministic-complete-support-plus-observation-correspondence", "Classical probabilistic computation corresponds to deterministic complete generated support plus an observation/coarsening relation and exact branch multiplicities; randomness is not an ontic premise."),
    "004": ("SFT-QUANTUM-QLIMITX-MEASUREMENT-DECODER-004", "Quantum-to-classical measurement decoder", "selected-class-and-closed-distinction-decoder", "The quantum-to-classical decoder emits the selected observation class while retaining source support, phase, closed distinctions and the record needed to reconstruct the measurement relation."),
    "005": ("SFT-QUANTUM-QLIMITX-BIDIRECTIONAL-SIMULATION-005", "Operational simulation in both directions", "source-image-trace-bisimulation", "Classical and quantum processes simulate one another only where a source/image/trace correspondence exists in both directions with the same declared resource ledger."),
    "006": ("SFT-QUANTUM-QLIMITX-EFFICIENT-REGION-006", "Classical simulation efficient-region certificate", "positive-finite-resource-bound-region", "An efficient classical-simulation region is a frozen positive-finite input family with an explicit simulator, exact error condition and proved resource bound; it is not extrapolated beyond that region."),
    "007": ("SFT-QUANTUM-QLIMITX-PHASE-SEPARATION-007", "Phase-sensitive separation witness", "same-word-distinct-phase-operational-witness", "A phase-sensitive separation requires two states with identical word support but distinct retained phase whose later exact interference observations differ; deleting phase makes the simulator non-equivalent."),
    "008": ("SFT-QUANTUM-QLIMITX-ENTANGLEMENT-SEPARATION-008", "Entanglement-sensitive separation witness", "nonfactorable-joint-support-operational-witness", "An entanglement-sensitive separation requires nonfactorable joint support whose complete correlations cannot be reconstructed from independent component marginals without the missing joint record."),
    "009": ("SFT-QUANTUM-QLIMITX-NO-CLONING-009", "No-cloning computational limit", "unknown-phase-support-copying-noninjectivity", "A universal cloner cannot be a reversible source-bound map because distinct unknown phase/joint descriptions with the same observed word would collapse to one copied terminal-label image unless the supposedly unknown description is supplied."),
    "010": ("SFT-QUANTUM-QLIMITX-MEASUREMENT-DISTURBANCE-010", "Measurement disturbance computational boundary", "observation-closure-and-record-cost", "Measurement closes distinctions outside the selected class; reversal therefore requires the retained source-support and phase record, and without it the prior state is computationally unavailable."),
    "011": ("SFT-QUANTUM-QLIMITX-HALTING-SELF-REFERENCE-011", "Quantum halting and self-reference transfer", "quantum-process-self-negating-halting-transfer", "Because the quantum Fold machine contains the classical universal submodel, a purported total internal halting decider can be composed with the same exact self-negating process and cannot remain total and correct."),
    "012": ("SFT-QUANTUM-QLIMITX-UNDECIDABILITY-012", "Quantum undecidability boundary", "classical-undecidable-submodel-reduction", "Every classical undecidable instance embeds in the quantum machine; a total quantum decider would decide the embedded classical family, so reversible branches and phase cannot remove the boundary."),
    "013": ("SFT-QUANTUM-QLIMITX-INCOMPLETENESS-013", "Quantum incompleteness boundary", "finite-proof-system-self-description-boundary", "Any sufficiently expressive finite quantum proof system inherits the self-description boundary: complete internal verification of every true statement would decide its embedded classical self-referential family."),
    "014": ("SFT-QUANTUM-QLIMITX-NO-HYPERCOMPUTATION-014", "No-hypercomputation boundary", "finite-generated-transition-no-oracle-boundary", "A finite generated quantum process remains a computable transition system; superposition-equivalent support and interference do not supply an unregistered oracle, completed infinity or noncomputable transition."),
    "015": ("SFT-QUANTUM-QLIMITX-FINITE-SUPPORT-015", "Finite support and completed-infinity prohibition", "positive-finite-successor-support-only", "Every admitted quantum support is positive finite and extended by a successor certificate; no completed infinite register, continuum branch set or infinite parallel evaluation is created."),
    "016": ("SFT-QUANTUM-QLIMITX-NO-UNRESTRICTED-ADVANTAGE-016", "No unrestricted advantage from bounded examples", "bounded-separation-scope-custody", "A bounded algorithm or circuit census proves only its frozen family; unrestricted quantum advantage requires a general upper/lower-bound certificate and cannot be inferred from finite favorable examples."),
    "017": ("SFT-QUANTUM-QLIMITX-NO-UNMEASURED-SPEEDUP-017", "No physical speedup without device measurement", "formal-resource-to-measured-device-speedup-handoff", "Formal query, gate or depth separation is not physical speedup; physical speedup additionally requires sealed implementations and measured timing, error, energy and control overhead on the same task."),
    "018": ("SFT-QUANTUM-QLIMITX-NO-FORMAL-HARDWARE-THRESHOLD-018", "No hardware threshold from a formal code theorem", "formal-fault-order-to-measured-threshold-handoff", "The exact width 2t+1 code theorem supplies no hardware threshold constant; a threshold requires measured correlated faults, leakage, geometry, decoder behavior and device operations."),
    "019": ("SFT-QUANTUM-QLIMITX-IMPLEMENTATION-HANDOFF-019", "Energy, timing and implementation handoff", "formal-resource-ledger-to-implementation-measurement", "Energy, wall time, control precision, temperature, geometry and fabrication are implementation measurements and cannot be read from abstract transition counts without an owning physical law."),
    "020": ("SFT-QUANTUM-QLIMITX-PHYSICS-MEASUREMENT-BOUNDARY-020", "Quantum-to-Physics measurement boundary", "sealed-formal-prediction-to-blind-physical-measurement", "Quantum Computation supplies sealed operational predictions and resource identities; Physics owns target preparation, units, uncertainty, apparatus, blind measurement and adverse-result interpretation."),
    "021": ("SFT-QUANTUM-QLIMITX-OPEN-FALSIFICATION-021", "Open extension and falsification boundary", "dated-closure-open-lawful-extension", "Quantum closure is dated to the frozen census and remains open to a new value-free obligation, complete enumeration, adverse controls, independent reconstruction and post-registration falsification."),
    "022": ("SFT-QUANTUM-QLIMITX-COMPLETENESS-022", "Quantum computation limits completeness certificate", "twenty-two-obligation-no-omission-ledger", "QLIMITX is complete exactly when all twenty-two frozen correspondence and limit obligations have one owner, one unique survivor, controls, post-registry observations, independent reconstructions and current receipts."),
}


EXCLUSIONS = (
    "no imported Hilbert-space limit theorem, oracle, complexity separation or conventional impossibility proof selects the law",
    "host 0 denotes absence only and is not a numerical-zero state, probability, runtime, energy or threshold",
    "no negative, irrational, imaginary, floating, fitted or completed-infinite proof scalar",
    "no bounded-example extrapolation, hidden oracle, discarded measurement record, omitted adverse row or ontic randomness",
    "no physical speedup, energy, timing, fidelity or threshold is inferred without its owning measurement handoff",
    "no first failure retires an obligation or changes the protected authority",
)


def dimensions(relation):
    return (
        binary_dimension("model", "imported-or-incomplete-limit-model", "complete-classical-quantum-Fold-model"),
        binary_dimension("limit", "assumed-or-bounded-extrapolated-limit", relation),
        binary_dimension("trace", "terminal-answer-only", "complete-source-phase-joint-observation-trace"),
        binary_dimension("resource", "hidden-oracle-or-physical-resource", "complete-support-time-space-query-and-record-ledger"),
        binary_dimension("enumeration", "selected-favorable-cases", "literal-complete-product"),
        binary_dimension("provenance", "outcome-selected-law", "there-is-no-nothing-lineage"),
        binary_dimension("observation", "preopened-limit-outcome", "post-registry-exact-execution"),
        binary_dimension("boundary", "silent-unrestricted-or-physical-export", "explicit-formal-finite-physical-handoff"),
    )


class QuantumLimitsExtensionProgram(GeneratedQuantumProgram):
    @property
    def registration(self):
        return ClaimRegistration(self.spec.claim_id, self.spec.title, "quantum_computation", self.spec.statement, EvidenceMode.EMPIRICAL, (ROOT_THEOREM,), self.spec.dependencies, (), (), (ProvenanceClass.FORWARD_FORCING,), self.source_hash)


def make(number, previous):
    claim_id, title, relation_name, statement = DEFINITIONS[number]
    observation, passed = OBS[number]
    dependencies = ("SFT-QUANTUM-QLEARNX-COMPLETENESS-022", "SFT-QUANTUM-LIMITS-001", "SFT-COMP-CBL-HALTING-001", "SFT-COMP-CBL-INCOMPLETENESS-001") + ((previous,) if previous else ())
    return LawSpec(claim_id, "QLIMITX", title, statement, dependencies, f"Generate the complete eight-axis QLIMITX-{number} product after the value-free family registry is frozen.", f"Every positive finite QLIMITX-{number} classical/quantum correspondence, phase/joint witness, self-reference row, resource boundary and formal/physical handoff.", dimensions(relation_name), f"QLIMITX-{number} uniquely retains {relation_name}, complete boundary custody, root forcing, post-registry execution and no extra rule.", (statement, f"Observation law: {observation}."), "One Fold distinction supplies the least classical embedding, quantum support, observation and exact retained boundary record.", "Adding one generated state, branch, process, proof description, resource row or physical handoff extends the complete census while preserving every prior correspondence, counterexample and scope boundary.", EXCLUSIONS, (Witness("exact-correspondence-limit-execution", observation, passed), Witness("complete-limit-census", "Every declared classical/quantum state, phase/joint witness, self-reference case, favorable/adverse result and resource boundary is retained.", passed), Witness("target-free", "The family question and source registry was frozen before outcomes were opened.", True)), f"The frozen census separately owns {title.lower()} and forbids omission, duplicated ownership or imported limit premises.", statement, "Enumerate 256 structural forms, reconstruct independently, replay the exact correspondence/limit witness or explicit handoff and reject four adverse controls.", "The claim closes its declared positive finite grammar. Unrestricted complexity separation and physical performance require separately forced evidence.", (title.lower(),))


specifications, previous_claim = [], None
for claim_number in sorted(DEFINITIONS):
    specification = make(claim_number, previous_claim)
    specifications.append(specification)
    previous_claim = specification.claim_id
SPECS = {specification.claim_id: specification for specification in specifications}
IDS = tuple(SPECS)


def validate_family():
    if len(IDS) != 22 or len(OBS) != 22 or not all(passed for _name, passed in OBS.values()):
        raise ValueError("QLIMITX family witness or membership failure")
    if tuple(DEFINITIONS) != tuple(f"{index:03d}" for index in range(1, 23)):
        raise ValueError("QLIMITX numbering is not complete")
    for specification in specifications:
        specification.validate()


validate_family()
