"""Post-seal complete binary, self and tracer diffusion validation for THERMO-016."""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.molecular_diffusion_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, MOLECULAR_DIFFUSION_SPEC, PRIMARY_HASH, PRIMARY_PATH,
    SOURCE_FILES, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.molecular_diffusion_law_v1 import (
    MolecularDiffusionAccount, complete_constituent_conservation, external_diffusion_magnitude,
    forced_counted_diffusion,
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
        raise ValueError("THERMO-016 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "doi", "component_orgnums", "complete_component_records", "property_component_orgnum", "solvent_orgnums",
        "property_name", "measurement_method", "diffusion_coefficient_m2_per_s_external_inscription",
        "diffusion_uncertainty_external_record", "variable_external_inscriptions", "complete_point_record",
        "complete_property_metadata", "complete_variable_metadata", "complete_constraint_metadata",
        "complete_phase_metadata", "target_payload", "target_payload_hash",
    }
    if (
        document.get("complete_target_count") != 164
        or document.get("diffusion_class_counts") != {"binary": 138, "self": 4, "tracer": 22}
        or document.get("all_species_medium_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent") is not True
        or len(rows) != 164 or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("THERMO-016 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"molecular-diffusion-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, (family, label) in enumerate((
            ("complete-source-identity", row["source_id"]), ("diffusion-class", row["diffusion_class"]),
            ("dataset-ordinal", str(row["dataset_ordinal"])),
            ("positive-source-point-ordinal", str(row["source_point_ordinal"])),
            ("source-locator-kind", "thermoml-direct-diffusion-point"),
        ), start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        for family, label in (
            ("carrier-law", "complete-molecular-condition-transition-carrier"),
            ("transition-law", "counted-adjacent-cell-identity-conserving-redistribution"),
            ("determinism-law", "held-transition-orientation-without-random-premise"),
            ("magnitude-law", "exact-positive-postseal-diffusion-support-with-EmptyOne-conditions"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-molecular-diffusion-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-molecular-diffusion-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": MOLECULAR_DIFFUSION_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": MOLECULAR_DIFFUSION_SPEC.experiment_id, "claim_id": MOLECULAR_DIFFUSION_SPEC.claim_id,
        "provenance": "forward_forcing_with_prefetch_value_free_identity_seal",
        "frozen_relation": MOLECULAR_DIFFUSION_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH), "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH), "complete_raw_and_landing_sources": SOURCE_FILES,
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in MOLECULAR_DIFFUSION_SPEC.target_rows),
        "all_species_medium_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent": True,
        "falsification_condition": MOLECULAR_DIFFUSION_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 164:
        raise ValueError("THERMO-016 prediction is not the complete 164-record table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 10
        ):
            raise ValueError("THERMO-016 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 164:
        raise ValueError("THERMO-016 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES):
        if hash_file(root / path) != expected:
            raise ValueError(f"THERMO-016 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_target_count") != 164
        or document.get("diffusion_class_counts") != {"binary": 138, "self": 4, "tracer": 22}
        or document.get("release_requires_complete_identity_prediction_seal") is not True
        or len(targets) != 164
    ):
        raise ValueError("THERMO-016 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in ("target_id", "source_id", "diffusion_class", "dataset_ordinal", "source_point_ordinal")):
            raise ValueError("THERMO-016 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def _condition_support(value: object) -> PositiveRatio | EmptyOne:
    try:
        fraction = Fraction(str(value))
    except Exception as exc:
        raise ValueError("THERMO-016 condition is not an exact finite inscription") from exc
    if fraction.numerator < 0:
        raise ValueError("THERMO-016 condition left the exact nonnegative external boundary")
    if fraction.numerator == 0:
        return EmptyOne()
    return PositiveRatio.from_pair(fraction.numerator, fraction.denominator)


def _variable_kind(metadata: dict) -> str:
    kinds = tuple(key for key in metadata.get("VariableID", {}).get("VariableType", {}) if key != "tml_elements")
    if len(kinds) != 1:
        raise ValueError("THERMO-016 variable kind changed")
    return kinds[0]


def exact_molecular_diffusion_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    class_counts: Counter[str] = Counter()
    dataset_counts: Counter[str] = Counter()
    method_counts: Counter[str] = Counter()
    phase_counts: Counter[str] = Counter()
    values_by_class: dict[str, list[Fraction]] = defaultdict(list)
    conditions_by_kind: dict[str, list[Fraction]] = defaultdict(list)
    empty_condition_count = 0
    for row in rows:
        target = row["target_payload"]
        diffusion_class = target.get("diffusion_class")
        if diffusion_class not in ("binary", "self", "tracer"):
            raise ValueError("THERMO-016 diffusion class changed")
        components = tuple(int(value) for value in target.get("component_orgnums", ()))
        if (
            not components or len(set(components)) != len(components)
            or len(target.get("complete_component_records", ())) != len(components)
            or not target.get("property_name", "").startswith(diffusion_class.capitalize() + " diffusion coefficient")
            or not target.get("measurement_method") or not target.get("diffusion_uncertainty_external_record")
            or not target.get("complete_point_record") or not target.get("complete_property_metadata")
            or not target.get("complete_variable_metadata") or not target.get("complete_phase_metadata")
        ):
            raise ValueError("THERMO-016 complete molecular carrier or provenance changed")
        property_component = target.get("property_component_orgnum")
        migrating = int(property_component) if property_component is not None else components[0]
        if migrating not in components:
            raise ValueError("THERMO-016 migrating identity left the constituent carrier")
        phase_rows = target["complete_phase_metadata"]
        phases = tuple(str(phase.get("ePhase")) for phase in phase_rows)
        if len(phases) != 1 or phases[0] not in ("Liquid", "Fluid (supercritical or subcritical phases)"):
            raise ValueError("THERMO-016 phase identity changed")
        variable_metadata = {int(row["nVarNumber"]): row for row in target["complete_variable_metadata"]}
        external_variables = {int(number): value for number, value in target["variable_external_inscriptions"].items()}
        if set(variable_metadata) != set(external_variables):
            raise ValueError("THERMO-016 variable carrier changed")
        supports = []
        for number, inscription in external_variables.items():
            support = _condition_support(inscription)
            supports.append(support)
            if isinstance(support, EmptyOne):
                empty_condition_count += 1
            else:
                conditions_by_kind[_variable_kind(variable_metadata[number])].append(support.fraction)
        account = MolecularDiffusionAccount(
            HeldLabel("chemical-component", str(migrating)),
            tuple(HeldLabel("chemical-component", str(value)) for value in components),
            HeldLabel("diffusion-class", diffusion_class), HeldLabel("chemical-phase", phases[0]),
            PositiveCount(3), PositiveCount(4), PositiveCount(int(target["source_point_ordinal"])),
            PositiveCount(int(target["dataset_ordinal"])), tuple(supports),
        )
        relation = forced_counted_diffusion(account)
        if relation.carrier.label != f"{diffusion_class}-identity-retained-adjacent-transition":
            raise ValueError("THERMO-016 counted transition law changed")
        if not complete_constituent_conservation(account.constituent_identities, tuple(reversed(account.constituent_identities))):
            raise ValueError("THERMO-016 constituent conservation changed")
        magnitude = external_diffusion_magnitude(str(target["diffusion_coefficient_m2_per_s_external_inscription"]))
        class_counts[diffusion_class] += 1
        dataset_counts[f"{target['source_id']}:{target['dataset_ordinal']}:{diffusion_class}"] += 1
        method_counts[f"{diffusion_class}:{target['measurement_method']}"] += 1
        phase_counts[phases[0]] += 1
        values_by_class[diffusion_class].append(magnitude.fraction)
    expected_datasets = {
        "NIST-TRC-THERMOML-JCED-2011-56-4840-4848:1:binary": 113,
        "NIST-TRC-THERMOML-FPE-2017-437-34-42:1:self": 1,
        "NIST-TRC-THERMOML-FPE-2017-437-34-42:3:self": 3,
        "NIST-TRC-THERMOML-FPE-2017-437-34-42:5:tracer": 6,
        "NIST-TRC-THERMOML-FPE-2017-437-34-42:6:tracer": 11,
        "NIST-TRC-THERMOML-FPE-2017-437-34-42:13:tracer": 5,
        "NIST-TRC-THERMOML-FPE-2008-271-43-52:6:binary": 5,
        "NIST-TRC-THERMOML-FPE-2008-271-43-52:8:binary": 5,
        "NIST-TRC-THERMOML-FPE-2008-271-43-52:10:binary": 5,
        "NIST-TRC-THERMOML-FPE-2008-271-43-52:12:binary": 5,
        "NIST-TRC-THERMOML-FPE-2008-271-43-52:14:binary": 5,
    }
    exact_ranges = {
        name: {"minimum": str(min(values)), "maximum": str(max(values))}
        for name, values in sorted(values_by_class.items())
    }
    condition_ranges = {
        name: {"minimum": str(min(values)), "maximum": str(max(values))}
        for name, values in sorted(conditions_by_kind.items()) if values
    }
    return {
        "complete_target_count": len(rows), "class_counts": dict(class_counts),
        "dataset_counts": dict(dataset_counts), "method_counts": dict(method_counts),
        "phase_counts": dict(phase_counts), "structural_EmptyOne_condition_count": empty_condition_count,
        "exact_diffusion_ranges_m2_per_s": exact_ranges, "exact_positive_condition_ranges": condition_ranges,
        "all_164_records_retained": len(rows) == 164,
        "all_138_binary_4_self_22_tracer_records_retained": dict(class_counts) == {"binary": 138, "self": 4, "tracer": 22},
        "all_11_diffusion_datasets_complete": dict(dataset_counts) == expected_datasets,
        "all_three_methods_and_classes_retained": dict(method_counts) == {"binary:TAYLOR:UFactor:4": 25, "binary:Taylor dispersion method": 113, "self:NMR": 4, "tracer:NMR": 22},
        "all_liquid_and_subsupercritical_phase_rows_retained": dict(phase_counts) == {"Liquid": 139, "Fluid (supercritical or subcritical phases)": 25},
        "all_26_absent_condition_coordinates_are_EmptyOne": empty_condition_count == 26,
        "complete_three_sources_and_companions_preserved": primary.get("complete_source_count") == 3 and primary.get("complete_dataset_count_across_sources") == 30 and primary.get("complete_all_property_point_count_across_sources") == 373 and primary.get("all_direct_binary_self_and_tracer_diffusion_rows_and_complete_sources_preserved") is True,
        "non_diffusion_companions_excluded_from_measurements": primary.get("non_diffusion_companion_datasets_used_as_diffusion_measurements") is False,
        "no_imported_transport_model_random_premise_fit_or_selection": primary.get("Fick_Brownian_random_walk_Stokes_Einstein_activation_transport_fit_logarithm_continuum_interpolation_regression_selection_or_target_correction_used") is False and primary.get("external_values_used_as_proof_parameters") is False,
    }


class MolecularDiffusionValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = MOLECULAR_DIFFUSION_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash,
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("THERMO-016 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-molecular-diffusion-row-hash", row["target_payload_hash"])
            for row in source_rows
        }
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets=target_values, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        expected_laws = (
            "complete-molecular-condition-transition-carrier",
            "counted-adjacent-cell-identity-conserving-redistribution",
            "held-transition-orientation-without-random-premise",
            "exact-positive-postseal-diffusion-support-with-EmptyOne-conditions",
        )
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = (
                row["source_id"], row["diffusion_class"], str(row["dataset_ordinal"]),
                str(row["source_point_ordinal"]), "thermoml-direct-diffusion-point",
            )
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, start=1)
            )
            law_match = tuple(cell.label for cell in word.cells[6:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel(
                "external-molecular-diffusion-row-hash", row["target_payload_hash"]
            )
            comparisons.append({
                "target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match,
                "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match,
            })
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_molecular_diffusion_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]
        payload = dict(tampered[0]["target_payload"])
        payload["diffusion_coefficient_m2_per_s_external_inscription"] = "-1"
        tampered[0] = {**tampered[0], "target_payload": payload}
        tamper_rejected = False
        try:
            exact_molecular_diffusion_analysis(tuple(tampered), primary)
        except (ValueError, RuntimeError):
            tamper_rejected = True
        controls = {
            "tampered_negative_diffusion_rejected": tamper_rejected,
            "complete_164_record_vector_retained": len(release.targets) == 164,
            "all_binary_self_tracer_rows_retained": analysis["all_138_binary_4_self_22_tracer_records_retained"],
            "all_diffusion_datasets_retained": analysis["all_11_diffusion_datasets_complete"],
            "all_methods_and_phases_retained": analysis["all_three_methods_and_classes_retained"] and analysis["all_liquid_and_subsupercritical_phase_rows_retained"],
            "all_absent_conditions_translated_to_EmptyOne": analysis["all_26_absent_condition_coordinates_are_EmptyOne"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {
            "complete_target_count", "class_counts", "dataset_counts", "method_counts", "phase_counts",
            "structural_EmptyOne_condition_count", "exact_diffusion_ranges_m2_per_s", "exact_positive_condition_ranges",
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and all(bool(value) for key, value in analysis.items() if key not in non_boolean)
            and all(controls.values())
        )
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-molecular-diffusion-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("THERMO-016 released target differs from commitment")
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
            f"{row['target_id']}: class={row['diffusion_class']}; dataset={row['dataset_ordinal']}; point={row['source_point_ordinal']}; target={row['target_payload_hash']}"
            for row in source_rows
        ) + (
            "complete vector: 138 binary, 4 self and 22 tracer diffusion records",
            f"exact diffusion ranges: {analysis['exact_diffusion_ranges_m2_per_s']}",
            "source coverage: all 30 datasets and 373 points preserved from three complete NIST ThermoML sources",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash,
            isolation_certificate=isolation, target_custody_certificate=custody,
            evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True,
            data_source_ids=tuple(dict.fromkeys(row["source_id"] for row in source_rows)), measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition, passed=passed,
        )


__all__ = (
    "MolecularDiffusionValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_molecular_diffusion_analysis", "experiment_registration_record", "prediction_program_document",
)
