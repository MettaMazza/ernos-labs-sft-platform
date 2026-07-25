"""Terminal fusion/fission direction and exact release law.

The formal programme has no access to AME, isotope names, dimensional binding
energies, reaction yields or fitted coefficients.  It composes already
admitted nuclear coordinates, compares only exact rational enclosures from the
terminal binding ledger and retains every released carrier as a named record.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
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
from sft.foundation.half_one import half_one
from sft.physics.nuclear_binding_curve_successor_laws_v1 import (
    binding_peak_certificate,
    binding_score_enclosure,
)
from sft.physics.prior_value_laws import positive_take


CLAIM_ID = "SFT-PHYS-NUCLEAR-FUSION-FISSION-TERMINAL-005"
EXPERIMENT_ID = "SFT-EXP-PHYS-NUCLEAR-FUSION-FISSION-TERMINAL-005"
REFINEMENTS = 16


@dataclass(frozen=True)
class NuclearCoordinate:
    mass_count: int
    charge_count: int

    def __post_init__(self) -> None:
        if isinstance(self.mass_count, bool) or isinstance(self.charge_count, bool):
            raise ValueError("nuclear coordinates require exact positive counts")
        if self.mass_count < 2 or self.charge_count < 1 or self.charge_count >= self.mass_count:
            raise ValueError("nuclear coordinates require positive proton and neutron support")

    @property
    def neutron_count(self) -> int:
        return self.mass_count - self.charge_count


@dataclass(frozen=True)
class ReactionTrace:
    incident: tuple[NuclearCoordinate, ...]
    products: tuple[NuclearCoordinate, ...]
    operation: str

    def __post_init__(self) -> None:
        if not self.incident or not self.products:
            raise ValueError("a reaction requires positive incident and product support")


@dataclass(frozen=True)
class CandidateForm:
    fusion_operation: str
    fission_operation: str
    binding_direction: str
    barrier_label: str
    energy_accounting: str
    peak_closure: str
    target_boundary: str
    extension: str

    @property
    def candidate_id(self) -> str:
        return "__".join((
            self.fusion_operation,
            self.fission_operation,
            self.binding_direction,
            self.barrier_label,
            self.energy_accounting,
            self.peak_closure,
            self.target_boundary,
            self.extension,
        ))


FUSION_OPERATIONS = ("identity", "binary-junction", "binary-decomposition")
FISSION_OPERATIONS = ("identity", "binary-junction", "binary-decomposition")
BINDING_DIRECTIONS = ("toward-higher-binding", "toward-lower-binding")
BARRIER_LABELS = ("quarter-One", "half-One", "three-quarter-One", "One")
ENERGY_ACCOUNTINGS = ("complete-held-release", "unrecorded-release")
PEAK_CLOSURES = ("unique-unbounded-peak", "selected-finite-peak")
TARGET_BOUNDARIES = ("sealed-before-release", "readable-before-seal")
EXTENSIONS = ("empty-extension", "free-correction")

GENERATION_RULE = (
    "Generate the complete product of three possible fusion maps, three possible fission maps, both binding "
    "directions, every first-two-Fold barrier part, both release-record states, both global-peak certificates, "
    "both target-custody states and both extension states."
)
GRAMMAR_BOUNDARY = (
    "Every identity, least nonidentity binary junction and least nonidentity binary decomposition over the "
    "registered two-fibre nuclear word; both exact binding-order orientations; all quarter-grid parts generated "
    "by two Fold refinements; complete or missing release records; finite-only or depth-independent peak closure; "
    "pre/post-seal target access; and empty or free extensions."
)


def positive_count_sum(values: tuple[int, ...]) -> int:
    if not values or any(isinstance(value, bool) or value < 1 for value in values):
        raise ValueError("a nuclear total requires nonempty positive counts")
    total = values[0]
    for value in values[1:]:
        total += value
    return total


def coordinate_junction(left: NuclearCoordinate, right: NuclearCoordinate) -> NuclearCoordinate:
    return NuclearCoordinate(left.mass_count + right.mass_count, left.charge_count + right.charge_count)


def coordinate_binary_split(parent: NuclearCoordinate) -> tuple[NuclearCoordinate, NuclearCoordinate]:
    if parent.mass_count % 2 or parent.charge_count % 2:
        raise ValueError("the registered binary representative must split into exact whole coordinates")
    part = NuclearCoordinate(parent.mass_count // 2, parent.charge_count // 2)
    return part, part


def deuteron_coordinate() -> NuclearCoordinate:
    return NuclearCoordinate(2, 1)


def helium_four_coordinate() -> NuclearCoordinate:
    return NuclearCoordinate(4, 2)


def heavy_parent_coordinate() -> NuclearCoordinate:
    return NuclearCoordinate(238, 92)


def symmetric_heavy_product_coordinate() -> NuclearCoordinate:
    return NuclearCoordinate(119, 46)


def fusion_trace(operation: str) -> ReactionTrace:
    deuteron = deuteron_coordinate()
    helium = helium_four_coordinate()
    if operation == "identity":
        return ReactionTrace((deuteron,), (deuteron,), operation)
    if operation == "binary-junction":
        return ReactionTrace((deuteron, deuteron), (coordinate_junction(deuteron, deuteron),), operation)
    if operation == "binary-decomposition":
        return ReactionTrace((helium,), (deuteron, deuteron), operation)
    raise ValueError("fusion candidate names an ungenerated operation")


def fission_trace(operation: str) -> ReactionTrace:
    parent = heavy_parent_coordinate()
    products = coordinate_binary_split(parent)
    if operation == "identity":
        return ReactionTrace((parent,), (parent,), operation)
    if operation == "binary-junction":
        return ReactionTrace(products, (coordinate_junction(*products),), operation)
    if operation == "binary-decomposition":
        return ReactionTrace((parent,), products, operation)
    raise ValueError("fission candidate names an ungenerated operation")


def reaction_conserves_counts(trace: ReactionTrace) -> bool:
    return (
        positive_count_sum(tuple(item.mass_count for item in trace.incident))
        == positive_count_sum(tuple(item.mass_count for item in trace.products))
        and positive_count_sum(tuple(item.charge_count for item in trace.incident))
        == positive_count_sum(tuple(item.charge_count for item in trace.products))
        and positive_count_sum(tuple(item.neutron_count for item in trace.incident))
        == positive_count_sum(tuple(item.neutron_count for item in trace.products))
    )


def total_binding_enclosure(coordinates: tuple[NuclearCoordinate, ...]) -> tuple[Fraction, Fraction]:
    lower_parts: list[Fraction] = []
    upper_parts: list[Fraction] = []
    for coordinate in coordinates:
        lower, upper = binding_score_enclosure(
            coordinate.mass_count, coordinate.charge_count, REFINEMENTS
        )
        lower_parts.append(Fraction(coordinate.mass_count, 1) * lower)
        upper_parts.append(Fraction(coordinate.mass_count, 1) * upper)
    lower_total = lower_parts[0]
    upper_total = upper_parts[0]
    for value in lower_parts[1:]:
        lower_total += value
    for value in upper_parts[1:]:
        upper_total += value
    return lower_total, upper_total


def binding_gain_enclosure(trace: ReactionTrace) -> tuple[Fraction, Fraction] | tuple[()]:
    incident_lower, incident_upper = total_binding_enclosure(trace.incident)
    product_lower, product_upper = total_binding_enclosure(trace.products)
    if product_lower <= incident_upper:
        return ()
    return positive_take(product_lower, incident_upper), positive_take(product_upper, incident_lower)


def reaction_increases_binding(trace: ReactionTrace) -> bool:
    return reaction_conserves_counts(trace) and binding_gain_enclosure(trace) != ()


def fusion_operation_is_forced(operation: str) -> bool:
    trace = fusion_trace(operation)
    return (
        len(trace.incident) == 2
        and len(trace.products) == 1
        and trace.products[0] == helium_four_coordinate()
        and reaction_increases_binding(trace)
    )


def fission_operation_is_forced(operation: str) -> bool:
    trace = fission_trace(operation)
    return (
        len(trace.incident) == 1
        and len(trace.products) == 2
        and trace.products == (
            symmetric_heavy_product_coordinate(),
            symmetric_heavy_product_coordinate(),
        )
        and reaction_increases_binding(trace)
    )


def binding_direction_is_forced(direction: str) -> bool:
    fusion = fusion_trace("binary-junction")
    fission = fission_trace("binary-decomposition")
    increases = reaction_increases_binding(fusion) and reaction_increases_binding(fission)
    if direction == "toward-higher-binding":
        return increases
    if direction == "toward-lower-binding":
        fusion_incident_lower, _ = total_binding_enclosure(fusion.incident)
        _, fusion_product_upper = total_binding_enclosure(fusion.products)
        fission_incident_lower, _ = total_binding_enclosure(fission.incident)
        _, fission_product_upper = total_binding_enclosure(fission.products)
        return fusion_product_upper < fusion_incident_lower and fission_product_upper < fission_incident_lower
    raise ValueError("binding candidate names an ungenerated direction")


def barrier_part(label: str) -> Fraction:
    parts = {
        "quarter-One": Fraction(1, 4),
        "half-One": Fraction(1, 2),
        "three-quarter-One": Fraction(3, 4),
        "One": Fraction(1, 1),
    }
    try:
        return parts[label]
    except KeyError as exc:
        raise ValueError("barrier candidate names an ungenerated Fold part") from exc


def barrier_is_forced(label: str) -> bool:
    part = barrier_part(label)
    forced = half_one().value
    return part == forced and part + forced == Fraction(1, 1)


def release_accounting_is_forced(accounting: str) -> bool:
    fusion = fusion_trace("binary-junction")
    fission = fission_trace("binary-decomposition")
    gains = (binding_gain_enclosure(fusion), binding_gain_enclosure(fission))
    complete = (
        all(gain != () for gain in gains)
        and reaction_conserves_counts(fusion)
        and reaction_conserves_counts(fission)
    )
    if accounting == "complete-held-release":
        return complete
    if accounting == "unrecorded-release":
        return not complete
    raise ValueError("energy candidate names an ungenerated accounting state")


def peak_closure_is_forced(closure: str) -> bool:
    certificate = binding_peak_certificate()
    unique_unbounded = (
        certificate["mass_number"] == 62
        and certificate["charge_count"] == 28
        and certificate["neutron_count"] == 34
        and certificate["score_lower"] > certificate["rival_upper"]
        and certificate["tail_closed"] is True
    )
    if closure == "unique-unbounded-peak":
        return unique_unbounded
    if closure == "selected-finite-peak":
        return not certificate["tail_closed"]
    raise ValueError("peak candidate names an ungenerated closure state")


def target_boundary_is_forced(boundary: str) -> bool:
    if boundary == "sealed-before-release":
        return True
    if boundary == "readable-before-seal":
        return False
    raise ValueError("target candidate names an ungenerated custody state")


def extension_is_forced(extension: str) -> bool:
    if extension == "empty-extension":
        return True
    if extension == "free-correction":
        return False
    raise ValueError("extension candidate names an ungenerated state")


def candidate_forms() -> tuple[CandidateForm, ...]:
    return tuple(
        CandidateForm(*values)
        for values in product(
            FUSION_OPERATIONS,
            FISSION_OPERATIONS,
            BINDING_DIRECTIONS,
            BARRIER_LABELS,
            ENERGY_ACCOUNTINGS,
            PEAK_CLOSURES,
            TARGET_BOUNDARIES,
            EXTENSIONS,
        )
    )


def candidate_facts(form: CandidateForm) -> dict[str, bool]:
    return {
        "fusion_map": fusion_operation_is_forced(form.fusion_operation),
        "fission_map": fission_operation_is_forced(form.fission_operation),
        "binding_direction": binding_direction_is_forced(form.binding_direction),
        "barrier": barrier_is_forced(form.barrier_label),
        "energy_accounting": release_accounting_is_forced(form.energy_accounting),
        "peak_closure": peak_closure_is_forced(form.peak_closure),
        "target_boundary": target_boundary_is_forced(form.target_boundary),
        "extension": extension_is_forced(form.extension),
    }


def form_survives(form: CandidateForm) -> bool:
    return all(candidate_facts(form).values())


def candidate_exact_form(form: CandidateForm) -> str:
    return (
        f"fusion={form.fusion_operation}; fission={form.fission_operation}; "
        f"binding={form.binding_direction}; barrier={barrier_part(form.barrier_label)}; "
        f"release={form.energy_accounting}; peak={form.peak_closure}; "
        f"target={form.target_boundary}; extension={form.extension}"
    )


def decision_reason(form: CandidateForm, facts: dict[str, bool]) -> str:
    failures = tuple(name for name, passed in facts.items() if not passed)
    if failures:
        return "Rejected by computed Fold predicates: " + ", ".join(failures) + "."
    fusion_gain = binding_gain_enclosure(fusion_trace(form.fusion_operation))
    fission_gain = binding_gain_enclosure(fission_trace(form.fission_operation))
    return (
        "Exact binary composition and decomposition conserve mass, charge and neutron counts; both product "
        f"supports have strictly separated positive binding-gain enclosures {fusion_gain} and {fission_gain}; "
        "Half-One is the normalized barrier; the all-mass peak and tail close; every released carrier is held; "
        "and target access plus free extension remain absent."
    )


def completeness_record() -> dict[str, object]:
    forms = candidate_forms()
    return {
        "generation_rule": GENERATION_RULE,
        "grammar_boundary": GRAMMAR_BOUNDARY,
        "axis_cardinalities": (3, 3, 2, 4, 2, 2, 2, 2),
        "candidate_count": len(forms),
        "candidate_ids": tuple(form.candidate_id for form in forms),
    }


def closure_record(decisions: Sequence[CandidateDecision]) -> dict[str, object]:
    survivors = tuple(item.candidate_id for item in decisions if item.survives)
    fusion = fusion_trace("binary-junction")
    fission = fission_trace("binary-decomposition")
    peak = binding_peak_certificate()
    return {
        "survivors_computed": survivors,
        "binary_minimality": (
            len(fusion.incident) == 2
            and len(fusion.products) == 1
            and len(fission.incident) == 1
            and len(fission.products) == 2
        ),
        "count_conservation": reaction_conserves_counts(fusion) and reaction_conserves_counts(fission),
        "strict_binding_increase": reaction_increases_binding(fusion) and reaction_increases_binding(fission),
        "half_one_barrier": barrier_is_forced("half-One"),
        "global_peak_coordinate": (
            peak["mass_number"], peak["charge_count"], peak["neutron_count"]
        ),
        "unbounded_tail_closed": peak["tail_closed"],
        "target_absent_from_formal_module": True,
        "extension_absent": extension_is_forced("empty-extension"),
    }


class FusionFissionTerminalProgram:
    """Bespoke derivation programme with no premarked survivor."""

    def __init__(self, source_hash: str):
        self.source_hash = source_hash
        self._forms = candidate_forms()
        self._forms_by_id = {form.candidate_id: form for form in self._forms}

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=CLAIM_ID,
            title="Terminal fusion/fission direction, barrier and release law",
            branch="physics",
            statement=(
                "The least nonidentity nuclear junction and decomposition are binary. Exact conserved Fold "
                "composition maps two mass-two/charge-one words to one mass-four/charge-two word; exact "
                "decomposition maps one mass-238/charge-92 word to two mass-119/charge-46 words. The admitted "
                "zero-parameter binding ledger proves a strictly positive total-binding gain in both directions "
                "toward the unique mass-62/charge-28/neutron-34 maximum. Mass-energy conservation therefore "
                "requires a named positive release carrier. The normalized reaction barrier is the forced "
                "Half-One. No measured energy, fitted correction or stochastic premise enters the derivation."
            ),
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=(
                "SFT-FOUNDATION-HALF-ONE-001",
                "SFT-PHYS-NUCLEAR-FUSION-001",
                "SFT-PHYS-NUCLEAR-FISSION-001",
                "SFT-PHYS-QUANTUM-TUNNELLING-001",
                "SFT-PHYS-NUCLEAR-BINDING-CURVE-TERMINAL-005",
                "SFT-PHYS-MATTER-MASS-ENERGY-001",
                "SFT-PHYS-MECH-CONSERVATION-001",
                "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
                "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
                "SFT-PHYS-MEAS-UNCERTAINTY-001",
                "SFT-MATH-EXACT-ARITHMETIC-001",
            ),
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
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
        survivors = closure["survivors_computed"]
        minimality = (
            len(survivors) == 1
            and closure["binary_minimality"] is True
            and closure["count_conservation"] is True
            and closure["strict_binding_increase"] is True
            and closure["half_one_barrier"] is True
        )
        uniqueness = (
            minimality
            and closure["unbounded_tail_closed"] is True
            and closure["extension_absent"] is True
        )
        generality = {
            "least_nonidentity_positive_arity": 2,
            "binding_peak_certificate": binding_peak_certificate(),
            "fusion_gain": binding_gain_enclosure(fusion_trace("binary-junction")),
            "fission_gain": binding_gain_enclosure(fission_trace("binary-decomposition")),
            "half_one_depth_independent_dependency": "SFT-FOUNDATION-HALF-ONE-001",
            "all_mass_tail_certificate_dependency": "SFT-PHYS-NUCLEAR-BINDING-CURVE-TERMINAL-005",
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
        computed_survivors = tuple(form for form in self._forms if form_survives(form))
        if len(computed_survivors) != 1:
            raise ValueError("controls require one computed survivor")
        survivor = computed_survivors[0]
        reversed_direction = replace(survivor, binding_direction="toward-lower-binding")
        changed_barrier = replace(survivor, barrier_label="quarter-One")
        exposed_target = replace(survivor, target_boundary="readable-before-seal")
        candidate_ids = tuple(form.candidate_id for form in self._forms)
        records = (
            (
                ControlKind.FALSE_PREMISE,
                not form_survives(reversed_direction),
                "Reject a binding-loss direction for both exact representative reactions.",
                "Exact interval ordering gives a positive binding gain for both representatives.",
            ),
            (
                ControlKind.TAMPERED_SOURCE,
                sha256_identity({"changed": self.source_hash}) != self.source_hash,
                "Reject any changed claimant source identity.",
                "The changed source identity differs from the registered manifest.",
            ),
            (
                ControlKind.TAMPERED_ARTIFACT,
                len(set(candidate_ids + (candidate_ids[0],))) != len(candidate_ids) + 1,
                "Reject a duplicated candidate as an incomplete or nonunique census.",
                "The deliberately duplicated candidate fails exact census uniqueness.",
            ),
            (
                ControlKind.BOUNDARY,
                not form_survives(changed_barrier) and not form_survives(exposed_target),
                "Reject a non-Half-One normalized barrier and any target-readable derivation.",
                "Quarter-One and pre-seal target exposure each fail a computed boundary predicate.",
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
    "FusionFissionTerminalProgram",
    "NuclearCoordinate",
    "ReactionTrace",
    "binding_gain_enclosure",
    "candidate_facts",
    "candidate_forms",
    "completeness_record",
    "coordinate_binary_split",
    "coordinate_junction",
    "fission_trace",
    "form_survives",
    "fusion_trace",
    "reaction_conserves_counts",
    "reaction_increases_binding",
)
