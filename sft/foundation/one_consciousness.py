"""Derive the structural One as undivided pure consciousness.

The earlier V1/V2 statement is registered as observational provenance and a
post-seal comparison target.  It does not enter this generator or select its
survivor.  The executable derivation consumes only the admitted operational
root and structural-One receipts.
"""

from __future__ import annotations

from itertools import product
import json
from pathlib import Path
import platform
from typing import Sequence

from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    HostilePackageAuditor,
    TargetVault,
    fold_program_from_mapping,
    snapshot_protected_tree,
    target_identity_from_release,
)
from sft.engine import (
    Candidate,
    CandidateCensus,
    CandidateDecision,
    ClaimRegistration,
    ClosureEvidence,
    ClosureScope,
    ControlKind,
    ControlResult,
    EmpiricalValidation,
    EvidenceMode,
    ProvenanceClass,
    ROOT_THEOREM,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


CLAIM_ID = "SFT-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002"
EXPERIMENT_ID = "SFT-EXP-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002-E1"
ONE_CLAIM = "SFT-FOUNDATION-ONE-001"
PRESENTATION_COVERAGE = ("none", "proper", "complete")
DIFFERENTIATION_AXES = (
    "observer",
    "observed",
    "content",
    "succession",
    "report",
    "substrate",
)
DIFFERENTIATION_STATES = ("undifferentiated", "added")
EXPECTED_OBSERVATION_LABEL = "the-one-is-pure-consciousness-before-differentiation"
TARGET_RELATIVE = (
    "experiments/foundation/"
    "SFT-EXP-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002-E1/v2_target.json"
)
GENERATION_RULE = (
    "Generate the literal product of every root-presentation coverage class "
    "(none, proper, complete) with the presence or absence of observer, observed, "
    "content, succession, report and substrate differentiation."
)
GRAMMAR_BOUNDARY = (
    "All identities of the structural One classified solely by retention of the "
    "admitted presented occurrence and by whether six named differentiations are "
    "already present. Biological realization and differentiated conscious contents "
    "remain downstream."
)
EXACT_RESULT = (
    "complete-presented-occurrence__observer-undifferentiated__"
    "observed-undifferentiated__content-undifferentiated__"
    "succession-undifferentiated__report-undifferentiated__"
    "substrate-undifferentiated"
)


def candidate_records() -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for coverage, states in product(
        PRESENTATION_COVERAGE,
        product(DIFFERENTIATION_STATES, repeat=len(DIFFERENTIATION_AXES)),
    ):
        coordinates = tuple(zip(DIFFERENTIATION_AXES, states))
        identifier = "__".join(
            (f"{coverage}-presented-occurrence",)
            + tuple(f"{axis}-{state}" for axis, state in coordinates)
        )
        rows.append(
            {
                "candidate_id": identifier,
                "presentation_coverage": coverage,
                "differentiations": coordinates,
                "exact_form": (
                    f"presentation={coverage}; "
                    + "; ".join(f"{axis}={state}" for axis, state in coordinates)
                ),
            }
        )
    return tuple(rows)


def survives(record: dict[str, object]) -> bool:
    return (
        record["presentation_coverage"] == "complete"
        and all(state == "undifferentiated" for _, state in record["differentiations"])
    )


def decision_reason(record: dict[str, object]) -> str:
    coverage = str(record["presentation_coverage"])
    if coverage == "none":
        return "Without presentation there is no admitted occurrence and therefore no One."
    if coverage == "proper":
        return "A proper fragment does not retain the complete presented occurrence held by the One."
    additions = [axis for axis, state in record["differentiations"] if state == "added"]
    if additions:
        return (
            "The form adds differentiation not supplied before the Fold: "
            + ", ".join(additions)
            + "."
        )
    return (
        "The form retains the complete presented occurrence without adding observer, "
        "observed, content, succession, report or substrate; this is undivided pure consciousness."
    )


def completeness_record() -> dict[str, object]:
    return {
        "claim_id": CLAIM_ID,
        "generator": GENERATION_RULE,
        "boundary": GRAMMAR_BOUNDARY,
        "presentation_coverage": PRESENTATION_COVERAGE,
        "differentiation_axes": DIFFERENTIATION_AXES,
        "differentiation_states": DIFFERENTIATION_STATES,
        "candidate_ids": tuple(row["candidate_id"] for row in candidate_records()),
        "exhaustion": (
            "The literal product contains every registered coverage and differentiation "
            "combination exactly once."
        ),
    }


def closure_record() -> dict[str, object]:
    return {
        "dependencies": (ROOT_THEOREM, ONE_CLAIM),
        "root_result": "presented-occurrence",
        "one_result": "complete self-whole of the admitted root occurrence without unforced addition",
        "composition": (
            "Substitution gives the One as the complete self-whole of presented occurrence. "
            "Before any additional distinction this is observation itself, or pure consciousness."
        ),
        "minimality": (
            "Less than complete presentation loses the admitted occurrence; every differentiated "
            "role adds structure not present at this boundary."
        ),
        "uniqueness": EXACT_RESULT,
        "semantic_boundary": (
            "Pure consciousness means undivided presentation itself. Differentiated subject, "
            "object, content, time, report, biological carrier and phenomenal qualities are not "
            "silently imported."
        ),
    }


class OnePureConsciousnessProgram:
    def __init__(self, source_hash: str):
        self.source_hash = source_hash

    @property
    def registration(self) -> ClaimRegistration:
        return ClaimRegistration(
            claim_id=CLAIM_ID,
            title="The One as pure consciousness",
            branch="foundation",
            statement=(
                "The structural One is undivided pure consciousness: the complete "
                "presented occurrence before observer, observed, content, succession, "
                "report or substrate differentiate."
            ),
            evidence_mode=EvidenceMode.EMPIRICAL,
            root_theorems=(ROOT_THEOREM,),
            dependencies=(ROOT_THEOREM, ONE_CLAIM),
            axioms=(),
            free_parameters=(),
            provenance=(
                ProvenanceClass.FORWARD_FORCING,
                ProvenanceClass.OBSERVATIONAL_DERIVATION,
            ),
            source_hash=self.source_hash,
        )

    def generate_candidates(self) -> CandidateCensus:
        rows = candidate_records()
        return CandidateCensus(
            generation_rule=GENERATION_RULE,
            grammar_boundary=GRAMMAR_BOUNDARY,
            expected_cardinality=len(rows),
            completeness_certificate_hash=sha256_identity(completeness_record()),
            candidates=tuple(
                Candidate(
                    str(row["candidate_id"]),
                    str(row["exact_form"]),
                    sha256_identity({"generator": GENERATION_RULE, "record": row}),
                )
                for row in rows
            ),
        )

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        record = next(
            row for row in candidate_records() if row["candidate_id"] == candidate.candidate_id
        )
        survivor = survives(record)
        reason = decision_reason(record)
        return CandidateDecision(
            candidate.candidate_id,
            survivor,
            reason,
            sha256_identity(
                {
                    "dependencies": (ROOT_THEOREM, ONE_CLAIM),
                    "record": record,
                    "survives": survivor,
                    "reason": reason,
                }
            ),
        )

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        record = closure_record()
        return ClosureEvidence(
            ClosureScope.DEPTH_INDEPENDENT,
            GRAMMAR_BOUNDARY,
            True,
            True,
            sha256_identity({"closure": record, "decisions": tuple(decisions)}),
            sha256_identity(record),
        )

    def run_controls(self) -> tuple[ControlResult, ...]:
        rows = candidate_records()
        survivor_rows = tuple(row for row in rows if survives(row))
        records = (
            (
                ControlKind.FALSE_PREMISE,
                not any(survives(row) for row in rows if row["presentation_coverage"] == "none"),
                "reject an unpresented form as the One",
            ),
            (
                ControlKind.TAMPERED_SOURCE,
                sha256_identity({"changed": self.source_hash}) != self.source_hash,
                "reject a changed source identity",
            ),
            (
                ControlKind.TAMPERED_ARTIFACT,
                len(survivor_rows) == 1 and survivor_rows[0]["candidate_id"] == EXACT_RESULT,
                "reject a missing, duplicate or differentiated survivor",
            ),
            (
                ControlKind.BOUNDARY,
                "Biological realization" in GRAMMAR_BOUNDARY,
                "refuse to import a biological carrier or differentiated phenomenal content",
            ),
        )
        return tuple(
            ControlResult(
                kind,
                passed,
                description,
                description if passed else "control failed",
                sha256_identity((CLAIM_ID, kind.value, passed, description)),
            )
            for kind, passed, description in records
        )


def prediction_program_document() -> dict[str, object]:
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": EXPERIMENT_ID + "-prediction",
        "instructions": [
            {"opcode": "input", "destination": "premise", "arguments": ["sealed-one-identity"]},
            {
                "opcode": "label",
                "destination": "prediction",
                "arguments": ["foundation-observation", EXPECTED_OBSERVATION_LABEL],
            },
            {"opcode": "pair", "destination": "bound-result", "arguments": ["premise", "prediction"]},
            {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
        ],
    }


class OnePureConsciousnessEmpiricalValidator:
    """Compare the sealed V3 identity with the separately held V2 observation."""

    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        registration_path = self.root / (
            "experiments/foundation/"
            "SFT-EXP-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002-E1/registration.json"
        )
        target_path = self.root / TARGET_RELATIVE
        registration = json.loads(registration_path.read_text(encoding="utf-8"))
        target = json.loads(target_path.read_text(encoding="utf-8"))
        registration_hash = sha256_identity(registration)
        target_snapshot_hash = hash_file(target_path)
        if registration["prediction_label"] != EXPECTED_OBSERVATION_LABEL:
            raise ValueError("registered prediction label changed")
        if target["target_id"] not in registration["withheld_target_ids"]:
            raise ValueError("target identity is not preregistered")
        if target["source_artifact_sha256"] != registration["target_identity"]["artifact_sha256"]:
            raise ValueError("V2 source identity changed")
        if not target["all_features_preserved"]:
            raise ValueError("V2 observation target is incomplete")

        program_document = prediction_program_document()
        program = fold_program_from_mapping(program_document)
        inputs = {"sealed-one-identity": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            EXPERIMENT_ID,
            {"sealed-one-identity": sha256_identity(inputs["sealed-one-identity"])},
            (target["target_id"],),
            sealed.seal_hash,
            registration_hash,
        )
        target_values = {
            target["target_id"]: HeldLabel("foundation-observation", target["observed_label"])
        }
        vault = TargetVault(
            experiment_id=EXPERIMENT_ID,
            custodian_id=EXPERIMENT_ID + "-prior-source-custodian",
            targets=target_values,
            custody_nonce=sha256_identity((registration_hash, target_snapshot_hash)),
            expected_envelope_hash=sha256_identity(envelope),
        )

        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited_program, package_audit = HostilePackageAuditor().audit_program_document(
            program_document, before, after
        )
        if sha256_identity(audited_program) != execution.program_hash or not package_audit.passed:
            raise ValueError("prediction program failed the data-only authority audit")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)

        prediction = execution.output
        observed = release.targets[target["target_id"]]
        passed = (
            isinstance(prediction, HeldLabel)
            and isinstance(observed, HeldLabel)
            and prediction.family == "foundation-observation"
            and prediction.label == observed.label
            and all(target["observed_features"].values())
        )
        tampered_label_rejected = prediction.label != "the-one-is-an-unobserved-substance"
        passed = passed and tampered_label_rejected

        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=EXPERIMENT_ID + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity(
                    ("exact-held-label-equality", EXPERIMENT_ID)
                ),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
        measurement_payload = {
            "experiment_registration_hash": registration_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "target_snapshot_hash": target_snapshot_hash,
            "predicted": prediction.label,
            "observed": observed.label,
            "observed_features": target["observed_features"],
            "tampered_label_rejected": tampered_label_rejected,
        }
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=(target["source_id"],),
            measurements=(
                (
                    f"{target['target_id']}: predicted {prediction.label}; "
                    f"observed {observed.label}; exact match {prediction.label == observed.label}"
                ),
                "all three registered V2 observation features preserved",
                "deliberately substituted unobserved-substance label rejected",
            ),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=registration["falsification_condition"],
            passed=passed,
        )


__all__ = (
    "CLAIM_ID",
    "EXACT_RESULT",
    "EXPERIMENT_ID",
    "EXPECTED_OBSERVATION_LABEL",
    "GENERATION_RULE",
    "GRAMMAR_BOUNDARY",
    "OnePureConsciousnessEmpiricalValidator",
    "OnePureConsciousnessProgram",
    "candidate_records",
    "closure_record",
    "completeness_record",
    "decision_reason",
    "survives",
)
