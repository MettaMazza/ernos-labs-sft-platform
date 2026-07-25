"""Public interface of the sole v3 SFT admission engine."""

from sft.engine.authority import AuthorityLedger
from sft.engine.engine import ENGINE_ID, ROOT_THEOREM, SFTAdmissionEngine
from sft.engine.errors import EngineHalt
from sft.engine.external import ExternalCommandValidator, ExternalValidatorError
from sft.engine.isolation import (
    CrossPlatformIsolationVerifier,
    IsolationCertificate,
    IsolationError,
    REQUIRED_DENIED_CAPABILITIES,
    TargetCustodyCertificate,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.repository import CensusAdmissionError, EngineRepository
from sft.engine.portable import (
    SUPPORTED_HOST_FAMILIES,
    host_family,
    portable_subprocess_environment,
)
from sft.engine.model import (
    Candidate,
    CandidateCensus,
    CandidateDecision,
    ClaimRegistration,
    ClosureEvidence,
    ClosureScope,
    ControlKind,
    ControlResult,
    EmpiricalValidation,
    EngineReceipt,
    EvidenceMode,
    ExternalValidation,
    GateResult,
    ProvenanceClass,
    SealedDerivation,
)

__all__ = [
    "AuthorityLedger",
    "Candidate",
    "CandidateCensus",
    "CandidateDecision",
    "CensusAdmissionError",
    "ClaimRegistration",
    "ClosureEvidence",
    "ClosureScope",
    "ControlKind",
    "ControlResult",
    "ENGINE_ID",
    "EmpiricalValidation",
    "EngineHalt",
    "EngineRepository",
    "EngineReceipt",
    "EvidenceMode",
    "ExternalCommandValidator",
    "ExternalValidation",
    "ExternalValidatorError",
    "IsolationCertificate",
    "IsolationError",
    "TargetCustodyCertificate",
    "CrossPlatformIsolationVerifier",
    "REQUIRED_DENIED_CAPABILITIES",
    "GateResult",
    "ProvenanceClass",
    "ROOT_THEOREM",
    "SFTAdmissionEngine",
    "SealedDerivation",
    "SUPPORTED_HOST_FAMILIES",
    "host_family",
    "portable_subprocess_environment",
    "seal_isolation_certificate",
    "seal_target_custody_certificate",
    "unsealed_isolation_certificate",
    "unsealed_target_custody_certificate",
]
