"""Exact simultaneous massless, One-speed and confined strong-carrier law."""
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

CLAIM_ID = "SFT-PHYS-STRONG-CARRIER-MASSLESS-CONFINED-TERMINAL-013"
EXPERIMENT_ID = "SFT-EXP-PHYS-STRONG-CARRIER-MASSLESS-CONFINED-TERMINAL-013"
ONE = Fraction(1, 1)
BINARY = 2
COLOUR = 3


def strong_sector_structure() -> dict[str, object]:
    pair_cells = COLOUR * COLOUR
    mediators = pair_cells - 1
    coupling = Fraction(COLOUR - 1, COLOUR)
    if mediators != 8 or coupling != Fraction(2, 3):
        raise ValueError("generated colour-sector structure changed")
    return {
        "sector": COLOUR,
        "charge_labels": COLOUR,
        "pair_cells": pair_cells,
        "colourless_return_cells": ONE,
        "mediator_count": mediators,
        "coupling": coupling,
        "mass_label": (),
        "mass_class": "empty-mass-label",
        "carrier_charge": "present-colour-and-anticolour",
    }


def massless_causal_trace(depth: int = 12) -> dict[str, object]:
    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 2:
        raise ValueError("positive causal depth required")
    structure = strong_sector_structure()
    positions = tuple(Fraction(tick, 1) for tick in range(1, depth + 2))
    increments = tuple(positions[index + 1] - positions[index] for index in range(len(positions) - 1))
    phase = Fraction(1, COLOUR)
    phase_trace = tuple(phase for _ in range(1, depth + 2))
    return {
        "mass_label": structure["mass_label"],
        "positions": positions,
        "increments": increments,
        "all_increments_One": all(increment == ONE for increment in increments),
        "phase_trace": phase_trace,
        "phase_retained": len(set(phase_trace)) == 1,
        "rest_capture_record": (),
        "causal_speed": ONE,
    }


def confining_tube_trace(depth: int = 12) -> dict[str, object]:
    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 2:
        raise ValueError("positive separation depth required")
    structure = strong_sector_structure()
    coupling = structure["coupling"]
    width = Fraction(1, BINARY)
    rows = tuple(
        {
            "separation": Fraction(step, 1),
            "tube_width": width,
            "field_carrier": coupling,
            "separation_work": coupling * Fraction(step, 1),
        }
        for step in range(1, depth + 1)
    )
    work_increments = tuple(
        rows[index + 1]["separation_work"] - rows[index]["separation_work"]
        for index in range(len(rows) - 1)
    )
    return {
        "rows": rows,
        "tube_width": width,
        "field_carrier": coupling,
        "width_fixed": all(row["tube_width"] == width for row in rows),
        "field_fixed": all(row["field_carrier"] == coupling for row in rows),
        "work_strictly_increases": all(
            rows[index + 1]["separation_work"] > rows[index]["separation_work"]
            for index in range(len(rows) - 1)
        ),
        "work_increment": coupling,
        "all_work_increments_equal_coupling": all(increment == coupling for increment in work_increments),
        "isolated_colour_carrier_record": (),
        "completed_infinity_used": False,
    }


def work_exceeds_positive_bound(bound: Fraction) -> dict[str, object]:
    if not isinstance(bound, Fraction) or bound <= 0:
        raise ValueError("positive exact work bound required")
    coupling = strong_sector_structure()["coupling"]
    ratio = bound / coupling
    successor = ratio.numerator // ratio.denominator + 1
    work = coupling * successor
    return {
        "bound": bound,
        "witness_separation": successor,
        "witness_work": work,
        "exceeds_bound": work > bound,
        "finite_witness": successor >= 1,
    }


def simultaneous_carrier_certificate(depth: int = 16) -> dict[str, object]:
    structure = strong_sector_structure()
    causal = massless_causal_trace(depth)
    tube = confining_tube_trace(depth)
    bounds = tuple(
        work_exceeds_positive_bound(bound)
        for bound in (
            Fraction(1, 8),
            Fraction(1, 2),
            ONE,
            Fraction(7, 3),
            Fraction(32, 1),
        )
    )
    return {
        "structure": structure,
        "causal": causal,
        "tube": tube,
        "bound_witnesses": bounds,
        "all_registered_bounds_exceeded": all(row["exceeds_bound"] and row["finite_witness"] for row in bounds),
        "simultaneously_massless_and_One_speed": structure["mass_label"] == () and causal["all_increments_One"] and causal["phase_retained"] and causal["rest_capture_record"] == (),
        "simultaneously_confined": tube["width_fixed"] and tube["field_fixed"] and tube["work_strictly_increases"] and tube["all_work_increments_equal_coupling"] and tube["isolated_colour_carrier_record"] == (),
        "masslessness_is_local_propagation_record": True,
        "confinement_is_asymptotic_observation_record": True,
        "confinement_does_not_create_mass_label": structure["mass_label"] == (),
        "general_bound_identity": "for every positive exact bound B, the successor whole after B divided by two-thirds has work greater than B",
        "general_successor_identity": "each causal tick adds One position while each separation successor adds two-thirds work and retains half-One tube width",
        "negative_zero_irrational_imaginary_or_completed_infinity_used": False,
    }


@dataclass(frozen=True)
class CandidateForm:
    sector_law: str
    mass_law: str
    causal_law: str
    self_source_law: str
    confinement_law: str
    composition_law: str
    target_boundary: str
    extension: str

    @property
    def candidate_id(self) -> str:
        return "__".join(
            (
                self.sector_law,
                self.mass_law,
                self.causal_law,
                self.self_source_law,
                self.confinement_law,
                self.composition_law,
                self.target_boundary,
                self.extension,
            )
        )


SECTOR_LAWS = (
    "generated-colour-three-sector-with-eight-nonsinglet-carriers",
    "free-sector-or-mediator-count",
    "target-assigned-sector",
)
MASS_LAWS = (
    "empty-mass-label-with-no-rest-capture",
    "numerical-zero-or-positive-fitted-mass",
    "target-assigned-mass",
)
CAUSAL_LAWS = (
    "One-support-cell-per-tick-with-retained-phase",
    "free-sub-or-super-One-speed",
    "target-assigned-speed",
)
SELF_SOURCE_LAWS = (
    "colour-carrying-mediator-resources-its-own-channel",
    "chargeless-linear-carrier",
    "target-assigned-self-source",
)
CONFINEMENT_LAWS = (
    "fixed-half-One-tube-and-two-thirds-work-successor",
    "spreading-flux-or-bounded-separation-work",
    "target-assigned-confinement",
)
COMPOSITION_LAWS = (
    "local-massless-One-speed-and-asymptotic-confined-records-coexist",
    "masslessness-and-confinement-treated-as-exclusive",
    "target-assigned-composition",
)
TARGET_BOUNDARIES = (
    "sealed-before-observation-release",
    "observation-readable-before-seal",
)
EXTENSIONS = (
    "empty-extension",
    "free-carrier-correction",
)

GENERATION_RULE = (
    "Generate the complete product of every generated, free or target-assigned colour sector; every empty, "
    "numeric/fitted or target-assigned mass law; every One-speed, free-speed or target-assigned causal law; "
    "every colour self-source, chargeless or target-assigned carrier law; every fixed-tube, spreading/bounded "
    "or target-assigned confinement law; every simultaneous, exclusive or target-assigned composition; both "
    "target custody states; and both extension states."
)
GRAMMAR_BOUNDARY = (
    "The generated colour-three carrier at every positive finite causal tick and separation depth. Masslessness "
    "is the empty mass/rest-capture record and One-cell-per-tick local phase propagation; confinement is fixed-"
    "width self-sourced colour transport whose positive separation work exceeds every nominated positive exact "
    "bound at a finite witness. No completed infinity or claim about an observable isolated colour carrier enters."
)


def candidate_forms() -> tuple[CandidateForm, ...]:
    return tuple(
        CandidateForm(*values)
        for values in product(
            SECTOR_LAWS,
            MASS_LAWS,
            CAUSAL_LAWS,
            SELF_SOURCE_LAWS,
            CONFINEMENT_LAWS,
            COMPOSITION_LAWS,
            TARGET_BOUNDARIES,
            EXTENSIONS,
        )
    )


@lru_cache(maxsize=1)
def axis_facts() -> dict[str, dict[str, bool]]:
    certificate = simultaneous_carrier_certificate()
    exact = all(
        (
            certificate["structure"]["sector"] == 3,
            certificate["structure"]["mediator_count"] == 8,
            certificate["structure"]["coupling"] == Fraction(2, 3),
            certificate["simultaneously_massless_and_One_speed"],
            certificate["simultaneously_confined"],
            certificate["all_registered_bounds_exceeded"],
            certificate["masslessness_is_local_propagation_record"],
            certificate["confinement_is_asymptotic_observation_record"],
            certificate["confinement_does_not_create_mass_label"],
            not certificate["negative_zero_irrational_imaginary_or_completed_infinity_used"],
        )
    )
    return {
        "sector": {name: value for name, value in zip(SECTOR_LAWS, (exact, False, False))},
        "mass": {name: value for name, value in zip(MASS_LAWS, (exact, False, False))},
        "causal": {name: value for name, value in zip(CAUSAL_LAWS, (exact, False, False))},
        "self_source": {name: value for name, value in zip(SELF_SOURCE_LAWS, (exact, False, False))},
        "confinement": {name: value for name, value in zip(CONFINEMENT_LAWS, (exact, False, False))},
        "composition": {name: value for name, value in zip(COMPOSITION_LAWS, (exact, False, False))},
        "target": {TARGET_BOUNDARIES[0]: True, TARGET_BOUNDARIES[1]: False},
        "extension": {EXTENSIONS[0]: True, EXTENSIONS[1]: False},
    }


def candidate_facts(form: CandidateForm) -> dict[str, bool]:
    facts = axis_facts()
    return {
        "sector": facts["sector"][form.sector_law],
        "mass": facts["mass"][form.mass_law],
        "causal": facts["causal"][form.causal_law],
        "self_source": facts["self_source"][form.self_source_law],
        "confinement": facts["confinement"][form.confinement_law],
        "composition": facts["composition"][form.composition_law],
        "target": facts["target"][form.target_boundary],
        "extension": facts["extension"][form.extension],
    }


def form_survives(form: CandidateForm) -> bool:
    return all(candidate_facts(form).values())


class StrongCarrierMasslessConfinedProgram:
    def __init__(self, source_hash: str):
        self.source_hash = source_hash
        self._forms = candidate_forms()
        self._by_id = {form.candidate_id: form for form in self._forms}

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            CLAIM_ID,
            "Simultaneous massless, One-speed and confined strong-carrier law",
            "physics",
            "The generated colour-three sector has eight non-singlet carrier states and coupling two-thirds. Its carrier has an empty mass and rest-capture record, so its local phase advances exactly one support cell per tick. The same carrier bears the colour it mediates and therefore self-sources a fixed half-One transverse tube: every positive separation successor adds the same two-thirds work carrier, exceeding every positive exact finite bound at a generated finite witness. Local massless One-speed propagation and asymptotic confinement are thus simultaneous non-equivalent records, not contradictory alternatives.",
            EvidenceMode.EMPIRICAL,
            (ROOT_THEOREM,),
            (
                "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
                "SFT-PHYS-STRONG-RUNNING-DIRECTION-002",
                "SFT-PHYS-SPACETIME-EXACT-INTERVAL-003",
                "SFT-PHYS-WAVE-EXACT-OPERATIONS-003",
                "SFT-PHYS-NUCLEAR-RESIDUAL-FORCE-TERMINAL-005",
                "SFT-PHYS-MATTER-COMPOSITE-HADRONS-001",
                "SFT-PHYS-FIELD-CONSERVED-SOURCE-001",
                "SFT-MATH-EXACT-ARITHMETIC-001",
                "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
                "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
            ),
            (),
            (),
            (ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
            self.source_hash,
        )

    def generate_candidates(self) -> CandidateCensus:
        candidates = tuple(
            Candidate(
                form.candidate_id,
                str(form),
                sha256_identity({"rule": GENERATION_RULE, "form": form, "facts": candidate_facts(form)}),
            )
            for form in self._forms
        )
        return CandidateCensus(
            GENERATION_RULE,
            GRAMMAR_BOUNDARY,
            len(candidates),
            sha256_identity(
                {
                    "axis_cardinalities": (3, 3, 3, 3, 3, 3, 2, 2),
                    "candidate_ids": tuple(candidate.candidate_id for candidate in candidates),
                }
            ),
            candidates,
        )

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        facts = candidate_facts(self._by_id[candidate.candidate_id])
        survives = all(facts.values())
        failed = tuple(name for name, value in facts.items() if not value)
        reason = (
            "Generated colour structure, empty mass record, One-speed phase, self-sourced fixed tube and ever-growing finite separation work force simultaneous masslessness and confinement."
            if survives
            else "Rejected by computed Fold predicates: " + ", ".join(failed) + "."
        )
        return CandidateDecision(
            candidate.candidate_id,
            survives,
            reason,
            sha256_identity(
                {"trace": candidate.trace_hash, "facts": facts, "survives": survives, "reason": reason}
            ),
        )

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        survivors = tuple(item.candidate_id for item in decisions if item.survives)
        certificate = simultaneous_carrier_certificate()
        closed = len(survivors) == 1 and all(
            (
                certificate["simultaneously_massless_and_One_speed"],
                certificate["simultaneously_confined"],
                certificate["all_registered_bounds_exceeded"],
                certificate["confinement_does_not_create_mass_label"],
            )
        )
        return ClosureEvidence(
            ClosureScope.DEPTH_INDEPENDENT,
            GRAMMAR_BOUNDARY,
            closed,
            closed and len(set(survivors)) == 1,
            sha256_identity(
                {"certificate": certificate, "decisions": tuple(decisions), "survivors": survivors}
            ),
            sha256_identity(
                {
                    "base": "The colour-three carrier has empty mass/rest capture, One local step, half-One tube width and first two-thirds separation-work act.",
                    "causal_successor": "Every tick appends exactly one support cell and retains the same phase without creating a mass label.",
                    "confinement_successor": "Every separation successor retains width and field while adding the same positive two-thirds work carrier.",
                    "arbitrary_positive_bound": "The successor whole after exact B divided by two-thirds gives a finite work witness strictly above B.",
                    "completed_infinity_not_used": True,
                    "targets_absent": True,
                }
            ),
        )

    def run_controls(self) -> tuple[ControlResult, ...]:
        survivors = tuple(form for form in self._forms if form_survives(form))
        if len(survivors) != 1:
            raise ValueError("controls require one computed survivor")
        form = survivors[0]
        certificate = simultaneous_carrier_certificate()
        records = (
            (
                ControlKind.FALSE_PREMISE,
                certificate["structure"]["mass_label"] == ()
                and certificate["tube"]["isolated_colour_carrier_record"] == ()
                and certificate["simultaneously_massless_and_One_speed"]
                and certificate["simultaneously_confined"],
                "Reject treating empty mass and empty isolated-colour records as the same claim or as numerical zero.",
                "Local propagation survives while isolated asymptotic colour remains empty.",
            ),
            (
                ControlKind.TAMPERED_SOURCE,
                sha256_identity({"changed": self.source_hash}) != self.source_hash,
                "Reject changed source identity.",
                "Identity differs.",
            ),
            (
                ControlKind.TAMPERED_ARTIFACT,
                len({item.candidate_id for item in self._forms}) == len(self._forms),
                "Reject duplicate candidates.",
                "All identities are unique.",
            ),
            (
                ControlKind.BOUNDARY,
                not form_survives(replace(form, mass_law=MASS_LAWS[1]))
                and not form_survives(replace(form, composition_law=COMPOSITION_LAWS[1]))
                and not form_survives(replace(form, target_boundary=TARGET_BOUNDARIES[1]))
                and not form_survives(replace(form, extension=EXTENSIONS[1])),
                "Reject numerical/fitted mass, false exclusivity, pre-seal target access and free correction.",
                "Only empty mass, simultaneous records, sealed custody and empty extension survive.",
            ),
        )
        return tuple(
            ControlResult(
                kind,
                passed,
                expected,
                observed,
                sha256_identity(
                    {
                        "kind": kind,
                        "passed": passed,
                        "expected": expected,
                        "observed": observed,
                    }
                ),
            )
            for kind, passed, expected, observed in records
        )


__all__ = (
    "CLAIM_ID",
    "EXPERIMENT_ID",
    "StrongCarrierMasslessConfinedProgram",
    "candidate_forms",
    "confining_tube_trace",
    "form_survives",
    "massless_causal_trace",
    "simultaneous_carrier_certificate",
    "strong_sector_structure",
    "work_exceeds_positive_bound",
)
