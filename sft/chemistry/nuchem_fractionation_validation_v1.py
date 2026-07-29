"""Capability-closed validation for separate NUCHEM-005–008 claims."""
import hashlib
from html.parser import HTMLParser
import json
import platform
from functools import lru_cache
from pathlib import Path

from pypdf import PdfReader

from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.nuchem_fractionation_batch_v1 import ANALYSIS_PATH, AUTHORITIES, EQUILIBRIUM_FRACTIONATION_SPEC, ISOTOPE_EXCHANGE_SPEC, KINETIC_FRACTIONATION_SPEC, RADIOCHEMICAL_EQUILIBRIUM_SPEC, SPECS
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


class _VisibleText(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.hidden = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}: self.hidden += 1
    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self.hidden: self.hidden -= 1
    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)


@lru_cache(maxsize=None)
def _surface(path: Path, kind: str) -> tuple[dict, ...]:
    if kind == "pdf":
        rows = []
        for number, page in enumerate(PdfReader(path).pages, start=1):
            text = _clean(page.extract_text() or "")
            rows.append({"page": number, "character_count": len(text), "text_sha256": digest(text.encode())})
        return tuple(rows)
    parser = _VisibleText(); parser.feed(path.read_text(errors="strict")); text = _clean("\n".join(parser.parts))
    return ({"document": 1, "character_count": len(text), "text_sha256": digest(text.encode())},)


def exact_analysis(root: Path, claim_id: str, omit_last: bool = False):
    for path, expected in AUTHORITIES:
        if hash_file(root / path) != expected: raise ValueError(f"NUCHEM-005–008 authority changed: {path}")
    analysis = json.loads((root / ANALYSIS_PATH).read_text())
    vector = dict(analysis); recorded = vector.pop("complete_result_vector_sha256")
    if recorded != digest(json.dumps(vector, sort_keys=True, separators=(",", ":")).encode()): raise ValueError("NUCHEM-005–008 result vector changed")
    pages = documents = characters = 0
    for source in analysis["complete_source_reconstruction"].values():
        reconstructed = _surface(root / source["snapshot_path"], source["surface_kind"])
        if reconstructed != tuple(source["complete_surface_vector"]): raise ValueError("complete NUCHEM-005–008 source reconstruction changed")
        characters += sum(row["character_count"] for row in reconstructed)
        if source["surface_kind"] == "pdf": pages += len(reconstructed)
        else: documents += len(reconstructed)
    if (pages, documents, characters) != (266, 1, 410095) or (pages, documents, characters) != (analysis["complete_pdf_page_count"], analysis["complete_html_document_count"], analysis["complete_extracted_character_count"]):
        raise ValueError("complete NUCHEM-005–008 source surface changed")

    if claim_id == RADIOCHEMICAL_EQUILIBRIUM_SPEC.claim_id:
        row = analysis["nuchem_005"]
        checks = {
            "SFT-CHEM-NUCHEM-005-PARENT-DAUGHTER": len(row["complete_parent_daughter_vectors"]) == 2,
            "SFT-CHEM-NUCHEM-005-TIME-SUPPORT": len(row["complete_reference_time_vector"]) == 2,
            "SFT-CHEM-NUCHEM-005-ACTIVITY": row["certified_activity_vector"][0]["value"] == "29.492" and row["certified_activity_vector"][1]["value"] == "26.30",
            "SFT-CHEM-NUCHEM-005-RATIO-REGIME": len(row["equilibrium_records"]) == 2,
            "SFT-CHEM-NUCHEM-005-TRANSIENT": "complete retained progeny" in row["complete_parent_daughter_vectors"][1][1],
            "SFT-CHEM-NUCHEM-005-SECULAR": "radioactive equilibrium" in row["equilibrium_records"][0],
            "SFT-CHEM-NUCHEM-005-ADVERSE-METHODS": row["all_assumptions_uncertainties_corrections_confirmations_and_unavailable_rows_retained"] and row["transient_or_secular_numeric_time_series_in_registered_sources"].startswith("unavailable"),
            "SFT-CHEM-NUCHEM-005-COMPLETE-SOURCES": analysis["complete_source_count"] == 5,
        }
        summary = {"equilibrium_records": 2, "certified_activity_rows": 2, "numeric_regime_time_series": "unavailable__preserved_not_fabricated"}
    elif claim_id == ISOTOPE_EXCHANGE_SPEC.claim_id:
        row = analysis["nuchem_006"]
        checks = {
            "SFT-CHEM-NUCHEM-006-ISOTOPES": len(row["complete_example_isotope_ratio_vector"]) == 4,
            "SFT-CHEM-NUCHEM-006-CARRIERS": "two retained carriers" in row["exchange_relation"],
            "SFT-CHEM-NUCHEM-006-CONSERVATION": "balance" in row["balance_and_nonideality_custody"],
            "SFT-CHEM-NUCHEM-006-EXCHANGE-QUOTIENT": row["complete_exchange_alpha_vector"][0]["alpha"] == "0.99893",
            "SFT-CHEM-NUCHEM-006-EQUILIBRIUM": "equilibrium constant" in row["exchange_relation"],
            "SFT-CHEM-NUCHEM-006-MULTISPECIES": len(row["complete_example_conditions"]) == 5 and row["complete_example_isotope_ratio_vector"][3]["standard_units_permil"] == "42.08",
            "SFT-CHEM-NUCHEM-006-ADVERSE-ASSUMPTIONS": row["all_assumptions_comparisons_nonideality_absent_unavailable_and_adverse_rows_retained"],
            "SFT-CHEM-NUCHEM-006-COMPLETE-SOURCES": analysis["complete_source_count"] == 5,
        }
        summary = {"exchange_alpha_rows": 4, "isotope_ratio_rows": 4, "example_conditions": 5}
    elif claim_id == EQUILIBRIUM_FRACTIONATION_SPEC.claim_id:
        row = analysis["nuchem_007"]
        checks = {
            "SFT-CHEM-NUCHEM-007-ISOTOPE-RATIOS": row["factor_definition"].startswith("alpha_A-B"),
            "SFT-CHEM-NUCHEM-007-PHASES": "R_A/R_B" in row["factor_definition"],
            "SFT-CHEM-NUCHEM-007-FACTORS": len(row["complete_table_1_vector"]) == 12 and row["complete_table_1_vector"][-1]["alpha"] == "1.01980",
            "SFT-CHEM-NUCHEM-007-ORIENTATION": row["complete_table_1_vector"][0]["alpha"] == "1.00000",
            "SFT-CHEM-NUCHEM-007-TEMPERATURE": len(row["temperature_support"]) == 2 and "figures 1 through 49" in row["temperature_support"][1],
            "SFT-CHEM-NUCHEM-007-EQUILIBRIUM": row["one_atom_exchange_correspondence"] == "for a one-atom exchange reaction K equals alpha" and len(row["complete_exchange_alpha_vector"]) == 4,
            "SFT-CHEM-NUCHEM-007-ADVERSE-UNAVAILABLE": row["all_fits_assumptions_estimated_curves_adverse_absent_unavailable_and_unresolved_rows_retained"] and "uncritically compiled" in row["adverse_record"],
            "SFT-CHEM-NUCHEM-007-COMPLETE-SOURCES": analysis["complete_source_count"] == 5,
        }
        summary = {"comparison_table_rows": 12, "exchange_alpha_rows": 4, "registered_curve_figures": 49}
    elif claim_id == KINETIC_FRACTIONATION_SPEC.claim_id:
        row = analysis["nuchem_008"]
        checks = {
            "SFT-CHEM-NUCHEM-008-REACTION-PATH": row["reaction_path"].startswith("electrolysis"),
            "SFT-CHEM-NUCHEM-008-TIME-RESOURCE": len(row["complete_table_1_vector"]) == 10 and row["complete_table_1_vector"][-1]["litres_collected"] == "150",
            "SFT-CHEM-NUCHEM-008-PRODUCTS": row["complete_table_1_vector"][-1]["residual_H2_in_cell_ppm"] == "+57.8",
            "SFT-CHEM-NUCHEM-008-RATES": row["kinetic_response_vector"]["initial_recombined_gas_density_change_ppm"] == "-20.5",
            "SFT-CHEM-NUCHEM-008-FACTOR": row["kinetic_response_vector"]["fractionation_factor"] == "2.4",
            "SFT-CHEM-NUCHEM-008-STEADY-STATE": row["steady_state_record"].startswith("at 150 litres"),
            "SFT-CHEM-NUCHEM-008-ADVERSE-CORRECTIONS": row["all_corrections_uncertainties_replicate_discrepancies_flow_reversals_estimates_losses_and_limits_retained"] and len(row["correction_vector"]["measurement_rows_ppm"]) == 3 and len(row["adverse_and_limit_vector"]) == 6,
            "SFT-CHEM-NUCHEM-008-COMPLETE-SOURCES": analysis["complete_source_count"] == 5,
        }
        summary = {"kinetic_series_rows": 10, "fractionation_factor": "2.4", "correction_ppm": "2.2 ± 0.5", "replicate_rows": 3}
    else: raise ValueError("unknown NUCHEM-005–008 claim")
    if omit_last: checks.pop(next(reversed(checks)))
    spec = {item.claim_id: item for item in SPECS}[claim_id]
    if tuple(checks) != tuple(target.target_id for target in spec.target_rows) or not all(checks.values()): raise ValueError(f"{claim_id} comparison changed")
    return {**summary, "complete_family_pdf_pages": pages, "complete_family_html_documents": documents, "complete_family_characters": characters, "complete_result_vector_sha256": recorded, "all_favorable_adverse_absent_unavailable_unresolved_uncertainty_assumption_correction_estimate_loss_signed_zero_decimal_continuum_and_historical_inscriptions_retained_as_external_provenance_only": True}, checks


class _Validator:
    def __init__(self, root: Path, spec): self.root, self.spec = root.resolve(), spec
    def validate(self, sealed):
        self.spec.validate(); analysis, checks = exact_analysis(self.root, self.spec.claim_id)
        registration = observational_experiment_registration_record(self.spec); registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.spec); program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(checks), sealed.seal_hash, registration_hash)
        vault = TargetVault(experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-external-target-custodian", targets={target: HeldLabel("external-observation", self.spec.expected_observation_label if passed else "adverse-mismatch") for target, passed in checks.items()}, custody_nonce=sha256_identity((registration_hash, analysis["complete_result_vector_sha256"])), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope); prediction = boundary.seal_prediction(execution.output, execution.trace); after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError("NUCHEM-005–008 prediction package changed")
        release = vault.release(prediction); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction); boundary.measurement_context(release.targets)
        comparisons = tuple({"target_id": target, "predicted": execution.output.label, "observed": release.targets[target].label, "passed": execution.output.label == release.targets[target].label} for target in checks)
        try: exact_analysis(self.root, self.spec.claim_id, True); omission = False
        except ValueError: omission = True
        passed = all(row["passed"] for row in comparisons) and omission
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-nuchem-fractionation-batch/1", self.spec.claim_id, self.spec.falsification_condition)), prediction_seal_hash=prediction.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash: raise ValueError("NUCHEM-005–008 target changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction.seal_hash, "analysis": analysis, "comparisons": comparisons, "omission_rejected": omission, "trace": execution.trace_hash}
        notes = ("complete five-source post-seal family retained as 266 PDF pages, 1 HTML document and 410,095 extracted characters", f"all {len(checks)} separately registered claim targets retained", "all measured values units uncertainties assumptions corrections estimates discrepancies losses adverse absent unavailable and unresolved records remain downstream provenance")
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row.source_id for row in self.spec.target_rows), notes, sha256_identity(payload), self.spec.falsification_condition, passed)


class RadiochemicalEquilibriumValidator(_Validator):
    def __init__(self, root): super().__init__(root, RADIOCHEMICAL_EQUILIBRIUM_SPEC)
class IsotopeExchangeValidator(_Validator):
    def __init__(self, root): super().__init__(root, ISOTOPE_EXCHANGE_SPEC)
class EquilibriumIsotopeFractionationValidator(_Validator):
    def __init__(self, root): super().__init__(root, EQUILIBRIUM_FRACTIONATION_SPEC)
class KineticIsotopeFractionationValidator(_Validator):
    def __init__(self, root): super().__init__(root, KINETIC_FRACTIONATION_SPEC)


__all__ = ("EquilibriumIsotopeFractionationValidator", "IsotopeExchangeValidator", "KineticIsotopeFractionationValidator", "RadiochemicalEquilibriumValidator", "exact_analysis")
