"""Capability-closed blind validation for Chemistry THERMO-019."""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.coupled_transport_batch_v1 import (
    COUPLED_TRANSPORT_SPEC, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH,
    SOURCE_FILES, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.coupled_transport_law_v1 import CoupledTransportAccount, forced_coupled_transport
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


PAIR_COUNTS = {"mass-heat": 22, "mass-charge": 146, "heat-charge": 64}
ROLE_COUNTS = {
    "mass-response-under-thermal-forcing": 22, "charge-response": 147,
    "mass-response-under-charge-probe": 31, "heat-response": 32,
}
PROPERTY_COUNTS = {
    "Binary diffusion coefficient, m2/s": 22, "Electrical conductivity, S/m": 147,
    "Thermal conductivity, W/m/K": 32, "Tracer diffusion coefficient, m2/s": 31,
}
METHOD_COUNTS = {
    "thermal-diffusion forced Rayleigh scattering": 22,
    "Radiometer CDM 210 Meterlab conductimeter with a CDC 745-9 cell": 115,
    "Electrochemistry (cyclic voltametry)": 31,
    "Coaxial cylinder method": 32,
    "contact method": 32,
}


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("THERMO-019 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "doi", "response_role", "component_orgnums", "complete_component_records", "mixture_class",
        "property_name", "property_phase", "measurement_method", "coupled_response_external_inscription",
        "coupled_response_uncertainty_external_record", "variable_external_inscriptions", "complete_point_record",
        "complete_property_metadata", "complete_variable_metadata", "complete_constraint_metadata",
        "complete_phase_metadata", "target_payload", "target_payload_hash",
    }
    if (
        document.get("complete_target_count") != 232 or document.get("complete_source_count") != 3
        or document.get("carrier_pair_counts") != PAIR_COUNTS
        or document.get("all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent") is not True
        or len(rows) != 232 or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("THERMO-019 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"coupled-transport-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, (family, label) in enumerate((
            ("complete-source-identity", row["source_id"]), ("carrier-pair", row["carrier_pair"]),
            ("dataset-ordinal", str(row["dataset_ordinal"])), ("property-number", str(row["property_number"])),
            ("positive-source-point-ordinal", str(row["source_point_ordinal"])),
            ("source-locator-kind", "thermoml-direct-coupled-transport-point"),
        ), start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        for family, label in (
            ("carrier-law", "complete-composition-phase-mass-heat-charge-triad"),
            ("transition-law", "counted-shared-adjacent-cell-event-ledger"),
            ("orientation-law", "held-per-carrier-directions-without-signed-flux"),
            ("magnitude-law", "exact-positive-postseal-pairwise-response-with-EmptyOne-conditions"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-coupled-transport-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-coupled-transport-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": COUPLED_TRANSPORT_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": COUPLED_TRANSPORT_SPEC.experiment_id, "claim_id": COUPLED_TRANSPORT_SPEC.claim_id,
        "provenance": "forward_forcing_with_prefetch_value_free_identity_seal",
        "frozen_relation": COUPLED_TRANSPORT_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH), "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH), "complete_raw_and_landing_sources": SOURCE_FILES,
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in COUPLED_TRANSPORT_SPEC.target_rows),
        "all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent": True,
        "falsification_condition": COUPLED_TRANSPORT_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 232:
        raise ValueError("THERMO-019 prediction is not the complete 232-record table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 11
        ):
            raise ValueError("THERMO-019 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 232:
        raise ValueError("THERMO-019 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES):
        if hash_file(root / path) != expected:
            raise ValueError(f"THERMO-019 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_target_count") != 232 or document.get("carrier_pair_counts") != PAIR_COUNTS
        or document.get("response_role_counts") != ROLE_COUNTS or document.get("property_counts") != PROPERTY_COUNTS
        or document.get("mixture_class_counts") != {"binary": 137, "ternary": 95}
        or document.get("measurement_method_counts") != METHOD_COUNTS
        or document.get("release_requires_complete_identity_prediction_seal") is not True or len(targets) != 232
    ):
        raise ValueError("THERMO-019 target registry changed")
    keys = ("target_id", "source_id", "carrier_pair", "dataset_ordinal", "property_number", "source_point_ordinal")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in keys):
            raise ValueError("THERMO-019 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def _support(value: object) -> PositiveRatio | EmptyOne:
    try:
        fraction = Fraction(str(value))
    except Exception as exc:
        raise ValueError("THERMO-019 support is not exact finite") from exc
    if fraction.numerator < 0:
        raise ValueError("THERMO-019 support became negative")
    return EmptyOne() if fraction.numerator == 0 else PositiveRatio.from_pair(fraction.numerator, fraction.denominator)


def _positive_external(value: object) -> PositiveRatio:
    support = _support(value)
    if isinstance(support, EmptyOne):
        raise ValueError("THERMO-019 measured response became absent")
    return support


def _kind(metadata: dict, outer: str, inner: str) -> str:
    kinds = tuple(key for key in metadata.get(outer, {}).get(inner, {}) if key != "tml_elements")
    if len(kinds) != 1:
        raise ValueError("THERMO-019 condition kind changed")
    return kinds[0]


def exact_coupled_transport_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    pairs: Counter[str] = Counter(); roles: Counter[str] = Counter(); properties: Counter[str] = Counter()
    mixtures: Counter[str] = Counter(); methods: Counter[str] = Counter(); datasets: Counter[str] = Counter()
    values: defaultdict[str, list[Fraction]] = defaultdict(list)
    conditions: defaultdict[str, list[Fraction]] = defaultdict(list)
    empty_count = 0
    expected_roles = {
        ("mass-heat", "Binary diffusion coefficient, m2/s"): "mass-response-under-thermal-forcing",
        ("mass-charge", "Electrical conductivity, S/m"): "charge-response",
        ("mass-charge", "Tracer diffusion coefficient, m2/s"): "mass-response-under-charge-probe",
        ("heat-charge", "Thermal conductivity, W/m/K"): "heat-response",
        ("heat-charge", "Electrical conductivity, S/m"): "charge-response",
    }
    for row in rows:
        target = row["target_payload"]
        components = tuple(int(value) for value in target.get("component_orgnums", ()))
        expected_class = {1: "pure", 2: "binary", 3: "ternary"}.get(len(components), "higher-component")
        pair = target.get("carrier_pair"); property_name = target.get("property_name")
        if (
            not components or len(set(components)) != len(components)
            or len(target.get("complete_component_records", ())) != len(components)
            or target.get("mixture_class") != expected_class
            or expected_roles.get((pair, property_name)) != target.get("response_role")
            or target.get("property_phase") != "Liquid" or not target.get("measurement_method")
            or not target.get("coupled_response_uncertainty_external_record")
            or not target.get("complete_point_record") or not target.get("complete_property_metadata")
            or not target.get("complete_variable_metadata") or not target.get("complete_phase_metadata")
        ):
            raise ValueError("THERMO-019 complete pair/composition/phase/provenance carrier changed")
        metadata = {int(item["nVarNumber"]): item for item in target["complete_variable_metadata"]}
        external = {int(number): value for number, value in target["variable_external_inscriptions"].items()}
        if set(metadata) != set(external):
            raise ValueError("THERMO-019 condition carrier changed")
        supports: list[PositiveRatio | EmptyOne] = []
        for number, inscription in external.items():
            support = _support(inscription); supports.append(support)
            if isinstance(support, EmptyOne): empty_count += 1
            else: conditions[_kind(metadata[number], "VariableID", "VariableType")].append(support.fraction)
        for constraint in target.get("complete_constraint_metadata", ()):
            support = _support(constraint["nConstraintValue"]); supports.append(support)
            if isinstance(support, EmptyOne): empty_count += 1
            else: conditions[_kind(constraint, "ConstraintID", "ConstraintType")].append(support.fraction)
        account = CoupledTransportAccount(
            tuple(HeldLabel("chemical-component", str(value)) for value in components), HeldLabel("chemical-phase", "Liquid"),
            tuple(HeldLabel("transport-carrier", name) for name in ("mass", "heat", "charge")),
            PositiveCount(3), PositiveCount(4), (PositiveCount(2), PositiveCount(3), PositiveCount(5)),
            PositiveCount(int(target["source_point_ordinal"])), PositiveCount(int(target["dataset_ordinal"])),
            PositiveCount(int(target["property_number"])), tuple(supports),
        )
        relation = forced_coupled_transport(account)
        if relation.carrier_topology.label != f"{expected_class}-composition-phase-shared-mass-heat-charge-event-ledger" or pair not in tuple(item.label for item in relation.pairwise_projections):
            raise ValueError("THERMO-019 triad projection changed")
        magnitude = _positive_external(target["coupled_response_external_inscription"])
        pairs[pair] += 1; roles[target["response_role"]] += 1; properties[property_name] += 1
        mixtures[expected_class] += 1; methods[target["measurement_method"]] += 1
        datasets[f"{target['source_id']}:{target['dataset_ordinal']}:{target['property_number']}:{pair}:{property_name}"] += 1
        values[property_name].append(magnitude.fraction)
    return {
        "complete_target_count": len(rows), "carrier_pair_counts": dict(pairs), "response_role_counts": dict(roles),
        "property_counts": dict(properties), "mixture_class_counts": dict(mixtures),
        "measurement_method_counts": dict(methods), "coupled_dataset_counts": dict(datasets),
        "structural_EmptyOne_condition_count": empty_count,
        "exact_response_ranges_by_property": {name: {"minimum": str(min(group)), "maximum": str(max(group))} for name, group in sorted(values.items())},
        "exact_positive_condition_ranges": {name: {"minimum": str(min(group)), "maximum": str(max(group))} for name, group in sorted(conditions.items())},
        "all_232_records_retained": len(rows) == 232,
        "all_three_pairwise_surfaces_retained": dict(pairs) == PAIR_COUNTS,
        "all_response_roles_retained": dict(roles) == ROLE_COUNTS,
        "all_four_property_families_retained": dict(properties) == PROPERTY_COUNTS,
        "all_137_binary_95_ternary_records_retained": dict(mixtures) == {"binary": 137, "ternary": 95},
        "all_five_methods_retained": dict(methods) == METHOD_COUNTS,
        "all_15_coupled_datasets_complete": len(datasets) == 15 and sum(datasets.values()) == 232,
        "all_six_absent_conditions_are_EmptyOne": empty_count == 6,
        "mass_heat_surface_is_thermal_forcing_method": all(
            row["target_payload"]["measurement_method"] == "thermal-diffusion forced Rayleigh scattering"
            for row in rows if row["carrier_pair"] == "mass-heat"
        ),
        "complete_three_sources_and_companions_preserved": (
            primary.get("complete_source_count") == 3 and primary.get("complete_dataset_count_across_sources") == 23
            and primary.get("complete_all_property_point_count_across_sources") == 375
            and primary.get("complete_coupled_dataset_count") == 15
            and primary.get("all_direct_coupled_rows_and_complete_sources_preserved") is True
        ),
        "companions_excluded_from_measurements": primary.get("companion_properties_used_as_coupled_measurements") is False,
        "no_imported_matrix_continuum_fitted_law_or_selection": (
            primary.get("Onsager_matrix_continuum_gradient_flux_equation_phenomenological_cross_coefficient_signed_magnitude_fit_logarithm_interpolation_regression_selection_or_target_correction_used") is False
            and primary.get("external_values_used_as_proof_parameters") is False
        ),
    }


class CoupledTransportValidator:
    def __init__(self, root: Path):
        self.root = root.resolve(); self.spec = COUPLED_TRANSPORT_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate(); registration = experiment_registration_record(self.root); registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root); program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash)
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope); prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root); audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError("THERMO-019 prediction package changed")
        predicted = _prediction_map(execution.output); source_rows = _source_rows(self.root)
        target_values = {row["target_id"]: HeldLabel("external-coupled-transport-row-hash", row["target_payload_hash"]) for row in source_rows}
        vault = TargetVault(experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-complete-target-custodian", targets=target_values, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)), expected_envelope_hash=sha256_identity(envelope))
        release = vault.release(prediction_seal); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal); boundary.measurement_context(release.targets)
        expected_laws = ("complete-composition-phase-mass-heat-charge-triad", "counted-shared-adjacent-cell-event-ledger", "held-per-carrier-directions-without-signed-flux", "exact-positive-postseal-pairwise-response-with-EmptyOne-conditions")
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identities = (row["source_id"], row["carrier_pair"], str(row["dataset_ordinal"]), str(row["property_number"]), str(row["source_point_ordinal"]), "thermoml-direct-coupled-transport-point")
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(identities, start=1))
            law_match = tuple(cell.label for cell in word.cells[7:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel("external-coupled-transport-row-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})
        primary = json.loads((self.root / PRIMARY_PATH).read_text()); analysis = exact_coupled_transport_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]; payload = dict(tampered[0]["target_payload"]); payload["coupled_response_external_inscription"] = "-1"; tampered[0] = {**tampered[0], "target_payload": payload}
        tamper_rejected = False
        try: exact_coupled_transport_analysis(tuple(tampered), primary)
        except (ValueError, RuntimeError): tamper_rejected = True
        controls = {
            "tampered_negative_coupled_response_rejected": tamper_rejected, "complete_232_record_vector_retained": len(release.targets) == 232,
            "all_pairwise_surfaces_roles_and_properties_retained": analysis["all_three_pairwise_surfaces_retained"] and analysis["all_response_roles_retained"] and analysis["all_four_property_families_retained"],
            "all_datasets_methods_and_EmptyOne_conditions_retained": analysis["all_15_coupled_datasets_complete"] and analysis["all_five_methods_retained"] and analysis["all_six_absent_conditions_are_EmptyOne"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {"complete_target_count", "carrier_pair_counts", "response_role_counts", "property_counts", "mixture_class_counts", "measurement_method_counts", "coupled_dataset_counts", "structural_EmptyOne_condition_count", "exact_response_ranges_by_property", "exact_positive_condition_ranges"}
        passed = all(row["passed"] for row in comparisons) and all(bool(value) for key, value in analysis.items() if key not in non_boolean) and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-coupled-transport-correspondence", self.spec.falsification_condition)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash: raise ValueError("THERMO-019 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        measurement_payload = {"experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash, "prediction_seal_hash": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = tuple(f"{row['target_id']}: pair={row['carrier_pair']}; dataset={row['dataset_ordinal']}; property={row['property_number']}; point={row['source_point_ordinal']}; target={row['target_payload_hash']}" for row in source_rows) + ("complete pair vector: 22 mass-heat, 146 mass-charge and 64 heat-charge records", "complete property vector: 22 thermally forced binary diffusion, 31 charge-probed tracer diffusion, 147 electrical conductivity and 32 thermal conductivity records", "source coverage: all 23 datasets and 375 points preserved from three complete NIST ThermoML sources") + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash, isolation_certificate=isolation, target_custody_certificate=custody, evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True, data_source_ids=tuple(dict.fromkeys(row["source_id"] for row in source_rows)), measurements=measurements, measurement_receipt_hash=sha256_identity(measurement_payload), falsification_condition=self.spec.falsification_condition, passed=passed)


__all__ = ("CoupledTransportValidator", "_identities", "_prediction_map", "_source_rows", "exact_coupled_transport_analysis", "experiment_registration_record", "prediction_program_document")
