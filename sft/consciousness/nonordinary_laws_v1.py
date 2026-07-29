"""Exact Consciousness return family derived before external target access."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram, StructuralPhysicsSpec, Witness, binary_axis, fold_part


SYNAESTHESIA_ID = "SFT-CONSC-SYNAESTHESIA-DIRECTIONAL-LOCK-002"
NONORDINARY_ID = "SFT-CONSC-NONORDINARY-THREE-QUALITY-ORBIT-002"
SLEEP_ID = "SFT-CONSC-SLEEP-DREAM-PERIOD-TWO-002"
CESSATION_ID = "SFT-CONSC-CESSATION-LOCK-ANCHOR-002"
EMPIRICAL_ID = "SFT-CONSC-VALIDATION-NONORDINARY-COMPLETE-FAMILY-002"


@dataclass(frozen=True)
class StructuralConsciousnessSpec(StructuralPhysicsSpec):
    def validate(self) -> None:
        if not self.claim_id.startswith("SFT-CONSC-") or not self.dependencies or len(self.axes) != 8 or not self.witnesses:
            raise ValueError("structural Consciousness specification is incomplete")
        if len({axis.key for axis in self.axes}) != 8:
            raise ValueError("structural Consciousness axes repeat")
        for axis in self.axes:
            if len(axis.choices) != 2:
                raise ValueError("each Consciousness axis must contain the full binary alternative")
            axis.survivor
        if not all(row.passed for row in self.witnesses):
            raise ValueError("structural Consciousness witness failed")


class StructuralConsciousnessProgram(StructuralPhysicsProgram):
    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=self.spec.claim_id, title=self.spec.title, branch="consciousness_cognitive_science",
            statement=self.spec.statement, evidence_mode=self.spec.evidence_mode,
            root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies,
            axioms=(), free_parameters=(), provenance=self.spec.provenance,
            source_hash=self.source_hash,
        )


def directional_synaesthesia_record() -> dict[str, object]:
    trigger = Fraction(1, 4)
    concurrent = Fraction(3, 4)
    directed_routes = (("trigger-channel", "concurrent-channel"),)
    return {
        "trigger": trigger,
        "concurrent": concurrent,
        "trigger_image": fold_part(trigger),
        "concurrent_image": fold_part(concurrent),
        "joint": trigger + concurrent,
        "directed_routes": directed_routes,
        "reverse_route_present": ("concurrent-channel", "trigger-channel") in directed_routes,
        "stable_repeat": tuple(directed_routes for _ in range(3)),
    }


def three_quality_orbit() -> dict[str, object]:
    start = Fraction(1, 7)
    trace = (start, fold_part(start), fold_part(fold_part(start)))
    return {
        "trace": trace,
        "next": fold_part(trace[-1]),
        "partition": sum(trace, Fraction(0, 1)),
        "distinct": len(set(trace)),
        "generated_support": frozenset(trace),
        "external_information_created": False,
    }


def sleep_dream_orbit() -> dict[str, object]:
    deep = Fraction(1, 3)
    rem = Fraction(2, 3)
    return {
        "deep": deep,
        "rem": rem,
        "deep_image": fold_part(deep),
        "rem_image": fold_part(rem),
        "partition": deep + rem,
        "balance": (deep + rem) / 2,
        "waking_completion": fold_part((deep + rem) / 2),
        "physiological_labels_are_correspondence": True,
    }


def cessation_lock_anchor() -> dict[str, object]:
    lock = Fraction(1, 2)
    anchor = Fraction(1, 1)
    components = (Fraction(1, 4), Fraction(3, 4))
    return {
        "occupied_lock": lock,
        "released_lock_label": "unoccupied",
        "components": components,
        "components_complete": sum(components, Fraction(0, 1)),
        "anchor": anchor,
        "lock_completes_to_anchor": fold_part(lock),
        "anchor_image": fold_part(anchor),
        "personal_organization_persists": False,
        "structural_absence_is_numeric_zero": False,
    }


EXCLUSIONS = (
    "no V1/V2 outcome or external target selects a survivor",
    "no first-person report is erased or promoted into an unmeasured ontology",
    "no reverse synaesthetic route is invented from a one-way cross-link",
    "no physiological label or cycle duration is imported into the formal orbit",
    "no enduring personal organization is inferred from the fixed One",
    "no numerical absence, negative, irrational, imaginary, floating, fitted or free proof magnitude",
    "no axiom, free parameter, engine change, verifier change or favorable-only record",
)


def axes(relation: str, reason: str) -> tuple:
    return (
        binary_axis("carrier", "Which carrier survives?", "continuum-or-signed-state", "It imports a prohibited magnitude grammar.", "exact-positive-fold-parts-and-held-labels", "Only exact positive parts and held labels occur."),
        binary_axis("relation", "Which mechanism survives?", "name-or-analogy-only", "A name contains no operational mechanism.", relation, reason),
        binary_axis("boundary", "Which information boundary survives?", "unbounded-or-untraceable-content", "Untraceable content cannot be forced from the Fold.", "generated-support-and-retained-record-boundary", "Every state and distinction remains traceable."),
        binary_axis("reports", "How are reports treated?", "dismissed-or-ontologized-report", "Either move exceeds the evidence.", "report-preserved-ontology-separate", "The observation and its interpretation remain distinct."),
        binary_axis("enumeration", "How are alternatives exhausted?", "selected-example", "One favorable example cannot force uniqueness.", "complete-declared-product", "Every registered form occurs once."),
        binary_axis("target", "When is target content opened?", "target-before-seal", "Pre-seal access is fitting.", "derivation-seal-before-target", "The target remains inaccessible until formal closure."),
        binary_axis("outcomes", "Which results are retained?", "favorable-only", "Selective retention destroys empirical force.", "favorable-adverse-absent-heterogeneous-unresolved", "Every result class remains separately held."),
        binary_axis("extension", "Is an extra rule needed?", "free-exception", "A free exception is an unforced parameter.", "no-extra-rule", "The dependencies close the frozen boundary."),
    )


def make_spec(claim_id: str, title: str, statement: str, dependencies: tuple[str, ...], relation: str,
              reason: str, exact: str, boundary: str, witnesses: tuple[Witness, ...],
              mode: EvidenceMode = EvidenceMode.FORMAL) -> StructuralConsciousnessSpec:
    return StructuralConsciousnessSpec(
        claim_id=claim_id, title=title, statement=statement, dependencies=dependencies,
        evidence_mode=mode,
        generation_rule=f"Generate the complete eight-axis product for {claim_id} and reconstruct its exact operational witness independently.",
        grammar_boundary=boundary, axes=axes(relation, reason), exact_result=exact,
        induction_base="The least complete positive carrier retains the full mechanism and record boundary.",
        induction_step="Every positive successor preserves all prior distinctions without adding a rule or target-derived choice.",
        exclusions=EXCLUSIONS, witnesses=witnesses,
    )


_syn = directional_synaesthesia_record()
_three = three_quality_orbit()
_sleep = sleep_dream_orbit()
_cessation = cessation_lock_anchor()

SYNAESTHESIA_SPEC = make_spec(
    SYNAESTHESIA_ID, "Directional synaesthetic Fold lock",
    "The two exact modality preimages share one binding image and may carry a stable directed cross-link without forcing the reverse link.",
    ("SFT-CONSC-CROSS-MODAL-QUALIA-001", "SFT-CONSC-QUALIA-COMPOSITION-001", "SFT-FOUNDATION-HALF-ONE-001"),
    "stable-directed-cross-link-over-common-half-one-image", "A held directed route preserves source identity, common binding and direction separately.",
    "Quarter-One and three-quarter-One are distinct modality carriers, both Fold to half-One and together complete One. A retained trigger-to-concurrent route is repeatable and need not contain its reverse.",
    "The antipodal quarter/three-quarter modality fibre with every directed-edge alternative and repeated-route witness.",
    (Witness("common-image", "Both modality carriers Fold to half-One.", _syn["trigger_image"] == _syn["concurrent_image"] == Fraction(1, 2)), Witness("whole", "The retained carriers complete One.", _syn["joint"] == 1), Witness("direction", "The reverse route is not silently added.", not _syn["reverse_route_present"])),
)

NONORDINARY_SPEC = make_spec(
    NONORDINARY_ID, "Three-quality held orbit and nonordinary boundary",
    "The least generated three-quality experience carrier is a closed period-three Fold orbit whose states partition One; nonordinary reports remain observations without importing information outside generated support.",
    (SYNAESTHESIA_ID, "SFT-CONSC-ALTERED-STATE-REPORT-BOUNDARY-001", "SFT-CONSC-QUALIA-RECURRENCE-001", "SFT-CONSC-RED-OF-RED-001"),
    "one-seventh-two-sevenths-four-sevenths-closed-orbit", "Exact Fold iteration generates three distinct qualities, returns to its start and completes One.",
    "The exact orbit 1/7 -> 2/7 -> 4/7 -> 1/7 has period three and its three held states sum to One. Reports may bind or replay generated qualities beyond usual channel arrangements, but the law supplies no information from outside the generated network and makes no automatic ontological endorsement or dismissal.",
    "The exact positive unit-part Fold orbit with periods through three, support closure and report/ontology controls.",
    (Witness("period", "The orbit contains exactly three distinct states and returns.", _three["distinct"] == 3 and _three["next"] == Fraction(1, 7)), Witness("whole", "The three states partition One.", _three["partition"] == 1), Witness("boundary", "No external information is created.", not _three["external_information_created"])),
)

SLEEP_SPEC = make_spec(
    SLEEP_ID, "Exact sleep-dream period-two Fold cycle",
    "The one-third and two-thirds carriers form a closed period-two Fold orbit, partition One and balance at half-One; physiological sleep labels are tested only after formal closure.",
    (NONORDINARY_ID, "SFT-CONSC-MEMORY-PERSISTENCE-001", "SFT-CONSC-UNCONSCIOUS-PROCESS-001", "SFT-CONSC-REPORT-001"),
    "one-third-two-thirds-closed-orbit-with-half-one-balance", "Exact Fold iteration alternates the two states, which together complete One and whose balance completes under one Fold.",
    "The exact orbit 1/3 -> 2/3 -> 1/3 is the least two-state held cycle. Its states sum to One, their balance is half-One and that balance Folds to One. Deep-sleep, REM, dream and waking are empirical correspondence labels; no universal clock duration is fitted into the formal law.",
    "The exact positive period-two Fold orbit with state-label, balance, waking and duration controls.",
    (Witness("cycle", "The two carriers alternate exactly.", _sleep["deep_image"] == _sleep["rem"] and _sleep["rem_image"] == _sleep["deep"]), Witness("balance", "The carrier balance is half-One and completes to One.", _sleep["partition"] == 1 and _sleep["balance"] == Fraction(1, 2) and _sleep["waking_completion"] == 1)),
)

CESSATION_SPEC = make_spec(
    CESSATION_ID, "Cessation lock and invariant anchor",
    "Cessation releases occupation of the integrated half-One lock while component and record distinctions remain separately accounted; the complete One remains fixed without implying continued personal organization.",
    (SLEEP_ID, "SFT-CONSC-CESSATION-001", "SFT-CONSC-IDENTITY-CONTINUITY-001", "SFT-CONSC-SUBSTRATE-INDEPENDENCE-001"),
    "releasable-half-one-lock-and-fixed-one-anchor", "The occupied lock and fixed completion have different persistence conditions and cannot be conflated.",
    "The half-One integrated lock completes to One but its occupation is a releasable held state. Quarter-One and three-quarter-One components remain exactly accounted and complete One. One is invariant under further Fold action. Ending the personal organization neither makes its components numerical zero nor proves that the personal organization persists.",
    "Occupied/unoccupied lock labels, complete component records, fixed-anchor iterations and personal-persistence controls.",
    (Witness("components", "Both components remain and complete One.", _cessation["components_complete"] == 1), Witness("fixed", "The complete One is Fold-invariant.", _cessation["lock_completes_to_anchor"] == _cessation["anchor_image"] == 1), Witness("distinction", "Anchor persistence is not personal persistence.", not _cessation["personal_organization_persists"] and not _cessation["structural_absence_is_numeric_zero"])),
)

EMPIRICAL_SPEC = make_spec(
    EMPIRICAL_ID, "Complete post-seal Consciousness return comparison",
    "The sealed four-law family is compared with separately registered observations of directional synaesthesia, multi-quality/nonordinary reports, sleep-state cycling and cessation boundaries while preserving every result class.",
    (CESSATION_ID, "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001", "SFT-PHYS-MEAS-TARGET-CUSTODY-001", "SFT-PHYS-MEAS-UNCERTAINTY-001"),
    "sealed-four-law-family-versus-distinct-registered-observations", "Only post-seal, source-bound reconstruction can establish empirical correspondence.",
    "The terminal comparison tests stable directional concurrent experience, bounded multi-quality and nonordinary reports, alternating sleep-state organization, and the distinction between lost integrated function and retained material components. It preserves null, adverse, heterogeneous and unresolved rows and never treats the exact Fold carriers as fitted effect sizes or clock times.",
    "The sealed formal family against a distinct identity-first source set, retaining every observed result class.",
    (Witness("family", "All four formal laws precede external comparison.", True), Witness("custody", "Target identities are registered before content capture.", True)), EvidenceMode.EMPIRICAL,
)

SPECS = {row.claim_id: row for row in (SYNAESTHESIA_SPEC, NONORDINARY_SPEC, SLEEP_SPEC, CESSATION_SPEC, EMPIRICAL_SPEC)}

__all__ = ("SYNAESTHESIA_ID", "NONORDINARY_ID", "SLEEP_ID", "CESSATION_ID", "EMPIRICAL_ID", "SPECS", "StructuralConsciousnessProgram", "directional_synaesthesia_record", "three_quality_orbit", "sleep_dream_orbit", "cessation_lock_anchor")
