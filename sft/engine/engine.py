"""Fail-closed orchestration for every v3 SFT derivation."""

from __future__ import annotations

from dataclasses import asdict
from typing import Iterable, Optional

from sft.engine.authority import AuthorityLedger
from sft.engine.canonical import is_sha256_identity, sha256_identity
from sft.engine.errors import EngineHalt
from sft.engine.isolation import CrossPlatformIsolationVerifier
from sft.engine.model import (
    CandidateCensus,
    CandidateDecision,
    ClaimRegistration,
    ClosureEvidence,
    ClosureScope,
    ControlKind,
    ControlResult,
    DerivationProgram,
    EmpiricalValidation,
    EmpiricalValidator,
    EngineReceipt,
    EvidenceMode,
    ExternalValidation,
    GateResult,
    IndependentValidator,
    ProvenanceClass,
    SealedDerivation,
)


ENGINE_ID = "sft-v3-single-admission-engine/1"
ROOT_THEOREM = "SFT-ROOT-THERE-IS-NO-NOTHING"
REQUIRED_CONTROLS = frozenset(ControlKind)
ALLOWED_PROVENANCE = frozenset(ProvenanceClass)


class SFTAdmissionEngine:
    """Run one derivation through every applicable SFT admission gate."""

    def __init__(self, authority: Optional[AuthorityLedger] = None):
        self.authority = authority if authority is not None else AuthorityLedger()

    def run(
        self,
        program: DerivationProgram,
        independent_validator: IndependentValidator,
        empirical_validator: Optional[EmpiricalValidator] = None,
        executed_source_hash: Optional[str] = None,
    ) -> EngineReceipt:
        gates: list[GateResult] = []
        registration = program.registration

        violations = self._registration_violations(registration, executed_source_hash)
        self._require(
            registration.claim_id,
            "registration",
            violations,
            gates,
            "one theorem, no axioms, zero free parameters and admitted dependencies",
        )

        try:
            census = program.generate_candidates()
        except Exception as exc:
            self._halt(registration.claim_id, "enumeration", (f"candidate generator raised: {exc}",), gates)
        violations = self._census_violations(census)
        self._require(
            registration.claim_id,
            "enumeration",
            violations,
            gates,
            "generated candidate census matches its registered complete boundary",
        )

        decisions: list[CandidateDecision] = []
        try:
            for candidate in census.candidates:
                decisions.append(program.decide_candidate(candidate))
        except Exception as exc:
            self._halt(registration.claim_id, "forcing", (f"candidate decision raised: {exc}",), gates)
        decision_tuple = tuple(decisions)
        violations = self._decision_violations(census, decision_tuple)
        self._require(
            registration.claim_id,
            "forcing",
            violations,
            gates,
            "every generated candidate decided and exactly one survivor remains",
        )

        try:
            closure = program.closure_evidence(decision_tuple)
        except Exception as exc:
            self._halt(registration.claim_id, "form_closure", (f"closure proof raised: {exc}",), gates)
        violations = self._closure_violations(closure)
        self._require(
            registration.claim_id,
            "form_closure",
            violations,
            gates,
            "minimality and named-shape uniqueness established at the exact boundary",
        )

        try:
            controls = program.run_controls()
        except Exception as exc:
            self._halt(registration.claim_id, "controls", (f"control execution raised: {exc}",), gates)
        violations = self._control_violations(controls)
        self._require(
            registration.claim_id,
            "controls",
            violations,
            gates,
            "all required false, tampered and boundary controls behaved as registered",
        )

        seal_hash = sha256_identity(
            {
                "engine_id": ENGINE_ID,
                "registration": registration,
                "census": census,
                "decisions": decision_tuple,
                "closure": closure,
                "controls": controls,
            }
        )
        sealed = SealedDerivation(
            claim_id=registration.claim_id,
            source_hash=registration.source_hash,
            census=census,
            decisions=decision_tuple,
            closure=closure,
            controls=controls,
            seal_hash=seal_hash,
        )
        gates.append(GateResult("seal", True, "derivation, census, closure and controls sealed"))

        try:
            external = independent_validator.validate(sealed)
        except Exception as exc:
            self._halt(registration.claim_id, "independent_validation", (f"validator raised: {exc}",), gates, seal_hash)
        external_validation_hash = sha256_identity(external)
        violations = self._external_violations(registration, sealed, external)
        self._require(
            registration.claim_id,
            "independent_validation",
            violations,
            gates,
            "distinct implementation recomputed the sealed result from declared inputs",
            seal_hash,
            external_validation_hash,
        )

        external_status = "independently_replicated"
        empirical_validation_hash = None
        if registration.evidence_mode is EvidenceMode.EMPIRICAL:
            if empirical_validator is None:
                self._halt(
                    registration.claim_id,
                    "empirical_validation",
                    ("empirical claim has no blind empirical validator",),
                    gates,
                    seal_hash,
                    external_validation_hash,
                )
            try:
                empirical = empirical_validator.validate(sealed)
            except Exception as exc:
                self._halt(
                    registration.claim_id,
                    "empirical_validation",
                    (f"empirical validator raised: {exc}",),
                    gates,
                    seal_hash,
                    external_validation_hash,
                )
            empirical_validation_hash = sha256_identity(empirical)
            violations = self._empirical_violations(sealed, empirical)
            self._require(
                registration.claim_id,
                "empirical_validation",
                violations,
                gates,
                "target-inaccessible prediction sealed before independent data measurement",
                seal_hash,
                external_validation_hash,
                empirical_validation_hash,
            )
            external_status = "empirically_tested_and_independently_replicated"
        elif empirical_validator is not None:
            self._halt(
                registration.claim_id,
                "empirical_validation",
                ("formal claim supplied empirical evidence without registering empirical mode",),
                gates,
                seal_hash,
                external_validation_hash,
            )

        model_admitted = closure.scope in {
            ClosureScope.FINITE_COMPLETE,
            ClosureScope.DEPTH_INDEPENDENT,
        }
        gates.append(
            GateResult(
                "model_admission",
                model_admitted,
                "closed law may become a dependency"
                if model_admitted
                else "conditional evidence preserved but barred from model dependency",
            )
        )
        return self._make_receipt(
            claim_id=registration.claim_id,
            accepted_evidence=True,
            model_admitted=model_admitted,
            closure_status=closure.scope.value,
            external_status=external_status,
            halted_stage=None,
            violations=(),
            gates=tuple(gates),
            seal_hash=seal_hash,
            external_validation_hash=external_validation_hash,
            empirical_validation_hash=empirical_validation_hash,
        )

    def _registration_violations(
        self,
        registration: ClaimRegistration,
        executed_source_hash: Optional[str],
    ) -> tuple[str, ...]:
        violations: list[str] = []
        for field_name in ("claim_id", "title", "branch", "statement"):
            value = getattr(registration, field_name)
            if not isinstance(value, str) or not value.strip():
                violations.append(f"{field_name} is missing")
        if registration.claim_id == ROOT_THEOREM:
            if registration.root_theorems:
                violations.append("the root theorem cannot cite itself as a premise")
            if registration.dependencies:
                violations.append("the root theorem cannot depend on a prior model claim")
        elif registration.root_theorems != (ROOT_THEOREM,):
            violations.append("foundation trace must contain exactly the single self-proven root theorem")
        if registration.axioms:
            violations.append("axioms are forbidden")
        if registration.free_parameters:
            violations.append("free, fitted or learned parameters are forbidden")
        if len(set(registration.dependencies)) != len(registration.dependencies):
            violations.append("dependency list contains duplicates")
        missing = [claim_id for claim_id in registration.dependencies if not self.authority.contains(claim_id)]
        if missing:
            violations.append("dependencies lack model-admitted receipts: " + ", ".join(sorted(missing)))
        if not registration.provenance:
            violations.append("derivation provenance is unclassified")
        invalid_provenance = [item for item in registration.provenance if item not in ALLOWED_PROVENANCE]
        if invalid_provenance:
            violations.append("inadmissible derivation provenance is present")
        if not isinstance(registration.evidence_mode, EvidenceMode):
            violations.append("evidence mode is invalid")
        if not is_sha256_identity(registration.source_hash):
            violations.append("source hash is not a canonical SHA-256 identity")
        if executed_source_hash is not None:
            if not is_sha256_identity(executed_source_hash):
                violations.append("executed source manifest hash is invalid")
            elif registration.source_hash != executed_source_hash:
                violations.append("registered source hash differs from the files loaded by the official runner")
        return tuple(violations)

    @staticmethod
    def _census_violations(census: CandidateCensus) -> tuple[str, ...]:
        violations: list[str] = []
        if not census.generation_rule.strip():
            violations.append("candidate generation rule is missing")
        if not census.grammar_boundary.strip():
            violations.append("candidate grammar boundary is missing")
        if isinstance(census.expected_cardinality, bool) or census.expected_cardinality < 1:
            violations.append("expected candidate cardinality must be a positive count")
        if len(census.candidates) != census.expected_cardinality:
            violations.append("generated candidate count does not match the registered cardinality")
        identifiers = [candidate.candidate_id for candidate in census.candidates]
        if len(set(identifiers)) != len(identifiers):
            violations.append("candidate census contains duplicate identifiers")
        if any(not candidate.candidate_id.strip() or not candidate.exact_form.strip() for candidate in census.candidates):
            violations.append("candidate identifiers and exact forms must be named")
        if any(not is_sha256_identity(candidate.trace_hash) for candidate in census.candidates):
            violations.append("every candidate requires a canonical trace hash")
        if not is_sha256_identity(census.completeness_certificate_hash):
            violations.append("candidate census lacks a completeness certificate hash")
        return tuple(violations)

    @staticmethod
    def _decision_violations(
        census: CandidateCensus,
        decisions: tuple[CandidateDecision, ...],
    ) -> tuple[str, ...]:
        violations: list[str] = []
        expected_ids = [candidate.candidate_id for candidate in census.candidates]
        decision_ids = [decision.candidate_id for decision in decisions]
        if decision_ids != expected_ids:
            violations.append("decisions do not correspond one-for-one with the generated census")
        survivors = [decision for decision in decisions if decision.survives]
        if len(survivors) != 1:
            violations.append("forcing did not leave exactly one survivor")
        if any(not decision.reason.strip() for decision in decisions):
            violations.append("every candidate decision requires an explicit reason")
        if any(not is_sha256_identity(decision.proof_hash) for decision in decisions):
            violations.append("every candidate decision requires a proof hash")
        return tuple(violations)

    @staticmethod
    def _closure_violations(closure: ClosureEvidence) -> tuple[str, ...]:
        violations: list[str] = []
        if not isinstance(closure.scope, ClosureScope):
            violations.append("closure scope is invalid")
        if not closure.exact_boundary.strip():
            violations.append("closure boundary is missing")
        if not closure.minimality_passed:
            violations.append("minimality gate failed")
        if not closure.named_shape_uniqueness_passed:
            violations.append("named-shape uniqueness gate failed")
        if not is_sha256_identity(closure.proof_hash):
            violations.append("closure proof hash is invalid")
        if closure.scope is ClosureScope.DEPTH_INDEPENDENT and not is_sha256_identity(
            closure.generality_certificate_hash
        ):
            violations.append("depth-independent closure lacks a generality certificate")
        return tuple(violations)

    @staticmethod
    def _control_violations(controls: tuple[ControlResult, ...]) -> tuple[str, ...]:
        violations: list[str] = []
        kinds = [control.kind for control in controls]
        missing = REQUIRED_CONTROLS.difference(kinds)
        if missing:
            violations.append("missing required controls: " + ", ".join(sorted(item.value for item in missing)))
        if len(set(kinds)) != len(kinds):
            violations.append("control kinds must not be duplicated")
        for control in controls:
            if not control.passed:
                violations.append(f"control failed: {control.kind.value}")
            if not control.expected_behavior.strip() or not control.observed_behavior.strip():
                violations.append(f"control lacks expected or observed behavior: {control.kind.value}")
            if not is_sha256_identity(control.receipt_hash):
                violations.append(f"control receipt hash is invalid: {control.kind.value}")
        return tuple(violations)

    @staticmethod
    def _external_violations(
        registration: ClaimRegistration,
        sealed: SealedDerivation,
        validation: ExternalValidation,
    ) -> tuple[str, ...]:
        violations: list[str] = []
        if not validation.validator_id.strip():
            violations.append("independent validator identity is missing")
        if not is_sha256_identity(validation.implementation_hash):
            violations.append("independent implementation hash is invalid")
        if validation.implementation_hash == registration.source_hash:
            violations.append("independent validator is not implementation-distinct")
        if validation.validated_seal_hash != sealed.seal_hash:
            violations.append("independent validator checked the wrong derivation seal")
        if not is_sha256_identity(validation.certificate_hash):
            violations.append("independent certificate hash is invalid")
        if not validation.recomputed_from_declared_inputs:
            violations.append("independent validator did not recompute from declared inputs")
        if not validation.passed:
            violations.append("independent validation failed")
        return tuple(violations)

    @staticmethod
    def _empirical_violations(
        sealed: SealedDerivation,
        validation: EmpiricalValidation,
    ) -> tuple[str, ...]:
        violations: list[str] = []
        if validation.validated_seal_hash != sealed.seal_hash:
            violations.append("empirical evaluator checked the wrong derivation seal")
        for label, value in (
            ("experiment registration", validation.experiment_registration_hash),
            ("measurement receipt", validation.measurement_receipt_hash),
        ):
            if not is_sha256_identity(value):
                violations.append(f"{label} hash is invalid")
        isolation_verifier = CrossPlatformIsolationVerifier()
        violations.extend(isolation_verifier.violations(validation.isolation_certificate))
        violations.extend(
            isolation_verifier.custody_violations(
                validation.target_custody_certificate,
                validation.isolation_certificate,
            )
        )
        custody_registration_matches = (
            validation.target_custody_certificate.experiment_registration_hash
            == validation.experiment_registration_hash
        )
        if not custody_registration_matches:
            violations.append("target custody checked the wrong experiment registration")
        required_truths = (
            ("evaluator did not verify the seal", validation.evaluator_verified_seal),
            ("target was not opened after seal", validation.target_opened_after_seal),
            ("not all favorable and unfavorable rows were preserved", validation.all_rows_preserved),
        )
        violations.extend(message for message, passed in required_truths if not passed)
        if not validation.data_source_ids:
            violations.append("empirical validation has no external data-source identity")
        if not validation.measurements:
            violations.append("empirical validation has no registered measurement")
        if not validation.falsification_condition.strip():
            violations.append("empirical falsification condition is missing")
        if not validation.passed:
            violations.append("empirical validation failed")
        return tuple(violations)

    def _require(
        self,
        claim_id: str,
        stage: str,
        violations: Iterable[str],
        gates: list[GateResult],
        pass_detail: str,
        seal_hash: Optional[str] = None,
        external_validation_hash: Optional[str] = None,
        empirical_validation_hash: Optional[str] = None,
    ) -> None:
        violation_tuple = tuple(violations)
        if violation_tuple:
            self._halt(
                claim_id,
                stage,
                violation_tuple,
                gates,
                seal_hash,
                external_validation_hash,
                empirical_validation_hash,
            )
        gates.append(GateResult(stage, True, pass_detail))

    def _halt(
        self,
        claim_id: str,
        stage: str,
        violations: tuple[str, ...],
        gates: list[GateResult],
        seal_hash: Optional[str] = None,
        external_validation_hash: Optional[str] = None,
        empirical_validation_hash: Optional[str] = None,
    ) -> None:
        gates.append(GateResult(stage, False, "; ".join(violations)))
        receipt = self._make_receipt(
            claim_id=claim_id,
            accepted_evidence=False,
            model_admitted=False,
            closure_status="not_admitted",
            external_status="not_admitted",
            halted_stage=stage,
            violations=violations,
            gates=tuple(gates),
            seal_hash=seal_hash,
            external_validation_hash=external_validation_hash,
            empirical_validation_hash=empirical_validation_hash,
        )
        raise EngineHalt(receipt)

    @staticmethod
    def _make_receipt(
        claim_id: str,
        accepted_evidence: bool,
        model_admitted: bool,
        closure_status: str,
        external_status: str,
        halted_stage: Optional[str],
        violations: tuple[str, ...],
        gates: tuple[GateResult, ...],
        seal_hash: Optional[str],
        external_validation_hash: Optional[str],
        empirical_validation_hash: Optional[str],
    ) -> EngineReceipt:
        payload = {
            "engine_id": ENGINE_ID,
            "claim_id": claim_id,
            "accepted_evidence": accepted_evidence,
            "model_admitted": model_admitted,
            "closure_status": closure_status,
            "external_status": external_status,
            "halted_stage": halted_stage,
            "violations": violations,
            "gate_results": gates,
            "derivation_seal_hash": seal_hash,
            "external_validation_hash": external_validation_hash,
            "empirical_validation_hash": empirical_validation_hash,
        }
        return EngineReceipt(receipt_hash=sha256_identity(payload), **payload)


def receipt_dict(receipt: EngineReceipt) -> dict[str, object]:
    """Return a JSON-compatible receipt representation."""

    return asdict(receipt)
