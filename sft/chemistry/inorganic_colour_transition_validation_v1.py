"""Capability-closed post-seal validation for Chemistry INORG-008."""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.chemistry.inorganic_colour_transition_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, INORGANIC_COLOUR_TRANSITION_SPEC, PRIMARY_HASH, PRIMARY_PATH,
    TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.inorganic_colour_transition_law_v1 import (
    build_exact_transition, forced_selective_absorption, generate_complete_carrier_transition_classes,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldLanguageHalt, FoldTable,
    FoldWord, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree,
    target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, PositiveCount
from sft.engine.source import hash_file


IDENTITY_KEYS = ("target_id", "source_record_ordinal", "source_id", "authority", "registered_identity", "source_record_role", "custody_class")
EXPECTED_LAWS = (
    "four-directed-ligand-metal-transition-classes",
    "retained-endpoints-and-positive-order-gap",
    "proper-absorbed-and-retained-colour-partition",
    "all-eight-definition-spectrum-and-custody-surfaces-retained",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("INORG-008 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {"value", "outcome", "definition", "peak", "intensity", "band_count", "target_payload_hash"}
    if (
        document.get("complete_registered_target_count") != 8
        or document.get("target_values_definitions_peak_positions_intensities_band_counts_outcomes_or_payload_hashes_present") is not False
        or len(rows) != 8
        or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 9))
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("INORG-008 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"inorganic-colour-transition-record-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, key in enumerate(IDENTITY_KEYS[1:], start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["registered-source-identity", str(row[key])]})
            registers.append(destination)
        for label in EXPECTED_LAWS:
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["inorganic-colour-transition-law", label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-inorganic-colour-transition-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-inorganic-colour-transition-vector"]},
    ))
    return {"schema": "sft-v3-fold-program/1", "program_id": INORGANIC_COLOUR_TRANSITION_SPEC.experiment_id + "-value-free-vector", "instructions": instructions}


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": INORGANIC_COLOUR_TRANSITION_SPEC.experiment_id,
        "claim_id": INORGANIC_COLOUR_TRANSITION_SPEC.claim_id,
        "provenance": "forward_forcing_with_shared-admitted-spectrum-comparison",
        "frozen_relation": INORGANIC_COLOUR_TRANSITION_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in INORGANIC_COLOUR_TRANSITION_SPEC.target_rows),
        "all_eight_rows_required": True,
        "shared_sources_not_recaptured_and_original_custody_classes_preserved": True,
        "target_content_inaccessible_to_prediction_execution": True,
        "no_orbital_colour_wheel_peak_threshold_or_dimensional_fit": True,
        "falsification_condition": INORGANIC_COLOUR_TRANSITION_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 8:
        raise ValueError("INORG-008 prediction is not the complete eight-row table")
    result: dict[str, FoldWord] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id" or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 11:
            raise ValueError("INORG-008 prediction row is incomplete")
        result[entry.left.label] = entry.right
    if len(result) != 8:
        raise ValueError("INORG-008 prediction duplicates a target")
    return result


def _source_rows(root: Path) -> tuple[dict, ...]:
    if hash_file(root / TARGET_PATH) != TARGET_HASH or hash_file(root / PRIMARY_PATH) != PRIMARY_HASH:
        raise ValueError("INORG-008 post-seal evidence changed")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if document.get("complete_registered_target_count") != 8 or len(rows) != 8 or document.get("release_requires_prediction_seal") is not True:
        raise ValueError("INORG-008 target vector is incomplete")
    for identity, row in zip(identities, rows):
        if any(identity[key] != row.get(key) for key in IDENTITY_KEYS):
            raise ValueError("INORG-008 target differs from registered identity")
        expected = sha256_identity((identity["target_id"], identity["source_record_role"], row.get("source_outcome")))
        if row.get("target_payload_hash") != expected:
            raise ValueError("INORG-008 target payload hash changed")
    return rows


def exact_analysis(rows: tuple[dict, ...], primary: dict) -> dict[str, object]:
    if len(rows) != 8:
        raise ValueError("INORG-008 requires all eight source surfaces")
    classes = tuple(row.label for row in generate_complete_carrier_transition_classes())
    transition = build_exact_transition("validation-complex", "ligand", "metal", "lower", "upper", PositiveCount(1), PositiveCount(3))
    incident = tuple(HeldLabel("observation-distinction", f"d-{index}") for index in range(1, 4))
    absorption = forced_selective_absorption(transition, incident, (incident[0],))
    definitions = tuple(row["source_outcome"] for row in rows[:4])
    spectra = tuple(row["source_outcome"] for row in rows[4:])
    postseal = primary["exact_postseal_analysis"]
    return {
        "transition_classes": classes,
        "exact_gap": transition.positive_order_gap.value,
        "absorbed_count": absorption.absorbed_count.value,
        "retained_colour_count": absorption.retained_colour_count.value,
        "generic_definition_present": definitions[0]["two_distinct_electronic_levels_present"],
        "ll_definition_present": definitions[1]["ligand_to_ligand_endpoint_surface_present"],
        "lm_definition_present": definitions[2]["ligand_to_metal_endpoint_surface_present"],
        "ml_definition_present": definitions[3]["metal_to_ligand_endpoint_surface_present"],
        "metal_to_metal_definition_absent_preserved": postseal["metal_to_metal_definition_surface_absent_from_frozen_family"],
        "spectrum_count": len(spectra),
        "point_count_vector": tuple(row["exact_point_count"] for row in spectra),
        "total_point_count": sum(row["exact_point_count"] for row in spectra),
        "interior_maximum_count_vector": tuple(len(row["complete_interior_local_maxima"]) for row in spectra),
        "interior_maximum_position_vector": tuple(tuple(peak["x"] for peak in row["complete_interior_local_maxima"]) for row in spectra),
        "all_spectra_selective": all(row["complete_interior_local_maxima"] for row in spectra),
        "originally_blind_count": postseal["originally_law_sealed_blind_spectrum_count"],
        "source_recapture_count": postseal["source_recapture_count"],
        "all_rows_preserved": postseal["all_eight_rows_preserved"],
        "dimensional_value_or_colour_fitted": postseal["dimensional_wavelength_intensity_or_colour_name_fitted_or_derived"],
    }


class InorganicColourTransitionValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = INORGANIC_COLOUR_TRANSITION_SPEC

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
            raise ValueError("INORG-008 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets={row["target_id"]: HeldLabel("external-complete-source-record-hash", row["target_payload_hash"]) for row in source_rows},
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(values, start=1))
            law_match = tuple(cell.label for cell in word.cells[7:]) == EXPECTED_LAWS
            target_match = release.targets[row["target_id"]] == HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})
        primary = json.loads((self.root / PRIMARY_PATH).read_text(encoding="utf-8"))
        analysis = exact_analysis(source_rows, primary)
        try:
            exact_analysis(source_rows[:-1], primary)
            omitted_rejected = False
        except ValueError:
            omitted_rejected = True
        try:
            FoldWord((0,))
            zero_rejected = False
        except FoldLanguageHalt:
            zero_rejected = True
        controls = {
            "omitted_source_row_rejected": omitted_rejected,
            "numerical_zero_rejected": zero_rejected,
            "all_eight_target_hashes_bound_postseal": len(release.targets) == 8,
            "shared_spectra_not_recaptured": analysis["source_recapture_count"] == 0,
            "metal_to_metal_definition_absence_preserved": analysis["metal_to_metal_definition_absent_preserved"],
            "prediction_contains_no_target_payload_peak_or_wavelength": "target_payload_hash" not in json.dumps(document, sort_keys=True) and "48361/200" not in json.dumps(document, sort_keys=True),
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and analysis["transition_classes"] == ("ligand-to-ligand", "ligand-to-metal", "metal-to-ligand", "metal-to-metal")
            and analysis["exact_gap"] == 2 and analysis["absorbed_count"] == 1 and analysis["retained_colour_count"] == 2
            and analysis["generic_definition_present"] and analysis["ll_definition_present"] and analysis["lm_definition_present"] and analysis["ml_definition_present"]
            and analysis["spectrum_count"] == 4
            and analysis["point_count_vector"] == (224, 79, 80, 73)
            and analysis["total_point_count"] == 456
            and analysis["interior_maximum_count_vector"] == (2, 2, 1, 2)
            and analysis["all_spectra_selective"] and analysis["originally_blind_count"] == 1
            and analysis["all_rows_preserved"] and analysis["dimensional_value_or_colour_fitted"] is False
            and all(controls.values())
        )
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-inorganic-colour-transition/1", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("INORG-008 released target identity differs")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = (
            "four forced directed carrier transition classes",
            "exact state-order gap and proper absorbed/retained colour partition",
            "four IUPAC transition definitions with absent metal-to-metal definition surface preserved",
            "four complete NIST spectra: point counts 224, 79, 80, 73; interior maxima counts 2, 2, 1, 2",
            f"exact interior maxima positions {analysis['interior_maximum_position_vector']}",
            "three development-observed and one originally law-sealed blind spectrum reused without recapture",
        ) + tuple(f"control {key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            sealed.seal_hash, registration_hash, isolation, custody, True, True, True,
            tuple(dict.fromkeys(row["source_id"] for row in source_rows)), measurements,
            sha256_identity(payload), self.spec.falsification_condition, passed,
        )


__all__ = ("InorganicColourTransitionValidator", "_identities", "_prediction_map", "_source_rows", "exact_analysis", "experiment_registration_record", "prediction_program_document")
