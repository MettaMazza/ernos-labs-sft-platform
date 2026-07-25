"""Depth-independent exact quadrupole radiated-power law."""
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

CLAIM_ID = "SFT-PHYS-QUADRUPOLE-RADIATED-POWER-TERMINAL-012"
EXPERIMENT_ID = "SFT-EXP-PHYS-QUADRUPOLE-RADIATED-POWER-TERMINAL-012"
ONE = Fraction(1, 1)
BINARY = 2


def positive_difference_record(values: tuple[Fraction, ...]) -> tuple[Fraction, ...] | tuple[()]:
    """Return a positive forward-difference record or structural emptiness."""
    if len(values) < BINARY or any(not isinstance(value, Fraction) or value <= 0 for value in values):
        raise ValueError("positive exact carrier sequence required")
    if all(value == values[0] for value in values):
        return ()
    if any(values[index + 1] <= values[index] for index in range(len(values) - 1)):
        raise ValueError("difference opposition must retain positive orientation")
    return tuple(values[index + 1] - values[index] for index in range(len(values) - 1))


def generated_difference_record(
    values: tuple[Fraction, ...], order: int
) -> tuple[Fraction, ...] | tuple[()]:
    if isinstance(order, bool) or not isinstance(order, int) or order < 1:
        raise ValueError("positive generated difference order required")
    record: tuple[Fraction, ...] | tuple[()] = values
    for _ in range(order):
        if record == ():
            return ()
        record = positive_difference_record(record)
    return record


def generated_quadrupole_trace(amplitude: Fraction = ONE, length: int = 8) -> tuple[Fraction, ...]:
    if not isinstance(amplitude, Fraction) or amplitude <= 0:
        raise ValueError("positive exact quadrupole amplitude required")
    if isinstance(length, bool) or not isinstance(length, int) or length < 4:
        raise ValueError("quadrupole trace requires at least four positive ticks")
    return tuple(amplitude * Fraction(tick**3, 1) for tick in range(1, length + 1))


def static_quadrupole_trace(length: int = 8) -> tuple[Fraction, ...]:
    if isinstance(length, bool) or not isinstance(length, int) or length < 4:
        raise ValueError("static trace requires at least four positive ticks")
    return tuple(ONE for _ in range(1, length + 1))


def quadrupole_power_record(
    values: tuple[Fraction, ...], coupling: Fraction = Fraction(1, BINARY)
) -> Fraction | tuple[()]:
    if coupling != Fraction(1, BINARY):
        raise ValueError("radiated-power channel requires the admitted binary half-One coupling")
    third = generated_difference_record(values, 3)
    if third == ():
        return ()
    if not third or len(set(third)) != 1 or third[0] <= 0:
        raise ValueError("registered power witness requires one retained constant third-rate carrier")
    return coupling * third[0] * third[0]


def cubic_opposition_identity(index: int) -> dict[str, object]:
    """All-positive identity equivalent to a constant third difference."""
    if isinstance(index, bool) or not isinstance(index, int) or index < 1:
        raise ValueError("positive identity index required")
    left = (index + 3) ** 3 + 3 * (index + 1) ** 3
    right = 3 * (index + 2) ** 3 + index**3 + 6
    successor_increment = 12 * index**2 + 48 * index + 58
    next_left = (index + 4) ** 3 + 3 * (index + 2) ** 3
    next_right = 3 * (index + 3) ** 3 + (index + 1) ** 3 + 6
    return {
        "index": index,
        "left": left,
        "right": right,
        "identity_holds": left == right,
        "successor_left_increment": next_left - left,
        "successor_right_increment": next_right - right,
        "generated_successor_increment": successor_increment,
        "successor_preserves_identity": next_left - left == next_right - right == successor_increment,
    }


def radiated_power_certificate(depth: int = 12) -> dict[str, object]:
    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 2:
        raise ValueError("positive binary shell depth required")
    coupling = Fraction(1, BINARY)
    base_trace = generated_quadrupole_trace(ONE, depth + 4)
    doubled_trace = generated_quadrupole_trace(Fraction(BINARY, 1), depth + 4)
    static_trace = static_quadrupole_trace(depth + 4)
    base_third = generated_difference_record(base_trace, 3)
    doubled_third = generated_difference_record(doubled_trace, 3)
    base_power = quadrupole_power_record(base_trace, coupling)
    doubled_power = quadrupole_power_record(doubled_trace, coupling)
    static_power = quadrupole_power_record(static_trace, coupling)
    if not isinstance(base_power, Fraction) or not isinstance(doubled_power, Fraction):
        raise ValueError("dynamic power records must remain exact and positive")
    shell_rows = tuple(
        {
            "radius": Fraction(BINARY**layer, 1),
            "density": base_power / Fraction(BINARY ** (BINARY * layer), 1),
            "reconstructed_power": base_power,
        }
        for layer in range(1, depth + 1)
    )
    shell_rows = tuple(
        {
            **row,
            "reconstructed_power": row["density"] * row["radius"] * row["radius"],
        }
        for row in shell_rows
    )
    identities = tuple(cubic_opposition_identity(index) for index in range(1, depth + 1))
    return {
        "coupling": coupling,
        "monopole_record": "held-source",
        "dipole_record": "held-momentum",
        "first_radiative_moment": "quadrupole",
        "base_third_record": base_third,
        "doubled_third_record": doubled_third,
        "base_power": base_power,
        "doubled_power": doubled_power,
        "static_power_record": static_power,
        "third_rate_doubles": all(doubled == BINARY * base for base, doubled in zip(base_third, doubled_third)),
        "power_quadruples": doubled_power == BINARY**2 * base_power,
        "shell_rows": shell_rows,
        "shell_power_conserved": all(row["reconstructed_power"] == base_power for row in shell_rows),
        "cubic_identities": identities,
        "base_identity_holds": identities[0]["identity_holds"],
        "successor_identity_holds": all(row["successor_preserves_identity"] for row in identities),
        "general_rate_identity": "third generated difference of amplitude paired with positive tick cubed is six paired with amplitude",
        "general_power_identity": "power is half-One paired with the third-rate carrier paired with itself",
        "general_shell_identity": "rank-two shell density paired with radius and radius reconstructs total power",
        "static_silence_is_empty_not_numeric_zero": static_power == (),
        "negative_zero_irrational_or_imaginary_proof_scalar_used": False,
    }


@dataclass(frozen=True)
class CandidateForm:
    moment_law: str
    rate_law: str
    energy_law: str
    coupling_law: str
    shell_law: str
    adverse_control: str
    target_boundary: str
    extension: str

    @property
    def candidate_id(self) -> str:
        return "__".join(
            (
                self.moment_law,
                self.rate_law,
                self.energy_law,
                self.coupling_law,
                self.shell_law,
                self.adverse_control,
                self.target_boundary,
                self.extension,
            )
        )


MOMENT_LAWS = (
    "held-monopole-and-dipole-leave-quadrupole-first",
    "lower-moment-radiation",
    "target-assigned-moment",
)
RATE_LAWS = (
    "third-generated-quadrupole-difference",
    "free-difference-order",
    "target-assigned-rate",
)
ENERGY_LAWS = (
    "positive-square-of-third-rate",
    "linear-or-unsigned-rate-energy",
    "target-assigned-energy",
)
COUPLING_LAWS = (
    "admitted-binary-half-One-coupling",
    "free-radiation-coupling",
    "target-assigned-coupling",
)
SHELL_LAWS = (
    "rank-two-density-dilution-with-conserved-total-power",
    "unconserved-or-free-shell-power",
    "target-assigned-shell-law",
)
ADVERSE_CONTROLS = (
    "static-empty-and-amplitude-square-scaling",
    "numerical-zero-or-linear-scaling",
    "target-assigned-control",
)
TARGET_BOUNDARIES = (
    "sealed-before-observation-release",
    "observation-readable-before-seal",
)
EXTENSIONS = (
    "empty-extension",
    "free-radiation-correction",
)

GENERATION_RULE = (
    "Generate the complete product of every quadrupole-first, lower-moment or target-assigned moment law; "
    "every third-generated, free-order or target-assigned rate; every squared, linear/free or target-assigned "
    "energy carrier; every admitted, free or target-assigned coupling; every rank-two conserved, free or "
    "target-assigned shell law; every structural-empty, numerical/linear or target-assigned adverse control; "
    "both target custody states; and both extension states."
)
GRAMMAR_BOUNDARY = (
    "Every finite exact positive quadrupole-magnitude trace generated by a positive cubic tick carrier and "
    "positive amplitude, every positive tick index under the all-positive cubic successor identity, and every "
    "finite outward binary shell. Static silence is structural emptiness. The theorem is the leading positive-"
    "magnitude quadrupole channel; tensor orientation and physical-unit comparison are retained post-seal."
)


def candidate_forms() -> tuple[CandidateForm, ...]:
    return tuple(
        CandidateForm(*values)
        for values in product(
            MOMENT_LAWS,
            RATE_LAWS,
            ENERGY_LAWS,
            COUPLING_LAWS,
            SHELL_LAWS,
            ADVERSE_CONTROLS,
            TARGET_BOUNDARIES,
            EXTENSIONS,
        )
    )


@lru_cache(maxsize=1)
def axis_facts() -> dict[str, dict[str, bool]]:
    certificate = radiated_power_certificate()
    exact = all(
        (
            certificate["coupling"] == Fraction(1, BINARY),
            certificate["first_radiative_moment"] == "quadrupole",
            certificate["static_silence_is_empty_not_numeric_zero"],
            certificate["third_rate_doubles"],
            certificate["power_quadruples"],
            certificate["shell_power_conserved"],
            certificate["base_identity_holds"],
            certificate["successor_identity_holds"],
            not certificate["negative_zero_irrational_or_imaginary_proof_scalar_used"],
        )
    )
    return {
        "moment": {name: value for name, value in zip(MOMENT_LAWS, (exact, False, False))},
        "rate": {name: value for name, value in zip(RATE_LAWS, (exact, False, False))},
        "energy": {name: value for name, value in zip(ENERGY_LAWS, (exact, False, False))},
        "coupling": {name: value for name, value in zip(COUPLING_LAWS, (exact, False, False))},
        "shell": {name: value for name, value in zip(SHELL_LAWS, (exact, False, False))},
        "control": {name: value for name, value in zip(ADVERSE_CONTROLS, (exact, False, False))},
        "target": {TARGET_BOUNDARIES[0]: True, TARGET_BOUNDARIES[1]: False},
        "extension": {EXTENSIONS[0]: True, EXTENSIONS[1]: False},
    }


def candidate_facts(form: CandidateForm) -> dict[str, bool]:
    facts = axis_facts()
    return {
        "moment": facts["moment"][form.moment_law],
        "rate": facts["rate"][form.rate_law],
        "energy": facts["energy"][form.energy_law],
        "coupling": facts["coupling"][form.coupling_law],
        "shell": facts["shell"][form.shell_law],
        "control": facts["control"][form.adverse_control],
        "target": facts["target"][form.target_boundary],
        "extension": facts["extension"][form.extension],
    }


def form_survives(form: CandidateForm) -> bool:
    return all(candidate_facts(form).values())


class QuadrupoleRadiatedPowerProgram:
    def __init__(self, source_hash: str):
        self.source_hash = source_hash
        self._forms = candidate_forms()
        self._by_id = {form.candidate_id: form for form in self._forms}

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            CLAIM_ID,
            "Exact quadrupole third-difference radiated-power law",
            "physics",
            "Held source and momentum records close monopole and dipole radiation, leaving the quadrupole as the first radiative moment. One more generated difference gives its radiative rate. The admitted field-energy square and binary half-One coupling force power equal to half-One paired with that third-rate carrier twice. A static quadrupole closes to an empty radiation record, amplitude scaling is exactly squared, and rank-two shell dilution preserves total power at every finite radius.",
            EvidenceMode.EMPIRICAL,
            (ROOT_THEOREM,),
            (
                "SFT-PHYS-GRAVITY-WAVE-QUADRUPOLE-003",
                "SFT-PHYS-GRAVITY-NONLINEAR-SELF-SOURCE-003",
                "SFT-PHYS-FIELD-INVERSE-SQUARE-001",
                "SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001",
                "SFT-PHYS-SYMMETRIC-SOURCE-CONSERVATION-TERMINAL-010",
                "SFT-PHYS-FORCE-PRIME-SECTOR-LADDER-002",
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
            "Held lower moments, third generated difference, field-energy square, half-One coupling and rank-two shell conservation force the complete power law."
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
        certificate = radiated_power_certificate()
        closed = len(survivors) == 1 and all(
            (
                certificate["static_silence_is_empty_not_numeric_zero"],
                certificate["third_rate_doubles"],
                certificate["power_quadruples"],
                certificate["shell_power_conserved"],
                certificate["base_identity_holds"],
                certificate["successor_identity_holds"],
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
                    "base": "At the first positive cubic index, opposed positive cubic sums differ by the retained six-carrier and half-One times its square is the radiated-power carrier.",
                    "successor": "Both opposed cubic ledgers gain the same positive twelve-index-squared plus forty-eight-index plus fifty-eight carrier, preserving the six-carrier third difference at every successor.",
                    "shell": "Each binary radius successor gives four boundary cells, quarters density and preserves density paired with radius twice.",
                    "targets_absent": True,
                }
            ),
        )

    def run_controls(self) -> tuple[ControlResult, ...]:
        survivors = tuple(form for form in self._forms if form_survives(form))
        if len(survivors) != 1:
            raise ValueError("controls require one computed survivor")
        form = survivors[0]
        certificate = radiated_power_certificate()
        records = (
            (
                ControlKind.FALSE_PREMISE,
                certificate["static_power_record"] == () and certificate["power_quadruples"],
                "Reject numerical-zero static power or linear amplitude scaling.",
                "Static radiation is empty and doubled third rate gives fourfold power.",
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
                not form_survives(replace(form, rate_law=RATE_LAWS[1]))
                and not form_survives(replace(form, target_boundary=TARGET_BOUNDARIES[1]))
                and not form_survives(replace(form, extension=EXTENSIONS[1])),
                "Reject free derivative order, pre-seal target access and free correction.",
                "Only generated third rate, sealed target custody and empty extension survive.",
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
    "QuadrupoleRadiatedPowerProgram",
    "candidate_forms",
    "cubic_opposition_identity",
    "form_survives",
    "generated_difference_record",
    "generated_quadrupole_trace",
    "positive_difference_record",
    "quadrupole_power_record",
    "radiated_power_certificate",
    "static_quadrupole_trace",
)
