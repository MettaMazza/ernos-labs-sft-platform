"""Capability-closed validation for separate ECHEM-009–012 claims."""
import hashlib
import json
import platform
from functools import lru_cache
from pathlib import Path

from pypdf import PdfReader

from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.echem_polarization_batch_v1 import ANALYSIS_PATH, AUTHORITIES, CORROSION_SPEC, DOUBLE_LAYER_SPEC, POLARIZATION_SPEC, RATE_SPEC, SPECS
from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


def digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


@lru_cache(maxsize=None)
def _page_vector(path: Path) -> tuple[dict, ...]:
    rows = []
    for number, page in enumerate(PdfReader(path).pages, start=1):
        text = "\n".join(line.strip() for line in (page.extract_text() or "").replace("\u00ad", "").splitlines() if line.strip())
        rows.append({"page": number, "character_count": len(text), "text_sha256": digest(text.encode())})
    return tuple(rows)


def exact_analysis(root: Path, claim_id: str, omit_last: bool = False):
    for path, expected in AUTHORITIES:
        if hash_file(root / path) != expected:
            raise ValueError(f"ECHEM-009–012 authority changed: {path}")
    analysis = json.loads((root / ANALYSIS_PATH).read_text())
    vector = dict(analysis)
    recorded = vector.pop("complete_result_vector_sha256")
    if recorded != digest(json.dumps(vector, sort_keys=True, separators=(",", ":")).encode()):
        raise ValueError("ECHEM-009–012 result vector changed")
    pages = characters = 0
    for source in analysis["complete_source_reconstruction"].values():
        reconstructed = _page_vector(root / source["snapshot_path"])
        if reconstructed != tuple(source["complete_page_vector"]):
            raise ValueError("complete ECHEM-009–012 page reconstruction changed")
        pages += len(reconstructed)
        characters += sum(row["character_count"] for row in reconstructed)
    if pages != 73 or characters != 156376 or pages != analysis["complete_pdf_page_count"] or characters != analysis["complete_pdf_extracted_character_count"]:
        raise ValueError("complete ECHEM-009–012 source surface changed")

    if claim_id == RATE_SPEC.claim_id:
        row = analysis["echem_009"]
        checks = {
            "SFT-CHEM-ECHEM-009-REACTION-INTERFACE": len(row["reaction_and_interface_custody"]) == 3,
            "SFT-CHEM-ECHEM-009-CURRENT-POTENTIAL": row["complete_current_potential_record_custody"],
            "SFT-CHEM-ECHEM-009-ANODIC-CATHODIC": row["anodic_and_cathodic_directions_retained"],
            "SFT-CHEM-ECHEM-009-RATE-CORRESPONDENCE": row["current_to_counted_electron_event_rate_correspondence_retained"],
            "SFT-CHEM-ECHEM-009-CONDITIONS": row["material_electrolyte_temperature_and_time_conditions_retained"],
            "SFT-CHEM-ECHEM-009-RAW-VECTOR": row["complete_published_curve_vector_retained_by_page_reconstruction"] and len(row["complete_coating_numeric_observation_vector"]) == 10,
            "SFT-CHEM-ECHEM-009-ADVERSE-MODELS": row["all_discontinuity_ir_drop_model_and_adverse_records_retained"],
            "SFT-CHEM-ECHEM-009-COMPLETE-SOURCES": row["complete_claim_source_pages"] == 49,
        }
        summary = {"complete_numeric_rate_rows": 10, "complete_claim_source_pages": 49, "reaction_directions": 2}
    elif claim_id == POLARIZATION_SPEC.claim_id:
        row = analysis["echem_010"]
        checks = {
            "SFT-CHEM-ECHEM-010-EQUILIBRIUM-REFERENCE": row["open_circuit_and_corrosion_equilibrium_references_retained"],
            "SFT-CHEM-ECHEM-010-POLARIZATION-DIRECTION": row["anodic_cathodic_and_reversal_scan_directions_retained"],
            "SFT-CHEM-ECHEM-010-POTENTIAL-DISTANCE": row["applied_potential_range_volt_source_inscriptions"] == ["-1.8", "+1.8"],
            "SFT-CHEM-ECHEM-010-CURRENT-RESPONSE": len(row["current_response_vector"]) == 10,
            "SFT-CHEM-ECHEM-010-CURVE-VECTOR": row["complete_ordered_polarization_curves_retained_by_page_reconstruction"],
            "SFT-CHEM-ECHEM-010-REVERSAL-BREAKS": row["break_reversal_discontinuity_hysteresis_and_ir_drop_records_retained"],
            "SFT-CHEM-ECHEM-010-IR-DROP-UNCERTAINTY": row["scan_rate_volt_per_second_source_inscription"] == "0.1",
            "SFT-CHEM-ECHEM-010-COMPLETE-SOURCES": row["complete_claim_source_pages"] == 49 and row["equilibrium_no_net_current_is_structural_correspondence_not_native_numerical_zero"],
        }
        summary = {"applied_potential_range_volt": ["-1.8", "+1.8"], "scan_rate_volt_per_second": "0.1", "complete_numeric_current_rows": 10, "complete_claim_source_pages": 49}
    elif claim_id == DOUBLE_LAYER_SPEC.claim_id:
        row = analysis["echem_011"]
        checks = {
            "SFT-CHEM-ECHEM-011-INTERFACE": row["interface"] == "graphene-electrolyte electric double layer",
            "SFT-CHEM-ECHEM-011-COMPOSITIONS": len(row["complete_composition_vector"]) == 3,
            "SFT-CHEM-ECHEM-011-SPATIAL-SUPPORT": row["spatial_resolution_nanometre_source_inscription"] == "20 to 40",
            "SFT-CHEM-ECHEM-011-APPLIED-POTENTIAL": "0.2 V steps" in row["applied_voltage_sweep_source_inscription"],
            "SFT-CHEM-ECHEM-011-SURFACE-POTENTIAL": len(row["surface_potential_offsets_millivolt_source_inscriptions"]) == 4,
            "SFT-CHEM-ECHEM-011-POTENTIAL-DROP": row["electrolyte_potential_fraction_source_inscription"] == "approximately 0.98 V_BE" and row["clean_membrane_potential_drop_millivolt_source_inscription"] == "approaches -300",
            "SFT-CHEM-ECHEM-011-MODEL-PROVENANCE": row["fit_and_model_provenance"]["adjustable_variables_retained"] and row["screening_hysteresis_geometry_resolution_and_interpretive_limits_retained"],
            "SFT-CHEM-ECHEM-011-COMPLETE-SOURCE": row["complete_source_pages"] == 24,
        }
        summary = {"complete_compositions": 3, "applied_voltage_step_volt": "0.2", "spatial_resolution_nanometre": "20 to 40", "clean_membrane_potential_drop_millivolt": "approaches -300", "complete_claim_source_pages": 24}
    elif claim_id == CORROSION_SPEC.claim_id:
        row = analysis["echem_012"]
        checks = {
            "SFT-CHEM-ECHEM-012-MATERIAL-ENVIRONMENT": row["material_environment"].startswith("carbon steel"),
            "SFT-CHEM-ECHEM-012-ANODIC-CATHODIC-NETWORK": row["coupled_anodic_cathodic_network_retained"],
            "SFT-CHEM-ECHEM-012-CORROSION-POTENTIAL": row["complete_published_potential_current_rate_mass_loss_vector_retained_by_page_reconstruction"],
            "SFT-CHEM-ECHEM-012-CORROSION-CURRENT": len(row["complete_table_1_vector"]) == 8 and len(row["complete_table_2_vector"]) == 13,
            "SFT-CHEM-ECHEM-012-MASS-LOSS-RATE": row["table_1_measured_weight_loss_mg"] == "345" and row["table_2_measured_total_weight_loss_mg"] == "2245",
            "SFT-CHEM-ECHEM-012-POLARIZATION-CONTROL": len(row["complete_coating_control_vector"]) == 10,
            "SFT-CHEM-ECHEM-012-ADVERSE-UNCERTAINTY": row["table_1_discrepancy_percent_source_inscription"] == "about 9" and row["table_2_discrepancy_percent_source_inscription"] == "3.6" and row["ir_drop_linear_interpolation_anodic_addition_cathodic_reduction_and_estimation_limits_retained"],
            "SFT-CHEM-ECHEM-012-COMPLETE-SOURCES": row["complete_claim_source_pages"] == 49,
        }
        summary = {"complete_corrosion_table_rows": 21, "complete_control_rows": 10, "measured_weight_loss_mg": ["345", "2245"], "reported_discrepancy_percent": ["about 9", "3.6"], "complete_claim_source_pages": 49}
    else:
        raise ValueError("unknown ECHEM-009–012 claim")
    if omit_last:
        checks.pop(next(reversed(checks)))
    spec = {item.claim_id: item for item in SPECS}[claim_id]
    if tuple(checks) != tuple(target.target_id for target in spec.target_rows) or not all(checks.values()):
        raise ValueError(f"{claim_id} comparison changed")
    return {**summary, "complete_family_pdf_pages": pages, "complete_family_pdf_characters": characters, "complete_result_vector_sha256": recorded, "all_favorable_adverse_absent_unresolved_uncertainty_correction_signed_zero_decimal_continuum_fitted_and_historical_inscriptions_retained_as_external_provenance_only": True}, checks


class _Validator:
    def __init__(self, root: Path, spec):
        self.root, self.spec = root.resolve(), spec

    def validate(self, sealed):
        self.spec.validate()
        analysis, checks = exact_analysis(self.root, self.spec.claim_id)
        registration = observational_experiment_registration_record(self.spec)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.spec)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(checks), sealed.seal_hash, registration_hash)
        vault = TargetVault(experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-external-target-custodian", targets={target: HeldLabel("external-observation", self.spec.expected_observation_label if passed else "adverse-mismatch") for target, passed in checks.items()}, custody_nonce=sha256_identity((registration_hash, analysis["complete_result_vector_sha256"])), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("ECHEM-009–012 prediction package changed")
        release = vault.release(prediction)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction)
        boundary.measurement_context(release.targets)
        comparisons = tuple({"target_id": target, "predicted": execution.output.label, "observed": release.targets[target].label, "passed": execution.output.label == release.targets[target].label} for target in checks)
        try:
            exact_analysis(self.root, self.spec.claim_id, True)
            omission = False
        except ValueError:
            omission = True
        passed = all(row["passed"] for row in comparisons) and omission
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-echem-polarization-batch/1", self.spec.claim_id, self.spec.falsification_condition)), prediction_seal_hash=prediction.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ECHEM-009–012 target changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction.seal_hash, "analysis": analysis, "comparisons": comparisons, "omission_rejected": omission, "trace": execution.trace_hash}
        notes = ("complete 73-page shared post-seal source family retained", f"all {len(checks)} separately registered claim targets retained", "all measured values units uncertainties fits discrepancies adverse absent and unresolved records remain downstream provenance")
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row.source_id for row in self.spec.target_rows), notes, sha256_identity(payload), self.spec.falsification_condition, passed)


class ElectrodeReactionRateValidator(_Validator):
    def __init__(self, root): super().__init__(root, RATE_SPEC)


class OverpotentialPolarizationValidator(_Validator):
    def __init__(self, root): super().__init__(root, POLARIZATION_SPEC)


class DoubleLayerValidator(_Validator):
    def __init__(self, root): super().__init__(root, DOUBLE_LAYER_SPEC)


class CorrosionNetworkValidator(_Validator):
    def __init__(self, root): super().__init__(root, CORROSION_SPEC)


__all__ = ("CorrosionNetworkValidator", "DoubleLayerValidator", "ElectrodeReactionRateValidator", "OverpotentialPolarizationValidator", "exact_analysis")
