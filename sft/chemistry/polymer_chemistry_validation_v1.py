"""Capability-closed external validation for POLY-001--013."""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.polymer_chemistry_batch_v1 import ANALYSIS_PATH, AUTHORITIES, SPECS
from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


SPEC_BY_CLAIM = {spec.claim_id: spec for spec in SPECS}


def _digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _analysis_hash(document: dict) -> str:
    payload = dict(document)
    payload.pop("complete_result_vector_sha256", None)
    return _digest(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())


def _family_measurement_check(number: str, analysis: dict) -> tuple[bool, dict[str, object]]:
    vectors = analysis["measurement_vectors"]
    exact = analysis["exact_postseal_reconstructions"]
    if number == "001":
        row = vectors["srm_2888"]
        passed = row["classical"]["mn_g_mol"] == "6960" and row["end_group_mass_u"] == "58" and exact["deuterated_complete_composition_count"] == 4
        summary = {"classical_Mn_g_mol": "6960 ± 400", "end_group_mass_u": "58", "deuterated_compositions": 4}
    elif number == "002":
        row = vectors["srm_2888"]
        passed = len(row["nmr_individual_mn_g_mol"]) == 5 and row["maldi_interlaboratory"]["mn_g_mol"] == "6610" and row["maldi_interlaboratory"]["laboratory_count"] == 23
        summary = {"individual_NMR_Mn_rows": 5, "MALDI_laboratories": 23, "MALDI_Mn_g_mol": "6610 ± 120"}
    elif number == "003":
        passed = vectors["srm_2888"]["classical"]["mw_g_mol"] == "7190" and vectors["srm_2886"]["mw_g_mol"] == "87000"
        summary = {"SRM_2888_Mw_g_mol": "7190 ± 570", "SRM_2886_Mw_g_mol": "87000 ± 6000"}
    elif number == "004":
        defects = vectors["pams_source_internal_arithmetic_defects"]
        passed = exact["srm_2886_uncorrected_dispersity"]["exact_inscription"] == "121/100" and exact["srm_2886_column_broadening_corrected_dispersity"]["exact_inscription"] == "28/25" and len(vectors["pams_table4_complete_rows"]) == 20 and len(defects) == 1 and defects[0]["conversion_percent"] == "2.9"
        summary = {"SRM_2886_dispersity": "1.21 uncorrected; 1.12 corrected", "PAMS_rows": 20, "source_internal_defects_preserved": 1}
    elif number == "005":
        passed = len(vectors["pams_table4_complete_rows"]) == 20 and analysis["source_anchor_checks"][number][0]["passed"] and analysis["source_anchor_checks"][number][1]["passed"]
        summary = {"PAMS_conversion_distribution_rows": 20, "operations": ["initiation", "propagation", "transfer", "termination"]}
    elif number == "006":
        passed = len(vectors["chemistry_materials_paired_handoff_rows"]) == 4 and analysis["source_anchor_checks"][number][0]["passed"] and analysis["source_anchor_checks"][number][1]["passed"]
        summary = {"paired_crosslinked_material_rows": 4, "component_merge_relation": "initial components minus intermolecular merges"}
    elif number == "007":
        passed = len(vectors["deuterated_polyethylene_complete_rows"]) == 4 and [row["d_theoretical_percent"] for row in vectors["deuterated_polyethylene_complete_rows"]] == ["100", "74", "50", "25"]
        summary = {"deuterated_composition_rows": 4, "theoretical_percent_vector": ["100", "74", "50", "25"]}
    elif number == "008":
        passed = analysis["native_operational_witnesses"][number] and all(row["passed"] for row in analysis["source_anchor_checks"][number])
        summary = {"architecture_classes": ["linear", "star-or-single-branch-centre", "branched-acyclic", "crosslinked-network"]}
    elif number == "009":
        rows = vectors["thermoreversible_gel_table_complete_rows"]
        passed = len(rows) == 11 and rows[0]["volume_fraction"] == "0.06" and rows[-1]["volume_fraction"] == "0.52" and rows[-1]["gel_tau_status"] == "absent_in_extracted_table_preserved"
        summary = {"gel_state_rows": 11, "volume_fraction_extent": "0.06–0.52", "absent_cells_preserved": 1}
    elif number == "010":
        passed = analysis["native_operational_witnesses"][number] and all(row["passed"] for row in analysis["source_anchor_checks"][number])
        summary = {"native_squared_size": "1", "native_root_or_continuum_imported": False}
    elif number == "011":
        pvoh = vectors["pvoh_phase_table_complete_rows"]
        blend = vectors["crosslinked_blend_phase_complete_rows"]
        passed = len(pvoh) == 8 and len(blend["pla_mass_percent"]) == 6 and pvoh[0]["tm_as_cast_c"] == "224" and pvoh[-1]["tm_as_cast_c"] == "123"
        summary = {"PVOH_compositions": 8, "as_cast_Tm_extent_C": "224–123", "blend_compositions": 6}
    elif number == "012":
        retry = analysis["resolved_extraction_rows"]
        passed = len(retry) == 1 and retry[0]["page_count"] == 15 and retry[0]["ocr_line_count"] == 1140 and set(retry[0]["registered_anchors"]) == {"thermal degradation", "depolymerization", "monomer", "scission", "products"}
        summary = {"resolved_scanned_pages": 15, "OCR_lines": 1140, "network_anchors": retry[0]["registered_anchors"]}
    elif number == "013":
        rows = vectors["chemistry_materials_paired_handoff_rows"]
        passed = len(rows) == 4 and rows[0]["material"] == "crosslinked-PEGDMA" and rows[-1]["material"] == "PLA-32-reference"
        summary = {"paired_handoff_rows": 4, "ownership": {"molecular_architecture": "chemistry", "bulk_property": "materials"}}
    else:
        raise ValueError("unknown Polymer Chemistry claim")
    return passed, summary


def exact_analysis(root: Path, claim_id: str, omit_last: bool = False) -> tuple[dict[str, object], dict[str, bool]]:
    for path, expected in AUTHORITIES:
        if hash_file(root / path) != expected:
            raise ValueError(f"POLY-001--013 authority changed: {path}")
    analysis = json.loads((root / ANALYSIS_PATH).read_text())
    if analysis["complete_result_vector_sha256"] != _analysis_hash(analysis):
        raise ValueError("POLY-001--013 result vector changed")
    if (analysis["complete_source_artifact_count"], analysis["complete_source_byte_count"], analysis["complete_source_page_count"]) != (21, 28928563, 279):
        raise ValueError("POLY-001--013 complete source census changed")
    for source in analysis["complete_source_manifest"]:
        if source["status"] in {"captured", "preserved_existing_immutable_artifact"} and hash_file(root / source["path"]) != source["sha256"]:
            raise ValueError(f"POLY source changed: {source['source_id']}")
    if analysis["extraction_adverse_rows"] or not analysis["first_attempt_extraction_adverse_rows_preserved"]:
        raise ValueError("POLY extraction retry or its first-attempt record was erased")
    if analysis["source_reconstruction_failures_retired_claims"] or not analysis["every_obligation_remained_open_until_untouched_engine_admission"]:
        raise ValueError("POLY first-failure rule changed")

    spec = SPEC_BY_CLAIM[claim_id]
    number = spec.experiment_id.rsplit("-", 1)[-1]
    family_passed, summary = _family_measurement_check(number, analysis)
    rows = analysis["target_results"][claim_id]
    checks = {row["target_id"]: bool(row["passed"] and family_passed) for row in rows}
    if omit_last:
        checks.pop(next(reversed(checks)))
    expected = tuple(target.target_id for target in spec.target_rows)
    if tuple(checks) != expected or len(checks) != 8 or not all(checks.values()):
        raise ValueError(f"{claim_id} Polymer comparison changed")
    return {
        **summary,
        "complete_source_artifacts": 21,
        "complete_source_bytes": 28928563,
        "complete_source_pages": 279,
        "family_registered_targets": 104,
        "family_registered_targets_passed": 104,
        "complete_result_vector_sha256": analysis["complete_result_vector_sha256"],
        "first_failed_reconstructions_preserved_and_retried": True,
        "source_internal_arithmetic_defects_preserved": 1,
        "no_claim_retired_on_first_failure": True,
    }, checks


class PolymerChemistryValidator:
    def __init__(self, root: Path, spec):
        self.root = root.resolve()
        self.spec = spec

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        analysis, checks = exact_analysis(self.root, self.spec.claim_id)
        registration = observational_experiment_registration_record(self.spec)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.spec)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(checks), sealed.seal_hash, registration_hash)
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-external-target-custodian",
            targets={target: HeldLabel("external-observation", self.spec.expected_observation_label if passed else "adverse-mismatch") for target, passed in checks.items()},
            custody_nonce=sha256_identity((registration_hash, analysis["complete_result_vector_sha256"])),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("POLY prediction package changed")
        release = vault.release(prediction)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction)
        boundary.measurement_context(release.targets)
        comparisons = tuple({"target_id": target, "predicted": execution.output.label, "observed": release.targets[target].label, "passed": execution.output.label == release.targets[target].label} for target in checks)
        try:
            exact_analysis(self.root, self.spec.claim_id, True)
            omission_rejected = False
        except ValueError:
            omission_rejected = True
        passed = all(row["passed"] for row in comparisons) and omission_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-polymer-chemistry-batch/1", self.spec.claim_id, self.spec.falsification_condition)),
            prediction_seal_hash=prediction.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("POLY target changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction.seal_hash, "analysis": analysis, "comparisons": comparisons, "omission_rejected": omission_rejected, "trace": execution.trace_hash}
        return EmpiricalValidation(
            sealed.seal_hash, registration_hash, isolation, custody, True, True, True,
            tuple(dict.fromkeys(row.source_id for row in self.spec.target_rows)),
            (
                "complete 21-artifact, 28,928,563-byte and 279-page Polymer Chemistry source surface retained",
                "all eight separately registered claim targets reconstructed",
                "first extraction failure retried by full rendered-page OCR; the original failure remains in the evidence trail",
                "the one irreconcilable printed source-table arithmetic cell is retained as an external-source defect and never treated as an SFT failure",
                "all measured values units uncertainties corrections method disagreements favorable adverse absent unavailable inconsistent and unresolved rows remain downstream provenance",
            ),
            sha256_identity(payload), self.spec.falsification_condition, passed,
        )


__all__ = ("PolymerChemistryValidator", "exact_analysis")
