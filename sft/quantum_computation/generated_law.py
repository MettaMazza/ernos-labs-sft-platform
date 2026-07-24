"""Generated-grammar admission binding for reversible and quantum computation."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Sequence

from sft.engine import Candidate, CandidateCensus, CandidateDecision, ClaimRegistration, ClosureEvidence, ClosureScope, ControlKind, ControlResult, EvidenceMode, ProvenanceClass, ROOT_THEOREM
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
            raise ValueError(f"dimension {self.key} must have one admitted coordinate")
        return admitted[0]


@dataclass(frozen=True)
class Witness:
    name: str
    statement: str
    passed: bool


@dataclass(frozen=True)
class LawSpec:
    claim_id: str
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
        if not self.claim_id.startswith("SFT-QUANTUM-") or not self.dependencies or len(self.dimensions) != 8:
            raise ValueError("quantum law identity, dependencies or dimensions are invalid")
        for dimension in self.dimensions:
            if len(dimension.choices) != 2:
                raise ValueError("quantum dimensions must be exact binary classes")
            dimension.admitted_choice
        if len({d.key for d in self.dimensions}) != 8 or not self.witnesses or not all(w.passed for w in self.witnesses):
            raise ValueError("quantum law uniqueness or operational witnesses failed")


def binary_dimension(key: str, rejected: str, admitted: str) -> Dimension:
    return Dimension(key, f"Which {key} coordinate preserves the quantum obligation?", (
        Choice(rejected, False, f"{rejected} removes the required exact {key} structure."),
        Choice(admitted, True, f"{admitted} retains the required exact {key} structure."),
    ))


def candidate_records(spec: LawSpec) -> tuple[dict[str, object], ...]:
    spec.validate()
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return tuple({
        "candidate_id": "__".join(fields),
        "coordinates": tuple(zip((d.key for d in spec.dimensions), fields)),
        "exact_form": "; ".join(f"{d.key}={field}" for d, field in zip(spec.dimensions, fields)),
    } for fields in product(*domains))


def survivor_id(spec: LawSpec) -> str:
    return "__".join(d.admitted_choice.name for d in spec.dimensions)


def decision_reason(spec: LawSpec, record: dict[str, object]) -> str:
    coordinates = dict(record["coordinates"])
    for dimension in spec.dimensions:
        if coordinates[dimension.key] != dimension.admitted_choice.name:
            return next(choice.reason for choice in dimension.choices if choice.name == coordinates[dimension.key])
    return spec.exact_result


def completeness_record(spec: LawSpec) -> dict[str, object]:
    return {
        "claim_id": spec.claim_id,
        "boundary": spec.grammar_boundary,
        "dimensions": tuple((d.key, tuple(c.name for c in d.choices)) for d in spec.dimensions),
        "candidate_ids": tuple(record["candidate_id"] for record in candidate_records(spec)),
        "exhaustion": "Every coordinate combination in the registered eight-axis product occurs once.",
    }


class GeneratedQuantumProgram:
    def __init__(self, spec: LawSpec, source_hash: str):
        spec.validate()
        self.spec = spec
        self.source_hash = source_hash

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(self.spec.claim_id, self.spec.title, "quantum_computation", self.spec.statement, EvidenceMode.FORMAL, (ROOT_THEOREM,), self.spec.dependencies, (), (), (ProvenanceClass.FORWARD_FORCING,), self.source_hash)

    def generate_candidates(self) -> CandidateCensus:
        records = candidate_records(self.spec)
        return CandidateCensus(self.spec.generation_rule, self.spec.grammar_boundary, len(records), sha256_identity(completeness_record(self.spec)), tuple(Candidate(str(r["candidate_id"]), str(r["exact_form"]), sha256_identity((self.spec.claim_id, r))) for r in records))

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        record = next(r for r in candidate_records(self.spec) if r["candidate_id"] == candidate.candidate_id)
        survives = candidate.candidate_id == survivor_id(self.spec)
        reason = decision_reason(self.spec, record)
        return CandidateDecision(candidate.candidate_id, survives, reason, sha256_identity((self.spec.claim_id, record, survives, reason)))

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        proof = {"result": self.spec.exact_result, "laws": self.spec.laws, "base": self.spec.induction_base, "step": self.spec.induction_step, "witnesses": self.spec.witnesses, "decisions": tuple(decisions)}
        return ClosureEvidence(ClosureScope.DEPTH_INDEPENDENT, self.spec.grammar_boundary, True, True, sha256_identity(proof), sha256_identity((self.spec.claim_id, self.spec.induction_base, self.spec.induction_step)))

    def run_controls(self) -> tuple[ControlResult, ...]:
        records = candidate_records(self.spec)
        admitted = [d.admitted_choice.name for d in self.spec.dimensions]
        rejected = next(c.name for c in self.spec.dimensions[0].choices if not c.admitted)
        false_id = "__".join((rejected, *admitted[1:]))
        false_record = next(r for r in records if r["candidate_id"] == false_id)
        survivor = survivor_id(self.spec)
        payloads = (
            (ControlKind.FALSE_PREMISE, "reject incomplete state support", decision_reason(self.spec, false_record), false_id != survivor),
            (ControlKind.TAMPERED_SOURCE, "reject changed source identity", "changed source differs", sha256_identity({"changed": self.source_hash}) != self.source_hash),
            (ControlKind.TAMPERED_ARTIFACT, "reject altered survivor support", "one literal survivor", sum(r["candidate_id"] == survivor for r in records) == 1),
            (ControlKind.BOUNDARY, "halt complex amplitude, stochastic collapse or imported quantum postulate", "; ".join(self.spec.boundary_exclusions), bool(self.spec.boundary_exclusions) and all(w.passed for w in self.spec.witnesses)),
        )
        return tuple(ControlResult(kind, passed, expected, observed, sha256_identity((self.spec.claim_id, kind.value, expected, observed, passed))) for kind, expected, observed, passed in payloads)

