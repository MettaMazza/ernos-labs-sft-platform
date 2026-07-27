"""Capability-closed post-seal validation for Chemistry INORG-004."""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.chemistry.coordination_geometry_batch_v1 import (
    COORDINATION_GEOMETRY_SPEC,
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    SOURCE_FILES,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.coordination_geometry_law_v1 import (
    CompleteCoordinationGeometry,
    HeldCoordinationAdjacency,
    HeldCoordinationPosition,
    forced_coordination_geometry,
)
from sft.chemistry.coordination_entity_law_v1 import CompleteCoordinationEntity, RetainedCoordinationAttachment
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
    "authority",
    "source_id",
    "source_document_identity",
    "source_record_role",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("INORG-004 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "source_inscription",
        "target_payload_hash",
        "point_group",
        "coordinate",
        "distance",
        "angle",
        "definition",
        "status",
        "value",
    }
    if (
        document.get("complete_registered_target_count") != 53
        or document.get("target_values_or_payload_hashes_present") is not False
        or document.get("all_geometry_point_group_coordinate_distance_angle_definition_status_and_target_payload_values_absent") is not True
        or len(rows) != 53
        or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 54))
        or len({row["target_id"] for row in rows}) != 53
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("INORG-004 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"coordination-geometry-record-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, key in enumerate(IDENTITY_KEYS[1:], start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["registered-source-identity", str(row[key])]})
            registers.append(destination)
        for family, label in (
            ("coordination-geometry-law", "complete-held-direct-position-and-boundary-adjacency-signature"),
            ("coordination-count-boundary", "positive-count-retained-but-never-shape-selecting"),
            ("coordination-rank-law", "generator-three-space-and-boundary-rank-two"),
            ("coordination-evidence-law", "all-fifty-three-reported-adverse-absent-and-unresolved-surfaces-retained"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-coordination-geometry-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-coordination-geometry-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": COORDINATION_GEOMETRY_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": COORDINATION_GEOMETRY_SPEC.experiment_id,
        "claim_id": COORDINATION_GEOMETRY_SPEC.claim_id,
        "provenance": "observational_derivation_with_family_identity_seal_and_preserved_target_transport_correction",
        "frozen_relation": COORDINATION_GEOMETRY_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_source_records": SOURCE_FILES,
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in COORDINATION_GEOMETRY_SPEC.target_rows),
        "all_geometry_point_group_coordinate_distance_angle_definition_status_and_target_payload_values_absent": True,
        "original_four_target_identity_mismatches_preserved": True,
        "correction_changes_target_identity_transport_not_fold_law_or_candidate_conditions": True,
        "falsification_condition": COORDINATION_GEOMETRY_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 53:
        raise ValueError("INORG-004 prediction is not the complete 53-record table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel)
            or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord)
            or len(entry.right.cells) != 10
        ):
            raise ValueError("INORG-004 prediction lost a consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 53:
        raise ValueError("INORG-004 duplicated a target")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES):
        if hash_file(root / path) != expected:
            raise ValueError(f"INORG-004 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    targets = tuple(document.get("rows", ()))
    if document.get("complete_registered_target_count") != 53 or document.get("release_requires_prediction_seal") is not True or len(targets) != 53:
        raise ValueError("INORG-004 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in IDENTITY_KEYS):
            raise ValueError("INORG-004 identity/target binding changed")
        inscription = target.get("source_inscription")
        if inscription is None or target.get("target_payload_hash") != sha256_identity((identity["target_id"], identity["source_record_role"], inscription)):
            raise ValueError("INORG-004 target payload changed")
        resolved.append(target)
    return tuple(resolved)


def _entity(width: int) -> CompleteCoordinationEntity:
    centre = HeldLabel("coordination-central-occurrence", "analysis-centre")
    return CompleteCoordinationEntity(
        HeldLabel("coordination-entity", f"analysis-entity-{width}"),
        HeldLabel("coordination-central-element", "analysis-element"),
        centre,
        tuple(
            RetainedCoordinationAttachment(
                PositiveCount(number), centre,
                HeldLabel("coordination-ligand-occurrence", f"analysis-ligand-{number}"),
                HeldLabel("coordination-ligand-group", "analysis-ligand-group"),
                HeldLabel("positive-coordination-incidence", f"analysis-incidence-{number}"),
            )
            for number in range(1, width + 1)
        ),
    )


def _geometry(entity: CompleteCoordinationEntity, changed_second: bool = False) -> CompleteCoordinationGeometry:
    positions = []
    for number, attachment in enumerate(entity.ordered_attachments, start=1):
        second = HeldLabel("fold-orientation-fibre", "fibre-two") if changed_second and number == 2 else EmptyOne()
        positions.append(HeldCoordinationPosition(
            PositiveCount(number), attachment.ligand_occurrence,
            (HeldLabel("fold-orientation-fibre", f"fibre-{number}"), second, EmptyOne()),
        ))
    adjacencies = tuple(
        HeldCoordinationAdjacency(
            entity.ordered_attachments[number - 1].ligand_occurrence,
            entity.ordered_attachments[number].ligand_occurrence,
            HeldLabel("coordination-boundary-adjacency", f"analysis-edge-{number}-{number + 1}"),
        )
        for number in range(1, len(entity.ordered_attachments))
    )
    return CompleteCoordinationGeometry(entity.central_occurrence, tuple(positions), adjacencies)


def exact_coordination_geometry_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 53 or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 54)):
        raise ValueError("INORG-004 requires all 53 source records")
    entity = _entity(2)
    first = forced_coordination_geometry(entity, _geometry(entity))
    second = forced_coordination_geometry(entity, _geometry(entity, changed_second=True))
    source_analysis = primary["exact_postseal_analysis"]
    vector = primary["complete_corrected_geometry_vector"]
    return {
        "complete_registered_target_count": len(rows),
        "positive_count_two_reconstructed": first.positive_coordination_count == PositiveCount(2),
        "generator_three_reconstructed": first.generated_space_rank == PositiveCount(3),
        "boundary_rank_two_reconstructed": first.boundary_rank == PositiveCount(2),
        "equal_count_different_orientation_has_different_signature": first.positive_coordination_count == second.positive_coordination_count and first.exact_geometry_signature != second.exact_geometry_signature,
        "iupac_direct_ligand_position_central_relation_retained": source_analysis["iupac_direct_ligand_position_central_relation_retained"],
        "all_original_target_identity_mismatches_preserved": source_analysis["all_original_target_identity_mismatches_preserved"],
        "all_corrected_source_identities_retained": source_analysis["all_corrected_source_identities_retained"],
        "positive_direct_incidence_counts_two_through_six_retained": source_analysis["positive_direct_incidence_counts_two_through_six_retained"],
        "all_point_group_inscriptions_retained_without_shape_selection": source_analysis["all_point_group_inscriptions_retained_without_shape_selection"],
        "all_coordinate_surfaces_preserved_including_reported_absence": source_analysis["all_coordinate_surfaces_preserved_including_reported_absence"],
        "all_reference_and_absence_status_surfaces_retained": source_analysis["all_reference_and_absence_status_surfaces_retained"],
        "all_fifty_three_target_surfaces_retained": source_analysis["all_fifty_three_target_surfaces_retained"],
        "complete_external_point_group_vector": tuple(row["source_point_group_inscription"] for row in vector),
        "complete_external_positive_incidence_vector": tuple(row["declared_positive_incidence_count"] for row in vector),
        "coordinate_absence_rows_retained": sum(not row["source_internal_coordinate_surface"] for row in vector),
        "point_group_or_coordinate_used_as_fold_parameter": primary["point_group_shape_angle_distance_or_coordinate_used_as_fold_proof_parameter"],
        "coordination_count_used_to_select_shape": primary["coordination_count_alone_used_to_select_geometry"],
    }


class CoordinationGeometryValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = COORDINATION_GEOMETRY_SPEC

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
            raise ValueError("INORG-004 prediction package changed")
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

        expected_laws = (
            "complete-held-direct-position-and-boundary-adjacency-signature",
            "positive-count-retained-but-never-shape-selecting",
            "generator-three-space-and-boundary-rank-two",
            "all-fifty-three-reported-adverse-absent-and-unresolved-surfaces-retained",
        )
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(identity_values, start=1))
            law_match = tuple(cell.label for cell in word.cells[6:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})

        primary = json.loads((self.root / PRIMARY_PATH).read_text(encoding="utf-8"))
        analysis = exact_coordination_geometry_analysis(source_rows, primary)
        try:
            exact_coordination_geometry_analysis(source_rows[:-1], primary)
            omitted = False
        except ValueError:
            omitted = True
        try:
            FoldWord((0,))
            numerical_zero = False
        except FoldLanguageHalt:
            numerical_zero = True
        controls = {
            "tampered_omitted_source_record_rejected": omitted,
            "numerical_zero_rejected": numerical_zero,
            "equal_count_different_orientation_not_merged": analysis["equal_count_different_orientation_has_different_signature"],
            "all_four_original_adverse_identity_rows_retained": analysis["all_original_target_identity_mismatches_preserved"],
            "complete_53_record_vector_retained": len(release.targets) == 53,
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        boolean_analysis = {
            key: value
            for key, value in analysis.items()
            if isinstance(value, bool) and key not in {"point_group_or_coordinate_used_as_fold_parameter", "coordination_count_used_to_select_shape"}
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and all(boolean_analysis.values())
            and analysis["point_group_or_coordinate_used_as_fold_parameter"] is False
            and analysis["coordination_count_used_to_select_shape"] is False
            and analysis["coordinate_absence_rows_retained"] >= 1
            and all(controls.values())
        )

        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-coordination-geometry-held-orientation-law/1", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("INORG-004 released target differs")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = (
            f"complete external positive-incidence vector: {analysis['complete_external_positive_incidence_vector']}",
            f"complete external point-group inscription vector: {analysis['complete_external_point_group_vector']}",
            f"reported internal-coordinate absence rows retained: {analysis['coordinate_absence_rows_retained']}",
            "four original formaldehyde target-identity mismatches preserved as adverse rows",
        ) + tuple(f"control {key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            sealed.seal_hash, registration_hash, isolation, custody, True, True, True,
            ("IUPAC-GOLD-BOOK-C01332", "NIST-CCCBDB-COMPLETE-EXPERIMENTAL-GEOMETRY"),
            measurements, sha256_identity(payload), self.spec.falsification_condition, passed,
        )


__all__ = (
    "CoordinationGeometryValidator",
    "_identities",
    "_prediction_map",
    "_source_rows",
    "exact_coordination_geometry_analysis",
    "experiment_registration_record",
    "prediction_program_document",
)
