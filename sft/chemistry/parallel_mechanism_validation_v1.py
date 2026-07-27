"""Capability-closed post-seal validation for Chemistry KIN-008."""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.chemistry.parallel_mechanism_batch_v1 import (
    ARTICLE_HTML_HASH, ARTICLE_HTML_PATH, ARTICLE_PDF_HASH, ARTICLE_PDF_PATH, IDENTITY_HASH, IDENTITY_PATH,
    INVENTORY_HASH, INVENTORY_PATH, PARALLEL_MECHANISM_SPEC, PEER_REVIEW_HASH, PEER_REVIEW_PATH,
    PRIMARY_HASH, PRIMARY_PATH, SUPPLEMENT_HASH, SUPPLEMENT_PATH, TARGET_HASH, TARGET_PATH,
    WORKBOOK_HASH, WORKBOOK_PATH,
)
from sft.chemistry.parallel_mechanism_law_v1 import (
    CompleteParallelMechanism, RetainedParallelPath, forced_parallel_mechanism_composition,
)
from sft.chemistry.sequential_mechanism_law_v1 import (
    CompleteSequentialMechanism, RetainedElementaryTransition, RetainedMechanismState,
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
    "target_id", "source_id", "article_doi", "reaction_surface_identity", "measurement_identity",
    "source_sheet_identity", "source_sheet_ordinal", "declared_max_row", "declared_max_column", "source_record_class",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("KIN-008 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "complete_rectangular_cells", "source_numeric_inscription", "source_label", "source_formula_inscription",
        "exact_positive_fraction", "target_payload", "target_payload_hash", "snapshot_hash",
    }
    if (
        document.get("complete_registered_target_count") != 28
        or document.get("complete_registered_rectangular_cell_position_count") != 18158
        or document.get("target_values_or_hashes_present") is not False
        or document.get("all_sheet_cell_label_time_product_concentration_replicate_uncertainty_status_value_and_target_hash_values_absent") is not True
        or len(rows) != 28
        or tuple(row["source_sheet_ordinal"] for row in rows) != tuple(range(1, 29))
        or len({row["target_id"] for row in rows}) != 28
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("KIN-008 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"parallel-mechanism-sheet-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        identities = (
            ("complete-source-identity", str(row["source_id"])),
            ("source-article-identity", str(row["article_doi"])),
            ("registered-reaction-surface", str(row["reaction_surface_identity"])),
            ("measurement-identity", str(row["measurement_identity"])),
            ("source-sheet-identity", str(row["source_sheet_identity"])),
            ("positive-source-sheet-ordinal", str(row["source_sheet_ordinal"])),
            ("positive-declared-max-row", str(row["declared_max_row"])),
            ("positive-declared-max-column", str(row["declared_max_column"])),
            ("source-record-class", str(row["source_record_class"])),
        )
        for number, (family, label) in enumerate(identities, start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        for family, label in (
            ("complete-parallel-support-law", "all-distinct-complete-path-words-retained-in-source-order"),
            ("common-boundary-law", "every-path-meets-one-retained-initial-state-with-shared-occurrences-explicit"),
            ("status-law", "all-products-times-replicates-formulas-weak-adverse-unresolved-and-unassigned-records-retained"),
            ("provenance-law", "complete-article-supplement-peer-review-and-twenty-eight-sheet-cell-ledger-retained"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-parallel-mechanism-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-parallel-mechanism-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": PARALLEL_MECHANISM_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": PARALLEL_MECHANISM_SPEC.experiment_id,
        "claim_id": PARALLEL_MECHANISM_SPEC.claim_id,
        "provenance": "forward_forcing_with_prefetch_and_value_free_twenty_eight_sheet_identity_seal",
        "frozen_relation": PARALLEL_MECHANISM_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_source_records": (
            (ARTICLE_HTML_PATH, ARTICLE_HTML_HASH), (ARTICLE_PDF_PATH, ARTICLE_PDF_HASH),
            (SUPPLEMENT_PATH, SUPPLEMENT_HASH), (PEER_REVIEW_PATH, PEER_REVIEW_HASH),
            (WORKBOOK_PATH, WORKBOOK_HASH), (INVENTORY_PATH, INVENTORY_HASH),
        ),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in PARALLEL_MECHANISM_SPEC.target_rows),
        "all_sheet_cell_label_time_product_concentration_replicate_uncertainty_status_value_and_target_hash_values_absent": True,
        "falsification_condition": PARALLEL_MECHANISM_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 28:
        raise ValueError("KIN-008 prediction is not the complete twenty-eight-sheet table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 14
        ):
            raise ValueError("KIN-008 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 28:
        raise ValueError("KIN-008 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (WORKBOOK_PATH, WORKBOOK_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError(f"KIN-008 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_registered_target_count") != 28
        or document.get("complete_registered_rectangular_cell_position_count") != 18158
        or document.get("release_requires_complete_identity_and_prediction_seal") is not True
        or document.get("identity_registry_hash") != IDENTITY_HASH
        or len(targets) != 28
    ):
        raise ValueError("KIN-008 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in IDENTITY_KEYS):
            raise ValueError("KIN-008 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def _state(label: str, occurrence: int, status: str) -> RetainedMechanismState:
    return RetainedMechanismState(
        HeldLabel("registered-mechanism-state", label), PositiveCount(occurrence),
        HeldLabel("held-state-condition", "same-reaction-held-buffer-composition-and-method"),
        HeldLabel("held-observation-status", status),
    )


def exact_parallel_mechanism_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 28:
        raise ValueError("KIN-008 requires the complete twenty-eight-sheet vector")
    if tuple(row["source_sheet_ordinal"] for row in rows) != tuple(range(1, 29)):
        raise ValueError("KIN-008 complete worksheet order changed")
    path_rows = tuple(primary.get("complete_parallel_path_family", ()))
    if len(path_rows) != 3:
        raise ValueError("KIN-008 complete parallel path family changed")
    reaction = HeldLabel("registered-reaction", "doi-10.1038-s41467-026-70199-4-Ac-CY-network")
    paths = []
    for row in path_rows:
        states = tuple(_state(label, ordinal, row["path_status"]) for ordinal, label in enumerate(row["ordered_state_word"], start=1))
        transitions = tuple(
            RetainedElementaryTransition(
                HeldLabel("registered-elementary-transition", f"{row['path_identity']}-edge-{ordinal}"),
                PositiveCount(ordinal), states[ordinal - 1].state_identity, states[ordinal].state_identity,
                HeldLabel("held-transition-condition", "same-reaction-held-buffer-composition-and-method"),
                HeldLabel("held-transition-status", row["path_status"]),
            )
            for ordinal in range(1, len(states))
        )
        paths.append(RetainedParallelPath(
            HeldLabel("registered-parallel-path", row["path_identity"]), PositiveCount(row["path_row"]),
            CompleteSequentialMechanism(reaction, states, transitions), HeldLabel("held-path-status", row["path_status"]),
        ))
    complete = CompleteParallelMechanism(reaction, HeldLabel("registered-mechanism-state", "1-EP"), tuple(paths))
    composition = forced_parallel_mechanism_composition(complete)

    cell_count = sum(row["target_payload"]["complete_rectangular_cell_count"] for row in rows)
    worksheet_cell_counts_match = all(
        row["target_payload"]["complete_rectangular_cell_count"]
        == row["declared_max_row"] * row["declared_max_column"]
        == len(row["target_payload"]["complete_rectangular_cells"])
        for row in rows
    )
    class_counts = {"EmptyOne": 0, "external_zero": 0, "positive": 0, "signed": 0, "formula": 0, "label": 0}
    for row in rows:
        coordinates = [cell["cell_coordinate"] for cell in row["target_payload"]["complete_rectangular_cells"]]
        if len(coordinates) != len(set(coordinates)):
            raise ValueError("KIN-008 duplicated a registered worksheet cell")
        for cell in row["target_payload"]["complete_rectangular_cells"]:
            value_class = cell["source_value_class"]
            if value_class.startswith("structural-EmptyOne"):
                class_counts["EmptyOne"] += 1
            elif value_class == "external-zero-glyph-observed-absence":
                class_counts["external_zero"] += 1
            elif value_class == "exact-positive-observed-magnitude":
                class_counts["positive"] += 1
            elif value_class == "external-signed-directional-inscription":
                class_counts["signed"] += 1
            elif value_class == "source-reported-derived-formula-not-used-as-proof-parameter":
                class_counts["formula"] += 1
            else:
                class_counts["label"] += 1
    expected_counts = {"EmptyOne": 8968, "external_zero": 2109, "positive": 6060, "signed": 0, "formula": 722, "label": 299}
    all_products = {state for path in path_rows for state in path["ordered_state_word"]}
    supp_products = set(primary["supplementary_figure_32_complete_vector"]["product_identity_word"])
    return {
        "complete_registered_target_count": len(rows),
        "complete_registered_rectangular_cell_position_count": cell_count,
        "complete_cell_class_census": class_counts,
        "complete_parallel_path_count": composition.path_count.value,
        "complete_source_data_worksheet_count": primary.get("complete_source_data_worksheet_count"),
        "complete_primary_parallel_product_time_observation_count": primary.get("complete_primary_parallel_product_time_observation_count"),
        "complete_primary_source_formula_count": primary.get("complete_primary_source_formula_count"),
        "three_complete_paths_retained": len(composition.ordered_paths) == 3,
        "every_path_meets_common_initial_state": all(path.mechanism.ordered_states[0].state_identity == composition.common_initial_state_identity for path in composition.ordered_paths),
        "every_path_retains_common_terminal_occurrence": all(state.label == "2" for state in composition.terminal_state_word),
        "all_seven_product_identities_covered_without_selection": all_products == supp_products,
        "every_path_state_edge_intermediate_and_status_retained": all(
            len(path.mechanism.ordered_transitions) == len(path.mechanism.ordered_states) - 1
            and path.path_status.label == path_rows[index]["path_status"]
            for index, path in enumerate(composition.ordered_paths)
        ),
        "all_twenty_eight_worksheets_and_cells_retained": worksheet_cell_counts_match and cell_count == 18158,
        "all_external_cell_classes_retained_exactly": class_counts == expected_counts,
        "all_source_zero_glyphs_remain_external_observed_absence": class_counts["external_zero"] == 2109,
        "no_signed_source_measurement_cell_present": class_counts["signed"] == 0,
        "all_source_formulas_retained_but_excluded_from_proof": class_counts["formula"] == 722 and primary.get("source_formulas_retained_as_provenance_and_never_used_as_fold_proof_parameters") is True,
        "unresolved_two-structure_peak_retained_without_selection": primary.get("unresolved_source_disclosure", {}).get("assignment_status") == "two possible structures retained; no preferred structure selected",
        "complete_article_supplement_peer_review_workbook_and_source_inventory_retained": primary.get("complete_source_file_count") == 5 and primary.get("article_page_count") == 11 and primary.get("supplementary_information_page_count") == 54,
        "no_imported_parallel_equation_stochastic_fit_selection_average_interpolation_or_target_correction": primary.get("imported_parallel_reaction_equation_stochastic_premise_fitted_path_weight_steady_state_selection_average_interpolation_or_target_correction_used_in_law") is False and primary.get("external_values_used_as_proof_parameters") is False,
    }


class ParallelMechanismValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = PARALLEL_MECHANISM_SPEC

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
            raise ValueError("KIN-008 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-parallel-mechanism-sheet-hash", row["target_payload_hash"])
            for row in source_rows
        }
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
            "all-distinct-complete-path-words-retained-in-source-order",
            "every-path-meets-one-retained-initial-state-with-shared-occurrences-explicit",
            "all-products-times-replicates-formulas-weak-adverse-unresolved-and-unassigned-records-retained",
            "complete-article-supplement-peer-review-and-twenty-eight-sheet-cell-ledger-retained",
        )
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, start=1)
            )
            law_match = tuple(cell.label for cell in word.cells[10:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel(
                "external-parallel-mechanism-sheet-hash", row["target_payload_hash"]
            )
            comparisons.append({
                "target_id": row["target_id"], "identity_match": identity_match,
                "law_match": law_match, "postseal_target_hash_match": target_match,
                "passed": identity_match and law_match and target_match,
            })
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_parallel_mechanism_analysis(source_rows, primary)
        try:
            exact_parallel_mechanism_analysis(source_rows[:-1], primary)
            omitted_sheet_rejected = False
        except (ValueError, RuntimeError, InadmissibleExactValue):
            omitted_sheet_rejected = True
        try:
            first = analysis["complete_parallel_path_count"]
            path_rows = primary["complete_parallel_path_family"]
            reaction = HeldLabel("registered-reaction", "tamper")
            states_a = (_state("a", 1, "held"), _state("b", 2, "held"))
            states_x = (_state("x", 1, "held"), _state("c", 2, "held"))
            def one_path(label, row, states):
                edge = RetainedElementaryTransition(HeldLabel("registered-elementary-transition", label), PositiveCount(1), states[0].state_identity, states[1].state_identity, HeldLabel("held-transition-condition", "held"), HeldLabel("held-transition-status", "held"))
                return RetainedParallelPath(HeldLabel("registered-parallel-path", label), PositiveCount(row), CompleteSequentialMechanism(reaction, states, (edge,)), HeldLabel("held-path-status", "held"))
            CompleteParallelMechanism(reaction, states_a[0].state_identity, (one_path("p1", 1, states_a), one_path("p2", 2, states_x)))
            broken_common_boundary_rejected = False
        except InadmissibleExactValue:
            broken_common_boundary_rejected = True
        controls = {
            "tampered_omitted_worksheet_rejected": omitted_sheet_rejected,
            "tampered_broken_common_initial_boundary_rejected": broken_common_boundary_rejected,
            "complete_twenty_eight_sheet_target_vector_retained": len(release.targets) == 28,
            "all_18158_registered_cell_positions_retained": analysis["complete_registered_rectangular_cell_position_count"] == 18158,
            "all_2109_external_zero_glyphs_remain_structural_EmptyOne": analysis["all_source_zero_glyphs_remain_external_observed_absence"],
            "unresolved_two-structure_peak_remains_visible": analysis["unresolved_two-structure_peak_retained_without_selection"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {
            "complete_registered_target_count", "complete_registered_rectangular_cell_position_count",
            "complete_cell_class_census", "complete_parallel_path_count", "complete_source_data_worksheet_count",
            "complete_primary_parallel_product_time_observation_count", "complete_primary_source_formula_count",
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
            comparison_implementation_identity_hash=sha256_identity(("exact-complete-parallel-composition-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("KIN-008 released target differs from commitment")
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
            f"{row['target_id']}: sheet={row['source_sheet_identity']}; rectangular-cells={row['target_payload']['complete_rectangular_cell_count']}; target={row['target_payload_hash']}"
            for row in source_rows
        ) + (
            "complete parallel path word: 1-EP->1->2; 1-EP->7->8->9->2; weak trace 1-EP->2-EP->2",
            "complete primary parallel product-time surface: 385 raw observations across Figure 4b, Supplementary Figure 32 and Figure 5c",
            "complete workbook: 28 worksheets and 18,158 registered cell positions; 2,109 source zero glyphs retained only as structural observed absence",
            "source formulas, every replicate and unresolved Supplementary Figure 31 two-structure peak retained without selecting or fitting a path",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash,
            isolation_certificate=isolation, target_custody_certificate=custody,
            evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True,
            data_source_ids=(source_rows[0]["source_id"],), measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition, passed=passed,
        )


__all__ = (
    "ParallelMechanismValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_parallel_mechanism_analysis", "experiment_registration_record", "prediction_program_document",
)
