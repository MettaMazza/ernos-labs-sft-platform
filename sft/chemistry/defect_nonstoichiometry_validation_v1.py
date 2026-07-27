"""Capability-closed empirical validation for INORG-016."""
from __future__ import annotations

import json
import platform
from pathlib import Path

from sft.chemistry.defect_nonstoichiometry_batch_v1 import (
    DEFECT_NONSTOICHIOMETRY_SPEC,
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    TARGET_HASH,
    TARGET_PATH,
    V1_PRIMARY_HASH,
    V1_PRIMARY_PATH,
    V1_TARGET_HASH,
    V1_TARGET_PATH,
)
from sft.chemistry.defect_nonstoichiometry_law_v1 import EMPTY_ONE, defect_state
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    EmptyOne,
    FoldLanguageHalt,
    FoldTable,
    FoldWord,
    HostilePackageAuditor,
    TargetVault,
    fold_program_from_mapping,
    snapshot_protected_tree,
    target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, PositiveCount
from sft.engine.source import hash_file


IDENTITY_KEYS = (
    "target_id",
    "source_record_ordinal",
    "source_id",
    "authority",
    "registered_identity",
    "source_record_role",
    "custody_class",
)
EXPECTED_LAWS = (
    "complete-reference-and-observed-local-support",
    "vacancy-is-retained-site-with-EmptyOne",
    "separate-positive-missing-and-added-supports",
    "exact-formula-defect-and-origin-classification",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("INORG-016 identity changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "definition",
        "value",
        "outcome",
        "source_outcome",
        "registered_surface_phrase",
        "target_payload_hash",
    }
    if (
        document.get("complete_registered_target_count") != 15
        or document.get(
            "target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present"
        )
        is not False
        or len(rows) != 15
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("INORG-016 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table_arguments: list[str] = []
    for ordinal, row in enumerate(_identities(root), 1):
        prefix = f"defect-record-{ordinal}"
        instructions.append(
            {"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]}
        )
        registers = ["premise"]
        for identity_ordinal, key in enumerate(IDENTITY_KEYS[1:], 1):
            destination = f"{prefix}-identity-{identity_ordinal}"
            instructions.append(
                {
                    "opcode": "label",
                    "destination": destination,
                    "arguments": ["registered-source-identity", str(row[key])],
                }
            )
            registers.append(destination)
        for label in EXPECTED_LAWS:
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append(
                {"opcode": "label", "destination": destination, "arguments": ["defect-law", label]}
            )
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend(
        (
            {"opcode": "table", "destination": "complete-defect-vector", "arguments": table_arguments},
            {"opcode": "emit", "destination": "", "arguments": ["complete-defect-vector"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": DEFECT_NONSTOICHIOMETRY_SPEC.experiment_id + "-value-free-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": DEFECT_NONSTOICHIOMETRY_SPEC.experiment_id,
        "claim_id": DEFECT_NONSTOICHIOMETRY_SPEC.claim_id,
        "provenance": "forward_forcing_with-family-identity-sealed-defect-vector",
        "frozen_relation": DEFECT_NONSTOICHIOMETRY_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "preserved_v1_target": (V1_TARGET_PATH, V1_TARGET_HASH),
        "preserved_v1_primary": (V1_PRIMARY_PATH, V1_PRIMARY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in DEFECT_NONSTOICHIOMETRY_SPEC.target_rows),
        "all_fifteen_rows_required": True,
        "target_content_inaccessible_to_prediction_execution": True,
        "v1_missing_note_surfaces_preserved_and_corrected_only_in_v2": True,
        "falsification_condition": DEFECT_NONSTOICHIOMETRY_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 15:
        raise ValueError("INORG-016 prediction incomplete")
    rows: dict[str, FoldWord] = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel)
            or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord)
            or len(entry.right.cells) != 11
        ):
            raise ValueError("INORG-016 prediction row incomplete")
        rows[entry.left.label] = entry.right
    if len(rows) != 15:
        raise ValueError("INORG-016 duplicate prediction target")
    return rows


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in (
        (V1_TARGET_PATH, V1_TARGET_HASH),
        (V1_PRIMARY_PATH, V1_PRIMARY_HASH),
        (TARGET_PATH, TARGET_HASH),
        (PRIMARY_PATH, PRIMARY_HASH),
    ):
        if hash_file(root / path) != expected:
            raise ValueError(f"INORG-016 evidence changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if (
        document.get("complete_registered_target_count") != 15
        or len(rows) != 15
        or document.get("release_requires_prediction_seal") is not True
        or tuple(document.get("corrected_registered_roles", ()))
        != (
            "surface-and-near-surface-bulk-role",
            "vacancy-interstitial-edge-corner-kink-examples",
        )
    ):
        raise ValueError("INORG-016 V2 target vector incomplete")
    for identity, row in zip(identities, rows):
        if any(identity[key] != row.get(key) for key in IDENTITY_KEYS):
            raise ValueError("INORG-016 identity changed after target opening")
        if row.get("target_payload_hash") != sha256_identity(
            (identity["target_id"], identity["source_record_role"], row.get("source_outcome"))
        ):
            raise ValueError("INORG-016 target payload changed")
    return rows


def _formula_vector(state) -> tuple[int, ...]:
    return tuple(entry.count.value for entry in state.observed_formula)


def exact_analysis(rows: tuple[dict, ...], primary: dict, v1_target: dict) -> dict:
    if len(rows) != 15:
        raise ValueError("INORG-016 requires all fifteen external surfaces")
    reference = ("A", "A", "B", "B")
    pristine = defect_state("pristine", reference, reference)
    vacancy = defect_state("vacancy", reference, ("A", EMPTY_ONE, "B", "B"))
    interstitial = defect_state("interstitial", reference, reference, ("A",))
    substitution = defect_state("substitution", reference, ("A", "C", "B", "B"))
    vacancy_a = next(row for row in vacancy.reconciliation if row.species.label == "A")
    interstitial_a = next(row for row in interstitial.reconciliation if row.species.label == "A")
    substitution_a = next(row for row in substitution.reconciliation if row.species.label == "A")
    substitution_c = next(row for row in substitution.reconciliation if row.species.label == "C")
    postseal = primary["exact_postseal_analysis"]
    return {
        "pristine_defect_absence": isinstance(pristine.defect_classes, EmptyOne),
        "reference_formula_vector": tuple(entry.count.value for entry in pristine.reference_formula),
        "vacancy_observed_formula_vector": _formula_vector(vacancy),
        "vacancy_missing_a_count": vacancy_a.missing_support.value,
        "vacancy_added_a_absence": isinstance(vacancy_a.added_support, EmptyOne),
        "vacancy_class_vector": tuple(label.label for label in vacancy.defect_classes),
        "vacancy_origin": vacancy.origin_class.label,
        "interstitial_observed_formula_vector": _formula_vector(interstitial),
        "interstitial_added_a_count": interstitial_a.added_support.value,
        "interstitial_origin": interstitial.origin_class.label,
        "substitution_observed_formula_vector": _formula_vector(substitution),
        "substitution_missing_a_count": substitution_a.missing_support.value,
        "substitution_added_c_count": substitution_c.added_support.value,
        "substitution_origin": substitution.origin_class.label,
        "complete_target_count": len(rows),
        "complete_source_count": len({row["source_id"] for row in rows}),
        "identity_only_unopened_target_count": sum(
            row["custody_class"] == "family-identity-only-unopened" for row in rows
        ),
        "all_registered_surfaces_present": all(
            row["source_outcome"]["registered_surface_present"] for row in rows
        ),
        "definition_note_surface_count": postseal["definition_note_surface_count"],
        "scope_mismatch_or_distinction_count": postseal["scope_mismatch_or_distinction_count"],
        "v1_missing_registered_surface_count": sum(
            not row["source_outcome"]["registered_surface_present"] for row in v1_target["rows"]
        ),
        "complete_target_vector_hash": postseal["complete_target_vector_hash"],
        "source_recapture_count": postseal["source_recapture_count"],
        "all_rows_preserved": postseal["all_rows_preserved"],
    }


class DefectNonstoichiometryValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = DEFECT_NONSTOICHIOMETRY_SPEC

    def validate(self, sealed):
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows),
            sealed.seal_hash,
            registration_hash,
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("INORG-016 capability-closed package changed")
        predictions = _prediction_map(execution.output)
        rows = _source_rows(self.root)
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets={
                row["target_id"]: HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
                for row in rows
            },
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        comparisons = []
        for row in rows:
            word = predictions[row["target_id"]]
            identity_values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, 1)
            )
            law_match = tuple(cell.label for cell in word.cells[7:]) == EXPECTED_LAWS
            target_match = release.targets[row["target_id"]] == HeldLabel(
                "external-complete-source-record-hash", row["target_payload_hash"]
            )
            comparisons.append(
                {
                    "target_id": row["target_id"],
                    "identity_match": identity_match,
                    "law_match": law_match,
                    "postseal_target_hash_match": target_match,
                    "passed": identity_match and law_match and target_match,
                }
            )
        primary = json.loads((self.root / PRIMARY_PATH).read_text(encoding="utf-8"))
        v1_target = json.loads((self.root / V1_TARGET_PATH).read_text(encoding="utf-8"))
        analysis = exact_analysis(rows, primary, v1_target)
        try:
            exact_analysis(rows[:-1], primary, v1_target)
            omission_rejected = False
        except ValueError:
            omission_rejected = True
        try:
            FoldWord((0,))
            numerical_zero_rejected = False
        except FoldLanguageHalt:
            numerical_zero_rejected = True
        document_text = json.dumps(document, sort_keys=True)
        controls = {
            "omitted_source_row_rejected": omission_rejected,
            "numerical_zero_rejected": numerical_zero_rejected,
            "all_fifteen_target_hashes_bound_postseal": len(release.targets) == 15,
            "v1_two_missing_note_surfaces_preserved": analysis["v1_missing_registered_surface_count"] == 2,
            "v2_two_note_surfaces_complete": analysis["definition_note_surface_count"] == 2,
            "two_scope_or_identity_distinctions_preserved": analysis["scope_mismatch_or_distinction_count"] == 2,
            "sources_not_recaptured": analysis["source_recapture_count"] == 0,
            "prediction_contains_no_definition_note_or_target_payload": not any(
                token in document_text
                for token in ("complete_definition_text", "complete_source_note_text", "target_payload_hash", "Surface vacancies")
            ),
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and analysis["pristine_defect_absence"]
            and analysis["reference_formula_vector"] == (1, 1)
            and analysis["vacancy_observed_formula_vector"] == (1, 2)
            and analysis["vacancy_missing_a_count"] == 1
            and analysis["vacancy_added_a_absence"]
            and analysis["vacancy_class_vector"] == ("vacancy",)
            and analysis["vacancy_origin"] == "intrinsic"
            and analysis["interstitial_observed_formula_vector"] == (3, 2)
            and analysis["interstitial_added_a_count"] == 1
            and analysis["interstitial_origin"] == "intrinsic"
            and analysis["substitution_observed_formula_vector"] == (1, 1, 2)
            and analysis["substitution_missing_a_count"] == 1
            and analysis["substitution_added_c_count"] == 1
            and analysis["substitution_origin"] == "extrinsic"
            and analysis["complete_target_count"] == 15
            and analysis["complete_source_count"] == 5
            and analysis["identity_only_unopened_target_count"] == 15
            and analysis["all_registered_surfaces_present"]
            and analysis["all_rows_preserved"]
            and all(controls.values())
        )
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=self.spec.experiment_id + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity(
                    ("exact-defect-nonstoichiometry/1", self.spec.falsification_condition)
                ),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity_hash = target_identity_from_release(release)
        if target_identity_hash != vault.commitment.target_identity_hash:
            raise ValueError("INORG-016 target identity differs")
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity_hash,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
        payload = {
            "registration": registration_hash,
            "sealed": sealed.seal_hash,
            "prediction": prediction_seal.seal_hash,
            "analysis": analysis,
            "comparisons": comparisons,
            "controls": controls,
            "trace": execution.trace_hash,
        }
        measurements = (
            "vacancy formula one-to-two with one positive missing A and structural EmptyOne occupancy",
            "native interstitial formula three-to-two; foreign substitution formula one-to-one-to-two",
            "complete fifteen-row five-source defect vector with two definition-note surfaces",
            "V1 two-surface adverse record preserved and V2 correction separately sealed",
            f"complete exact target vector {analysis['complete_target_vector_hash']}",
        ) + tuple(f"control {key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            sealed.seal_hash,
            registration_hash,
            isolation,
            custody,
            True,
            True,
            True,
            tuple(dict.fromkeys(row["source_id"] for row in rows)),
            measurements,
            sha256_identity(payload),
            self.spec.falsification_condition,
            passed,
        )


__all__ = (
    "DefectNonstoichiometryValidator",
    "_identities",
    "_prediction_map",
    "_source_rows",
    "exact_analysis",
    "experiment_registration_record",
    "prediction_program_document",
)
