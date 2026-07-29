"""Capability-closed ECHEM-013 storage-handoff validation."""
import hashlib
import json
import platform
from pathlib import Path

from sft.chemistry.echem_storage_handoff_batch_v1 import ANALYSIS_PATH, AUTHORITIES, STORAGE_SPEC
from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


def digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def exact_analysis(root: Path, omit_last: bool = False):
    for path, expected in AUTHORITIES:
        if hash_file(root / path) != expected:
            raise ValueError(f"ECHEM-013 authority changed: {path}")
    analysis = json.loads((root / ANALYSIS_PATH).read_text())
    vector = dict(analysis)
    recorded = vector.pop("complete_result_vector_sha256")
    if recorded != digest(json.dumps(vector, sort_keys=True, separators=(",", ":")).encode()):
        raise ValueError("ECHEM-013 result vector changed")
    owners = analysis["complete_ownership_vector"]
    certificates = analysis["complete_admitted_certificate_vector"]
    source = analysis["complete_nist_source"]
    if hash_file(root / source["snapshot_path"]) != source["snapshot_sha256"] or (root / source["snapshot_path"]).stat().st_size != source["byte_count"]:
        raise ValueError("ECHEM-013 NIST source reconstruction changed")
    checks = {
        "SFT-CHEM-ECHEM-013-CHEMISTRY-OWNER": owners[0]["owner"] == "chemistry" and owners[0]["claim_id"] == certificates["chemistry"]["claim_id"],
        "SFT-CHEM-ECHEM-013-MATERIALS-OWNER": owners[1]["owner"] == "materials" and owners[1]["claim_id"] == certificates["materials"]["claim_id"],
        "SFT-CHEM-ECHEM-013-ENGINEERING-BOUNDARY": owners[2]["owner"] == "engineering" and owners[2]["claim_id"] == certificates["engineering"]["claim_id"],
        "SFT-CHEM-ECHEM-013-UNIQUE-OWNERSHIP": analysis["one_owner_per_coordinate"] and analysis["complete_owner_count"] == 3,
        "SFT-CHEM-ECHEM-013-DIRECTED-HANDOFF": len(analysis["directed_handoff_vector"]) == 2,
        "SFT-CHEM-ECHEM-013-PAIRED-RECORDS": all(row["engine_receipt_hash"].startswith("sha256:") for row in certificates.values()),
        "SFT-CHEM-ECHEM-013-EXTERNAL-MATERIAL-SURFACE": source["byte_count"] == 97292 and all(analysis["nist_material_performance_correspondence"].values()),
        "SFT-CHEM-ECHEM-013-NO-DUPLICATE-OWNERSHIP": analysis["duplicate_ownership_rows"] == [] and analysis["cross_branch_handoff_adds_no_duplicate_natural_law_or_application_selected_rule"],
    }
    if omit_last:
        checks.pop(next(reversed(checks)))
    if tuple(checks) != tuple(row.target_id for row in STORAGE_SPEC.target_rows) or not all(checks.values()):
        raise ValueError("ECHEM-013 comparison changed")
    return {"complete_owner_count": 3, "complete_directed_handoff_count": 2, "complete_nist_source_bytes": 97292, "complete_admitted_certificate_count": 3, "complete_result_vector_sha256": recorded, "development_observed_source_surface_disclosed": analysis["source_surface_development_observed_before_claim_specific_extraction"]}, checks


class StorageHandoffValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        STORAGE_SPEC.validate()
        analysis, checks = exact_analysis(self.root)
        registration = observational_experiment_registration_record(STORAGE_SPEC)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(STORAGE_SPEC)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(STORAGE_SPEC.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(checks), sealed.seal_hash, registration_hash)
        vault = TargetVault(experiment_id=STORAGE_SPEC.experiment_id, custodian_id=STORAGE_SPEC.experiment_id + "-external-target-custodian", targets={target: HeldLabel("external-observation", STORAGE_SPEC.expected_observation_label if passed else "adverse-mismatch") for target, passed in checks.items()}, custody_nonce=sha256_identity((registration_hash, analysis["complete_result_vector_sha256"])), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("ECHEM-013 prediction package changed")
        release = vault.release(prediction)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction)
        boundary.measurement_context(release.targets)
        comparisons = tuple({"target_id": target, "predicted": execution.output.label, "observed": release.targets[target].label, "passed": execution.output.label == release.targets[target].label} for target in checks)
        try:
            exact_analysis(self.root, True)
            omission = False
        except ValueError:
            omission = True
        passed = all(row["passed"] for row in comparisons) and omission
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=STORAGE_SPEC.experiment_id + "-prediction-executor", host_platform=platform.system() or "host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-echem-storage-handoff/1", STORAGE_SPEC.falsification_condition)), prediction_seal_hash=prediction.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ECHEM-013 target changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction.seal_hash, "analysis": analysis, "comparisons": comparisons, "omission_rejected": omission, "trace": execution.trace_hash}
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row.source_id for row in STORAGE_SPEC.target_rows), ("three admitted branch-owner certificates retained", "two directed handoffs and complete 97,292-byte NIST Materials source retained", "development-observed source status disclosed and never relabelled blind"), sha256_identity(payload), STORAGE_SPEC.falsification_condition, passed)


__all__ = ("StorageHandoffValidator", "exact_analysis")
