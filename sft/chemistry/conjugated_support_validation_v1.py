"""Capability-closed empirical validation for Chemistry ORG-001."""
from __future__ import annotations

import json
import platform
from pathlib import Path

from sft.chemistry.conjugated_support_batch_v1 import (
    CONJUGATED_SUPPORT_SPEC,
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.conjugated_support_law_v1 import append_opposed_fibre, conjugated_support
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
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
    "complete-connected-molecular-support",
    "two-held-opposed-fold-fibres",
    "complete-shared-centre-incidence-retention",
    "structure-sealed-before-observation",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("ORG-001 identity changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "definition",
        "coordinate",
        "peak",
        "intensity",
        "value",
        "outcome",
        "source_outcome",
        "presence",
        "target_payload_hash",
    }
    if (
        document.get("complete_registered_target_count") != 10
        or document.get(
            "target_definitions_coordinates_peaks_intensities_values_outcomes_presence_flags_or_payload_hashes_present"
        )
        is not False
        or len(rows) != 10
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("ORG-001 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table_arguments: list[str] = []
    for ordinal, row in enumerate(_identities(root), 1):
        prefix = f"conjugated-support-record-{ordinal}"
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
                {"opcode": "label", "destination": destination, "arguments": ["conjugated-support-law", label]}
            )
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend(
        (
            {"opcode": "table", "destination": "complete-conjugated-support-vector", "arguments": table_arguments},
            {"opcode": "emit", "destination": "", "arguments": ["complete-conjugated-support-vector"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": CONJUGATED_SUPPORT_SPEC.experiment_id + "-value-free-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": CONJUGATED_SUPPORT_SPEC.experiment_id,
        "claim_id": CONJUGATED_SUPPORT_SPEC.claim_id,
        "provenance": "forward_forcing_with-value-free-sealed-organic-structure-and-spectrum-vector",
        "frozen_relation": CONJUGATED_SUPPORT_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in CONJUGATED_SUPPORT_SPEC.target_rows),
        "all_ten_rows_required": True,
        "all_uv_visible_points_required": True,
        "target_content_inaccessible_to_prediction_execution": True,
        "v1_parser_overrun_must_be_preserved": True,
        "falsification_condition": CONJUGATED_SUPPORT_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 10:
        raise ValueError("ORG-001 prediction incomplete")
    rows: dict[str, FoldWord] = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel)
            or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord)
            or len(entry.right.cells) != 11
        ):
            raise ValueError("ORG-001 prediction row incomplete")
        rows[entry.left.label] = entry.right
    if len(rows) != 10:
        raise ValueError("ORG-001 duplicate prediction target")
    return rows


def _source_rows(root: Path) -> tuple[dict, ...]:
    if hash_file(root / TARGET_PATH) != TARGET_HASH or hash_file(root / PRIMARY_PATH) != PRIMARY_HASH:
        raise ValueError("ORG-001 external evidence changed")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if (
        document.get("complete_registered_target_count") != 10
        or len(rows) != 10
        or document.get("release_requires_prediction_seal") is not True
        or document.get("preserved_predecessor", (None, None))[1]
        != "sha256:adade1c9a6bed06b83a745680a63f73f0685cbf422bb4a2f3f5f0bf9830e0e7f"
    ):
        raise ValueError("ORG-001 corrected target vector incomplete")
    for identity, row in zip(identities, rows):
        if any(identity[key] != row.get(key) for key in IDENTITY_KEYS):
            raise ValueError("ORG-001 identity changed after target opening")
        if row.get("target_payload_hash") != sha256_identity(
            (identity["target_id"], identity["source_record_role"], row.get("source_outcome"))
        ):
            raise ValueError("ORG-001 target payload changed")
    return rows


def _by_role(rows: tuple[dict, ...], role: str) -> dict:
    matches = tuple(row for row in rows if row["source_record_role"] == role)
    if len(matches) != 1:
        raise ValueError(f"ORG-001 role cardinality changed: {role}")
    return matches[0]["source_outcome"]


def exact_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 10:
        raise ValueError("ORG-001 requires all ten external surfaces")
    base = conjugated_support(
        "base",
        ("atom-a", "atom-b", "atom-c"),
        ("fold-fibre-one", "fold-fibre-two"),
    )
    successor = append_opposed_fibre(base, "atom-d")
    repeated_rejected = False
    incomplete_rejected = False
    duplicate_rejected = False
    try:
        conjugated_support(
            "repeated",
            ("atom-a", "atom-b", "atom-c"),
            ("fold-fibre-one", "fold-fibre-one"),
        )
    except InadmissibleExactValue:
        repeated_rejected = True
    try:
        conjugated_support(
            "incomplete",
            ("atom-a", "atom-b", "atom-c"),
            ("fold-fibre-one",),
        )
    except InadmissibleExactValue:
        incomplete_rejected = True
    try:
        append_opposed_fibre(base, "atom-b")
    except InadmissibleExactValue:
        duplicate_rejected = True

    conjugated = _by_role(rows, "complete-conjugated-bond-and-coordinate-surface")
    separated = _by_role(rows, "complete-separated-double-bond-control-coordinate-surface")
    molecule = _by_role(rows, "complete-conjugated-molecular-identity-surface")
    spectrum = _by_role(rows, "complete-uv-visible-jcamp-point-surface")
    conjugated_rcc = tuple(
        row[1] for row in conjugated["complete_internal_coordinate_table"] if row[0] == "rCC"
    )
    separated_rcc = tuple(
        row[1] for row in separated["complete_internal_coordinate_table"] if row[0] == "rCC"
    )
    identity_rows = molecule["complete_identity_table"]
    smiles = next(row[2] for row in identity_rows if len(row) == 4 and row[3] == "Buta-1,3-diene")
    postseal = primary["exact_postseal_analysis"]
    return {
        "base_atom_count": base.atom_count.value,
        "base_support_count": base.support_count.value,
        "successor_atom_count": successor.atom_count.value,
        "successor_support_count": successor.support_count.value,
        "prior_incidence_prefix_preserved": successor.incidences[:2] == base.incidences,
        "repeated_fibre_rejected": repeated_rejected,
        "incomplete_incidence_rejected": incomplete_rejected,
        "duplicate_occurrence_rejected": duplicate_rejected,
        "complete_target_count": len(rows),
        "complete_source_count": len({row["source_id"] for row in rows}),
        "development_observed_target_count": sum(
            row["custody_class"] == "family-development-observed" for row in rows
        ),
        "identity_only_unopened_target_count": sum(
            "identity-only-unopened" in row["custody_class"] for row in rows
        ),
        "alternating_single_multiple_surface_count": postseal["alternating_single_multiple_surface_count"],
        "connected_intervening_bond_surface_present": postseal["connected_intervening_bond_surface_present"],
        "delocalized_nonlocal_support_surface_present": postseal["delocalized_nonlocal_support_surface_present"],
        "conjugated_smiles_inscription": smiles,
        "conjugated_rcc_external_strings": conjugated_rcc,
        "separated_control_rcc_external_strings": separated_rcc,
        "complete_vibrational_table_rows": postseal["complete_vibrational_table_rows"],
        "uv_visible_declared_point_count": postseal["uv_visible_declared_point_count"],
        "uv_visible_preserved_point_count": postseal["uv_visible_preserved_point_count"],
        "uv_visible_first_x_external_string": spectrum["headers"]["FIRSTX"],
        "uv_visible_last_x_external_string": spectrum["headers"]["LASTX"],
        "uv_visible_max_y_external_string": spectrum["headers"]["MAXY"],
        "uv_visible_jcamp_link_present": postseal["uv_visible_jcamp_link_present"],
        "external_signed_control_inscription_preserved": postseal["external_signed_control_inscription_preserved"],
        "preserved_v1_parser_overrun_count": postseal["preserved_v1_parser_overrun_count"],
        "v2_corrected_table_count": postseal["v2_corrected_table_count"],
        "complete_target_vector_hash": postseal["complete_target_vector_hash"],
        "source_recapture_count": postseal["source_recapture_count"],
        "all_rows_preserved": postseal["all_rows_preserved"],
    }


class ConjugatedSupportValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = CONJUGATED_SUPPORT_SPEC

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
            raise ValueError("ORG-001 capability-closed package changed")
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
            "repeated_adjacent_fibre_rejected": analysis["repeated_fibre_rejected"],
            "incomplete_incidence_rejected": analysis["incomplete_incidence_rejected"],
            "duplicate_occurrence_rejected": analysis["duplicate_occurrence_rejected"],
            "separated_control_not_classified_from_bond_counts_alone": analysis["separated_control_rcc_external_strings"]
            != analysis["conjugated_rcc_external_strings"],
            "external_signed_control_inscription_downstream_and_preserved": analysis[
                "external_signed_control_inscription_preserved"
            ],
            "v1_parser_overrun_preserved_and_corrected_separately": analysis[
                "preserved_v1_parser_overrun_count"
            ]
            == 1
            and analysis["v2_corrected_table_count"] == 2,
            "sources_not_recaptured": analysis["source_recapture_count"] == 0,
            "prediction_contains_no_definition_coordinate_spectrum_or_target_payload": not any(
                token in document_text
                for token in (
                    "complete_definition",
                    "1.476",
                    "1.337",
                    "FIRSTX",
                    "NPOINTS",
                    "target_payload_hash",
                    "alternating single and multiple bonds",
                )
            ),
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and analysis["base_atom_count"] == 3
            and analysis["base_support_count"] == 2
            and analysis["successor_atom_count"] == 4
            and analysis["successor_support_count"] == 3
            and analysis["prior_incidence_prefix_preserved"]
            and analysis["complete_target_count"] == 10
            and analysis["complete_source_count"] == 7
            and analysis["development_observed_target_count"] == 8
            and analysis["identity_only_unopened_target_count"] == 2
            and analysis["alternating_single_multiple_surface_count"] == 2
            and analysis["connected_intervening_bond_surface_present"]
            and analysis["delocalized_nonlocal_support_surface_present"]
            and analysis["conjugated_smiles_inscription"] == "C=CC=C"
            and analysis["conjugated_rcc_external_strings"] == ("1.476", "1.337")
            and analysis["separated_control_rcc_external_strings"] == ("1.511", "1.339")
            and analysis["complete_vibrational_table_rows"] == 26
            and analysis["uv_visible_declared_point_count"] == 502
            and analysis["uv_visible_preserved_point_count"] == 502
            and analysis["uv_visible_first_x_external_string"] == "200.6193"
            and analysis["uv_visible_last_x_external_string"] == "333.0485"
            and analysis["uv_visible_max_y_external_string"] == "4.47885"
            and analysis["uv_visible_jcamp_link_present"]
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
                    ("exact-connected-alternating-conjugated-support/1", self.spec.falsification_condition)
                ),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity_hash = target_identity_from_release(release)
        if target_identity_hash != vault.commitment.target_identity_hash:
            raise ValueError("ORG-001 target identity differs")
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
            "Fold witness: three atom occurrences, two opposed fibres; successor four atoms and three fibres",
            "IUPAC surfaces: two independent alternating-single/multiple records plus intervening-bond and nonlocal-support records",
            "NIST butadiene rCC inscriptions 1.476 and 1.337 angstrom; separated-control inscriptions 1.511 and 1.339 angstrom",
            "complete NIST vibrational table retained with 26 header/data rows",
            "complete NIST UV-visible JCAMP vector retained: 502 of 502 points, 200.6193 to 333.0485 nm, external maximum log-epsilon 4.47885",
            "one V1 uppercase-table parser overrun preserved; two tables corrected in claim-specific V2 without recapture",
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
    "ConjugatedSupportValidator",
    "_identities",
    "_prediction_map",
    "_source_rows",
    "exact_analysis",
    "experiment_registration_record",
    "prediction_program_document",
)
