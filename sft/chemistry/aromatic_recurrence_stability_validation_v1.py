"""Capability-closed empirical validation for Chemistry ORG-003."""
from __future__ import annotations

import json
import platform
from pathlib import Path

from sft.chemistry.aromatic_recurrence_stability_batch_v1 import (
    AROMATIC_RECURRENCE_STABILITY_SPEC,
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.aromatic_recurrence_stability_law_v1 import (
    ExactAromaticRecurrence,
    append_complete_pair_layer,
    aromatic_recurrence,
    aromatic_stability_order,
    complete_ordered_pair_cells,
)
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
from sft.physics.structural_constants import generator_period_three


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
    "complete-two-fibre-cycle-recurrence",
    "complete-four-ordered-pair-cell-layer",
    "positive-recurrence-opening-gap",
    "blind-complete-energy-vector-after-seal",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("ORG-003 identity changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "definition",
        "note",
        "table",
        "value",
        "sign",
        "uncertainty",
        "outcome",
        "source_outcome",
        "presence",
        "target_payload_hash",
    }
    if (
        document.get("complete_registered_target_count") != 9
        or document.get("development_observed_target_count") != 6
        or document.get("outcome_unopened_blind_target_count") != 3
        or document.get(
            "target_definitions_notes_tables_values_signs_uncertainties_outcomes_presence_flags_or_payload_hashes_present"
        )
        is not False
        or len(rows) != 9
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("ORG-003 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table_arguments: list[str] = []
    for ordinal, row in enumerate(_identities(root), 1):
        prefix = f"aromatic-recurrence-record-{ordinal}"
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
                {"opcode": "label", "destination": destination, "arguments": ["aromatic-recurrence-law", label]}
            )
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend(
        (
            {"opcode": "table", "destination": "complete-aromatic-energy-vector", "arguments": table_arguments},
            {"opcode": "emit", "destination": "", "arguments": ["complete-aromatic-energy-vector"]},
        )
    )
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": AROMATIC_RECURRENCE_STABILITY_SPEC.experiment_id + "-value-free-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    spec = AROMATIC_RECURRENCE_STABILITY_SPEC
    return {
        "experiment_id": spec.experiment_id,
        "claim_id": spec.claim_id,
        "provenance": "forward_forcing_with-six-development-observed-and-three-outcome-unopened-blind-complete-surfaces",
        "frozen_relation": spec.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in spec.target_rows),
        "all_nine_rows_required": True,
        "six_development_observed_rows_not_blind": True,
        "three_independent_rows_outcome_unopened_before_seal": True,
        "all_complete_scientific_table_rows_required": True,
        "target_content_inaccessible_to_prediction_execution": True,
        "falsification_condition": spec.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 9:
        raise ValueError("ORG-003 prediction incomplete")
    rows: dict[str, FoldWord] = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel)
            or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord)
            or len(entry.right.cells) != 11
        ):
            raise ValueError("ORG-003 prediction row incomplete")
        rows[entry.left.label] = entry.right
    if len(rows) != 9:
        raise ValueError("ORG-003 duplicate prediction target")
    return rows


def _source_rows(root: Path) -> tuple[dict, ...]:
    if hash_file(root / TARGET_PATH) != TARGET_HASH or hash_file(root / PRIMARY_PATH) != PRIMARY_HASH:
        raise ValueError("ORG-003 external evidence changed")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if (
        document.get("complete_registered_target_count") != 9
        or len(rows) != 9
        or document.get("release_requires_prediction_seal") is not True
        or document.get("all_favourable_adverse_absent_scope_and_unresolved_rows_preserved") is not True
    ):
        raise ValueError("ORG-003 complete target vector incomplete")
    for identity, row in zip(identities, rows):
        if any(identity[key] != row.get(key) for key in IDENTITY_KEYS):
            raise ValueError("ORG-003 identity changed after target opening")
        if row.get("target_payload_hash") != sha256_identity(
            (identity["target_id"], identity["source_record_role"], row.get("source_outcome"))
        ):
            raise ValueError("ORG-003 target payload changed")
        if hash_file(root / row["opened_snapshot_path"]) != row["opened_snapshot_sha256"]:
            raise ValueError("ORG-003 opened snapshot changed")
    return rows


def _by_role(rows: tuple[dict, ...], role: str) -> dict:
    matches = tuple(row for row in rows if row["source_record_role"] == role)
    if len(matches) != 1:
        raise ValueError(f"ORG-003 role cardinality changed: {role}")
    return matches[0]["source_outcome"]


def _property(surface: dict, label: str) -> tuple[str, str, str]:
    matches = []
    for table in surface["complete_experimental_data_tables"]:
        for row in table:
            if row and row[0] == label:
                matches.append(row)
    if len(matches) != 1 or len(matches[0]) < 4:
        raise ValueError(f"ORG-003 property cardinality changed: {label}")
    return matches[0][1], matches[0][2], matches[0][3]


def _directed_hundredths(value: str) -> tuple[str, int]:
    direction = "below-reference" if value.startswith("-") else "above-reference"
    magnitude = value[1:] if value.startswith("-") else value
    whole, part = magnitude.split(".")
    if len(part) != 2 or not whole.isdigit() or not part.isdigit():
        raise ValueError("ORG-003 external magnitude is not exact hundredths")
    result = int(whole) * 100 + int(part)
    if result < 1:
        raise ValueError("ORG-003 external magnitude is not positive")
    return direction, result


def _hundredths(value: int) -> str:
    if value < 1:
        raise ValueError("ORG-003 comparison magnitude must remain positive")
    return f"{value // 100}.{value % 100:02d}"


def exact_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 9:
        raise ValueError("ORG-003 requires all nine external surfaces")
    centres = tuple(f"centre-{position}" for position in range(1, generator_period_three() * 2 + 1))
    base = aromatic_recurrence("carrier", centres, PositiveCount(1))
    successor = append_complete_pair_layer(base)
    second_successor = append_complete_pair_layer(successor)
    stability = aromatic_stability_order(base)
    incomplete_rejected = duplicate_boundary_rejected = open_cycle_rejected = False
    try:
        ExactAromaticRecurrence(
            base.molecular_carrier,
            base.cycle,
            base.boundary_fibres,
            ((complete_ordered_pair_cells()[0], complete_ordered_pair_cells()[1], complete_ordered_pair_cells()[2]),),
        )
    except InadmissibleExactValue:
        incomplete_rejected = True
    try:
        ExactAromaticRecurrence(
            base.molecular_carrier,
            base.cycle,
            (base.boundary_fibres[0], base.boundary_fibres[0]),
            base.pair_cell_layers,
        )
    except InadmissibleExactValue:
        duplicate_boundary_rejected = True
    try:
        aromatic_recurrence("invalid", ("left", "right"), PositiveCount(1))
    except InadmissibleExactValue:
        open_cycle_rejected = True

    blind_roles = (
        "complete-cccbdb-benzene-experimental-data-surface",
        "complete-cccbdb-cyclohexene-experimental-data-surface",
        "complete-cccbdb-cyclohexane-experimental-data-surface",
    )
    blind_values = {role: _property(_by_role(rows, role), "Hfg(298.15K)") for role in blind_roles}
    benzene_direction, benzene = _directed_hundredths(blind_values[blind_roles[0]][0])
    cyclohexene_direction, cyclohexene = _directed_hundredths(blind_values[blind_roles[1]][0])
    cyclohexane_direction, cyclohexane = _directed_hundredths(blind_values[blind_roles[2]][0])
    if (benzene_direction, cyclohexene_direction, cyclohexane_direction) != (
        "above-reference",
        "below-reference",
        "below-reference",
    ):
        raise ValueError("ORG-003 directed external relation changed")
    single = cyclohexane - cyclohexene
    cyclic = cyclohexane + benzene
    localized = generator_period_three() * single
    excess = localized - cyclic
    uncertainties = {role: _directed_hundredths(blind_values[role][1])[1] for role in blind_roles}
    envelope = (
        generator_period_three() * (uncertainties[blind_roles[1]] + uncertainties[blind_roles[2]])
        + uncertainties[blind_roles[0]]
        + uncertainties[blind_roles[2]]
    )
    postseal = primary["exact_postseal_analysis"]
    return {
        "primitive_support_count": base.positive_support_count.value,
        "successor_support_count": successor.positive_support_count.value,
        "second_successor_support_count": second_successor.positive_support_count.value,
        "complete_first_return": base.first_return_trace[0] == base.first_return_trace[-1],
        "complete_pair_cell_perturbation_closure": base.complete_registered_perturbation_closure,
        "positive_recurrence_opening_gap": stability.closed_recurrence_precedes_opened_reference,
        "incomplete_pair_cell_layer_rejected": incomplete_rejected,
        "duplicated_boundary_fibre_rejected": duplicate_boundary_rejected,
        "open_two_centre_cycle_rejected": open_cycle_rejected,
        "complete_target_count": len(rows),
        "complete_source_count": len({row["source_id"] for row in rows}),
        "development_observed_target_count": sum(
            row["custody_class"] == "family-development-observed-before-ORG-003-seal" for row in rows
        ),
        "outcome_unopened_blind_target_count": sum(
            row["custody_class"].startswith("identity-only-outcome-unopened") for row in rows
        ),
        "blind_hfg_298_external_strings": {
            "benzene": blind_values[blind_roles[0]][0],
            "cyclohexene": blind_values[blind_roles[1]][0],
            "cyclohexane": blind_values[blind_roles[2]][0],
        },
        "blind_hfg_298_uncertainty_external_strings": {
            "benzene": blind_values[blind_roles[0]][1],
            "cyclohexene": blind_values[blind_roles[1]][1],
            "cyclohexane": blind_values[blind_roles[2]][1],
        },
        "blind_single_isolated_hydrogenation_magnitude_kj_per_mol": _hundredths(single),
        "blind_cyclic_threefold_hydrogenation_magnitude_kj_per_mol": _hundredths(cyclic),
        "blind_localized_threefold_reference_magnitude_kj_per_mol": _hundredths(localized),
        "blind_recurrence_stability_excess_magnitude_kj_per_mol": _hundredths(excess),
        "blind_conservative_uncertainty_envelope_kj_per_mol": _hundredths(envelope),
        "blind_stability_excess_lower_envelope_kj_per_mol": _hundredths(excess - envelope),
        **postseal,
    }


class AromaticRecurrenceStabilityValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = AROMATIC_RECURRENCE_STABILITY_SPEC

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
            raise ValueError("ORG-003 capability-closed package changed")
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
        document_text = json.dumps(document, sort_keys=True).casefold()
        controls = {
            "omitted_source_row_rejected": omission_rejected,
            "numerical_zero_rejected": numerical_zero_rejected,
            "all_nine_target_hashes_bound_postseal": len(release.targets) == 9,
            "incomplete_pair_cell_layer_rejected": analysis["incomplete_pair_cell_layer_rejected"],
            "duplicated_boundary_fibre_rejected": analysis["duplicated_boundary_fibre_rejected"],
            "open_two_centre_cycle_rejected": analysis["open_two_centre_cycle_rejected"],
            "development_observed_rows_not_mislabelled_blind": analysis["development_observed_target_count"] == 6,
            "three_independent_outcomes_opened_only_after_seal": analysis["outcome_unopened_blind_target_count"] == 3,
            "blind_recurrence_stability_excess_clears_conservative_envelope": analysis[
                "blind_recurrence_stability_excess_magnitude_kj_per_mol"
            ]
            == "150.39"
            and analysis["blind_stability_excess_lower_envelope_kj_per_mol"] == "143.79",
            "external_signed_and_absent_inscriptions_downstream_and_preserved": analysis[
                "all_signed_and_absent_external_inscriptions_preserved_downstream"
            ],
            "blind_sources_not_recaptured": analysis["blind_source_recapture_count"] == 0,
            "prediction_contains_no_huckel_electron_count_enthalpy_value_sign_uncertainty_or_payload": not any(
                token in document_text
                for token in (
                    "hückel",
                    "huckel",
                    "4n+2",
                    "hfg",
                    "82.93",
                    "-4.32",
                    "-123.14",
                    "150.39",
                    "target_payload_hash",
                )
            ),
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and analysis["primitive_support_count"] == 6
            and analysis["successor_support_count"] == 10
            and analysis["second_successor_support_count"] == 14
            and analysis["complete_first_return"]
            and analysis["complete_pair_cell_perturbation_closure"]
            and analysis["positive_recurrence_opening_gap"]
            and analysis["complete_target_count"] == 9
            and analysis["complete_source_count"] == 9
            and analysis["aromatic_cycle_stability_surface_present"]
            and analysis["cyclic_delocalization_and_thermodynamic_stability_surface_present"]
            and analysis["resonance_energy_unobservable_estimate_boundary_present"]
            and analysis["blind_hfg_298_external_strings"]
            == {"benzene": "82.93", "cyclohexene": "-4.32", "cyclohexane": "-123.14"}
            and analysis["blind_hfg_298_uncertainty_external_strings"]
            == {"benzene": "0.50", "cyclohexene": "0.98", "cyclohexane": "0.79"}
            and analysis["blind_single_isolated_hydrogenation_magnitude_kj_per_mol"] == "118.82"
            and analysis["blind_cyclic_threefold_hydrogenation_magnitude_kj_per_mol"] == "206.07"
            and analysis["blind_localized_threefold_reference_magnitude_kj_per_mol"] == "356.46"
            and analysis["blind_recurrence_stability_excess_magnitude_kj_per_mol"] == "150.39"
            and sum(analysis["blind_cccbdb_complete_table_counts"].values()) == 59
            and sum(analysis["blind_cccbdb_complete_row_counts"].values()) == 353
            and sum(analysis["development_webbook_complete_table_counts"].values()) == 9
            and sum(analysis["development_webbook_complete_row_counts"].values()) == 121
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
                    ("exact-aromatic-recurrence-stability/1", self.spec.falsification_condition)
                ),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity_hash = target_identity_from_release(release)
        if target_identity_hash != vault.commitment.target_identity_hash:
            raise ValueError("ORG-003 target identity differs")
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
            "Fold recurrence support sequence forced without imported electron-count rule: 6, 10, 14",
            "complete authority surface: nine sources; six transparently development-observed and three independently outcome-unopened before seal",
            "blind CCCBDB Hfg(298.15 K) external strings: benzene 82.93, cyclohexene -4.32, cyclohexane -123.14 kJ mol^-1",
            "blind exact transfer magnitudes: isolated 118.82, cyclic threefold 206.07, localized threefold reference 356.46 kJ mol^-1",
            "blind recurrence-stability excess: 150.39 kJ mol^-1; conservative uncertainty 6.60; positive lower envelope 143.79",
            "complete blind CCCBDB surface retained: 59 scientific tables and 353 rows",
            "complete development WebBook surface retained: 9 thermochemistry tables and 121 rows",
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
            tuple(row["source_id"] for row in rows),
            measurements,
            sha256_identity(payload),
            self.spec.falsification_condition,
            passed,
        )


__all__ = (
    "AromaticRecurrenceStabilityValidator",
    "_identities",
    "_prediction_map",
    "_source_rows",
    "exact_analysis",
    "experiment_registration_record",
    "prediction_program_document",
)
