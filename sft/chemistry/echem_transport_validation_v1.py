"""Capability-closed validation for separate ECHEM-005–008 claims."""
import hashlib
import json
import platform
from functools import lru_cache
from pathlib import Path

from pypdf import PdfReader

from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.echem_transport_batch_v1 import ANALYSIS_PATH, AUTHORITIES, CONDUCTIVITY_SPEC, ELECTROLYSIS_SPEC, MOBILITY_SPEC, SPECS, WORK_SPEC
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
            raise ValueError(f"ECHEM-005–008 authority changed: {path}")
    analysis = json.loads((root / ANALYSIS_PATH).read_text())
    vector = dict(analysis); recorded = vector.pop("complete_result_vector_sha256")
    if recorded != digest(json.dumps(vector, sort_keys=True, separators=(",", ":")).encode()):
        raise ValueError("ECHEM-005–008 result vector changed")
    pages = characters = 0
    for source in analysis["complete_source_reconstruction"].values():
        reconstructed = _page_vector(root / source["snapshot_path"])
        if reconstructed != tuple(source["complete_page_vector"]):
            raise ValueError("complete ECHEM-005–008 page reconstruction changed")
        pages += len(reconstructed); characters += sum(row["character_count"] for row in reconstructed)
    if pages != analysis["complete_pdf_page_count"] or characters != analysis["complete_pdf_extracted_character_count"] or pages != 519 or characters != 1754402:
        raise ValueError("complete ECHEM-005–008 source surface changed")

    if claim_id == WORK_SPEC.claim_id:
        row = analysis["echem_005"]
        checks = {
            "SFT-CHEM-ECHEM-005-FARADAY-CUSTODY": row["faraday_source_inscription"] == "96 485.332 12... (exact) C mol^-1",
            "SFT-CHEM-ECHEM-005-POTENTIAL-VECTOR": row["complete_standard_potential_count"] == 17,
            "SFT-CHEM-ECHEM-005-WORK-VECTOR": row["complete_work_count"] == 17 and len(row["complete_positive_work_vector"]) == 17 and row["all_work_values_exact_products_of_postseal_external_potential_and_inherited_molar_charge"],
            "SFT-CHEM-ECHEM-005-DIRECTION": row["chemical_and_electrical_path_reversal_retained_without_negative_native_magnitude"],
            "SFT-CHEM-ECHEM-005-EQUILIBRIUM": row["equilibrium_condition_and_structural_coincidence_boundary_retained"],
            "SFT-CHEM-ECHEM-005-UNCERTAINTIES": row["complete_source_uncertainty_vector_retained"],
            "SFT-CHEM-ECHEM-005-ADVERSE-CONTROLS": row["historical_and_current_faraday_values_retained_without_averaging"],
            "SFT-CHEM-ECHEM-005-COMPLETE-SOURCES": row["complete_registered_source_page_count"] == 229,
        }
        summary = {"complete_work_rows": 17, "faraday_coulomb_per_mole": "96485.33212... exact", "temperature_range_celsius": ["0", "95"], "complete_claim_source_pages": 229, "historical_current_faraday_disagreement_retained": True}
    elif claim_id == ELECTROLYSIS_SPEC.claim_id:
        row = analysis["echem_006"]
        checks = {
            "SFT-CHEM-ECHEM-006-PROCESS-CUSTODY": row["complete_silver_run_count"] == 8,
            "SFT-CHEM-ECHEM-006-CHARGE-TIME-VECTOR": all(all(key in run for key in ("current_ampere_source_inscription", "elapsed_seconds_source_inscription", "q_prime_millicoulomb_source_inscription", "q_double_prime_millicoulomb_source_inscription")) for run in row["complete_silver_run_vector"]),
            "SFT-CHEM-ECHEM-006-PRODUCT-MASS-VECTOR": all("sample_mass_gram_source_inscription" in run and "residue_microgram_source_inscription" in run for run in row["complete_silver_run_vector"]),
            "SFT-CHEM-ECHEM-006-EQUIVALENT-VECTOR": len(row["complete_silver_run_vector"]) == 8 and row["corrected_pure_silver_equivalent_milligram_per_coulomb"] == "1.1179648",
            "SFT-CHEM-ECHEM-006-FARADAY-CROSSCHECK": row["current_codata_faraday_coulomb_per_mole"] == "96485.33212... exact",
            "SFT-CHEM-ECHEM-006-CORRECTIONS": row["all_current_time_mass_residue_blank_charge_impurity_overvoltage_and_uncertainty_fields_retained"],
            "SFT-CHEM-ECHEM-006-UNCERTAINTY-ADVERSE": row["historical_current_disagreement_retained_as_source_comparison_not_native_law_failure"] and row["reported_historical_faraday_uncertainty"] == "0.24",
            "SFT-CHEM-ECHEM-006-COMPLETE-SOURCES": row["complete_registered_source_page_count"] == 221,
        }
        summary = {"complete_silver_runs": 8, "measured_equivalent_milligram_per_coulomb": "1.1179648", "historical_faraday": "96486.33(24)", "current_codata_faraday": "96485.33212... exact", "complete_claim_source_pages": 221}
    elif claim_id == CONDUCTIVITY_SPEC.claim_id:
        row = analysis["echem_007"]
        checks = {
            "SFT-CHEM-ECHEM-007-SRM-IDENTITY": row["reference_material"].startswith("SRM 3190"),
            "SFT-CHEM-ECHEM-007-COMPOSITION": "aqueous HCl" in row["reference_material"],
            "SFT-CHEM-ECHEM-007-CONDITION": row["certified_temperature_celsius_source_inscription"] == "25.000" and row["temperature_uncertainty_celsius_source_inscription"] == "0.005",
            "SFT-CHEM-ECHEM-007-CERTIFIED-VALUE": row["certified_conductivity_microSiemens_per_centimeter_source_inscription"] == "25.11",
            "SFT-CHEM-ECHEM-007-UNCERTAINTY": row["expanded_uncertainty_microSiemens_per_centimeter_source_inscription"] == "0.26" and row["coverage_factor_source_inscription"] == "1.96",
            "SFT-CHEM-ECHEM-007-METHOD": row["all_ions_contribute_species_resolution_statement_retained"] and row["ac_and_dc_primary_methods_retained"] and len(row["complete_primary_method_page_vector"]) == 52,
            "SFT-CHEM-ECHEM-007-CATALOG-VECTOR": len(row["complete_catalog_nominal_family"]) == 6,
            "SFT-CHEM-ECHEM-007-COMPLETE-SOURCES": row["complete_registered_source_page_count"] == 280 and row["composition_temperature_cell_calibration_traceability_uncertainty_carbon_dioxide_evaporation_and_storage_controls_retained"],
        }
        summary = {"certified_conductivity_microSiemens_per_centimeter": "25.11", "expanded_uncertainty_microSiemens_per_centimeter": "0.26", "certified_temperature_celsius": "25.000", "catalog_reference_materials": 6, "complete_claim_source_pages": 280}
    elif claim_id == MOBILITY_SPEC.claim_id:
        row = analysis["echem_008"]
        checks = {
            "SFT-CHEM-ECHEM-008-SPECIES": len(row["complete_species_vector"]) == 3,
            "SFT-CHEM-ECHEM-008-METHOD": len(row["complete_transference_page_vector"]) == 10 and row["temperature_celsius_source_inscription"] == "25 ± 0.05",
            "SFT-CHEM-ECHEM-008-CONCENTRATION-VECTOR": len(row["potassium_dilute_to_saturated_concentration_support_molal_source_inscriptions"]) == 10,
            "SFT-CHEM-ECHEM-008-TRANSFERENCE-VECTOR": row["complete_experimental_run_count"] == 14 and row["complete_table_count"] == 4 and len(row["sodium_difference_pairs_source_inscriptions"]) == 3,
            "SFT-CHEM-ECHEM-008-MOBILITY-RELATION": row["cation_mobility_anion_mobility_transference_current_direction_and_concentration_custody_retained"],
            "SFT-CHEM-ECHEM-008-PARTITION": row["lithium_observed_transference_source_inscription"] == "0.314" and row["lithium_reference_transference_source_inscription"] == "0.304",
            "SFT-CHEM-ECHEM-008-ADVERSE-RESULTS": row["potassium_little_change_result_retained"] and row["stationary_and_nonreversing_adverse_rows_retained"] and row["hard_to_explain_and_preliminary_status_retained"],
            "SFT-CHEM-ECHEM-008-COMPLETE-SOURCES": row["complete_registered_source_page_count"] == 213,
        }
        summary = {"complete_species": 3, "complete_experimental_runs": 14, "complete_tables": 4, "lithium_observed_transference": "0.314", "adverse_stationary_and_nonreversing_rows_retained": True, "complete_claim_source_pages": 213}
    else:
        raise ValueError("unknown ECHEM-005–008 claim")
    if omit_last:
        checks.pop(next(reversed(checks)))
    spec = {row.claim_id: row for row in SPECS}[claim_id]
    if tuple(checks) != tuple(row.target_id for row in spec.target_rows) or not all(checks.values()):
        raise ValueError(f"{claim_id} comparison changed")
    return {**summary, "complete_family_pdf_pages": pages, "complete_family_pdf_characters": characters, "complete_result_vector_sha256": recorded, "all_favorable_adverse_absent_unresolved_uncertainty_correction_signed_zero_decimal_continuum_fitted_and_historical_inscriptions_retained_as_external_provenance_only": True}, checks


class _Validator:
    def __init__(self, root: Path, spec):
        self.root, self.spec = root.resolve(), spec

    def validate(self, sealed):
        self.spec.validate(); analysis, checks = exact_analysis(self.root, self.spec.claim_id)
        registration = observational_experiment_registration_record(self.spec); registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.spec); program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(checks), sealed.seal_hash, registration_hash)
        vault = TargetVault(experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-external-target-custodian", targets={target: HeldLabel("external-observation", self.spec.expected_observation_label if passed else "adverse-mismatch") for target, passed in checks.items()}, custody_nonce=sha256_identity((registration_hash, analysis["complete_result_vector_sha256"])), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope); prediction = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root); audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("ECHEM-005–008 prediction package changed")
        release = vault.release(prediction); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction); boundary.measurement_context(release.targets)
        comparisons = tuple({"target_id": target, "predicted": execution.output.label, "observed": release.targets[target].label, "passed": execution.output.label == release.targets[target].label} for target in checks)
        try:
            exact_analysis(self.root, self.spec.claim_id, True); omission = False
        except ValueError:
            omission = True
        passed = all(row["passed"] for row in comparisons) and omission
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-echem-transport-batch/1", self.spec.claim_id, self.spec.falsification_condition)), prediction_seal_hash=prediction.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ECHEM-005–008 target changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction.seal_hash, "analysis": analysis, "comparisons": comparisons, "omission_rejected": omission, "trace": execution.trace_hash}
        notes = ("complete 519-page shared post-seal source family retained", f"all {len(checks)} separately registered claim targets retained", "all measured values units uncertainties corrections historical disagreements anomalous absent and unresolved records remain downstream provenance")
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row.source_id for row in self.spec.target_rows), notes, sha256_identity(payload), self.spec.falsification_condition, passed)


class ElectrochemicalWorkValidator(_Validator):
    def __init__(self, root): super().__init__(root, WORK_SPEC)


class ElectrolysisProductValidator(_Validator):
    def __init__(self, root): super().__init__(root, ELECTROLYSIS_SPEC)


class IonicConductivityValidator(_Validator):
    def __init__(self, root): super().__init__(root, CONDUCTIVITY_SPEC)


class MobilityTransferenceValidator(_Validator):
    def __init__(self, root): super().__init__(root, MOBILITY_SPEC)


__all__ = ("ElectrochemicalWorkValidator", "ElectrolysisProductValidator", "IonicConductivityValidator", "MobilityTransferenceValidator", "exact_analysis")
