"""Capability-closed validation for separate NUCHEM-009–012 claims."""
import hashlib
import json
import platform
from functools import lru_cache
from pathlib import Path

from pypdf import PdfReader

from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.nuchem_terminal_batch_v1 import ANALYSIS_PATH, AUTHORITIES, FISSION_PRODUCT_SPEC, RADIOLYSIS_SPEC, RADIOTRACER_SPEC, SEPARATION_SPEC, SPECS
from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


def digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _clean(text: str) -> str:
    return "\n".join(line.strip() for line in text.replace("\u00ad", "").splitlines() if line.strip())


@lru_cache(maxsize=None)
def _surface(path: Path) -> tuple[dict, ...]:
    rows = []
    for number, page in enumerate(PdfReader(path).pages, start=1):
        text = _clean(page.extract_text() or "")
        rows.append({"page": number, "character_count": len(text), "text_sha256": digest(text.encode())})
    return tuple(rows)


def exact_analysis(root: Path, claim_id: str, omit_last: bool = False):
    for path, expected in AUTHORITIES:
        if hash_file(root / path) != expected: raise ValueError(f"NUCHEM-009–012 authority changed: {path}")
    analysis = json.loads((root / ANALYSIS_PATH).read_text()); vector = dict(analysis); recorded = vector.pop("complete_result_vector_sha256")
    if recorded != digest(json.dumps(vector, sort_keys=True, separators=(",", ":")).encode()): raise ValueError("NUCHEM-009–012 result vector changed")
    pages = characters = 0
    for source in analysis["complete_source_reconstruction"].values():
        reconstructed = _surface(root / source["snapshot_path"])
        if reconstructed != tuple(source["complete_surface_vector"]): raise ValueError("complete NUCHEM-009–012 source reconstruction changed")
        pages += len(reconstructed); characters += sum(row["character_count"] for row in reconstructed)
    if (pages, characters) != (370, 837013) or (pages, characters) != (analysis["complete_pdf_page_count"], analysis["complete_extracted_character_count"]): raise ValueError("complete NUCHEM-009–012 source surface changed")

    if claim_id == RADIOTRACER_SPEC.claim_id:
        row = analysis["nuchem_009"]
        checks = {
            "SFT-CHEM-NUCHEM-009-TRACER-CHEMISTRY": len(row["complete_tracer_chemical_vector"]) == 8 and "58CoO" in row["complete_tracer_chemical_vector"],
            "SFT-CHEM-NUCHEM-009-OBSERVATION-SUPPORT": row["detector_support"]["simple_experiment_detector_count"] == "2" and len(row["flotation_mean_residence_time_minutes"]) == 3,
            "SFT-CHEM-NUCHEM-009-COUNTS": row["gold_leach_vector"]["tank_1_injected_activity_mCi"] == "100" and row["gold_leach_vector"]["tank_7_injected_activity_mCi"] == "130",
            "SFT-CHEM-NUCHEM-009-RECOVERY": row["cobalt_recovery_vector"]["recovery_in_copper_matte_percent"] == "70-75",
            "SFT-CHEM-NUCHEM-009-LOCALIZATION": row["cobalt_recovery_vector"]["short_circuit_percent"] == "about 5" and row["cobalt_recovery_vector"]["blocked_settling_tank_volume_percent"] == "nearly 30",
            "SFT-CHEM-NUCHEM-009-INFERENCE-BOUNDARY": row["observation_model_boundary"].startswith("measured curves"),
            "SFT-CHEM-NUCHEM-009-ADVERSE-LIMITS": row["all_background_decay_correction_normalization_loss_fit_assumption_adverse_absent_unavailable_and_unresolved_rows_retained"],
            "SFT-CHEM-NUCHEM-009-COMPLETE-SOURCE": analysis["complete_source_count"] == 4,
        }
        summary = {"tracer_chemistry_rows": 8, "flotation_rows": 3, "cobalt_recovery_percent": "70-75", "short_circuit_percent": "about 5"}
    elif claim_id == SEPARATION_SPEC.claim_id:
        row = analysis["nuchem_010"]
        checks = {
            "SFT-CHEM-NUCHEM-010-SPECIES": len(row["complete_species_vector"]) == 14,
            "SFT-CHEM-NUCHEM-010-STREAMS": len(row["complete_process_vector"]) == 9,
            "SFT-CHEM-NUCHEM-010-BALANCE": row["resin_vector"]["pre_column_48V_uCi"] == "2562" and row["resin_vector"]["post_column_48V_uCi"] == "1626",
            "SFT-CHEM-NUCHEM-010-RECOVERY": row["resin_vector"]["48V_recovery_percent"] == "92" and row["post_titanium_removal_vector"]["extraction_percent"] == "71",
            "SFT-CHEM-NUCHEM-010-DECONTAMINATION": row["resin_vector"]["post_column_Sc"] == "not detectable" and row["competitive_species_vector"]["extraction_percent"] == "71",
            "SFT-CHEM-NUCHEM-010-STAGES": row["post_titanium_removal_vector"]["time_minutes"] == "180" and row["competitive_species_vector"]["time_minutes"] == "60",
            "SFT-CHEM-NUCHEM-010-ADVERSE-UNCERTAINTY": row["adverse_initial_radiotracer_vector"]["extraction_percent"] == "1" and row["all_detection_limits_uncertainties_single_replicates_losses_interference_unexpected_adverse_estimates_and_future_work_retained"],
            "SFT-CHEM-NUCHEM-010-COMPLETE-SOURCE": analysis["complete_source_count"] == 4,
        }
        summary = {"species_rows": 14, "post_column_recovery_percent": "92", "post_titanium_extraction_percent": "71", "competitive_extraction_percent": "71", "adverse_initial_extraction_percent": "1"}
    elif claim_id == FISSION_PRODUCT_SPEC.claim_id:
        row = analysis["nuchem_011"]
        checks = {
            "SFT-CHEM-NUCHEM-011-PHYSICS-HANDOFF": len(row["complete_chemical_groups"]["noble_gases"]) == 2,
            "SFT-CHEM-NUCHEM-011-CHEMICAL-IDENTITY": len(row["complete_chemical_groups"]["stable_salt_soluble_fluorides"]) == 7 and len(row["complete_chemical_groups"]["noble_metals_or_nonstable_fluorides"]) == 7,
            "SFT-CHEM-NUCHEM-011-PHASE-LOCATION": len(row["phase_location_behavior"]) == 5 and len(row["sample_support"]) == 5,
            "SFT-CHEM-NUCHEM-011-DISTRIBUTION": row["iodine_balance_vector"]["salt_inventory_range_percent"] == "45-71" and row["surface_vector"]["metal_area_percent"] == "26",
            "SFT-CHEM-NUCHEM-011-REDISTRIBUTION": row["surface_vector"]["graphite_area_percent"] == "74" and "deposit" in row["phase_location_behavior"][4],
            "SFT-CHEM-NUCHEM-011-TIME-SAMPLE": row["operating_support"]["235U_effective_full_power_hours"] == ">9000" and row["operating_support"]["233U_effective_full_power_hours"] == ">5100",
            "SFT-CHEM-NUCHEM-011-ADVERSE-DISCREPANCY": len(row["adverse_and_unresolved_vector"]) == 6 and row["all_inventory_bases_samples_conditions_variances_losses_conjectures_adverse_absent_unavailable_and_unresolved_rows_retained"],
            "SFT-CHEM-NUCHEM-011-COMPLETE-SOURCE": analysis["complete_source_count"] == 4,
        }
        summary = {"chemical_groups": 4, "salt_fluoride_rows": 7, "noble_metal_rows": 7, "iodine_salt_inventory_percent": "45-71 (median 62)", "unaccounted_iodine": "about one-quarter to one-third"}
    elif claim_id == RADIOLYSIS_SPEC.claim_id:
        row = analysis["nuchem_012"]
        checks = {
            "SFT-CHEM-NUCHEM-012-RESOURCE-HANDOFF": "absorbed-energy resource" in row["yield_definition"],
            "SFT-CHEM-NUCHEM-012-SPECIES": len(row["complete_product_vector"]) == 6,
            "SFT-CHEM-NUCHEM-012-NETWORK": len(row["reaction_vector"]) == 4,
            "SFT-CHEM-NUCHEM-012-YIELDS": [(x["G"], x["uncertainty"]) for x in row["preferred_yield_vector"]] == [("10.0", "0.2"), ("2.0", "0.2"), ("4.0", "0.4"), ("4.0", "0.4")],
            "SFT-CHEM-NUCHEM-012-CONDITIONS": len(row["very_high_dose_vector"]) == 2 and row["very_high_dose_vector"][0]["G_N2"] == "12.4 ± 0.4",
            "SFT-CHEM-NUCHEM-012-PARTITION-CLOSURE": len(row["complete_rare_gas_sensitized_table"]) == 5 and row["complete_rare_gas_sensitized_table"][-1]["G_minus_N2O"] == "4.1",
            "SFT-CHEM-NUCHEM-012-ADVERSE-UNCERTAINTY": len(row["adverse_and_limit_vector"]) == 12 and row["all_methods_conditions_dosimetry_corrections_tentative_unreliable_questionable_nonlinear_adverse_absent_unavailable_and_unresolved_rows_retained"],
            "SFT-CHEM-NUCHEM-012-COMPLETE-SOURCE": analysis["complete_source_count"] == 4,
        }
        summary = {"preferred_yield_rows": 4, "preferred_G_vector": ["N2 10.0 ± 0.2", "O2 measured 2.0 ± 0.2", "O2 calculated 4.0 ± 0.4", "NO 4.0 ± 0.4"], "rare_gas_rows": 5, "very_high_dose_rows": 2}
    else: raise ValueError("unknown NUCHEM-009–012 claim")
    if omit_last: checks.pop(next(reversed(checks)))
    spec = {item.claim_id: item for item in SPECS}[claim_id]
    if tuple(checks) != tuple(target.target_id for target in spec.target_rows) or not all(checks.values()): raise ValueError(f"{claim_id} comparison changed")
    return {**summary, "complete_family_pdf_pages": pages, "complete_family_characters": characters, "complete_result_vector_sha256": recorded, "all_favorable_adverse_absent_unavailable_unresolved_uncertainty_assumption_correction_fit_estimate_loss_signed_zero_decimal_continuum_and_historical_inscriptions_retained_as_external_provenance_only": True}, checks


class _Validator:
    def __init__(self, root: Path, spec): self.root, self.spec = root.resolve(), spec
    def validate(self, sealed):
        self.spec.validate(); analysis, checks = exact_analysis(self.root, self.spec.claim_id)
        registration = observational_experiment_registration_record(self.spec); registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.spec); program = fold_program_from_mapping(document); inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(checks), sealed.seal_hash, registration_hash)
        vault = TargetVault(experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-external-target-custodian", targets={target: HeldLabel("external-observation", self.spec.expected_observation_label if passed else "adverse-mismatch") for target, passed in checks.items()}, custody_nonce=sha256_identity((registration_hash, analysis["complete_result_vector_sha256"])), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs); boundary = BlindExperimentBoundary(envelope); prediction = boundary.seal_prediction(execution.output, execution.trace); after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError("NUCHEM-009–012 prediction package changed")
        release = vault.release(prediction); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction); boundary.measurement_context(release.targets)
        comparisons = tuple({"target_id": target, "predicted": execution.output.label, "observed": release.targets[target].label, "passed": execution.output.label == release.targets[target].label} for target in checks)
        try: exact_analysis(self.root, self.spec.claim_id, True); omission = False
        except ValueError: omission = True
        passed = all(row["passed"] for row in comparisons) and omission
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-nuchem-terminal-batch/1", self.spec.claim_id, self.spec.falsification_condition)), prediction_seal_hash=prediction.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash: raise ValueError("NUCHEM-009–012 target changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction.seal_hash, "analysis": analysis, "comparisons": comparisons, "omission_rejected": omission, "trace": execution.trace_hash}
        notes = ("complete four-source post-seal family retained as 370 PDF pages and 837,013 extracted characters", f"all {len(checks)} separately registered claim targets retained", "all measured values units uncertainties assumptions corrections fits estimates losses adverse absent unavailable and unresolved records remain downstream provenance; disclosed pre-seal snippets are never relabelled blind")
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row.source_id for row in self.spec.target_rows), notes, sha256_identity(payload), self.spec.falsification_condition, passed)


class RadiotracerValidator(_Validator):
    def __init__(self, root): super().__init__(root, RADIOTRACER_SPEC)
class SeparationValidator(_Validator):
    def __init__(self, root): super().__init__(root, SEPARATION_SPEC)
class FissionProductValidator(_Validator):
    def __init__(self, root): super().__init__(root, FISSION_PRODUCT_SPEC)
class RadiolysisValidator(_Validator):
    def __init__(self, root): super().__init__(root, RADIOLYSIS_SPEC)


__all__ = ("FissionProductValidator", "RadiolysisValidator", "RadiotracerValidator", "SeparationValidator", "exact_analysis")
