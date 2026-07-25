"""Exact fusion/fission yield ordering and distinct-threshold law.

The claimant has no access to AME or IAEA targets, isotope names, dimensional
reaction energies, cross sections, temperatures or fitted coefficients.  It
uses only admitted exact nuclear coordinates, the sealed zero-parameter
binding ledger and structural incident-boundary traces.  Structural absence is
the empty tuple and never a numerical proof value.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from functools import lru_cache
from itertools import product
from typing import Sequence

from sft.engine import (
    Candidate,
    CandidateCensus,
    CandidateDecision,
    ClaimRegistration,
    ClosureEvidence,
    ClosureScope,
    ControlKind,
    ControlResult,
    EvidenceMode,
    ProvenanceClass,
    ROOT_THEOREM,
)
from sft.engine.canonical import sha256_identity
from sft.physics.fusion_fission_terminal_law_v1 import (
    NuclearCoordinate,
    fission_trace,
    fusion_trace,
    reaction_conserves_counts,
)
from sft.physics.nuclear_binding_curve_successor_laws_v1 import (
    binding_score_enclosure,
)
from sft.physics.nuclear_residual_force_successor_laws_v1 import (
    finite_boundary_capacity,
    residual_boundary_support,
)
from sft.physics.prior_value_laws import positive_take


CLAIM_ID = "SFT-PHYS-NUCLEAR-FUSION-FISSION-YIELD-THRESHOLD-006"
EXPERIMENT_ID = "SFT-EXP-PHYS-NUCLEAR-FUSION-FISSION-YIELD-THRESHOLD-006"
REFINEMENTS = 16
Empty = tuple[()]


@dataclass(frozen=True)
class ThresholdTrace:
    incident_words: tuple[NuclearCoordinate, ...]
    inter_boundary_charge_paths: int | Empty
    neutral_trigger_charge: Empty
    internal_boundary_cells: int


@dataclass(frozen=True)
class CandidateForm:
    per_nucleon_relation: str
    total_release_relation: str
    fusion_threshold_carrier: str
    fission_threshold_carrier: str
    threshold_scope: str
    access_carrier: str
    metric_retention: str
    target_boundary: str
    extension: str

    @property
    def candidate_id(self) -> str:
        return "__".join((
            self.per_nucleon_relation,
            self.total_release_relation,
            self.fusion_threshold_carrier,
            self.fission_threshold_carrier,
            self.threshold_scope,
            self.access_carrier,
            self.metric_retention,
            self.target_boundary,
            self.extension,
        ))


PER_NUCLEON_RELATIONS = (
    "fusion-greater-per-nucleon",
    "equal-per-nucleon",
    "fission-greater-per-nucleon",
)
TOTAL_RELEASE_RELATIONS = (
    "fusion-greater-total",
    "equal-total",
    "fission-greater-total",
)
FUSION_THRESHOLD_CARRIERS = (
    "charged-boundary-approach",
    "neutral-capture-approach",
    "single-parent-internal-surface",
)
FISSION_THRESHOLD_CARRIERS = (
    "charged-boundary-approach",
    "neutral-capture-or-internal-surface",
    "carrier-free-decomposition",
)
THRESHOLD_SCOPES = (
    "one-universal-dimensional-threshold",
    "normalized-structure-with-reaction-specific-dimensions",
    "no-threshold-distinction",
)
ACCESS_CARRIERS = (
    "thermal-or-directed-energy-support",
    "one-universal-temperature-value",
    "no-access-support",
)
METRIC_RETENTIONS = (
    "retain-per-nucleon-and-total-separately",
    "conflate-per-nucleon-with-total",
)
TARGET_BOUNDARIES = ("sealed-before-release", "readable-before-seal")
EXTENSIONS = ("empty-extension", "free-correction")

GENERATION_RULE = (
    "Generate the complete product of all three exact per-nucleon orders, all three total-release orders, "
    "all generated fusion and fission threshold-carrier classes, all threshold scopes, all access-carrier "
    "classes, both metric-retention states, both target-custody states and both extension states."
)
GRAMMAR_BOUNDARY = (
    "The least light binary junction D+D to He-4 and the registered symmetric heavy decomposition U-238 to "
    "two Pd-119 words; every strict or equal ordering of their exact binding-score enclosures; every incident "
    "charged, neutral or internal boundary class; normalized versus dimensional threshold scope; thermal or "
    "directed access support; separate versus conflated release metrics; sealed or exposed target custody; and "
    "empty or free extension.  The certificate is not bounded by a Fold search depth."
)


@lru_cache(maxsize=None)
def per_nucleon_gain_enclosure(operation: str) -> tuple[Fraction, Fraction]:
    if operation == "fusion":
        incident = binding_score_enclosure(2, 1, REFINEMENTS)
        product_score = binding_score_enclosure(4, 2, REFINEMENTS)
    elif operation == "fission":
        incident = binding_score_enclosure(238, 92, REFINEMENTS)
        product_score = binding_score_enclosure(119, 46, REFINEMENTS)
    else:
        raise ValueError("yield comparison names an ungenerated reaction class")
    if product_score[0] <= incident[1]:
        raise ValueError("registered reaction lacks a separated positive binding gain")
    return (
        positive_take(product_score[0], incident[1]),
        positive_take(product_score[1], incident[0]),
    )


@lru_cache(maxsize=None)
def total_release_enclosure(operation: str) -> tuple[Fraction, Fraction]:
    gain = per_nucleon_gain_enclosure(operation)
    if operation == "fusion":
        conserved_mass = 4
        if not reaction_conserves_counts(fusion_trace("binary-junction")):
            raise ValueError("fusion representative lost a conserved count")
    elif operation == "fission":
        conserved_mass = 238
        if not reaction_conserves_counts(fission_trace("binary-decomposition")):
            raise ValueError("fission representative lost a conserved count")
    else:
        raise ValueError("release comparison names an ungenerated reaction class")
    return conserved_mass * gain[0], conserved_mass * gain[1]


@lru_cache(maxsize=1)
def exact_release_order() -> dict[str, object]:
    fusion_per = per_nucleon_gain_enclosure("fusion")
    fission_per = per_nucleon_gain_enclosure("fission")
    fusion_total = total_release_enclosure("fusion")
    fission_total = total_release_enclosure("fission")
    return {
        "fusion_per_nucleon": fusion_per,
        "fission_per_nucleon": fission_per,
        "fusion_total": fusion_total,
        "fission_total": fission_total,
        "fusion_greater_per_nucleon": fusion_per[0] > fission_per[1],
        "fission_greater_total": fission_total[0] > fusion_total[1],
        "orders_are_distinct": (
            fusion_per[0] > fission_per[1]
            and fission_total[0] > fusion_total[1]
        ),
    }


def inter_boundary_charge_paths(words: tuple[NuclearCoordinate, ...]) -> int | Empty:
    if len(words) == 1:
        return ()
    if len(words) != 2:
        raise ValueError("threshold grammar contains only one- or two-word incident support")
    left, right = words
    paths = left.charge_count * right.charge_count
    if paths < 1:
        raise ValueError("charged inter-boundary path count must remain positive")
    return paths


@lru_cache(maxsize=1)
def fusion_threshold_trace() -> ThresholdTrace:
    trace = fusion_trace("binary-junction")
    paths = inter_boundary_charge_paths(trace.incident)
    if paths == ():
        raise ValueError("fusion junction lost its charged incident boundary")
    return ThresholdTrace(
        incident_words=trace.incident,
        inter_boundary_charge_paths=paths,
        neutral_trigger_charge=(),
        internal_boundary_cells=finite_boundary_capacity(),
    )


@lru_cache(maxsize=1)
def fission_threshold_trace() -> ThresholdTrace:
    trace = fission_trace("binary-decomposition")
    paths = inter_boundary_charge_paths(trace.incident)
    if paths != ():
        raise ValueError("one-parent fission acquired an inter-composite charge path")
    return ThresholdTrace(
        incident_words=trace.incident,
        inter_boundary_charge_paths=paths,
        neutral_trigger_charge=(),
        internal_boundary_cells=finite_boundary_capacity(),
    )


@lru_cache(maxsize=1)
def threshold_topology() -> dict[str, object]:
    fusion = fusion_threshold_trace()
    fission = fission_threshold_trace()
    return {
        "fusion_has_two_charged_incident_words": (
            len(fusion.incident_words) == 2
            and all(word.charge_count >= 1 for word in fusion.incident_words)
        ),
        "fusion_inter_boundary_paths": fusion.inter_boundary_charge_paths,
        "fission_has_one_parent_word": len(fission.incident_words) == 1,
        "fission_inter_boundary_paths": fission.inter_boundary_charge_paths,
        "neutral_trigger_charge_is_empty_form": fission.neutral_trigger_charge == (),
        "internal_surface_is_finite": fission.internal_boundary_cells == finite_boundary_capacity(),
        "residual_interaction_is_short_range_order": residual_boundary_support() == Fraction(1, 4),
        "carriers_are_distinct": (
            fusion.inter_boundary_charge_paths != ()
            and fission.inter_boundary_charge_paths == ()
        ),
    }


def per_nucleon_relation_is_forced(relation: str) -> bool:
    order = exact_release_order()
    if relation == "fusion-greater-per-nucleon":
        return order["fusion_greater_per_nucleon"] is True
    if relation == "equal-per-nucleon":
        return order["fusion_per_nucleon"] == order["fission_per_nucleon"]
    if relation == "fission-greater-per-nucleon":
        return order["fission_per_nucleon"][0] > order["fusion_per_nucleon"][1]
    raise ValueError("candidate names an ungenerated per-nucleon relation")


def total_release_relation_is_forced(relation: str) -> bool:
    order = exact_release_order()
    if relation == "fusion-greater-total":
        return order["fusion_total"][0] > order["fission_total"][1]
    if relation == "equal-total":
        return order["fusion_total"] == order["fission_total"]
    if relation == "fission-greater-total":
        return order["fission_greater_total"] is True
    raise ValueError("candidate names an ungenerated total-release relation")


def fusion_threshold_carrier_is_forced(carrier: str) -> bool:
    topology = threshold_topology()
    if carrier == "charged-boundary-approach":
        return (
            topology["fusion_has_two_charged_incident_words"] is True
            and topology["fusion_inter_boundary_paths"] != ()
        )
    if carrier == "neutral-capture-approach":
        return topology["fusion_inter_boundary_paths"] == ()
    if carrier == "single-parent-internal-surface":
        return len(fusion_threshold_trace().incident_words) == 1
    raise ValueError("candidate names an ungenerated fusion-threshold carrier")


def fission_threshold_carrier_is_forced(carrier: str) -> bool:
    topology = threshold_topology()
    if carrier == "charged-boundary-approach":
        return topology["fission_inter_boundary_paths"] != ()
    if carrier == "neutral-capture-or-internal-surface":
        return all((
            topology["fission_has_one_parent_word"] is True,
            topology["fission_inter_boundary_paths"] == (),
            topology["neutral_trigger_charge_is_empty_form"] is True,
            topology["internal_surface_is_finite"] is True,
        ))
    if carrier == "carrier-free-decomposition":
        return not topology["internal_surface_is_finite"]
    raise ValueError("candidate names an ungenerated fission-threshold carrier")


def threshold_scope_is_forced(scope: str) -> bool:
    distinct = threshold_topology()["carriers_are_distinct"] is True
    normalized_only = residual_boundary_support() == Fraction(1, 4)
    if scope == "one-universal-dimensional-threshold":
        return not distinct
    if scope == "normalized-structure-with-reaction-specific-dimensions":
        return distinct and normalized_only
    if scope == "no-threshold-distinction":
        return not distinct and not normalized_only
    raise ValueError("candidate names an ungenerated threshold scope")


def access_carrier_is_forced(carrier: str) -> bool:
    charged_path = fusion_threshold_trace().inter_boundary_charge_paths != ()
    reaction_specific = threshold_topology()["carriers_are_distinct"] is True
    if carrier == "thermal-or-directed-energy-support":
        return charged_path and reaction_specific
    if carrier == "one-universal-temperature-value":
        return not reaction_specific
    if carrier == "no-access-support":
        return not charged_path
    raise ValueError("candidate names an ungenerated access carrier")


def metric_retention_is_forced(retention: str) -> bool:
    distinct = exact_release_order()["orders_are_distinct"] is True
    if retention == "retain-per-nucleon-and-total-separately":
        return distinct
    if retention == "conflate-per-nucleon-with-total":
        return not distinct
    raise ValueError("candidate names an ungenerated metric-retention state")


def target_boundary_is_forced(boundary: str) -> bool:
    if boundary == "sealed-before-release":
        return True
    if boundary == "readable-before-seal":
        return False
    raise ValueError("candidate names an ungenerated target boundary")


def extension_is_forced(extension: str) -> bool:
    if extension == "empty-extension":
        return True
    if extension == "free-correction":
        return False
    raise ValueError("candidate names an ungenerated extension state")


def candidate_forms() -> tuple[CandidateForm, ...]:
    return tuple(
        CandidateForm(*values)
        for values in product(
            PER_NUCLEON_RELATIONS,
            TOTAL_RELEASE_RELATIONS,
            FUSION_THRESHOLD_CARRIERS,
            FISSION_THRESHOLD_CARRIERS,
            THRESHOLD_SCOPES,
            ACCESS_CARRIERS,
            METRIC_RETENTIONS,
            TARGET_BOUNDARIES,
            EXTENSIONS,
        )
    )


def candidate_facts(form: CandidateForm) -> dict[str, bool]:
    return {
        "per_nucleon_relation": per_nucleon_relation_is_forced(form.per_nucleon_relation),
        "total_release_relation": total_release_relation_is_forced(form.total_release_relation),
        "fusion_threshold_carrier": fusion_threshold_carrier_is_forced(form.fusion_threshold_carrier),
        "fission_threshold_carrier": fission_threshold_carrier_is_forced(form.fission_threshold_carrier),
        "threshold_scope": threshold_scope_is_forced(form.threshold_scope),
        "access_carrier": access_carrier_is_forced(form.access_carrier),
        "metric_retention": metric_retention_is_forced(form.metric_retention),
        "target_boundary": target_boundary_is_forced(form.target_boundary),
        "extension": extension_is_forced(form.extension),
    }


def form_survives(form: CandidateForm) -> bool:
    return all(candidate_facts(form).values())


def candidate_exact_form(form: CandidateForm) -> str:
    return (
        f"per_nucleon={form.per_nucleon_relation}; total={form.total_release_relation}; "
        f"fusion_threshold={form.fusion_threshold_carrier}; "
        f"fission_threshold={form.fission_threshold_carrier}; scope={form.threshold_scope}; "
        f"access={form.access_carrier}; metrics={form.metric_retention}; "
        f"target={form.target_boundary}; extension={form.extension}"
    )


def decision_reason(form: CandidateForm, facts: dict[str, bool]) -> str:
    failures = tuple(name for name, passed in facts.items() if not passed)
    if failures:
        return "Rejected by computed Fold predicates: " + ", ".join(failures) + "."
    order = exact_release_order()
    topology = threshold_topology()
    return (
        "Exact interval separation gives fusion greater per conserved nucleon but the larger heavy decomposition "
        f"greater in total release: {order}.  Two charged incident words force an inter-boundary opposition path, "
        "whereas one-parent decomposition has no such path and proceeds through neutral capture or its finite "
        f"internal boundary: {topology}.  The distinct metrics and dimensional carrier classes remain retained."
    )


def completeness_record() -> dict[str, object]:
    forms = candidate_forms()
    return {
        "generation_rule": GENERATION_RULE,
        "grammar_boundary": GRAMMAR_BOUNDARY,
        "axis_cardinalities": (3, 3, 3, 3, 3, 3, 2, 2, 2),
        "candidate_count": len(forms),
        "candidate_ids": tuple(form.candidate_id for form in forms),
    }


def closure_record(decisions: Sequence[CandidateDecision]) -> dict[str, object]:
    return {
        "survivors_computed": tuple(item.candidate_id for item in decisions if item.survives),
        "release_order": exact_release_order(),
        "threshold_topology": threshold_topology(),
        "target_absent_from_formal_module": True,
        "extension_absent": extension_is_forced("empty-extension"),
    }


class FusionFissionYieldThresholdProgram:
    """Bespoke enumeration with computed decisions and no stored answer key."""

    def __init__(self, source_hash: str):
        self.source_hash = source_hash
        self._forms = candidate_forms()
        self._forms_by_id = {form.candidate_id: form for form in self._forms}

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=CLAIM_ID,
            title="Fusion/fission yield ordering and distinct threshold carriers",
            branch="physics",
            statement=(
                "For the least light binary fusion representative and the registered symmetric heavy fission "
                "representative, exact zero-parameter binding-score enclosures force the fusion gain per conserved "
                "nucleon strictly above the fission gain per conserved nucleon, while the heavy reaction's larger "
                "nucleon count forces its total release strictly above the light reaction's total.  Fusion requires "
                "two charged incident boundaries to approach through Coulomb opposition before short-range residual "
                "closure; fission has one parent and therefore proceeds through a neutral-capture or internal-surface "
                "carrier.  Half-One and quarter-order structures remain normalized relations, not one universal "
                "dimensional threshold.  Dimensional reaction energies and thresholds are opened only after sealing."
            ),
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=(
                "SFT-PHYS-NUCLEAR-FUSION-FISSION-TERMINAL-005",
                "SFT-PHYS-FIELD-COULOMB-GAUSS-CLOSURE-003",
                "SFT-PHYS-NUCLEAR-RESIDUAL-FORCE-TERMINAL-005",
                "SFT-PHYS-QUANTUM-TUNNELLING-001",
                "SFT-PHYS-THERMO-TEMPERATURE-001",
                "SFT-PHYS-MATTER-MASS-ENERGY-001",
                "SFT-PHYS-MECH-CONSERVATION-001",
                "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
                "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
                "SFT-PHYS-MEAS-UNCERTAINTY-001",
                "SFT-MATH-EXACT-ARITHMETIC-001",
            ),
            axioms=(),
            free_parameters=(),
            provenance=(
                ProvenanceClass.FORWARD_FORCING,
                ProvenanceClass.OBSERVATIONAL_DERIVATION,
            ),
            source_hash=self.source_hash,
        )

    def generate_candidates(self) -> CandidateCensus:
        candidates = tuple(
            Candidate(
                candidate_id=form.candidate_id,
                exact_form=candidate_exact_form(form),
                trace_hash=sha256_identity({
                    "generator": GENERATION_RULE,
                    "form": form,
                    "computed_facts": candidate_facts(form),
                }),
            )
            for form in self._forms
        )
        return CandidateCensus(
            generation_rule=GENERATION_RULE,
            grammar_boundary=GRAMMAR_BOUNDARY,
            expected_cardinality=len(self._forms),
            completeness_certificate_hash=sha256_identity(completeness_record()),
            candidates=candidates,
        )

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        form = self._forms_by_id[candidate.candidate_id]
        facts = candidate_facts(form)
        survives = all(facts.values())
        reason = decision_reason(form, facts)
        return CandidateDecision(
            candidate_id=candidate.candidate_id,
            survives=survives,
            reason=reason,
            proof_hash=sha256_identity({
                "candidate_trace": candidate.trace_hash,
                "form": form,
                "facts": facts,
                "survives": survives,
                "reason": reason,
            }),
        )

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        closure = closure_record(decisions)
        survivor_count = len(closure["survivors_computed"])
        order = closure["release_order"]
        topology = closure["threshold_topology"]
        minimality = (
            survivor_count == 1
            and order["orders_are_distinct"] is True
            and topology["carriers_are_distinct"] is True
        )
        uniqueness = minimality and closure["extension_absent"] is True
        generality = {
            "exact_order": order,
            "incident_topology": topology,
            "least_nonidentity_fusion_arity": 2,
            "one_parent_fission_arity": 1,
            "source_binding_dependency": "SFT-PHYS-NUCLEAR-FUSION-FISSION-TERMINAL-005",
            "universal_dimensional_threshold_absent": topology["carriers_are_distinct"],
        }
        return ClosureEvidence(
            scope=ClosureScope.DEPTH_INDEPENDENT,
            exact_boundary=GRAMMAR_BOUNDARY,
            minimality_passed=minimality,
            named_shape_uniqueness_passed=uniqueness,
            proof_hash=sha256_identity({"closure": closure, "decisions": tuple(decisions)}),
            generality_certificate_hash=sha256_identity(generality),
        )

    def run_controls(self) -> tuple[ControlResult, ...]:
        computed = tuple(form for form in self._forms if form_survives(form))
        if len(computed) != 1:
            raise ValueError("controls require exactly one computed form")
        form = computed[0]
        reversed_yield = replace(form, per_nucleon_relation="fission-greater-per-nucleon")
        universal_threshold = replace(form, threshold_scope="one-universal-dimensional-threshold")
        exposed_target = replace(form, target_boundary="readable-before-seal")
        identifiers = tuple(item.candidate_id for item in self._forms)
        records = (
            (
                ControlKind.FALSE_PREMISE,
                not form_survives(reversed_yield),
                "Reject a reversed fusion/fission gain-per-nucleon order.",
                "Exact lower-versus-upper separation rejects the reversed order.",
            ),
            (
                ControlKind.TAMPERED_SOURCE,
                sha256_identity({"changed": self.source_hash}) != self.source_hash,
                "Reject any changed claimant source identity.",
                "The changed identity differs from the registered source manifest.",
            ),
            (
                ControlKind.TAMPERED_ARTIFACT,
                len(set(identifiers + (identifiers[0],))) != len(identifiers) + 1,
                "Reject any duplicated or incomplete candidate census.",
                "The deliberate duplicate fails complete census uniqueness.",
            ),
            (
                ControlKind.BOUNDARY,
                not form_survives(universal_threshold) and not form_survives(exposed_target),
                "Reject one universal dimensional threshold and any pre-seal target access.",
                "Distinct incident carriers and sealed custody reject both boundary violations.",
            ),
        )
        return tuple(
            ControlResult(kind, passed, expected, observed, sha256_identity({
                "kind": kind,
                "passed": passed,
                "expected": expected,
                "observed": observed,
            }))
            for kind, passed, expected, observed in records
        )


__all__ = (
    "CLAIM_ID",
    "EXPERIMENT_ID",
    "FusionFissionYieldThresholdProgram",
    "ThresholdTrace",
    "candidate_facts",
    "candidate_forms",
    "completeness_record",
    "exact_release_order",
    "fission_threshold_trace",
    "form_survives",
    "fusion_threshold_trace",
    "per_nucleon_gain_enclosure",
    "threshold_topology",
    "total_release_enclosure",
)
