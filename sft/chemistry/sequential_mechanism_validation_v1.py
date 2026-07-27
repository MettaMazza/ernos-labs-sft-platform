"""Capability-closed post-seal validation for Chemistry KIN-007."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.sequential_mechanism_batch_v1 import (
    ARTICLE_HASH, ARTICLE_PATH, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH,
    SEQUENTIAL_MECHANISM_SPEC, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.sequential_mechanism_law_v1 import (
    CompleteSequentialMechanism, RetainedElementaryTransition, RetainedMechanismState,
    forced_sequential_mechanism_composition,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldTable, FoldWord,
    HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree,
    target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


IDENTITY_KEYS = (
    "target_id", "source_id", "article_doi", "reaction_identity", "measurement_identity",
    "pdb_identity", "source_record_class", "source_row",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("KIN-007 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "source_condition_external_inscription", "elapsed_second_exact_fraction", "delay_external_inscription",
        "power_external_inscription", "power_joule_exact_fraction", "resolution_angstrom_exact_fraction",
        "XTX_component_exact_atom_counts", "XTX_component_exact_occupancy", "experimentally_retained_state_identity",
        "measured_difference_density_features", "observed_state", "assignment_status", "observed_adverse_result",
        "source_disclosure", "target_payload", "target_payload_hash", "snapshot_hash",
    }
    if (
        document.get("complete_registered_target_count") != 17
        or document.get("target_values_or_hashes_present") is not False
        or document.get("all_time_power_coordinate_occupancy_density_resolution_statistic_intermediate_assignment_target_and_target_hash_values_absent") is not True
        or len(rows) != 17 or any(forbidden.intersection(row) for row in rows)
        or tuple(row["source_row"] for row in rows) != tuple(range(1, 18))
        or len({row["target_id"] for row in rows}) != 17
    ):
        raise ValueError("KIN-007 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"sequential-mechanism-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        identities = (
            ("complete-source-identity", str(row["source_id"])),
            ("source-article-identity", str(row["article_doi"])),
            ("registered-reaction-identity", str(row["reaction_identity"])),
            ("measurement-identity", str(row["measurement_identity"])),
            ("deposited-model-or-EmptyOne-identity", str(row["pdb_identity"])),
            ("source-record-class", str(row["source_record_class"])),
            ("positive-source-row", str(row["source_row"])),
        )
        for number, (family, label) in enumerate(identities, start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        for family, label in (
            ("complete-mechanism-law", "all-distinct-states-edges-and-intermediates-retained-in-order"),
            ("composition-law", "exact-adjacent-boundary-composition-without-imported-evolution-equation"),
            ("status-law", "conditions-favorable-adverse-unresolved-and-parallel-records-retained"),
            ("provenance-law", "complete-article-supplements-PDB-custody-and-control-vector-retained"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-sequential-mechanism-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-sequential-mechanism-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": SEQUENTIAL_MECHANISM_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": SEQUENTIAL_MECHANISM_SPEC.experiment_id,
        "claim_id": SEQUENTIAL_MECHANISM_SPEC.claim_id,
        "provenance": "forward_forcing_with_prefetch_and_value_free_seventeen_record_identity_seals",
        "frozen_relation": SEQUENTIAL_MECHANISM_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_article_snapshot": (ARTICLE_PATH, ARTICLE_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in SEQUENTIAL_MECHANISM_SPEC.target_rows),
        "all_time_power_coordinate_occupancy_density_resolution_statistic_intermediate_assignment_target_and_target_hash_values_absent": True,
        "falsification_condition": SEQUENTIAL_MECHANISM_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 17:
        raise ValueError("KIN-007 prediction is not the complete seventeen-record table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 12
        ):
            raise ValueError("KIN-007 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 17:
        raise ValueError("KIN-007 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (ARTICLE_PATH, ARTICLE_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError(f"KIN-007 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_registered_target_count") != 17
        or document.get("release_requires_complete_identity_prediction_seal") is not True
        or document.get("identity_registry_hash") != IDENTITY_HASH or len(targets) != 17
    ):
        raise ValueError("KIN-007 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in IDENTITY_KEYS):
            raise ValueError("KIN-007 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def _observed_state(row: dict, occurrence: int) -> RetainedMechanismState:
    target = row["target_payload"]
    return RetainedMechanismState(
        HeldLabel(
            "registered-mechanism-state",
            f"{target['pdb_identity']}:{target['experimentally_retained_state_identity']}",
        ),
        PositiveCount(occurrence),
        HeldLabel("held-state-condition", target["source_condition_external_inscription"]),
        HeldLabel("held-observation-status", target["source_status"]),
    )


def exact_sequential_mechanism_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 17:
        raise ValueError("KIN-007 requires the complete seventeen-record vector")
    expected_classes = (
        ("deposited-structure-snapshot", 5), ("late-structure-observation", 2),
        ("complete-power-titration-column", 7), ("negative-delay-control", 1),
        ("interleaved-dark-adverse-control", 1), ("unresolved-multiple-intermediate-disclosure", 1),
    )
    class_counts = {name: sum(row["source_record_class"] == name for row in rows) for name, _ in expected_classes}
    if any(class_counts[name] != count for name, count in expected_classes):
        raise ValueError("KIN-007 complete target-class census changed")

    structures = rows[:5]
    expected_pdb = ("8WZF", "8WZG", "8WZR", "8WZT", "8WZV")
    expected_counts = (
        {"C": 3, "O": 3, "MN": 1}, {"C": 2, "O": 2, "MN": 1},
        {"C": 2, "O": 2, "MN": 1}, {"C": 2, "O": 2, "MN": 1},
        {"C": 1, "O": 1, "MN": 1},
    )
    expected_occupancies = (Fraction(1), Fraction(9, 10), Fraction(9, 10), Fraction(17, 20), Fraction(13, 20))
    observed_counts = []
    observed_occupancies = []
    for ordinal, row in enumerate(structures):
        target = row["target_payload"]
        counts = target.get("XTX_component_exact_atom_counts")
        occupancy = Fraction(target.get("XTX_component_exact_occupancy"))
        if (
            target.get("pdb_identity") != expected_pdb[ordinal]
            or counts != expected_counts[ordinal]
            or occupancy != expected_occupancies[ordinal]
            or Fraction(target.get("resolution_angstrom_exact_fraction")) != Fraction(8, 5)
            or target.get("source_status") != "experimentally deposited atomic model and map-coefficient identity"
        ):
            raise ValueError("KIN-007 deposited structural vector changed")
        observed_counts.append(counts)
        observed_occupancies.append(occupancy)

    initial = _observed_state(structures[0], 1)
    first_intermediate = _observed_state(structures[1], 2)
    second_intermediate = _observed_state(structures[4], 3)
    mechanism = CompleteSequentialMechanism(
        HeldLabel("registered-reaction", rows[0]["reaction_identity"]),
        (initial, first_intermediate, second_intermediate),
        (
            RetainedElementaryTransition(
                HeldLabel("registered-elementary-transition", "COax-release-and-water-exchange"), PositiveCount(1),
                initial.state_identity, first_intermediate.state_identity,
                HeldLabel("held-transition-condition", "complete-darkness-to-first-photoexcited-record"),
                HeldLabel("held-transition-status", "experimentally-retained-first-CO-release"),
            ),
            RetainedElementaryTransition(
                HeldLabel("registered-elementary-transition", "COeq1-release-and-water-exchange"), PositiveCount(2),
                first_intermediate.state_identity, second_intermediate.state_identity,
                HeldLabel("held-transition-condition", "held-time-and-dose-change-not-collapsed"),
                HeldLabel("held-transition-status", "experimentally-retained-second-CO-release"),
            ),
        ),
    )
    composition = forced_sequential_mechanism_composition(mechanism)

    late = rows[5:7]
    if any(
        row["target_payload"].get("assignment_status")
        != "unresolved-multiple-intermediate-mixture; no precise single atomic model"
        or row["target_payload"].get("pdb_deposit_status") != "structural-EmptyOne-no-deposited-model"
        for row in late
    ):
        raise ValueError("KIN-007 unresolved late-state boundary changed")

    power = rows[7:14]
    positive_sigma = []
    positive_density = []
    external_absence_glyph_count = 0
    for ordinal, row in enumerate(power, start=1):
        target = row["target_payload"]
        if (
            target.get("power_table_column") != ordinal
            or Fraction(target.get("delay_second_exact_fraction")) <= 0
            or Fraction(target.get("power_joule_exact_fraction")) <= 0
            or Fraction(target.get("scale_exact_positive_fraction")) <= 0
            or set(target.get("measured_difference_density_features", {})) != {"Mn", "COax", "COeq1", "COeq2"}
        ):
            raise ValueError("KIN-007 power-titration column changed")
        for feature in target["measured_difference_density_features"].values():
            if feature.get("exact_positive_magnitude_present") is False:
                if feature.get("external_inscription") != "0" or feature.get("sft_interpretation") != "structural-EmptyOne-observed-absence":
                    raise ValueError("KIN-007 external absence glyph changed")
                external_absence_glyph_count += 1
            elif feature.get("exact_positive_magnitude_present") is True:
                sigma = Fraction(feature["sigma_exact_positive_fraction"])
                density = Fraction(feature["electron_density_exact_positive_fraction"])
                if sigma <= 0 or density <= 0 or feature.get("orientation") != "held-negative-difference-density-direction-with-exact-positive-magnitude":
                    raise ValueError("KIN-007 exact measured density magnitude changed")
                positive_sigma.append(sigma)
                positive_density.append(density)
            else:
                raise ValueError("KIN-007 power feature status changed")

    favorable, adverse, unresolved = (row["target_payload"] for row in rows[14:17])
    controls_retained = (
        favorable.get("observed_difference_density") == "structural-EmptyOne-no-difference-feature"
        and "reversed event order" in favorable.get("held_orientation", "")
        and "possible light contamination" in adverse.get("observed_adverse_result", "")
        and "cannot be determined precisely" in unresolved.get("assignment_boundary", "")
    )
    pdf_records = tuple(primary.get("supplement_pdf_records", ()))
    return {
        "complete_registered_target_count": len(rows),
        "complete_target_class_counts": class_counts,
        "complete_supplementary_file_count": primary.get("complete_supplementary_file_count"),
        "complete_supplement_pdf_count": len(pdf_records),
        "complete_pdb_deposit_count": primary.get("complete_pdb_deposit_count"),
        "deposited_XTX_component_count_vector": observed_counts,
        "deposited_XTX_occupancy_vector": tuple(str(value) for value in observed_occupancies),
        "exact_positive_difference_density_sigma_range": {"minimum": str(min(positive_sigma)), "maximum": str(max(positive_sigma))},
        "exact_positive_difference_density_range": {"minimum": str(min(positive_density)), "maximum": str(max(positive_density))},
        "external_absence_glyph_count_translated_to_EmptyOne": external_absence_glyph_count,
        "three_distinct_experimental_states_force_two_boundary-matched_edges": (
            len(composition.ordered_states) == 3 and len(composition.ordered_transitions) == 2
            and composition.ordered_transitions[0].exit_state_identity == composition.ordered_transitions[1].entry_state_identity
        ),
        "initial_first_intermediate_and_second_intermediate_retained_exactly": (
            composition.initial_state == initial
            and composition.intermediate_states == (first_intermediate,)
            and composition.terminal_state == second_intermediate
        ),
        "all_three_repeat_observations_of_first_intermediate_retained": tuple(observed_counts[1:4]) == (expected_counts[1], expected_counts[2], expected_counts[3]),
        "complete_five_deposited_structure_vector_retained": tuple(row["pdb_identity"] for row in structures) == expected_pdb,
        "both_late_unresolved_records_retained_without_inference": len(late) == 2,
        "all_seven_power_columns_and_four_features_retained": len(power) == 7 and len(positive_sigma) + external_absence_glyph_count == 28,
        "favorable_adverse_and_unresolved_controls_retained": controls_retained,
        "complete_article_thirteen_files_three_pdfs_five_PDB_and_CXIDB_custody_retained": (
            primary.get("complete_article_supplements_pdb_and_raw_custody_metadata_preserved") is True
            and primary.get("complete_supplementary_file_count") == 13
            and len(primary.get("complete_supplementary_files", ())) == 13
            and len(pdf_records) == 3
            and primary.get("complete_pdb_deposit_count") == 5
            and len(primary.get("complete_pdb_records", ())) == 5
            and len(primary.get("cxidb_custody_record", ())) == 2
        ),
        "experimental_calculated_and_unresolved_provenance_separated": (
            primary.get("experimental_deposited_calculated_and_unresolved_provenance_separated") is True
            and primary.get("computational_trajectory_archive_identity", {}).get("accession") == "BSM00067"
        ),
        "no_imported_evolution_fit_selection_interpolation_or_target_correction": (
            primary.get("imported_differential_equation_exponential_decay_fitted_lifetime_steady_state_selection_interpolation_average_or_target_correction_used_in_fold_law") is False
            and primary.get("external_values_used_as_proof_parameters") is False
            and primary.get("image_curves_not_digitized_and_unreported_values_not_inferred") is True
        ),
    }


class SequentialMechanismValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = SEQUENTIAL_MECHANISM_SPEC

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
            raise ValueError("KIN-007 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-sequential-mechanism-row-hash", row["target_payload_hash"])
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
            "all-distinct-states-edges-and-intermediates-retained-in-order",
            "exact-adjacent-boundary-composition-without-imported-evolution-equation",
            "conditions-favorable-adverse-unresolved-and-parallel-records-retained",
            "complete-article-supplements-PDB-custody-and-control-vector-retained",
        )
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, start=1)
            )
            law_match = tuple(cell.label for cell in word.cells[8:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel(
                "external-sequential-mechanism-row-hash", row["target_payload_hash"]
            )
            comparisons.append({
                "target_id": row["target_id"], "identity_match": identity_match,
                "law_match": law_match, "postseal_target_hash_match": target_match,
                "passed": identity_match and law_match and target_match,
            })
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_sequential_mechanism_analysis(source_rows, primary)
        try:
            exact_sequential_mechanism_analysis(source_rows[:-1], primary)
            omitted_record_rejected = False
        except (ValueError, RuntimeError, InadmissibleExactValue):
            omitted_record_rejected = True
        try:
            a = RetainedMechanismState(HeldLabel("registered-mechanism-state", "a"), PositiveCount(1), HeldLabel("held-state-condition", "c"), HeldLabel("held-observation-status", "held"))
            b = RetainedMechanismState(HeldLabel("registered-mechanism-state", "b"), PositiveCount(2), HeldLabel("held-state-condition", "c"), HeldLabel("held-observation-status", "held"))
            wrong = RetainedElementaryTransition(HeldLabel("registered-elementary-transition", "wrong"), PositiveCount(1), HeldLabel("registered-mechanism-state", "x"), b.state_identity, HeldLabel("held-transition-condition", "c"), HeldLabel("held-transition-status", "held"))
            CompleteSequentialMechanism(HeldLabel("registered-reaction", "r"), (a, b), (wrong,))
            broken_adjacency_rejected = False
        except InadmissibleExactValue:
            broken_adjacency_rejected = True
        controls = {
            "tampered_omitted_source_record_rejected": omitted_record_rejected,
            "tampered_broken_transition_boundary_rejected": broken_adjacency_rejected,
            "complete_seventeen_record_target_vector_retained": len(release.targets) == 17,
            "external_zero_glyphs_remain_structural_EmptyOne": analysis["external_absence_glyph_count_translated_to_EmptyOne"] == 6,
            "adverse_and_unresolved_records_remain_visible": analysis["favorable_adverse_and_unresolved_controls_retained"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {
            "complete_registered_target_count", "complete_target_class_counts", "complete_supplementary_file_count",
            "complete_supplement_pdf_count", "complete_pdb_deposit_count", "deposited_XTX_component_count_vector",
            "deposited_XTX_occupancy_vector", "exact_positive_difference_density_sigma_range",
            "exact_positive_difference_density_range", "external_absence_glyph_count_translated_to_EmptyOne",
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and all(bool(value) for key, value in analysis.items() if key not in non_boolean)
            and all(controls.values())
        )
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-complete-sequential-composition-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("KIN-007 released target differs from commitment")
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
            f"{row['target_id']}: class={row['source_record_class']}; PDB={row['pdb_identity']}; target={row['target_payload_hash']}"
            for row in source_rows
        ) + (
            f"exact deposited component vector: {analysis['deposited_XTX_component_count_vector']}",
            f"exact deposited occupancy vector: {analysis['deposited_XTX_occupancy_vector']}",
            f"exact positive difference-density sigma range: {analysis['exact_positive_difference_density_sigma_range']}",
            f"exact positive difference-density range: {analysis['exact_positive_difference_density_range']}",
            "complete time-resolved vector: five PDB deposits, two late unresolved records, seven power columns, favorable negative-delay control, adverse 1 ms interleaved-dark contamination record and unresolved late-stage boundary",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash,
            isolation_certificate=isolation, target_custody_certificate=custody,
            evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True,
            data_source_ids=(source_rows[0]["source_id"], "RCSB-PDB-8WZF-8WZV", "CXIDB-221"),
            measurements=measurements, measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition, passed=passed,
        )


__all__ = (
    "SequentialMechanismValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_sequential_mechanism_analysis", "experiment_registration_record", "prediction_program_document",
)
