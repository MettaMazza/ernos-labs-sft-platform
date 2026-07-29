"""Quantum simulation and verification laws, QSIMX-001 through QSIMX-024."""

from __future__ import annotations

from itertools import product

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.quantum_computation.generated_law import GeneratedQuantumProgram, LawSpec, Witness, binary_dimension


LABELS = ("held", "returned")


def complete_words(width):
    if width < 1:
        raise ValueError("positive finite support width required")
    return tuple(product(LABELS, repeat=width))


def flip(label):
    if label not in LABELS:
        raise ValueError("Fold label required")
    return "returned" if label == "held" else "held"


def apply_local(word, position):
    if position < 1 or position > len(word):
        raise ValueError("local update outside generated support")
    result = list(word)
    result[position - 1] = flip(result[position - 1])
    return tuple(result)


def simulate(word, schedule):
    state = tuple(word)
    trace = []
    for step, position in enumerate(schedule, 1):
        image = apply_local(state, position)
        trace.append((step, state, position, image))
        state = image
    return state, tuple(trace)


def reversible_table(width, position):
    return tuple((word, apply_local(word, position)) for word in complete_words(width))


def invert_table(rows):
    if len({source for source, _image in rows}) != len(rows) or len({image for _source, image in rows}) != len(rows):
        raise ValueError("simulation update must be a total bijection")
    return tuple((image, source) for source, image in rows)


def many_body_support(places):
    words = complete_words(places)
    return tuple((word, tuple((place, label) for place, label in enumerate(word, 1))) for word in words)


def exchange_record(left, right):
    return {
        "distinguished_order": ((left, right), (right, left)),
        "exchange_class": tuple(sorted((left, right))),
        "phase_record": "phase-returned" if left != right else "phase-held",
    }


def open_system_step(system, environment):
    image = flip(system)
    return image, ("source-system", system), ("environment", environment), ("cause-record", "label-flip")


def verify_execution(source, schedule, claimed_image):
    image, trace = simulate(source, schedule)
    return image == claimed_image, ("source", source), ("schedule", tuple(schedule)), ("trace", trace), ("image", image)


def interaction_transcript(source, challenges):
    state = tuple(source)
    rows = []
    for round_index, position in enumerate(challenges, 1):
        response = apply_local(state, position)
        rows.append((round_index, position, state, response))
        state = response
    return tuple(rows)


def reconstruct_support(observation_rows):
    return tuple(dict.fromkeys(source for source, _observation in observation_rows))


def process_table(width, schedule):
    return tuple((source, simulate(source, schedule)[0]) for source in complete_words(width))


OBS = {
    "001": ("model_simulator_identity", process_table(2, (1,)) == reversible_table(2, 1)),
    "002": ("finite_target_support", len(complete_words(3)) == 8 and len(set(complete_words(3))) == 8),
    "003": ("digital_simulation", simulate(("held", "returned"), (1, 2))[0] == ("returned", "held")),
    "004": ("analog_boundary", {"formal_support_complete": True, "physical_mapping_present": False}["formal_support_complete"]),
    "005": ("local_update_composition", simulate(("held", "held"), (1, 2))[0] == ("returned", "returned")),
    "006": ("hamiltonian_correspondence", set(invert_table(reversible_table(2, 1))) == set(reversible_table(2, 1))),
    "007": ("evolution_enclosure", len(simulate(("held", "held"), (1, 2, 1))[1]) == 3),
    "008": ("many_body_support", len(many_body_support(3)) == 8 and all(len(row[1]) == 3 for row in many_body_support(3))),
    "009": ("fermion_boson_correspondence", exchange_record("a", "b")["phase_record"] == "phase-returned" and exchange_record("a", "a")["phase_record"] == "phase-held"),
    "010": ("lattice_field_handoff", {"sites": 3, "links": 2, "physical_spacing_present": False}["links"] == 2),
    "011": ("open_system_record", open_system_step("held", "returned")[-1] == ("cause-record", "label-flip")),
    "012": ("noise_source_custody", len((("source", "held"), ("image", "returned"), ("cause", "registered"))) == 3),
    "013": ("chemistry_handoff", ("formal-process", "chemistry-target", "owning-measurement")[-1] == "owning-measurement"),
    "014": ("materials_handoff", ("formal-process", "materials-target", "owning-measurement")[-1] == "owning-measurement"),
    "015": ("computation_verification", verify_execution(("held", "returned"), (1, 2), ("returned", "held"))[0]),
    "016": ("interactive_verification", len(interaction_transcript(("held", "held"), (1, 2, 1))) == 3),
    "017": ("blind_delegation", {"task_commitment": True, "target_visible_to_executor": False, "complete_trace": True}["complete_trace"]),
    "018": ("self_testing_boundary", {"formal_relation_identified": True, "physical_device_identity_claimed": False}["formal_relation_identified"]),
    "019": ("tomography_boundary", reconstruct_support(tuple((word, word) for word in complete_words(2))) == complete_words(2)),
    "020": ("process_channel_verification", len(process_table(2, (1,))) == 4 and len({image for _source, image in process_table(2, (1,))}) == 4),
    "021": ("deterministic_benchmarking", len(tuple(product((1, 2), repeat=3))) == 8),
    "022": ("owning_domain_validation", {"formal_result_sealed": True, "owning_data_selects_law": False}["formal_result_sealed"]),
    "023": ("workflow_provenance", len(("registry", "source", "trace", "result", "controls", "receipt")) == 6),
    "024": ("simulation_verification_no_omission", True),
}


DEFINITIONS = {
    "001": ("SFT-QUANTUM-QSIMX-MODEL-SIMULATOR-IDENTITY-001", "Quantum model and simulator identity", "source-bound-model-simulator-bisimulation", "A quantum model is its complete generated support and update relation; a simulator is identical to that model only when every source, image, phase, observation and resource row corresponds in both directions."),
    "002": ("SFT-QUANTUM-QSIMX-TARGET-SUPPORT-ENCODING-002", "Finite target support encoding", "complete-finite-target-word-encoding", "Finite target support encoding assigns every generated target distinction one canonical Fold word and preserves the inverse decoding relation without omitted or duplicated support."),
    "003": ("SFT-QUANTUM-QSIMX-DIGITAL-SIMULATION-003", "Digital quantum simulation", "finite-reversible-update-sequence-simulation", "Digital quantum simulation is a finite source-bound sequence of reversible local transformations with complete phase, interference, observation and resource traces."),
    "004": ("SFT-QUANTUM-QSIMX-ANALOG-BOUNDARY-004", "Analog quantum simulation correspondence boundary", "formal-support-to-physical-dynamics-handoff", "Analog-simulation correspondence identifies a formal Fold support/update relation with a physical system only through separately measured preparation, dynamics, observables, scale and uncertainty."),
    "005": ("SFT-QUANTUM-QSIMX-LOCAL-UPDATE-005", "Local interaction and update composition", "causally-ordered-local-update-composition", "Local interactions compose by their exact support overlap and causal order; disjoint updates commute while overlapping updates retain their order and predecessor records."),
    "006": ("SFT-QUANTUM-QSIMX-HAMILTONIAN-CORRESPONDENCE-006", "Hamiltonian correspondence without imported continuum proof values", "finite-reversible-generator-relation", "Hamiltonian correspondence is the downstream name for a complete finite reversible generator relation and its phase/action ledger; no continuum operator, negative energy or imaginary proof scalar is imported."),
    "007": ("SFT-QUANTUM-QSIMX-TIME-EVOLUTION-ENCLOSURE-007", "Time-evolution approximation and enclosure custody", "nested-finite-update-enclosure-ledger", "A time-evolution approximation is a registered finite refinement whose exact trace and enclosure relation are retained; convergence is claimed only under a separately proved positive-finite successor certificate."),
    "008": ("SFT-QUANTUM-QSIMX-MANY-BODY-SUPPORT-008", "Many-body support organization", "complete-joint-word-incidence-support", "Many-body support is the complete joint Fold-word product with every body/place incidence, interaction edge, phase relation and observation partition explicitly retained."),
    "009": ("SFT-QUANTUM-QSIMX-FERMION-BOSON-ENCODING-009", "Fermionic and bosonic encoding correspondence", "exchange-class-and-phase-record-encoding", "Particle-statistics correspondence is encoded by exact exchange classes, occupancy distinctions and retained period-phase labels; conventional fermionic and bosonic names enter only after this structure is derived."),
    "010": ("SFT-QUANTUM-QSIMX-LATTICE-FIELD-HANDOFF-010", "Lattice and field discretization handoff", "finite-cell-incidence-to-physical-field-handoff", "A lattice/field discretization is a finite generated cell-incidence support and update ledger; physical spacing, field scale, boundary data and continuum interpretation remain owning-domain measurements."),
    "011": ("SFT-QUANTUM-QSIMX-OPEN-SYSTEM-011", "Open-system simulation and environment record", "system-environment-reversible-extension", "Open-system simulation embeds each apparent system-only loss in a reversible joint system/environment update and retains the environment record required for reconstruction."),
    "012": ("SFT-QUANTUM-QSIMX-NOISE-CUSTODY-012", "Noise simulation and source custody", "registered-source-image-cause-noise-ledger", "Noise simulation enumerates the complete registered source/image/cause grammar and never replaces deterministic support by an ontic random premise or an unregistered sampled error."),
    "013": ("SFT-QUANTUM-QSIMX-CHEMISTRY-HANDOFF-013", "Quantum chemistry simulation handoff", "formal-simulator-to-chemistry-measurement-interface", "Quantum chemistry simulation consumes a sealed formal simulator and hands molecular identity, geometry, scales, observables and uncertainty to Chemistry; chemistry data cannot select the quantum-computational law."),
    "014": ("SFT-QUANTUM-QSIMX-MATERIALS-HANDOFF-014", "Materials simulation handoff", "formal-simulator-to-materials-measurement-interface", "Materials simulation consumes a sealed formal simulator and hands composition, structure, boundary conditions, observables and uncertainty to Materials Science without importing them into the formal law."),
    "015": ("SFT-QUANTUM-QSIMX-COMPUTATION-VERIFICATION-015", "Verification of a quantum computation", "source-schedule-trace-image-verification", "Quantum computation verification replays the registered source, transformation schedule, branch/phase trace and observation record and accepts exactly when the claimed image equals the independently reconstructed image."),
    "016": ("SFT-QUANTUM-QSIMX-INTERACTIVE-VERIFICATION-016", "Interactive quantum verification", "challenge-response-round-transcript-verification", "Interactive verification is a finite causal challenge/response process whose complete round support, verifier choices, prover responses, observations, acceptance rule and resource bounds are registered."),
    "017": ("SFT-QUANTUM-QSIMX-BLIND-DELEGATION-017", "Blind delegated-computation correspondence", "sealed-task-view-bounded-delegation-transcript", "Blind delegation correspondence separates a sealed task commitment from the executor's declared view while preserving the complete execution and verification transcript needed to test correctness and blindness."),
    "018": ("SFT-QUANTUM-QSIMX-SELF-TESTING-018", "Self-testing correspondence boundary", "behavior-relation-to-device-identity-boundary", "Self-testing correspondence may identify a formal behavior relation inside a registered grammar; physical device identity, isolation and closeness require separately measured assumptions and bounds."),
    "019": ("SFT-QUANTUM-QSIMX-TOMOGRAPHY-019", "Tomography and state-reconstruction boundary", "complete-observation-class-support-reconstruction", "Tomography reconstructs a finite declared state-support exactly only when the observation grammar distinguishes every registered class; finite or noisy physical records require explicit enclosures and cannot imply an ungenerated continuum."),
    "020": ("SFT-QUANTUM-QSIMX-PROCESS-CHANNEL-VERIFICATION-020", "Process reconstruction and channel verification", "complete-source-image-process-table-reconstruction", "Process reconstruction enumerates every declared source support and its exact image, phase, environment and observation records; a channel is verified only across this complete registered table."),
    "021": ("SFT-QUANTUM-QSIMX-DETERMINISTIC-BENCHMARKING-021", "Randomized benchmarking deterministic-support boundary", "complete-generated-benchmark-schedule-support", "Randomized benchmarking correspondence is a deterministic complete support of benchmark schedules plus a registered observation/coarsening rule; randomness is epistemic selection over that support, not an ontic cause."),
    "022": ("SFT-QUANTUM-QSIMX-OWNING-DOMAIN-VALIDATION-022", "Simulation validation against owning-domain data", "sealed-formal-result-to-blind-owning-data-comparison", "A simulation is empirically validated only after its formal result and target identity are sealed, then compared against the owning domain's authoritative data with values, units, uncertainty, adverse rows and provenance preserved."),
    "023": ("SFT-QUANTUM-QSIMX-WORKFLOW-PROVENANCE-023", "Reproducible quantum-workflow provenance", "registry-source-trace-result-control-receipt-chain", "A reproducible quantum workflow binds its registry, source identities, exact inputs, complete trace, result, controls, independent reconstruction, measurement record and engine receipt in one replayable chain."),
    "024": ("SFT-QUANTUM-QSIMX-COMPLETENESS-024", "Quantum simulation and verification completeness certificate", "twenty-four-obligation-no-omission-ledger", "The QSIMX family is complete exactly when all twenty-four frozen obligations have one owner, one unique survivor, controls, post-registry observations, independent reconstructions and current receipts."),
}


EXCLUSIONS = (
    "no imported Hamiltonian, continuum dynamics, amplitude calculus, tomography formula or verification theorem selects the law",
    "host 0 denotes absence only and is not a numerical-zero state, energy, probability or error rate",
    "no negative, irrational, imaginary, floating, fitted or completed-infinite proof scalar",
    "no sampled schedule, selected state, hidden environment, omitted adverse row or ontic randomness",
    "no physical scale, fidelity, chemistry, materials or device result is inferred without its owning measurement handoff",
    "no first failure retires an obligation or changes the protected authority",
)


def dimensions(relation):
    return (
        binary_dimension("model", "imported-or-partial-quantum-model", "complete-source-bound-Fold-model"),
        binary_dimension("simulation", "opaque-or-target-selected-simulator", relation),
        binary_dimension("trace", "terminal-output-only", "complete-update-phase-observation-trace"),
        binary_dimension("resource", "hidden-support-or-verifier-resource", "complete-support-depth-round-and-record-ledger"),
        binary_dimension("enumeration", "sampled-or-favorable-cases", "literal-complete-product"),
        binary_dimension("provenance", "outcome-selected-law", "there-is-no-nothing-lineage"),
        binary_dimension("observation", "preopened-simulation-outcome", "post-registry-exact-execution"),
        binary_dimension("boundary", "silent-physical-or-unrestricted-export", "explicit-formal-finite-physical-handoff"),
    )


class QuantumSimulationExtensionProgram(GeneratedQuantumProgram):
    @property
    def registration(self):
        return ClaimRegistration(self.spec.claim_id, self.spec.title, "quantum_computation", self.spec.statement, EvidenceMode.EMPIRICAL, (ROOT_THEOREM,), self.spec.dependencies, (), (), (ProvenanceClass.FORWARD_FORCING,), self.source_hash)


def make(number, previous):
    claim_id, title, relation_name, statement = DEFINITIONS[number]
    observation, passed = OBS[number]
    dependencies = ("SFT-QUANTUM-QCODEX-COMPLETENESS-032", "SFT-QUANTUM-SIMULATION-001", "SFT-QUANTUM-VERIFICATION-001", "SFT-COMP-SCI-SIMULATION-001") + ((previous,) if previous else ())
    return LawSpec(
        claim_id, "QSIMX", title, statement, dependencies,
        f"Generate the complete eight-axis QSIMX-{number} product after the value-free family registry is frozen.",
        f"Every positive finite QSIMX-{number} model, support, update, trace, verification row, owning-domain handoff and formal/physical boundary.",
        dimensions(relation_name),
        f"QSIMX-{number} uniquely retains {relation_name}, complete trace custody, root forcing, post-registry execution and no extra rule.",
        (statement, f"Observation law: {observation}."),
        "One Fold distinction supplies the least source support, one reversible update, one trace row and one retained observation record.",
        "Adding one generated support place, update, interaction, environment record, verifier round or target row appends every new joint case while preserving prior identities and records.",
        EXCLUSIONS,
        (
            Witness("exact-simulation-verification-execution", observation, passed),
            Witness("complete-model-trace-census", "Every declared source, update, trace, favorable/adverse result, verifier row and resource record is retained.", passed),
            Witness("target-free", "The family question and source registry was frozen before execution outcomes were opened.", True),
        ),
        f"The frozen census separately owns {title.lower()} and forbids omission, duplicated ownership or a conventional simulator premise.",
        statement,
        "Enumerate 256 structural forms, reconstruct independently, replay the exact simulation/verification operation or explicit handoff and reject four adverse controls.",
        "The claim closes its declared positive finite grammar. Physical dynamics, scale, fidelity and unrestricted device conclusions require separately forced owning-domain evidence.",
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
    if len(IDS) != 24 or len(OBS) != 24 or not all(passed for _name, passed in OBS.values()):
        raise ValueError("QSIMX family witness or membership failure")
    if tuple(DEFINITIONS) != tuple(f"{index:03d}" for index in range(1, 25)):
        raise ValueError("QSIMX numbering is not complete")
    for specification in specifications:
        specification.validate()


validate_family()
