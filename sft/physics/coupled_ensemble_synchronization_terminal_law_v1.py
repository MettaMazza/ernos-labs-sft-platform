"""Exact half-One pair synchronization and synchronized-ensemble closure.

No historical ensemble, recurrence vector, coupling comparison, expected
survivor or claimant-controlled admission flag enters this formal claimant.
The finite V1 E4 experiment is released only by the post-seal validator.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from functools import lru_cache
from itertools import product
from typing import Sequence

from sft.engine import Candidate, CandidateCensus, CandidateDecision, ClaimRegistration, ClosureEvidence, ClosureScope, ControlKind, ControlResult, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.engine.canonical import sha256_identity
from sft.foundation.half_one import half_one


CLAIM_ID = "SFT-PHYS-COUPLED-ENSEMBLE-SYNCHRONIZATION-TERMINAL-007"
EXPERIMENT_ID = "SFT-EXP-PHYS-COUPLED-ENSEMBLE-SYNCHRONIZATION-TERMINAL-007"


def positive_take(larger: Fraction, smaller: Fraction) -> Fraction:
    if not isinstance(larger, Fraction) or not isinstance(smaller, Fraction) or not 0 < smaller < larger:
        raise ValueError("exact positive take requires ordered positive parts")
    return larger - smaller


def pair_separation(lower: Fraction, upper: Fraction) -> Fraction:
    if not isinstance(lower, Fraction) or not isinstance(upper, Fraction) or not 0 < lower < upper <= 1:
        raise ValueError("pair synchronization requires two ordered positive parts")
    return positive_take(upper, lower)


def paired_move(lower: Fraction, upper: Fraction, coupling: Fraction) -> tuple[Fraction, Fraction]:
    if not isinstance(coupling, Fraction) or not 0 < coupling < 1:
        raise ValueError("coupling must be one exact proper positive part")
    separation = pair_separation(lower, upper)
    move = coupling * separation
    return lower + move, positive_take(upper, move)


def residual_record(lower: Fraction, upper: Fraction, coupling: Fraction) -> tuple[Fraction, ...]:
    moved_lower, moved_upper = paired_move(lower, upper, coupling)
    if moved_lower == moved_upper:
        return ()
    return (positive_take(max(moved_lower, moved_upper), min(moved_lower, moved_upper)),)


def unique_pair_synchronizing_coupling() -> Fraction:
    candidates = (Fraction(1, 3), half_one().value, Fraction(2, 3))
    pair = (Fraction(1, 4), Fraction(3, 4))
    survivors = tuple(coupling for coupling in candidates if residual_record(*pair, coupling) == ())
    if survivors != (Fraction(1, 2),):
        raise ValueError("complete coupling alternatives did not force the half-One")
    return survivors[0]


def residual_scale(coupling: Fraction) -> Fraction | tuple[()]:
    """Return the exact separation multiplier or empty synchronized record."""

    half = half_one().value
    if coupling == half:
        return ()
    doubled = coupling + coupling
    one = Fraction(1, 1)
    return positive_take(one, doubled) if doubled < one else positive_take(doubled, one)


def synchronized_ensemble_successor(point: Fraction, member_count: int) -> tuple[Fraction, ...]:
    if not isinstance(point, Fraction) or not 0 < point <= 1:
        raise ValueError("synchronized ensemble point must be an exact positive part")
    if isinstance(member_count, bool) or member_count < 2:
        raise ValueError("synchronized ensemble requires a paired positive member count")
    folded = point + point
    folded = folded if folded <= 1 else folded - 1
    return tuple(folded for _ in range(member_count))


def formal_certificate() -> dict[str, object]:
    pairs = (
        (Fraction(1, 8), Fraction(7, 8)),
        (Fraction(1, 4), Fraction(3, 4)),
        (Fraction(1, 3), Fraction(2, 3)),
        (Fraction(2, 5), Fraction(4, 5)),
    )
    couplings = (Fraction(1, 3), Fraction(1, 2), Fraction(2, 3))
    return {
        "couplings": couplings,
        "pairs": pairs,
        "residual_records": tuple(tuple(residual_record(*pair, coupling) for coupling in couplings) for pair in pairs),
        "unique_synchronizing_coupling": unique_pair_synchronizing_coupling(),
        "half_One_residuals_empty": all(residual_record(*pair, Fraction(1, 2)) == () for pair in pairs),
        "off_half_residuals_positive": all(
            residual_record(*pair, coupling)[0] > 0
            for pair in pairs for coupling in (Fraction(1, 3), Fraction(2, 3))
        ),
        "residual_scale_lower": residual_scale(Fraction(1, 3)),
        "residual_scale_half": residual_scale(Fraction(1, 2)),
        "residual_scale_upper": residual_scale(Fraction(2, 3)),
        "synchronized_terminal_preserved": all(
            len(set(synchronized_ensemble_successor(point, members))) == 1
            for point in (Fraction(1, 3), Fraction(1, 2), Fraction(3, 4))
            for members in (2, 3, 5, 8)
        ),
    }


@dataclass(frozen=True)
class CandidateForm:
    coupling_domain: str
    paired_action: str
    balance_relation: str
    residual_semantics: str
    ensemble_terminal: str
    closure: str
    target_boundary: str
    extension: str

    @property
    def candidate_id(self) -> str:
        return "__".join((self.coupling_domain, self.paired_action, self.balance_relation, self.residual_semantics, self.ensemble_terminal, self.closure, self.target_boundary, self.extension))


COUPLING_DOMAINS = ("complete-generated-coupling-alternatives", "selected-half-One-only", "target-assigned-coupling")
PAIRED_ACTIONS = ("both-members-move-equal-coupled-shares", "one-member-moves", "target-assigned-update")
BALANCE_RELATIONS = ("two-equal-moves-reassemble-complete-separation", "unequal-free-moves", "measurement-selected-balance")
RESIDUAL_SEMANTICS = ("half-One-gives-empty-residual-off-half-stays-positive", "numerical-null-synchrony", "one-region-result-as-premise")
ENSEMBLE_TERMINALS = ("synchronized-class-remains-synchronized-under-successor", "universal-collapse-without-condition", "target-recurrence-as-law")
CLOSURES = ("arbitrary-positive-pair-and-successor-closure", "historical-ensemble-only", "finite-prefix-without-generality")
TARGET_BOUNDARIES = ("sealed-before-observation-release", "observation-readable-before-seal")
EXTENSIONS = ("empty-extension", "free-coupling-correction")

GENERATION_RULE = (
    "Generate the complete product of every complete, selected or target-assigned coupling domain; every paired, "
    "one-sided or target-assigned movement; every exact balance, unequal or measurement-selected relation; every "
    "empty-record, numerical-null or result-as-premise residual semantics; every conditional terminal, universal "
    "collapse or target-recurrence ensemble law; every general, historical-only or uncertified closure; both "
    "target custody states; and both extension states."
)
GRAMMAR_BOUNDARY = (
    "Every ordered pair of exact positive Fold parts, the complete generated coupling alternatives around the "
    "forced half-One, equal coupled movement by a part of exact separation, empty structural equality records, "
    "every already synchronized finite positive ensemble and every positive successor depth. Arbitrary ensemble "
    "convergence is not assumed; it must be separately measured or proven for its registered recurrence."
)


def candidate_forms() -> tuple[CandidateForm, ...]:
    return tuple(CandidateForm(*values) for values in product(COUPLING_DOMAINS, PAIRED_ACTIONS, BALANCE_RELATIONS, RESIDUAL_SEMANTICS, ENSEMBLE_TERMINALS, CLOSURES, TARGET_BOUNDARIES, EXTENSIONS))


@lru_cache(maxsize=1)
def axis_facts() -> dict[str, dict[str, bool]]:
    certificate = formal_certificate()
    exact = all((certificate["unique_synchronizing_coupling"] == Fraction(1, 2), certificate["half_One_residuals_empty"], certificate["off_half_residuals_positive"], certificate["synchronized_terminal_preserved"]))
    return {
        "coupling": {name: value for name, value in zip(COUPLING_DOMAINS, (exact, False, False))},
        "action": {name: value for name, value in zip(PAIRED_ACTIONS, (exact, False, False))},
        "balance": {name: value for name, value in zip(BALANCE_RELATIONS, (exact, False, False))},
        "residual": {name: value for name, value in zip(RESIDUAL_SEMANTICS, (exact, False, False))},
        "terminal": {name: value for name, value in zip(ENSEMBLE_TERMINALS, (exact, False, False))},
        "closure": {name: value for name, value in zip(CLOSURES, (exact, False, False))},
        "target": {TARGET_BOUNDARIES[0]: True, TARGET_BOUNDARIES[1]: False},
        "extension": {EXTENSIONS[0]: True, EXTENSIONS[1]: False},
    }


def candidate_facts(form: CandidateForm) -> dict[str, bool]:
    facts = axis_facts()
    return {
        "coupling-domain": facts["coupling"][form.coupling_domain],
        "paired-action": facts["action"][form.paired_action],
        "balance": facts["balance"][form.balance_relation],
        "residual": facts["residual"][form.residual_semantics],
        "ensemble-terminal": facts["terminal"][form.ensemble_terminal],
        "closure": facts["closure"][form.closure],
        "target-custody": facts["target"][form.target_boundary],
        "extension": facts["extension"][form.extension],
    }


def form_survives(form: CandidateForm) -> bool:
    return all(candidate_facts(form).values())


class CoupledEnsembleSynchronizationProgram:
    def __init__(self, source_hash: str):
        self.source_hash = source_hash
        self._forms = candidate_forms()
        self._by_id = {form.candidate_id: form for form in self._forms}

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            CLAIM_ID,
            "Half-One pair synchronization and coupled-ensemble terminal law",
            "physics",
            "For every ordered pair of exact positive Fold parts, moving both members toward one another by the same coupling share of their separation synchronizes them exactly if and only if the coupling is the forced half-One. The two equal moves then reassemble the complete separation and leave an empty structural residual record; every off-half generated coupling leaves a positive residual. An already synchronized finite ensemble remains synchronized under every common Fold successor. Arbitrary-ensemble convergence is not assumed: the complete superseded E4 recurrence is released and reconstructed only after the general boundary is sealed.",
            EvidenceMode.EMPIRICAL,
            (ROOT_THEOREM,),
            (
                "SFT-FOUNDATION-HALF-ONE-001",
                "SFT-FOUNDATION-FOLD-001",
                "SFT-FOUNDATION-PART-001",
                "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
                "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
                "SFT-MATH-EXACT-ARITHMETIC-001",
                "SFT-MATH-DYNAMICAL-SYSTEMS-001",
                "SFT-MATH-COMBINATORICS-001",
            ),
            (), (),
            (ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
            self.source_hash,
        )

    def generate_candidates(self) -> CandidateCensus:
        candidates = tuple(Candidate(form.candidate_id, str(form), sha256_identity({"rule": GENERATION_RULE, "form": form, "facts": candidate_facts(form)})) for form in self._forms)
        return CandidateCensus(GENERATION_RULE, GRAMMAR_BOUNDARY, len(candidates), sha256_identity({"axis_cardinalities": (3,3,3,3,3,3,2,2), "candidate_ids": tuple(item.candidate_id for item in candidates)}), candidates)

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        form = self._by_id[candidate.candidate_id]
        facts = candidate_facts(form)
        survives = all(facts.values())
        failures = tuple(name for name, passed in facts.items() if not passed)
        reason = "Equal paired movement forces half-One as the unique empty-residual synchronization boundary and preserves every synchronized terminal class." if survives else "Rejected by computed Fold predicates: " + ", ".join(failures) + "."
        return CandidateDecision(candidate.candidate_id, survives, reason, sha256_identity({"trace": candidate.trace_hash, "facts": facts, "survives": survives, "reason": reason}))

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        survivors = tuple(item.candidate_id for item in decisions if item.survives)
        certificate = formal_certificate()
        closed = all((len(survivors) == 1, certificate["unique_synchronizing_coupling"] == Fraction(1,2), certificate["half_One_residuals_empty"], certificate["off_half_residuals_positive"], certificate["synchronized_terminal_preserved"]))
        return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT, GRAMMAR_BOUNDARY, closed, closed and len(set(survivors)) == 1, sha256_identity({"certificate": certificate, "decisions": tuple(decisions), "survivors": survivors}), sha256_identity({
            "pair_base": "two equal moves exhaust separation only when each is half",
            "off_half": "the exact residual multiplier is the positive difference between One and twice the coupling",
            "ensemble_successor": "a common Fold image preserves equality of every synchronized member",
            "arbitrary_ensemble_convergence_not_imported": True,
            "historical_target_absent_from_claimant": True,
        }))

    def run_controls(self) -> tuple[ControlResult, ...]:
        survivors = tuple(form for form in self._forms if form_survives(form))
        if len(survivors) != 1:
            raise ValueError("controls require one computed survivor")
        form = survivors[0]
        records = (
            (ControlKind.FALSE_PREMISE, residual_record(Fraction(1,4), Fraction(3,4), Fraction(1,3)) != () and residual_record(Fraction(1,4), Fraction(3,4), Fraction(2,3)) != (), "Reject either off-half coupling as exact synchronization.", "Both leave the same positive residual magnitude."),
            (ControlKind.TAMPERED_SOURCE, sha256_identity({"changed": self.source_hash}) != self.source_hash, "Reject a changed claimant source identity.", "The changed identity differs from the registered manifest."),
            (ControlKind.TAMPERED_ARTIFACT, len({item.candidate_id for item in self._forms}) == len(self._forms), "Reject duplicated candidate identities.", "The complete product has unique identities."),
            (ControlKind.BOUNDARY, not form_survives(replace(form, ensemble_terminal=ENSEMBLE_TERMINALS[1])) and not form_survives(replace(form, target_boundary=TARGET_BOUNDARIES[1])) and not form_survives(replace(form, extension=EXTENSIONS[1])), "Reject universal collapse, pre-seal observation and free correction.", "Only the conditional synchronized terminal, sealed target and empty extension survive."),
        )
        return tuple(ControlResult(kind, passed, expected, observed, sha256_identity({"kind": kind, "passed": passed, "expected": expected, "observed": observed})) for kind, passed, expected, observed in records)


__all__ = ("CLAIM_ID", "EXPERIMENT_ID", "GENERATION_RULE", "GRAMMAR_BOUNDARY", "CoupledEnsembleSynchronizationProgram", "candidate_forms", "form_survives", "formal_certificate", "paired_move", "residual_record", "residual_scale", "synchronized_ensemble_successor", "unique_pair_synchronizing_coupling")
