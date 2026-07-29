"""Capability-closed validation for separate NUCHEM-001–004 claims."""
import hashlib
from html.parser import HTMLParser
import json
import platform
from functools import lru_cache
from pathlib import Path

from pypdf import PdfReader

from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.nuchem_initial_batch_v1 import ACTIVITY_SPEC, ANALYSIS_PATH, AUTHORITIES, BRANCHING_SPEC, CARRIER_SPEC, SPECS, TRANSFORMATION_SPEC
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
    def __init__(self):
        super().__init__(convert_charrefs=True); self.hidden = 0; self.parts = []
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
        if hash_file(root / path) != expected:
            raise ValueError(f"NUCHEM-001–004 authority changed: {path}")
    analysis = json.loads((root / ANALYSIS_PATH).read_text())
    vector = dict(analysis); recorded = vector.pop("complete_result_vector_sha256")
    if recorded != digest(json.dumps(vector, sort_keys=True, separators=(",", ":")).encode()):
        raise ValueError("NUCHEM-001–004 result vector changed")
    pages = documents = characters = 0
    for source in analysis["complete_source_reconstruction"].values():
        reconstructed = _surface(root / source["snapshot_path"], source["surface_kind"])
        if reconstructed != tuple(source["complete_surface_vector"]):
            raise ValueError("complete NUCHEM-001–004 source reconstruction changed")
        characters += sum(row["character_count"] for row in reconstructed)
        if source["surface_kind"] == "pdf": pages += len(reconstructed)
        else: documents += len(reconstructed)
    if (pages, documents, characters) != (8, 2, 34442) or (pages, documents, characters) != (analysis["complete_pdf_page_count"], analysis["complete_html_document_count"], analysis["complete_extracted_character_count"]):
        raise ValueError("complete NUCHEM-001–004 source surface changed")

    if claim_id == CARRIER_SPEC.claim_id:
        row = analysis["nuchem_001"]
        checks = {
            "SFT-CHEM-NUCHEM-001-ELEMENT": "elements 1 through 112" in row["element_identity_surface"],
            "SFT-CHEM-NUCHEM-001-NUCLIDE": "90Sr" in row["complete_nuclide_identity_vector"] and "90Y" in row["complete_nuclide_identity_vector"],
            "SFT-CHEM-NUCHEM-001-STATE": row["nuclear_state_custody"].endswith("state inferred"),
            "SFT-CHEM-NUCHEM-001-SPECIES": "standardized 90Sr solution" in row["chemical_carrier"],
            "SFT-CHEM-NUCHEM-001-PHASE": len(row["complete_phase_matrix_vector"]) == 4,
            "SFT-CHEM-NUCHEM-001-AMOUNT": len(row["amount_forms"]) == 4,
            "SFT-CHEM-NUCHEM-001-UNCERTAINTY": row["certified_massic_activity"]["value"] == "29.492" and len(row["complete_uncertainty_vector"]) == 12,
            "SFT-CHEM-NUCHEM-001-COMPLETE-SOURCES": row["complete_registered_source_surface_retained"],
        }
        summary = {"complete_nuclide_rows": len(row["complete_nuclide_identity_vector"]), "sr90_massic_activity_kBq_per_g": "29.492 ± 0.088", "uncertainty_rows": 12}
    elif claim_id == TRANSFORMATION_SPEC.claim_id:
        row = analysis["nuchem_002"]
        checks = {
            "SFT-CHEM-NUCHEM-002-PARENT": row["parent_daughter_vector"][0]["parent"] == "90Sr",
            "SFT-CHEM-NUCHEM-002-DAUGHTER": row["parent_daughter_vector"][0]["daughter"] == "90Y",
            "SFT-CHEM-NUCHEM-002-CHEMICAL-STATES": len(row["parent_daughter_chemical_states"]) == 3,
            "SFT-CHEM-NUCHEM-002-CHANNELS": len(row["channel_identity_vector"]) == 5,
            "SFT-CHEM-NUCHEM-002-NETWORK": row["complete_directed_network_retained"] and len(row["parent_daughter_vector"]) == 4,
            "SFT-CHEM-NUCHEM-002-EQUILIBRIUM": len(row["equilibrium_records"]) == 2,
            "SFT-CHEM-NUCHEM-002-ADVERSE-METHODS": len(row["method_assumption_vector"]) == 3 and len(row["complete_confirmatory_comparison_vector"]) == 3,
            "SFT-CHEM-NUCHEM-002-COMPLETE-SOURCES": row["complete_registered_source_surface_retained"],
        }
        summary = {"directed_network_rows": 4, "channel_rows": 5, "equilibrium_records": 2, "confirmatory_rows": 3}
    elif claim_id == ACTIVITY_SPEC.claim_id:
        row = analysis["nuchem_003"]
        checks = {
            "SFT-CHEM-NUCHEM-003-IDENTITY": row["identity_and_chemical_form_retained"],
            "SFT-CHEM-NUCHEM-003-AMOUNT-FORMS": len(row["amount_forms"]) == 5,
            "SFT-CHEM-NUCHEM-003-ACTIVITY-UNIT": row["becquerel_definition"] == "one nuclear transformation per second",
            "SFT-CHEM-NUCHEM-003-REFERENCE-TIME": len(row["reference_time_vector"]) == 2,
            "SFT-CHEM-NUCHEM-003-MASSIC-ACTIVITY": row["complete_massic_activity_vector"] == [{"coverage_factor": "2", "expanded_uncertainty": "0.088", "nuclide": "90Sr", "unit": "kBq·g-1", "value": "29.492"}, {"coverage_factor": "2", "expanded_uncertainty": "0.23", "nuclide": "232U", "unit": "Bq·g-1", "value": "26.30"}],
            "SFT-CHEM-NUCHEM-003-UNCERTAINTY": len(row["complete_uncertainty_vector"]) == 12,
            "SFT-CHEM-NUCHEM-003-TIME-RELATION": row["decay_correction_and_reference_time_retained"] and len(row["complete_half_life_vector"]) == 3,
            "SFT-CHEM-NUCHEM-003-COMPLETE-SOURCES": row["complete_registered_source_surface_retained"],
        }
        summary = {"massic_activity_rows": 2, "half_life_rows": 3, "sr90_massic_activity_kBq_per_g": "29.492 ± 0.088", "u232_massic_activity_Bq_per_g": "26.30 ± 0.23"}
    elif claim_id == BRANCHING_SPEC.claim_id:
        row = analysis["nuchem_004"]
        checks = {
            "SFT-CHEM-NUCHEM-004-CHANNELS": len(row["complete_channel_vector"]) == 5,
            "SFT-CHEM-NUCHEM-004-DAUGHTERS": len(row["complete_daughter_vector"]) == 4,
            "SFT-CHEM-NUCHEM-004-BRANCH-FRACTIONS": "fraction of decays" in row["probability_per_decay_relation"] and row["numeric_probability_per_decay_rows_in_registered_sources"].startswith("absent"),
            "SFT-CHEM-NUCHEM-004-CHEMICAL-RECOVERY": "monitoring radiochemical procedures" in row["chemical_recovery_custody"],
            "SFT-CHEM-NUCHEM-004-PARTITION": "without renormalizing after omission" in row["partition_support"],
            "SFT-CHEM-NUCHEM-004-METHODS": len(row["primary_method_vector"]) == 4 and len(row["complete_confirmatory_method_vector"]) == 5,
            "SFT-CHEM-NUCHEM-004-ADVERSE-UNCERTAINTY": len(row["complete_assumption_discrepancy_uncertainty_vector"]["confirmations"]) == 3 and row["unavailable_numeric_branch_fractions_preserved_as_unavailable_not_fabricated"],
            "SFT-CHEM-NUCHEM-004-COMPLETE-SOURCES": row["complete_registered_source_surface_retained"],
        }
        summary = {"channel_rows": 5, "daughter_rows": 4, "numeric_branch_fraction_status": "unavailable_in_registered_sources__preserved_not_fabricated", "method_rows": 9}
    else:
        raise ValueError("unknown NUCHEM-001–004 claim")
    if omit_last:
        checks.pop(next(reversed(checks)))
    spec = {item.claim_id: item for item in SPECS}[claim_id]
    if tuple(checks) != tuple(target.target_id for target in spec.target_rows) or not all(checks.values()):
        raise ValueError(f"{claim_id} comparison changed")
    return {**summary, "complete_family_pdf_pages": pages, "complete_family_html_documents": documents, "complete_family_characters": characters, "complete_result_vector_sha256": recorded, "all_favorable_adverse_absent_unavailable_unresolved_uncertainty_assumption_correction_signed_zero_decimal_continuum_and_historical_inscriptions_retained_as_external_provenance_only": True}, checks


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
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError("NUCHEM-001–004 prediction package changed")
        release = vault.release(prediction); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction); boundary.measurement_context(release.targets)
        comparisons = tuple({"target_id": target, "predicted": execution.output.label, "observed": release.targets[target].label, "passed": execution.output.label == release.targets[target].label} for target in checks)
        try: exact_analysis(self.root, self.spec.claim_id, True); omission = False
        except ValueError: omission = True
        passed = all(row["passed"] for row in comparisons) and omission
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-nuchem-initial-batch/1", self.spec.claim_id, self.spec.falsification_condition)), prediction_seal_hash=prediction.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash: raise ValueError("NUCHEM-001–004 target changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction.seal_hash, "analysis": analysis, "comparisons": comparisons, "omission_rejected": omission, "trace": execution.trace_hash}
        notes = ("complete four-source post-seal family retained as 8 PDF pages, 2 HTML documents and 34,442 extracted characters", f"all {len(checks)} separately registered claim targets retained", "all measured values units uncertainties assumptions discrepancies adverse absent unavailable and unresolved records remain downstream provenance")
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row.source_id for row in self.spec.target_rows), notes, sha256_identity(payload), self.spec.falsification_condition, passed)


class NuclideCarrierValidator(_Validator):
    def __init__(self, root): super().__init__(root, CARRIER_SPEC)
class RadioactiveTransformationValidator(_Validator):
    def __init__(self, root): super().__init__(root, TRANSFORMATION_SPEC)
class ActivityAmountTimeValidator(_Validator):
    def __init__(self, root): super().__init__(root, ACTIVITY_SPEC)
class RadioactiveBranchingYieldValidator(_Validator):
    def __init__(self, root): super().__init__(root, BRANCHING_SPEC)


__all__ = ("ActivityAmountTimeValidator", "NuclideCarrierValidator", "RadioactiveBranchingYieldValidator", "RadioactiveTransformationValidator", "exact_analysis")
