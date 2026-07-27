"""Capability-closed post-seal validation for Chemistry KIN-002."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.concentration_dependence_batch_v1 import (
    CONCENTRATION_DEPENDENCE_SPEC, IDENTITY_HASH, IDENTITY_PATH, PDF_HASH, PDF_PATH, PRIMARY_HASH, PRIMARY_PATH,
    TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.concentration_dependence_law_v1 import (
    ConcentrationRateRow, external_positive_magnitude, forced_concentration_dependence,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, EmptyOne, FoldTable, FoldWord,
    HostilePackageAuditor, PositiveRatio, TargetVault, fold_program_from_mapping,
    snapshot_protected_tree, target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, PositiveCount
from sft.engine.source import hash_file


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("KIN-002 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "reaction_identity", "measurement_method", "temperature_K_external_inscription",
        "flow_density_1e16_molecule_cm_minus3_external_inscription",
        "rate_coefficient_molecule_minus1_cm3_s_minus1_external_inscription", "target_payload", "target_payload_hash",
    }
    if (
        document.get("complete_target_count") != 9
        or document.get("all_species_temperature_density_rate_uncertainty_method_note_and_target_hash_values_absent") is not True
        or len(rows) != 9 or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("KIN-002 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"concentration-rate-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, (family, label) in enumerate((
            ("complete-source-identity", row["source_id"]), ("table-number", row["table_number"]),
            ("positive-source-row-ordinal", str(row["source_row_ordinal"])), ("source-locator-kind", "complete-primary-concentration-rate-table-row"),
        ), start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        for family, label in (
            ("reactant-law", "one-held-registered-reactant"),
            ("intervention-law", "exact-positive-concentration-with-complete-condition-record"),
            ("response-law", "exact-positive-elementary-rate-with-all-adverse-rows-retained"),
            ("relation-law", "complete-source-ordered-table-without-fitted-exponent"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-concentration-rate-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-concentration-rate-vector"]},
    ))
    return {"schema": "sft-v3-fold-program/1", "program_id": CONCENTRATION_DEPENDENCE_SPEC.experiment_id + "-value-free-complete-vector", "instructions": instructions}


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": CONCENTRATION_DEPENDENCE_SPEC.experiment_id, "claim_id": CONCENTRATION_DEPENDENCE_SPEC.claim_id,
        "provenance": "forward_forcing_with_prefetch_value_free_identity_seal", "frozen_relation": CONCENTRATION_DEPENDENCE_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH), "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH), "complete_primary_pdf": (PDF_PATH, PDF_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in CONCENTRATION_DEPENDENCE_SPEC.target_rows),
        "all_species_temperature_density_rate_uncertainty_method_note_and_target_hash_values_absent": True,
        "falsification_condition": CONCENTRATION_DEPENDENCE_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 9:
        raise ValueError("KIN-002 prediction is not the complete nine-row table")
    resolved = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id" or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 9:
            raise ValueError("KIN-002 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 9:
        raise ValueError("KIN-002 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (PDF_PATH, PDF_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError(f"KIN-002 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if document.get("complete_target_count") != 9 or document.get("release_requires_complete_identity_prediction_seal") is not True or len(targets) != 9:
        raise ValueError("KIN-002 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in ("target_id", "source_id", "table_number", "source_row_ordinal")):
            raise ValueError("KIN-002 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def exact_concentration_dependence_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    law_rows = []
    densities = []
    rates = []
    temperatures = []
    uncertainty_records = 0
    note_markers = []
    for row in rows:
        target = row["target_payload"]
        if (
            target.get("reaction_identity") != "OH + dimethyl ether" or "Laval" not in target.get("measurement_method", "")
            or target.get("fitted_exponent_or_coefficient_used_in_fold_law") is not False
            or "pseudo-first-order" not in target.get("source_table_fit_disclosure", "")
        ):
            raise ValueError("KIN-002 source reaction, method or fit disclosure changed")
        temperature = external_positive_magnitude(target["temperature_K_external_inscription"])
        density = external_positive_magnitude(target["flow_density_1e16_molecule_cm_minus3_external_inscription"])
        rate = external_positive_magnitude(target["rate_coefficient_molecule_minus1_cm3_s_minus1_external_inscription"])
        uncertainties = tuple(external_positive_magnitude(target[name]) for name in (
            "temperature_uncertainty_K_external_inscription", "flow_density_uncertainty_1e16_molecule_cm_minus3_external_inscription",
            "rate_uncertainty_molecule_minus1_cm3_s_minus1_external_inscription",
        ))
        uncertainty_records += len(uncertainties)
        note_markers.append(target.get("source_note_markers", ""))
        law_rows.append(ConcentrationRateRow(
            HeldLabel("registered-reactant", "OH-plus-DME"),
            HeldLabel("complete-condition", f"temperature-{target['temperature_K_external_inscription']}-K"),
            density, rate, PositiveCount(int(row["source_row_ordinal"])), uncertainties + (EmptyOne(),),
        ))
        densities.append(density.fraction)
        rates.append(rate.fraction)
        temperatures.append(temperature.fraction)
    relation = forced_concentration_dependence(tuple(law_rows))
    source_order = tuple(item[3].value for item in relation.ordered_rows)
    return {
        "complete_target_count": len(rows), "complete_uncertainty_record_count": uncertainty_records,
        "source_note_markers_in_order": note_markers,
        "exact_temperature_range_K": {"minimum": str(min(temperatures)), "maximum": str(max(temperatures))},
        "exact_flow_density_range_1e16_molecule_cm_minus3": {"minimum": str(min(densities)), "maximum": str(max(densities))},
        "exact_rate_range_molecule_minus1_cm3_s_minus1": {"minimum": str(min(rates)), "maximum": str(max(rates))},
        "all_nine_rows_retained_in_source_order": source_order == tuple(range(1, 10)),
        "all_27_uncertainty_coordinates_retained": uncertainty_records == 27,
        "all_notes_and_adverse_rows_retained": len(note_markers) == 9,
        "complete_pdf_and_table_preserved": primary.get("complete_pdf_page_count") == 13 and primary.get("all_table_2_rows_uncertainties_and_notes_preserved") is True,
        "no_imported_power_order_fit_or_selection": primary.get("mass_action_power_law_reaction_order_fitted_exponent_coefficient_logarithm_continuum_derivative_selection_or_target_correction_used_in_law") is False and primary.get("external_values_used_as_proof_parameters") is False,
    }


class ConcentrationDependenceValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = CONCENTRATION_DEPENDENCE_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash)
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("KIN-002 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {row["target_id"]: HeldLabel("external-concentration-rate-row-hash", row["target_payload_hash"]) for row in source_rows}
        vault = TargetVault(experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-complete-target-custodian", targets=target_values, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)), expected_envelope_hash=sha256_identity(envelope))
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        expected_laws = ("one-held-registered-reactant", "exact-positive-concentration-with-complete-condition-record", "exact-positive-elementary-rate-with-all-adverse-rows-retained", "complete-source-ordered-table-without-fitted-exponent")
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = (row["source_id"], row["table_number"], str(row["source_row_ordinal"]), "complete-primary-concentration-rate-table-row")
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(identity_values, start=1))
            law_match = tuple(cell.label for cell in word.cells[5:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel("external-concentration-rate-row-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_concentration_dependence_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]
        payload = dict(tampered[0]["target_payload"]); payload["flow_density_1e16_molecule_cm_minus3_external_inscription"] = "-1"; tampered[0] = {**tampered[0], "target_payload": payload}
        try:
            exact_concentration_dependence_analysis(tuple(tampered), primary); tamper_rejected = False
        except (ValueError, RuntimeError):
            tamper_rejected = True
        controls = {
            "tampered_negative_density_rejected": tamper_rejected, "complete_nine_row_vector_retained": len(release.targets) == 9,
            "source_order_and_uncertainties_retained": analysis["all_nine_rows_retained_in_source_order"] and analysis["all_27_uncertainty_coordinates_retained"],
            "complete_pdf_and_table_retained": analysis["complete_pdf_and_table_preserved"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {"complete_target_count", "complete_uncertainty_record_count", "source_note_markers_in_order", "exact_temperature_range_K", "exact_flow_density_range_1e16_molecule_cm_minus3", "exact_rate_range_molecule_minus1_cm3_s_minus1"}
        passed = all(row["passed"] for row in comparisons) and all(bool(value) for key, value in analysis.items() if key not in non_boolean) and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-concentration-dependence-correspondence", self.spec.falsification_condition)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("KIN-002 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        measurement_payload = {"experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash, "prediction_seal_hash": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = tuple(f"{row['target_id']}: source-row={row['source_row_ordinal']}; target={row['target_payload_hash']}" for row in source_rows) + (f"exact density range: {analysis['exact_flow_density_range_1e16_molecule_cm_minus3']}", f"exact rate range: {analysis['exact_rate_range_molecule_minus1_cm3_s_minus1']}", "complete primary Table 2: nine rows and 27 uncertainty coordinates; no fitted exponent in the Fold law") + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash, isolation_certificate=isolation, target_custody_certificate=custody, evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True, data_source_ids=(source_rows[0]["source_id"],), measurements=measurements, measurement_receipt_hash=sha256_identity(measurement_payload), falsification_condition=self.spec.falsification_condition, passed=passed)


__all__ = ("ConcentrationDependenceValidator", "_identities", "_prediction_map", "_source_rows", "exact_concentration_dependence_analysis", "experiment_registration_record", "prediction_program_document")
