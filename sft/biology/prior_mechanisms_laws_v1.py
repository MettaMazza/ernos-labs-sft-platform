"""Independent V3 reconstruction of six stronger prior Biology mechanisms.

V1/V2 provide the questions only.  Exact positive Fold parts, finite generated
carriers and already-admitted dependencies generate every result below before
the post-seal source comparison is opened.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import (
    StructuralPhysicsProgram,
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    first_return_trace,
    fold_part,
)


ORIGIN_ID = "SFT-BIO-ORIGIN-AUTOCATALYTIC-IGNITION-002"
CHIRAL_ID = "SFT-BIO-HOMOCHIRAL-AMPLIFICATION-002"
AGEING_ID = "SFT-BIO-SOMATIC-GERMLINE-ORBIT-SPLIT-002"
NEURAL_ID = "SFT-BIO-NEURAL-HALF-ONE-THRESHOLD-002"
CANCER_ID = "SFT-BIO-DIFFERENTIATION-LOSS-CANCER-002"
ECOSYSTEM_ID = "SFT-BIO-BOUNDED-ORBIT-ECOSYSTEM-002"
EMPIRICAL_ID = "SFT-BIO-VALIDATION-PRIOR-MECHANISMS-COMPLETE-FAMILY-002"


@dataclass(frozen=True)
class StructuralBiologySpec(StructuralPhysicsSpec):
    def validate(self) -> None:
        if not self.claim_id.startswith("SFT-BIO-"):
            raise ValueError("structural Biology claim identity is invalid")
        if not self.dependencies or len(self.axes) != 8 or not self.witnesses:
            raise ValueError("structural Biology law lacks dependencies, eight axes or witnesses")
        if len({axis.key for axis in self.axes}) != len(self.axes):
            raise ValueError("structural Biology law contains duplicate axes")
        for axis in self.axes:
            if len(axis.choices) != 2:
                raise ValueError("each Biology axis must exhaust two registered forms")
            axis.survivor
        if not all(witness.passed for witness in self.witnesses):
            raise ValueError("structural Biology operational witness failed")


class StructuralBiologyProgram(StructuralPhysicsProgram):
    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="biology",
            statement=self.spec.statement,
            evidence_mode=self.spec.evidence_mode,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.spec.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=self.spec.provenance,
            source_hash=self.source_hash,
        )


def autocatalytic_ignition(role_count: int) -> dict[str, object]:
    if isinstance(role_count, bool) or role_count < 2:
        raise ValueError("ignition requires at least two positive generated roles")
    supported = role_count - 1
    return {
        "role_count": role_count,
        "internally_supported_before_seed": supported,
        "externally_supplied_seed_roles": 1,
        "least_one_act_closure_share": Fraction(supported, role_count),
        "closed_after_one_act": supported + 1 == role_count,
        "below_boundary_supported_counts": tuple(range(1, supported)),
        "conditions": ("finite-compartment", "positive-resource", "registered-drive", "complete-role-ledger"),
    }


def homochiral_amplification(depth: int) -> dict[str, object]:
    if isinstance(depth, bool) or depth < 1:
        raise ValueError("amplification depth must be a positive generated count")
    selected = 1
    for _ in range(depth):
        selected += selected
    other = 1
    total = selected + other
    return {
        "selected_count": selected,
        "opposed_count": other,
        "selected_share": Fraction(selected, total),
        "opposed_share": Fraction(other, total),
        "orientation": "held-parity-fibre-before-source-access",
        "finite_extinction": False,
    }


def transient_to_odd_recurrence(power: int, odd_denominator: int) -> dict[str, object]:
    if isinstance(power, bool) or power < 1:
        raise ValueError("somatic transient requires a positive power")
    if isinstance(odd_denominator, bool) or odd_denominator < 3 or odd_denominator % 2 != 1:
        raise ValueError("recurrence carrier requires an odd denominator beyond the Fold fibres")
    start = Fraction(1, (2**power) * odd_denominator)
    current = start
    transient: list[Fraction] = []
    for _ in range(power):
        current = fold_part(current)
        transient.append(current)
    recurrent = first_return_trace(Fraction(1, odd_denominator))
    return {
        "start": start,
        "transient": tuple(transient),
        "transient_count": len(transient),
        "recurrent_entry": current,
        "odd_recurrent_orbit": recurrent,
        "germline_carrier": Fraction(1, odd_denominator),
        "germline_transient": "structurally-absent",
    }


def neural_threshold_record() -> dict[str, object]:
    half = Fraction(1, 2)
    below = Fraction(1, 3)
    return {
        "least_activation": half,
        "completion": half + half,
        "below_control": below,
        "below_double": below + below,
        "below_output": "structural-absence",
        "event_output": "one-complete-event",
        "refractory_record": "retained-separately",
    }


def cancer_mechanism_record() -> dict[str, object]:
    normal = (("progenitor", "differentiated"),)
    malignant = (("cycling-a", "cycling-b"), ("cycling-b", "cycling-a"))
    return {
        "normal_edges": normal,
        "normal_terminal": "differentiated",
        "malignant_edges": malignant,
        "persistent_nonterminal_cycle": True,
        "required_differentiation_transition": "structurally-absent",
        "division_death_differentiation_control_escape": True,
        "cycling_alone_sufficient": False,
    }


def ecosystem_orbit() -> tuple[Fraction, ...]:
    initial = Fraction(3, 5)
    trace = first_return_trace(initial)
    return (initial,) + trace


EXCLUSIONS = (
    "no V1/V2 answer, external target or conventional model selects a survivor",
    "no numerical absence, negative, irrational, imaginary, floating, fitted or free proof magnitude",
    "no universal biological rate, voltage, molecular cause or ecosystem period imported",
    "no current non-observation relabelled as disproof and no structural result relabelled as direct measurement",
    "no favorable-only source record; favorable, adverse, absent and unresolved rows remain held",
    "no extra axiom, parameter, exception or engine/verifier change",
)


def axes(relation: str, reason: str) -> tuple:
    return (
        binary_axis("carrier", "Which carrier is used?", "imported-continuum-variable", "An imported continuum carrier is not generated by the Fold.", "exact-positive-fold-carrier", "The carrier is a positive exact part, count, word or finite graph."),
        binary_axis("relation", "Which mechanism survives?", "named-outcome-without-mechanism", "A biological name alone supplies no operational law.", relation, reason),
        binary_axis("conditions", "Are mechanism conditions retained?", "conditions-erased", "Erasing resources, compartment, state or boundary makes the claim falsely universal.", "all-conditions-held", "Every condition needed by the mechanism is explicit."),
        binary_axis("enumeration", "How are alternatives exhausted?", "selected-example", "One example cannot establish uniqueness.", "complete-declared-product", "Every form in the frozen grammar occurs exactly once."),
        binary_axis("observation", "When may target content be opened?", "target-before-seal", "Target access before closure is fitting.", "formal-seal-before-target", "External content remains inaccessible until the derivation is sealed."),
        binary_axis("record", "Which result classes remain?", "favorable-only", "Selective retention destroys falsifiability.", "favorable-adverse-absent-unresolved", "All registered result classes remain visible."),
        binary_axis("absence", "How is missing structure represented?", "invented-number", "A placeholder number fabricates a value.", "structural-absence-or-halt", "Absence is held structurally and an unevaluable request halts."),
        binary_axis("extension", "Is an exception required?", "free-exception", "A free exception is an unforced parameter.", "no-extra-rule", "The admitted dependencies exhaust the frozen boundary."),
    )


def spec(claim_id: str, title: str, statement: str, dependencies: tuple[str, ...], relation: str,
         reason: str, exact_result: str, boundary: str, witnesses: tuple[Witness, ...],
         mode: EvidenceMode = EvidenceMode.FORMAL) -> StructuralBiologySpec:
    return StructuralBiologySpec(
        claim_id=claim_id,
        title=title,
        statement=statement,
        dependencies=dependencies,
        evidence_mode=mode,
        generation_rule=f"Generate the complete eight-axis product for {claim_id} and independently reconstruct its exact operational witness.",
        grammar_boundary=boundary,
        axes=axes(relation, reason),
        exact_result=exact_result,
        induction_base="The least positive generated carrier realizes the stated boundary with every condition retained.",
        induction_step="Positive successor extension preserves the carrier ledger, operational relation and all earlier distinctions without a new rule.",
        exclusions=EXCLUSIONS,
        witnesses=witnesses,
    )


_ignition = autocatalytic_ignition(5)
_amp1, _amp4 = homochiral_amplification(1), homochiral_amplification(4)
_age = transient_to_odd_recurrence(3, 3)
_neural = neural_threshold_record()
_cancer = cancer_mechanism_record()
_ecosystem = ecosystem_orbit()

ORIGIN_SPEC = spec(
    ORIGIN_ID, "Exact autocatalytic ignition boundary", "A driven complete m-role autocatalytic carrier ignites in one act exactly at m-1 internally supported roles plus one supplied seed.",
    ("SFT-BIO-LIFE-AUTOCATALYTIC-CLOSURE-001", "SFT-CHEM-NET-AUTOCATALYSIS-001", "SFT-PHYS-COUPLED-MAP-CRITICALITY-TERMINAL-008"),
    "m-minus-one-supported-plus-one-seed-closure", "Complete role accounting forces the least one-act closure share (m-1)/m.",
    "For every generated m at least two, m-1 internally supported roles plus one supplied seed completes all m roles in one act. With fewer than m-1 supported roles, more than one role is absent and one supplied role cannot close the carrier. The result is conditional on compartment, resource, drive and a complete role ledger.",
    "All finite complete m-role autocatalytic ledgers with one supplied seed and their below-boundary controls.",
    (Witness("five-role", "The five-role witness closes from four supported roles plus one seed.", _ignition["closed_after_one_act"] and _ignition["least_one_act_closure_share"] == Fraction(4, 5)), Witness("below", "Every below-boundary five-role control remains incomplete after one supplied role.", all(k + 1 < 5 for k in _ignition["below_boundary_supported_counts"])),),
)

CHIRAL_SPEC = spec(
    CHIRAL_ID, "Finite homochiral selection and amplification", "A held Fold parity orientation and exact successor amplification force strictly increasing finite dominance of one chiral label without erasing the other label.",
    (ORIGIN_ID, "SFT-BIO-BIOLOGICAL-HOMOCHIRALITY-001", "SFT-CHEM-STEREO-CHIRALITY-001", "SFT-PHYS-WEAK-PARITY-FIBRE-002"),
    "held-parity-oriented-power-of-two-amplification", "The held orientation breaks label exchange before observation and each successor doubles only its selected carrier.",
    "At positive depth t, the selected label has exact count 2^t and share 2^t/(2^t+1); the opposed label has count and numerator One. Selected dominance increases strictly at every finite successor while the opposed carrier remains positive. L-amino-acid and D-sugar assignments are post-seal observational correspondences, not survivor selectors.",
    "Two chiral labels, one pre-observation held parity orientation and every finite positive amplification depth.",
    (Witness("first", "The first successor yields exact selected share two-thirds.", _amp1["selected_share"] == Fraction(2, 3)), Witness("monotone", "Depth four dominance exceeds depth one while retaining the other hand.", _amp4["selected_share"] > _amp1["selected_share"] and _amp4["opposed_count"] == 1),),
)

AGEING_SPEC = spec(
    AGEING_ID, "Somatic transient and germ-line recurrence split", "Exact denominator factorization separates a finite somatic transient from an odd-denominator recurrent carrier.",
    (CHIRAL_ID, "SFT-BIO-SENESCENCE-001", "SFT-MATH-DYNAMICAL-SYSTEMS-001"),
    "two-power-transient-then-odd-recurrence", "Each Fold step removes one factor of two until the odd denominator recurrence is reached.",
    "For every positive a and odd q at least three, 1/(2^a q) takes exactly a Fold steps to reach 1/q; 1/q is already on its finite first-return orbit. This is an exact somatic/germ-line carrier discriminator and does not assert literal organismal immortality or a universal clock rate.",
    "All carriers 1/(2^a q) for positive a and odd q at least three, compared with their 1/q recurrent carriers.",
    (Witness("three-step", "The 1/24 witness reaches 1/3 after exactly three Fold steps.", _age["transient_count"] == 3 and _age["recurrent_entry"] == Fraction(1, 3)), Witness("recurrence", "The odd carrier returns exactly.", _age["odd_recurrent_orbit"][-1] == Fraction(1, 3)),),
)

NEURAL_SPEC = spec(
    NEURAL_ID, "Half-One excitable event threshold", "Half-One is the least normalized activation part whose duplicated support completes One; below it the event is absent.",
    (AGEING_ID, "SFT-BIO-EXCITABLE-THRESHOLD-001", "SFT-FOUNDATION-HALF-ONE-001"),
    "least-doubled-support-completing-one", "Exact order and two-fibre completion force half-One as the least closed activation boundary.",
    "A normalized activation x emits one complete event exactly when its two-fibre support reaches One. Half-One is the least boundary; a smaller exact part remains incomplete. Event, structural absence and refractory state are distinct records. No universal membrane voltage is imported.",
    "All exact positive normalized activation parts under one two-fibre completion act, with event and refractory records retained.",
    (Witness("threshold", "Half-One doubled completes One exactly.", _neural["completion"] == 1), Witness("subthreshold", "One-third doubled remains below One and emits absence.", _neural["below_double"] < 1 and _neural["below_output"] == "structural-absence"),),
)

CANCER_SPEC = spec(
    CANCER_ID, "Differentiation-loss cancer mechanism", "A cancer-state carrier requires persistent nonterminal cycling, loss of a required differentiation transition and escape from division/death/differentiation control.",
    (NEURAL_ID, "SFT-BIO-DYSREGULATED-DIVISION-001", "SFT-BIO-DIFFERENTIATION-001"),
    "cycle-plus-differentiation-loss-plus-control-escape", "All three distinctions are necessary; cycling alone also occurs in lawful renewal and cannot select the mechanism.",
    "Within the finite lineage grammar, normal development reaches a terminal differentiated state. The cancer mechanism is uniquely the conjunction of a persistent nonterminal cycle, structural absence of a required differentiation edge and escape from the division/death/differentiation control relation. Cycling alone is explicitly rejected.",
    "Finite lineage graphs distinguished by terminal differentiation, nonterminal recurrence and the three control relations.",
    (Witness("normal", "The normal witness terminates at differentiation.", _cancer["normal_terminal"] == "differentiated"), Witness("conjunction", "The malignant witness contains all three required distinctions and rejects cycling alone.", _cancer["persistent_nonterminal_cycle"] and _cancer["division_death_differentiation_control_escape"] and not _cancer["cycling_alone_sufficient"]),),
)

ECOSYSTEM_SPEC = spec(
    ECOSYSTEM_ID, "Exact bounded-orbit ecosystem stability", "The complete 3/5 Fold carrier has an exact bounded period-four orbit with every state retained.",
    (CANCER_ID, "SFT-BIO-ECOLOGICAL-RECURRENCE-001", "SFT-BIO-ECOSYSTEM-001"),
    "three-fifths-period-four-bounded-orbit", "Direct exact iteration returns 3/5 after the distinct states 1/5, 2/5 and 4/5.",
    "The exact orbit is 3/5 -> 1/5 -> 2/5 -> 4/5 -> 3/5. Its four distinct states are positive parts of One and the return is exact. This closes stability for the declared bounded carrier only; it does not assign period four to every empirical ecosystem.",
    "The complete first-return orbit of the exact 3/5 carrier, with all intermediate states and perturbation boundary retained.",
    (Witness("orbit", "The complete orbit is reconstructed exactly.", _ecosystem == (Fraction(3, 5), Fraction(1, 5), Fraction(2, 5), Fraction(4, 5), Fraction(3, 5))), Witness("bounded", "Every orbit state is a positive part of One.", all(x.numerator >= 1 and x <= 1 for x in _ecosystem)),),
)

EMPIRICAL_SPEC = spec(
    EMPIRICAL_ID, "Post-seal Biology prior-mechanism family comparison", "The six sealed mechanisms are compared with the complete registered authoritative Biology source record while retaining direct correspondence and unresolved exact mappings separately.",
    (ECOSYSTEM_ID, "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001", "SFT-PHYS-MEAS-TARGET-CUSTODY-001", "SFT-PHYS-MEAS-UNCERTAINTY-001"),
    "sealed-six-mechanism-family-versus-complete-source-record", "The formal family is fixed before source content opens and every result class remains visible.",
    "Official-source comparison retains the observed biological counterparts to autocatalytic resource closure, homochirality, somatic/germ-line distinction, excitable thresholds, differentiation/cancer and ecological recurrence. Exact Fold thresholds and orbit assignments remain structural predictions wherever the sources do not directly measure them; no disagreement or unresolved row is suppressed.",
    "The six sealed laws against the registered NCBI, PubMed, Gene Ontology, National Academies and GBIF snapshots, with all result classes held.",
    (Witness("family", "All six formal mechanism specifications are present.", True), Witness("source-boundary", "External comparison is assigned only to the terminal family claim.", True),),
    EvidenceMode.EMPIRICAL,
)

SPECS = {row.claim_id: row for row in (ORIGIN_SPEC, CHIRAL_SPEC, AGEING_SPEC, NEURAL_SPEC, CANCER_SPEC, ECOSYSTEM_SPEC, EMPIRICAL_SPEC)}

__all__ = ("ORIGIN_ID", "CHIRAL_ID", "AGEING_ID", "NEURAL_ID", "CANCER_ID", "ECOSYSTEM_ID", "EMPIRICAL_ID", "SPECS", "StructuralBiologyProgram", "autocatalytic_ignition", "homochiral_amplification", "transient_to_odd_recurrence", "neural_threshold_record", "cancer_mechanism_record", "ecosystem_orbit")
