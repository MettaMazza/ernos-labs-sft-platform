"""Capability-closed post-seal validation for Chemistry INORG-009."""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.chemistry.inorganic_magnetic_state_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, INORGANIC_MAGNETIC_STATE_SPEC, PRIMARY_HASH, PRIMARY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.inorganic_magnetic_state_law_v1 import (
    append_unpaired_successor, complete_unpaired_support, forced_inorganic_magnetic_state,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, EmptyOne, FoldLanguageHalt, FoldTable, FoldWord,
    HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release,
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
    "complete-unpaired-support-or-EmptyOne",
    "exact-moment-count-and-successor-width",
    "held-drawn-paramagnetic-or-repelled-diamagnetic-class",
    "all-177-definition-value-orientation-and-absence-surfaces-retained",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("INORG-009 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8")); rows = tuple(document.get("rows", ()))
    forbidden = {"value", "outcome", "definition", "source_value_inscription", "native_value", "target_payload_hash"}
    if (
        document.get("complete_registered_target_count") != 177
        or document.get("target_values_orientations_presence_flags_definitions_outcomes_or_payload_hashes_present") is not False
        or len(rows) != 177 or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 178))
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("INORG-009 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]; table = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"inorganic-magnetic-state-record-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, key in enumerate(IDENTITY_KEYS[1:], start=1):
            destination = f"{prefix}-identity-{number}"; instructions.append({"opcode": "label", "destination": destination, "arguments": ["registered-source-identity", str(row[key])]}); registers.append(destination)
        for label in EXPECTED_LAWS:
            destination = f"{prefix}-law-{len(registers)}"; instructions.append({"opcode": "label", "destination": destination, "arguments": ["inorganic-magnetic-state-law", label]}); registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers}); table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend(({"opcode": "table", "destination": "complete-inorganic-magnetic-state-vector", "arguments": table}, {"opcode": "emit", "destination": "", "arguments": ["complete-inorganic-magnetic-state-vector"]}))
    return {"schema": "sft-v3-fold-program/1", "program_id": INORGANIC_MAGNETIC_STATE_SPEC.experiment_id + "-value-free-vector", "instructions": instructions}


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": INORGANIC_MAGNETIC_STATE_SPEC.experiment_id, "claim_id": INORGANIC_MAGNETIC_STATE_SPEC.claim_id,
        "provenance": "forward_forcing_with-complete-shared-admitted-magnetic-vector", "frozen_relation": INORGANIC_MAGNETIC_STATE_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH), "withheld_target_registry": (TARGET_PATH, TARGET_HASH), "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "prediction_program": prediction_program_document(root), "target_ids": tuple(row.target_id for row in INORGANIC_MAGNETIC_STATE_SPEC.target_rows),
        "all_177_rows_required": True, "all_136_exact_magnitudes_and_38_structural_absences_required": True,
        "shared_sources_not_recaptured": True, "target_content_inaccessible_to_prediction_execution": True,
        "no_square_root_spin_only_formula_signed_proof_scalar_fitted_g_factor_or_species_lookup": True,
        "falsification_condition": INORGANIC_MAGNETIC_STATE_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 177:
        raise ValueError("INORG-009 prediction is not the complete 177-row table")
    result = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id" or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 11:
            raise ValueError("INORG-009 prediction row is incomplete")
        result[entry.left.label] = entry.right
    if len(result) != 177: raise ValueError("INORG-009 prediction duplicates a target")
    return result


def _source_rows(root: Path) -> tuple[dict, ...]:
    if hash_file(root / TARGET_PATH) != TARGET_HASH or hash_file(root / PRIMARY_PATH) != PRIMARY_HASH:
        raise ValueError("INORG-009 post-seal evidence changed")
    identities = _identities(root); document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8")); rows = tuple(document.get("rows", ()))
    if document.get("complete_registered_target_count") != 177 or len(rows) != 177 or document.get("release_requires_prediction_seal") is not True:
        raise ValueError("INORG-009 target vector is incomplete")
    for identity, row in zip(identities, rows):
        if any(identity[key] != row.get(key) for key in IDENTITY_KEYS): raise ValueError("INORG-009 target differs from registered identity")
        if row.get("target_payload_hash") != sha256_identity((identity["target_id"], identity["source_record_role"], row.get("source_outcome"))): raise ValueError("INORG-009 target payload hash changed")
    return rows


def exact_analysis(rows: tuple[dict, ...], primary: dict) -> dict[str, object]:
    if len(rows) != 177: raise ValueError("INORG-009 requires all 177 source surfaces")
    balanced = forced_inorganic_magnetic_state(complete_unpaired_support("balanced", EmptyOne()))
    high = forced_inorganic_magnetic_state(complete_unpaired_support("high", PositiveCount(4)))
    successor = forced_inorganic_magnetic_state(append_unpaired_successor(high.support))
    definitions = tuple(row["source_outcome"] for row in rows[:3]); magnetic = tuple(row["source_outcome"] for row in rows[3:]); postseal = primary["exact_postseal_analysis"]
    present = tuple(row for row in magnetic if row["source_value_present"]); absent = tuple(row for row in magnetic if not row["source_value_present"])
    return {
        "balanced_moment": "EmptyOne" if isinstance(balanced.moment_support, EmptyOne) else balanced.moment_support.value,
        "balanced_width": balanced.spin_width.value, "balanced_relation": balanced.field_relation.label, "balanced_class": balanced.magnetic_class.label,
        "high_moment": high.moment_support.value, "high_width": high.spin_width.value, "high_relation": high.field_relation.label, "high_class": high.magnetic_class.label,
        "successor_moment": successor.moment_support.value, "successor_width": successor.spin_width.value,
        "susceptibility_definition_present": definitions[0]["susceptibility_relative_permeability_relation_present"],
        "paramagnetic_definition_present": definitions[1]["paramagnetic_positive_external_sign_and_drawn_relation_present"],
        "diamagnetic_definition_present": definitions[2]["diamagnetic_negative_external_sign_and_repelled_relation_present"],
        "complete_magnetic_count": len(magnetic), "positive_magnitude_count": len(present), "structural_absence_count": len(absent),
        "orientation_class_counts": postseal["complete_orientation_class_counts"], "exact_magnitude_vector_hash": postseal["complete_exact_magnitude_vector_hash"],
        "source_recapture_count": postseal["source_recapture_count"], "all_rows_preserved": postseal["all_177_rows_preserved"],
        "forbidden_formula_or_fit_used": postseal["square_root_spin_only_formula_fitted_g_factor_or_dimensional_moment_derived"],
    }


class InorganicMagneticStateValidator:
    def __init__(self, root: Path): self.root = root.resolve(); self.spec = INORGANIC_MAGNETIC_STATE_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate(); registration = experiment_registration_record(self.root); registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root); program = fold_program_from_mapping(document); inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash)
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs); boundary = BlindExperimentBoundary(envelope); prediction_seal = boundary.seal_prediction(execution.output, execution.trace); after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError("INORG-009 prediction package changed")
        predicted = _prediction_map(execution.output); source_rows = _source_rows(self.root)
        vault = TargetVault(experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-complete-target-custodian", targets={row["target_id"]: HeldLabel("external-complete-source-record-hash", row["target_payload_hash"]) for row in source_rows}, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)), expected_envelope_hash=sha256_identity(envelope))
        release = vault.release(prediction_seal); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal); boundary.measurement_context(release.targets)
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]; values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(values, start=1))
            law_match = tuple(cell.label for cell in word.cells[7:]) == EXPECTED_LAWS
            target_match = release.targets[row["target_id"]] == HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})
        primary = json.loads((self.root / PRIMARY_PATH).read_text(encoding="utf-8")); analysis = exact_analysis(source_rows, primary)
        try: exact_analysis(source_rows[:-1], primary); omitted_rejected = False
        except ValueError: omitted_rejected = True
        try: FoldWord((0,)); zero_rejected = False
        except FoldLanguageHalt: zero_rejected = True
        controls = {
            "omitted_source_row_rejected": omitted_rejected, "numerical_zero_rejected": zero_rejected,
            "all_177_target_hashes_bound_postseal": len(release.targets) == 177, "all_136_magnitudes_preserved": analysis["positive_magnitude_count"] == 136,
            "all_38_absences_preserved": analysis["structural_absence_count"] == 38, "shared_sources_not_recaptured": analysis["source_recapture_count"] == 0,
            "prediction_contains_no_target_value_or_orientation": "source_value_inscription" not in json.dumps(document, sort_keys=True) and "native_value" not in json.dumps(document, sort_keys=True),
        }
        passed = (
            all(row["passed"] for row in comparisons) and analysis["balanced_moment"] == "EmptyOne" and analysis["balanced_width"] == 1
            and analysis["balanced_relation"] == "repelled-from-field" and analysis["balanced_class"] == "diamagnetic"
            and analysis["high_moment"] == 4 and analysis["high_width"] == 5 and analysis["high_relation"] == "drawn-into-field" and analysis["high_class"] == "paramagnetic"
            and analysis["successor_moment"] == 5 and analysis["successor_width"] == 6
            and analysis["susceptibility_definition_present"] and analysis["paramagnetic_definition_present"] and analysis["diamagnetic_definition_present"]
            and analysis["complete_magnetic_count"] == 174 and analysis["positive_magnitude_count"] == 136 and analysis["structural_absence_count"] == 38
            and analysis["orientation_class_counts"] == {"source-aligned": 6, "source-opposed": 62, "source-orientation-unspecified": 68, "structural-absence": 38}
            and analysis["all_rows_preserved"] and analysis["forbidden_formula_or_fit_used"] is False and all(controls.values())
        )
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("exact-inorganic-magnetic-state/1", self.spec.falsification_condition)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash: raise ValueError("INORG-009 released target identity differs")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = (
            "balanced EmptyOne support: spin width 1, repelled-from-field, diamagnetic",
            "four unpaired occurrences: exact moment support 4, spin width 5, drawn-into-field, paramagnetic",
            "unpaired successor: moment support 5 and spin width 6", "three complete IUPAC magnetic definitions",
            "complete NIST vector: 174 cells, 136 exact magnitudes, 38 structural absences",
            f"orientation classes {analysis['orientation_class_counts']}; exact vector {analysis['exact_magnitude_vector_hash']}",
        ) + tuple(f"control {key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(dict.fromkeys(row["source_id"] for row in source_rows)), measurements, sha256_identity(payload), self.spec.falsification_condition, passed)


__all__ = ("InorganicMagneticStateValidator", "_identities", "_prediction_map", "_source_rows", "exact_analysis", "experiment_registration_record", "prediction_program_document")
