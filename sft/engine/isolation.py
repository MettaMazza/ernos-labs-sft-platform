"""Portable capability and custody certificates for blind empirical work.

This module deliberately does not pretend that Python can impose an operating-
system sandbox uniformly.  Official prediction code must instead execute in a
capability-closed SFT language, while target material is held by a distinct
custody phase until the prediction has been sealed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from sft.engine.canonical import is_sha256_identity, sha256_identity


class IsolationError(RuntimeError):
    """Raised when a portable isolation certificate is incomplete or false."""


REQUIRED_DENIED_CAPABILITIES = (
    "clock",
    "dynamic_import",
    "environment",
    "filesystem_read",
    "filesystem_write",
    "foreign_function",
    "network",
    "subprocess",
)


@dataclass(frozen=True)
class IsolationCertificate:
    """Evidence that a prediction used only its registered capabilities.

    The certificate is portable evidence about an SFT interpreter run, not an
    assertion about a host-specific sandbox.  `host_platform` is metadata only
    and cannot change policy or scientific behavior.
    """

    adapter_id: str
    executor_id: str
    host_platform: str
    python_implementation: str
    interpreter_hash: str
    program_hash: str
    input_manifest_hash: str
    registered_target_identity_hash: str
    comparison_implementation_identity_hash: str
    prediction_seal_hash: str
    denied_capabilities: tuple[str, ...]
    attempted_forbidden_operations: tuple[str, ...]
    target_material_present: bool
    comparison_code_present: bool
    output_hash: str
    trace_hash: str
    completed: bool
    certificate_hash: str


@dataclass(frozen=True)
class TargetCustodyCertificate:
    """Evidence that a distinct custodian released targets only after sealing."""

    adapter_id: str
    custodian_id: str
    experiment_registration_hash: str
    registered_target_identity_hash: str
    prediction_seal_hash: str
    target_release_manifest_hash: str
    target_absent_until_prediction_seal: bool
    released_after_prediction_seal: bool
    certificate_hash: str


def isolation_certificate_payload(certificate: IsolationCertificate) -> dict[str, object]:
    """Return the certificate fields covered by its identity hash."""

    payload = asdict(certificate)
    payload.pop("certificate_hash")
    return payload


def seal_isolation_certificate(certificate: IsolationCertificate) -> IsolationCertificate:
    """Seal an unsealed certificate after an authorized interpreter run.

    This helper computes identity only.  It does not turn an arbitrary Python
    process into a capability-closed interpreter.
    """

    return replace(
        certificate,
        certificate_hash=sha256_identity(isolation_certificate_payload(certificate)),
    )


def target_custody_certificate_payload(
    certificate: TargetCustodyCertificate,
) -> dict[str, object]:
    payload = asdict(certificate)
    payload.pop("certificate_hash")
    return payload


def seal_target_custody_certificate(
    certificate: TargetCustodyCertificate,
) -> TargetCustodyCertificate:
    return replace(
        certificate,
        certificate_hash=sha256_identity(target_custody_certificate_payload(certificate)),
    )


class CrossPlatformIsolationVerifier:
    """Apply one capability policy on macOS, Windows and Linux."""

    adapter_id = "sft-portable-capability-custody/1"

    def violations(self, certificate: IsolationCertificate) -> tuple[str, ...]:
        violations: list[str] = []
        if certificate.adapter_id != self.adapter_id:
            violations.append("isolation adapter identity is not the portable SFT adapter")
        if not certificate.executor_id.strip():
            violations.append("prediction executor identity is missing")
        for label, value in (
            ("interpreter", certificate.interpreter_hash),
            ("program", certificate.program_hash),
            ("input manifest", certificate.input_manifest_hash),
            ("registered target identity", certificate.registered_target_identity_hash),
            ("comparison implementation identity", certificate.comparison_implementation_identity_hash),
            ("prediction seal", certificate.prediction_seal_hash),
            ("output", certificate.output_hash),
            ("trace", certificate.trace_hash),
            ("certificate", certificate.certificate_hash),
        ):
            if not is_sha256_identity(value):
                violations.append(f"{label} hash is invalid")
        if tuple(sorted(certificate.denied_capabilities)) != REQUIRED_DENIED_CAPABILITIES:
            violations.append("denied capabilities do not exactly match the portable policy")
        if certificate.attempted_forbidden_operations:
            violations.append("prediction attempted a forbidden capability")
        if certificate.target_material_present:
            violations.append("target material entered the prediction capability set")
        if certificate.comparison_code_present:
            violations.append("comparison code entered the prediction capability set")
        if not certificate.completed:
            violations.append("capability-closed prediction did not complete")
        expected = sha256_identity(isolation_certificate_payload(certificate))
        if certificate.certificate_hash != expected:
            violations.append("isolation certificate identity does not match its contents")
        if not certificate.host_platform.strip():
            violations.append("host platform metadata is missing")
        if not certificate.python_implementation.strip():
            violations.append("Python implementation metadata is missing")
        return tuple(violations)

    def verify(self, certificate: IsolationCertificate) -> None:
        violations = self.violations(certificate)
        if violations:
            raise IsolationError("; ".join(violations))

    def custody_violations(
        self,
        certificate: TargetCustodyCertificate,
        isolation: IsolationCertificate,
    ) -> tuple[str, ...]:
        violations: list[str] = []
        if certificate.adapter_id != self.adapter_id:
            violations.append("custody adapter identity is not the portable SFT adapter")
        if not certificate.custodian_id.strip():
            violations.append("target custodian identity is missing")
        if certificate.custodian_id == isolation.executor_id:
            violations.append("target custodian and prediction executor must be distinct")
        for label, value in (
            ("experiment registration", certificate.experiment_registration_hash),
            ("registered target identity", certificate.registered_target_identity_hash),
            ("prediction seal", certificate.prediction_seal_hash),
            ("target release manifest", certificate.target_release_manifest_hash),
            ("custody certificate", certificate.certificate_hash),
        ):
            if not is_sha256_identity(value):
                violations.append(f"{label} hash is invalid")
        if certificate.registered_target_identity_hash != isolation.registered_target_identity_hash:
            violations.append("custody and prediction target identities differ")
        if certificate.prediction_seal_hash != isolation.prediction_seal_hash:
            violations.append("custody and prediction seal identities differ")
        if not certificate.target_absent_until_prediction_seal:
            violations.append("custodian released target material before prediction sealing")
        if not certificate.released_after_prediction_seal:
            violations.append("custodian did not record a post-seal target release")
        expected = sha256_identity(target_custody_certificate_payload(certificate))
        if certificate.certificate_hash != expected:
            violations.append("target custody certificate identity does not match its contents")
        return tuple(violations)

    def verify_custody(
        self,
        certificate: TargetCustodyCertificate,
        isolation: IsolationCertificate,
    ) -> None:
        violations = self.custody_violations(certificate, isolation)
        if violations:
            raise IsolationError("; ".join(violations))


def unsealed_isolation_certificate(
    *,
    executor_id: str,
    host_platform: str,
    python_implementation: str,
    interpreter_hash: str,
    program_hash: str,
    input_manifest_hash: str,
    registered_target_identity_hash: str,
    comparison_implementation_identity_hash: str,
    prediction_seal_hash: str,
    output_hash: str,
    trace_hash: str,
    attempted_forbidden_operations: tuple[str, ...] = (),
    target_material_present: bool = False,
    comparison_code_present: bool = False,
    completed: bool = True,
) -> IsolationCertificate:
    """Construct the pre-seal record emitted by the portable interpreter.

    Official callers remain responsible for supplying records produced by the
    registered interpreter.  Independent validation checks those records.
    """

    return IsolationCertificate(
        adapter_id=CrossPlatformIsolationVerifier.adapter_id,
        executor_id=executor_id,
        host_platform=host_platform,
        python_implementation=python_implementation,
        interpreter_hash=interpreter_hash,
        program_hash=program_hash,
        input_manifest_hash=input_manifest_hash,
        registered_target_identity_hash=registered_target_identity_hash,
        comparison_implementation_identity_hash=comparison_implementation_identity_hash,
        prediction_seal_hash=prediction_seal_hash,
        denied_capabilities=REQUIRED_DENIED_CAPABILITIES,
        attempted_forbidden_operations=attempted_forbidden_operations,
        target_material_present=target_material_present,
        comparison_code_present=comparison_code_present,
        output_hash=output_hash,
        trace_hash=trace_hash,
        completed=completed,
        certificate_hash="",
    )


def unsealed_target_custody_certificate(
    *,
    custodian_id: str,
    experiment_registration_hash: str,
    registered_target_identity_hash: str,
    prediction_seal_hash: str,
    target_release_manifest_hash: str,
    target_absent_until_prediction_seal: bool = True,
    released_after_prediction_seal: bool = True,
) -> TargetCustodyCertificate:
    return TargetCustodyCertificate(
        adapter_id=CrossPlatformIsolationVerifier.adapter_id,
        custodian_id=custodian_id,
        experiment_registration_hash=experiment_registration_hash,
        registered_target_identity_hash=registered_target_identity_hash,
        prediction_seal_hash=prediction_seal_hash,
        target_release_manifest_hash=target_release_manifest_hash,
        target_absent_until_prediction_seal=target_absent_until_prediction_seal,
        released_after_prediction_seal=released_after_prediction_seal,
        certificate_hash="",
    )
