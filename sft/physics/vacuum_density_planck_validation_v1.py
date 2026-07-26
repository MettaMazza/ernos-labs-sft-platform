"""Exact post-seal validation of the complete Planck/CODATA vacuum record."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

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
    EmpiricalValidation,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import experiment_registration_record, prediction_program_document
from sft.physics.vacuum_density_planck_empirical_v1 import (
    CLAIM_ID,
    CODATA_HASH,
    CODATA_PATH,
    EXPERIMENT_ID,
    OBSERVATION_LABEL,
    PDF_HASH,
    PDF_PATH,
    SOURCE_HASH,
    SOURCE_IDS,
    SOURCE_PATH,
    SPEC,
)


TARGET_IDS = ("PLANCK-CODATA-WITHHELD-COMPLETE-VACUUM-SCALE-RECORD",)
FALSIFICATION_CONDITION = SPEC.falsification_condition


def source_hashes() -> dict[str, str]:
    return {SOURCE_PATH: SOURCE_HASH, PDF_PATH: PDF_HASH, CODATA_PATH: CODATA_HASH}


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"vacuum-density source identity changed: {relative}")
    record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
    if record.get("schema") != "sft-v3-vacuum-density-planck-postseal-source-record/1":
        raise ValueError("vacuum-density source schema changed")
    if record.get("formal_receipt_hash") != "sha256:c7b4777b12fc70628b0fd9a2f7d957274b61ede7f3624a665781364c8c9f7723":
        raise ValueError("formal vacuum receipt binding changed")
    sources = record.get("sources", ())
    if len(sources) != 2:
        raise ValueError("complete Planck/CODATA source pair is required")
    planck, codata = sources
    if planck.get("snapshot_hash") != PDF_HASH or planck.get("source_page") != 225:
        raise ValueError("Planck primary-table binding changed")
    if codata.get("snapshot_hash") != CODATA_HASH:
        raise ValueError("CODATA speed binding changed")
    target = record.get("registered_target", {})
    expected = {
        "planck_hubble_central_km_s_mpc": "67.68",
        "planck_hubble_standard_uncertainty_km_s_mpc": "0.42",
        "planck_vacuum_fraction_central": "0.6889",
        "planck_vacuum_fraction_standard_uncertainty": "0.0056",
        "planck_matter_fraction_central": "0.3111",
        "planck_matter_fraction_standard_uncertainty": "0.0056",
        "codata_speed_km_s": "299792.458",
        "planck_page": 225,
    }
    if any(target.get(key) != value for key, value in expected.items()):
        raise ValueError("Planck/CODATA target row changed")
    if target.get("all_registered_rows_retained") is not True or target.get("older_hubble_transcription_corrected_without_rewriting_prior_receipts") is not True:
        raise ValueError("Planck correction or row-retention control changed")
    custody = record.get("row_custody", {})
    if not all(custody.get(key) is True for key in (
        "formal_receipt_precedes_primary_pdf_retrieval",
        "target_inaccessible_to_formal_executable",
        "target_did_not_rewrite_formal_survivor",
        "complete_uncertainty_rows_retained",
        "local_floor_and_global_fraction_kept_separate",
        "dimensional_transport_uses_held_external_references_only",
        "unfavorable_type_control_retained",
    )):
        raise ValueError("Planck/CODATA custody record changed")
    return record


def exact_vacuum_analysis(target: dict[str, object]) -> dict[str, object]:
    vacuum = Fraction(target["planck_vacuum_fraction_central"])
    vacuum_width = Fraction(target["planck_vacuum_fraction_standard_uncertainty"])
    matter = Fraction(target["planck_matter_fraction_central"])
    matter_width = Fraction(target["planck_matter_fraction_standard_uncertainty"])
    hubble = Fraction(target["planck_hubble_central_km_s_mpc"])
    hubble_width = Fraction(target["planck_hubble_standard_uncertainty_km_s_mpc"])
    speed = Fraction(target["codata_speed_km_s"])
    vacuum_lower, vacuum_upper = vacuum - vacuum_width, vacuum + vacuum_width
    normalized_lower, normalized_upper = 3 * vacuum_lower, 3 * vacuum_upper
    predicted_share = Fraction(11, 16)
    predicted_normalized = Fraction(33, 16)
    hubble_lower, hubble_upper = hubble - hubble_width, hubble + hubble_width
    lambda_lower = predicted_normalized * (hubble_lower / speed) ** 2
    lambda_central = predicted_normalized * (hubble / speed) ** 2
    lambda_upper = predicted_normalized * (hubble_upper / speed) ** 2
    local_floor = Fraction(1, 2 ** 20)
    return {
        "vacuum_interval": (vacuum_lower, vacuum_upper),
        "matter_interval": (matter - matter_width, matter + matter_width),
        "predicted_share": predicted_share,
        "share_inside_interval": vacuum_lower <= predicted_share <= vacuum_upper,
        "normalized_interval": (normalized_lower, normalized_upper),
        "predicted_normalized": predicted_normalized,
        "normalized_inside_interval": normalized_lower <= predicted_normalized <= normalized_upper,
        "central_budget_closes": vacuum + matter == 1,
        "hubble_interval": (hubble_lower, hubble_upper),
        "lambda_mpc_inverse_square_interval": (lambda_lower, lambda_upper),
        "lambda_mpc_inverse_square_central": lambda_central,
        "dimensional_transport_positive": 0 < lambda_lower < lambda_central < lambda_upper,
        "local_floor": local_floor,
        "local_floor_outside_global_interval": local_floor < vacuum_lower,
        "half_one_mode_mean_outside_global_interval": Fraction(1, 2) < vacuum_lower,
        "primary_hubble_correction_retained": target["older_hubble_transcription_corrected_without_rewriting_prior_receipts"] and hubble == Fraction("67.68"),
        "all_rows_retained": target["all_registered_rows_retained"],
    }


class VacuumDensityPlanckValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong vacuum-density comparison seal")
        registration = experiment_registration_record(SPEC)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(SPEC)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(EXPERIMENT_ID, {"registered-premise": sha256_identity(inputs["registered-premise"])}, TARGET_IDS, sealed.seal_hash, registration_hash)
        targets = {TARGET_IDS[0]: authoritative_record(self.root)["registered_target"]}
        vault = TargetVault(
            experiment_id=EXPERIMENT_ID,
            custodian_id=EXPERIMENT_ID + "-external-target-custodian",
            targets=targets,
            custody_nonce=sha256_identity((registration_hash, source_hashes())),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("vacuum-density prediction package audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if not isinstance(execution.output, HeldLabel) or execution.output.family != "physical-observation" or execution.output.label != OBSERVATION_LABEL:
            raise ValueError("vacuum-density prediction label changed")
        analysis = exact_vacuum_analysis(context[TARGET_IDS[0]])
        formal = all(row[2] for row in SPEC.operational_witnesses)
        empirical = all((
            analysis["share_inside_interval"],
            analysis["normalized_inside_interval"],
            analysis["central_budget_closes"],
            analysis["dimensional_transport_positive"],
            analysis["local_floor_outside_global_interval"],
            analysis["half_one_mode_mean_outside_global_interval"],
            analysis["primary_hubble_correction_retained"],
            analysis["all_rows_retained"],
        ))
        tampered = dict(context[TARGET_IDS[0]])
        tampered["planck_vacuum_fraction_central"] = "0.6000"
        tampered_rejected = not exact_vacuum_analysis(tampered)["share_inside_interval"]
        passed = formal and empirical and tampered_rejected
        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity(("exact-vacuum-density-Planck-comparator/1", registration_hash, FALSIFICATION_CONDITION))
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=interpreter_hash,
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=comparator_hash,
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {
            "seal": sealed.seal_hash,
            "prediction_seal": prediction_seal.seal_hash,
            "source_hashes": source_hashes(),
            "target_identity": target_identity,
            "analysis": analysis,
            "formal": formal,
            "empirical": empirical,
            "tampered_rejected": tampered_rejected,
            "trace": execution.trace_hash,
        }
        measurements = (
            "The formal vacuum-density law was admitted before the primary Planck PDF was retrieved.",
            "Historical V1/V2 targets and an older local transcription were known; no historical-blindness claim is made.",
            "The exact 11/16 vacuum share lies inside the complete Planck 0.6889 +/- 0.0056 interval.",
            "The exact 33/16 normalized magnitude lies inside the three-direction transported Planck interval.",
            "Page 225 directly reports H0=67.68 +/- 0.42; the older 67.66 transcription is corrected here without rewriting prior receipts.",
            "CODATA exact c transports the sealed coefficient to a positive exact inverse-square-megaparsec interval.",
            "One/2^20 and the finite-ledger mean remain outside the global fraction interval, preserving their distinct types.",
            "A tampered vacuum central value of 0.6000 rejects the registered comparison.",
        )
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            analysis["all_rows_retained"],
            SOURCE_IDS,
            measurements,
            sha256_identity(payload),
            FALSIFICATION_CONDITION,
            passed,
        )


__all__ = ("FALSIFICATION_CONDITION", "TARGET_IDS", "VacuumDensityPlanckValidator", "authoritative_record", "exact_vacuum_analysis", "source_hashes")
