"""Capability-closed post-seal validation for Chemistry KIN-003."""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.chemistry.temperature_dependence_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, PDF_HASH, PDF_PATH, PRIMARY_HASH, PRIMARY_PATH, TARGET_HASH, TARGET_PATH,
    TEMPERATURE_DEPENDENCE_SPEC,
)
from sft.chemistry.temperature_dependence_law_v1 import (
    TemperatureRateRow, external_positive_magnitude, forced_temperature_dependence,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldTable, FoldWord, HostilePackageAuditor,
    TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release,
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
        raise ValueError("KIN-003 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "reaction_identity", "measurement_method", "temperature_K_external_inscription",
        "total_density_1e16_molecule_cm_minus3_external_inscription",
        "rate_coefficient_molecule_minus1_cm3_s_minus1_external_inscription", "target_payload", "target_payload_hash",
    }
    if (
        document.get("complete_target_count") != 19 or document.get("complete_condition_row_count") != 14
        or document.get("all_temperature_rate_density_uncertainty_method_note_and_target_hash_values_absent") is not True
        or len(rows) != 19 or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("KIN-003 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"temperature-rate-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, (family, label) in enumerate((
            ("complete-source-identity", row["source_id"]),
            ("table-number", row["table_number"]),
            ("positive-source-condition-row-ordinal", str(row["source_condition_row_ordinal"])),
            ("registered-reaction-key", row["reaction_key"]),
        ), start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        for family, label in (
            ("reaction-law", "held-registered-reaction-per-row"),
            ("intervention-law", "exact-positive-temperature-with-complete-condition-record"),
            ("response-law", "exact-positive-elementary-rate-with-all-adverse-rows-retained"),
            ("relation-law", "complete-source-ordered-table-without-imported-or-fitted-form"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-temperature-rate-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-temperature-rate-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": TEMPERATURE_DEPENDENCE_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": TEMPERATURE_DEPENDENCE_SPEC.experiment_id,
        "claim_id": TEMPERATURE_DEPENDENCE_SPEC.claim_id,
        "provenance": "forward_forcing_with_prefetch_value_free_identity_seal",
        "frozen_relation": TEMPERATURE_DEPENDENCE_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_primary_pdf": (PDF_PATH, PDF_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in TEMPERATURE_DEPENDENCE_SPEC.target_rows),
        "all_temperature_rate_density_uncertainty_method_note_and_target_hash_values_absent": True,
        "falsification_condition": TEMPERATURE_DEPENDENCE_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 19:
        raise ValueError("KIN-003 prediction is not the complete nineteen-target table")
    resolved = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id" or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 9:
            raise ValueError("KIN-003 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 19:
        raise ValueError("KIN-003 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (PDF_PATH, PDF_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError(f"KIN-003 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_target_count") != 19 or document.get("complete_condition_row_count") != 14
        or document.get("release_requires_complete_identity_prediction_seal") is not True or len(targets) != 19
    ):
        raise ValueError("KIN-003 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        keys = ("target_id", "source_id", "table_number", "source_condition_row_ordinal", "reaction_key")
        if any(identity[key] != target.get(key) for key in keys):
            raise ValueError("KIN-003 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def exact_temperature_dependence_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    law_rows = []
    temperatures = []
    densities = []
    rates = []
    uncertainty_records = 0
    reaction_counts: dict[str, int] = {}
    for target_ordinal, row in enumerate(rows, start=1):
        target = row["target_payload"]
        if (
            target.get("reaction_identity") not in {"OH + ethanol", "OH + propan-2-ol"}
            or "Laval" not in target.get("measurement_method", "")
            or target.get("fitted_arrhenius_prefactor_or_activation_value_used_in_fold_law") is not False
            or "95 percent confidence" not in target.get("source_error_disclosure", "")
        ):
            raise ValueError("KIN-003 source reaction, method or error disclosure changed")
        temperature = external_positive_magnitude(target["temperature_K_external_inscription"])
        density = external_positive_magnitude(target["total_density_1e16_molecule_cm_minus3_external_inscription"])
        rate = external_positive_magnitude(target["rate_coefficient_molecule_minus1_cm3_s_minus1_external_inscription"])
        uncertainties = tuple(external_positive_magnitude(target[name]) for name in (
            "temperature_uncertainty_K_external_inscription",
            "total_density_uncertainty_1e16_molecule_cm_minus3_external_inscription",
            "rate_uncertainty_molecule_minus1_cm3_s_minus1_external_inscription",
        ))
        uncertainty_records += len(uncertainties)
        reaction_counts[target["reaction_key"]] = reaction_counts.get(target["reaction_key"], 0) + 1
        law_rows.append(TemperatureRateRow(
            HeldLabel("registered-reaction", target["reaction_key"]),
            HeldLabel(
                "complete-condition",
                f"{target['bath_gas']}-density-{target['total_density_1e16_molecule_cm_minus3_external_inscription']}-source-row-{target['source_condition_row_ordinal']}",
            ),
            temperature, rate, PositiveCount(int(target["source_condition_row_ordinal"])),
            PositiveCount(target_ordinal), uncertainties,
        ))
        temperatures.append(temperature.fraction)
        densities.append(density.fraction)
        rates.append(rate.fraction)
    relation = forced_temperature_dependence(tuple(law_rows))
    matrix = tuple(primary.get("complete_source_ordered_table_matrix", ()))
    absence_cells = sum(
        row[key] == "EmptyOne"
        for row in matrix
        for key in (
            "ethanol_rate_1e_minus11_molecule_minus1_cm3_s_minus1_external_inscription",
            "propan-2-ol_rate_1e_minus11_molecule_minus1_cm3_s_minus1_external_inscription",
        )
    )
    return {
        "complete_target_count": len(rows),
        "complete_condition_row_count": len(matrix),
        "complete_uncertainty_record_count": uncertainty_records,
        "reaction_target_counts": reaction_counts,
        "structural_absence_cell_count": absence_cells,
        "exact_temperature_range_K": {"minimum": str(min(temperatures)), "maximum": str(max(temperatures))},
        "exact_density_range_1e16_molecule_cm_minus3": {"minimum": str(min(densities)), "maximum": str(max(densities))},
        "exact_rate_range_molecule_minus1_cm3_s_minus1": {"minimum": str(min(rates)), "maximum": str(max(rates))},
        "all_nineteen_targets_retained_in_source_order": tuple(row[5].value for row in relation.ordered_rows) == tuple(range(1, 20)),
        "both_registered_reactions_retained": reaction_counts == {"ethanol": 13, "propan-2-ol": 6},
        "all_fifty_seven_uncertainty_coordinates_retained": uncertainty_records == 57,
        "all_fourteen_condition_rows_and_nine_absences_retained": len(matrix) == 14 and absence_cells == 9,
        "complete_pdf_and_measured_table_preserved": (
            primary.get("complete_pdf_page_count") == 27
            and primary.get("all_table_1_rows_columns_uncertainties_absences_and_note_preserved") is True
        ),
        "fitted_table_excluded_without_value_selection": primary.get("fitted_table_2_excluded_by_prefetch_measured_table_rule") is True,
        "no_imported_or_fitted_form_or_selection": (
            primary.get("arrhenius_exponential_logarithmic_prefactor_activation_value_continuum_derivative_selection_fit_or_target_correction_used_in_law") is False
            and primary.get("external_values_used_as_proof_parameters") is False
        ),
    }


class TemperatureDependenceValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = TEMPERATURE_DEPENDENCE_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash,
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("KIN-003 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-temperature-rate-row-hash", row["target_payload_hash"])
            for row in source_rows
        }
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets=target_values,
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        expected_laws = (
            "held-registered-reaction-per-row",
            "exact-positive-temperature-with-complete-condition-record",
            "exact-positive-elementary-rate-with-all-adverse-rows-retained",
            "complete-source-ordered-table-without-imported-or-fitted-form",
        )
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = (
                row["source_id"], row["table_number"], str(row["source_condition_row_ordinal"]), row["reaction_key"],
            )
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, start=1)
            )
            law_match = tuple(cell.label for cell in word.cells[5:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel(
                "external-temperature-rate-row-hash", row["target_payload_hash"]
            )
            comparisons.append({
                "target_id": row["target_id"], "identity_match": identity_match,
                "law_match": law_match, "postseal_target_hash_match": target_match,
                "passed": identity_match and law_match and target_match,
            })
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_temperature_dependence_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]
        payload = dict(tampered[0]["target_payload"])
        payload["temperature_K_external_inscription"] = "-1"
        tampered[0] = {**tampered[0], "target_payload": payload}
        try:
            exact_temperature_dependence_analysis(tuple(tampered), primary)
            tamper_rejected = False
        except (ValueError, RuntimeError):
            tamper_rejected = True
        controls = {
            "tampered_negative_temperature_rejected": tamper_rejected,
            "complete_nineteen_target_vector_retained": len(release.targets) == 19,
            "source_order_reactions_and_uncertainties_retained": (
                analysis["all_nineteen_targets_retained_in_source_order"]
                and analysis["both_registered_reactions_retained"]
                and analysis["all_fifty_seven_uncertainty_coordinates_retained"]
            ),
            "complete_pdf_measured_table_and_structural_absences_retained": (
                analysis["complete_pdf_and_measured_table_preserved"]
                and analysis["all_fourteen_condition_rows_and_nine_absences_retained"]
            ),
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {
            "complete_target_count", "complete_condition_row_count", "complete_uncertainty_record_count",
            "reaction_target_counts", "structural_absence_cell_count", "exact_temperature_range_K",
            "exact_density_range_1e16_molecule_cm_minus3", "exact_rate_range_molecule_minus1_cm3_s_minus1",
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and all(bool(value) for key, value in analysis.items() if key not in non_boolean)
            and all(controls.values())
        )
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-temperature-dependence-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("KIN-003 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {
            "experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash, "analysis": analysis,
            "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash,
        }
        measurements = tuple(
            f"{row['target_id']}: condition-row={row['source_condition_row_ordinal']}; reaction={row['reaction_key']}; target={row['target_payload_hash']}"
            for row in source_rows
        ) + (
            f"exact temperature range K: {analysis['exact_temperature_range_K']}",
            f"exact rate range molecule^-1 cm^3 s^-1: {analysis['exact_rate_range_molecule_minus1_cm3_s_minus1']}",
            "complete primary measured Table 1: fourteen condition rows, nineteen measured targets, fifty-seven uncertainty coordinates and nine structural absences; no imported or fitted temperature law",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash,
            isolation_certificate=isolation, target_custody_certificate=custody,
            evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True,
            data_source_ids=(source_rows[0]["source_id"],), measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition, passed=passed,
        )


__all__ = (
    "TemperatureDependenceValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_temperature_dependence_analysis", "experiment_registration_record", "prediction_program_document",
)
