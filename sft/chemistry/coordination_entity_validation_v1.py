"""Capability-closed post-seal structural validation for Chemistry INORG-001."""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.chemistry.coordination_entity_batch_v1 import (
    COORDINATION_ENTITY_SPEC, IDENTITY_HASH, IDENTITY_PATH, INVENTORY_HASH, INVENTORY_PATH,
    PRIMARY_HASH, PRIMARY_PATH, SOURCE_FILES, SPEC_HASH, SPEC_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.coordination_entity_law_v1 import (
    CompleteCoordinationEntity, RetainedCoordinationAttachment,
    append_ligand_preserves_coordination_identity, forced_coordination_entity_identity_law,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldTable, FoldWord,
    HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree,
    target_identity_from_release,
)
from sft.claim_evidence.fold_language import FoldLanguageHalt
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


IDENTITY_KEYS = (
    "target_id", "source_record_ordinal", "authority", "source_document_identity", "source_record_role",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("INORG-001 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {"source_inscription", "target_payload_hash", "value", "formula", "point_group", "link_count", "coordinate", "reference", "status"}
    if (
        document.get("complete_registered_target_count") != 20
        or document.get("target_values_or_hashes_present") is not False
        or document.get("all_definition_formula_point_group_link_count_coordinate_reference_and_limitation_values_absent") is not True
        or len(rows) != 20
        or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 21))
        or len({row["target_id"] for row in rows}) != 20
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("INORG-001 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"coordination-entity-record-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, key in enumerate(IDENTITY_KEYS[1:], start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": ["registered-source-identity", str(row[key])]})
            registers.append(destination)
        for family, label in (
            ("coordination-carrier-law", "one-central-occurrence-and-every-ligand-occurrence-retained"),
            ("coordination-incidence-law", "each-central-ligand-attachment-is-one-positive-incidence-trace"),
            ("coordination-custody-law", "all-20-definition-structure-value-reference-and-limitation-records-retained"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-coordination-structure-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-coordination-structure-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": COORDINATION_ENTITY_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": COORDINATION_ENTITY_SPEC.experiment_id,
        "claim_id": COORDINATION_ENTITY_SPEC.claim_id,
        "provenance": "observational_derivation_with_prefetch_and_value_free_20_record_identity_seal",
        "frozen_relation": COORDINATION_ENTITY_SPEC.exact_result,
        "prefetch_specification": (SPEC_PATH, SPEC_HASH),
        "source_inventory": (INVENTORY_PATH, INVENTORY_HASH),
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_source_records": SOURCE_FILES,
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in COORDINATION_ENTITY_SPEC.target_rows),
        "all_definition_formula_point_group_link_count_coordinate_reference_limitation_value_and_target_hash_values_absent": True,
        "falsification_condition": COORDINATION_ENTITY_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 20:
        raise ValueError("INORG-001 prediction is not the complete 20-record table")
    resolved = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id" or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 8:
            raise ValueError("INORG-001 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 20:
        raise ValueError("INORG-001 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES):
        if hash_file(root / path) != expected:
            raise ValueError(f"INORG-001 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    targets = tuple(document.get("rows", ()))
    if document.get("complete_registered_target_count") != 20 or document.get("release_requires_prediction_seal") is not True or len(targets) != 20:
        raise ValueError("INORG-001 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in IDENTITY_KEYS):
            raise ValueError("INORG-001 identity/target binding changed")
        inscription = target.get("source_inscription")
        if not isinstance(inscription, str) or not inscription:
            raise ValueError("INORG-001 target inscription absent")
        if target.get("target_payload_hash") != sha256_identity((identity["target_id"], identity["source_record_role"], inscription)):
            raise ValueError("INORG-001 target payload hash changed")
        resolved.append(target)
    return tuple(resolved)


def _entity(central_label: str = "Fe-one") -> CompleteCoordinationEntity:
    central = HeldLabel("coordination-central-occurrence", central_label)
    attachments = tuple(
        RetainedCoordinationAttachment(
            PositiveCount(number), central,
            HeldLabel("coordination-ligand-occurrence", f"CO-{number}"),
            HeldLabel("coordination-ligand-group", "CO"),
            HeldLabel("positive-coordination-incidence", f"Fe-C-{number}"),
        )
        for number in range(1, 6)
    )
    return CompleteCoordinationEntity(
        HeldLabel("coordination-entity", "FeCO5"), HeldLabel("coordination-central-element", "Fe"), central, attachments,
    )


def exact_coordination_entity_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 20 or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 21)):
        raise ValueError("INORG-001 requires the complete source-ordered 20-record vector")
    counts = {authority: sum(row["authority"] == authority for row in rows) for authority in ("IUPAC", "NIST-CCCBDB")}
    result = forced_coordination_entity_identity_law(_entity())
    successor_central = _entity().central_occurrence
    successor = RetainedCoordinationAttachment(
        PositiveCount(6), successor_central, HeldLabel("coordination-ligand-occurrence", "CO-6"),
        HeldLabel("coordination-ligand-group", "CO"), HeldLabel("positive-coordination-incidence", "Fe-C-6"),
    )
    inscriptions = {row["source_record_role"]: row["source_inscription"] for row in rows}
    adverse = primary["adverse_and_limitation_surface"]
    return {
        "complete_registered_target_count": len(rows),
        "source_class_census": counts,
        "source_class_census_matches": counts == {"IUPAC": 3, "NIST-CCCBDB": 17},
        "single_retained_central_occurrence_reconstructed": result.central_occurrence == HeldLabel("coordination-central-occurrence", "Fe-one"),
        "five_distinct_ligand_occurrences_and_incidences_reconstructed": len(set(result.ordered_ligand_occurrences)) == 5 and len(set(result.ordered_attachment_traces)) == 5,
        "successor_preserves_complete_prior_identity": append_ligand_preserves_coordination_identity(_entity(), successor),
        "iupac_central_ligand_structure_retained": "central atom" in inscriptions["coordination-entity-current-term"] and "ligands" in inscriptions["coordination-entity-current-term"],
        "nist_iron_pentacarbonyl_structure_retained": inscriptions["FeCO5-C-Fe-link-count"] == "5" and inscriptions["FeCO5-entity-identity"].startswith("Fe(CO)5"),
        "nist_ferrocene_structure_retained": inscriptions["ferrocene-C-Fe-link-count"] == "10" and inscriptions["ferrocene-entity-identity"].startswith("Fe(C5H5)2"),
        "all_reported_absences_and_disclaimers_retained": all(adverse.values()),
        "source_values_remain_postseal_evidence_only": primary["no_source_value_used_as_fold_proof_parameter"] is True,
    }


class CoordinationEntityValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = COORDINATION_ENTITY_SPEC

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
            raise ValueError("INORG-001 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {row["target_id"]: HeldLabel("external-complete-source-record-hash", row["target_payload_hash"]) for row in source_rows}
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
            "one-central-occurrence-and-every-ligand-occurrence-retained",
            "each-central-ligand-attachment-is-one-positive-incidence-trace",
            "all-20-definition-structure-value-reference-and-limitation-records-retained",
        )
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value for index, value in enumerate(identity_values, start=1))
            law_match = tuple(cell.label for cell in word.cells[5:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel("external-complete-source-record-hash", row["target_payload_hash"])
            comparisons.append({"target_id": row["target_id"], "identity_match": identity_match, "law_match": law_match, "postseal_target_hash_match": target_match, "passed": identity_match and law_match and target_match})
        primary = json.loads((self.root / PRIMARY_PATH).read_text(encoding="utf-8"))
        analysis = exact_coordination_entity_analysis(source_rows, primary)
        try:
            exact_coordination_entity_analysis(source_rows[:-1], primary)
            omitted_record_rejected = False
        except ValueError:
            omitted_record_rejected = True
        try:
            central = HeldLabel("coordination-central-occurrence", "Fe-one")
            CompleteCoordinationEntity(
                HeldLabel("coordination-entity", "control"), HeldLabel("coordination-central-element", "Fe"), central,
                (RetainedCoordinationAttachment(PositiveCount(1), HeldLabel("coordination-central-occurrence", "other"), HeldLabel("coordination-ligand-occurrence", "L-one"), HeldLabel("coordination-ligand-group", "L"), HeldLabel("positive-coordination-incidence", "edge-one")),),
            )
            central_mismatch_rejected = False
        except InadmissibleExactValue:
            central_mismatch_rejected = True
        try:
            FoldWord((0,))
            numerical_zero_rejected = False
        except FoldLanguageHalt:
            numerical_zero_rejected = True
        controls = {
            "tampered_omitted_source_record_rejected": omitted_record_rejected,
            "tampered_central_occurrence_mismatch_rejected": central_mismatch_rejected,
            "numerical_zero_rejected": numerical_zero_rejected,
            "complete_20_record_vector_retained": len(release.targets) == 20,
            "reported_absence_and_disclaimer_surface_visible": analysis["all_reported_absences_and_disclaimers_retained"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {"complete_registered_target_count", "source_class_census"}
        passed = all(row["passed"] for row in comparisons) and all(bool(value) for key, value in analysis.items() if key not in non_boolean) and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-coordination-identity-law/1", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("INORG-001 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = tuple(f"{row['target_id']}: {row['source_record_role']}={row['source_inscription']}; target={row['target_payload_hash']}" for row in source_rows) + tuple(f"control {key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            sealed.seal_hash, registration_hash, isolation, custody, True, True, True,
            ("IUPAC-GOLD-BOOK-C01330-C00930-L03518", "NIST-CCCBDB-SRD101-FECO5-FERROCENE"),
            measurements, sha256_identity(measurement_payload), self.spec.falsification_condition, passed,
        )


__all__ = (
    "CoordinationEntityValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_coordination_entity_analysis", "experiment_registration_record", "prediction_program_document",
)
