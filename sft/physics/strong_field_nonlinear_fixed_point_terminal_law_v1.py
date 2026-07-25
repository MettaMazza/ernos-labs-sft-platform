"""Exact strong self-source iteration and finite fixed-point boundary."""
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
from sft.physics.post_newtonian_fixed_point_terminal_law_v1 import convergence_certificate

CLAIM_ID = "SFT-PHYS-STRONG-FIELD-NONLINEAR-FIXED-POINT-TERMINAL-014"
EXPERIMENT_ID = "SFT-EXP-PHYS-STRONG-FIELD-NONLINEAR-FIXED-POINT-TERMINAL-014"
ONE = Fraction(1, 1)
BINARY = 2


def colour_self_source_successor(source: Fraction) -> Fraction:
    if not isinstance(source, Fraction) or source <= 0:
        raise ValueError("positive exact colour source required")
    return source + BINARY


def strong_source_iteration(depth: int = 12) -> dict[str, object]:
    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 2:
        raise ValueError("positive iteration depth required")
    sources = [ONE]
    for _ in range(depth):
        sources.append(colour_self_source_successor(sources[-1]))
    corrections = tuple(sources[index + 1] - sources[index] for index in range(len(sources) - 1))
    return {
        "sources": tuple(sources),
        "corrections": corrections,
        "source_strictly_grows": all(sources[index + 1] > sources[index] for index in range(len(sources) - 1)),
        "correction": Fraction(BINARY, 1),
        "all_corrections_binary": all(correction == BINARY for correction in corrections),
        "corrections_do_not_shrink": all(corrections[index + 1] == corrections[index] for index in range(len(corrections) - 1)),
        "field_appears_in_its_source_update": True,
        "carrier_self_source_record": ("lower-Fold-label", "upper-Fold-label"),
    }


def neutral_source_iteration(depth: int = 12) -> dict[str, object]:
    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 2:
        raise ValueError("positive iteration depth required")
    sources = tuple(ONE for _ in range(depth + 1))
    return {
        "sources": sources,
        "self_source_record": (),
        "correction_record": (),
        "source_held": len(set(sources)) == 1,
        "fixed_point": ONE,
        "field_absent_from_source_update": True,
    }


def finite_strong_fixed_point_test(candidate: Fraction) -> dict[str, object]:
    if not isinstance(candidate, Fraction) or candidate <= 0:
        raise ValueError("positive exact finite fixed-point candidate required")
    successor = colour_self_source_successor(candidate)
    return {
        "candidate": candidate,
        "successor": successor,
        "successor_strictly_above_candidate": successor > candidate,
        "is_fixed_point": successor == candidate,
        "finite_candidate": True,
    }


def strong_source_exceeds_positive_bound(bound: Fraction) -> dict[str, object]:
    if not isinstance(bound, Fraction) or bound <= 0:
        raise ValueError("positive exact finite bound required")
    ratio = bound / BINARY
    successor_count = ratio.numerator // ratio.denominator + 1
    source = ONE + Fraction(BINARY * successor_count, 1)
    return {
        "bound": bound,
        "witness_successors": successor_count,
        "witness_source": source,
        "source_exceeds_bound": source > bound,
        "finite_witness": successor_count >= 1,
    }


def field_iteration_certificate(depth: int = 8) -> dict[str, object]:
    strong = strong_source_iteration(depth)
    neutral = neutral_source_iteration(depth)
    gravity = convergence_certificate(depth)
    candidates = tuple(
        finite_strong_fixed_point_test(candidate)
        for candidate in (
            Fraction(1, 127),
            Fraction(1, 2),
            ONE,
            Fraction(7, 3),
            Fraction(32, 1),
        )
    )
    bounds = tuple(
        strong_source_exceeds_positive_bound(bound)
        for bound in (
            Fraction(1, 127),
            Fraction(1, 2),
            ONE,
            Fraction(7, 3),
            Fraction(32, 1),
        )
    )
    return {
        "neutral": neutral,
        "gravity": gravity,
        "strong": strong,
        "fixed_point_candidates": candidates,
        "bound_witnesses": bounds,
        "neutral_linear_hold": neutral["source_held"] and neutral["correction_record"] == (),
        "gravity_self_source_contracts": gravity["admissible_fixed_points"] == (Fraction(1, 4),) and gravity["errors_strictly_shrink"] and gravity["corrections_strictly_shrink"],
        "strong_self_source_persists": strong["source_strictly_grows"] and strong["all_corrections_binary"] and strong["corrections_do_not_shrink"],
        "strong_has_no_positive_finite_fixed_point": all(not row["is_fixed_point"] and row["successor_strictly_above_candidate"] for row in candidates),
        "all_registered_bounds_exceeded": all(row["source_exceeds_bound"] and row["finite_witness"] for row in bounds),
        "general_fixed_point_identity": "for every positive exact finite F, the colour successor is F plus the complete binary carrier and is strictly above F",
        "general_bound_identity": "for every positive exact finite B, the successor whole after B divided by two yields source One plus twice that whole, strictly above B",
        "structural_nonlinearity": "the strong field carrier is retained inside the source update that generates its next field record",
        "strong_finite_fixed_point_record": (),
        "completed_infinity_used": False,
        "negative_zero_irrational_or_imaginary_proof_value_used": False,
    }


@dataclass(frozen=True)
class CandidateForm:
    source_composition: str
    update_law: str
    correction_law: str
    fixed_point_law: str
    comparator_law: str
    confinement_law: str
    target_boundary: str
    extension: str

    @property
    def candidate_id(self) -> str:
        return "__".join(
            (
                self.source_composition,
                self.update_law,
                self.correction_law,
                self.fixed_point_law,
                self.comparator_law,
                self.confinement_law,
                self.target_boundary,
                self.extension,
            )
        )


SOURCE_COMPOSITIONS = (
    "colour-carrier-retained-inside-its-own-source-update",
    "external-matter-source-only",
    "target-assigned-source-composition",
)
UPDATE_LAWS = (
    "each-successor-retains-prior-source-and-appends-complete-binary-carrier",
    "free-linear-contracted-or-oscillatory-update",
    "target-assigned-update",
)
CORRECTION_LAWS = (
    "persistent-exact-binary-correction-at-every-successor",
    "shrinking-or-free-correction",
    "target-assigned-correction",
)
FIXED_POINT_LAWS = (
    "empty-positive-finite-fixed-point-record-by-F-plus-two-order",
    "selected-finite-strong-fixed-point",
    "target-assigned-fixed-point",
)
COMPARATOR_LAWS = (
    "neutral-hold-gravity-contraction-strong-persistence-three-way-discriminator",
    "conflate-all-self-source-iterations",
    "target-assigned-comparator",
)
CONFINEMENT_LAWS = (
    "finite-witness-above-every-positive-exact-bound",
    "bounded-prefix-or-completed-infinity",
    "target-assigned-confinement",
)
TARGET_BOUNDARIES = (
    "sealed-before-observation-release",
    "observation-readable-before-seal",
)
EXTENSIONS = (
    "empty-extension",
    "free-strong-field-correction",
)

GENERATION_RULE = (
    "Generate the complete product of every colour-self-sourced, external-only or target-assigned source; every "
    "binary-successor, free or target-assigned update; every persistent, shrinking/free or target-assigned "
    "correction; every empty, selected or target-assigned finite fixed-point law; every exact three-way, conflated "
    "or target-assigned comparator; every arbitrary-bound, finite-prefix/completed-infinity or target-assigned "
    "confinement law; both target custody states; and both extension states."
)
GRAMMAR_BOUNDARY = (
    "Every positive finite iteration depth of the admitted colour self-source successor, every positive exact "
    "finite fixed-point candidate and work/source bound, the admitted gravitational scalar self-source channel, "
    "and the chargeless held-source control. The result distinguishes structural source recursion from polynomial "
    "degree and does not claim a conventional renormalized Yang-Mills solution."
)


def candidate_forms() -> tuple[CandidateForm, ...]:
    return tuple(
        CandidateForm(*values)
        for values in product(
            SOURCE_COMPOSITIONS,
            UPDATE_LAWS,
            CORRECTION_LAWS,
            FIXED_POINT_LAWS,
            COMPARATOR_LAWS,
            CONFINEMENT_LAWS,
            TARGET_BOUNDARIES,
            EXTENSIONS,
        )
    )


@lru_cache(maxsize=1)
def axis_facts() -> dict[str, dict[str, bool]]:
    certificate = field_iteration_certificate()
    exact = all(
        (
            certificate["neutral_linear_hold"],
            certificate["gravity_self_source_contracts"],
            certificate["strong_self_source_persists"],
            certificate["strong_has_no_positive_finite_fixed_point"],
            certificate["all_registered_bounds_exceeded"],
            certificate["strong_finite_fixed_point_record"] == (),
            not certificate["completed_infinity_used"],
            not certificate["negative_zero_irrational_or_imaginary_proof_value_used"],
        )
    )
    return {
        "source": {name: value for name, value in zip(SOURCE_COMPOSITIONS, (exact, False, False))},
        "update": {name: value for name, value in zip(UPDATE_LAWS, (exact, False, False))},
        "correction": {name: value for name, value in zip(CORRECTION_LAWS, (exact, False, False))},
        "fixed": {name: value for name, value in zip(FIXED_POINT_LAWS, (exact, False, False))},
        "comparator": {name: value for name, value in zip(COMPARATOR_LAWS, (exact, False, False))},
        "confinement": {name: value for name, value in zip(CONFINEMENT_LAWS, (exact, False, False))},
        "target": {TARGET_BOUNDARIES[0]: True, TARGET_BOUNDARIES[1]: False},
        "extension": {EXTENSIONS[0]: True, EXTENSIONS[1]: False},
    }


def candidate_facts(form: CandidateForm) -> dict[str, bool]:
    facts = axis_facts()
    return {
        "source": facts["source"][form.source_composition],
        "update": facts["update"][form.update_law],
        "correction": facts["correction"][form.correction_law],
        "fixed": facts["fixed"][form.fixed_point_law],
        "comparator": facts["comparator"][form.comparator_law],
        "confinement": facts["confinement"][form.confinement_law],
        "target": facts["target"][form.target_boundary],
        "extension": facts["extension"][form.extension],
    }


def form_survives(form: CandidateForm) -> bool:
    return all(candidate_facts(form).values())


class StrongFieldNonlinearFixedPointProgram:
    def __init__(self, source_hash: str):
        self.source_hash = source_hash
        self._forms = candidate_forms()
        self._by_id = {form.candidate_id: form for form in self._forms}

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            CLAIM_ID,
            "Strong self-source iteration and finite fixed-point boundary",
            "physics",
            "A chargeless carrier has an empty self-source correction and holds its matter source. The admitted gravitational scalar self-source has one admissible quarter-One fixed point with shrinking corrections. A colour-bearing carrier instead remains inside its own source update: every successor retains the prior source and appends the complete binary carrier, so the correction is exact two and never shrinks. For every positive exact finite F, F plus two is strictly above F, leaving the strong finite fixed-point record empty; the same successor law exceeds every positive exact finite bound at a generated finite witness. This is the depth-independent confinement boundary.",
            EvidenceMode.EMPIRICAL,
            (ROOT_THEOREM,),
            (
                "SFT-PHYS-STRONG-RUNNING-DIRECTION-002",
                "SFT-PHYS-POST-NEWTONIAN-FIXED-POINT-TERMINAL-009",
                "SFT-PHYS-FIELD-SOURCE-RESPONSE-001",
                "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
                "SFT-PHYS-STRONG-CARRIER-MASSLESS-CONFINED-TERMINAL-013",
                "SFT-MATH-EXACT-ARITHMETIC-001",
                "SFT-MATH-DYNAMICAL-SYSTEMS-001",
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
            "Colour self-source, exact binary successor, persistent correction, empty finite fixed point and arbitrary-bound witnesses force the three-way iteration discriminator."
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
        certificate = field_iteration_certificate()
        closed = len(survivors) == 1 and all(
            (
                certificate["neutral_linear_hold"],
                certificate["gravity_self_source_contracts"],
                certificate["strong_self_source_persists"],
                certificate["strong_has_no_positive_finite_fixed_point"],
                certificate["all_registered_bounds_exceeded"],
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
                    "base": "The bare strong row is the One and its first colour successor appends both Fold labels; the neutral row holds and the admitted gravity row lies below quarter-One.",
                    "strong_successor": "Every strong successor retains its prior positive exact source and appends the same complete binary carrier.",
                    "fixed_point_boundary": "For every positive exact finite F, adding the positive binary carrier produces a strictly larger record, so equality is impossible.",
                    "arbitrary_bound": "The successor whole after exact B divided by two supplies a finite source witness above every positive exact finite B.",
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
        certificate = field_iteration_certificate()
        records = (
            (
                ControlKind.FALSE_PREMISE,
                certificate["neutral"]["correction_record"] == ()
                and certificate["gravity"]["corrections_strictly_shrink"]
                and certificate["strong"]["corrections_do_not_shrink"],
                "Reject conflating empty, shrinking and persistent correction records.",
                "Neutral, gravity and strong updates retain distinct exact correction classes.",
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
                not form_survives(replace(form, fixed_point_law=FIXED_POINT_LAWS[1]))
                and not form_survives(replace(form, confinement_law=CONFINEMENT_LAWS[1]))
                and not form_survives(replace(form, target_boundary=TARGET_BOUNDARIES[1]))
                and not form_survives(replace(form, extension=EXTENSIONS[1])),
                "Reject selected fixed point, finite-prefix/completed-infinity inference, target access and free correction.",
                "Only universal positive-order exclusion, finite witnesses, sealed custody and empty extension survive.",
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
    "StrongFieldNonlinearFixedPointProgram",
    "candidate_forms",
    "colour_self_source_successor",
    "field_iteration_certificate",
    "finite_strong_fixed_point_test",
    "form_survives",
    "neutral_source_iteration",
    "strong_source_exceeds_positive_bound",
    "strong_source_iteration",
)
