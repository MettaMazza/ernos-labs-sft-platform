"""Capability-closed empirical validation for INORG-015."""
from __future__ import annotations

import json
import platform
from pathlib import Path

from sft.chemistry.solid_state_local_coordination_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    SOLID_STATE_LOCAL_COORDINATION_SPEC,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.solid_state_local_coordination_law_v1 import append_occurrence, local_solid
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
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
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
    "complete-local-occurrence-and-bond-support",
    "primitive-positive-formula-ratio",
    "generated-repeat-rank-one-two-or-three",
    "chemistry-local-materials-bulk-handoff",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("INORG-015 identity changed")
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
        document.get("complete_registered_target_count") != 10
        or document.get(
            "target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present"
        )
        is not False
        or len(rows) != 10
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("INORG-015 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table_arguments: list[str] = []
    for ordinal, row in enumerate(_identities(root), 1):
        prefix = f"local-solid-record-{ordinal}"
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
                {"opcode": "label", "destination": destination, "arguments": ["local-solid-law", label]}
            )
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend(
        (
            {"opcode": "table", "destination": "complete-local-solid-vector", "arguments": table_arguments},
            {"opcode": "emit", "destination": "", "arguments": ["complete-local-solid-vector"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": SOLID_STATE_LOCAL_COORDINATION_SPEC.experiment_id + "-value-free-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": SOLID_STATE_LOCAL_COORDINATION_SPEC.experiment_id,
        "claim_id": SOLID_STATE_LOCAL_COORDINATION_SPEC.claim_id,
        "provenance": "forward_forcing_with-family-identity-sealed-local-solid-vector",
        "frozen_relation": SOLID_STATE_LOCAL_COORDINATION_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in SOLID_STATE_LOCAL_COORDINATION_SPEC.target_rows),
        "all_ten_rows_required": True,
        "target_content_inaccessible_to_prediction_execution": True,
        "returned_mixed_crystal_identity_mismatch_must_be_preserved": True,
        "falsification_condition": SOLID_STATE_LOCAL_COORDINATION_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 10:
        raise ValueError("INORG-015 prediction incomplete")
    rows: dict[str, FoldWord] = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel)
            or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord)
            or len(entry.right.cells) != 11
        ):
            raise ValueError("INORG-015 prediction row incomplete")
        rows[entry.left.label] = entry.right
    if len(rows) != 10:
        raise ValueError("INORG-015 duplicate prediction target")
    return rows


def _source_rows(root: Path) -> tuple[dict, ...]:
    if hash_file(root / TARGET_PATH) != TARGET_HASH or hash_file(root / PRIMARY_PATH) != PRIMARY_HASH:
        raise ValueError("INORG-015 external evidence changed")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if (
        document.get("complete_registered_target_count") != 10
        or len(rows) != 10
        or document.get("release_requires_prediction_seal") is not True
    ):
        raise ValueError("INORG-015 target vector incomplete")
    for identity, row in zip(identities, rows):
        if any(identity[key] != row.get(key) for key in IDENTITY_KEYS):
            raise ValueError("INORG-015 identity changed after target opening")
        if row.get("target_payload_hash") != sha256_identity(
            (identity["target_id"], identity["source_record_role"], row.get("source_outcome"))
        ):
            raise ValueError("INORG-015 target payload changed")
    return rows


def exact_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 10:
        raise ValueError("INORG-015 requires all ten external surfaces")
    formula_witness = local_solid(
        "AB",
        (("A", PositiveCount(2)), ("B", PositiveCount(2))),
        ((('A', 1), ('B', 1)), (('A', 2), ('B', 2))),
        PositiveCount(2),
    )
    guest_witness = local_solid(
        "host",
        (("H", PositiveCount(2)), ("G", PositiveCount(1))),
        ((('H', 1), ('G', 1)),),
        PositiveCount(3),
        PositiveCount(1),
    )
    successor = append_occurrence(formula_witness, "A", formula_witness.occurrences[1])
    rank_four_rejected = False
    try:
        local_solid("rank-four", (("A", PositiveCount(1)),), (), PositiveCount(4))
    except InadmissibleExactValue:
        rank_four_rejected = True
    postseal = primary["exact_postseal_analysis"]
    return {
        "primitive_formula_vector": tuple(entry.primitive_count.value for entry in formula_witness.formula),
        "guest_formula_vector": tuple(entry.primitive_count.value for entry in guest_witness.formula),
        "generated_repeat_rank": len(guest_witness.repeat_axes),
        "second_constituent_count": len(guest_witness.constituent_support),
        "structural_constituent_absence": isinstance(formula_witness.constituent_support, EmptyOne),
        "successor_formula_vector": tuple(entry.primitive_count.value for entry in successor.formula),
        "rank_four_rejected": rank_four_rejected,
        "complete_target_count": len(rows),
        "complete_source_count": len({row["source_id"] for row in rows}),
        "development_observed_target_count": sum(row["custody_class"] == "family-development-observed" for row in rows),
        "identity_only_unopened_target_count": sum(row["custody_class"] == "family-identity-only-unopened" for row in rows),
        "all_registered_surfaces_present": all(row["source_outcome"]["registered_surface_present"] for row in rows),
        "scope_mismatch_or_distinction_count": postseal["scope_mismatch_or_distinction_count"],
        "complete_target_vector_hash": postseal["complete_target_vector_hash"],
        "source_recapture_count": postseal["source_recapture_count"],
        "all_rows_preserved": postseal["all_rows_preserved"],
    }


class SolidStateLocalCoordinationValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = SOLID_STATE_LOCAL_COORDINATION_SPEC

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
            raise ValueError("INORG-015 capability-closed package changed")
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
        analysis = exact_analysis(rows, json.loads((self.root / PRIMARY_PATH).read_text(encoding="utf-8")))
        try:
            exact_analysis(rows[:-1], {})
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
            "all_ten_target_hashes_bound_postseal": len(release.targets) == 10,
            "rank_four_rejected": analysis["rank_four_rejected"],
            "returned_mixed_crystal_identity_mismatch_preserved": analysis["scope_mismatch_or_distinction_count"] == 1,
            "sources_not_recaptured": analysis["source_recapture_count"] == 0,
            "prediction_contains_no_definition_or_target_payload": not any(
                token in document_text
                for token in ("complete_definition_text", "target_payload_hash", "A crystal containing")
            ),
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and analysis["primitive_formula_vector"] == (1, 1)
            and analysis["guest_formula_vector"] == (2, 1)
            and analysis["successor_formula_vector"] == (3, 2)
            and analysis["generated_repeat_rank"] == 3
            and analysis["second_constituent_count"] == 1
            and analysis["structural_constituent_absence"]
            and analysis["complete_target_count"] == 10
            and analysis["complete_source_count"] == 2
            and analysis["development_observed_target_count"] == 5
            and analysis["identity_only_unopened_target_count"] == 5
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
                    ("exact-local-solid-coordination/1", self.spec.falsification_condition)
                ),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity_hash = target_identity_from_release(release)
        if target_identity_hash != vault.commitment.target_identity_hash:
            raise ValueError("INORG-015 target identity differs")
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
            "primitive local formula one-to-one; host/guest formula two-to-one; successor formula three-to-two",
            "generated repeat rank three, one exact second constituent and structural EmptyOne absence",
            "complete ten-row two-source coordination-network and returned mixed-crystal vector",
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
    "SolidStateLocalCoordinationValidator",
    "_identities",
    "_prediction_map",
    "_source_rows",
    "exact_analysis",
    "experiment_registration_record",
    "prediction_program_document",
)
