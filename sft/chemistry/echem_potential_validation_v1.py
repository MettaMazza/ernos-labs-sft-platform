"""Capability-closed external validation for separate ECHEM-002, 003 and 004 claims."""
import hashlib
import json
import platform
from pathlib import Path
from pypdf import PdfReader
from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.echem_potential_batch_v1 import ANALYSIS_PATH, AUTHORITIES, CELL_POTENTIAL_SPEC, CONCENTRATION_POTENTIAL_SPEC, ELECTRODE_POTENTIAL_SPEC, PDF_PATH
from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file

def digest(payload): return "sha256:" + hashlib.sha256(payload).hexdigest()

def exact_analysis(root: Path, claim_id: str, omit_last=False):
    for path, expected in AUTHORITIES:
        if hash_file(root / path) != expected: raise ValueError(f"ECHEM-002-004 authority changed: {path}")
    analysis = json.loads((root / ANALYSIS_PATH).read_text())
    vector = dict(analysis); recorded = vector.pop("complete_result_vector_sha256")
    if recorded != digest(json.dumps(vector, sort_keys=True, separators=(",", ":")).encode()): raise ValueError("ECHEM-002-004 result vector changed")
    pages = []
    for number, page in enumerate(PdfReader(root / PDF_PATH).pages, start=1):
        text = "\n".join(line.strip() for line in (page.extract_text() or "").replace("\u00ad", "").splitlines() if line.strip())
        pages.append({"page": number, "complete_extracted_text": text, "text_sha256": digest(text.encode()), "character_count": len(text)})
    if pages != analysis["complete_pages_in_order"] or len(pages) != 8 or sum(row["character_count"] for row in pages) != 37013: raise ValueError("complete NIST PDF reconstruction changed")
    if claim_id == ELECTRODE_POTENTIAL_SPEC.claim_id:
        row = analysis["echem_002"]
        checks = {
            "SFT-CHEM-ECHEM-002-STANDARD-ROWS": row["complete_standard_potential_row_count"] == 17 and len(row["complete_standard_potential_rows"]) == 17,
            "SFT-CHEM-ECHEM-002-REFERENCE-CONDITION": row["reference_and_condition_retained"],
            "SFT-CHEM-ECHEM-002-DIRECTION-VECTOR": row["all_observed_potentials_strictly_descend_with_temperature"],
            "SFT-CHEM-ECHEM-002-UNCERTAINTY-VECTOR": len(row["standard_deviation_vector_source_inscriptions"]) == 17,
            "SFT-CHEM-ECHEM-002-ADVERSE-DIFFERENCE": row["adverse_cross_study_difference_and_unexplained_result_retained"],
            "SFT-CHEM-ECHEM-002-MODEL-PROVENANCE": row["least_squares_and_adjustable_parameter_provenance_retained"],
            "SFT-CHEM-ECHEM-002-COMPLETE-PDF": analysis["complete_pdf_page_count"] == 8,
        }
        summary = {"complete_standard_potential_rows": 17, "temperature_range_celsius_source_inscriptions": ["0", "95"], "complete_pdf_pages": 8, "complete_pdf_characters": 37013, "adverse_cross_study_difference_retained": True}
    elif claim_id == CELL_POTENTIAL_SPEC.claim_id:
        row = analysis["echem_003"]
        checks = {
            "SFT-CHEM-ECHEM-003-CELL-CARRIERS": row["two_hydrogen_and_two_silver_chloride_electrodes_retained"],
            "SFT-CHEM-ECHEM-003-NO-LIQUID-JUNCTION": row["cell_without_liquid_junction_retained"],
            "SFT-CHEM-ECHEM-003-EMF-ROWS": row["complete_smoothed_emf_row_count"] == 88 and len(row["complete_smoothed_emf_rows"]) == 8,
            "SFT-CHEM-ECHEM-003-MOLALITY-DIRECTION": row["every_fixed_temperature_emf_column_strictly_descends_with_molality"],
            "SFT-CHEM-ECHEM-003-CORRECTIONS": row["measurement_corrections_and_unapplied_corrections_retained"],
            "SFT-CHEM-ECHEM-003-REVERSAL-CONVENTION": analysis["echem_002"]["convention_reversal_retained"],
            "SFT-CHEM-ECHEM-003-COMPLETE-PDF": analysis["complete_pdf_page_count"] == 8,
        }
        summary = {"complete_cell_emf_measurements": 88, "complete_molality_rows": 8, "complete_temperature_columns": 11, "complete_pdf_pages": 8, "complete_pdf_characters": 37013, "unapplied_corrections_retained": True}
    elif claim_id == CONCENTRATION_POTENTIAL_SPEC.claim_id:
        row = analysis["echem_004"]
        checks = {
            "SFT-CHEM-ECHEM-004-MOLALITY-TEMPERATURE-SUPPORT": row["complete_molality_count"] == 8 and row["complete_temperature_count"] == 11,
            "SFT-CHEM-ECHEM-004-EMF-ROWS": row["complete_emf_measurement_count"] == 88,
            "SFT-CHEM-ECHEM-004-ACTIVITY-ROWS": row["complete_activity_coefficient_measurement_count"] == 88,
            "SFT-CHEM-ECHEM-004-POTENTIAL-DIRECTION": row["every_fixed_temperature_emf_column_strictly_descends_with_molality"],
            "SFT-CHEM-ECHEM-004-ACTIVITY-DIRECTION": row["every_fixed_temperature_activity_column_strictly_descends_with_molality"],
            "SFT-CHEM-ECHEM-004-MODEL-PROVENANCE": row["source_logarithm_Debye_Huckel_least_squares_and_smoothing_models_retained_only_as_external_provenance"],
            "SFT-CHEM-ECHEM-004-ADVERSE-BEHAVIOR": row["source_explicitly_reports_anomalous_or_unexplained_behavior"],
            "SFT-CHEM-ECHEM-004-COMPLETE-PDF": analysis["complete_pdf_page_count"] == 8,
        }
        summary = {"complete_emf_measurements": 88, "complete_activity_measurements": 88, "complete_molality_rows": 8, "complete_temperature_columns": 11, "complete_pdf_pages": 8, "complete_pdf_characters": 37013, "adverse_anomaly_retained": True}
    else: raise ValueError("unknown ECHEM-002-004 claim")
    if omit_last: checks.pop(next(reversed(checks)))
    spec = {ELECTRODE_POTENTIAL_SPEC.claim_id: ELECTRODE_POTENTIAL_SPEC, CELL_POTENTIAL_SPEC.claim_id: CELL_POTENTIAL_SPEC, CONCENTRATION_POTENTIAL_SPEC.claim_id: CONCENTRATION_POTENTIAL_SPEC}[claim_id]
    if tuple(checks) != tuple(row.target_id for row in spec.target_rows) or not all(checks.values()): raise ValueError(f"{claim_id} comparison changed")
    return {**summary, "complete_result_vector_sha256": recorded, "all_conventional_signed_zero_decimal_continuum_fitted_and_smoothed_inscriptions_retained_as_external_provenance_only": True}, checks

class _Validator:
    def __init__(self, root, spec): self.root, self.spec = root.resolve(), spec
    def validate(self, sealed):
        self.spec.validate(); analysis, checks = exact_analysis(self.root, self.spec.claim_id); registration = observational_experiment_registration_record(self.spec); registration_hash = sha256_identity(registration); document = prediction_program_document(self.spec); program = fold_program_from_mapping(document); inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}; envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(checks), sealed.seal_hash, registration_hash); vault = TargetVault(experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-external-target-custodian", targets={target: HeldLabel("external-observation", self.spec.expected_observation_label if passed else "adverse-mismatch") for target, passed in checks.items()}, custody_nonce=sha256_identity((registration_hash, analysis["complete_result_vector_sha256"])), expected_envelope_hash=sha256_identity(envelope)); before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs); boundary = BlindExperimentBoundary(envelope); prediction = boundary.seal_prediction(execution.output, execution.trace); after = snapshot_protected_tree(self.root); audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError("ECHEM prediction package changed")
        release = vault.release(prediction); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction); boundary.measurement_context(release.targets); comparisons = tuple({"target_id": target, "predicted": execution.output.label, "observed": release.targets[target].label, "passed": execution.output.label == release.targets[target].label} for target in checks)
        try: exact_analysis(self.root, self.spec.claim_id, True); omission = False
        except ValueError: omission = True
        passed = all(row["passed"] for row in comparisons) and omission; isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-echem-potential-batch/1", self.spec.claim_id, self.spec.falsification_condition)), prediction_seal_hash=prediction.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash)); target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash: raise ValueError("ECHEM target changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction.seal_hash, target_release_manifest_hash=release.release_hash)); payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction.seal_hash, "analysis": analysis, "comparisons": comparisons, "omission_rejected": omission, "trace": execution.trace_hash}; notes = ("complete eight-page NIST Ag/AgCl source retained", f"all {len(checks)} separately registered claim targets retained", "all conventional values signs zero glyphs fitted equations smoothing corrections uncertainties adverse and absent records remain downstream provenance")
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row.source_id for row in self.spec.target_rows), notes, sha256_identity(payload), self.spec.falsification_condition, passed)

class ElectrodePotentialValidator(_Validator):
    def __init__(self, root): super().__init__(root, ELECTRODE_POTENTIAL_SPEC)
class CellPotentialValidator(_Validator):
    def __init__(self, root): super().__init__(root, CELL_POTENTIAL_SPEC)
class ConcentrationPotentialValidator(_Validator):
    def __init__(self, root): super().__init__(root, CONCENTRATION_POTENTIAL_SPEC)
__all__ = ("CellPotentialValidator", "ConcentrationPotentialValidator", "ElectrodePotentialValidator", "exact_analysis")
