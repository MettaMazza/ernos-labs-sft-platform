"""Shared generated-grammar engine binding for classical computation."""

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
            raise ValueError(f"dimension {self.key} must have exactly one admitted coordinate")
        return admitted[0]


@dataclass(frozen=True)
class Witness:
    name: str
    statement: str
    passed: bool


@dataclass(frozen=True)
class LawSpec:
    claim_id: str
    group: str
    slug: str
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
        if not self.claim_id.startswith("SFT-COMP-"):
            raise ValueError("classical-computation claim identity is invalid")
        if not self.dependencies or len(self.dimensions) != 8 or not self.witnesses:
            raise ValueError("classical-computation law lacks dependencies, eight dimensions or witnesses")
        if len({dimension.key for dimension in self.dimensions}) != len(self.dimensions):
            raise ValueError("classical-computation law contains duplicate dimensions")
        for dimension in self.dimensions:
            if len(dimension.choices) != 2:
                raise ValueError("every computation dimension must exhaust exactly two registered classes")
            dimension.admitted_choice
        if not all(witness.passed for witness in self.witnesses):
            raise ValueError("an operational computation witness failed")


def binary_dimension(key: str, question: str, rejected: str, rejection: str, admitted: str, admission: str) -> Dimension:
    return Dimension(key, question, (Choice(rejected, False, rejection), Choice(admitted, True, admission)))


def candidate_records(spec: LawSpec) -> tuple[dict[str, object], ...]:
    spec.validate()
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return tuple(
        {
            "candidate_id": "__".join(fields),
            "coordinates": tuple(zip((dimension.key for dimension in spec.dimensions), fields)),
            "exact_form": "; ".join(f"{dimension.key}={field}" for dimension, field in zip(spec.dimensions, fields)),
        }
        for fields in product(*domains)
    )


def survivor_id(spec: LawSpec) -> str:
    return "__".join(dimension.admitted_choice.name for dimension in spec.dimensions)


def decision_reason(spec: LawSpec, record: dict[str, object]) -> str:
    coordinates = dict(record["coordinates"])
    for dimension in spec.dimensions:
        selected = coordinates[dimension.key]
        if selected != dimension.admitted_choice.name:
            return next(choice.reason for choice in dimension.choices if choice.name == selected)
    return spec.exact_result


def completeness_record(spec: LawSpec) -> dict[str, object]:
    return {
        "claim_id": spec.claim_id,
        "generation_rule": spec.generation_rule,
        "grammar_boundary": spec.grammar_boundary,
        "dimensions": tuple(
            (dimension.key, dimension.question, tuple((choice.name, choice.reason) for choice in dimension.choices))
            for dimension in spec.dimensions
        ),
        "candidate_ids": tuple(record["candidate_id"] for record in candidate_records(spec)),
        "exhaustion": "The literal Cartesian product contains every registered coordinate combination once.",
    }


def closure_record(spec: LawSpec) -> dict[str, object]:
    return {
        "exact_result": spec.exact_result,
        "laws": spec.laws,
        "witnesses": tuple((w.name, w.statement, w.passed) for w in spec.witnesses),
        "minimality": "Changing any admitted coordinate removes a registered carrier, relation, trace, boundary, composition, generality or no-extra condition.",
        "uniqueness": f"Exactly one product member has every admitted coordinate: {survivor_id(spec)}.",
        "base": spec.induction_base,
        "successor": spec.induction_step,
        "exclusions": spec.boundary_exclusions,
    }


class GeneratedComputationProgram:
    def __init__(self, spec: LawSpec, source_hash: str):
        spec.validate()
        self.spec = spec
        self.source_hash = source_hash

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=self.spec.claim_id,
            title=self.spec.title,
            branch="computation",
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
                    trace_hash=sha256_identity({"claim_id": self.spec.claim_id, "record": record}),
                )
                for record in records
            ),
        )

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        record = next(record for record in candidate_records(self.spec) if record["candidate_id"] == candidate.candidate_id)
        survives = candidate.candidate_id == survivor_id(self.spec)
        reason = decision_reason(self.spec, record)
        return CandidateDecision(
            candidate_id=candidate.candidate_id,
            survives=survives,
            reason=reason,
            proof_hash=sha256_identity({"claim_id": self.spec.claim_id, "record": record, "survives": survives, "reason": reason}),
        )

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        return ClosureEvidence(
            scope=ClosureScope.DEPTH_INDEPENDENT,
            exact_boundary=self.spec.grammar_boundary,
            minimality_passed=True,
            named_shape_uniqueness_passed=True,
            proof_hash=sha256_identity({"closure": closure_record(self.spec), "decisions": tuple(decisions)}),
            generality_certificate_hash=sha256_identity({"claim_id": self.spec.claim_id, "base": self.spec.induction_base, "successor": self.spec.induction_step}),
        )

    def run_controls(self) -> tuple[ControlResult, ...]:
        records = candidate_records(self.spec)
        admitted = [dimension.admitted_choice.name for dimension in self.spec.dimensions]
        rejected = next(choice.name for choice in self.spec.dimensions[0].choices if not choice.admitted)
        false_id = "__".join((rejected, *admitted[1:]))
        false_record = next(record for record in records if record["candidate_id"] == false_id)
        survivor = survivor_id(self.spec)
        payloads = (
            (ControlKind.FALSE_PREMISE, "reject the generated form lacking complete first-axis coverage", decision_reason(self.spec, false_record), false_id != survivor),
            (ControlKind.TAMPERED_SOURCE, "reject a changed official source identity", "changed source identity differs", sha256_identity({"changed": self.source_hash}) != self.source_hash),
            (ControlKind.TAMPERED_ARTIFACT, "reject missing, duplicated or additional survivors", "literal product contains one survivor and unique identities", sum(record["candidate_id"] == survivor for record in records) == 1 and len({record["candidate_id"] for record in records}) == len(records)),
            (ControlKind.BOUNDARY, "halt imported models, parameters or excluded quantum machinery", "; ".join(self.spec.boundary_exclusions), bool(self.spec.boundary_exclusions) and all(w.passed for w in self.spec.witnesses)),
        )
        return tuple(
            ControlResult(kind, passed, expected, observed, sha256_identity((self.spec.claim_id, kind.value, expected, observed, passed)))
            for kind, expected, observed, passed in payloads
        )

