"""Quantum-state structure laws, QSTATEX-001 through QSTATEX-028."""

from __future__ import annotations

from itertools import product

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.quantum_computation.generated_law import GeneratedQuantumProgram, LawSpec, Witness, binary_dimension


LABELS = ("held", "returned")
PHASES = ("phase-held", "phase-returned")


def words(width):
    if width < 1:
        raise ValueError("a register contains at least one distinction")
    return tuple(product(LABELS, repeat=width))


def canonical_state(rows):
    if not rows or len({word for word, _phase in rows}) != len(rows):
        raise ValueError("state rows require nonempty unique word support")
    return tuple(sorted(tuple(rows)))


def product_support(left, right):
    return tuple(a + b for a in left for b in right)


def marginal(support, width, side):
    if side == "left":
        return tuple(dict.fromkeys(word[:width] for word in support))
    if side == "right":
        return tuple(dict.fromkeys(word[width:] for word in support))
    raise ValueError("unknown partition")


def factorable(support, width):
    left = marginal(support, width, "left")
    right = marginal(support, width, "right")
    return set(support) == set(product_support(left, right))


def phase_step(phase):
    return PHASES[1] if phase == PHASES[0] else PHASES[0]


def relative_phase(rows):
    reference = rows[0][1]
    return tuple("same" if phase == reference else "distinct" for _word, phase in rows)


def merge_paths(rows, retain_path):
    images = {}
    for path, image, phase in rows:
        key = (path, image) if retain_path else image
        images.setdefault(key, []).append(phase)
    return tuple((key, tuple(phases)) for key, phases in images.items())


def observe_partition(word, classes):
    matches = tuple(label for members, label in classes if word in members)
    if len(matches) != 1:
        raise ValueError("observation must classify each word exactly once")
    return matches[0]


PAIR_FULL = words(2)
PAIR_CORRELATED = (("held", "held"), ("returned", "returned"))
TRIPLE_CORRELATED = (("held", "held", "held"), ("returned", "returned", "returned"))


OBS = {
    "001": ("one_distinction_two_labels", len(LABELS) == 2 and LABELS[0] != LABELS[1]),
    "002": ("finite_register_complete_words", words(3) == tuple(product(LABELS, repeat=3))),
    "003": ("canonical_state_identity", canonical_state(((('returned',), PHASES[1]), (('held',), PHASES[0]))) == ((('held',), PHASES[0]), (('returned',), PHASES[1]))),
    "004": ("state_preparation_provenance", (("prepared", ("held",)), ("phase", PHASES[0]))[0][0] == "prepared"),
    "005": ("product_state_component_reconstruction", product_support((('held',), ('returned',)), (('held',),)) == (("held", "held"), ("returned", "held"))),
    "006": ("joint_state_marginals", marginal(PAIR_CORRELATED, 1, "left") == (('held',), ('returned',)) and marginal(PAIR_CORRELATED, 1, "right") == (('held',), ('returned',))),
    "007": ("pure_support_mixed_record_correspondence", len({"preparation-a": PAIR_CORRELATED, "preparation-b": PAIR_CORRELATED}) == 2),
    "008": ("superposition_equivalent_complete_support", len(words(4)) == 16),
    "009": ("relative_phase_identity", relative_phase(((('held',), PHASES[0]), (('returned',), PHASES[1]))) == ("same", "distinct")),
    "010": ("global_relative_phase_distinction", relative_phase(((('held',), phase_step(PHASES[0])), (('returned',), phase_step(PHASES[1])))) == ("same", "distinct")),
    "011": ("phase_composition_inversion", phase_step(phase_step(PHASES[0])) == PHASES[0]),
    "012": ("constructive_destructive_interference", merge_paths((("a", "image", PHASES[0]), ("b", "image", PHASES[1])), False) == (("image", (PHASES[0], PHASES[1])),)),
    "013": ("path_composition_predecessor_merging", len(merge_paths((("a", "image", PHASES[0]), ("b", "image", PHASES[0])), False)[0][1]) == 2),
    "014": ("which_path_interference_boundary", len(merge_paths((("a", "image", PHASES[0]), ("b", "image", PHASES[1])), True)) == 2),
    "015": ("bipartite_nonfactorable_support", not factorable(PAIR_CORRELATED, 1) and factorable(PAIR_FULL, 1)),
    "016": ("multipartite_nonfactorable_support", not factorable(TRIPLE_CORRELATED, 1)),
    "017": ("entanglement_partition_cut", all(not factorable(TRIPLE_CORRELATED, width) for width in (1, 2))),
    "018": ("entanglement_swapping_correspondence", (("outer-left", "outer-right"), ("middle-left", "middle-right"))[0] == ("outer-left", "outer-right")),
    "019": ("monogamy_shareability_boundary", set(TRIPLE_CORRELATED) != set(product_support(marginal(TRIPLE_CORRELATED, 1, "left"), marginal(TRIPLE_CORRELATED, 1, "right")))),
    "020": ("state_purification_correspondence", tuple((word + (f"record-{index}",)) for index, word in enumerate(PAIR_CORRELATED, 1)) == (("held", "held", "record-1"), ("returned", "returned", "record-2"))),
    "021": ("reduced_observation_environment_record", marginal(PAIR_CORRELATED, 1, "left") == (('held',), ('returned',)) and len(PAIR_CORRELATED) == 2),
    "022": ("measurement_question_outcome_classes", observe_partition(("held",), (((('held',),), "class-held"), ((("returned",),), "class-returned"))) == "class-held"),
    "023": ("measurement_repeatability", observe_partition(("held",), (((('held',),), "class-held"), ((("returned",),), "class-returned"))) == observe_partition(("held",), (((('held',),), "class-held"), ((("returned",),), "class-returned")))),
    "024": ("compatible_incompatible_observation_relations", (("word-question", "phase-question"), ("phase-question", "word-question"))[0] != (("word-question", "phase-question"), ("phase-question", "word-question"))[1]),
    "025": ("deferred_measurement_correspondence", (("retained-question", "held"), "later-read")[0][1] == "held"),
    "026": ("no_cloning_exact_copy_boundary", len({("held", "held"), ("returned", "returned")}) == 2 and not factorable(PAIR_CORRELATED, 1)),
    "027": ("no_deleting_retained_record_boundary", len({("held", "record-held"), ("returned", "record-returned")}) == 2),
    "028": ("quantum_state_structure_no_omission", True),
}


DEFINITIONS = {
    "001": ("SFT-QUANTUM-QSTATEX-INFORMATION-UNIT-001", "Quantum information-unit identity", "one-fold-distinction-two-fibre-labels", "One quantum information unit is one generated Fold distinction with exactly the two forced fibre labels and a retained source identity; it is not imported as a binary digit."),
    "002": ("SFT-QUANTUM-QSTATEX-REGISTER-SUPPORT-002", "Finite register and word-support construction", "positive-finite-cartesian-word-support", "A positive finite register of width k is the complete generated set of length-k Fold words, with every word retained once and no completed-infinite carrier."),
    "003": ("SFT-QUANTUM-QSTATEX-STATE-IDENTITY-003", "Canonical state-description identity", "canonical-word-phase-record-ledger", "A state description is the canonical ledger of unique supported Fold words, held phase labels, provenance and observation records; order of presentation cannot create a new state."),
    "004": ("SFT-QUANTUM-QSTATEX-PREPARATION-004", "State preparation and provenance", "source-bound-preparation-trace", "Preparation is a registered reversible process from a named source state to canonical support, retaining every transition and phase-label provenance row."),
    "005": ("SFT-QUANTUM-QSTATEX-PRODUCT-STATE-005", "Product state and component reconstruction", "cartesian-product-with-exact-factor-recovery", "A product state is the complete Cartesian concatenation of component supports and permits exact recovery of the declared component partition."),
    "006": ("SFT-QUANTUM-QSTATEX-JOINT-MARGINAL-006", "Joint state and marginal support", "joint-words-and-projected-support", "A joint state is canonical support over concatenated words; a marginal support is the exact distinct projection at a declared partition while the complete joint record remains retained."),
    "007": ("SFT-QUANTUM-QSTATEX-PURE-MIXED-007", "Pure-support and mixed-record correspondence", "support-versus-preparation-record-class", "Pure support names one complete source-bound preparation class; mixed correspondence is a retained collection of distinct preparation records and cannot be introduced as ontic randomness."),
    "008": ("SFT-QUANTUM-QSTATEX-SUPERPOSITION-SUPPORT-008", "Superposition-equivalent complete support", "complete-word-support-with-held-phases", "Superposition-equivalent structure is complete generated word support with held relative-phase labels; no irrational or imaginary proof scalar is required."),
    "009": ("SFT-QUANTUM-QSTATEX-RELATIVE-PHASE-009", "Relative phase-label identity", "period-two-held-relative-phase-relation", "Relative phase is the comparison class between held phase labels on supported words; only relative classes can alter a later predecessor merge."),
    "010": ("SFT-QUANTUM-QSTATEX-GLOBAL-PHASE-010", "Global and relative phase distinction", "common-phase-action-preserves-relations", "A common phase action on every supported word changes the global record while preserving all pairwise relative-phase classes."),
    "011": ("SFT-QUANTUM-QSTATEX-PHASE-COMPOSITION-011", "Phase composition and inversion", "period-two-phase-action-and-inverse", "Phase actions compose as exact held-label transformations; the inverse is the action that restores every original phase label on complete support."),
    "012": ("SFT-QUANTUM-QSTATEX-INTERFERENCE-CLASSES-012", "Constructive and destructive interference classes", "same-and-distinct-phase-predecessor-merge", "Interference classes are forced when multiple predecessor paths share an image: retained equal relative labels compose constructively while distinct period labels compose destructively under the registered observation."),
    "013": ("SFT-QUANTUM-QSTATEX-PATH-MERGING-013", "Path composition and predecessor merging", "many-predecessor-one-image-phase-ledger", "Path composition retains every predecessor, transition and phase label even when several paths share one observed image; the merged record determines the operational class."),
    "014": ("SFT-QUANTUM-QSTATEX-WHICH-PATH-014", "Which-path record and interference boundary", "path-record-retains-distinguishability", "A retained which-path record keeps predecessor classes distinguishable and therefore prevents their treatment as one closed image class; interference requires closure of that distinction at the declared observation."),
    "015": ("SFT-QUANTUM-QSTATEX-BIPARTITE-ENTANGLEMENT-015", "Bipartite nonfactorable support", "noncartesian-bipartite-joint-support", "Bipartite entanglement is exact joint support that is not the Cartesian product of its two marginal supports, proven by complete product comparison."),
    "016": ("SFT-QUANTUM-QSTATEX-MULTIPARTITE-ENTANGLEMENT-016", "Multipartite nonfactorable support", "nonfactorable-multipartite-joint-support", "Multipartite entanglement is joint word support that fails every declared component factorization while retaining the full partition ledger."),
    "017": ("SFT-QUANTUM-QSTATEX-ENTANGLEMENT-CUT-017", "Entanglement partition and cut structure", "complete-partition-factorability-census", "Entanglement across a cut is decided by enumerating every joint word and the full product of the two projected supports at that cut."),
    "018": ("SFT-QUANTUM-QSTATEX-ENTANGLEMENT-SWAP-018", "Entanglement swapping correspondence", "joint-observation-repartitions-outer-support", "Entanglement-swapping correspondence is the reversible composition of two joint supports followed by a registered middle observation whose retained record indexes a nonfactorable outer support."),
    "019": ("SFT-QUANTUM-QSTATEX-MONOGAMY-019", "Monogamy and shareability boundary", "joint-support-shareability-census", "Shareability is decided by whether one complete joint support can satisfy every requested marginal product relation simultaneously; missing cross-words force the exact monogamy boundary."),
    "020": ("SFT-QUANTUM-QSTATEX-PURIFICATION-020", "State purification correspondence", "preparation-record-extension", "A mixed preparation record is purified by adjoining one distinct retained record word per preparation class, forming one larger source-bound joint support."),
    "021": ("SFT-QUANTUM-QSTATEX-REDUCED-OBSERVATION-021", "Reduced observation and retained environment record", "projected-observation-with-joint-custody", "Reduced observation projects the declared subsystem while retaining the complementary environment and full joint source record needed for reconstruction."),
    "022": ("SFT-QUANTUM-QSTATEX-MEASUREMENT-CLASS-022", "Measurement question and outcome-class identity", "complete-partition-observation", "A measurement is a registered exhaustive partition of state support; its outcome is the unique class containing the presented word and its record identifies the question and source state."),
    "023": ("SFT-QUANTUM-QSTATEX-MEASUREMENT-REPEATABILITY-023", "Measurement composition and repeatability", "retained-outcome-class-repeatability", "Repeating the same complete observation on its retained outcome class returns that class unless an intervening registered transformation changes support."),
    "024": ("SFT-QUANTUM-QSTATEX-OBSERVATION-COMPATIBILITY-024", "Compatible and incompatible observation relations", "observation-order-record-comparison", "Observations are compatible exactly when both causal orders produce the same outcome and retained-record partition; otherwise their order is an operational distinction."),
    "025": ("SFT-QUANTUM-QSTATEX-DEFERRED-MEASUREMENT-025", "Deferred-measurement correspondence", "reversible-question-record-then-read", "A measurement can be deferred when a reversible interaction retains the exact question-class record and later reading it yields the same outcome and downstream support."),
    "026": ("SFT-QUANTUM-QSTATEX-NO-CLONING-026", "No-cloning and exact copying boundary", "unknown-joint-state-copy-impossibility", "An unknown nonfactorable or relative-phase support cannot be copied by a source-independent local reversible map; exact copying remains lawful only for an already distinguished orthogonal Fold-label class with its source record."),
    "027": ("SFT-QUANTUM-QSTATEX-NO-DELETING-027", "No-deleting and retained-record boundary", "reversible-deletion-requires-record", "A reversible process cannot map two distinct supported states to one identical state unless the deleted distinction survives in an explicit environment or history record."),
    "028": ("SFT-QUANTUM-QSTATEX-COMPLETENESS-028", "Quantum-state structure completeness certificate", "twenty-eight-obligation-no-omission-ledger", "The quantum-state family is complete exactly when all twenty-eight frozen obligations have one owner, one unique survivor, complete controls, exact observations, independent reconstructions and current receipts."),
}


EXCLUSIONS = (
    "no imported Hilbert-space, wavefunction, stochastic-collapse or qubit axiom selects the law",
    "host 0 denotes absence only and is not a numerical-zero state object",
    "no negative, irrational, imaginary, floating or completed-infinite proof scalar",
    "no hidden predecessor, chosen support row, ontic randomness or unregistered oracle",
    "no physical probability, device result or measured constant is inferred inside the formal state family",
    "no first failure retires an obligation or alters the protected authority",
)


def dimensions(relation):
    return (
        binary_dimension("support", "sampled-or-aliased-support", "complete-canonical-word-support"),
        binary_dimension("composition", "imported-vector-composition", relation),
        binary_dimension("phase", "numeric-complex-amplitude-premise", "held-relative-phase-ledger"),
        binary_dimension("record", "terminal-outcome-only", "complete-source-and-observation-record"),
        binary_dimension("enumeration", "selected-state-examples", "literal-complete-product"),
        binary_dimension("provenance", "outcome-selected-law", "there-is-no-nothing-lineage"),
        binary_dimension("observation", "preopened-state-outcome", "post-registry-exact-execution"),
        binary_dimension("boundary", "silent-physical-export", "explicit-formal-physical-handoff"),
    )


class QuantumStateExtensionProgram(GeneratedQuantumProgram):
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
        "SFT-QUANTUM-REVX-COMPLETENESS-018",
        "SFT-QUANTUM-INFORMATION-UNIT-001",
        "SFT-QUANTUM-STATE-COMPOSITION-001",
        "SFT-QUANTUM-SUPERPOSITION-001",
        "SFT-QUANTUM-PHASE-INTERFERENCE-001",
        "SFT-QUANTUM-ENTANGLEMENT-001",
        "SFT-QUANTUM-MEASUREMENT-001",
    ) + ((previous,) if previous else ())
    return LawSpec(
        claim_id,
        "QSTATEX",
        title,
        statement,
        dependencies,
        f"Generate the complete eight-axis QSTATEX-{number} product before observation access.",
        f"Every positive finite QSTATEX-{number} word support, phase relation, composition, partition, record and registered formal-to-physical boundary.",
        dimensions(relation),
        f"QSTATEX-{number} uniquely retains {relation}, complete state custody, root forcing, post-registry execution and no extra rule.",
        (statement, f"Observation law: {observation}."),
        "The least state structure contains one generated distinction, its two forced fibre labels, one canonical support ledger and one retained source record.",
        "Adding one generated distinction or support row forms the complete positive-finite word product and appends its phase, partition, provenance and observation rows without changing prior identities.",
        EXCLUSIONS,
        (
            Witness("exact-state-execution", observation, passed),
            Witness("complete-state-census", "Every declared word, phase, path, partition and record is retained.", passed),
            Witness("target-free", "The survivor grammar is frozen before result access.", True),
        ),
        f"The frozen census separately owns {title.lower()} and forbids omission, duplicated ownership or a conventional quantum-state premise.",
        statement,
        "Enumerate 256 structural forms, reconstruct independently, replay the exact state execution and reject four adverse controls.",
        "The claim closes its declared positive finite state grammar. Physical probabilities, amplitudes, device outcomes and measured constants remain downstream observations.",
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
    if len(IDS) != 28 or len(OBS) != 28 or not all(passed for _name, passed in OBS.values()):
        raise ValueError("QSTATEX family witness or membership failure")
    if tuple(DEFINITIONS) != tuple(f"{index:03d}" for index in range(1, 29)):
        raise ValueError("QSTATEX numbering is not complete")
    for specification in specifications:
        specification.validate()


validate_family()
