"""Typed evidence objects consumed and emitted by the single admission engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Protocol, Sequence

from sft.engine.isolation import IsolationCertificate, TargetCustodyCertificate


class EvidenceMode(str, Enum):
    FORMAL = "formal"
    EMPIRICAL = "empirical"


class ProvenanceClass(str, Enum):
    DIRECT_FORCING = "direct_forcing"
    FORWARD_FORCING = "forward_forcing"
    CONSTITUTIONAL_RELATION = "constitutional_relation"
    OBSERVATIONAL_DERIVATION = "observational_derivation"


class ControlKind(str, Enum):
    FALSE_PREMISE = "false_premise"
    TAMPERED_SOURCE = "tampered_source"
    TAMPERED_ARTIFACT = "tampered_artifact"
    BOUNDARY = "boundary"


class ClosureScope(str, Enum):
    CONDITIONAL_GRAMMAR = "conditional_grammar"
    FINITE_COMPLETE = "finite_complete"
    DEPTH_INDEPENDENT = "depth_independent"


@dataclass(frozen=True)
class ClaimRegistration:
    claim_id: str
    title: str
    branch: str
    statement: str
    evidence_mode: EvidenceMode
    root_theorems: tuple[str, ...]
    dependencies: tuple[str, ...]
    axioms: tuple[str, ...]
    free_parameters: tuple[str, ...]
    provenance: tuple[ProvenanceClass, ...]
    source_hash: str


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    exact_form: str
    trace_hash: str


@dataclass(frozen=True)
class CandidateCensus:
    generation_rule: str
    grammar_boundary: str
    expected_cardinality: int
    completeness_certificate_hash: str
    candidates: tuple[Candidate, ...]


@dataclass(frozen=True)
class CandidateDecision:
    candidate_id: str
    survives: bool
    reason: str
    proof_hash: str


@dataclass(frozen=True)
class ClosureEvidence:
    scope: ClosureScope
    exact_boundary: str
    minimality_passed: bool
    named_shape_uniqueness_passed: bool
    proof_hash: str
    generality_certificate_hash: Optional[str] = None


@dataclass(frozen=True)
class ControlResult:
    kind: ControlKind
    passed: bool
    expected_behavior: str
    observed_behavior: str
    receipt_hash: str


@dataclass(frozen=True)
class SealedDerivation:
    claim_id: str
    source_hash: str
    census: CandidateCensus
    decisions: tuple[CandidateDecision, ...]
    closure: ClosureEvidence
    controls: tuple[ControlResult, ...]
    seal_hash: str


@dataclass(frozen=True)
class ExternalValidation:
    validator_id: str
    implementation_hash: str
    validated_seal_hash: str
    certificate_hash: str
    recomputed_from_declared_inputs: bool
    passed: bool


@dataclass(frozen=True)
class EmpiricalValidation:
    validated_seal_hash: str
    experiment_registration_hash: str
    isolation_certificate: IsolationCertificate
    target_custody_certificate: TargetCustodyCertificate
    evaluator_verified_seal: bool
    target_opened_after_seal: bool
    all_rows_preserved: bool
    data_source_ids: tuple[str, ...]
    measurements: tuple[str, ...]
    measurement_receipt_hash: str
    falsification_condition: str
    passed: bool


@dataclass(frozen=True)
class GateResult:
    gate: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class EngineReceipt:
    engine_id: str
    claim_id: str
    accepted_evidence: bool
    model_admitted: bool
    closure_status: str
    external_status: str
    halted_stage: Optional[str]
    violations: tuple[str, ...]
    gate_results: tuple[GateResult, ...]
    derivation_seal_hash: Optional[str]
    receipt_hash: str = field(compare=False)


class DerivationProgram(Protocol):
    @property
    def registration(self) -> ClaimRegistration: ...

    def generate_candidates(self) -> CandidateCensus: ...

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision: ...

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence: ...

    def run_controls(self) -> tuple[ControlResult, ...]: ...


class IndependentValidator(Protocol):
    def validate(self, sealed: SealedDerivation) -> ExternalValidation: ...


class EmpiricalValidator(Protocol):
    def validate(self, sealed: SealedDerivation) -> EmpiricalValidation: ...
