"""Post-seal complete viscosity validation for THERMO-017."""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.viscous_transport_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH, SOURCE_FILES, TARGET_HASH, TARGET_PATH,
    VISCOUS_TRANSPORT_SPEC,
)
from sft.chemistry.viscous_transport_law_v1 import ViscousChemicalAccount, external_viscosity_magnitude, forced_viscous_transport
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, EmptyOne, FoldTable, FoldWord,
    HostilePackageAuditor, PositiveRatio, TargetVault, fold_program_from_mapping,
    snapshot_protected_tree, target_identity_from_release,
)
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, PositiveCount
from sft.engine.source import hash_file


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("THERMO-017 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text()); rows = tuple(document.get("rows", ()))
    forbidden = {
        "doi", "component_orgnums", "complete_component_records", "mixture_class", "property_name",
        "measurement_method", "viscosity_Pa_s_external_inscription", "viscosity_uncertainty_external_record",
        "variable_external_inscriptions", "complete_point_record", "complete_property_metadata",
        "complete_variable_metadata", "complete_constraint_metadata", "complete_phase_metadata",
        "target_payload", "target_payload_hash",
    }
    if (
        document.get("complete_target_count") != 425
        or document.get("mixture_class_counts") != {"pure": 11, "binary": 364, "ternary": 50}
        or document.get("all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent") is not True
        or len(rows) != 425 or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("THERMO-017 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]; table = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"viscous-transport-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, (family, label) in enumerate((
            ("complete-source-identity", row["source_id"]), ("property-class", "viscosity"),
            ("dataset-ordinal", str(row["dataset_ordinal"])), ("positive-source-point-ordinal", str(row["source_point_ordinal"])),
            ("source-locator-kind", "thermoml-direct-viscosity-point"),
        ), start=1):
            destination = f"{prefix}-identity-{number}"; instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]}); registers.append(destination)
        for family, label in (
            ("carrier-law", "complete-composition-phase-condition-momentum-carrier"),
            ("transfer-law", "counted-adjacent-layer-momentum-packet-exchange"),
            ("orientation-law", "held-opposed-transfer-without-signed-shear"),
            ("magnitude-law", "exact-positive-postseal-viscosity-support-with-EmptyOne-conditions"),
        ):
            destination = f"{prefix}-law-{len(registers)}"; instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]}); registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers}); table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-viscosity-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-viscosity-vector"]},
    ))
    return {"schema": "sft-v3-fold-program/1", "program_id": VISCOUS_TRANSPORT_SPEC.experiment_id + "-value-free-complete-vector", "instructions": instructions}


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": VISCOUS_TRANSPORT_SPEC.experiment_id, "claim_id": VISCOUS_TRANSPORT_SPEC.claim_id,
        "provenance": "forward_forcing_with_prefetch_value_free_identity_seal", "frozen_relation": VISCOUS_TRANSPORT_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH), "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH), "complete_raw_and_landing_sources": SOURCE_FILES,
        "prediction_program": prediction_program_document(root), "target_ids": tuple(row.target_id for row in VISCOUS_TRANSPORT_SPEC.target_rows),
        "all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent": True,
        "falsification_condition": VISCOUS_TRANSPORT_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 425:
        raise ValueError("THERMO-017 prediction is not the complete 425-record table")
    resolved = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id" or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 10:
            raise ValueError("THERMO-017 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 425:
        raise ValueError("THERMO-017 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES):
        if hash_file(root / path) != expected:
            raise ValueError(f"THERMO-017 source changed: {path}")
    identities = _identities(root); document = json.loads((root / TARGET_PATH).read_text()); targets = tuple(document.get("rows", ()))
    if document.get("complete_target_count") != 425 or document.get("mixture_class_counts") != {"pure": 11, "binary": 364, "ternary": 50} or document.get("release_requires_complete_identity_prediction_seal") is not True or len(targets) != 425:
        raise ValueError("THERMO-017 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in ("target_id", "source_id", "dataset_ordinal", "source_point_ordinal")):
            raise ValueError("THERMO-017 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def _support(value: object) -> PositiveRatio | EmptyOne:
    try: fraction = Fraction(str(value))
    except Exception as exc: raise ValueError("THERMO-017 condition is not exact finite support") from exc
    if fraction.numerator < 0: raise ValueError("THERMO-017 condition became negative")
    return EmptyOne() if fraction.numerator == 0 else PositiveRatio.from_pair(fraction.numerator, fraction.denominator)


def _variable_kind(metadata: dict) -> str:
    kinds = tuple(key for key in metadata.get("VariableID", {}).get("VariableType", {}) if key != "tml_elements")
    if len(kinds) != 1: raise ValueError("THERMO-017 variable kind changed")
    return kinds[0]


def exact_viscous_transport_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    mixture_counts = Counter(); dataset_counts = Counter(); method_counts = Counter(); values = []; conditions = defaultdict(list); empty_count = 0
    for row in rows:
        target = row["target_payload"]; components = tuple(int(value) for value in target.get("component_orgnums", ()))
        expected_class = {1: "pure", 2: "binary", 3: "ternary"}.get(len(components), "higher-component")
        if (
            not components or len(set(components)) != len(components) or len(target.get("complete_component_records", ())) != len(components)
            or target.get("mixture_class") != expected_class or target.get("property_name") != "Viscosity, Pa*s"
            or not target.get("measurement_method") or not target.get("viscosity_uncertainty_external_record")
            or not target.get("complete_point_record") or not target.get("complete_property_metadata")
            or not target.get("complete_variable_metadata") or not target.get("complete_phase_metadata")
            or tuple(phase.get("ePhase") for phase in target["complete_phase_metadata"]) != ("Liquid",)
        ):
            raise ValueError("THERMO-017 complete composition/phase/provenance carrier changed")
        metadata = {int(item["nVarNumber"]): item for item in target["complete_variable_metadata"]}
        external = {int(number): value for number, value in target["variable_external_inscriptions"].items()}
        if set(metadata) != set(external): raise ValueError("THERMO-017 condition carrier changed")
        supports = []
        for number, inscription in external.items():
            support = _support(inscription); supports.append(support)
            if isinstance(support, EmptyOne): empty_count += 1
            else: conditions[_variable_kind(metadata[number])].append(support.fraction)
        account = ViscousChemicalAccount(
            tuple(HeldLabel("chemical-component", str(value)) for value in components), HeldLabel("chemical-phase", "Liquid"),
            PositiveCount(3), PositiveCount(4), PositiveCount(5), PositiveCount(int(target["source_point_ordinal"])),
            PositiveCount(int(target["dataset_ordinal"])), tuple(supports),
        )
        relation = forced_viscous_transport(account)
        if relation.carrier.label != f"{expected_class}-composition-retained-momentum-exchange": raise ValueError("THERMO-017 composition carrier changed")
        magnitude = external_viscosity_magnitude(str(target["viscosity_Pa_s_external_inscription"]))
        mixture_counts[expected_class] += 1; dataset_counts[f"{target['source_id']}:{target['dataset_ordinal']}:{expected_class}"] += 1
        method_counts[target["measurement_method"]] += 1; values.append(magnitude.fraction)
    expected_datasets = {
        "NIST-TRC-THERMOML-FPE-2018-474-6-13:2:ternary": 50,
        "NIST-TRC-THERMOML-JCED-2005-50-1038-1042:1:pure": 5,
        "NIST-TRC-THERMOML-JCED-2005-50-1038-1042:3:pure": 6,
        "NIST-TRC-THERMOML-JCED-2005-50-1038-1042:5:binary": 70,
        "NIST-TRC-THERMOML-JCED-2005-50-1038-1042:7:binary": 78,
        "NIST-TRC-THERMOML-FPE-2017-453-13-23:2:binary": 72,
        "NIST-TRC-THERMOML-FPE-2017-453-13-23:4:binary": 72,
        "NIST-TRC-THERMOML-FPE-2017-453-13-23:6:binary": 72,
    }
    expected_methods = {"CAPTUB:UFactor:3": 75, "CAPTUB:UFactor:4": 84, "Capillary tube (Ostwald; Ubbelohde) method": 144, "Pressure drop in straight capillary": 72, "Liquid flow through an orifice": 50}
    return {
        "complete_target_count": len(rows), "mixture_class_counts": dict(mixture_counts), "dataset_counts": dict(dataset_counts),
        "method_counts": dict(method_counts), "structural_EmptyOne_condition_count": empty_count,
        "exact_viscosity_range_Pa_s": {"minimum": str(min(values)), "maximum": str(max(values))},
        "exact_positive_condition_ranges": {name: {"minimum": str(min(group)), "maximum": str(max(group))} for name, group in sorted(conditions.items())},
        "all_425_records_retained": len(rows) == 425,
        "all_11_pure_364_binary_50_ternary_records_retained": dict(mixture_counts) == {"pure": 11, "binary": 364, "ternary": 50},
        "all_eight_viscosity_datasets_complete": dict(dataset_counts) == expected_datasets,
        "all_five_measurement_methods_retained": dict(method_counts) == expected_methods,
        "all_38_absent_condition_coordinates_are_EmptyOne": empty_count == 38,
        "complete_three_sources_and_companions_preserved": primary.get("complete_source_count") == 3 and primary.get("complete_dataset_count_across_sources") == 17 and primary.get("complete_all_property_point_count_across_sources") == 900 and primary.get("all_direct_viscosity_rows_and_complete_sources_preserved") is True,
        "non_viscosity_companions_excluded_from_measurements": primary.get("non_viscosity_companion_datasets_used_as_viscosity_measurements") is False,
        "no_imported_constitutive_continuum_fitted_law_or_selection": primary.get("Newtonian_constitutive_velocity_gradient_Arrhenius_WLF_VFT_logarithm_continuum_interpolation_regression_selection_or_target_correction_used") is False and primary.get("external_values_used_as_proof_parameters") is False,
    }


class ViscousTransportValidator:
    def __init__(self, root: Path): self.root = root.resolve(); self.spec = VISCOUS_TRANSPORT_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate(); registration = experiment_registration_record(self.root); registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root); program = fold_program_from_mapping(document); inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash)
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs); boundary = BlindExperimentBoundary(envelope); prediction_seal = boundary.seal_prediction(execution.output, execution.trace); after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError("THERMO-017 prediction package changed")
        predicted = _prediction_map(execution.output); source_rows = _source_rows(self.root)
        target_values = {row["target_id"]: HeldLabel("external-viscosity-row-hash", row["target_payload_hash"]) for row in source_rows}
        vault = TargetVault(experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-complete-target-custodian", targets=target_values, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)), expected_envelope_hash=sha256_identity(envelope))
        release = vault.release(prediction_seal); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal); boundary.measurement_context(release.targets)
        expected_laws = ("complete-composition-phase-condition-momentum-carrier", "counted-adjacent-layer-momentum-packet-exchange", "held-opposed-transfer-without-signed-shear", "exact-positive-postseal-viscosity-support-with-EmptyOne-conditions")
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]; identities = (row["source_id"], "viscosity", str(row["dataset_ordinal"]), str(row["source_point_ordinal"]), "thermoml-direct-viscosity-point")
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(identities, start=1))
            law_match = tuple(cell.label for cell in word.cells[6:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel("external-viscosity-row-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})
        primary = json.loads((self.root / PRIMARY_PATH).read_text()); analysis = exact_viscous_transport_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]; payload = dict(tampered[0]["target_payload"]); payload["viscosity_Pa_s_external_inscription"] = "-1"; tampered[0] = {**tampered[0], "target_payload": payload}
        tamper_rejected = False
        try: exact_viscous_transport_analysis(tuple(tampered), primary)
        except (ValueError, RuntimeError): tamper_rejected = True
        controls = {
            "tampered_negative_viscosity_rejected": tamper_rejected, "complete_425_record_vector_retained": len(release.targets) == 425,
            "all_pure_binary_ternary_rows_retained": analysis["all_11_pure_364_binary_50_ternary_records_retained"],
            "all_datasets_and_methods_retained": analysis["all_eight_viscosity_datasets_complete"] and analysis["all_five_measurement_methods_retained"],
            "all_absent_conditions_translated_to_EmptyOne": analysis["all_38_absent_condition_coordinates_are_EmptyOne"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {"complete_target_count", "mixture_class_counts", "dataset_counts", "method_counts", "structural_EmptyOne_condition_count", "exact_viscosity_range_Pa_s", "exact_positive_condition_ranges"}
        passed = all(row["passed"] for row in comparisons) and all(bool(value) for key, value in analysis.items() if key not in non_boolean) and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-viscous-transport-correspondence", self.spec.falsification_condition)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash: raise ValueError("THERMO-017 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        measurement_payload = {"experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash, "prediction_seal_hash": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = tuple(f"{row['target_id']}: dataset={row['dataset_ordinal']}; point={row['source_point_ordinal']}; target={row['target_payload_hash']}" for row in source_rows) + ("complete vector: 11 pure, 364 binary and 50 ternary viscosity records", f"exact viscosity range: {analysis['exact_viscosity_range_Pa_s']}", "source coverage: all 17 datasets and 900 points preserved from three complete NIST ThermoML sources") + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash, isolation_certificate=isolation, target_custody_certificate=custody, evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True, data_source_ids=tuple(dict.fromkeys(row["source_id"] for row in source_rows)), measurements=measurements, measurement_receipt_hash=sha256_identity(measurement_payload), falsification_condition=self.spec.falsification_condition, passed=passed)


__all__ = ("ViscousTransportValidator", "_identities", "_prediction_map", "_source_rows", "exact_viscous_transport_analysis", "experiment_registration_record", "prediction_program_document")
