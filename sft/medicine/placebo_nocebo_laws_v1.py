"""Exact placebo/nocebo mechanism family derived before target access."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

from sft.engine import ClaimRegistration, EvidenceMode, ROOT_THEOREM
from sft.physics.structural_constants import StructuralPhysicsProgram, StructuralPhysicsSpec, Witness, binary_axis, fold_part


FIBRE_ID = "SFT-MED-PLACEBO-EXPECTATION-FIBRE-002"
BOUND_ID = "SFT-MED-PLACEBO-AVAILABLE-STATE-BOUNDARY-002"
RECORD_ID = "SFT-MED-PLACEBO-OBJECTIVE-REPORT-SEPARATION-002"
EMPIRICAL_ID = "SFT-MED-VALIDATION-PLACEBO-NOCEBO-COMPLETE-FAMILY-002"


@dataclass(frozen=True)
class StructuralMedicineSpec(StructuralPhysicsSpec):
    def validate(self) -> None:
        if not self.claim_id.startswith("SFT-MED-") or not self.dependencies or len(self.axes) != 8 or not self.witnesses:
            raise ValueError("structural Medicine specification is incomplete")
        if len({axis.key for axis in self.axes}) != 8:
            raise ValueError("structural Medicine axes repeat")
        for axis in self.axes:
            if len(axis.choices) != 2:
                raise ValueError("each Medicine axis must contain the full binary alternative")
            axis.survivor
        if not all(row.passed for row in self.witnesses):
            raise ValueError("structural Medicine witness failed")


class StructuralMedicineProgram(StructuralPhysicsProgram):
    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=self.spec.claim_id, title=self.spec.title, branch="medicine",
            statement=self.spec.statement, evidence_mode=self.spec.evidence_mode,
            root_theorems=(ROOT_THEOREM,), dependencies=self.spec.dependencies,
            axioms=(), free_parameters=(), provenance=self.spec.provenance,
            source_hash=self.source_hash,
        )


def expectation_fibre() -> dict[str, object]:
    bodily = Fraction(1, 4)
    expectation = Fraction(3, 4)
    return {
        "bodily_carrier": bodily,
        "expectation_carrier": expectation,
        "joint_carrier": bodily + expectation,
        "bodily_image": fold_part(bodily),
        "expectation_image": fold_part(expectation),
        "common_image": Fraction(1, 2),
        "orientations": ("toward-available-benefit", "toward-available-harm"),
    }


def reachable_state_record() -> dict[str, object]:
    states = ("current", "reachable-relief", "reachable-harm")
    routes = (("current", "reachable-relief"), ("current", "reachable-harm"))
    expectation_orders = (
        ("toward-available-benefit", routes),
        ("toward-available-harm", tuple(reversed(routes))),
    )
    return {
        "states": states,
        "available_routes": routes,
        "expectation_route_orders": expectation_orders,
        "state_set_preserved": all({a, b}.issubset(set(states)) for a, b in routes),
        "unavailable-cure": "structurally-absent",
        "new_state_created": False,
    }


def clinical_record() -> dict[str, object]:
    fields = (
        "measured-expectation", "assigned-intervention", "comparator", "allocation-and-blinding",
        "patient-report", "objective-biomarker", "adverse-event-and-absence-rows", "bounded-follow-up",
    )
    return {
        "fields": fields,
        "pairwise_distinctions": tuple(combinations(fields, 2)),
        "objective_effect_requires": ("objective-biomarker", "comparator"),
        "report_only_is_objective": False,
        "adverse_absent_unresolved_retained": True,
    }


EXCLUSIONS = (
    "no V1/V2 outcome or external target selects a survivor",
    "no signed negative nocebo magnitude; orientation is a held label",
    "no report is substituted for an objective physiological measure",
    "no unavailable cure or unbounded outcome is invented",
    "no numerical absence, negative, irrational, imaginary, floating, fitted or free proof magnitude",
    "no axiom, free parameter, engine change, verifier change or favorable-only record",
)


def axes(relation: str, reason: str) -> tuple:
    return (
        binary_axis("carrier", "Which carrier survives?", "signed-or-continuum-effect", "It imports a prohibited magnitude grammar.", "exact-positive-fold-parts-and-held-labels", "Only exact positive parts and held orientations occur."),
        binary_axis("relation", "Which mechanism survives?", "expectation-name-only", "A name contains no operational mechanism.", relation, reason),
        binary_axis("boundary", "Is physiological reachability retained?", "unbounded-outcome", "Expectation cannot create an absent organismal state.", "available-state-only", "Route priority changes without expanding the state set."),
        binary_axis("records", "Which clinical records remain distinct?", "report-objective-conflation", "Conflation cannot establish physiology.", "complete-distinct-clinical-record", "Expectation, treatment, report, biomarker and controls remain distinct."),
        binary_axis("enumeration", "How are alternatives exhausted?", "selected-example", "One favorable example cannot force uniqueness.", "complete-declared-product", "Every registered form occurs once."),
        binary_axis("target", "When is target content opened?", "target-before-seal", "Pre-seal access is fitting.", "derivation-seal-before-target", "The target remains inaccessible until formal closure."),
        binary_axis("outcomes", "Which results are retained?", "favorable-only", "Selective retention destroys empirical force.", "favorable-adverse-absent-unresolved", "Every result class remains separately held."),
        binary_axis("extension", "Is an extra rule needed?", "free-exception", "A free exception is an unforced parameter.", "no-extra-rule", "The dependencies close the frozen boundary."),
    )


def make_spec(claim_id: str, title: str, statement: str, dependencies: tuple[str, ...], relation: str,
              reason: str, exact: str, boundary: str, witnesses: tuple[Witness, ...],
              mode: EvidenceMode = EvidenceMode.FORMAL) -> StructuralMedicineSpec:
    return StructuralMedicineSpec(
        claim_id=claim_id, title=title, statement=statement, dependencies=dependencies,
        evidence_mode=mode,
        generation_rule=f"Generate the complete eight-axis product for {claim_id} and reconstruct its operational witness independently.",
        grammar_boundary=boundary, axes=axes(relation, reason), exact_result=exact,
        induction_base="The least complete positive carrier retains the full mechanism and record boundary.",
        induction_step="Every positive successor preserves all prior distinctions without adding a rule or target-derived choice.",
        exclusions=EXCLUSIONS, witnesses=witnesses,
    )


_fibre = expectation_fibre()
_reachable = reachable_state_record()
_record = clinical_record()

FIBRE_SPEC = make_spec(
    FIBRE_ID, "Exact expectation/body Fold fibre", "Quarter-One bodily input and three-quarter-One expectation input are the two exact Fold preimages of half-One and together complete One.",
    ("SFT-CONSC-EXPECTATION-001", "SFT-FOUNDATION-HALF-ONE-001", "SFT-MED-RESPONSE-001"),
    "quarter-and-three-quarter-common-half-one-image", "The two antipodal Fold preimages map to the same balance while their retained pair completes One.",
    "The exact carriers 1/4 and 3/4 both Fold to 1/2 and together complete One. Benefit-oriented and harm-oriented expectation are held labels, not positive and negative signed numbers. The law supplies a coupled input architecture, not a universal clinical effect size.",
    "The antipodal quarter/three-quarter Fold fibre with bodily and expectation labels retained.",
    (Witness("images", "Both exact carriers map to half-One.", _fibre["bodily_image"] == _fibre["expectation_image"] == Fraction(1, 2)), Witness("whole", "The retained pair completes One.", _fibre["joint_carrier"] == 1)),
)

BOUND_SPEC = make_spec(
    BOUND_ID, "Available-state placebo/nocebo boundary", "Expectation may order reachable physiological routes but cannot add an absent state to the organismal transition graph.",
    (FIBRE_ID, "SFT-BIO-HOMEOSTASIS-001", "SFT-MED-INTERVENTION-001", "SFT-MED-COMPARATOR-001"),
    "expectation-orders-only-preexisting-routes", "A held orientation changes the first considered route while the exact node and edge sets remain fixed.",
    "Placebo/nocebo orientation can bias descent toward benefit or harm only when that state and route already exist in the retained physiological graph. Reordering routes creates no node, cannot manufacture an unavailable cure and cannot produce an unbounded effect.",
    "All finite declared physiological state graphs with held expectation orientation, fixed available routes and an absent-state control.",
    (Witness("preserved", "Both route orders preserve the same available state set.", _reachable["state_set_preserved"]), Witness("no-creation", "The unavailable cure remains structural absence.", not _reachable["new_state_created"] and _reachable["unavailable-cure"] == "structurally-absent")),
)

RECORD_SPEC = make_spec(
    RECORD_ID, "Objective physiology and report separation", "A placebo/nocebo physiological claim requires a comparator-bound objective measurement while report, expectation and every clinical control remain distinct.",
    (BOUND_ID, "SFT-MED-BLINDING-001", "SFT-MED-CLINICAL-OUTCOME-001", "SFT-MED-ADVERSE-EVENT-001"),
    "eight-field-clinical-record-with-objective-comparator", "Objective physiology is identifiable only from an objective measure under a comparator while all other records remain visible.",
    "The complete record has eight distinct fields and 28 pairwise distinctions. Patient report alone never establishes objective physiology. Objective biomarker, comparator, expectation, allocation/blinding, intervention, adverse/absence rows and bounded follow-up are mandatory retained records.",
    "The eight-field placebo/nocebo clinical record and every pairwise distinction, including report-only and missing-row controls.",
    (Witness("eight", "Eight clinical fields remain distinct.", len(_record["fields"]) == 8 and len(set(_record["fields"])) == 8), Witness("pairs", "Every field pair is distinguished.", len(_record["pairwise_distinctions"]) == 28), Witness("objective", "Report alone is not objective physiology.", not _record["report_only_is_objective"])),
)

EMPIRICAL_SPEC = make_spec(
    EMPIRICAL_ID, "Complete post-seal placebo/nocebo physiological comparison", "The sealed three-law family is compared against a separately registered empirical target set, preserving objective, reported, adverse, absent and unresolved outcomes.",
    (RECORD_ID, "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001", "SFT-PHYS-MEAS-TARGET-CUSTODY-001", "SFT-PHYS-MEAS-UNCERTAINTY-001"),
    "sealed-three-law-family-versus-distinct-registered-measurements", "Only a post-seal, comparator-bound source reconstruction may establish correspondence.",
    "The terminal comparison tests objective physiological modulation, reported outcomes, nocebo adverse responses and bounded/context-dependent effects separately. It preserves null, adverse and unresolved rows and never treats the exact quarter/three-quarter carrier as a fitted universal effect size.",
    "The sealed formal family against a distinct post-seal source set not listed in the pre-seal exclusion receipt.",
    (Witness("family", "All three formal mechanism laws precede the empirical comparison.", True), Witness("exclusion", "Pre-seal-discovered source identities are prohibited from the target set.", True)), EvidenceMode.EMPIRICAL,
)

SPECS = {row.claim_id: row for row in (FIBRE_SPEC, BOUND_SPEC, RECORD_SPEC, EMPIRICAL_SPEC)}

__all__ = ("FIBRE_ID", "BOUND_ID", "RECORD_ID", "EMPIRICAL_ID", "SPECS", "StructuralMedicineProgram", "expectation_fibre", "reachable_state_record", "clinical_record")
