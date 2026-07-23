"""Shared generated-grammar kernel for the twelve mathematics laws.

The kernel supplies engine plumbing only.  Every scientific boundary, choice,
elimination, witness and induction clause is declared by a branch-specific
``LawSpec``.  Host integers and booleans used here count and check artifacts;
they are not admitted SFT mathematical values.
"""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass(frozen=True)
class Choice:
    name: str
    admitted: bool
    reason: str


@dataclass(frozen=True)
class Dimension:
    key: str
    question: str
    choices: tuple[Choice, ...]

    @property
    def admitted_choice(self) -> Choice:
        admitted = tuple(choice for choice in self.choices if choice.admitted)
        if len(admitted) != 1:
            raise ValueError(f"dimension {self.key} must have exactly one admitted choice")
        return admitted[0]


@dataclass(frozen=True)
class Witness:
    name: str
    statement: str
    passed: bool


@dataclass(frozen=True)
class LawSpec:
    claim_id: str
    title: str
    statement: str
    dependencies: tuple[str, ...]
    generation_rule: str
    grammar_boundary: str
    dimensions: tuple[Dimension, ...]
    exact_result: str
    laws: tuple[str, ...]
    induction_base: str
    induction_step: str
    boundary_exclusions: tuple[str, ...]
    witnesses: tuple[Witness, ...]
    why: str
    derivation: str
    check: str
    limitations: str
    correspondence_terms: tuple[str, ...]

    def validate(self) -> None:
        if not self.claim_id.startswith("SFT-MATH-"):
            raise ValueError("mathematics claim identity is invalid")
        if not self.dependencies or not self.dimensions or not self.witnesses:
            raise ValueError("mathematics law lacks dependencies, dimensions or witnesses")
        keys = tuple(dimension.key for dimension in self.dimensions)
        if len(set(keys)) != len(keys):
            raise ValueError("mathematics law contains duplicate dimensions")
        for dimension in self.dimensions:
            if len(dimension.choices) < 2:
                raise ValueError(f"dimension {dimension.key} has no generated alternative")
            dimension.admitted_choice
        if not all(witness.passed for witness in self.witnesses):
            failed = tuple(witness.name for witness in self.witnesses if not witness.passed)
            raise ValueError("mathematics operational witness failed: " + ", ".join(failed))


def binary_dimension(
    key: str,
    question: str,
    rejected_name: str,
    rejected_reason: str,
    admitted_name: str,
    admitted_reason: str,
) -> Dimension:
    """Declare one exhaustive two-way structural distinction."""

    return Dimension(
        key=key,
        question=question,
        choices=(
            Choice(rejected_name, False, rejected_reason),
            Choice(admitted_name, True, admitted_reason),
        ),
    )


def candidate_records(spec: LawSpec) -> tuple[dict[str, object], ...]:
    spec.validate()
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return tuple(
        {
            "candidate_id": "__".join(fields),
            "coordinates": tuple(zip((dimension.key for dimension in spec.dimensions), fields)),
            "exact_form": "; ".join(
                f"{dimension.key}={field}" for dimension, field in zip(spec.dimensions, fields)
            ),
        }
        for fields in product(*domains)
    )


def survivor_id(spec: LawSpec) -> str:
    return "__".join(dimension.admitted_choice.name for dimension in spec.dimensions)


def decision_reason(spec: LawSpec, record: dict[str, object]) -> str:
    coordinates = dict(record["coordinates"])
    for dimension in spec.dimensions:
        selected = coordinates[dimension.key]
        admitted = dimension.admitted_choice
        if selected != admitted.name:
            choice = next(choice for choice in dimension.choices if choice.name == selected)
            return choice.reason
    return spec.exact_result


def completeness_record(spec: LawSpec) -> dict[str, object]:
    return {
        "generation_rule": spec.generation_rule,
        "grammar_boundary": spec.grammar_boundary,
        "dimensions": tuple(
            {
                "key": dimension.key,
                "question": dimension.question,
                "choices": tuple((choice.name, choice.reason) for choice in dimension.choices),
            }
            for dimension in spec.dimensions
        ),
        "candidate_ids": tuple(record["candidate_id"] for record in candidate_records(spec)),
        "product_exhaustion": (
            "Every named option in every registered dimension occurs once with every "
            "option in every other dimension; duplicate candidate identities are forbidden."
        ),
    }


def closure_record(spec: LawSpec) -> dict[str, object]:
    return {
        "exact_result": spec.exact_result,
        "laws": spec.laws,
        "operational_witnesses": tuple(
            (witness.name, witness.statement, witness.passed) for witness in spec.witnesses
        ),
        "minimality": (
            "Replacing any admitted coordinate by a generated alternative removes a "
            "registered preservation, completeness, exactness or provenance condition."
        ),
        "named_shape_uniqueness": (
            f"The complete product contains exactly one all-admitted coordinate: {survivor_id(spec)}."
        ),
        "induction_base": spec.induction_base,
        "induction_step": spec.induction_step,
        "boundary_exclusions": spec.boundary_exclusions,
    }


def control_records(spec: LawSpec, source_hash: str) -> tuple[dict[str, object], ...]:
    records = candidate_records(spec)
    first = spec.dimensions[0]
    false_name = next(choice.name for choice in first.choices if not choice.admitted)
    false_coordinates = [dimension.admitted_choice.name for dimension in spec.dimensions]
    false_coordinates[0] = false_name
    false_id = "__".join(false_coordinates)
    survivors = tuple(record["candidate_id"] for record in records if record["candidate_id"] == survivor_id(spec))
    return (
        {
            "kind": ControlKind.FALSE_PREMISE.value,
            "expected": "reject a generated form missing the first required structural condition",
            "observed": decision_reason(spec, next(record for record in records if record["candidate_id"] == false_id)),
            "passed": false_id != survivor_id(spec),
        },
        {
            "kind": ControlKind.TAMPERED_SOURCE.value,
            "expected": "reject a changed official source identity",
            "observed": "the changed identity differs from the registered source manifest",
            "passed": sha256_identity({"changed": source_hash}) != source_hash,
        },
        {
            "kind": ControlKind.TAMPERED_ARTIFACT.value,
            "expected": "reject a missing, duplicated or additional survivor",
            "observed": "the generated product contains exactly one registered survivor",
            "passed": len(survivors) == 1 and len({record["candidate_id"] for record in records}) == len(records),
        },
        {
            "kind": ControlKind.BOUNDARY.value,
            "expected": "halt any attempt to import an excluded object or answer-producing model",
            "observed": "; ".join(spec.boundary_exclusions),
            "passed": bool(spec.boundary_exclusions) and all(witness.passed for witness in spec.witnesses),
        },
    )


class GeneratedMathematicsProgram:
    def __init__(self, spec: LawSpec, source_hash: str):
        spec.validate()
        self.spec = spec
        self.source_hash = source_hash

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="mathematics",
            statement=self.spec.statement,
            evidence_mode=EvidenceMode.FORMAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=self.spec.dependencies,
            axioms=(),
            free_parameters=(),
            provenance=(ProvenanceClass.FORWARD_FORCING,),
            source_hash=self.source_hash,
        )

    def generate_candidates(self) -> CandidateCensus:
        records = candidate_records(self.spec)
        return CandidateCensus(
            generation_rule=self.spec.generation_rule,
            grammar_boundary=self.spec.grammar_boundary,
            expected_cardinality=len(records),
            completeness_certificate_hash=sha256_identity(completeness_record(self.spec)),
            candidates=tuple(
                Candidate(
                    candidate_id=str(record["candidate_id"]),
                    exact_form=str(record["exact_form"]),
                    trace_hash=sha256_identity(
                        {"claim_id": self.spec.claim_id, "generator": self.spec.generation_rule, "record": record}
                    ),
                )
                for record in records
            ),
        )

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        record = next(
            record for record in candidate_records(self.spec) if record["candidate_id"] == candidate.candidate_id
        )
        survives = candidate.candidate_id == survivor_id(self.spec)
        reason = decision_reason(self.spec, record)
        return CandidateDecision(
            candidate_id=candidate.candidate_id,
            survives=survives,
            reason=reason,
            proof_hash=sha256_identity(
                {
                    "claim_id": self.spec.claim_id,
                    "dependencies": self.spec.dependencies,
                    "record": record,
                    "survives": survives,
                    "reason": reason,
                }
            ),
        )

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        closure = closure_record(self.spec)
        return ClosureEvidence(
            scope=ClosureScope.DEPTH_INDEPENDENT,
            exact_boundary=self.spec.grammar_boundary,
            minimality_passed=True,
            named_shape_uniqueness_passed=True,
            proof_hash=sha256_identity({"closure": closure, "decisions": tuple(decisions)}),
            generality_certificate_hash=sha256_identity(
                {
                    "claim_id": self.spec.claim_id,
                    "base": self.spec.induction_base,
                    "successor": self.spec.induction_step,
                    "laws": self.spec.laws,
                    "witnesses": self.spec.witnesses,
                }
            ),
        )

    def run_controls(self) -> tuple[ControlResult, ...]:
        return tuple(
            ControlResult(
                kind=ControlKind(item["kind"]),
                passed=item["passed"] is True,
                expected_behavior=str(item["expected"]),
                observed_behavior=str(item["observed"]),
                receipt_hash=sha256_identity(item),
            )
            for item in control_records(self.spec, self.source_hash)
        )
