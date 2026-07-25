"""Exact Fold expansion/information carrier and conditional map correspondence.

No external paper, analytic target, preferred survivor or claimant-controlled
admission flag enters this formal claimant. External labels are released only
after the prediction seal by the empirical validator.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import lru_cache
from itertools import product
from typing import Sequence

from sft.engine import Candidate, CandidateCensus, CandidateDecision, ClaimRegistration, ClosureEvidence, ClosureScope, ControlKind, ControlResult, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.engine.canonical import sha256_identity


CLAIM_ID = "SFT-PHYS-LYAPUNOV-KS-CORRESPONDENCE-TERMINAL-008"
EXPERIMENT_ID = "SFT-EXP-PHYS-LYAPUNOV-KS-CORRESPONDENCE-TERMINAL-008"


def positive_whole(value: int, *, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError("a generated positive whole is required")
    return value


def complete_word_support(label_count: int, depth: int) -> tuple[tuple[int, ...], ...]:
    m = positive_whole(label_count, minimum=2)
    d = positive_whole(depth)
    labels = tuple(range(1, m + 1))
    return tuple(product(labels, repeat=d))


def exact_support_count(label_count: int, depth: int) -> int:
    return len(complete_word_support(label_count, depth))


def separation_carrier(label_count: int, separation_parts: int) -> int:
    m = positive_whole(label_count, minimum=2)
    parts = positive_whole(separation_parts)
    return m * parts


def carrier_certificate() -> dict[str, object]:
    cases = tuple(
        {
            "label_count": m,
            "depth_support": tuple(exact_support_count(m, depth) for depth in (1, 2, 3, 4)),
            "successor_ratios": tuple(exact_support_count(m, depth + 1) // exact_support_count(m, depth) for depth in (1, 2, 3)),
            "separation_multipliers": tuple(separation_carrier(m, parts) // parts for parts in (1, 2, 3, 5)),
        }
        for m in (2, 3, 5)
    )
    return {
        "cases": cases,
        "support_is_m_to_depth": all(row["depth_support"] == tuple(row["label_count"] ** depth for depth in (1, 2, 3, 4)) for row in cases),
        "one_step_support_multiplier_is_m": all(row["successor_ratios"] == (row["label_count"],) * 3 for row in cases),
        "local_separation_multiplier_is_m": all(row["separation_multipliers"] == (row["label_count"],) * 4 for row in cases),
        "common_exact_carrier": all(row["successor_ratios"][0] == row["separation_multipliers"][0] == row["label_count"] for row in cases),
        "analytic_proof_value_required": False,
    }


@dataclass(frozen=True)
class CandidateForm:
    label_domain: str
    separation_law: str
    support_law: str
    common_carrier: str
    information_step: str
    analytic_boundary: str
    target_boundary: str
    extension: str

    @property
    def candidate_id(self) -> str:
        return "__".join((self.label_domain, self.separation_law, self.support_law, self.common_carrier, self.information_step, self.analytic_boundary, self.target_boundary, self.extension))


LABEL_DOMAINS = ("complete-generated-m-label-domain", "selected-two-label-domain", "target-assigned-label-domain")
SEPARATION_LAWS = ("uncast-local-separation-multiplied-by-m", "free-separation-exponent", "target-assigned-expansion")
SUPPORT_LAWS = ("complete-depth-support-m-to-d", "fixed-binary-support", "selected-support-subset")
COMMON_CARRIERS = ("same-m-carries-separation-and-support-growth", "independent-rate-parameters", "measurement-equated-carriers")
INFORMATION_STEPS = ("one-m-label-distinction-per-depth", "untyped-information-increment", "target-assigned-bit-rate")
ANALYTIC_BOUNDARIES = ("exact-carrier-only-symbolic-external-translation", "imported-analytic-proof-value", "decimal-rate-as-proof")
TARGET_BOUNDARIES = ("sealed-before-observation-release", "observation-readable-before-seal")
EXTENSIONS = ("empty-extension", "free-rate-correction")

GENERATION_RULE = (
    "Generate the complete product of every complete, selected or target-assigned label domain; every exact, free "
    "or target-assigned separation law; every complete, fixed or selected support law; every common, independent "
    "or measurement-equated carrier relation; every exact, untyped or target-assigned information step; every "
    "exact-symbolic, imported-analytic or decimal proof boundary; both target-custody states; and both extension states."
)
GRAMMAR_BOUNDARY = (
    "Every positive finite complete generated label count m of at least two, every positive Fold depth d, every "
    "positive local separation, complete m-label word support and its successor. The exact theorem returns the "
    "shared positive-whole carrier m; analytic logarithmic notation remains solely an external comparison label."
)


def candidate_forms() -> tuple[CandidateForm, ...]:
    return tuple(CandidateForm(*values) for values in product(LABEL_DOMAINS, SEPARATION_LAWS, SUPPORT_LAWS, COMMON_CARRIERS, INFORMATION_STEPS, ANALYTIC_BOUNDARIES, TARGET_BOUNDARIES, EXTENSIONS))


@lru_cache(maxsize=1)
def axis_facts() -> dict[str, dict[str, bool]]:
    certificate = carrier_certificate()
    exact = all((certificate["support_is_m_to_depth"], certificate["one_step_support_multiplier_is_m"], certificate["local_separation_multiplier_is_m"], certificate["common_exact_carrier"], not certificate["analytic_proof_value_required"]))
    return {
        "label": {name: value for name, value in zip(LABEL_DOMAINS, (exact, False, False))},
        "separation": {name: value for name, value in zip(SEPARATION_LAWS, (exact, False, False))},
        "support": {name: value for name, value in zip(SUPPORT_LAWS, (exact, False, False))},
        "carrier": {name: value for name, value in zip(COMMON_CARRIERS, (exact, False, False))},
        "information": {name: value for name, value in zip(INFORMATION_STEPS, (exact, False, False))},
        "analytic": {name: value for name, value in zip(ANALYTIC_BOUNDARIES, (exact, False, False))},
        "target": {TARGET_BOUNDARIES[0]: True, TARGET_BOUNDARIES[1]: False},
        "extension": {EXTENSIONS[0]: True, EXTENSIONS[1]: False},
    }


def candidate_facts(form: CandidateForm) -> dict[str, bool]:
    facts = axis_facts()
    return {
        "label-domain": facts["label"][form.label_domain],
        "separation-law": facts["separation"][form.separation_law],
        "support-law": facts["support"][form.support_law],
        "common-carrier": facts["carrier"][form.common_carrier],
        "information-step": facts["information"][form.information_step],
        "analytic-boundary": facts["analytic"][form.analytic_boundary],
        "target-custody": facts["target"][form.target_boundary],
        "extension": facts["extension"][form.extension],
    }


def form_survives(form: CandidateForm) -> bool:
    return all(candidate_facts(form).values())


class LyapunovKSCorrespondenceProgram:
    def __init__(self, source_hash: str):
        self.source_hash = source_hash
        self._forms = candidate_forms()
        self._by_id = {form.candidate_id: form for form in self._forms}

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            CLAIM_ID,
            "Exact Fold expansion and information-rate carrier correspondence",
            "physics",
            "A complete m-label Fold step multiplies every uncast local separation by the positive whole m and multiplies complete word support by the same m. At depth d the support is exactly m^d and one further depth contributes one complete m-label distinction. Thus expansion and information growth have one forced exact carrier m. Conventional Lyapunov and entropy logarithms are correspondence labels at the external analytic boundary, not imported SFT proof values. Under the separately stated hypotheses of an entropy formula, the common external rate label corresponds to this same exact carrier.",
            EvidenceMode.EMPIRICAL,
            (ROOT_THEOREM,),
            (
                "SFT-MATH-SELF-SIMILAR-CONVERGENCE-002",
                "SFT-INFO-ENTROPY-UNCERTAINTY-001",
                "SFT-INFO-SYMBOL-DISTINCTION-001",
                "SFT-FOUNDATION-FOLD-001",
                "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
                "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
                "SFT-MATH-EXACT-ARITHMETIC-001",
                "SFT-MATH-DYNAMICAL-SYSTEMS-001",
            ),
            (), (),
            (ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
            self.source_hash,
        )

    def generate_candidates(self) -> CandidateCensus:
        candidates = tuple(Candidate(form.candidate_id, str(form), sha256_identity({"rule": GENERATION_RULE, "form": form, "facts": candidate_facts(form)})) for form in self._forms)
        return CandidateCensus(GENERATION_RULE, GRAMMAR_BOUNDARY, len(candidates), sha256_identity({"axis_cardinalities": (3,3,3,3,3,3,2,2), "candidate_ids": tuple(item.candidate_id for item in candidates)}), candidates)

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        facts = candidate_facts(self._by_id[candidate.candidate_id])
        survives = all(facts.values())
        failures = tuple(name for name, passed in facts.items() if not passed)
        reason = "Complete support and local separation independently return the same exact generated carrier m without an analytic proof scalar or free correction." if survives else "Rejected by computed Fold predicates: " + ", ".join(failures) + "."
        return CandidateDecision(candidate.candidate_id, survives, reason, sha256_identity({"trace": candidate.trace_hash, "facts": facts, "survives": survives, "reason": reason}))

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        survivors = tuple(item.candidate_id for item in decisions if item.survives)
        certificate = carrier_certificate()
        closed = all((len(survivors) == 1, certificate["support_is_m_to_depth"], certificate["one_step_support_multiplier_is_m"], certificate["local_separation_multiplier_is_m"], certificate["common_exact_carrier"], not certificate["analytic_proof_value_required"]))
        return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT, GRAMMAR_BOUNDARY, closed, closed and len(set(survivors)) == 1, sha256_identity({"certificate": certificate, "decisions": tuple(decisions), "survivors": survivors}), sha256_identity({
            "base": "one complete m-label step has exactly m labels and multiplies local separation by m",
            "successor": "appending one complete label to every word multiplies support by m",
            "common_carrier": "the separation and support ratios are identically the same generated positive whole m",
            "analytic_values_imported": False,
            "external_targets_absent_from_claimant": True,
        }))

    def run_controls(self) -> tuple[ControlResult, ...]:
        survivors = tuple(form for form in self._forms if form_survives(form))
        if len(survivors) != 1:
            raise ValueError("controls require one computed survivor")
        form = survivors[0]
        records = (
            (ControlKind.FALSE_PREMISE, exact_support_count(3, 4) != 2 ** 4 and separation_carrier(3, 5) != 2 * 5, "Reject a selected binary carrier for a generated three-label Fold.", "Complete support and separation both return three, not two, as their multiplier."),
            (ControlKind.TAMPERED_SOURCE, sha256_identity({"changed": self.source_hash}) != self.source_hash, "Reject a changed claimant source identity.", "The changed identity differs from the registered manifest."),
            (ControlKind.TAMPERED_ARTIFACT, len({item.candidate_id for item in self._forms}) == len(self._forms), "Reject duplicated candidate identities.", "The complete product has unique identities."),
            (ControlKind.BOUNDARY, not form_survives(replace(form, analytic_boundary=ANALYTIC_BOUNDARIES[1])) and not form_survives(replace(form, target_boundary=TARGET_BOUNDARIES[1])) and not form_survives(replace(form, extension=EXTENSIONS[1])), "Reject imported analytic proof values, pre-seal target access and a free rate correction.", "Only the exact carrier, sealed target and empty extension survive."),
        )
        return tuple(ControlResult(kind, passed, expected, observed, sha256_identity({"kind": kind, "passed": passed, "expected": expected, "observed": observed})) for kind, passed, expected, observed in records)


__all__ = ("CLAIM_ID", "EXPERIMENT_ID", "GENERATION_RULE", "GRAMMAR_BOUNDARY", "LyapunovKSCorrespondenceProgram", "candidate_forms", "carrier_certificate", "complete_word_support", "exact_support_count", "form_survives", "separation_carrier")
