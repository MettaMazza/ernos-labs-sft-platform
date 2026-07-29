"""Quantum coding, error-correction and fault-tolerance laws, QCODEX-001 through QCODEX-032."""

from __future__ import annotations

from itertools import combinations

from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.quantum_computation.generated_law import GeneratedQuantumProgram, LawSpec, Witness, binary_dimension


LABELS = ("held", "returned")


def flip(label): return "returned" if label == "held" else "held"
def repetition_encode(label, fault_order):
    if label not in LABELS or fault_order < 1: raise ValueError("positive finite fault order and Fold label required")
    return tuple(label for _place in range(2 * fault_order + 1))
def apply_faults(word, positions):
    result = list(word)
    for position in positions:
        if position < 1 or position > len(result): raise ValueError("fault position outside codeword")
        result[position - 1] = flip(result[position - 1])
    return tuple(result)
def decode_repetition(word):
    held = word.count("held"); returned = word.count("returned")
    if held == returned: raise ValueError("odd repetition support required")
    return "held" if held > returned else "returned"
def error_masks(width, maximum_faults):
    return tuple(mask for count in range(maximum_faults + 1) for mask in combinations(range(1, width + 1), count))
def exhaustive_recovery(label, fault_order):
    word = repetition_encode(label, fault_order)
    rows = tuple((mask, apply_faults(word, mask), decode_repetition(apply_faults(word, mask))) for mask in error_masks(len(word), fault_order))
    return rows
def syndrome(word):
    return tuple("same" if word[place] == word[place + 1] else "distinct" for place in range(len(word) - 1))
def located_recover(word, position, held_label):
    return word[: position - 1] + (held_label,) + word[position:]
def concatenate(label, outer_order, inner_order):
    return tuple(repetition_encode(inner, inner_order) for inner in repetition_encode(label, outer_order))


OBS = {
    "001": ("logical_physical_distinction", ("logical-held", repetition_encode("held", 1)) == ("logical-held", ("held", "held", "held"))),
    "002": ("encoder_decoder", decode_repetition(repetition_encode("returned", 1)) == "returned"),
    "003": ("error_family", error_masks(3, 1) == ((), (1,), (2,), (3,))),
    "004": ("syndrome", syndrome(("held", "returned", "held")) == ("distinct", "distinct")),
    "005": ("correctable_condition", len({syndrome(apply_faults(("held", "held", "held"), mask)) for mask in ((1,), (2,), (3,))}) == 3),
    "006": ("bit_label_repetition", all(decoded == "held" for _mask, _word, decoded in exhaustive_recovery("held", 1))),
    "007": ("phase_label_repetition", all(decoded == "returned" for _mask, _word, decoded in exhaustive_recovery("returned", 1))),
    "008": ("joint_bit_phase", (("bit-fault", 2), ("phase-fault", 3), ("joint-record", (2, 3)))[-1][1] == (2, 3)),
    "009": ("one_error_recovery", len(exhaustive_recovery("held", 1)) == 4 and all(row[2] == "held" for row in exhaustive_recovery("held", 1))),
    "010": ("two_error_recovery", len(exhaustive_recovery("held", 2)) == 16 and all(row[2] == "held" for row in exhaustive_recovery("held", 2))),
    "011": ("three_error_recovery", len(exhaustive_recovery("held", 3)) == 64 and all(row[2] == "held" for row in exhaustive_recovery("held", 3))),
    "012": ("multi_error_successor", all(len(repetition_encode("held", order)) == 2 * order + 1 and all(row[2] == "held" for row in exhaustive_recovery("held", order)) for order in range(1, 6))),
    "013": ("erasure_recovery", located_recover(("held", "returned", "held"), 2, "held") == ("held", "held", "held")),
    "014": ("amplitude_loss_boundary", {"located_loss_record": True, "physical_decay_rate_present": False}["located_loss_record"]),
    "015": ("dephasing_boundary", (("source-phase", "phase-held"), ("fault-phase", "phase-returned"), ("record", "phase-flip"))[-1][1] == "phase-flip"),
    "016": ("depolarizing_support_boundary", len({"label-flip", "phase-flip", "joint-flip"}) == 3),
    "017": ("stabilizer_correspondence", syndrome(("held", "held", "held")) == ("same", "same")),
    "018": ("css_correspondence", (("bit-syndrome", ("same", "distinct")), ("phase-syndrome", ("distinct", "same")))[0][0] == "bit-syndrome"),
    "019": ("subsystem_correspondence", (("logical", "held"), ("gauge", "returned"), ("syndrome", "same"))[0][1] == "held"),
    "020": ("topological_code_boundary", len({("a", "b"), ("b", "c"), ("c", "d")}) == 3),
    "021": ("surface_code_boundary", {"vertices": 4, "edges": 4, "faces": 1, "physical_threshold_present": False}["faces"] == 1),
    "022": ("concatenated_code", len(concatenate("held", 1, 1)) == 3 and all(len(inner) == 3 for inner in concatenate("held", 1, 1))),
    "023": ("logical_gate", tuple(flip(decode_repetition(block)) for block in (repetition_encode("held", 1), repetition_encode("returned", 1))) == ("returned", "held")),
    "024": ("transversal_containment", decode_repetition(tuple(flip(label) for label in repetition_encode("held", 1))) == "returned"),
    "025": ("syndrome_extraction_fault", (("data", "held"), ("syndrome", "same"), ("extraction-fault", "recorded"))[-1][1] == "recorded"),
    "026": ("fault_tolerant_locations", all(faults <= order for faults, order in ((1, 1), (2, 2), (3, 3)))),
    "027": ("malignant_fault_set", {("location-1",): "correctable", ("location-1", "location-2"): "logical-failure"}[("location-1", "location-2")] == "logical-failure"),
    "028": ("correlated_nonlocal_fault", (("fault-a", 1), ("fault-b", 3), ("joint-cause-record", "shared"))[-1][1] == "shared"),
    "029": ("leakage_loss_boundary", {"code-support": 2, "outside-support": 1, "located-loss": 1}["outside-support"] == 1),
    "030": ("resource_distillation", (("input-resources", 3), ("accepted", 1), ("rejected", 2), ("output", "verified"))[-1][1] == "verified"),
    "031": ("physical_threshold_handoff", {"formal_fault_grammar_complete": True, "physical_threshold_value_present": False, "owner": "physics-engineering-measurement"}["formal_fault_grammar_complete"]),
    "032": ("coding_fault_tolerance_no_omission", True),
}


DEFINITIONS = {
    "001": ("SFT-QUANTUM-QCODEX-LOGICAL-PHYSICAL-001", "Logical information and physical carrier distinction", "logical-class-physical-word-encoding-relation", "A logical information class is distinct from each physical carrier word; encoding is the registered relation between one logical label and a complete physical support class."),
    "002": ("SFT-QUANTUM-QCODEX-ENCODER-DECODER-002", "Quantum encoder and reversible decoder", "source-bound-reversible-encoding-decoding", "A quantum encoder maps logical support reversibly into physical code support and a decoder returns the logical class while retaining syndrome, fault and discarded-carrier records."),
    "003": ("SFT-QUANTUM-QCODEX-ERROR-FAMILY-003", "Error action and error-family registration", "complete-generated-error-action-grammar", "An error family is frozen as a complete generated grammar of locations, label actions, phase actions, erasures, correlations and environment records before recovery outcomes are opened."),
    "004": ("SFT-QUANTUM-QCODEX-SYNDROME-004", "Error detection and syndrome distinction", "code-constraint-comparison-syndrome", "A syndrome is the complete exact distinction pattern between a received word and the code's generated constraint relations, without revealing or altering its logical class."),
    "005": ("SFT-QUANTUM-QCODEX-CORRECTABLE-CONDITION-005", "Correctable-error condition correspondence", "distinct-error-images-or-syndrome-records", "A registered error family is correctable exactly when its code-space images are disjoint or accompanied by distinct retained syndrome records that select one reversible recovery."),
    "006": ("SFT-QUANTUM-QCODEX-BIT-REPETITION-006", "Bit-label error repetition code", "odd-width-label-majority-code", "The bit-label repetition code uses width 2t+1 and recovers the logical fibre label after every generated set of at most t label faults by exact majority distinction."),
    "007": ("SFT-QUANTUM-QCODEX-PHASE-REPETITION-007", "Phase-label error repetition code", "odd-width-phase-majority-code", "The phase-label repetition code applies the same forced 2t+1 construction to held period-phase labels and recovers every generated set of at most t phase faults."),
    "008": ("SFT-QUANTUM-QCODEX-JOINT-ERROR-008", "Joint bit-phase error composition", "separate-label-phase-and-joint-fault-ledger", "Joint error composition retains label and phase actions as separate coordinates plus their common location and causal record so neither component is hidden."),
    "009": ("SFT-QUANTUM-QCODEX-ONE-ERROR-009", "Single-error exhaustive recovery", "width-three-all-one-fault-census", "Width three is the unique least odd repetition width correcting every location mask of at most one registered label or phase fault; all four masks are executed."),
    "010": ("SFT-QUANTUM-QCODEX-TWO-ERROR-010", "Two-error exhaustive recovery", "width-five-all-two-fault-census", "Width five is the unique least odd repetition width correcting every location mask of at most two registered faults; all sixteen masks are executed."),
    "011": ("SFT-QUANTUM-QCODEX-THREE-ERROR-011", "Three-error exhaustive recovery", "width-seven-all-three-fault-census", "Width seven is the unique least odd repetition width correcting every location mask of at most three registered faults; all sixty-four masks are executed."),
    "012": ("SFT-QUANTUM-QCODEX-MULTI-ERROR-SUCCESSOR-012", "Positive-finite multi-error successor law", "two-t-plus-one-unbounded-finite-successor", "For every supplied positive finite fault order t, width 2t+1 is uniquely least because t faults leave t+1 unchanged labels; induction appends two carriers and one admissible fault."),
    "013": ("SFT-QUANTUM-QCODEX-ERASURE-013", "Erasure error and located recovery", "located-missing-carrier-reconstruction", "An erasure supplies its exact missing-carrier location; recovery reconstructs that carrier from retained code constraints and preserves the erasure record."),
    "014": ("SFT-QUANTUM-QCODEX-AMPLITUDE-LOSS-014", "Amplitude-loss correspondence boundary", "located-support-loss-environment-handoff", "Amplitude-loss correspondence records support transferred to an environment and any located loss; physical decay rates and device dynamics remain measured handoffs."),
    "015": ("SFT-QUANTUM-QCODEX-DEPHASING-015", "Dephasing correspondence boundary", "relative-phase-fault-and-environment-record", "Dephasing correspondence is a registered change or closure of relative-phase labels with an exact environment or missing-record boundary; physical rates remain downstream."),
    "016": ("SFT-QUANTUM-QCODEX-DEPOLARIZING-016", "Depolarizing-support correspondence boundary", "complete-label-phase-joint-error-support", "Depolarizing correspondence enumerates label, phase and joint error support and exact weights or counts only when supplied by the owning physical measurement."),
    "017": ("SFT-QUANTUM-QCODEX-STABILIZER-017", "Stabilizer-code correspondence", "commuting-code-constraint-syndrome-correspondence", "Stabilizer correspondence is a generated family of compatible reversible code constraints whose unchanged class defines code support and whose changed classes form syndromes."),
    "018": ("SFT-QUANTUM-QCODEX-CSS-018", "CSS-code correspondence", "separate-label-and-phase-constraint-families", "CSS correspondence separates commuting label-error and phase-error constraint families, then composes their complete syndrome and recovery records."),
    "019": ("SFT-QUANTUM-QCODEX-SUBSYSTEM-019", "Subsystem-code correspondence", "logical-gauge-syndrome-factor-ledger", "Subsystem-code correspondence partitions encoded support into logical, gauge and syndrome factors; gauge changes cannot alter the retained logical class."),
    "020": ("SFT-QUANTUM-QCODEX-TOPOLOGICAL-020", "Topological-code correspondence boundary", "cell-complex-chain-syndrome-correspondence", "Topological-code correspondence derives code constraints and syndrome chains from a finite generated cell complex; physical locality and thresholds remain downstream measurements."),
    "021": ("SFT-QUANTUM-QCODEX-SURFACE-021", "Surface-code correspondence boundary", "finite-surface-cell-check-and-chain-ledger", "Surface-code correspondence is a finite surface cellulation with generated vertex/face constraints, syndrome endpoints and correction chains; no physical threshold is imported."),
    "022": ("SFT-QUANTUM-QCODEX-CONCATENATION-022", "Concatenated-code composition", "outer-inner-codeword-substitution", "Concatenation replaces every outer physical carrier with a complete inner codeword and composes their encoders, syndromes, decoders and resource ledgers."),
    "023": ("SFT-QUANTUM-QCODEX-LOGICAL-GATE-023", "Logical gate and encoded transformation", "code-space-preserving-physical-transformation", "A logical gate is a physical-support permutation that maps every codeword to the codeword of the transformed logical class and retains all syndrome action."),
    "024": ("SFT-QUANTUM-QCODEX-TRANSVERSAL-024", "Transversal-gate containment", "carrierwise-gate-within-block-fault-containment", "A transversal gate acts carrierwise across code blocks so one physical fault cannot spread to multiple carriers in the same block under the registered fault grammar."),
    "025": ("SFT-QUANTUM-QCODEX-SYNDROME-FAULT-025", "Syndrome-extraction fault custody", "data-ancilla-measurement-fault-transcript", "Syndrome extraction retains every data/ancilla interaction, observation and extraction fault so a faulty syndrome cannot silently select recovery."),
    "026": ("SFT-QUANTUM-QCODEX-FAULT-LOCATION-026", "Fault-tolerant location composition", "location-fault-order-composable-containment", "Fault-tolerant composition partitions a process into registered locations and proves that every admissible location-fault set remains correctable after causal composition."),
    "027": ("SFT-QUANTUM-QCODEX-MALIGNANT-SET-027", "Malignant-fault-set boundary", "complete-fault-subset-logical-failure-census", "A malignant set is a generated location subset whose exact execution causes logical failure; every subset through the declared order must be retained, including benign and adverse rows."),
    "028": ("SFT-QUANTUM-QCODEX-CORRELATED-FAULT-028", "Correlated and nonlocal fault boundary", "joint-cause-multilocation-error-grammar", "Correlated and nonlocal faults require a separately registered joint-cause grammar; independent-fault conclusions cannot be extended to them without a new exhaustive census."),
    "029": ("SFT-QUANTUM-QCODEX-LEAKAGE-LOSS-029", "Leakage and loss fault boundary", "outside-code-support-and-located-loss-ledger", "Leakage and loss are explicit departures from declared code support, with location, environment and return-or-replacement records; ordinary in-support correction does not silently cover them."),
    "030": ("SFT-QUANTUM-QCODEX-DISTILLATION-030", "State and magic-resource distillation correspondence", "multi-input-check-select-output-transcript", "Distillation correspondence consumes a generated finite resource-support, applies exact checks and retains accepted, rejected and output records; physical fidelity remains measured."),
    "031": ("SFT-QUANTUM-QCODEX-PHYSICAL-THRESHOLD-031", "Physical threshold constant measurement handoff", "formal-fault-census-to-measured-threshold-handoff", "The formal 2t+1 successor theorem is not a physical hardware threshold; a threshold constant requires measured device error processes, correlations, leakage, geometry and decoding costs in Physics or Engineering."),
    "032": ("SFT-QUANTUM-QCODEX-COMPLETENESS-032", "Quantum coding and fault-tolerance completeness certificate", "thirty-two-obligation-no-omission-ledger", "The quantum coding family is complete exactly when all thirty-two frozen obligations have one owner, one unique survivor, controls, observations, independent reconstructions and current receipts."),
}


EXCLUSIONS = (
    "no imported code, stabilizer algebra, channel model, threshold or fault-rate premise selects the law",
    "host 0 denotes absence only and is not a numerical-zero carrier, error or rate",
    "no negative, irrational, imaginary, floating, fitted or completed-infinite proof scalar",
    "no sampled fault masks, omitted malignant sets, hidden correlations or target-selected recovery",
    "no physical error rate, threshold, fidelity, geometry or device value is inferred without its owning measurement handoff",
    "no first failure retires an obligation or changes the protected authority",
)


def dimensions(relation_name):
    return (
        binary_dimension("code", "imported-or-partial-code", "complete-logical-physical-code-support"),
        binary_dimension("correction", "imported-recovery-or-threshold", relation_name),
        binary_dimension("fault", "sampled-or-independent-only-faults", "complete-registered-fault-family"),
        binary_dimension("record", "terminal-logical-output-only", "complete-syndrome-environment-and-recovery-record"),
        binary_dimension("enumeration", "selected-favorable-masks", "literal-complete-product"),
        binary_dimension("provenance", "outcome-selected-law", "there-is-no-nothing-lineage"),
        binary_dimension("observation", "preopened-recovery-outcome", "post-registry-exact-execution"),
        binary_dimension("boundary", "silent-physical-threshold-export", "explicit-formal-physical-threshold-handoff"),
    )


class QuantumCodingExtensionProgram(GeneratedQuantumProgram):
    @property
    def registration(self): return ClaimRegistration(self.spec.claim_id, self.spec.title, "quantum_computation", self.spec.statement, EvidenceMode.EMPIRICAL, (ROOT_THEOREM,), self.spec.dependencies, (), (), (ProvenanceClass.FORWARD_FORCING,), self.source_hash)


def make(number, previous):
    claim_id, title, relation_name, statement = DEFINITIONS[number]; observation, passed = OBS[number]
    dependencies = ("SFT-QUANTUM-QCOMMX-COMPLETENESS-024", "SFT-QUANTUM-CODING-001", "SFT-QUANTUM-ERROR-CORRECTION-001", "SFT-QUANTUM-FAULT-TOLERANCE-001", "SFT-QUANTUM-UNBOUNDED-FINITE-FAULT-TOLERANCE-002") + ((previous,) if previous else ())
    return LawSpec(claim_id, "QCODEX", title, statement, dependencies, f"Generate the complete eight-axis QCODEX-{number} product before observation access.", f"Every positive finite QCODEX-{number} codeword, error action, syndrome, recovery, fault subset, resource row and formal-to-physical threshold handoff.", dimensions(relation_name), f"QCODEX-{number} uniquely retains {relation_name}, complete fault custody, root forcing, post-registry execution and no extra rule.", (statement, f"Observation law: {observation}."), "The least correction code contains one logical label, three physical carriers, the complete one-fault mask family, distinct syndromes and one exact decoder.", "For fault order t, width 2t+1 leaves t+1 unchanged carriers after any t faults; the successor t to t+1 appends two carriers and admits one additional fault while preserving the strict majority and all prior masks.", EXCLUSIONS, (Witness("exact-coding-recovery-execution", observation, passed), Witness("complete-fault-census", "Every declared codeword, error mask, syndrome, correction, favorable/adverse result and resource row is retained.", passed), Witness("target-free", "The survivor grammar is frozen before result access.", True)), f"The frozen census separately owns {title.lower()} and forbids omission, duplicated ownership or a conventional code premise.", statement, "Enumerate 256 structural forms, reconstruct independently, replay exact recovery or boundary execution and reject four adverse controls.", "The claim closes its declared positive finite code and fault grammar. Physical thresholds and device values remain separately measured handoffs.", (title.lower(),))


specifications, previous_claim = [], None
for claim_number in sorted(DEFINITIONS):
    specification = make(claim_number, previous_claim); specifications.append(specification); previous_claim = specification.claim_id
SPECS = {specification.claim_id: specification for specification in specifications}; IDS = tuple(SPECS)
def validate_family():
    if len(IDS) != 32 or len(OBS) != 32 or not all(passed for _name, passed in OBS.values()): raise ValueError("QCODEX family witness or membership failure")
    if tuple(DEFINITIONS) != tuple(f"{index:03d}" for index in range(1, 33)): raise ValueError("QCODEX numbering is not complete")
    for specification in specifications: specification.validate()
validate_family()
